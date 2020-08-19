#!/usr/bin/python
import os
import pymysql
import sys
import json
from datetime import date, datetime, timedelta
import cgitb
import time
import requests
import numpy as np

print("Content-Type: text/html")
print("")

DEBUG_MODE = False

if DEBUG_MODE:
	print("DSC190 API - Connected to API")
	cgitb.enable(format='text')

#-----------------------------------------------
# GET Request
#form = cgi.FieldStorage()


#if DEBUG_MODE:
#	print("making a GET request")
#	print("form")
#	print(form)

#params = {}
#for key in form.keys():
#	params[key] = form[key].value
#-----------------------------------------------

#-----------------------------------------------
# POST Request
params = json.load(sys.stdin)

if DEBUG_MODE:
	print("making a POST request")
	print("Using sys.stdin:", params)
	print("cmd = {}".format(params["cmd"]))
#-----------------------------------------------

if DEBUG_MODE:
	print("params")
	print(params)

num_params = len(params)

if DEBUG_MODE:
	print("num_params")
	print(num_params)

SERVERNAME = 'localhost'
USERNAME = 'iotdev'
PASSWORD = 'iotdb190'
DBNAME = 'iotdb'

connection = pymysql.connect(host=SERVERNAME,
							 user=USERNAME,
							 password=PASSWORD,
							 db=DBNAME,
							 cursorclass=pymysql.cursors.DictCursor,
							 autocommit=True)

cursor = connection.cursor()

def get_current_time():
	return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def get_current_day():
	return datetime.now().date().strftime('%Y-%m-%d')

def get_previous_day():
    days_to_subtract = 1
    return (datetime.today() - timedelta(days=days_to_subtract)).date().strftime('%Y-%m-%d')

def calculate_RMSE(group_temps, meteostat_temps):
	if DEBUG_MODE:
		print('in calculate_RMSE')
	errors = [((group_temp - meteostat_temp)**2) for group_temp, meteostat_temp in zip(group_temps, meteostat_temps)]
	if DEBUG_MODE:
		print('errors:')
		print(errors[:2])
	rmse = np.sqrt(np.mean((errors)))
	if DEBUG_MODE:
		print('rmse:')
		print(rmse)
		print('returning rmse')
	return rmse

def calculate_MAE(group_temps, meteostat_temps):
	errors = [(group_temp - meteostat_temp) for group_temp, meteostat_temp in zip(group_temps, meteostat_temps)]
	mae = np.mean(np.absolute((errors)))
	return mae

def calculate_MAPE(group_temps, meteostat_temps):
	errors = [((group_temp - meteostat_temp) / group_temp) for group_temp, meteostat_temp in zip(group_temps, meteostat_temps)]
	mape = round(np.mean(np.abs(errors)) * 100, 1)
	return mape

def calculate_offsets(group_temps, meteostat_temps):
	offsets = [(group_temp - meteostat_temp) for group_temp, meteostat_temp in zip(group_temps, meteostat_temps)]
	return offsets

def convert_query_to_json(data):
    # convert query result to json format
    json_data = []
    cols = [column[0] for column in cursor.description]
    for row in data:
        _temp_dict = {}
        for col in cols:
            _temp_dict[col] = row[col]
        json_data.append(_temp_dict)
    return json_data

# Dev MAC address to nearest station dictionary
mac_to_station = {
    "80:7D:3A:A2:9C:08": 72290,
    "3C:71:BF:6F:13:B8": "KRHV0",
    "CC:50:E3:AF:E1:B4": 72290,
    "3C:71:BF:64:36:C0": 72290,
    "3C:71:BF:6C:62:2C": "KRHV0",
    "3C:71:BF:63:81:BC": 72290,
    "80:7D:3A:BA:E2:14": 72290,
    "CC:50:E3:AF:E3:80": "KRHV0",
    "CC:50:E3:A8:EB:3C": 72290,
    "CC:50:E3:B0:21:8C": 72295,
    "3C:71:BF:6C:5D:B4": 72290,
    "A4:CF:12:43:71:4C": 72290,
    "A4:CF:12:43:7E:00": 72483,
    "3C:71:BF:63:DF:70": 72290, # Note: I didn't find this particular beacon manually in the map
    "CC:50:E3:B0:21:78": 72290,
    "3C:71:BF:6C:A9:7C": 72290,
    "CC:50:E3:AF:E3:80": 72290, # Note: I didn't find this particular beacon manually in the map
    "3C:71:BF:62:E7:FC": 72290, # Note: I didn't find this particular beacon manually in the map
    "80:7D:3A:E9:67:5C": 72290,
    "A4:CF:12:43:52:D0": 72494,
    "CC:50:E3:A9:79:3C": 72290,
    "CC:50:E3:AF:E4:E0": 72295,
    "3C:71:BF:63:E6:30": 72494,
    "CC:50:E3:B0:21:A4": 72295,
    "3C:71:BF:63:EE:0C": 72295,
    "A4:CF:12:43:71:60": "KRHV0",
    "CC:50:E3:AF:E4:68": 72494,
    "80:7D:3A:BC:7F:00": 72793,
    "CC:50:E3:A1:45:2C": 72290,
    "3C:71:BF:63:DF:98": 72509,
    "3C:71:BF:63:DC:D0": 72290,
    "CC:50:E3:B0:92:B4": 72290,
    "3C:71:BF:62:E4:30": 72295,
    "3C:71:BF:64:21:DC": 72295
}

