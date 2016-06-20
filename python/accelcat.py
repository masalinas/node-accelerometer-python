# -*- coding: utf-8 -*-
''' Accelerometer, Velocity and Displacement python service'''
import time
import datetime
import numpy
import pandas
import json
import paho.mqtt.client as mqtt
from microstacknode.hardware.accelerometer.mma8452q import MMA8452Q

# accelerometer configuration and sample rate
MQTT_MESSAGE_BROKER_IP = '192.168.1.29'
MQTT_MESSAGE_BROKER_PORT = 1883
G_RANGE = 2
GRAVITY = 9.80665 # in SI units (m/s^2)
SAMPLE_CALIBRATION = 1024 # number of sampples
SAMPLE_FILTERING = 100 # rolling mean samples number
WINDOW_FILTERING = 20 # rolling mean window
#T = 0.5  # seconds sample rate (2 Hz)
#T = 0.2  # seconds sample rate (5 Hz)
T = 0.02  # seconds sample rate (50 Hz)
#T = 0.002  # seconds sample rate (500 Hz)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

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

    sstatex = sstatex / SAMPLE_CALIBRATION # m/s^2#
    sstatey = sstatey / SAMPLE_CALIBRATION # m/s^2
    sstatez = (sstatez / SAMPLE_CALIBRATION) - GRAVITY # m/s^2

    return (sstatex, sstatey, sstatez)

# low pass filtering: pandas rolling mean
def low_pass_filtering(s, N):
    return s.rolling(window=N, win_type='triang').mean()
           
if __name__ == '__main__':
    # STEP01: configure mqtt client and connect to message broker
    mqttc = mqtt.Client()
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message

    mqttc.connect(MQTT_MESSAGE_BROKER_IP, MQTT_MESSAGE_BROKER_PORT, 60)

    with MMA8452Q() as accelerometer:
        # STEP02: Configure accelerometer
        accelerometer.standby()
        accelerometer.set_g_range(G_RANGE)
        accelerometer.activate()
        print("g = {}".format(G_RANGE))
        time.sleep(T)

        # STEP03: auto-calibration
        Cax, Cay, Caz = auto_calibration()
        print('----')
        print(' calibration data | x: {}, y: {}, z: {}'.format(Cax, Cay, Caz))
        
        # initialize variables
        Aix = 0
        Aiy = 0
        Aiz = 0
        Vix = 0
        Viy = 0
        Viz = 0
        
        while True:
            # STEP04: apply a convolution filter to the three axis (moving average filter)
            # extract SAMPLE_FILTERING raw data from the three accelerometer axis
            index = range(0, SAMPLE_FILTERING)
            filtval = []
            for i in index:
                filtval.append(accelerometer.get_xyz_ms2())

            # create the data frame from the raw data to be filtered
            dataFrame = pandas.DataFrame(filtval, index=index, columns=list('xyz'))
            
            # apply the convolution filter with a window WINDOW_FILTERING samples of to the data frame
            dataFiltered = low_pass_filtering(dataFrame, WINDOW_FILTERING)

            # STEP05: calculate displacement and velocity using a trapezoidal method integration
            # velocity integration from acceleration
            # displacement integration from velocity
            # remove gravity from z axis
            for index, ms in dataFiltered.iterrows():
               if numpy.isnan(ms['z']):
                   continue
               
               if ms['x'] >=0:
                   Ax = (ms['x'] - Cax) * 1000 # mm/s^2
                   Vx = Aix * T + abs((Ax - Aix) / 2) * T # mm/s
                   Dx = Vix * T + abs((Vx - Vix) / 2) * T # mm
               else:
                   Ax = ms['x'] * 1000 # mm/s^2
                   Vx = Aix * T - abs((Ax - Aix) / 2) * T # mm/s
                   Dx = Vix * T - abs((Vx - Vix) / 2) * T # mm
                
               Aix = Ax
               Vix = Vx

               if ms['y'] >=0:
                   Ay = (ms['y'] - Cay) * 1000 # mm/s^2
                   Vy = Aiy * T + abs((Ay - Aiy) / 2) * T # mm/s
                   Dy = Viy * T + abs((Vy - Viy) / 2) * T # mm
               else:
                   Ay = ms['y'] * 1000 # mm/s^2
                   Vy = Aiy * T - abs((Ay - Aiy) / 2) * T # mm/s
                   Dy = Viy * T - abs((Vy - Viy) / 2) * T # mm           

               Aiy = Ay
               Viy = Vy

               if ms['z'] >=0:
                   Az = (ms['z'] - Caz - GRAVITY) * 1000 # mm/s^2
                   Vz = Aiy * T + abs((Ay - Aiz) / 2) * T # mm/s
                   Dz = Viy * T + abs((Vy - Viz) / 2) * T # mm
               else:
                   Az = (ms['z'] + GRAVITY) * 1000 # mm/s^2
                   Vz = Aiz * T - abs((Az - Aiz) / 2) * T # mm/s
                   Dz = Viz * T - abs((Vz - Viz) / 2) * T # mm

               Aiz = Az                                 
               Viz = Vz

               # create JSON data
               #data = {'tstamp': datetime.datetime.now().isoformat(),
               data = {'tstamp': time.mktime(datetime.datetime.now().timetuple()) + datetime.datetime.now().microsecond/1000000.0,
                       'D': {'x': Dx,
                             'y': Dy,
                             'z': Dz},
                       'V': {'x': Vx,
                             'y': Vy,
                             'z': Vz},
                       'A': {'x': Ax,
                             'y': Ay,
                             'z': Az}}
                       
               # logging result
               print("----")
               print(datetime.datetime.now())
               print('mm/s^2 | x: {:.2f}, y: {:.2f}, z: {:.2f}'.format(Ax, Ay, Az))
               print('mm/s | x: {:.2f}, y: {:.2f}, z: {:.2f}'.format(Vx, Vy, Vz))
               print('mm | x: {:.2f}, y: {:.2f}, z: {:.2f}'.format(Dx, Dy, Dz))

               # publish JSON result on message broker
               mqttc.publish("sensor/accelerometer", json.dumps(data))

               # sleep for the next data
               time.sleep(T)
