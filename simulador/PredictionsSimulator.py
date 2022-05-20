"""
PREDICTION SIMULATOR
--------------------

this program is for filling out RobotPredictions table from ClassificatoRobotPrediction database
so as to a bot (a python deamon) sends data to the dashboard web app of plantinator's

The idea is when the complete plantinator system gets production stage, the local data produced 
by the robot is sent to the dashboard running in heroku cloud platform

"""

import mysql.connector
import sys
import environ
from datetime import datetime
import random
import time

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

if __name__ == "__main__":
	#Testing class
	dboperator = DBOperator()    
	npred = 10 #predictions
	for p in range(npred):
		today = datetime.now().strftime("%d-%m-%Y")
		ttime = datetime.now().strftime("%H:%M")
		numseeddet = random.randrange(4)
		sq1, sq2, sq3 = random.randrange(4), random.randrange(4), random.randrange(4)
		delpred = 0

		datavals = f"STR_TO_DATE('{today}','%d-%m-%Y'), '{ttime}', {numseeddet}, {sq1}, {sq2}, {sq3}, {delpred}"
		columnnames = "PredDate, PredTime, Num_Seedl_detected, SeedlQ1, SeedlQ2, SeedlQ3, DeliveredPrediction"

		dboperator.insert_data("RobotPredictions", datavals, columnnames)

		time.sleep(60)