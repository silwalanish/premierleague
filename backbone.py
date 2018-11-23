from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QGraphicsDropShadowEffect, QSizePolicy
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QSize
from PyQt5.QtGui import QImage, QColor, QPixmap
from database import *
from datetime import datetime
import urllib.request
import json
import sys

BASE_URL = "http://api.football-data.org/v1/"
API_KEY = open('football.api_key').read()

try:
    import httplib
except:
    import http.client as httplib

def have_internet():
    conn = httplib.HTTPConnection("www.google.com", timeout=5)
    try:
        conn.request("HEAD", "/")
        conn.close()
        return True
    except:
        conn.close()
        return False

def getCurrentMatchWeek():
	url = BASE_URL + "/competitions/445/leagueTable"
	headers = {
				'X-Auth-Token': API_KEY,
				'X-Response-Control': 'minified'
				}
	request = urllib.request.Request(url, headers = headers)
	response = json.loads(urllib.request.urlopen(request).read())
	return int(response['matchday'])


def clearLayout(layout):
	for i in reversed(range(layout.count())): 
		if (layout.itemAt(i).widget()):
			layout.itemAt(i).widget().setParent(None)

def makeTable(table):
	cont = QWidget()
	tableLayout = QVBoxLayout()
	header = QWidget()
	layout = QHBoxLayout()
	headerPos = QLabel("Position")
	headerPos.setObjectName("Pos")
	layout.addWidget(headerPos)
	headerLogo = QLabel("Logo")
	headerLogo.setObjectName("Logo")
	layout.addWidget(headerLogo)
	headerTeam = QLabel("Team")
	headerTeam.setObjectName("TeamName")
	layout.addWidget(headerTeam)
	layout.addWidget(QLabel("P"))
	layout.addWidget(QLabel("W"))
	layout.addWidget(QLabel("D"))
	layout.addWidget(QLabel("L"))
	layout.addWidget(QLabel("G"))
	layout.addWidget(QLabel("GA"))
	layout.addWidget(QLabel("GD"))
	layout.addWidget(QLabel("PTS"))
	header.setLayout(layout)
	header.setObjectName("TableHeader")

	tableLayout.addWidget(header)
	for row in table:
		tableLayout.addWidget(Row(row))
	tableLayout.setSpacing(0)
	tableLayout.setContentsMargins(0, 0, 0, 0)
	cont.setLayout(tableLayout)
	return cont

class Fixture(QWidget):

	def __init__(self, fixture):
		super().__init__()
		self.date = fixture['date']
		self.stat = fixture['stat']
		self.htId = fixture['htId']
		self.atId = fixture['atId']
		self.res = fixture['res']

		self.initUI()

	def initUI(self):
		self.mainlayout = QVBoxLayout()
		self.content = QWidget()
		self.contentLayout = QHBoxLayout()

		self.htlogo = QLabel()
		self.atlogo = QLabel()
		self.htname = QLabel()
		self.atname = QLabel()
		self.resCont = QLabel()

		self.htlogo.setPixmap(QPixmap("badge-50x50.png"))
		self.atlogo.setPixmap(QPixmap("badge-50x50.png"))

		self.row = QHBoxLayout()
		self.dateCont = QLabel()
		datetime_object = datetime.strptime(self.date, "%Y-%m-%dT%H:%M:%SZ")
		self.dateCont.setText(datetime.strftime(datetime_object, "%d, %b %H:%M"))
		self.dateCont.setObjectName("DateCont")
		self.row.addStretch()
		self.row.addWidget(self.dateCont)
		self.row.addStretch()

		self.mainlayout.addLayout(self.row)

		self.ht = Team.get(self.htId)
		self.at = Team.get(self.atId)

		self.htname.setText(self.ht.name.replace(" FC", ""))
		self.atname.setText(self.at.name.replace(" FC", ""))
		self.resCont.setText((str(self.res['ght']) + ' - ' + str(self.res['gat'])) if self.stat == "FINISHED" else self.stat)

		self.contentLayout.addWidget(self.htlogo)
		self.contentLayout.addWidget(self.htname)
		self.contentLayout.addStretch()
		self.contentLayout.addWidget(self.resCont)
		self.contentLayout.addStretch()
		self.contentLayout.addWidget(self.atname)
		self.contentLayout.addWidget(self.atlogo)

		self.contentLayout.setContentsMargins(0, 0, 0, 0)
		self.content.setLayout(self.contentLayout)

		self.shadow = QGraphicsDropShadowEffect()
		self.shadow.setBlurRadius(5)
		self.shadow.setXOffset(5)
		self.shadow.setYOffset(5)
		self.shadow.setColor(QColor(56, 0, 60, 255))

		self.content.setGraphicsEffect(self.shadow)

		self.mainlayout.addWidget(self.content)
		self.mainlayout.setSpacing(0)
		self.setLayout(self.mainlayout)

		self.setObjectName('Fixture')
		self.htlogo.setObjectName('Logo')
		self.atlogo.setObjectName('Logo')
		self.htname.setObjectName('TeamName')
		self.atname.setObjectName('TeamName')
		self.resCont.setObjectName('Result')

		self.htLogoloader = ImageRequest(self.ht.crestUrl, (50, 50))
		self.atLogoLoader = ImageRequest(self.at.crestUrl, (50, 50))

		self.htLogoloader.onResponse.connect(self.onHtLogo)
		self.atLogoLoader.onResponse.connect(self.onAtLogo)

		self.htLogoloader.start()
		self.atLogoLoader.start()

	def onHtLogo(self, image):
		self.htlogo.setPixmap(QPixmap(image))

	def onAtLogo(self, image):
		self.atlogo.setPixmap(QPixmap(image))

