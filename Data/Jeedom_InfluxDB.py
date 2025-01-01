#!/usr/bin/python3

""" mainHTTPGetListener.py: Retrieve GET request from Jeedom and forward them to InfluxDB """

from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib
import sys
import shlex, subprocess
import json

__author__ = "Hervé Froment"
__copyright__ = "Copyright 2019"
__license__ = "MIT License"
__version__ = "1.0.0"
__status__ = "Betat"

###########################
#    SCRIPT SETTINGS
###########################
# Set the port where you want the bridge service to run
PORT_NUMBER = 12345
# InfluxDB Server parameters
INLUXDB_SERVER_IP = '192.168.1.52'
INLUXDB_SERVER_IP2 = '192.168.1.166'
INLUXDB_SERVER_PORT = '8086'
#INFLUXDB_USERNAME = 'domotique'
#INFLUXDB_PASSWORD = 'domotique'
INFLUXDB_DB_NAME = 'domoticz'
###########################


# This class will handles any incoming request from jeedom
# Request expected (Jeedom Push URL)
# > http://IP_FROM_SERVER:PORT_NUMBER/updateData?name=#cmd_name#&cmd_id=#cmd_id#&val=#value#&location=salon

class JeedomHandler(BaseHTTPRequestHandler):
    """ Handle Jeedom > InfluxDB Requests """

    # Disable Log messages
    @staticmethod
    def log_message(format, *args):
        return

    # Handler for the GET requests
    def do_GET(self):
        # Part 1: Get the correct GET request from jeedom
        try:
            parsed_url = urllib.parse.urlparse(self.path)
            print(parsed_url)
            query = urllib.parse.parse_qs(parsed_url.query)
            # Extract the value, the name and the location + add current time
            try:
                val=query["val"][0]
                cmd_id = query["cmd_id"][0]
            except:
                print('no value in url')
                val = ''
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
        except:
            print("URL Parsing error : ", sys.exc_info()[0])
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()


        # Part 2: Write Data to InfluxDB
            
        if val !='':
            try:
                conversion = devices_dict[str(cmd_id)]
                # print(conversion)
                dataType = conversion['DataType']
                idx = conversion['Idx']
                if idx != '':
                    # requeteInfluxdb = 'curl -i -XPOST \'http://' + INLUXDB_SERVER_IP + ':' + INLUXDB_SERVER_PORT + '/write?db=' + INFLUXDB_DB_NAME + '\' --data-binary "' + dataType + ',idx=' + idx + ' value=' + val + '"'
                    # print(requeteInfluxdb)
                    # args = shlex.split(requeteInfluxdb)
                    # process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    # stdout, stderr = process.communicate()
                    requeteInfluxdb = 'curl -i -XPOST \'http://' + INLUXDB_SERVER_IP2 + ':' + INLUXDB_SERVER_PORT + '/write?db=' + INFLUXDB_DB_NAME + '\' --data-binary "' + dataType + ',idx=' + idx + ' value=' + val + '"'
                    print(requeteInfluxdb)
                    args = shlex.split(requeteInfluxdb)
                    process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, stderr = process.communicate()
            except:
                print('L\'équipement ' + cmd_id + ' n\'est pas dans la liste')
        return


if __name__ == '__main__':
    """ Start Jeedom-InfluxDB bridge """
		
    with open('devices.json', 'r') as f:
        devices_dict = json.load(f)
    print(devices_dict)

    try:
        # Start the web server to handle the request
        server = HTTPServer(('', PORT_NUMBER), JeedomHandler)
        print('Started Jeedom-InfluxDB bridge on port ', PORT_NUMBER)

        # Wait forever for incoming http requests
        server.serve_forever()

    except KeyboardInterrupt:
        print('^C received, shutting down the Jeedom-InfluxDB bridge ')
        server.socket.close()







# with open('distros.json', 'r') as f:
    # distros_dict = json.load(f)

# for distro in distros_dict:
    # print(distro)

# #print(distros_dict[0])
# #print(distros_dict['0'])
# toto = distros_dict['55']
# print(toto['Owner'])
# try:
    # toto = distros_dict['0']
    # print(toto['Owner'])
# except Exception as e:
    # print('0' + ' n\'existe pas')