if params['cmd'] == "LIST":
	if DEBUG_MODE:
		print('cmd is LIST')
	sql = "SELECT * FROM devices"
	
	if num_params == 2:
		sql += " WHERE groupID = " + params['gid']

	cursor.execute(sql)
	data = cursor.fetchall()

	if not data:
		print("You have an empty query output. Please check your parameters.")
	else:
		for item in data:
            		item['lastseen'] = str(item['lastseen'])
        	json_data = convert_query_to_json(data)

		if DEBUG_MODE:
			print('printing JSON')
        	print(json.dumps({'devices': json_data}, indent=2))

if params['cmd'] == "GROUPS":
	if DEBUG_MODE:
		print('cmd is GROUPS')
	sql = "SELECT * FROM groups"

	if num_params == 2:
		sql += " WHERE groupID = " + params['gid']

	cursor.execute(sql)
	data = cursor.fetchall()

	if not data:
		print("You have an empty query output. Please check your parameters.")
	else:
		data = str(data)
		data = data.replace("u\'", "\'").replace("\'", "\"")
		print('{"groups" : ')
		print(data)
		print('}')

if params['cmd'] == "REG":
	if DEBUG_MODE:
		print('cmd is REG')
	mac = params['mac']
	gid = params['gid']
	#ip = ''

	#if params['ip'] != '':
	#	ip = params['ip']

	if DEBUG_MODE:
		print('params:')
		print(mac, gid)

	current_time = get_current_time()

	if DEBUG_MODE:
		print('current_time:', current_time)
		print('type(current_time):')
		print(type(current_time))
		print('mac:')
		print(mac)
		print('making SQL command')

	# make and execute SQL command
	sql = "SELECT * FROM devices"
	sql += " WHERE mac = " + '\"' + mac + '\"'

	if DEBUG_MODE:
		print('executing SQL')
		print(sql)

	cursor.execute(sql)
	data = cursor.fetchall()

	if DEBUG_MODE:
		print('data:')
		print(data)

	# if device was never registered
	if not data:
		if DEBUG_MODE:
			print('inserting new data')
		sql_insert = 'INSERT INTO devices(groupID, mac, lastseen)' +\
			' VALUES ("{}", "{}", "{}")'.format(
				gid, mac, current_time)
		if DEBUG_MODE:
			print('made sql_insert command')
			print('sql_insert:')
			print(sql_insert)

		# execute the cursor
		try:
			if DEBUG_MODE:
				print('try to execute sql insert command')
			cursor.execute(sql_insert)
			res = {"Status": "200 OK", "Mac": mac,
				"Timestamp": current_time}
		except:
			if DEBUG_MODE:
				print('sql insert failed. setting res')
			res = {
				"Registration Failed": "Unable " +
				"to complete new device registration."}

	# else, device was already registered
	else:
		deviceID = data[0]["devID"]
		if DEBUG_MODE:
			print('updating existing data')
		sql_update = "UPDATE devices SET lastseen = {}" +\
			" WHERE mac = {} AND devID = {}"		
		sql_update = sql_update.format('\"' + current_time + '\"',
				'\"' + mac + '\"', deviceID)
		if DEBUG_MODE:
			print('made sql update command')
			print('sql_update:')
			print(sql_update)
		
		# execute the cursor
		try:
			if DEBUG_MODE:
				print('try to execute sql update command')
			cursor.execute(sql_update)
			if DEBUG_MODE:
				print('finished executing sql update command')
				print('setting res')
			res = {"Status": "200 OK", "Mac": mac,
				"Timestamp": current_time}
		except:
			if DEBUG_MODE:
				print('sql update failed. setting res')
			res = {
				"Registration Failed": "Unable to " +
				"update existing device's record. " + 
				"Please try different parameters."}

	print(json.dumps(res, indent=2))