class Row(QWidget):

	def __init__(self, row):
		super().__init__()
		self.row = row
		self.initUI()

	def initUI(self):
		self.mainlayout = QVBoxLayout()
		self.cont = QWidget()
		self.contLayout = QHBoxLayout()

		self.position = QLabel()
		self.logo = QLabel()
		self.teamName = QLabel()
		self.playedGames = QLabel()
		self.wins = QLabel()
		self.draws = QLabel()
		self.losses = QLabel()
		self.goals = QLabel()
		self.goalsAgainst = QLabel()
		self.goalsDiff = QLabel()
		self.points = QLabel()

		self.team = Team.get(self.row.team_id)

		self.logo.setPixmap(QPixmap("badge-50x50.png"))
		self.position.setNum(self.row.position)
		self.teamName.setText(self.team.name)
		self.playedGames.setNum(self.row.playedGames)
		self.wins.setNum(self.row.wins)
		self.draws.setNum(self.row.draws)
		self.losses.setNum(self.row.losses)
		self.goals.setNum(self.row.goals)
		self.goalsAgainst.setNum(self.row.goalsAgainst)
		self.goalsDiff.setNum(self.row.goals - self.row.goalsAgainst)
		self.points.setNum((self.row.wins * 3) + (self.row.draws * 1))

		self.contLayout.addWidget(self.position)
		self.contLayout.addWidget(self.logo)
		self.contLayout.addWidget(self.teamName)
		self.contLayout.addWidget(self.playedGames)
		self.contLayout.addWidget(self.wins)
		self.contLayout.addWidget(self.draws)
		self.contLayout.addWidget(self.losses)
		self.contLayout.addWidget(self.goals)
		self.contLayout.addWidget(self.goalsAgainst)
		self.contLayout.addWidget(self.goalsDiff)
		self.contLayout.addWidget(self.points)

		self.cont.setLayout(self.contLayout)

		self.cont.setObjectName("TableRow")
		self.teamName.setObjectName("TeamName")
		self.logo.setObjectName("Logo")
		self.position.setObjectName("Pos")

		self.mainlayout.addWidget(self.cont)
		self.setLayout(self.mainlayout)
		self.mainlayout.setContentsMargins(0,0,0,0)

		self.imageLoader = ImageRequest(self.team.crestUrl, (50, 50))
		self.imageLoader.onResponse.connect(self.onImageLoad)
		self.imageLoader.start()

	def onImageLoad(self, image):
		self.logo.setPixmap(QPixmap(image))

