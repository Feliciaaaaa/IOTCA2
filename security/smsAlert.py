from gpiozero import MCP3008
from time import sleep

from twilio.rest import Client

account_sid = "AC7d12b851012a4f9eb3858b26239678c5"
auth_token = "eabc0e5e668edbc2601dc1848c134cea"
client = Client(account_sid, auth_token)

my_hp = "+6588692298"
twilio_hp = "+13852194395"

adc = MCP3008(channel=0)

while True:   
   light_value = adc.value
   print(light_value)
   if adc.value>0.8:
      sms = "All the staff has left the room, the motion sensor will be turned on."
      print(sms)
      message = client.api.account.messages.create(to=my_hp,
                                                from_=twilio_hp,
                                                body=sms)
      break
   else:
      sleep(3)
