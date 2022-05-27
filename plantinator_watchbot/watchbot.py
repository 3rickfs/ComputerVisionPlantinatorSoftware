"""
Plantinator watchbot
--------------------

Programm for sending queries to ClassifierRobotPredictions mysql database 
and seeking for changes to update web app dashboard

"""

import mysql.connector
import sys
import environ
from datetime import datetime
import requests
import json

env = environ.Env()
environ.Env.read_env()

class DBOperator():
	def __init__(self):
		self.usr = env('DATABASE_USER')
		self.pw = env('DATABASE_PW')
		self.ht = env('DATABASE_HOST')
		self.pt = env('DATABASE_PORT')
		self.db_name = env('DATABASE_NAME')
		self.conn = ""
		self.cursor = ""
		self.results = []

	def Connect2DB(self):
		#Connect to MariaDB database
		try:
			conn = mysql.connector.connect(
											host=self.ht,
											user=self.usr,
											port=self.pt,
											password=self.pw,
											database=self.db_name,
											)
		except mysql.connector.Error as e:
			print(f"Database connection fatal error: {e}")
			sys.exit(1)

    	#Return db connection and cursor
		return conn, conn.cursor()

	def connect_disconnect_DB(func):
		def inner(self, *args, **kwargs):
			self.conn, self.cursor = self.Connect2DB()
			func(self, *args, **kwargs)
			self.closeDBconn()
		return inner
    
	def star_decorator(func):
		def inner(*args, **kwargs):
			print("*" * 60)
			func(*args, **kwargs)
			print("*" * 60)
		return inner
    
	def closeDBconn(self):
		print("closing open database")
		self.cursor.close()
		self.conn.close()

	@star_decorator
	@connect_disconnect_DB
	def insert_data(self, tname, data, columns):
		print(f"Filling out {tname} table")
		print(f"INSERT INTO {tname} ({columns}) VALUES ({data});")
		self.cursor.execute(f"INSERT INTO {tname} ({columns}) VALUES ({data});")
		self.conn.commit()
		print("data inserted into table")

	@star_decorator
	@connect_disconnect_DB
	def update_data(self, table, column, dataid, newvalue):
		print(f"updating some data in table: {table}, column: {column}, dataid: {dataid} and newvalue: {newvalue}")
		if type(newvalue) == type(date.today()) or type(newvalue) == type(3.14) or type(newvalue) == type(3):
			if type(newvalue) == type(date.today()): newvalue = "STR_TO_DATE('" + newvalue.strftime("%d-%m-%Y") + "', '%d-%m-%Y')"            
			print(f"UPDATE {table} SET {column} = {newvalue} WHERE id={dataid};")
			self.cursor.execute(f"UPDATE {table} SET {column} = {newvalue} WHERE id={dataid};")
		else:
			if type(newvalue) == type('string'):
				print(f"UPDATE {table} SET {column}='{newvalue}' WHERE id={dataid};")
				self.cursor.execute(f"UPDATE {table} SET {column}='{newvalue}' WHERE id={dataid};")                
		self.conn.commit()
		print("data finally updated")

	@star_decorator
	@connect_disconnect_DB
	def read_data(self,table,cname,value):
		print(f"Reading table: {table}")
		self.cursor.execute(f"SELECT * FROM {table} WHERE {cname} = {value};")
		self.get_select_query_results()

	def get_select_query_results(self):
		self.results = []
		for d in self.cursor:
			self.results.append(d)

class DBTransmitter():
	def __init__(self):
		self.user_agent_name = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0"
		self.loginpage_url = "http://localhost:8000/login/?next=/"
		self.postrequest_url = "http://localhost:8000/bridge_script_webapp/" #"http://localhost:8000/"
		self.ws_csrfmiddlewaretoken = env('WS_CSRF')
		self.ws_username = env('WS_USERNAME')
		self.ws_password = env('WS_PASSWORD')
		self.data = None
		self.response = None
		self.rqstjson = None

		#Here the request formation
		#Sending post request
		#publishig results

	def send_data(self, data):
		print("Preparing for post request")
		self.data = data
		self.request_generator()
		self.push_post_request()
		self.print_results()

		
	def request_generator(self):
		print("Generating request")
		pred_num = len(self.data)
		colnames = ["prediction_" + str(i+1) for i in range(pred_num)]
		rqst = {}
		for r, c in enumerate(self.data):
			cc = [i for i in c]
			cc[1] = str(cc[1].isoformat())
			cc[2] = str(cc[2])
			rqst[colnames[r]] = cc
		#print(rqst)
		self.rqstjson = json.dumps(rqst)
		print(rqst)

	def push_post_request(self):
		# Create session
		session = requests.session()

		# Add user-agent string
		session.headers.update({'User-Agent': self.user_agent_name})

		# Get login page
		#response = session.get(self.loginpage_url)
		#print(response.text)
		# Get csrf
		# Do something to response.text

		# Post to login
		#print(f"CSRF token: {self.ws_csrfmiddlewaretoken}")

		#self.response = session.post(self.loginpage_url, data={
		#    'username': self.ws_username,
		#    'password': self.ws_password,},
		#    cookies= {'csrftoken': 'D4YtG9SrjXURwdxFYhjy2i3TpA0jQDuomf8ms7jZs4qtOhX6l2krDVi4AaNie5ny'}, #self.ws_csrfmiddlewaretoken,
		#)

		#'csrfmiddlewaretoken': 'enN9mr2LpfE6JvNy8jx5yx82KLiHYFxTDeNOxyRCi91u3ATQMyQ5GielBmyl1xwb' #self.ws_csrfmiddlewaretoken,
		#'csrftoken': 'enN9mr2LpfE6JvNy8jx5yx82KLiHYFxTDeNOxyRCi91u3ATQMyQ5GielBmyl1xwb' #self.ws_csrfmiddlewaretoken,
		#cookie = {'csrftoken': self.ws_csrfmiddlewaretoken},
		#cookies = {'csrftoken': csrf_token}
		#requests.post(var["BASE_URL"] + "_api/send-notification/", json=data, headers=headers, cookies=cookies)

		# Post desired data
		self.response = session.post(self.postrequest_url, data={
		    'data': self.rqstjson,
		})

	def print_results(self):
		print("There are results here!")
		print(self.response.status_code)
		#print(self.response.text)


def datalist2bsent(res):
	dl2bs = []
	for d in res:
		if d[7] == 0:
			dl2bs.append(d)
	return dl2bs


if __name__ == '__main__':
	dboperator = DBOperator()
	dbtransmitter = DBTransmitter()
	dboperator.read_data('RobotPredictions','DeliveredPrediction',0)
	data2bsend = datalist2bsent(dboperator.results)
	#print(data2bsend[1])
	#ndata = json.dumps(data2bsend)
	#print(ndata)
	dbtransmitter.send_data(data2bsend) #Send information to the server going through post requests


	