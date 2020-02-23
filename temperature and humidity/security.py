from gpiozero import MCP3008
from gpiozero import Buzzer
from gpiozero import MotionSensor
from time import time
from time import sleep

from twilio.rest import Client

pir = MotionSensor(26, sample_rate=5,queue_len=1)
bz = Buzzer(5)

account_sid = "AC2c93ac93d1b535cb4cc943bbda8fbed7"
auth_token = "eeaa2ed6768129d4ca22c355fc1693ed"
client = Client(account_sid, auth_token)

my_hp = "+6596651442"
twilio_hp = "+15702410802"

adc = MCP3008(channel=0)

while True:   
   bz.off()
   old_time = time()
   pir.wait_for_motion()
   new_time = time()
   if new_time - old_time > 1:
      print("Motion detected after {:.2f} seconds".format(new_time-
            old_time))
      bz.on()
      sleep(1)
      bz.off()
   old_time = new_time
   pir.wait_for_no_motion()
   new_time = time() 
   sms = "Someone move the device!!!"
   print(sms)
   message = client.api.account.messages.create(to=my_hp,
                                                from_=twilio_hp,
                                                body=sms) 
   sleep(60*10)
