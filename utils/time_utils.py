from datetime import datetime, time
import pytz
from config import NY_START, NY_END

def es_horario_ny():
    tz_ny = pytz.timezone('America/New_York')
    ahora_ny = datetime.now(tz_ny).time()
    return time(*NY_START) <= ahora_ny <= time(*NY_END) 