if params['cmd'] == "LOG":
	if DEBUG_MODE:
		print('cmd is LOG')
	gid = params['gid']
	devmac = params['devmac']
	beacons = params['beacons'] if params['beacons'] else []
	if DEBUG_MODE:
		print('params:')
		print(gid, devmac, beacons)

	current_time = get_current_time()

	# process beacons
	if DEBUG_MODE:
		print('processing beacons')
	# check if the device found at least one beacon
	# if so, then add the beacon(s) to the database
	if beacons != []:
		for beacon in beacons:
			blemac = beacon['mac']
			blerssi = beacon['rssi']
			if DEBUG_MODE:
				print('adding new beacon')
				print('beacon:', beacon)
				print('blemac:', blemac)
				print('blerssi:', blerssi)

			if DEBUG_MODE:
				print('creating sql insert command')
			sql_insert = 'INSERT INTO blelogs(gid, devmac, blemac, blerssi, timestamp)' +\
				' VALUES ("{}", "{}", "{}", "{}", "{}")'.format(
					gid, devmac, blemac, blerssi, current_time)
			if DEBUG_MODE:
				print('made sql_insert command')
				print('sql_insert:')
				print(sql_insert)
	
			# execute the cursor
			try:
				cursor.execute(sql_insert)
				# res = {"Status": "200 OK", "Timestamp": current_time}
			except:
				print('sql_insert failed.')
				# res = {"Insertion Failed": "Unable to insert the device's log data. " +
				#	"Please try different parameters."}
		
		# Update lastseen timestamp in devices table
		# make and execute SQL command
		sql = "SELECT * FROM devices"
		sql += " WHERE mac = " + '\"' + devmac + '\"'

		if DEBUG_MODE:
			print('executing SQL')
			print(sql)

		cursor.execute(sql)
		data = cursor.fetchall()

		if DEBUG_MODE:
			print('data:')
			print(data)

		# if device was never registered
		if not data:
			if DEBUG_MODE:
				print('inserting new data')
			sql_insert = 'INSERT INTO devices(groupID, mac, lastseen)' +\
				' VALUES ("{}", "{}", "{}")'.format(
					gid, devmac, current_time)
			if DEBUG_MODE:
				print('made sql_insert command')
				print('sql_insert:')
				print(sql_insert)
			
			# execute the cursor
			try:
				if DEBUG_MODE:
					print('try to execute sql insert command')
				cursor.execute(sql_insert)
				res = {"Status": "200 OK", "Mac": devmac,
					"Timestamp": current_time}
			except:
				if DEBUG_MODE:
					print('sql insert failed. setting res')
				res = {
					"Registration Failed": "Unable " +
					"to complete new device registration."}

		# else, device was already registered
		else:
			for row in data:
				if DEBUG_MODE:
					print('updating existing data')
				sql_update = "UPDATE devices SET lastseen = {}" +\
					"WHERE mac = {} AND devID = {}"
				sql_update = sql_update.format('\"' + current_time + '\"',
					'\"' + devmac + '\"', row['devID'])
				if DEBUG_MODE:
					print('made sql update command')
					print('sql_update:')
					print(sql_update)

				# execute the cursor
				try:
					if DEBUG_MODE:
						print('try to execute sql update command')
					cursor.execute(sql_update)
					if DEBUG_MODE:
						print('finished executing sql update command')
						print('setting res')
					res = {"Status": "200 OK", "Mac": devmac,
						"Timestamp": current_time}
				except:
					if DEBUG_MODE:
						print('sql update failed. setting res')
					res = {
						"Registration Failed": "Unable to " +
						"update existing device's record. " +
						"Please try different parameters."}

		print(json.dumps(res, indent=2))
		print('\n')

if params['cmd'] == "LOGDEV":
	if DEBUG_MODE:
		print('cmd is LOGDEV')
	mac = params['mac']
	gid = params['gid']
	rssi = params['RSSI']
	if DEBUG_MODE:
		print('params:')
		print(mac, gid, rssi)

	current_time = get_current_time()

	if DEBUG_MODE:
		print('creating sql insert command')
	sql_insert = 'INSERT INTO devlogs(mac, groupID, RSSI, lastseen)' +\
		' VALUES ("{}", "{}", "{}", "{}")'.format(
			mac, gid, rssi, current_time)
	if DEBUG_MODE:
			print('made sql_insert command')
			print('sql_insert:')
			print(sql_insert)
	
	# execute the cursor
	try:
		cursor.execute(sql_insert)
		res = {"Status": "200 OK", "Timestamp": current_time}
	except:
		res = {"Insertion Failed": "Unable to insert the device's logdev data. " +
			"Please try different parameters."}

	print(json.dumps(res, indent=2))
	
# BLELOG command
if params['cmd'] == 'BLELOG':
	if DEBUG_MODE:
		print('cmd is BLELOG')
	sql = 'SELECT * FROM blelogs WHERE gid=7 ORDER BY timestamp DESC LIMIT 10'
	cursor.execute(sql)
	data = cursor.fetchall()
	if not data:
		print("Your query output is empty. Please check your selection")
	else:
		for item in data:
			item['timestamp'] = str(item['timestamp'])
		json_data = convert_query_to_json(data)

		if DEBUG_MODE:
			print('printing JSON')
		print(json.dumps({'blelogs': json_data}, indent=2))

# GETLOCATIONS command
if params['cmd'] == 'GETLOCATIONS':
	if DEBUG_MODE:
		print('cmd is GETLOCATIONS')
	gid = params['gid']
	sql = "SELECT DISTINCT mac, dev_lat, dev_long, groupID, lastseen FROM devices WHERE dev_lat IS NOT NULL AND dev_long IS NOT NULL"
	if gid == "07":
		sql += " AND groupID = '%s' " % gid
	cursor.execute(sql)
	data = cursor.fetchall()
	for row in data:
		row['dev_lat']  = str(row['dev_lat'])
		row['dev_long'] = str(row['dev_long'])
		row['lastseen'] = str(row['lastseen'])
	data = str(data).replace("u\'", '\'').replace("'", '"')
	print('{"devices" : %s}' % data)

# TOP5BLELOGS command
if params['cmd'] == 'TOP5BLELOGS':
	if DEBUG_MODE:
		print('cmd is TOP5BLELOGS')
	devmac = params['devmac']
	sql = "SELECT * FROM blelogs WHERE devmac = '%s' ORDER BY timestamp DESC LIMIT 5" % devmac
	cursor.execute(sql)
	data = cursor.fetchall()
	time = datetime.now()
	for row in data:
		lastseen = (time - row['timestamp']).total_seconds()
		if lastseen <= 10:
			row['status'] = 'Seen in the last 10 seconds'
			row['color']  = 'green'
		if lastseen > 10 and lastseen <= 600:
			row['status'] = 'Seen in the last 10 minutes'
			row['color']  = 'yellow'
		if lastseen > 600:
			row['status'] = 'Not seen in more than 10 minutes'
			row['color']  = 'red'
		row['timestamp'] = str(row['timestamp'])
	
	data = str(data).replace("u\'", "\'").replace("'",'"')
	
	print('{"blelogs" : %s}' % data)

