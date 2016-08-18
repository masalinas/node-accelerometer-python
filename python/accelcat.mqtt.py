#!/usr/bin/env python3
# -*- coding: utf-8 -*-

''' Accelerometer, Velocity and Displacement python service'''
import time
import datetime
import numpy
import pandas
import json
import math
import paho.mqtt.client as mqtt
from microstacknode.hardware.accelerometer.mma8452q import MMA8452Q

# accelerometer configuration and sample rate
MQTT_MESSAGE_BROKER_IP = '54.213.197.15' # mqtt default server
MQTT_MESSAGE_BROKER_PORT = 1883 # mqtt default port
MQTT_MESSAGE_KEEPALIVE = 43200 # 12 horas
MQTT_MESSAGE_PUB_SENSOR = 'sensor/pub/accelerometer' # default mqtt publish sensor topic 
MQTT_MESSAGE_SUB_SENSOR = 'sensor/sub/accelerometer' # default mqtt subscrtiber sensor topic 
MQTT_IS_CONNECTED = 0 # Mqtt status connection
MQTT_RECONNECTION_FREC = 5 # reconnection frecuency in seconds

G_RANGE = 2
GRAVITY = 9.80665 # in SI units (m/s^2)
SAMPLE_CALIBRATION = 1024 # number of sampples
SAMPLE_FILTERING = 100 # rolling mean samples number
WINDOW_FILTERING = 20 # rolling mean window
#T = 0.2  # seconds. Sample rate (5 Hz)
T = 0.02  # seconds. Sample rate (50 Hz)
#T = 0.002  # seconds. Sample rate (500 Hz)
R = 6 # sample transport rate in minutes

def reconnect():
    global MQTT_IS_CONNECTED
    while(MQTT_IS_CONNECTED == 0):
       try:
          mqttc.reconnect()
          
          #print("Reconnected to MQTT server: {} in the port: {} with result code: ".format(MQTT_MESSAGE_BROKER_IP, MQTT_MESSAGE_BROKER_PORT) + str(0) + "\n")
          MQTT_IS_CONNECTED = 1
           
       except Exception as e:
          print("Error reconnecting with error: " + str(e))
             
          time.sleep(MQTT_RECONNECTION_FREC) 

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT server: {} in the port: {} with result code: ".format(MQTT_MESSAGE_BROKER_IP, MQTT_MESSAGE_BROKER_PORT) + str(rc) + "\n")
    global MQTT_IS_CONNECTED
    MQTT_IS_CONNECTED = 1

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    mqttc.subscribe(MQTT_MESSAGE_SUB_SENSOR, qos=1)
    print("Subscribe to MQTT topic: {}".format(MQTT_MESSAGE_SUB_SENSOR) + "\n")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print("Message from topic: " + msg.topic + ", message payload: " + str(msg.payload) + "\n")

# The callback for when the client receives a DISCONNECT response from server
def on_disconnect(client, userdata, rc):
    print("Disconnected from MQTT server: {} in the port: {} with result code: ".format(MQTT_MESSAGE_BROKER_IP, MQTT_MESSAGE_BROKER_PORT) + str(rc) + "\n")
    global MQTT_IS_CONNECTED
    MQTT_IS_CONNECTED = 0

    if rc != 0:
        print("Unexpected MQTT disconnection. Attempting to reconnect.")
        reconnect()

# calibration: This calibration routine removes the acceleration offset component in the sensor output due
# to the earth's gravity (static acceleration)
def auto_calibration():
    sstatex = 0
    sstatey = 0
    sstatez = 0
    for i in range(0, SAMPLE_CALIBRATION):
        ms = accelerometer.get_xyz_ms2()
        
        sstatex = sstatex + ms['x']
        sstatey = sstatey + ms['y']
        sstatez = sstatez + ms['z']

    sstatex = sstatex / SAMPLE_CALIBRATION  # m/s^2
    sstatey = sstatey / SAMPLE_CALIBRATION # m/s^2
    sstatez = (sstatez / SAMPLE_CALIBRATION) - GRAVITY # m/s^2

    return (sstatex, sstatey, sstatez)

# low pass filtering: pandas rolling mean
def low_pass_filtering(s, N):
    # return pandas.rolling_mean(x, N)[N-1:]
    return s.rolling(window=N, win_type='triang').mean()
           
