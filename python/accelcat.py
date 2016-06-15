''' Prints the accelerometer values every second.'''
import time
import datetime
import json
import paho.mqtt.client as mqtt
from microstacknode.hardware.accelerometer.mma8452q import MMA8452Q

# accelerometer configuration and sample rate
G_RANGE = 2
GRAVITY = 9.80665
#INTERVAL = 0.5  # seconds (2 Hz)
INTERVAL = 0.2  # seconds (5 Hz)
#INTERVAL = 0.02  # seconds (50 Hz)
#INTERVAL = 0.002  # seconds (500 Hz)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

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
        time.sleep(INTERVAL)  # settle

        # initialize velocity variables
        ti = time.time()
        Aix = 0
        Aiy = 0
        Aiz = 0
        Vix = 0
        Viy = 0
        Viz = 0
        Dix = 0
        Diy = 0
        Diz = 0

        # print data
        while True:
            new_time = time.time()

            raw = accelerometer.get_xyz(raw=True)
            g = accelerometer.get_xyz()
            ms = accelerometer.get_xyz_ms2()
           
            # position and velocity inference
            Ax = ms['x'] * 1000                                              # mm/s^2
            Vx = Vix + ((Ax - Aix) * INTERVAL)
            Dx = Dix + Vx * INTERVAL
            #Dx = Dix + Vix * INTERVAL + 0.5 * Ax * INTERVAL * INTERVAL      # mm
            #Vx = Dx / new_time                                              # mm/s
            Aix = Ax
            Vix = Vx
            Dix = Dx

            Ay = ms['y'] * 1000                                              # mm/s^2
            Vy = Viy + ((Ay - Aiy) * INTERVAL)
            Dy = Diy + Vy * INTERVAL                                        
            #Dy = Diy + Viy * INTERVAL + 0.5 * Ay * INTERVAL * INTERVAL      # mm
            #Vy = Dy / new_time                                              # mm/s
            Aiy = Ay
            Viy = Vy
            Diy = Dy

            Az = (ms['z'] - 9.8) * 1000                                      # mm/s^2
            Vz = Viz + ((Az - Aiz) * INTERVAL)
            Dz = Diz + Vz * INTERVAL
            #Dz = Diz + Viz * INTERVAL + 0.5 * Az * INTERVAL * INTERVAL      # mm
            #Vz = Dz / new_time                                              # mm/s
            Aiz = Az                                 
            Viz = Vz
            Diz = Dz

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

            print("----")
            print(datetime.datetime.now())
            print('  raw | x: {}, y: {}, z: {}'.format(raw['x'], raw['y'], raw['z']))
            print('    G | x: {:.2f}, y: {:.2f}, z: {:.2f}'.format(g['x'], g['y'], g['z']))
            print('mm/s^2 | x: {:.2f}, y: {:.2f}, z: {:.2f}'.format(Ax, Ay, Az))
            print('mm/s | x: {:.2f}, y: {:.2f}, z: {:.2f}'.format(Vx, Vy, Vz))

            mqttc.publish("sensor/accelerometer", json.dumps(data))

            time.sleep(INTERVAL)
