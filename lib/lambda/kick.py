import time

def on_event(event, context):
    # this is to seed some time seperate between the creation of accounts, to help avoid race conditions
    # where two accounts are trying to start at the same time. 
    print('on event does not need to do anything, everything is handled by the iscomplete handler')
    return {'PhysicalResourceId': event['ResourceProperties']['PhysicalResourceId']}
    
