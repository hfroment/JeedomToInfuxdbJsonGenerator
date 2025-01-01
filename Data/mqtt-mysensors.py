#!/usr/bin/python
#
# mqtt-mysensors by Theo Arends
#
# Provides MySensors MQTT service using a mysensors serial gateway version 1.4
#
# Execute: mqtt-mysensors &
#
# Needs paho.mqtt.client
#   - git clone http://git.eclipse.org/gitroot/paho/org.eclipse.paho.mqtt.python.git
#   - python setup.py install
# Needs pyserial 2.7
#   - apt-get install python-pip
#   - pip install pyserial
#
# Topic = <topic_prefix>/<node_id>/<child_id>/<variable_type> <value>
#   - mysensors/4/0/V_LIGHT ON
#
# **** Start of user configuration values

serial_portname = "/dev/ttyUSB_CH340"   # MySensors serial gateway port
serial_bps = 115200            # MySensors serial gateway baud rate

mqtt_hostname = "192.168.1.166"             # MQTT broker ip address or name
mqtt_portnum = 1883             # MQTT broker port

topic_prefix = "mysensors"     # MQTT mysensors topic prefix

M_INFO = 3                     # Print messages: 0 - none, 1 - Startup, 2 - Serial, 3 - All

# **** End of user configuration values

import paho.mqtt.client as mqtt
import serial
import time
import signal
import sys

# mysensor_command
C_PRESENTATION = '0'
C_SET = '1'
C_REQ = '2'
C_INTERNAL = '3'
C_STREAM = '4'

# mysensor_data
V_codes = ['TEMP',
'HUM',
'STATUS',
'PERCENTAGE',
'PRESSURE',
'FORECAST',
'RAIN',
'RAINRATE',
'WIND',
'GUST',
'DIRECTION',
'UV',
'WEIGHT',
'DISTANCE',
'IMPEDANCE',
'ARMED',
'TRIPPED',
'WATT',
'KWH',
'SCENE_ON',
'SCENE_OFF',
'HVAC_FLOW_STATE',
'HVAC_SPEED',
'LIGHT_LEVEL',
'VAR1',
'VAR2',
'VAR3',
'VAR4',
'VAR5',
'UP',
'DOWN',
'STOP',
'IR_SEND',
'IR_RECEIVE',
'FLOW',
'VOLUME',
'LOCK_STATUS',
'LEVEL',
'VOLTAGE',
'CURRENT',
'RGB',
'RGBW',
'ID',
'UNIT_PREFIX',
'HVAC_SETPOINT_COOL',
'HVAC_SETPOINT_HEAT',
'HVAC_FLOW_MODE',
'TEXT',
'CUSTOM',
'POSITION',
'IR_RECORD',
'PH',
'ORP',
'EC',
'VAR',
'VA',
'POWER_FACTOR']

# mysensor_internal
I_codes = ['BATTERY_LEVEL',
'TIME',
'VERSION',
'ID_REQUEST',
'ID_RESPONSE',
'INCLUSION_MODE',
'CONFIG',
'FIND_PARENT',
'FIND_PARENT_RESPONSE',
'LOG_MESSAGE',
'CHILDREN',
'SKETCH_NAME',
'SKETCH_VERSION',
'REBOOT',
'GATEWAY_READY',
'SIGNING_PRESENTATION',
'NONCE_REQUEST',
'NONCE_RESPONSE',
'HEARTBEAT_REQUEST',
'PRESENTATION',
'DISCOVER_REQUEST',
'DISCOVER_RESPONSE',
'HEARTBEAT_RESPONSE',
'LOCKED',
'PING',
'PONG',
'REGISTRATION_REQUEST',
'REGISTRATION_RESPONSE',
'DEBUG',
'SIGNAL_REPORT_REQUEST',
'SIGNAL_REPORT_REVERSE',
'SIGNAL_REPORT_RESPONSE',
'PRE_SLEEP_NOTIFICATION',
'POST_SLEEP_NOTIFICATION']

# mysensor_sensor
S_codes = ['DOOR', 
'MOTION', 
'SMOKE', 
'BINARY', 
'DIMMER', 
'COVER', 
'TEMP', 
'HUM', 
'BARO', 
'WIND', 
'RAIN', 
'UV', 
'WEIGHT', 
'POWER', 
'HEATER', 
'DISTANCE', 
'LIGHT_LEVEL', 
'ARDUINO_NODE', 
'ARDUINO_REPEATER_NODE', 
'LOCK', 
'IR', 
'WATER', 
'AIR_QUALITY', 
'CUSTOM', 
'DUST', 
'SCENE_CONTROLLER', 
'RGB_LIGHT', 
'RGBW_LIGHT', 
'COLOR_SENSOR', 
'HVAC', 
'MULTIMETER', 
'SPRINKLER', 
'WATER_LEAK', 
'SOUND', 
'VIBRATION', 
'MOISTURE', 
'INFO', 
'GAS', 
'GPS', 
'WATER_QUALITY']

M_NACK = '0'
M_ACK = '1'

B_codes = ['OFF', 'ON']

