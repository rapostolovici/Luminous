from Test2_2 import snapshot
from datetime import datetime, timedelta
# Create a `datetime` variable to store the start time
start_time = datetime.now()
# Create a `datetime` variable to store the current time
# (these will be almost the same at the start)
now_time = datetime.now()
# Run a loop for 2 minutes
while (now_time < start_time + timedelta(minutes=180)):
    print("Doing stuff")
    sleep(1)
    # Update the current time
    now_time = datetime.now()
for i in range(2):#we will specify the exact amount of time our program will execute, that meaning for 3 hours
  snapshot()
