import time
import random

def on_event(event, context):
    # this is to seed some time seperate between the creation of accounts, to help avoid race conditions
    # where two accounts are trying to start at the same time. 
    time.sleep(random.randint(0,180))
    return {'PhysicalResourceId': event['ResourceProperties']['PhysicalResourceId']}
    
