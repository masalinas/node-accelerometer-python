# node-accelerometer

A proof of concept to demostrate any measure captured from a accelerometer attached to a raspberry pi 3 and transport this information throw mqtt protocol to a central server thats centralize this information using a message broker like mosca and node-red to parse and visualize it .

![glukose_gateway_app](https://cloud.githubusercontent.com/assets/1216181/14147087/6862711e-f69a-11e5-9e9f-05efadedca9e.png)

The Node-RED flow Designer

![glukose-gateway-nodered](https://cloud.githubusercontent.com/assets/1216181/14145560/9d61d428-f694-11e5-8bb4-f975103a27ba.png)

# Infraestructure Techonologies:

- [NodeJS](https://nodejs.org/): Event-driven I/O server-side JavaScript environment based on V8. Includes API documentation, change-log, examples and announcements.
- [mosca](https://github.com/mcollina/mosca): MQTT broker as a module http://mosca.io.
- [Node-Red](http://nodered.org/): A visual tool for wiring the Internet of Things.

# Frontend Techonologies:

- [node-red-contrib-graphs](https://www.npmjs.com/package/node-red-contrib-graphs): A Node-RED graphing package.
- [node-red-contrib-ui](https://www.npmjs.com/package/node-red-contrib-ui): UI nodes for node-red.

# Installation:

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
[{"id":"2a3e1609.eb51fa","type":"ui_tab","z":"66a7a68a.89d808","name":"Home","icon":"dashboard","order":"1"},{"id":"3111afea.fdc34","type":"mqtt-broker","z":"66a7a68a.89d808","broker":"127.0.0.1","port":"1883","clientid":"","usetls":false,"verifyservercert":true,"compatmode":true,"keepalive":"60","cleansession":true,"willTopic":"","willQos":"0","willRetain":null,"willPayload":"","birthTopic":"","birthQos":"0","birthRetain":null,"birthPayload":""},{"id":"9186d7c4.d09e18","type":"mqtt in","z":"66a7a68a.89d808","name":"Accelerometer Mqtt","topic":"sensor/accelerometer","broker":"3111afea.fdc34","x":128.5,"y":214,"wires":[["74e693c.b495e6c","6ffb6e8.392319","e99370e5.0b85f"]]},{"id":"bfe1206a.e51c8","type":"ui_chart","z":"66a7a68a.89d808","tab":"2a3e1609.eb51fa","name":"Accelerometer","group":"1","order":1,"interpolate":"linear","nodata":"No Data","removeOlder":"10","removeOlderUnit":"1","x":478.5,"y":272,"wires":[[],[]]},{"id":"74e693c.b495e6c","type":"function","z":"66a7a68a.89d808","name":"Z Axis","func":"var measure = JSON.parse(msg.payload);\n\nmsg.payload = measure.data.z;\n\nreturn msg;","outputs":1,"noerr":0,"x":316.5,"y":297,"wires":[["bfe1206a.e51c8","b5f5e26e.76afc"]]},{"id":"b5f5e26e.76afc","type":"debug","z":"66a7a68a.89d808","name":"","active":true,"console":"false","complete":"false","x":473.5,"y":325,"wires":[]},{"id":"e99370e5.0b85f","type":"function","z":"66a7a68a.89d808","name":"X Axis","func":"var measure = JSON.parse(msg.payload);\n\nmsg.topic = measure.data.x;\n\nreturn msg;","outputs":1,"noerr":0,"x":323,"y":135,"wires":[[]]},{"id":"6ffb6e8.392319","type":"function","z":"66a7a68a.89d808","name":"Y Axis","func":"var measure = JSON.parse(msg.payload);\n\nmsg.topic = measure.data.y;\n\nreturn msg;","outputs":"1","noerr":0,"x":317,"y":214,"wires":[[]]}]
```

Access Node-Red UI Web
```
  http://localhost:1880/ui
```

# Licenses
The source code is released under Apache 2.0.

