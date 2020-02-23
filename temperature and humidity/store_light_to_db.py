from gpiozero import MCP3008
import mysql.connector
from time import sleep
import sys

try:
    mcp3008 = MCP3008(channel=0)
    u='iotuser';pw='dmitiot';
    h='localhost';db='iotdatabase'

    cnx = mysql.connector.connect(user=u,password=pw,host=h,database=db) 
    cursor = cnx.cursor()
    print("Successfully connected to database!")
    
    update = True
    while update:
      try:
         sensor_value = (1024*(1.0-mcp3008.value))
         sensor_value = round(sensor_value)
         print("Sensor value:", sensor_value)
         sql = "INSERT INTO lights (light_value) VALUES (%(val)s)"
         cursor.execute(sql, {'val': sensor_value })
         cnx.commit()
         print("Wait 2 secs before getting next light values..")
         sleep(2)
      except mysql.connector.Error as err:
         print(err)
      except KeyboardInterrupt:
         update = False
         cursor.close()
         cnx.close()
      except:
         print("Error while inserting data...")
         print(sys.exc_info()[0])
         print(sys.exc_info()[1])
except:
    print(sys.exc_info()[0])
    print(sys.exc_info()[1])

