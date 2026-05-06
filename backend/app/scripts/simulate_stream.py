import time
import random
import logging
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.models.vital import Vital

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("simulator")

# Simulation Constants (WESAD-like patterns)
ACTIVITIES = ["Resting", "Walking", "Running"]
VITALS_CONFIG = {
    "Resting": {"hr": (60, 80), "spo2": (97, 99), "temp": (36.5, 37.0), "bp_sys": (110, 120), "bp_dia": (70, 80)},
    "Walking": {"hr": (85, 110), "spo2": (96, 98), "temp": (36.8, 37.2), "bp_sys": (120, 130), "bp_dia": (75, 85)},
    "Running": {"hr": (130, 170), "spo2": (95, 97), "temp": (37.0, 38.0), "bp_sys": (140, 160), "bp_dia": (80, 90)},
}

def get_demo_patient(db: Session):
    return db.query(User).filter(User.email == "patient@rpm.com").first()

def generate_packet(patient_id: UUID, current_activity: str):
    config = VITALS_CONFIG[current_activity]
    
    # Randomize
    hr = random.normalvariate((config["hr"][0] + config["hr"][1])/2, 5)
    spo2 = random.uniform(*config["spo2"])
    temp = random.normalvariate((config["temp"][0] + config["temp"][1])/2, 0.2)
    bp_sys = random.randint(*config["bp_sys"])
    bp_dia = random.randint(*config["bp_dia"])

    ts = datetime.utcnow()
    
    return [
        Vital(patient_id=patient_id, ts=ts, vital_type="heart_rate", value=hr, unit="bpm", source="DATASET", activity_label=current_activity),
        Vital(patient_id=patient_id, ts=ts, vital_type="spo2", value=spo2, unit="%", source="DATASET", activity_label=current_activity),
        Vital(patient_id=patient_id, ts=ts, vital_type="temperature", value=temp, unit="C", source="DATASET", activity_label=current_activity),
         # Storing BP as separate for simplicity in this demo, or skipping chart for now.
         # Let's add them so manual entry matches.
        Vital(patient_id=patient_id, ts=ts, vital_type="blood_pressure_sys", value=bp_sys, unit="mmHg", source="DATASET", activity_label=current_activity),
        Vital(patient_id=patient_id, ts=ts, vital_type="blood_pressure_dia", value=bp_dia, unit="mmHg", source="DATASET", activity_label=current_activity),
    ]

from app.services.alert_rules import check_vital_alert

def run_simulation():
    logger.info("Starting WESAD/HAR Dataset Simulator...")
    db = SessionLocal()
    
    try:
        patient = get_demo_patient(db)
        # ... catch logic ...

        while True:
            # Change activity occasionally
            if counter % 10 == 0:
                current_activity = random.choice(ACTIVITIES)
                logger.info(f"Activity Changed to: {current_activity}")

            vitals = generate_packet(patient.id, current_activity)
            db.add_all(vitals)
            db.commit() # Commit vitals first to get IDs if needed
            
            # Check Alerts
            for v in vitals:
                check_vital_alert(db, v)
            db.commit() # Commit alerts
            
            logger.info(f"Ingested {len(vitals)} vitals for {patient.email} [{current_activity}]")
            
            counter += 1
            time.sleep(5) # 5 seconds interval for demo speed
            
    except KeyboardInterrupt:
# ...
        logger.info("Stopping simulator...")
    finally:
        db.close()

if __name__ == "__main__":
    run_simulation()
