# node-accelerometer

A proof of concept to demostrate any measure captured from a accelerometer attached to a raspberry pi 3 and transport this information throw mqtt protocol to a central server thats centralize this information using a message broker like mosca and node-red to parse and visualize it .

The Node-RED flow Designer

![picapp - apple imac](https://cloud.githubusercontent.com/assets/1216181/16017496/80f963a4-31a0-11e6-8f53-ec98471e6322.png)

The Node-RED UI with node-red-contrib-graph node-red module

![screen_accele](https://cloud.githubusercontent.com/assets/1216181/16090034/194ef248-332e-11e6-9454-d22389459136.png)

The Raspberry pi 3 and accelerometer connected

![accelerometer_raspberrypi](https://cloud.githubusercontent.com/assets/1216181/16017883/41bb0646-31a2-11e6-907b-8fb9019c17c8.jpeg)

Architecture

![accelerometer_arch](https://cloud.githubusercontent.com/assets/1216181/16018154/7defe644-31a3-11e6-93c2-b8d0c215537d.jpg)


# Hardware:

- [Raspberry pi 3](https://www.raspberrypi.org/): The Raspberry Pi is a series of credit card-sized single-board computers developed in the United Kingdom by the Raspberry Pi Foundation.
- [Microstack™ Baseboard For Raspberry Pi®](http://www.microstack.org.uk/assets/pibaseboard/FormattedPiBaseboardgettingstarted.pdf): Microstack™ Baseboard brings the exciting range of Microstack™ modules to Raspberry Pi®.
- [Microstack™ Accelerometer](http://www.generationrobots.com/media/Microstack/Microstack-accelerometer-for-raspberry-pi-getting-started.pdf): Find out which way is up! Detect taps, flicks, swishes and shakes, make a 3D motion controller or discover how much force has been
applied. 

# Infraestructure Techonologies:

- [Raspbian](https://www.raspberrypi.org/downloads/raspbian/): Last raspbian for raspberry pi. Raspbian is the Foundation’s official supported operating system.
- [NodeJS](https://nodejs.org/): Event-driven I/O server-side JavaScript environment based on V8. Includes API documentation, change-log, examples and announcements.
- [mosca](https://github.com/mcollina/mosca): MQTT broker as a module http://mosca.io.
- [Node-Red](http://nodered.org/): A visual tool for wiring the Internet of Things.

# Frontend Techonologies:

- [node-red-contrib-graphs](https://www.npmjs.com/package/node-red-contrib-graphs): A Node-RED graphing package.
- [node-red-contrib-ui](https://www.npmjs.com/package/node-red-contrib-ui): UI nodes for node-red.

# Installation:

Install python 3 mqtt modeule and microstack shield modules on raspberry-pi 3:
```
  sudo apt-get install python3-microstacknode
  sudo apt-get install python3-pip
  sudo pip3 install paho-mqtt
```

Install mosca mqtt message broker:
```
  npm install mosca bunyan -g
  mosca -v | bunyan
```

Execute npm to install node-red and node-red npm modules:
```
  npm install
```

Start node-red
```
  node node_modules/node-red/red.js
```

Access Node-Red Web designer
```
  http://localhost:1880
```

Copy and import this flow from node-red import clipboard
```
[{"id":"3111afea.fdc34","type":"mqtt-broker","z":"66a7a68a.89d808","broker":"127.0.0.1","port":"1883","clientid":"","usetls":false,"verifyservercert":true,"compatmode":true,"keepalive":"60","cleansession":true,"willTopic":"","willQos":"0","willRetain":null,"willPayload":"","birthTopic":"","birthQos":"0","birthRetain":null,"birthPayload":""},{"id":"9186d7c4.d09e18","type":"mqtt in","z":"66a7a68a.89d808","name":"Accelerometer Mqtt","topic":"sensor/accelerometer","broker":"3111afea.fdc34","x":128.5,"y":214,"wires":[["ff33dc25.99f42","45db47ad.89b3f8","d6479b56.8174a8","b5f5e26e.76afc"]]},{"id":"b5f5e26e.76afc","type":"debug","z":"66a7a68a.89d808","name":"","active":true,"console":"false","complete":"payload","x":384.5,"y":73,"wires":[]},{"id":"ff33dc25.99f42","type":"function","z":"66a7a68a.89d808","name":"Acceleration","func":"var measure = JSON.parse(msg.payload);\n\nmsg.payload = {'A': measure.A,\n               'tstamp': measure.tstamp};\n\nreturn msg;","outputs":1,"noerr":0,"x":377,"y":171,"wires":[["a05b625c.5decb"]]},{"id":"a05b625c.5decb","type":"iot-datasource","z":"66a7a68a.89d808","name":"Acceleration","tstampField":"tstamp","dataField":"A","disableDiscover":false,"x":573,"y":171,"wires":[[]]},{"id":"45db47ad.89b3f8","type":"function","z":"66a7a68a.89d808","name":"Velocity","func":"var measure = JSON.parse(msg.payload);\n\nmsg.payload = {'V': measure.V,\n               'tstamp': measure.tstamp};\n\nreturn msg;","outputs":1,"noerr":0,"x":369,"y":253,"wires":[["e0a9f0d5.f4a37"]]},{"id":"d6479b56.8174a8","type":"function","z":"66a7a68a.89d808","name":"Position","func":"var measure = JSON.parse(msg.payload);\n\nmsg.payload = {'D': measure.D,\n               'tstamp': measure.tstamp};\n\nreturn msg;","outputs":1,"noerr":0,"x":369,"y":337,"wires":[["81319b06.9cc8e8"]]},{"id":"e0a9f0d5.f4a37","type":"iot-datasource","z":"66a7a68a.89d808","name":"Velocity","tstampField":"tstamp","dataField":"V","disableDiscover":false,"x":562,"y":253,"wires":[[]]},{"id":"81319b06.9cc8e8","type":"iot-datasource","z":"66a7a68a.89d808","name":"Position","tstampField":"tstamp","dataField":"D","disableDiscover":false,"x":563,"y":337,"wires":[[]]}]
```

Access Node-Red UI Web
```
  http://localhost:1880/ui
```

# Licenses
The source code is released under Apache 2.0.