class TeamCard(QWidget):

	def __init__(self, team):
		super().__init__()
		self.team = team
		
		self.initUI()

	def initUI(self):
		self.card = QWidget()
		self.cardLayout = QVBoxLayout()

		self.layout = QHBoxLayout()
		self.logo = QLabel()
		self.desLayout = QVBoxLayout()

		self.logo.setPixmap(QPixmap("badge-50x50.png"))

		self.nameLabel = QLabel()
		self.nameLabel.setText(self.team.name+"("+ self.team.shortName +")")
		self.desLayout.addWidget(self.nameLabel)

		if (self.team.squadMarketValue):
			self.teamValue = QLabel()
			self.teamValue.setText(self.team.squadMarketValue)
			self.desLayout.addWidget(self.teamValue)
		
		self.layout.addWidget(self.logo)
		self.layout.addLayout(self.desLayout)
		self.layout.addStretch()
		self.layout.setSpacing(0)
		self.layout.setContentsMargins(0, 0, 0, 0)

		self.card.setLayout(self.layout)
		self.shadow = QGraphicsDropShadowEffect()
		self.shadow.setBlurRadius(5)
		self.shadow.setXOffset(2)
		self.shadow.setYOffset(2)
		self.shadow.setColor(QColor(0, 0, 0, 125))
		self.card.setGraphicsEffect(self.shadow)

		self.imageLoader = ImageRequest(self.team.crestUrl, (50, 50))
		self.imageLoader.onResponse.connect(self.onImageLoad)
		self.imageLoader.start()

		self.card.setObjectName("TeamCard")
		self.nameLabel.setObjectName("Title")
		self.logo.setObjectName("Image")

		self.cardLayout.addWidget(self.card)
		self.setLayout(self.cardLayout)

	def onImageLoad(self, image):
		self.logo.setPixmap(QPixmap(image))

class NetworkRequest(QThread):

	onResponse = pyqtSignal(dict)

	def __init__(self, url, headers):
		super().__init__()
		self.url = url
		self.headers = headers
		if (self.headers):
			self.request = urllib.request.Request(self.url, headers = self.headers)
		else:
			self.request = self.url

	def run(self):		
		response = self.getResponse()
		if (response):
			response = json.loads(response)
			self.onResponse.emit(response)
		else:
			self.onResponse.emit({error: True})

	def getResponse(self):
		try:
			response = urllib.request.urlopen(self.request).read()
		except Exception as e:
			print (e)		
			response = None
		return response

class ImageRequest(NetworkRequest):

	cache = dict()

	onResponse = pyqtSignal(QImage)

	def __init__(self, url, size, headers = None):
		super().__init__(url, headers)
		self.size = size

	def run(self):
		if (self.url in self.cache): 
			self.onResponse.emit(self.cache[self.url])
			return
		imageData = self.getResponse()
		if (imageData):
			image = QImage.fromData(imageData)
			image = image.scaled(self.size[0], self.size[1], Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
			self.cache[self.url] = image
			self.onResponse.emit(image)
		else:
			self.onResponse.emit(QImage(self.size[0], self.size[1], QImage.Format_RGBA8888))

class FixtureRequest(NetworkRequest):

	onResponse = pyqtSignal(list)

	def __init__(self, leagueId, matchDay):
		url = BASE_URL + "/competitions/"+ str(leagueId) + "/fixtures/?matchday="+ str(matchDay)
		headers = {
					'X-Auth-Token': API_KEY,
					'X-Response-Control': 'compressed'
					}
		super().__init__(url, headers)

		self.leagueId = leagueId
		self.matchDay = matchDay

	def run(self):
		response = self.getResponse()
		if (response):
			response = json.loads(response)
			self.onResponse.emit(response['fixtures'])
		else:
			self.onResponse.emit([None])

class TableRequest(NetworkRequest):

	onResponse = pyqtSignal(list)

	def __init__(self, leagueId, matchDay):
		url = BASE_URL + "/competitions/"+ str(leagueId) + "/leagueTable?matchday="+ str(matchDay)
		headers = {
					'X-Auth-Token': API_KEY,
					'X-Response-Control': 'full'
					}
		super().__init__(url, headers)
		self.leagueId = leagueId
		self.matchDay = matchDay

	def run(self):
		response = self.getResponse()
		if (response):
			response = json.loads(response)
			Table.updateTable(response['standing'])
		self.onResponse.emit(Table.all())

class TeamListRequest(NetworkRequest):

	onResponse = pyqtSignal(list)

	def __init__(self, leagueId):
		url = BASE_URL + "/competitions/"+ str(leagueId) +"/teams"
		headers = {
				'X-Auth-Token' : API_KEY,
				'X-Response-Control' : 'full'
				}
		super().__init__(url, headers)
		self.leagueId = leagueId

	def run(self):
		response = self.getResponse()
		if (response):
			response = json.loads(response)
			for team in response['teams']:
				self.addTeam(team)
		allteam = Team.all()
		self.onResponse.emit(allteam)

	def addTeam(self, teaminfo):
		id = getIDFromURL(teaminfo['_links']['self']['href'])
		team = Team.get(id)
		if team == None:
			team = Team(teaminfo, id = id)
			try:
				team.insert()
				team.save()
			except Exception as e:
				print (e)

