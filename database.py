import sqlite3
import re


def getIDFromURL(url):
	id = re.findall(r'\d+', url)
	return id[-1]

class Database(object):

	db = None

	@staticmethod
	def connect():
		Database.db = sqlite3.connect("data/database.sqlite3", check_same_thread=False)

	@staticmethod
	def cursor():
		if (Database.db == None):
			Database.connect()
		return Database.db.cursor()

	@staticmethod
	def close():
		Database.db.close()
		Database.db = None

class Model(object):

	sql = ""

	primary_key = "id"

	search_key = "id"

	table = ""

	fields = []
	
	def __init__(self, *args, **kwargs):
		super().__init__()
		for field in self.fields:
			setattr(self, field, None)
		if (args):
			for field in args[0]:
				if (field in self.fields):
					setattr(self, field, args[0][field])
		if (kwargs):
			for field in kwargs:
				if (field in self.fields):
					setattr(self, field, kwargs[field])

	def insert(self):
		query = "INSERT INTO "
		query += self.table
		query += "("
		for field in self.fields:
			query += field + (", " if (field != self.fields[-1]) else "")
		query += ") values ("
		for i in range(len(self.fields)):
			query += "?" + ("," if (i != len(self.fields)-1) else "")
		query += ")"

		try:
			Database.cursor().execute(query, tuple(getattr(self, field) for field in self.fields))
		except sqlite3.IntegrityError as e:
			print ("Some Values Were not set.")
			print (e)
	
	def update(self):
		query = "UPDATE "
		query += self.table
		query += " SET "
		for field in self.fields:
			query += field + "= ?" + (", " if (field != self.fields[-1]) else "")
		query += " WHERE " + self.primary_key + " = '"+ getattr(self, self.primary_key) +"'"
		try:
			Database.cursor().execute(query, tuple(getattr(self, field) for field in self.fields))
		except e:
			print ("Some Error Occurred")
			print (e)

	def delete(self):
		query = "DELETE FROM " + self.table + " WHERE " + self.primary_key + " = '"+ getattr(self, self.primary_key) +"'"
		try:
			Database.cursor().execute(query)
		except e:
			print ("Some Error Occurred")
			print (e)

	def save(self):
		Database.db.commit()

	@classmethod
	def get(cls, id):
		result = Database.cursor().execute("Select * from "+ cls.table +" where `"+ cls.search_key +"`='" + str(id) + "'").fetchone()
		if (result):
			return cls.fromTuple(result)
		else:
			return None

	@classmethod
	def all(cls):
		result = Database.cursor().execute("Select * from "+ cls.table).fetchall()
		return [cls.fromTuple(row) for row in result]

	@classmethod
	def fromTuple(cls, data):
		obj = cls()
		setattr(obj, cls.primary_key, data[0])
		for i in range(1, len(data)):
			setattr(obj, cls.fields[i-1], data[i])
		return obj

	@classmethod
	def setup(cls):
		Database.cursor().execute("DROP TABLE IF EXISTS "+ cls.table)
		Database.cursor().execute(cls.sql)

class Table(Model):

	sql = """CREATE TABLE leagueTable(
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		team_id INTEGER NOT NULL,	
		position INTEGER NOT NULL,
		playedGames INTEGER NOT NULL,		
		wins INTEGER NOT NULL,
		draws INTEGER NOT NULL,
		losses INTEGER NOT NULL,
		goals INTEGER NOT NULL,
		goalsAgainst INTEGER NOT NULL
	)"""

	table = "leagueTable"

	fields = ['team_id', 'position', 'playedGames', 'wins', 'draws', 'losses', 'goals', 'goalsAgainst']

	@staticmethod
	def updateTable(latestTable):
		Database.cursor().execute('DELETE FROM leagueTable')
		Database.db.commit()
		for row in latestTable:
			tableRow = Table(row, team_id = getIDFromURL(row['_links']['team']['href']))
			tableRow.insert()
			tableRow.save()

class Team(Model):

	sql = """CREATE TABLE teams(
		team_id INTEGER PRIMARY KEY AUTOINCREMENT,
		id INTEGER NOT NULL,
		name TEXT NOT NULL,
		code TEXT NOT NULL,
		shortName TEXT,
		squadMarketValue TEXT,
		crestUrl TEXT
	)"""

	primary_key = 'team_id'

	search_key = 'id'

	table = "teams"

	fields = ['id', 'name', 'code', 'shortName', 'squadMarketValue', 'crestUrl']


