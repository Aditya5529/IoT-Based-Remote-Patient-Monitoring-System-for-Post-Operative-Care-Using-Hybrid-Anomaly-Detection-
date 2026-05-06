from sqlalchemy.orm import Session
from app.models.vital import Vital
from app.models.alert import Alert, AlertSeverity, AlertStatus
from app.services.ml_anomaly import evaluate_vital_risk

def check_vital_alert(db: Session, vital: Vital):
    """
    Evaluates the patient's entire state using PyTorch DAGMM and Scikit Isolation Forest.
    """
    # 1. Fetch latest state of all 5 vitals for this patient
    # Default norms if patient has no history
    current_state = {
        'heart_rate': 75.0,
        'spo2': 98.0,
        'temperature': 36.6,
        'glucose': 100.0,
        'resp_rate': 16.0
    }
    
    # Override with latest from DB
    latest_vitals = db.query(Vital).filter(Vital.patient_id == vital.patient_id).order_by(Vital.ts.desc()).limit(20).all()
    for v in latest_vitals:
        if v.vital_type in current_state:
            current_state[v.vital_type] = v.value
            
    # Include the newly submitted vital instantly
    if vital.vital_type in current_state:
         current_state[vital.vital_type] = vital.value
         
    # 2. Run Deep ML Multivariate Inference
    is_anomaly, reason, recommendation = evaluate_vital_risk(
        hr=current_state['heart_rate'],
        spo2=current_state['spo2'],
        temp=current_state['temperature'],
        gluc=current_state['glucose'],
        resp=current_state['resp_rate']
    )
    
    if is_anomaly:
        # Find assigned doctor
        doctor_id = None
        if vital.patient and vital.patient.patient_profile:
            if vital.patient.patient_profile.doctors:
                doctor_id = vital.patient.patient_profile.doctors[0].user_id
        
        if not doctor_id:
            print(f"⚠️ No assigned doctor for patient {vital.patient_id}. Alert skipped.")
            return
            
        # Add rich recommendation into the reason or raw_meta
        full_reason = f"{reason} | RECOMMENDATION: {recommendation}"
        
        # Check active alert
        existing = db.query(Alert).filter(
            Alert.patient_id == vital.patient_id,
            Alert.vital_type == vital.vital_type,
            Alert.status == AlertStatus.NEW
        ).first()

        if existing:
            existing.measured_value = vital.value
            existing.ts = vital.ts
            existing.reason = full_reason
        else:
            alert = Alert(
                patient_id=vital.patient_id,
                doctor_id=doctor_id,
                vital_type="HEART_RISK_ANOMALY",
                measured_value=vital.value,
                severity=AlertSeverity.CRITICAL, 
                reason=full_reason,
                status=AlertStatus.NEW,
                alert_type="ML_DAGMM_IF_ANOMALY",
                anomaly_score=1.0
            )
            db.add(alert)

