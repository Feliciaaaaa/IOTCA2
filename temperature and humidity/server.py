from flask import Flask, render_template, jsonify, request,Response

import mysql.connector
import sys

import json
import numpy
import datetime
import decimal

import gevent
import gevent.monkey
from gevent.pywsgi import WSGIServer

gevent.monkey.patch_all()


class GenericEncoder(json.JSONEncoder):
    
    def default(self, obj):  
        if isinstance(obj, numpy.generic):
            return numpy.asscalar(obj) 
        elif isinstance(obj, datetime.datetime):  
            return obj.strftime('%Y-%m-%d %H:%M:%S') 
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        else:  
            return json.JSONEncoder.default(self, obj) 

def data_to_json(data):
    json_data = json.dumps(data,cls=GenericEncoder)
    return json_data

def connect_to_mysql(host,user,password,database):
    try:
        cnx = mysql.connector.connect(host=host,user=user,password=password,database=database)

        cursor = cnx.cursor()
        print("Successfully connected to database!")

        return cnx,cursor

    except:
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])

        return None

def fetch_fromdb_as_json(cnx,cursor,sql):
    
    try:
        cursor.execute(sql)
        row_headers=[x[0] for x in cursor.description] 
        results = cursor.fetchall()
        data = []
        for result in results:
            data.append(dict(zip(row_headers,result)))
        
        data_reversed = data[::-1]

        data = {'data':data_reversed}

        return data_to_json(data)

    except:
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])
        return None
                            

app = Flask(__name__)

@app.route("/api/getdata",methods = ['POST', 'GET'])
def apidata_getdata():
    if request.method == 'POST':
        try:
            host='localhost'; user='iotuser'; password='dmitiot'; database='iotdatabase';
            sql="SELECT * FROM lights ORDER BY datetime_value DESC LIMIT 10"
            cnx,cursor = connect_to_mysql(host,user,password,database)
            json_data = fetch_fromdb_as_json(cnx,cursor,sql)
            loaded_r = json.loads(json_data)
            data = {'chart_data': loaded_r, 'title': "IOT Data"}
            return jsonify(data)
        except:
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])

@app.route("/")
def chartsimple():
    return render_template('index.html')
from gpiozero import LED
led = LED(18)

def ledOn():
  led.on()
  return "On"

def ledOff():
  led.off()
  return "Off"

@app.route("/writeLED/<status>")
def writePin(status):

   if status == 'On':
     response = ledOn()
   else:
     response = ledOff()

   return response

import Adafruit_DHT
pin = 4

@app.route("/getDHT",methods = ['POST', 'GET'])
def getDHT():
    humidity, temperature = Adafruit_DHT.read_retry(11, pin)
    #import random
    #humidity, temperature = random.randint(1,100), random.randint(20,30)
    data = {'temperature': temperature, 'humidity': humidity}
    print(data)
    return jsonify(data)

if __name__ == '__main__':
   try:
        print('Server waiting for requests')
        http_server = WSGIServer(('0.0.0.0', 8001), app)
        app.debug = True
        http_server.serve_forever()
   except:
        print("Exception")
        import sys
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])

