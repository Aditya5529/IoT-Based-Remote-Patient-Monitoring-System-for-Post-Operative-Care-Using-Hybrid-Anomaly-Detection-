from app.db.session import SessionLocal
from app.models.vital import Vital
from app.models.threshold import Threshold
from app.models.alert import Alert, AlertSeverity, AlertStatus

def evaluate_vitals(vital_id: str):
    """
    Evaluate a single vital reading against thresholds.
    """
    db = SessionLocal()
    try:
        vital = db.query(Vital).filter(Vital.id == vital_id).first()
        if not vital:
            return

        patient_id = vital.patient_id
        vital_type = vital.vital_type
        value = vital.value
    
        # Fetch thresholds for this patient and vital type
        # Priority: Patient Specific > Global Default
        threshold = db.query(Threshold).filter(
            Threshold.patient_id == patient_id, 
            Threshold.vital_type == vital_type,
            Threshold.enabled == True
        ).first()
        
        if not threshold:
             threshold = db.query(Threshold).filter(
                Threshold.patient_id == None, 
                Threshold.vital_type == vital_type,
                Threshold.enabled == True
            ).first()

        if not threshold:
            return # No rules
            
        is_abnormal = False
        reason = ""

        # Check boundaries
        # Adjust for activity context if needed (Simplistic implementation)
        # E.g., if running, increase HR max by 20%
        run_adjustment = 0
        if vital.activity_label == "running" and vital_type == "HR":
            run_adjustment = 30 # Allow 30 bpm higher
        
        current_max = (threshold.max_value or 9999) + run_adjustment
        
        if value < (threshold.min_value or -9999):
            is_abnormal = True
            reason = f"Low {vital_type}: {value} (Min: {threshold.min_value})"
        elif value > current_max:
            is_abnormal = True
            reason = f"High {vital_type}: {value} (Max: {current_max})"
            
        if is_abnormal:
            # Check duration? For now, immediate alert for MVP simplicity unless configured
            # To do duration, we'd need to fetch recent vitals and see if they are ALL abnormal.
            # Let's implement immediate alert first.
            
            # De-duplicate: Don't create new alert if there is already an OPEN alert for this type
            existing_alert = db.query(Alert).filter(
                Alert.patient_id == patient_id,
                Alert.vital_type == vital_type,
                Alert.status == AlertStatus.NEW
            ).first()
            
            if existing_alert:
                # Maybe update it or just ignore
                return
                
            print(f"Creating Alert: {reason}")
            alert = Alert(
                patient_id=patient_id,
                vital_type=vital_type,
                measured_value=value,
                severity=AlertSeverity.WARNING if "High" in reason else AlertSeverity.CRITICAL,
                reason=reason,
                status=AlertStatus.NEW
            )
            db.add(alert)
            db.commit()
    finally:
        db.close()
