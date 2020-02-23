import time
from gpiozero import MCP3008, LED
from blynkapi import Blynk
from time import sleep

auth_token = "cIcy124bygB-GEiFr58bq5Mx9KPWW-9s"

led = LED(4)
adc = MCP3008(channel=0)

while True:
  try:

    button = Blynk(auth_token, pin = "V0")
    button_val = str(button.get_val()[0])
    print("Button value is %s" %(button_val))
    if button_val=="1":
      led.on()
    else:
      led.off()

    light = Blynk(auth_token, pin = "V1")
    light_sensor_value = adc.value*1024+1
    s_light_sensor_value = str(light_sensor_value)
    fs_light_sensor_value = "[\""+ s_light_sensor_value+"\"]"
    print("Light sensor value is %s" %(fs_light_sensor_value))
    light.set_val_old(fs_light_sensor_value)

    time.sleep(1)

  except KeyboardInterrupt:
    print "Program aborted"
    sys.exit()

  except:
    print "Unexpected error:", sys.exc_info()[0]
    sys.exit()

