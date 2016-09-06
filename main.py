# import dependencies
import requests
import httplib2
from bs4 import BeautifulSoup, SoupStrainer
import xlsxwriter

url = "http://www.nhl.com/scores/htmlreports/20152016/PL020790.HTM"

def write_out_sheet(sheet_name, data, workbook):
	'''
	Function takes a sheet name and writes the data set out to it.
	'''
	sheet = workbook.add_worksheet(sheet_name)
	
	r, c = 0, 0

	for row in data:

		for col in row:

			sheet.write(r, c, col)
			c += 1

		c = 0	
		r += 1

def scrape_game():
	'''
	Function takes a url of NHL.com game report and returns an excel workbook containing formated data for shots, goals,
	faceoffs, and penalties.
	'''
	# create a connection
	http = httplib2.Http()

	url = raw_input('Enter a url: ')

	status, response = http.request(url)

	soup = BeautifulSoup(response,'lxml')

	rows = soup.findAll('tr', {'class': 'evenColor'})

	shots = [['Event','Player','Time_1','Time_2']]
	goals = [['Event','Player', 'Assist_1', 'Assist_2', 'Time_1', 'Time_2']]
	faceoffs = [['Event', 'Winning_Player', 'Loosing_Player', 'Time_1', 'Time_2']]
	penalties = [['Event', 'Initiator', 'Reciever', 'Time_1', 'Time_2']]

	visitor = str(soup.findAll('table', {'id': 'Visitor'})[0].findAll('tr')[3].getText().split('Game')[0].replace(" ", "_"))
	home = str(soup.findAll('table', {'id': 'Home'})[0].findAll('tr')[3].getText().split('Game')[0].replace(" ", "_"))
	date = str(soup.findAll('table', {'id': 'GameInfo'})[0].findAll('tr')[3].getText().replace(" ", "_"))

	for row in rows:

		entry = row.findAll('td')

		index = entry[0].getText()
		time = entry[3].getText()
		event = entry[4].getText()
		meta = entry[5].getText()

		if time[1] == ":":
			time_1 = time[:4]
			time_2 = time[4:]

		else:
			time_1 = time[:5]
			time_2 = time[5:]

		if event == "SHOT":
			player = ''.join([i for i in meta.split("#",1)[1].split(",",1)[0] if not i.isdigit()]).replace(" ","")
			print event, player, time_1, time_2
			shots.append([event, player, time_1, time_2])

		if event == "GOAL":

			assists = len(meta.split("#")) - 2
			scorer = ''.join([i for i in meta.split("#",1)[1].split("(",1)[0] if not i.isdigit()]).replace(" ","")

			if assists > 0:
				assist_1 = ''.join([i for i in meta.split("#")[2].split("(")[0]if not i.isdigit()]).replace(" ","")
			else:
				assist_1 = 'NA'
				assist_2 = 'NA'

			if assists > 1:
				assist_2 = ''.join([i for i in meta.split("#")[3].split("(")[0]if not i.isdigit()]).replace(" ","")
			else:
				assist_2 = 'NA'

			print event, scorer, assist_1, assist_2, time_1, time_2
			goals.append([event,scorer,assist_1,assist_2,time_1,time_2])

		if event == "FAC":
			winning_team = meta.split("won",1)[0].replace(" ", "")

			if "vs" in meta.split(winning_team,1)[1].split(winning_team,1)[1]:

				winner = ''.join([i for i in meta.split("#",1)[1].split(" v",1)[0] if not i.isdigit()]).replace(" ","")
				loser = ''.join([i for i in meta.split("#",2)[2] if not i.isdigit()]).replace(" ","")

			else:

				loser = ''.join([i for i in meta.split("#",1)[1].split(" v",1)[0] if not i.isdigit()]).replace(" ","")
				winner = ''.join([i for i in meta.split("#",2)[2] if not i.isdigit()]).replace(" ","")

			print event, winner, loser, time_1, time_2
			faceoffs.append([event, winner, loser, time_1, time_2])

		if event == "PENL":

			initiator =''.join([i for i in meta.split("#",1)[1] if not i.isdigit()]).replace(" ","").split()[0]
			reciever = ''.join([i for i in meta.split("#",1)[1] if not i.isdigit()]).replace(" ","").split()[-1].split("#",1)[1]

			print event, initiator, reciever, time_1, time_2
			penalties.append([event, initiator, reciever, time_1, time_2 ])

	title = visitor + '_vs_' + home + '_' + date + '.xlsx'
	title = "".join(('\t'.join([line.strip() for line in title])).split())

	workbook = xlsxwriter.Workbook(title)

	write_out_sheet('shots', shots, workbook)
	write_out_sheet('goals', goals, workbook)
	write_out_sheet('faceoffs', faceoffs, workbook)
	write_out_sheet('penalties', penalties, workbook)
	workbook.close()


scrape_game()