# GET_NUM_DEVICES command
if params['cmd'] == 'GET_NUM_DEVICES':
	if DEBUG_MODE:
		print('cmd is GET_NUM_DEVICES')
	devmac = params['devmac']
	sql = "SELECT count(DISTINCT blemac) AS counts, left(timestamp, 10) AS date FROM blelogs WHERE devmac='%s' GROUP BY date" % devmac
	cursor.execute(sql)
	data = cursor.fetchall()
	updated_data = []
	for row in data:
		updated_data.append([row['date'], row['counts'], 'gold'])
	updated_data = str(updated_data).replace("u\'",'\'').replace("'",'"')
	print('{"visitors" : %s}' % updated_data)

# RSSI_PER_HOUR command
if params['cmd'] == 'RSSI_PER_HOUR':
	if DEBUG_MODE:
		print('cmd is RSSI_PER_HOUR')
	devmac = params['devmac']
	sql = "SELECT avg(blerssi) AS avg_rssi, substring(timestamp, 12, 2) AS hour FROM blelogs WHERE devmac='%s' GROUP BY hour" % devmac
	cursor.execute(sql)
	data = cursor.fetchall()
	updated_data = []
	for row in data:
		updated_data.append([int(row['hour']), row['avg_rssi']])
	updated_data = str(updated_data).replace("u\'",'\'').replace("'",'"')
	print('{"hourly" : %s}' % updated_data)

# WEATHER command
if params['cmd'] == "WEATHER":
	url = 'http://api.openweathermap.com.org/data/2.5/weather'
	params = {'zip': "95765,us", 'appid': "0354c29c5e773c46d37727c8a0455d58"}
	r = requests.get(url, params=params)
	data = r.json()
	
	gid = "07"
	timestamp = get_current_time()
	provider = 'Open Weather'
	hum = data['main']['humidity']
	temp = data['main']['temp']
	min_temp = data['main']['temp_min']
	max_temp = data['main']['temp_max']
	
	sql = "INSERT INTO forecast(gid, temp, min_temp, max_temp, hum, timestamp, provider) VALUES ('%s','%s','%s','%s','%s','%s','%s')" % (gid, temp, min_temp, max_temp, hum, timestamp, provider)
	cursor.execute(sql)

# POSTMC command
if params['cmd'] == "POSTMC":
	gid = "07"
	mac = params['devmac']
	temp = params['temp']
	hum = params['hum']
	time = get_current_time()
	sql = "INSERT INTO mcdata(gid, mac, temp, hum, timerstamp, status) VALUES ('%s','%s','%s','%s',NOW(),'ACTIVE')" % (gid, mac, temp, hum)
	try:
		cursor.execute(sql)
		status = 'OK'
	except:
		status = 'DB Error'
	print("{'timestamp': %s, 'status': %s}" % (time, status))

# GETMCDATA command
if params['cmd'] == "GETMCDATA":
	devmac = params['devmac']
	sql = "SELECT avg(temp) AS avg_temp, avg(hum) AS avg_hum, substring(timerstamp, 12, 2) AS hour FROM mcdata WHERE mac='%s' AND DATE_ADD(timerstamp, INTERVAL HOUR(now()) HOUR) >= now() GROUP BY hour" % devmac
	cursor.execute(sql)
	rows = cursor.fetchall()
	newrows = []
	for row in rows:
		newrows.append([int(row['hour']), int(row['avg_temp']), int(row['avg_hum'])])
	newrows = str(newrows).replace("u\'",'\'').replace("'",'"')
	print('{"mcdata" : %s}' % newrows)

# GETMETEOSTATDATA command
if params['cmd'] == "GETMETEOSTATDATA":
	devmac = params['devmac']
	url = 'https://api.meteostat.net/v1/history/hourly'
	params = {'station': str(mac_to_station[devmac]), 'start': get_current_day(), 'end': get_current_day(), 'time_zone': "America/Los_Angeles",
	          'time_format': "Y-m-d%20H:i", 'key': "UcOLB4Z5"}
	r = requests.get(url, params=params)
	data = r.json()
	rows = data['data']
	newrows = []
	for row in rows:
	    newrows.append([int(row['time_local'][-5:-3]), int(row['temperature']), int(row['humidity'])])
	newrows = str(newrows).replace("u\'",'\'').replace("'",'"')
	print('{"meteostatdata" : %s}' % newrows)

