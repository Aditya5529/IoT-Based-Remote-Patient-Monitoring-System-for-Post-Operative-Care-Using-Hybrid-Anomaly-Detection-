# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.session import Base
from app.models.user import User
from app.models.vital import Vital
from app.models.threshold import Threshold
from app.models.alert import Alert
from app.models.message import Message
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.iot import IoTDevice, IoTVital