mypublish = ""

serial_port = None
client = None
 
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
  if M_INFO > 0:
    print("\nMQTT-MySensors service connected with result code "+str(rc))

# Subscribing in on_connect() means that if we lose the connection and
# reconnect then subscriptions will be renewed.
  client.subscribe(topic_prefix+"/#")

# The callback for when a PUBLISH message is received from the server.
def on_message1(client, userdata, msg):

  print(f"message received: topic: {msg.topic} payload: {msg.payload}")
  if M_INFO > 2:
    print(" Last published |"+mypublish+"|")
    #print("MQTT subscribed |"+msg.topic+"|"+msg.payload+"|")
    print("MQTT subscribed |"+msg.topic+"|"+str(msg.payload)+"|")
    print((msg.payload.decode()))

def on_message(client, userdata, msg):

  if M_INFO > 2:
    print(" Last published |"+mypublish+"|")
    print("MQTT subscribed |"+msg.topic+"|"+msg.payload.decode()+"|")

  mysubscribe = msg.topic+"/"+msg.payload.decode()
  if mypublish != mysubscribe:
    parts = msg.topic.split("/")  # mysensors/4/0/V_LIGHT/ON

    try:
      if (len(parts) > 3) and (int(parts[1]) < 256) and (int(parts[2]) < 256):
        command = C_PRESENTATION
        idx = "0"
        mysensor_data = parts[3].upper()
        msg_payload = msg.payload.decode().rstrip()
        payload = ""
        if mysensor_data[0] == 'I':
          command = C_INTERNAL
          if len(msg_payload) != 0:
            payload = ";" + msg_payload
          if mysensor_data[2:22] in I_codes:
            idx = str(I_codes.index(mysensor_data[2:22]))
        else:
          if len(msg_payload) == 0:
            command = C_REQ
          else:
            command = C_SET
            payload = ";" + msg_payload
            #if mysensor_data == 'V_LIGHT':
              #if msg_payload.upper() in B_codes:
                #payload = ";"+str(B_codes.index(msg_payload.upper()))
          if mysensor_data[2:22] in V_codes:
            idx = str(V_codes.index(mysensor_data[2:22]))
        myserial = parts[1]+";"+parts[2]+";"+command+";0;"+idx+payload + "\n"
        serial_port.write(myserial.encode())
        if M_INFO > 1:
          print("     Serial out |"+myserial+"|")

    except:
      print("exception");
      pass

if M_INFO > 0:
  print("MQTT mysensors serial gateway service.")

################################################################
# Attach a handler to the keyboard interrupt (control-C).
def _sigint_handler(signal, frame):
    print("Keyboard interrupt caught, closing down...")
    if serial_port is not None:
        serial_port.close()

    if client is not None:
        client.loop_stop()
        
    sys.exit(0)

signal.signal(signal.SIGINT, _sigint_handler)        
################################################################

client = mqtt.Client()
client.enable_logger()
client.on_connect = on_connect
client.on_message = on_message

# Start a background thread to connect to the MQTT network.
print(mqtt_hostname, mqtt_portnum)
client.connect_async(mqtt_hostname, mqtt_portnum)
client.loop_start()

################################################################
# Connect to the serial device.
serial_port = serial.Serial(serial_portname, baudrate=115200, timeout=100000)

# wait briefly for the Arduino to complete waking up
time.sleep(0.2)

print(f"Entering Arduino event loop for {serial_portname}.  Enter Control-C to quit.")

while(True):
    input = serial_port.readline().decode(encoding='ascii',errors='ignore').rstrip()
    if len(input) == 0:
        print("Serial device timed out, no data received.")
    else:
      print(f"Received from serial device: {input}")
      rv = input.rstrip()

      if M_INFO > 1:
        print("      Serial in |"+rv+"|")

      parts = rv.split(";")  # 2;0;1;0;0;25.0
      if len(parts) > 4:
        mysensor_data = ''
        payload = parts[5]
        if parts[2] == C_PRESENTATION:
          if int(parts[4]) < len(S_codes):
            mysensor_data = "S_"+S_codes[int(parts[4])]
          else:
            mysensor_data = "S_UNKNOWN"
        elif parts[2] == C_INTERNAL:
          if int(parts[4]) < len(I_codes):
            mysensor_data = "I_"+I_codes[int(parts[4])]
          else:
            mysensor_data = "I_UNKNOWN"
        else:
          if int(parts[4]) < len(V_codes):
            mysensor_data = "V_"+V_codes[int(parts[4])]
          else:  
            mysensor_data = "V_UNKNOWN"
#             if mysensor_data == "V_LIGHT":
#               if int(parts[5]) < len(B_codes):
#                 payload = B_codes[int(parts[5])] # ON / OFF
        mytopic = topic_prefix+"/"+parts[0]+"/"+parts[1]+"/"+mysensor_data
        mypublish = mytopic+"/"+payload

        if M_INFO > 2:
          print("  New published |"+mypublish+"|")
          print(" MQTT published |"+mytopic+"|"+payload+"|")

        client.publish(mytopic, payload)
      rv = ''

