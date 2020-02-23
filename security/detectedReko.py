from gpiozero import MotionSensor,Buzzer
import picamera
import telegram
import time
import boto3
import botocore
import json
from twilio.rest import Client

# Sends a message to SMS
account_sid = "AC7d12b851012a4f9eb3858b26239678c5"
auth_token = "eabc0e5e668edbc2601dc1848c134cea"
client = Client(account_sid, auth_token)
my_hp = "+6588692298"
twilio_hp = "+13852194395"

# Set the filename and bucket name
BUCKET = 'sp-p1844331-s3-bucket' # replace with your own unique bucket name
location = {'LocationConstraint': 'us-east-1'}
file_path = "."
file_name = "test.jpg"

# Connect to motion sensor and buzzer
pir = MotionSensor(26, sample_rate=5,queue_len=1)
bz = Buzzer(5)

# Connect to our bot
bot = telegram.Bot(token="778518288:AAEpuWpCgYH2YF3bK0CZDGg6tEvVjjiT43E")

# Sets the id for the active chat
chat_id=638292737

# Minimum time between captures
DELAY = 5

def uploadToS3(file_path,file_name, bucket_name,location):
    s3 = boto3.resource('s3') # Create an S3 resource
    exists = True

    try:
        s3.meta.client.head_bucket(Bucket=bucket_name)
    except botocore.exceptions.ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            exists = False

    if exists == False:
        s3.create_bucket(Bucket=bucket_name,CreateBucketConfiguration=location)
    
    # Upload the file
    full_path = file_path + "/" + file_name
    s3.Object(bucket_name, file_name).put(Body=open(full_path, 'rb'))
    print("File uploaded")


def detect_labels(bucket, key, max_labels=10, min_confidence=90, region="us-east-1"):
	rekognition = boto3.client("rekognition", region)
	response = rekognition.detect_labels(
		Image={
			"S3Object": {
				"Bucket": bucket,
				"Name": key,
			}
		},
		MaxLabels=max_labels,
		MinConfidence=min_confidence,
	)
	return response['Labels']


def detect_faces(bucket, key, max_labels=10, min_confidence=90, region="us-east-1"):
	rekognition = boto3.client("rekognition", region)
	response = rekognition.detect_faces(
		Image={
			"S3Object": {
				"Bucket": bucket,
				"Name": key,
			}
		},
		Attributes=['ALL']
	)
	return response['FaceDetails']

def takePhoto(file_path,file_name):
    with picamera.PiCamera() as camera:
        while True:
            full_path = file_path + "/" + file_name
            bz.off()
            pir.wait_for_motion()
            timestring = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
            bz.on()
            print ("Taking photo " +timestring)
            camera.capture(full_path)
            bz.off()
            message = "Motion detected at " + timestring + ", taking photo..."
            bot.sendMessage(chat_id=chat_id, text=message)
            bot.sendPhoto(chat_id=chat_id, photo=open(full_path, 'rb'))
            sms = "Motion detected at " + timestring + ", check the taken photo online now."
            print(sms)
            message = client.api.account.messages.create(to=my_hp,
                                                        from_=twilio_hp,
                                                        body=sms)
            uploadToS3(file_path,file_name, BUCKET,location)
            print('Detected faces for')    
            for faceDetail in detect_faces(BUCKET, file_name):
                ageLow = faceDetail['AgeRange']['Low']
                ageHigh = faceDetail['AgeRange']['High']
                print('Age between {} and {} years old'.format(ageLow,ageHigh))
                print('Here are the other attributes:')
                print(json.dumps(faceDetail, indent=4, sort_keys=True))
            time.sleep(DELAY)
        
        
takePhoto(file_path, file_name)