from Test2_2 import snapshot
from datetime import datetime, timedelta
from logzero import logger, logfile
from pathlib import Path
from time import sleep

base_folder = Path(__file__).parent.resolve()
logfile(base_folder/"events.log")

    
 
# Create a `datetime` variable to store the start time
start_time = datetime.now()
# Create a `datetime` variable to store the current time
# (these will be almost the same at the start)
now_time = datetime.now()
# Run a loop for 2 minutes
while (now_time < start_time + timedelta(minutes=175)):
  try:
    snapshot()
    sleep(1)
    # Update the current time
    now_time = datetime.now() 
  except Exception as e:
    logger.error(f'{e.__class__.__name__}: {e})')