# GETTEMPERATURES command
if params['cmd'] == "GETTEMPERATURES":
	devmac = params['devmac']

	# Group device's data
	sql = "SELECT avg(temp) AS avg_temp, substring(timerstamp, 12, 2) AS hour FROM mcdata WHERE mac='%s' AND DATE_ADD(timerstamp, INTERVAL HOUR(now()) HOUR) >= now() GROUP BY hour" % devmac
	cursor.execute(sql)
	rows = cursor.fetchall()

	# Meteostat API data
	url = 'https://api.meteostat.net/v1/history/hourly'
	params = {'station': str(mac_to_station[devmac]), 'start': get_current_day(), 'end': get_current_day(), 'time_zone': "America/Los_Angeles",
	          'time_format': "Y-m-d%20H:i", 'key': "UcOLB4Z5"}
	r = requests.get(url, params=params)
	data = r.json()
	meteostat_data = data['data']

	newrows = []
	min_length = min(len(rows), len(meteostat_data))
	for i in range(min_length):
		group_row = rows[i]
		temp_list = [int(group_row['hour']), int(group_row['avg_temp'])]
		meteostat_row = meteostat_data[i]
		temp_list.append(int(meteostat_row['temperature']))
		newrows.append(temp_list)
	newrows = str(newrows).replace("u\'",'\'').replace("'",'"')
	print('{"temperatures" : %s}' % newrows)

# GETHUMIDITIES command
if params['cmd'] == "GETHUMIDITIES":
	devmac = params['devmac']

	# Group device's data
	sql = "SELECT avg(hum) AS avg_hum, substring(timerstamp, 12, 2) AS hour FROM mcdata WHERE mac='%s' AND DATE_ADD(timerstamp, INTERVAL HOUR(now()) HOUR) >= now() GROUP BY hour" % devmac
	cursor.execute(sql)
	rows = cursor.fetchall()

	# Meteostat API data
	url = 'https://api.meteostat.net/v1/history/hourly'
	params = {'station': str(mac_to_station[devmac]), 'start': get_current_day(), 'end': get_current_day(), 'time_zone': "America/Los_Angeles",
	          'time_format': "Y-m-d%20H:i", 'key': "UcOLB4Z5"}
	r = requests.get(url, params=params)
	data = r.json()
	meteostat_data = data['data']

	newrows = []
	min_length = min(len(rows), len(meteostat_data))
	for i in range(min_length):
		group_row = rows[i]
		temp_list = [int(group_row['hour']), int(group_row['avg_hum'])]
		meteostat_row = meteostat_data[i]
		temp_list.append(int(meteostat_row['humidity']))
		newrows.append(temp_list)
	newrows = str(newrows).replace("u\'",'\'').replace("'",'"')
	print('{"humidities" : %s}' % newrows)

# COMPARETEMPERATURES command
if params['cmd'] == "COMPARETEMPERATURES":
	if DEBUG_MODE:
		print('cmd is COMPARETEMPERATURES')
	devmac = params['devmac']

	# Group device's data
	if DEBUG_MODE:
		print('getting group device data')
	sql = "SELECT avg(temp) AS avg_temp, substring(timerstamp, 12, 2) AS hour FROM mcdata WHERE mac='%s' AND DATE_ADD(timerstamp, INTERVAL HOUR(now()) HOUR) >= now() GROUP BY hour" % devmac
	cursor.execute(sql)
	rows = cursor.fetchall()
	if DEBUG_MODE:
		print('group device data:')
		print(rows[:5])

	# Local Meteostat API data
	if DEBUG_MODE:
		print('getting local Meteostat API data')
	url = 'https://api.meteostat.net/v1/history/hourly'
	params = {'station': str(mac_to_station[devmac]), 'start': get_current_day(), 'end': get_current_day(), 'time_zone': "America/Los_Angeles",
	          'time_format': "Y-m-d%20H:i", 'key': "UcOLB4Z5"}
	r = requests.get(url, params=params)
	data = r.json()
	meteostat_data = data['data']
	if DEBUG_MODE:
		print('local Meteostat API data:')
		print(meteostat_data[:5])

	# add group's and local Meteostat API data to output
	if DEBUG_MODE:
		print('adding group and local Meteostat API data to output')
	newrows = []
	newrow  = ['Group']
	if DEBUG_MODE:
		print('getting group data')
	group_temps = [row.get('avg_temp', 0) for row in rows]
	if DEBUG_MODE:
		print('getting local Meteostat API data')
	meteostat_temps = [row.get('temperature', 0) for row in meteostat_data]
	if DEBUG_MODE:
		print('calculating RMSE')
		print('group_temps:')
		print(group_temps[:5], len(group_temps))
		print('meteostat_temps:')
		print(meteostat_temps[:5], len(meteostat_temps))
	cur_rmse = calculate_RMSE(group_temps, meteostat_temps)
	if DEBUG_MODE:
		print('cur_rmse:')
		print(cur_rmse)
	newrow.append(cur_rmse)
	if DEBUG_MODE:
		print('calculating MAE')
	cur_mae = calculate_MAE(group_temps, meteostat_temps)
	if DEBUG_MODE:
		print('cur_mae:')
		print(cur_mae)
	newrow.append(cur_mae)
	cur_mape = calculate_MAPE(group_temps, meteostat_temps)
	if DEBUG_MODE:
		print('cur_mape:')
		print(cur_mape)
	newrow.append(cur_mape)
	newrows.append(newrow)
	if DEBUG_MODE:
		print('current output:')
		print(newrows)

	# Class data
	if DEBUG_MODE:
		print('getting class data')
	sql = "SELECT avg(temp) AS avg_temp, substring(timerstamp, 12, 2) AS hour FROM mcdata WHERE DATE_ADD(timerstamp, INTERVAL HOUR(now()) HOUR) >= now() GROUP BY hour"
	cursor.execute(sql)
	rows = cursor.fetchall()
	if DEBUG_MODE:
		print('class data:')
		print(rows[:5])

	# Average Meteostat API data
	if DEBUG_MODE:
		print('getting average Meteostat API data')
	stations = ["72290", "KRHV0", "72295", "72483", "72494", "72793", "72509"]
	all_meteostat_temps = []
	for station in stations:
		params = {'station': station, 'start': get_current_day(), 'end': get_current_day(), 'time_zone': "America/Los_Angeles",
		          'time_format': "Y-m-d%20H:i", 'key': "UcOLB4Z5"}
		r = requests.get(url, params=params)
		data = r.json()
		meteostat_data = data['data']
		meteostat_temps = [row.get('temperature', 0) for row in meteostat_data]
		all_meteostat_temps.append(meteostat_temps)
	all_meteostat_temps = [item for sublist in all_meteostat_temps for item in sublist]
	if DEBUG_MODE:
		print('average Meteostat API data:')
		print(all_meteostat_temps)

	# add class and all Meteostat API data to output
	if DEBUG_MODE:
		print('adding class and all Meteostat API data to output')
	newrow2 = ["Class"]
	all_group_temps = [row.get('avg_temp', 0) for row in rows]
	cur_rmse = calculate_RMSE(all_group_temps, all_meteostat_temps)
	newrow2.append(cur_rmse)
	cur_mae = calculate_MAE(all_group_temps, all_meteostat_temps)
	newrow2.append(cur_mae)
	cur_mape = calculate_MAPE(all_group_temps, all_meteostat_temps)
	newrow2.append(cur_mape)
	newrows.append(newrow2)
	if DEBUG_MODE:
		print('current output:')
		print(newrows)

	newrows = str(newrows).replace("u\'",'\'').replace("'",'"')
	print('{"comparetemperatures" : %s}' % newrows)