if __name__ == '__main__':
    # STEP01: initialize transport time and final meassures
    ti = time.time()

    AxF=0
    AyF=0
    AzF=0
    VxF=0
    VyF=0
    VzF=0
    DxF=0
    DyF=0
    DzF=0

    # STEP02: configure mqtt client and connect to message broker
    # be careful with the version used: 3.1 or 3.1.1. Not all mqtt message broker implement the last default version used by paho client
    #mqttc = mqtt.Client(client_id="accelcal", clean_session=False) # if use mosca mqtt broker we can use the default version 3.1.1
    mqttc = mqtt.Client(client_id="accelcal", clean_session=False, protocol=mqtt.MQTTv31) #if use ActiveMQ message broker not implement version 3.1.1, specifie the version 3.1
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.on_disconnect = on_disconnect

    try:
         print("Connection to Server: {} and port: {}".format(MQTT_MESSAGE_BROKER_IP, MQTT_MESSAGE_BROKER_PORT))
         # mqttc.connect(MQTT_MESSAGE_BROKER_IP, MQTT_MESSAGE_BROKER_PORT, MQTT_MESSAGE_KEEPALIVE)
         mqttc.connect(MQTT_MESSAGE_BROKER_IP, MQTT_MESSAGE_BROKER_PORT)
    except Exception as e:
         print("Error reconnecting with error: " + str(e))

         print("Unexpected MQTT disconnection. Attempting to reconnect.")
         reconnect() 
    finally:
         mqttc.loop_start()

    # connect to the accelerometer device MMA8452Q
    with MMA8452Q() as accelerometer:
        # STEP03: Configure accelerometer
        accelerometer.standby()
        accelerometer.set_g_range(G_RANGE)
        accelerometer.activate()
        print("Accelerometer G range configuration = {}".format(G_RANGE) + "\n")
        time.sleep(T)

        # STEP04: auto-calibration
        Cax, Cay, Caz = auto_calibration()
        print('----')
        print('Auto-calibration data | x: {}, y: {}, z: {}'.format(Cax, Cay, Caz) + "\n")
        
        Aix = 0
        Aiy = 0
        Aiz = 0
        Vix = 0
        Viy = 0
        Viz = 0
        
        while True:
            # STEP05: apply a convolution filter to the three axis (moving average filter)
            # extract the raw data from the three accelerometer axis
            index = range(0, SAMPLE_FILTERING)
            filtval = []
            for i in index:
                filtval.append(accelerometer.get_xyz_ms2())

            # create the data frame from the raw data to be filtered
            dataFrame = pandas.DataFrame(filtval, index=index, columns=list('xyz'))
            
            # apply the convolution filter to the data frame
            dataFiltered = low_pass_filtering(dataFrame, WINDOW_FILTERING)

            for index, ms in dataFiltered.iterrows():
               # STEP06: calculate displacement and velocity using a trapezoidal method integration
               # velocity integration from acceleration
               # displacement integration from velocity
               # remove gravity from z axis
               if numpy.isnan(ms['z']):
                   continue

               if ms['x'] >=0:
                   Ax = (ms['x'] - Cax) * 1000 # mm/s^2
                   Vx = Aix * T + abs((Ax - Aix) / 2) * T # mm/s
                   Dx = Vix * T + abs((Vx - Vix) / 2) * T # mm
               else:
                   Ax = (ms['x'] - Cax) * 1000 # mm/s^2
                   Vx = Aix * T - abs((Ax - Aix) / 2) * T # mm/s
                   Dx = Vix * T - abs((Vx - Vix) / 2) * T # mm
                
               Aix = Ax
               Vix = Vx

               if ms['y'] >=0:
                   Ay = (ms['y'] - Cay) * 1000 # mm/s^2
                   Vy = Aiy * T + abs((Ay - Aiy) / 2) * T # mm/s
                   Dy = Viy * T + abs((Vy - Viy) / 2) * T # mm
               else:
                   Ay = (ms['y'] - Cay) * 1000 # mm/s^2
                   Vy = Aiy * T - abs((Ay - Aiy) / 2) * T # mm/s
                   Dy = Viy * T - abs((Vy - Viy) / 2) * T # mm           

               Aiy = Ay
               Viy = Vy

               if ms['z'] >=0:
                   Az = (ms['z'] - Caz - GRAVITY) * 1000 # mm/s^2
                   Vz = Aiz * T + abs((Az - Aiz) / 2) * T # mm/s
                   Dz = Viz * T + abs((Vz - Viz) / 2) * T # mm
               else:
                   Az = (ms['z'] - Caz + GRAVITY) * 1000 # mm/s^2
                   Vz = Aiz * T - abs((Az - Aiz) / 2) * T # mm/s
                   Dz = Viz * T - abs((Vz - Viz) / 2) * T # mm

               Aiz = Az                                 
               Viz = Vz
               
               # STEP07: get the maximun value in the three axis
               if VxF < abs(Vx):
                  AxF = abs(Ax)
                  VxF = abs(Vx)
                  DxF = abs(Dx)		              

               if VyF < abs(Vy):
                  AyF = abs(Ay)
                  VyF = abs(Vy)
                  DyF = abs(Dy)

               if VzF < abs(Vz):
                  AzF = abs(Az)
                  VzF = abs(Vz)
                  DzF = abs(Dz)
               
               # STEP08: create JSON data after transport rate
               if (time.time() - ti) > R * 60:
                 data = {'tstamp': datetime.datetime.now().isoformat(),
                 #data = {'tstamp': time.mktime(datetime.datetime.now().timetuple()) + datetime.datetime.now().microsecond/1000000.0,
                       'D': {'x': DxF,
                             'y': DyF,
                             'z': DzF},
                       'V': {'x': VxF,
                             'y': VyF,
                             'z': VzF},
                       'A': {'x': AxF,
                             'y': AyF,
                             'z': AzF}}
                       
                 # logging result
                 print("----")
                 print(datetime.datetime.now())
                 print('Acceleration [mm/s^2] | x: {:.2f}, y: {:.2f}, z: {:.2f}'.format(AxF, AyF, AzF))
                 print('Velocity [mm/s] | x: {:.2f}, y: {:.2f}, z: {:.2f}'.format(VxF, VyF, VzF))
                 print('Distance [mm] | x: {:.2f}, y: {:.2f}, z: {:.2f}'.format(DxF, DyF, DzF))
                 print("\n")

                 # publish JSON result on message broker
                 print("Mqtt status: {}".format(MQTT_IS_CONNECTED))
                 if MQTT_IS_CONNECTED == 1:
                     (rc, mid) = mqttc.publish(MQTT_MESSAGE_PUB_SENSOR, json.dumps(data))
                     print("rc: {} | mid: {} | data: {}".format(rc, mid, json.dumps(data)))
                     print('Mqtt Published correctly')

                 # initialize transport time and final meassures
                 ti = time.time()

                 AxF=0
                 AyF=0
                 AzF=0
                 VxF=0
                 VyF=0
                 VzF=0
                 DxF=0
                 DyF=0
                 DzF=0

               # next data (T sample rate) 
               time.sleep(T)
