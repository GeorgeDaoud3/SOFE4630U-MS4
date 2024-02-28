import glob, os
from google.cloud import pubsub_v1      #pip install google-cloud-pubsub  ##to install
import time
import json;
import random
import threading
import uuid

files=glob.glob("*.json")
if len(files)>0:
   os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=files[0];

project_id = ""
topic_name = ""

electionID = int(input("Please enter the election ID (integer): "))
machineID = int(input("Please enter the machine ID (integer): "))

if "ELECTION_SUB_ID" in os.environ:
    subscription_id = os.environ["ELECTION_SUB_ID"];
else: 
    subscription_id = "ex_election-result-"+str(machineID)+"-sub_tmp2"
    
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_name)

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_id)
print(subscription_path)
topic_path = 'projects/{project_id}/topics/{topic}'.format(
    project_id=project_id,
    topic=topic_name,  # Set this to something appropriate.
)
print(topic_path)
sub_filter = "attributes.function=\"result\" AND attributes.machineID=\""+str(machineID)+"\"";
print(sub_filter)

messageRecieved=False;
last_uuid='';
def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    global last_uuid,messageRecieved
    message_data = json.loads(message.data);
    print(f"Received {message_data}.")
    if last_uuid==message_data['UUID'] :
        messageRecieved=True;
    message_data = json.loads(message.data);
    message.ack()
    
    
def thread_function():
    with subscriber:
        try:
            subscription = subscriber.create_subscription(
                    request={"name": subscription_path, "topic": topic_path, "filter": sub_filter}
                )
        except:
            pass
        streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
        try:
            streaming_pull_future.result()
        except KeyboardInterrupt:
            streaming_pull_future.cancel()
            return
    
    
x = threading.Thread(target=thread_function)
x.start()
    
while True:
    last_uuid=str(uuid.uuid1())
    messageRecieved=False;
    value={'machine_ID': machineID, 'voter_ID': int(random.random()*100), 
           'voting': int(random.random()*5), 'election_ID': electionID, 'UUID': last_uuid,
           'timestamp':int(1000*time.time())}
    future = publisher.publish(topic_path, json.dumps(value).encode('utf-8'),function="submit vote");
    print("The message "+str(value)+" is sent")
    c=1;
    while( messageRecieved==False):
        time.sleep(0.01);
        c=c+1;
        if(c==1000):
            print('time out')
            break;
    time.sleep(1);
    
    
    
    