# COMPAREHUMIDITIES command
if params['cmd'] == "COMPAREHUMIDITIES":
	if DEBUG_MODE:
		print('cmd is COMPAREHUMIDITIES')
	devmac = params['devmac']

	# Group device's data
	if DEBUG_MODE:
		print('getting group device data')
	sql = "SELECT avg(hum) AS avg_hum, substring(timerstamp, 12, 2) AS hour FROM mcdata WHERE mac='%s' AND DATE_ADD(timerstamp, INTERVAL HOUR(now()) HOUR) >= now() GROUP BY hour" % devmac
	cursor.execute(sql)
	rows = cursor.fetchall()
	if DEBUG_MODE:
		print('group device data:')
		print(rows[:5])

	# Local Meteostat API data
	if DEBUG_MODE:
		print('getting local Meteostat API data')
	url = 'https://api.meteostat.net/v1/history/hourly'
	params = {'station': str(mac_to_station[devmac]), 'start': get_current_day(), 'end': get_current_day(), 'time_zone': "America/Los_Angeles",
	          'time_format': "Y-m-d%20H:i", 'key': "UcOLB4Z5"}
	r = requests.get(url, params=params)
	data = r.json()
	meteostat_data = data['data']
	if DEBUG_MODE:
		print('local Meteostat API data:')
		print(meteostat_data[:5])

	# add group's and local Meteostat API data to output
	if DEBUG_MODE:
		print('adding group and local Meteostat API data to output')
	newrows = []
	newrow  = ['Group']
	if DEBUG_MODE:
		print('getting group data')
	group_hums = [row.get('avg_hum', 0) for row in rows]
	if DEBUG_MODE:
		print('getting local Meteostat API data')
	meteostat_hums = [row.get('humidity', 0) for row in meteostat_data]
	if DEBUG_MODE:
		print('calculating RMSE')
		print('group_hums:')
		print(group_hums[:5], len(group_hums))
		print('meteostat_hums:')
		print(meteostat_hums[:5], len(meteostat_hums))
	cur_rmse = calculate_RMSE(group_hums, meteostat_hums)
	if DEBUG_MODE:
		print('cur_rmse:')
		print(cur_rmse)
	newrow.append(cur_rmse)
	if DEBUG_MODE:
		print('calculating MAE')
	cur_mae = calculate_MAE(group_hums, meteostat_hums)
	if DEBUG_MODE:
		print('cur_mae:')
		print(cur_mae)
	newrow.append(cur_mae)
	cur_mape = calculate_MAPE(group_hums, meteostat_hums)
	if DEBUG_MODE:
		print('cur_mape:')
		print(cur_mape)
	newrow.append(cur_mape)
	newrows.append(newrow)
	if DEBUG_MODE:
		print('current output:')
		print(newrows)

	# Class data
	if DEBUG_MODE:
		print('getting class data')
	sql = "SELECT avg(hum) AS avg_hum, substring(timerstamp, 12, 2) AS hour FROM mcdata WHERE DATE_ADD(timerstamp, INTERVAL HOUR(now()) HOUR) >= now() GROUP BY hour"
	cursor.execute(sql)
	rows = cursor.fetchall()
	if DEBUG_MODE:
		print('class data:')
		print(rows[:5])

	# Average Meteostat API data
	if DEBUG_MODE:
		print('getting average Meteostat API data')
	stations = ["72290", "KRHV0", "72295", "72483", "72494", "72793", "72509"]
	all_meteostat_hums = []
	for station in stations:
		params = {'station': station, 'start': get_current_day(), 'end': get_current_day(), 'time_zone': "America/Los_Angeles",
		          'time_format': "Y-m-d%20H:i", 'key': "UcOLB4Z5"}
		r = requests.get(url, params=params)
		data = r.json()
		meteostat_data = data['data']
		meteostat_hums = [row.get('humidity', 0) for row in meteostat_data]
		all_meteostat_hums.append(meteostat_hums)
	all_meteostat_hums = [item for sublist in all_meteostat_hums for item in sublist]
	if DEBUG_MODE:
		print('average Meteostat API data:')
		print(all_meteostat_hums)

	# add class and all Meteostat API data to output
	if DEBUG_MODE:
		print('adding class and all Meteostat API data to output')
	newrow2 = ["Class"]
	all_group_hums = [row.get('avg_hum', 0) for row in rows]
	cur_rmse = calculate_RMSE(all_group_hums, all_meteostat_hums)
	newrow2.append(cur_rmse)
	cur_mae = calculate_MAE(all_group_hums, all_meteostat_hums)
	newrow2.append(cur_mae)
	cur_mape = calculate_MAPE(all_group_hums, all_meteostat_hums)
	newrow2.append(cur_mape)
	newrows.append(newrow2)
	if DEBUG_MODE:
		print('current output:')
		print(newrows)

	newrows = str(newrows).replace("u\'",'\'').replace("'",'"')
	print('{"comparehumidities" : %s}' % newrows)

