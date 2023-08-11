from paho.mqtt import client as mqtt
import mqtt_secrets
import time
import json
import random

# verify = 1

'''mqtt_init() initializes the parameters needed to make a connection with and publish data to the MQTT broker. These values are read from
    the mqtt_secrets file, so any changes have to go there. This is especially true for client ID, unless you are able to read the MAC address
    for your device once during the initialization phase, so you don't have to enter it for every unique device'''
def mqtt_init():
	global MQTT_TOPIC_NAME, MQTT_BROKER, MQTT_PORT, username, password, client_id
	MQTT_TOPIC_NAME = mqtt_secrets.MQTT_TOPIC_NAME
	MQTT_BROKER = mqtt_secrets.MQTT_BROKER
	MQTT_PORT = mqtt_secrets.MQTT_PORT
	username = mqtt_secrets.MQTT_USER
	password = mqtt_secrets.MQTT_PASSWORD
	client_id = mqtt_secrets.client_id
	
'''This dict contains the fields to be sent to the influx db. An important point to note is that once a packet is sent for the first time, 
	each value becomes associated with whatever datatype was first sent. For example, if the first packet to be sent had a field called Current, 
	and the datatype of that measurement was float, all subsequent Current values should be float, or the DB will crash (unless that has been fixed). '''
def dict_init(id):
	global data_dict
	data_dict = {
				"value1": 0.0,
				"value2": 0.0,
				"value3": "somerandomvalue" ,                      # you should replace value with whatever you are measuring (voltage, current, power, etc.)         
				"_meta": {"device_id" : id, 
							"app_id" : "app_ID"}
	} 
	
'''on_connect() is a built in paho-mqtt function that returns the status of the connection when a connect request is made'''
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print('Connected to MQTT broker\n')
        pass
    else:
        print('Failed to connect to MQTT broker, reason is {}\n'.format(rc))
        pass

'''mqtt_connect() connects to the mqtt broker and returns the client object'''
def mqtt_connect():
	global username, password, MQTT_BROKER, MQTT_PORT, client_id
	client = mqtt.Client(client_id)
	client.username_pw_set(username, password)
	client.tls_set()
	client.on_connect = on_connect
	client.connect(MQTT_BROKER, MQTT_PORT, 60)
	return client
	
if __name__ == '__main__':		# start the program

	mqtt_init()                         # initializing the mqtt instance
	dict_init(client_id)     # initializing the dictionary for our mqtt publish
	mqtt_client = mqtt_connect()        # this creates the connection and we will refer to the returned client object as mqtt_client and perform operations 
	                                    # like looping, disconnecting, reconnecting, etc. on this
	mqtt_client.loop_start()            # all mqtt connections should be looped everytime you want to publish. 
	while True:
		try:
			value = random.uniform(0, 2.5)          # generate a random float number between 0 and 2.5
			data_dict.update({"value1": value})      # update our dictionary's values with the new values
			status = mqtt_client.publish(MQTT_TOPIC_NAME, json.dumps(data_dict))    # publish the data (we use json.dumps(dict) because published messages have to be strings)
            # This commented block below is used to check if the message was sent successfully. It is a one time operation, but you need to 
            # uncomment the verify variable at the top of the code. It is not mandatory. 
		
			# print("{}, {}". format(value, json.dumps(data_dict)))
			# verify = 0
			# if status[0] == 0:
			# 	print("Sent")
			# else:
			# 	print("failed")
			time.sleep(1)		# sleep for 1 second
		except KeyboardInterrupt:
				print('User interrupted, exiting the loop now')
				break

	mqtt_client.loop_stop()
	mqtt_client.disconnect()
	print('Client disconnected from the broker. No longer sending any data.')