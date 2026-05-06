from sqlalchemy.orm import Session
from app.models.iot import IoTVital
from app.models.alert import Alert, AlertSeverity, AlertStatus
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.services.ml_anomaly import evaluate_vital_risk
from app.db.session import SessionLocal

# Fallback thresholds
HR_HIGH = 120.0
HR_LOW = 50.0
SPO2_LOW = 92.0
TEMP_HIGH = 38.0

def process_iot_vitals_background(vital_id: str):
    """
    Background task to evaluate IoT vitals for anomalies and create alerts.
    """
    db = SessionLocal()
    try:
        vital = db.query(IoTVital).filter(IoTVital.id == vital_id).first()
        if not vital:
            return
            
        # Prepare values for ML Engine. Use default norms if missing.
        hr = vital.heart_rate if vital.heart_rate is not None else 75.0
        spo2 = vital.spo2 if vital.spo2 is not None else 98.0
        temp = vital.temperature if vital.temperature is not None else 36.6
        # IoT typically doesn't send glucose/resp. Use norms.
        gluc = 100.0
        resp = 16.0
        
        is_anomaly = False
        reasons = []
        
        # 1. Rule-Based Fallback
        severity = AlertSeverity.INFO
        
        if hr > 140 or hr < 40:
            is_anomaly = True
            severity = AlertSeverity.CRITICAL
            reasons.append(f"CRITICAL Heart Rate ({hr} bpm)")
        elif hr > HR_HIGH or hr < HR_LOW:
            is_anomaly = True
            severity = AlertSeverity.WARNING if severity == AlertSeverity.INFO else severity
            reasons.append(f"Abnormal Heart Rate ({hr} bpm)")
            
        if spo2 < 85:
            is_anomaly = True
            severity = AlertSeverity.CRITICAL
            reasons.append(f"CRITICAL Low SpO2 ({spo2}%)")
        elif spo2 < SPO2_LOW:
            is_anomaly = True
            severity = AlertSeverity.WARNING if severity == AlertSeverity.INFO else severity
            reasons.append(f"Low SpO2 ({spo2}%)")
            
        if temp > 39.5:
            is_anomaly = True
            severity = AlertSeverity.CRITICAL
            reasons.append(f"CRITICAL High Temperature ({temp} C)")
        elif temp > TEMP_HIGH:
            is_anomaly = True
            severity = AlertSeverity.WARNING if severity == AlertSeverity.INFO else severity
            reasons.append(f"High Temperature ({temp} C)")
            
        # 2. ML Engine Integration (DAGMM + Isolation Forest)
        try:
            ml_is_anomaly, ml_reason, ml_rec = evaluate_vital_risk(hr, spo2, temp, gluc, resp)
            if ml_is_anomaly:
                is_anomaly = True
                severity = AlertSeverity.CRITICAL
                reasons.append("ML Engine detected physiological anomaly.")
        except Exception as e:
            print(f"ML Engine error during IoT background processing: {e}")
            
        if is_anomaly:
            # Fetch assigned doctor
            doctor_id = None
            patient_profile = db.query(Patient).filter(Patient.user_id == vital.patient_id).first()
            if patient_profile and patient_profile.doctors:
                doctor_id = patient_profile.doctors[0].user_id
                
            alert = Alert(
                patient_id=vital.patient_id,
                doctor_id=doctor_id,
                vital_type="IOT_ANOMALY",
                measured_value=hr,  # Just tracking HR as base metric for IoT alert
                severity=severity,
                reason="; ".join(reasons),
                status=AlertStatus.NEW,
                alert_type="ML_DAGMM_IF_ANOMALY",
                anomaly_score=1.0,
                source=vital.source
            )
            db.add(alert)
            db.commit()
    finally:
        db.close()