# OFFSETTEMPERATURES command
if params['cmd'] == "OFFSETTEMPERATURES":
	if DEBUG_MODE:
		print('cmd is OFFSETTEMPERATURES')
	devmac = params['devmac']

	# Group device's data
	if DEBUG_MODE:
		print('getting group device data')
	sql = "SELECT avg(temp) AS avg_temp, substring(timerstamp, 12, 2) AS hour FROM mcdata WHERE mac='%s' AND DATE_ADD(timerstamp, INTERVAL HOUR(now()) HOUR) >= now() GROUP BY hour" % devmac
	cursor.execute(sql)
	rows = cursor.fetchall()
	if DEBUG_MODE:
		print('group device data:')
		print(rows[:5])

	# Local Meteostat API data
	if DEBUG_MODE:
		print('getting local Meteostat API data')
	url = 'https://api.meteostat.net/v1/history/hourly'
	params = {'station': str(mac_to_station[devmac]), 'start': get_current_day(), 'end': get_current_day(), 'time_zone': "America/Los_Angeles",
	          'time_format': "Y-m-d%20H:i", 'key': "UcOLB4Z5"}
	r = requests.get(url, params=params)
	data = r.json()
	meteostat_data = data['data']
	if DEBUG_MODE:
		print('local Meteostat API data:')
		print(meteostat_data[:5])

	# add group's and local Meteostat API data to output
	if DEBUG_MODE:
		print('adding group and local Meteostat API data to output')
	newrows = []
	if DEBUG_MODE:
		print('getting group data')
	group_temps = [row.get('avg_temp', 0) for row in rows]
	if DEBUG_MODE:
		print('getting local Meteostat API data')
	meteostat_temps = [row.get('temperature', 0) for row in meteostat_data]
	if DEBUG_MODE:
		print('calculating offsets')
		print('group_temps:')
		print(group_temps[:5], len(group_temps))
		print('meteostat_temps:')
		print(meteostat_temps[:5], len(meteostat_temps))
	cur_offsets = calculate_offsets(group_temps, meteostat_temps)
	if DEBUG_MODE:
		print('cur_offsets:')
		print(cur_offsets)

	# Class data
	if DEBUG_MODE:
		print('getting class data')
	sql = "SELECT avg(temp) AS avg_temp, substring(timerstamp, 12, 2) AS hour FROM mcdata WHERE DATE_ADD(timerstamp, INTERVAL HOUR(now()) HOUR) >= now() GROUP BY hour"
	cursor.execute(sql)
	rows = cursor.fetchall()
	if DEBUG_MODE:
		print('class data:')
		print(rows[:5])

	# Average Meteostat API data
	if DEBUG_MODE:
		print('getting average Meteostat API data')
	stations = ["72290", "KRHV0", "72295", "72483", "72494", "72793", "72509"]
	all_meteostat_temps = []
	for station in stations:
		params = {'station': station, 'start': get_current_day(), 'end': get_current_day(), 'time_zone': "America/Los_Angeles",
		          'time_format': "Y-m-d%20H:i", 'key': "UcOLB4Z5"}
		r = requests.get(url, params=params)
		data = r.json()
		meteostat_data = data['data']
		meteostat_temps = [row.get('temperature', 0) for row in meteostat_data]
		all_meteostat_temps.append(meteostat_temps)
	all_meteostat_temps = [item for sublist in all_meteostat_temps for item in sublist]
	if DEBUG_MODE:
		print('average Meteostat API data:')
		print(all_meteostat_temps)

	# add class and all Meteostat API data to output
	if DEBUG_MODE:
		print('adding class and all Meteostat API data to output')
	all_group_temps = [row.get('avg_temp', 0) for row in rows]
	all_cur_offsets = calculate_offsets(all_group_temps, all_meteostat_temps)
	min_length = min(len(cur_offsets), len(all_cur_offsets))
	for i in range(min_length):
		row = rows[i]
		group_offset = cur_offsets[i]
		class_offset = all_cur_offsets[i]
		newrows.append([int(row['hour']), int(group_offset), int(class_offset)])
	if DEBUG_MODE:
		print('current output:')
		print(newrows)

	newrows = str(newrows).replace("u\'",'\'').replace("'",'"')
	print('{"offsettemperatures" : %s}' % newrows)

