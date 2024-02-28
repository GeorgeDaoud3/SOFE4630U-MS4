import glob, os
from google.cloud import pubsub_v1      #pip install google-cloud-pubsub  ##to install
import redis        # pip install redis
import time

files=glob.glob("*.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=files[0];
redis_ip = os.environ["REDIS_IP"];
project_id = os.environ["GCP_PROJECT"];
subscription_id = os.environ["ELECTION_SUB_ID"];
topic_name = os.environ["TOPIC_NAME"];

print(files[0])
print(redis_ip)
print(project_id)
print(subscription_id)
print(topic_name)

for i in range(60):
    try:
        redis = redis.Redis(host=redis_ip, port=6379, db=0,password='election')
        time.sleep(1);
        redis.ping() 
        print('connected to redis');
        break;
    except:
        print('failed to connect to redis');
        
    
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_id)
topic_path = 'projects/{project_id}/topics/{topic}'.format(
    project_id=project_id,
    topic=topic_name,  # Set this to something appropriate.
)
sub_filter = "attributes.function=\"submit vote\""

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_name)

import json

def callback(message: pubsub_v1.subscriber.message.Message) -> None:

    message_data = json.loads(message.data);
    print(f"Received {message_data}.")
    #try:
    if(redis.exists(str(message_data["voter_ID"])+","+str(message_data['election_ID']))):
        value={'result': 'Already Voted!!!','UUID': message_data['UUID']}
        future = publisher.publish(topic_path, json.dumps(value).encode('utf-8'),function="result",machineID=str(message_data['machine_ID']));
    else:
        redis.set(str(message_data["voter_ID"])+","+str(message_data['election_ID']),message_data["timestamp"])
        value={'machine_ID': message_data['machine_ID'], 'voting': message_data['voting'], 'election_ID': message_data['election_ID'], 'UUID': message_data['UUID']}
        print(value)
        future = publisher.publish(topic_path, json.dumps(value).encode('utf-8'),function="record vote");
    #except:
        #pass;
    message.ack()
    


print(f"Listening for messages on {subscription_path}..\n")

with subscriber:
    try:
        subscription = subscriber.create_subscription(
                request={"name": subscription_path, "topic": topic_path, "filter": sub_filter}
            )
    except:
        pass;
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    try:
        streaming_pull_future.result()
    except KeyboardInterrupt:
        streaming_pull_future.cancel()
