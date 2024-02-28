import glob, os
from google.cloud import pubsub_v1      #pip install google-cloud-pubsub  ##to install
import psycopg2
import time

files=glob.glob("*.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=files[0];
postgres_host = os.environ["POSTGRES_HOST"];
project_id = os.environ["GCP_PROJECT"];
subscription_id = os.environ["ELECTION_SUB_ID"];
topic_name = os.environ["TOPIC_NAME"];

print(files[0]);
print(postgres_host);
print(project_id);
print(subscription_id);
print(topic_name);
c=0;
while True:
    try:
        conn = psycopg2.connect(database = "election", 
                user = "admin", 
                host= postgres_host,
                password = "adminpassword",
                port = 5432)
        print('Successfully connected to POSTGRES server');
        break;
    except:
        print('Waiting for POSTGRES server');
        time.sleep(10);
        c=c+1;
        if c>=60:
            break;
        
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_id)
topic_path = 'projects/{project_id}/topics/{topic}'.format(
    project_id=project_id,
    topic=topic_name,  # Set this to something appropriate.
)
sub_filter = "attributes.function=\"record vote\""

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_name)
conn.autocommit = True

import json

def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    global conn
    message_data = json.loads(message.data);
    print(f"Received {message_data}.")
    value={'result': 'successful','UUID': message_data['UUID']}
    
    mycursor = conn.cursor()

    sql = "INSERT INTO votes (electionID, machineID, voting) VALUES (%s, %s, %s)"
    val = (message_data['election_ID'], message_data['machine_ID'], message_data['voting'])
    mycursor.execute(sql, val)

    conn.commit()

    future = publisher.publish(topic_path, json.dumps(value).encode('utf-8'),function="result",machineID=str(message_data['machine_ID']));
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