# OFFSETHUMIDITIES command
if params['cmd'] == "OFFSETHUMIDITIES":
	if DEBUG_MODE:
		print('cmd is OFFSETHUMIDITIES')
	devmac = params['devmac']

	# Group device's data
	if DEBUG_MODE:
		print('getting group device data')
	sql = "SELECT avg(hum) AS avg_hum, substring(timerstamp, 12, 2) AS hour FROM mcdata WHERE mac='%s' AND DATE_ADD(timerstamp, INTERVAL HOUR(now()) HOUR) >= now() GROUP BY hour" % devmac
	cursor.execute(sql)
	rows = cursor.fetchall()
	if DEBUG_MODE:
		print('group device data:')
		print(rows[:5])

	# Local Meteostat API data
	if DEBUG_MODE:
		print('getting local Meteostat API data')
	url = 'https://api.meteostat.net/v1/history/hourly'
	params = {'station': str(mac_to_station[devmac]), 'start': get_current_day(), 'end': get_current_day(), 'time_zone': "America/Los_Angeles",
	          'time_format': "Y-m-d%20H:i", 'key': "UcOLB4Z5"}
	r = requests.get(url, params=params)
	data = r.json()
	meteostat_data = data['data']
	if DEBUG_MODE:
		print('local Meteostat API data:')
		print(meteostat_data[:5])

	# add group's and local Meteostat API data to output
	if DEBUG_MODE:
		print('adding group and local Meteostat API data to output')
	newrows = []
	if DEBUG_MODE:
		print('getting group data')
	group_hums = [row.get('avg_hum', 0) for row in rows]
	if DEBUG_MODE:
		print('getting local Meteostat API data')
	meteostat_hums = [row.get('humidity', 0) for row in meteostat_data]
	if DEBUG_MODE:
		print('calculating offsets')
		print('group_hums:')
		print(group_hums[:5], len(group_hums))
		print('meteostat_hums:')
		print(meteostat_hums[:5], len(meteostat_hums))
	cur_offsets = calculate_offsets(group_hums, meteostat_hums)
	if DEBUG_MODE:
		print('cur_offsets:')
		print(cur_offsets)

	# Class data
	if DEBUG_MODE:
		print('getting class data')
	sql = "SELECT avg(hum) AS avg_hum, substring(timerstamp, 12, 2) AS hour FROM mcdata WHERE DATE_ADD(timerstamp, INTERVAL HOUR(now()) HOUR) >= now() GROUP BY hour"
	cursor.execute(sql)
	rows = cursor.fetchall()
	if DEBUG_MODE:
		print('class data:')
		print(rows[:5])

	# Average Meteostat API data
	if DEBUG_MODE:
		print('getting average Meteostat API data')
	stations = ["72290", "KRHV0", "72295", "72483", "72494", "72793", "72509"]
	all_meteostat_hums = []
	for station in stations:
		params = {'station': station, 'start': get_current_day(), 'end': get_current_day(), 'time_zone': "America/Los_Angeles",
		          'time_format': "Y-m-d%20H:i", 'key': "UcOLB4Z5"}
		r = requests.get(url, params=params)
		data = r.json()
		meteostat_data = data['data']
		meteostat_hums = [row.get('humidity', 0) for row in meteostat_data]
		all_meteostat_hums.append(meteostat_hums)
	all_meteostat_hums = [item for sublist in all_meteostat_hums for item in sublist]
	if DEBUG_MODE:
		print('average Meteostat API data:')
		print(all_meteostat_hums)

	# add class and all Meteostat API data to output
	if DEBUG_MODE:
		print('adding class and all Meteostat API data to output')
	all_group_hums = [row.get('avg_hum', 0) for row in rows]
	all_cur_offsets = calculate_offsets(all_group_hums, all_meteostat_hums)
	min_length = min(len(cur_offsets), len(all_cur_offsets))
	for i in range(min_length):
		row = rows[i]
		group_offset = cur_offsets[i]
		class_offset = all_cur_offsets[i]
		newrows.append([int(row['hour']), int(group_offset), int(class_offset)])
	if DEBUG_MODE:
		print('current output:')
		print(newrows)

	newrows = str(newrows).replace("u\'",'\'').replace("'",'"')
	print('{"offsethumidities" : %s}' % newrows)

# UPDATETABLE command
if params['cmd'] == "UPDATETABLE":
	devmac = params['devmac']
	sql = "SELECT avg(temp) AS avg_temp, avg(hum) AS avg_hum, substring(timerstamp, 12, 2) AS hour FROM mcdata WHERE mac='%s' AND DATE_ADD(timerstamp, INTERVAL HOUR(now()) HOUR) >= now() GROUP BY hour" % devmac
	cursor.execute(sql)
	rows = cursor.fetchall()
	newrows = []
	for row in rows:
		cur_dict = {"hour": int(row['hour']), "avg_temp": round(row['avg_temp'], 1), "avg_hum": round(row['avg_hum'], 1)}
		newrows.append(cur_dict)
	newrows = str(newrows).replace("u\'",'\'').replace("'",'"')
	print('{"mcdata" : %s}' % newrows)

cursor.close()
connection.close()

if DEBUG_MODE:
	print("connection is closed")
