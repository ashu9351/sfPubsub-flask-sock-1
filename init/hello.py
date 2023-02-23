from flask import Flask,render_template,request,jsonify
from threading import Timer
import random
import time
from flask_sock import Sock
import grpc
import requests
import threading
import io
import pubsub_api_pb2 as pb2
import pubsub_api_pb2_grpc as pb2_grpc
import avro.schema
import avro.io
import time
import certifi
import json

#comment



app = Flask(__name__)
sock = Sock(app)
arg = [1]
counter = 0
@sock.route('/echo')
def test(sock):
    
    if counter == 0 :
        call_api(sock)
        
    '''starttime = time.time()
    while True:
       
        n = random.random()
        arg.append(n)
        print("again" , n)
        print("again" , arg)
        
        #time.sleep(5)'''

def auth():
    authurl = 'https://login.salesforce.com/services/oauth2/token'
    payload={
        'grant_type': 'password',
        'client_id': '3MVG9ZL0ppGP5UrAP59A8.dNkSsWx54hRgtkftFHZh1bxEMSGF6kwnRNA8VheLBe2RHROd01KucH2QHHt5ggh',
        'client_secret': '22883FEE07FDBA0FD71F317F8A4821155253D7853C280B4302EA229A30B1DDEF',
        'username': 'ashutoshexams@gmail.com',
        'password': 'ashutosh9351aozWQvXaav1CPDQaHHgtU7pQy',
        'organizationId': '00D28000000dVa8EAE'
    }
    '''payload = {
        'grant_type': 'password',
        'client_id': clientId,
        'client_secret': clientSecret,
        'username': username,
        'password': password,
    }'''
    res = requests.post(authurl, 
        headers={"Content-Type":"application/x-www-form-urlencoded"},
        data=payload)
    
    if res.status_code == 200:
        response = res.json()

        access_token = response['access_token']
        instance_url = response['instance_url']
        access_token = access_token.encode(encoding="ascii",errors="ignore").decode('utf-8')
        instance_url = instance_url.encode(encoding="ascii",errors="ignore").decode('utf-8')
        print(access_token)
        print(instance_url)
    
        
    authmetadata = (('accesstoken', access_token),('instanceurl', instance_url),('tenantid', '00D28000000dVa8EAE'))
    return authmetadata

def publishmessage(decodemsg,sock):
    message = 'Connected and waiting' if not(decodemsg) else json.loads(json.dumps(decodemsg))
    print("Got an event!", json.loads(json.dumps(decodemsg)))
               
    message = json.dumps(message)
    sock.send(message)

def call_api(sock):
    semaphore = threading.Semaphore(1)
    latest_replay_id = None
    global counter
    counter = 1
    print('counter called----------')
    
    print("tick")
    
    with open(certifi.where(), 'rb') as f:
        creds = grpc.ssl_channel_credentials(f.read())
    with grpc.secure_channel('api.pubsub.salesforce.com:7443', creds) as channel:
        authmetadata = auth()

        stub = pb2_grpc.PubSubStub(channel)       
        def fetchReqStream(topic):
            while True:
                semaphore.acquire()
                yield pb2.FetchRequest(            
                    topic_name = topic,
                    replay_preset = pb2.ReplayPreset.LATEST,num_requested = 1)

        def decode(schema, payload):
            schema = avro.schema.parse(schema)
            buf = io.BytesIO(payload)
            decoder = avro.io.BinaryDecoder(buf)
            reader = avro.io.DatumReader(schema)
            ret = reader.read(decoder)
            return ret

        mysubtopic = "/event/New_Fruit_Created__e" #"/data/AccountChangeEvent"
        print('Subscribing to ' + mysubtopic)
        print(authmetadata)
        substream = stub.Subscribe(fetchReqStream(mysubtopic),
                metadata=authmetadata)
        message = ''
        for event in substream:
            if event.events:
                semaphore.release()
                print("Number of events received: ", len(event.events))
                payloadbytes = event.events[0].event.payload
                schemaid = event.events[0].event.schema_id
                schema = stub.GetSchema(
                        pb2.SchemaRequest(schema_id=schemaid),
                        metadata=authmetadata).schema_json
                decoded = decode(schema, payloadbytes)
                publishmessage(decoded,sock)
               
                
            else:
                print("[", time.strftime('%b %d, %Y %l:%M%p %Z'),
                "] The subscription is active.")
                latest_replay_id = event.latest_replay_id 
        
   


@app.route('/')
def hello():
    
    return render_template('index.html')

#test()
@app.route('/second', methods=['GET', 'POST'])
def second():
   
    
    return render_template('second.html',data=arg)

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=80)
