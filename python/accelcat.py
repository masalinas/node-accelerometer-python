''' Prints the accelerometer values every second.'''
import time
import datetime
import json
import paho.mqtt.client as mqtt
from microstacknode.hardware.accelerometer.mma8452q import MMA8452Q

# accelerometer configuration and sample rate
G_RANGE = 2
GRAVITY = 9.80665 # in SI units (m/s^2)
SAMPLE_CALIBRATION = 1024 # number of calibration sampples
SAMPLE_LOW_FILTERING = 64
T = 0.2  # seconds sample rate (5 Hz)
#T = 0.02  # seconds sample rate (50 Hz)
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

# auto calibration function n start-up
def calibration():
    sstatex = 0
    sstatey = 0
    sstatez = 0
    for i in range(0, SAMPLE_CALIBRATION):
        ms = accelerometer.get_xyz_ms2()
        
        sstatex = sstatex + ms['x']
        sstatey = sstatey + ms['y']
        sstatez = sstatez + ms['z']

    sstatex = sstatex / 1024 # m/s^`2
    sstatey = sstatey / 1024 # m/s^`2
    sstatez = (sstatez / 1024) - GRAVITY # m/s^`2

    return (sstatex, sstatey, sstatez)

# low_filtering
# def low_filtering():
    
if __name__ == '__main__':
    mqttc = mqtt.Client()
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message

    mqttc.connect("192.168.1.29", 1883, 60)

    with MMA8452Q() as accelerometer:
        # Configure (This is completely optional -- shown here as an example)
        accelerometer.standby()
        accelerometer.set_g_range(G_RANGE)
        accelerometer.activate()
        print("g = {}".format(G_RANGE))
        time.sleep(T)  # settle

        # initial calibration
        print("------------------------------------------")
        print('Waiting for auto-calibration')
        Cax, Cay, Caz = calibration()
        print(' calibration data | x: {}, y: {}, z: {}'.format(Cax, Cay, Caz))

        # initialize velocity variables
        Aix = 0
        Aiy = 0
        Aiz = 0
        Vix = 0
        Viy = 0
        Viz = 0
        
        # print data
        while True:
            # get accelerometer data
            raw = accelerometer.get_xyz(raw=True)
            g = accelerometer.get_xyz()
            ms = accelerometer.get_xyz_ms2()
           
            # calculate velocity and position from acceleration
            if ms['x'] >=0:
                Ax = (ms['x'] - Cax) * 1000 # mm/s^`2
                Vx = Aix * T + abs((Ax - Aix) / 2) * T # mm/s
                Dx = Vix * T + abs((Vx - Vix) / 2) * T # mm
            else:
                Ax = ms['x'] * 1000 # mm/s^`2
                Vx = Aix * T - abs((Ax - Aix) / 2) * T # mm/s
                Dx = Vix * T - abs((Vx - Vix) / 2) * T # mm
                
            Aix = Ax
            Vix = Vx

            if ms['y'] >=0:
                Ay = (ms['y'] - Cay) * 1000 # mm/s^`2
                Vy = Aiy * T + abs((Ay - Aiy) / 2) * T # mm/s
                Dy = Viy * T + abs((Vy - Viy) / 2) * T # mm
            else:
                Ay = ms['y'] * 1000 # mm/s^`2
                Vy = Aiy * T - abs((Ay - Aiy) / 2) * T # mm/s
                Dy = Viy * T - abs((Vy - Viy) / 2) * T # mm           

            Aiy = Ay
            Viy = Vy

            if ms['z'] >=0:
                Az = (ms['z'] - Caz - GRAVITY) * 1000 # mm/s^`2
                Vz = Aiy * T + abs((Ay - Aiz) / 2) * T # mm/s
                Dz = Viy * T + abs((Vy - Viz) / 2) * T # mm
            else:
                Az = (ms['z'] + GRAVITY) * 1000 # mm/s^`2
                Vz = Aiz * T - abs((Az - Aiz) / 2) * T # mm/s
                Dz = Viz * T - abs((Vz - Viz) / 2) * T # mm

            Aiz = Az                                 
            Viz = Vz

            # create measure JSON data
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
                          'z': Az}
                   }

            print("------------------------------------------")
            print(datetime.datetime.now())
            print('   raw | x: {}, y: {}, z: {}'.format(raw['x'], raw['y'], raw['z']))
            print('     G | x: {:.2f}, y: {:.2f}, z: {:.2f}'.format(g['x'], g['y'], g['z']))
            print('mm/s^2 | x: {:.2f}, y: {:.2f}, z: {:.2f}'.format(Ax, Ay, Az))
            print('mm/s   | x: {:.2f}, y: {:.2f}, z: {:.2f}'.format(Vx, Vy, Vz))
            print('mm     | x: {:.2f}, y: {:.2f}, z: {:.2f}'.format(Dx, Dy, Dz))

            mqttc.publish("sensor/accelerometer", json.dumps(data))

            time.sleep(T)
