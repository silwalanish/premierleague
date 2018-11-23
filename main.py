import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
from backbone import *
from database import *
from datetime import datetime

class Window(QMainWindow):
	
	def __init__(self):
		super().__init__()
		self.matchWeek = getCurrentMatchWeek()
		self.initUI()

	def initUI(self):
		self.setMinimumSize(800, 500)
		self.setGeometry(300, 100, 800, 500)
		self.setWindowTitle('Premier League')
		self.setWindowIcon(QIcon('logo.png'))

		self.cw = QWidget()
		self.mainlayout = QVBoxLayout()
		self.content = QWidget()

		scroll = QScrollArea()
		scroll.setWidgetResizable(True)
		scroll.setWidget(self.content)

		self.tabs = QTabWidget()
		self.teamsTab = QWidget()
		self.tableTab = QWidget()
		self.fixturesTab = QWidget()

		self.contentLayout = QVBoxLayout()

		self.teamsTabLayout = QVBoxLayout()
		self.tableTabLayout = QVBoxLayout()
		self.fixturesTabLayout = QVBoxLayout()

		self.teamsTab.setLayout(self.teamsTabLayout)
		self.tableTab.setLayout(self.tableTabLayout)
		self.fixturesTab.setLayout(self.fixturesTabLayout)

		self.tabs.addTab(self.teamsTab, "Teams")
		self.tabs.addTab(self.tableTab, "Table")
		self.tabs.addTab(self.fixturesTab, "Fixtures")

		self.contentLayout.addWidget(self.tabs)

		self.content.setLayout(self.contentLayout)	

		self.mainlayout.addWidget(scroll)

		self.cw.setLayout(self.mainlayout)

		self.setCentralWidget(self.cw)	

		self.tabs.currentChanged.connect(self.onTabChanged)
		self.tabs.setCurrentIndex(0)
		self.teamsTabUI()

	def onTabChanged(self, index):
		if (index == 0):
			self.teamsTabUI()
		elif (index == 1):
			self.tableTabUI()
		elif (index == 2):
			self.fixturesTabUI()

	def teamsTabUI(self):
		clearLayout(self.teamsTabLayout)
		self.teamLoader = TeamListRequest(445)
		self.teamLoader.onResponse.connect(self.onTeamList)
		self.teamLoader.start()

	def onTeamList(self, teamlist):
		for team in teamlist:
			self.teamsTabLayout.addWidget(TeamCard(team))

	def tableTabUI(self):
		clearLayout(self.tableTabLayout)
		self.tableLoader = TableRequest(445, self.matchWeek)
		self.tableLoader.onResponse.connect(self.onTable)
		self.tableLoader.start()

	def onTable(self, table):
		self.tableTabLayout.setContentsMargins(0, 0, 0, 0)
		self.tableTabLayout.setSpacing(0)
		self.tableTabLayout.addWidget(makeTable(table))

	def fixturesTabUI(self):
		clearLayout(self.fixturesTabLayout)
		self.gameweektabs = QTabWidget()
		for i in range(1, 39):
			widget = QWidget()
			layout = QVBoxLayout()
			widget.setLayout(layout)
			self.gameweektabs.addTab(widget, "Matchweek "+str(i))
		self.gameweektabs.currentChanged.connect(self.gameweekselect)
		self.gameweektabs.setCurrentIndex(self.matchWeek)
		self.fixturesTabLayout.addWidget(self.gameweektabs)

	def gameweekselect(self, index):
		self.fixtureLoader = FixtureRequest(445, index + 1)
		self.fixtureLoader.onResponse.connect(self.onFixtures)
		self.fixtureLoader.start()

	def onFixtures(self, fixtureList):
		widget = self.gameweektabs.currentWidget()
		layout = widget.layout()
		clearLayout(layout)
		if (fixtureList[0]):
			for fixture in fixtureList:
				layout.addWidget(Fixture(fixture))
		else:
			layout.addWidget(QLabel("An Error Encountered!"))
			layout.addStretch()

def main():
	app = QApplication(sys.argv)

	app.setStyleSheet(open('themes/default.themes').read())

	window = Window()
	window.show()

	sys.exit(app.exec_())


if __name__ == '__main__':
	main()
