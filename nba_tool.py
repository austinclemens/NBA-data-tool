from __future__ import division

import urllib2
import string
import time
import re
import os
import pyPdf
import json
import csv
import datetime
import math
import nltk
import sys
from numpy import *
import numpy as numpy
import pandas as pd
import matplotlib.pyplot as plt
import scipy
import sklearn
import scipy
from sklearn import linear_model
from operator import itemgetter

# NOTES:
# Problems as of 1/27:
# getday needs to be modified to be more forgiving when there are typos (some games are not being picked up) (not urgent)
# Some players are still being recorded as blanks when sides are written.  Not sure what part of the function this originates from.
# Some way to deal with the triple quotes thing? (not urgent)

# to run this: execfile("/Users/austinc/Desktop/Current Work/NBA/NBA Stats/nba_tool.py")

teamlist=["76ers","mavericks","celtics","lakers","grizzlies","pacers","spurs","bobcats","bucks","bulls","cavaliers","clippers","hawks","heat","jazz","kings","knicks","magic","nets","nuggets","pelicans","pistons","raptors","rockets","suns","thunder","timberwolves","trail blazers","warriors","wizards"]

def getday(day,month,year):
	"""This function downloads a gamebook for a given day, month, and year, and places it in
	the unprocessed gamebooks folder. This is kind of bugged - NBA.com sometimes typos the dates
	on games and this needs to be rewritten slightly to forgive those kinds of errors and get
	the game anyways."""
	if month<10:
		month="0%s" % (month)
	if day<10:
		day="0%s" % (day)
	url="http://www.nba.com/gameline/%s%s%s/" % (year,month,day)
	print url
	day_games=urllib2.urlopen(url).read()
	gameid_find=re.compile('/[0-9]{4}/[0-9]{2}/[0-9]{2}/([0-9]{10})-(...)-(...)-')
	games=gameid_find.findall(day_games)
	games=[game for game in set(games)]
	print games
	for game in games:
		url='http://www.nba.com/data/html/nbacom/2013/gameinfo/%s%s%s/%s_Book.pdf' % (year,month,day,game[0])
		print url
		f = urllib2.urlopen(url)
		data = f.read()
		with open("/Users/austinc/Desktop/Current Work/NBA/unprocessed_gamebooks/%s%s%s_%s.pdf" % (year,month,day,game[0]), "wb") as code:
			code.write(data)



def get_gamebooks(startmonth,startday,startyear,endmonth,endday,endyear):
	"""This function retrieves gamebooks from NBA.com. These books give the starters for each
	quarter. It takes six arguments: the month, day, and year you want to start collecting
	gamebooks from, and the month, day, and year you want to stop collecting gamebooks. It
	is inclusive of these two dates. I have no idea what would happen if you tried to use this
	for years prior to the 2013-2014 season."""
	try:
		startmonth=int(startmonth)
		startday=int(startday)
		startyear=int(startyear)
		endmonth=int(endmonth)
		endday=int(endday)
		endyear=int(endyear)
	except:
		print "All arguments need to be whole numbers."
	currentyear=int(time.strftime("%Y"))
	currentmonth=int(time.strftime("%m"))
	currentday=int(time.strftime("%d"))
	if currentyear<endyear or (currentyear==endyear and currentmonth<endmonth) or (currentyear==endyear and currentmonth==endmonth and currentday<endday):
		print "I can't retrieve games that haven't happened yet. Retrieving games from start date to present."
		if currentyear<endyear:
			endyear=currentyear
		if currentyear==endyar and currentmonth<endmonth:
			endmonth=currentmonth
		if currentyear==endyear and currentmonth==endmonth and currentday<endday:
			endday=currentday
	if startyear<2013:
		print 'Results may be unpredictable for seasons before 2013-2014...'
	dates=[]
	while startyear<endyear or startmonth<endmonth or startday<=endday:
		dates.append([startday,startmonth,startyear])
		if startmonth==12 and startday==31:
			startyear=startyear+1
		if startday==31:
			startmonth=(startmonth+1)%13
		startday=(startday+1)%32
	dates=[date for date in dates if date[0]!=0]
	dates=[date for date in dates if date[1]!=0]
	for date in dates:
		getday(date[0],date[1],date[2])
	


def get_draft_data(year1,year2):
	"""This function scrapes data on draft picks and the per of those picks from basketball-reference.com"""
	direct='/Users/austinc/Desktop/'
	for year in range(year1,year2):
		url='http://www.basketball-reference.com/draft/NBA_%s.html' % (year)
		f = urllib2.urlopen(url)
		data = f.read()
		player_record=re.compile('<td align="right"  csk="[0-9]{1,2}">([0-9]{1,2})</td>\n   <td align="left"  csk="...\.[0-9]{1,3}"><a href="/teams/.../draft.html" title=".*?">(...)</a></td>\n   <td align="left"  csk=".*?">(.*?)</td>\n   <td align="left"  csk=".*?">.*?</td>\n   <td align="right" >(.*?)</td>\n   <td align="right" >(.*?)</td>\n   <td align="right" >(.*?)</td>\n   <td align="right" >(.*?)</td>\n   <td align="right" >(.*?)</td>\n   <td align="right" >(.*?)</td>\n   <td align="right" >(.*?)</td>\n   <td align="right" >(.*?)</td>\n   <td align="right" >(.*?)</td>\n   <td align="right" >(.*?)</td>\n   <td align="right" >(.*?)</td>\n   <td align="right" >(.*?)</td>\n   <td align="right" >(.*?)</td>\n   <td align="right" >(.*?)</td>\n</tr>')
		drafted=player_record.findall(data)
		player_name=re.compile('>(.*?)<')
		url_pname=re.compile('"(/players/*/.*?.html)"')
		drafted2=[]
		for player in drafted:
			player=list(player)
			player.append(year)
			if player[2][0]=="<":
				pname=player_name.findall(player[2])[0]
				player.append(pname)
				player[2]=url_pname.findall(player[2])[0]
			else:
				player.append(player[2])
				player[2]=""
			drafted2.append(player)
		drafted3=[]
		for player in drafted2:
			if player[2]=="":
				player.append(0)
				drafted3.append(player)
			else:
				url='http://www.basketball-reference.com%s' % (player[2])
				print url
				f=urllib2.urlopen(url)
				p_stats=f.read()
				per_find=re.compile('<tr  class="full_table" id="advanced.[12][09]..">\n   <td align="left".*?</td>\n   <td align="right".*?</td>\n   <td align="left".*?</td>\n   <td align="left".*?</td>\n   <td align="center".*?</td>\n   <td align="right".*?</td>\n   <td align="right".*?>(.*?)</td>\n   <td align="right".*?>(.*?)</td>')
				pers=per_find.findall(p_stats)
				try:
					pers1=[float(per[1]) for per in pers if int(per[0])>=200]
				except:
					pers1=[]
				print pers
				try:
					player.append(max(pers1))
				except:
					player.append(0)
				for per in pers:
					if int(per[0])>=200:
						player.append(per[1])
					if int(per[0])<200:
						player.append(per[0])
				drafted3.append(player) 
		with open('/Users/austinc/Desktop/Current Work/NBA/draft_data.csv','a') as csvfile:
			writer=csv.writer(csvfile)
			for row in drafted3:
				writer.writerow(row)




def process_gamebooks(diagnostics=0):
	"""This function processes all gamebooks in the unprocessed gamebooks folder, unless the file
	'processed.txt' shows the gamebook has already been processed. Processed gamebooks are moved
	to the processed gamebooks folder"""
	direct='/Users/austinc/Desktop/Current Work/NBA/unprocessed_gamebooks/'
	gamebooks=os.listdir(direct)
	completion_check=[line for line in open('%sprocessed.txt' % (direct),'rb')]
	for gamebook in gamebooks:
		if '%s\n' % (gamebook) not in completion_check and gamebook[0]!='.':
			game_text=[]
			date=gamebook[:8]
			date=datetime.datetime(int(date[0:4]),int(date[4:6]),int(date[6:8]))
			pdf=pyPdf.PdfFileReader(open('%s%s' % (direct,gamebook),'rb'))
			print '%s%s' % (direct,gamebook)
			for page in pdf.pages:
				game_text.append(page.extractText())
			find_first=re.compile('(1ST QUARTER ONLY)')
			find_second=re.compile('(2ND QUARTER ONLY)')
			find_third=re.compile('(3RD QUARTER ONLY)')
			find_fourth=re.compile('(4TH QUARTER ONLY)')
			find_first_pbp=re.compile('(Start of 1st Period)')
			find_second_pbp=re.compile('(Start of 2nd Period)')
			find_third_pbp=re.compile('(Start of 3rd Period)')
			find_fourth_pbp=re.compile('(Start of 4th Period)')
			find_1stot_pbp=re.compile('(Start of 1st OT)')
			find_2ndot_pbp=re.compile('(Start of 2nd OT)')
			find_3rdot_pbp=re.compile('(Start of 3rd OT)')
			find_end_fourth_pbp=re.compile('(End of 4th Period)')
			find_end_1stot_pbp=re.compile('(End of 1st OT)')
			find_end_2ndot_pbp=re.compile('(End of 2nd OT)')
			find_end_3rdot_pbp=re.compile('(End of 3rd OT)')
			find_teams=re.compile('(?:1234FINAL|12341OTFINAL|12341OT2OTFINAL|12341OT2OT3OTFINAL)(76ers|Trail Blazers|[a-zA-Z]*?)[0-9]{6,17}(76ERS|TRAIL BLAZERS|[a-zA-Z]*?)[0-9]')
			teams=find_teams.findall(game_text[0])
			teams=[list(teams[0])]
			if teams[0][1]=="ERS":
				teams[0][1]="76ERS"
			print teams
			away_team=teams[0][0]
			home_team=teams[0][1]
			pfind=re.compile("[ ]{0,1}[0-9]{1,2}([A-Za-z\.\-' ]{1,40})[0-9]{1,2}:")
			team0_temp=pfind.findall(game_text[0].split('TOTALS')[0])
			team1_temp=pfind.findall(game_text[0].split('TOTALS')[1])
			away=[]
			home=[]
			for player in team0_temp:
				if player[-1]=="G" or player[-1]=="F" or player[-1]=="C":
					away.append(player[0:-1])
				else:
					away.append(player)
			for player in team1_temp:
				if player[-1]=="G" or player[-1]=="F" or player[-1]=="C":
					home.append(player[0:-1])
				else:
					home.append(player)
			for page in game_text:
				if len(find_first_pbp.findall(page))>0:
					first_pbp_page=game_text.index(page)
				if len(find_second_pbp.findall(page))>0:
					second_pbp_page=game_text.index(page)
				if len(find_third_pbp.findall(page))>0:
					third_pbp_page=game_text.index(page)
				if len(find_fourth_pbp.findall(page))>0:
					fourth_pbp_page=game_text.index(page)
				if len(find_end_fourth_pbp.findall(page))>0:
					fourth_end_page=game_text.index(page)
				if len(find_end_1stot_pbp.findall(page))>0:
					ot1_end_page=game_text.index(page)
				if len(find_1stot_pbp.findall(page))>0:
					ot1_start_page=game_text.index(page)
				if len(find_end_2ndot_pbp.findall(page))>0:
					ot2_end_page=game_text.index(page)
				if len(find_2ndot_pbp.findall(page))>0:
					ot2_start_page=game_text.index(page)
				if len(find_end_3rdot_pbp.findall(page))>0:
					ot3_end_page=game_text.index(page)
				if len(find_3rdot_pbp.findall(page))>0:
					ot3_start_page=game_text.index(page)
			pbp_player_finder=re.compile("%s Starters: (Mbah a Moute|Marc Morris|Mark Morris|Marc. Morris|Mark. Morris|De Colo|World Peace|Lucas III|[a-zA-Z\-']{1,20} Jr.|[a-zA-Z\-']{1,20}|[A-Za-z']{1,4}\. [a-zA-Z\-']{1,20})  (Mbah a Moute|Marc Morris|Mark Morris|Marc. Morris|Mark. Morris|De Colo|World Peace|Lucas III|[a-zA-Z\-']{1,20} Jr.|[a-zA-Z\-']{1,20}|[A-Za-z']{1,4}\. [a-zA-Z\-']{1,20})  (Mbah a Moute|Marc Morris|Mark Morris|Marc. Morris|Mark. Morris|De Colo|World Peace|Lucas III|[a-zA-Z\-']{1,20} Jr.|[a-zA-Z\-']{1,20}|[A-Za-z']{1,4}\. [a-zA-Z\-']{1,20})  (Mbah a Moute|Marc Morris|Mark Morris|Marc. Morris|Mark. Morris|De Colo|World Peace|Lucas III|[a-zA-Z\-']{1,20} Jr.|[a-zA-Z\-']{1,20}|[A-Za-z']{1,4}\. [a-zA-Z\-']{1,20})  (Mbah a Moute|Marc Morris|Mark Morris|Marc. Morris|Mark. Morris|De Colo|World Peace|Lucas III|[a-zA-Z\-']{1,20} Jr.|[a-zA-Z\-']{1,20}|[A-Za-z']{1,4}\. [a-zA-Z\-']{1,20})%s Starters: (Mbah a Moute|Marc Morris|Mark Morris|Marc. Morris|Mark. Morris|De Colo|World Peace|Lucas III|[a-zA-Z\-']{1,20} Jr.|[a-zA-Z\-']{1,20}|[A-Za-z']{1,4}\. [a-zA-Z\-']{1,20})  (Mbah a Moute|Marc Morris|Mark Morris|Marc. Morris|Mark. Morris|De Colo|World Peace|Lucas III|[a-zA-Z\-']{1,20} Jr.|[a-zA-Z\-']{1,20}|[A-Za-z']{1,4}\. [a-zA-Z\-']{1,20})  (Mbah a Moute|Marc Morris|Mark Morris|Marc. Morris|Mark. Morris|De Colo|World Peace|Lucas III|[a-zA-Z\-']{1,20} Jr.|[a-zA-Z\-']{1,20}|[A-Za-z']{1,4}\. [a-zA-Z\-']{1,20})  (Mbah a Moute|Marc Morris|Mark Morris|Marc. Morris|Mark. Morris|De Colo|World Peace|Lucas III|[a-zA-Z\-']{1,20} Jr.|[a-zA-Z\-']{1,20}|[A-Za-z']{1,4}\. [a-zA-Z\-']{1,20})  (Mbah a Moute|Marc Morris|Mark Morris|Marc. Morris|Mark. Morris|De Colo|World Peace|Lucas III|[a-zA-Z\-']{1,20} Jr.|[a-zA-Z\-']{1,20}|[A-Za-z']{1,4}\. [a-zA-Z\-']{1,20})Time" % (teams[0][1],teams[0][0]))
			q1_home_pbp_starters=pbp_player_finder.findall(game_text[first_pbp_page])[0][0:5]
			q1_away_pbp_starters=pbp_player_finder.findall(game_text[first_pbp_page])[0][5:]
			q2_home_pbp_starters=pbp_player_finder.findall(game_text[second_pbp_page])[0][0:5]
			q2_away_pbp_starters=pbp_player_finder.findall(game_text[second_pbp_page])[0][5:]
			q3_home_pbp_starters=pbp_player_finder.findall(game_text[third_pbp_page])[0][0:5]
			q3_away_pbp_starters=pbp_player_finder.findall(game_text[third_pbp_page])[0][5:]
			q4_home_pbp_starters=pbp_player_finder.findall(game_text[fourth_pbp_page])[0][0:5]
			q4_away_pbp_starters=pbp_player_finder.findall(game_text[fourth_pbp_page])[0][5:]
			try:
				ot1_home_pbp_starters=pbp_player_finder.findall(game_text[ot1_start_page])[0][0:5]
				ot1_away_pbp_starters=pbp_player_finder.findall(game_text[ot1_start_page])[0][5:]
			except:
				ot1_home_pbp_starters=[]
				ot1_away_pbp_starters=[]
			try:
				ot2_home_pbp_starters=pbp_player_finder.findall(game_text[ot2_start_page])[0][0:5]
				ot2_away_pbp_starters=pbp_player_finder.findall(game_text[ot2_start_page])[0][5:]
			except:
				ot2_home_pbp_starters=[]
				ot2_away_pbp_starters=[]
			try:
				ot3_home_pbp_starters=pbp_player_finder.findall(game_text[ot3_start_page])[0][0:5]
				ot3_away_pbp_starters=pbp_player_finder.findall(game_text[ot3_start_page])[0][5:]
			except:
				ot3_home_pbp_starters=[]
				ot3_away_pbp_starters=[]
			sub_url='http://stats.nba.com/stats/playbyplay?GameID=%s&StartPeriod=0&EndPeriod=0' % (gamebook[9:19])
			subs=urllib2.urlopen(sub_url)
			subs=json.load(subs)
			sub_finder=re.compile("([0-9]{2}:[0-9]{2}|:[0-9]{2}\.[0-9])   SUB: (Mbah a Moute|Marc Morris|Mark Morris|Marc. Morris|Mark. Morris|De Colo|World Peace|Lucas III|[a-zA-Z\-']{1,20} Jr.|[a-zA-Z\-']{1,20}|[A-Za-z']{1,5}\. [a-zA-Z\-']{1,20}) FOR (Mbah a Moute|Marc Morris|Mark Morris|Marc. Morris|Mark. Morris|De Colo|World Peace|Lucas III|[A-Za-z']{1,4}\. [a-zA-Z\-']{1,30}|[a-zA-Z\-']{1,20} Jr.|[a-zA-Z\-']{1,30})")
			home_subs=[]
			away_subs=[]
			for play in subs['resultSets'][0]['rowSet']:
				if play[7] is not None:
					if play[7][0:3]=='SUB':
						sub_pattern=play[7].replace('SUB:','')
						sub_pattern=sub_pattern.split(' FOR ')
						sub_pattern=[sub_pattern[0].strip(),sub_pattern[1].strip()]
						sub_pattern=[play[1],sub_pattern[0],sub_pattern[1],play[4]]
						home_subs.append(sub_pattern)
				if play[9] is not None:
					if play[9][0:3]=='SUB':
						sub_pattern=play[9].replace('SUB:','')
						sub_pattern=sub_pattern.split(' FOR ')
						sub_pattern=[sub_pattern[0].strip(),sub_pattern[1].strip()]
						sub_pattern=[play[1],sub_pattern[0],sub_pattern[1],play[4]]
						away_subs.append(sub_pattern)
			# q1_subs2=[sub_finder.findall(page) for page in game_text[first_pbp_page:second_pbp_page]]
			# q2_subs2=[sub_finder.findall(page) for page in game_text[second_pbp_page:third_pbp_page]]
			# q3_subs2=[sub_finder.findall(page) for page in game_text[third_pbp_page:fourth_pbp_page]]
			# q4_subs2=[sub_finder.findall(page) for page in game_text[fourth_pbp_page:fourth_end_page+1]]
			# q1_subs=[]
			# q2_subs=[]
			# q3_subs=[]
			# q4_subs=[]
			# for sub_list in q1_subs2:
			# 	for sub in sub_list:
			# 		q1_subs.append(sub)
			# for sub_list in q2_subs2:
			# 	for sub in sub_list:
			# 		q2_subs.append(sub)
			# for sub_list in q3_subs2:
			# 	for sub in sub_list:
			# 		q3_subs.append(sub)
			# for sub_list in q4_subs2:
			# 	for sub in sub_list:
			# 		q4_subs.append(sub)
			# q1_subs3=[]
			# q2_subs3=[]
			# q3_subs3=[]
			# q4_subs3=[]
			# for sub in q1_subs:
			# 	if sub[0][0]==':':
			# 		q1_subs3.append((0,int(sub[0][1:3]),sub[1],sub[2].replace('Copyright','')))
			# 	if sub[0][0]!=':':
			# 		q1_subs3.append((int(sub[0][0:2]),int(sub[0][3:5]),sub[1],sub[2].replace('Copyright','')))
			# for sub in q2_subs:
			# 	if sub[0][0]==':':
			# 		q2_subs3.append((0,int(sub[0][1:3]),sub[1],sub[2].replace('Copyright','')))
			# 	if sub[0][0]!=':':
			# 		q2_subs3.append((int(sub[0][0:2]),int(sub[0][3:5]),sub[1],sub[2].replace('Copyright','')))
			# for sub in q3_subs:
			# 	if sub[0][0]==':':
			# 		q3_subs3.append((0,int(sub[0][1:3]),sub[1],sub[2].replace('Copyright','')))
			# 	if sub[0][0]!=':':
			# 		q3_subs3.append((int(sub[0][0:2]),int(sub[0][3:5]),sub[1],sub[2].replace('Copyright','')))
			# for sub in q4_subs:
			# 	if sub[0][0]==':':
			# 		q4_subs3.append((0,int(sub[0][1:3]),sub[1],sub[2].replace('Copyright','')))
			# 	if sub[0][0]!=':':
			# 		q4_subs3.append((int(sub[0][0:2]),int(sub[0][3:5]),sub[1],sub[2].replace('Copyright','')))
			# q1_subs=q1_subs3
			# q2_subs=q2_subs3
			# q3_subs=q3_subs3
			# q4_subs=q4_subs3
			home_names=[]
			away_names=[]
			name_list_home=list(q1_home_pbp_starters)+list(q2_home_pbp_starters)+list(q3_home_pbp_starters)+list(q4_home_pbp_starters)+list(ot1_home_pbp_starters)+list(ot2_home_pbp_starters)+list(ot3_home_pbp_starters)
			name_list_away=list(q1_away_pbp_starters)+list(q2_away_pbp_starters)+list(q3_away_pbp_starters)+list(q4_away_pbp_starters)+list(ot1_away_pbp_starters)+list(ot2_away_pbp_starters)+list(ot3_away_pbp_starters)
			for name in name_list_home:
				home_names.append(name)
			for sub_pattern in home_subs:
				home_names.append(sub_pattern[1])
				home_names.append(sub_pattern[2])
			for name in name_list_away:
				away_names.append(name)
			for sub_pattern in away_subs:
				away_names.append(sub_pattern[1])
				away_names.append(sub_pattern[2])
			home_names=[name for name in set(home_names)]
			away_names=[name for name in set(away_names)]
			if diagnostics==1:
				print 'names diagnostic'
				print "HOME_NAMES,"
				print home_names
				print "AWAY_NAMES,"
				print away_names
				print "HOME_SUBS,"
				print home_subs
				print "AWAY_SUBS,"
				print away_subs
				print "HOME,"
				print home
				print "AWAY,"
				print away
			matched_home_names=match_names(home_names,home,diagnostics)
			matched_away_names=match_names(away_names,away,diagnostics)
			if diagnostics==1:
				print "Matched home names,"
				print matched_home_names
				print "Matched away names"
				print matched_away_names
			nba_call_url='http://stats.nba.com/stats/shotchartdetail?Season=2013-14&SeasonType=Regular%%20Season&TeamID=0&PlayerID=0&GameID=%s&Outcome=&Location=&Month=0&SeasonSegment=&DateFrom=&Dateto=&OpponentTeamID=0&VsConference=&VsDivision=&Position=&RookieYear=&GameSegment=&Period=0&LastNGames=0&ContextMeasure=FGA' % (gamebook[9:19])
			plays=urllib2.urlopen(nba_call_url)
			data=json.load(plays)
			# SHOT LOOP STARTS HERE
			# SHOT LOOP STARTS HERE
			holder=[]
			for shot in  data['resultSets'][0]['rowSet']:
				dists={}
				if shot[4] in matched_home_names.keys() or shot[4] in matched_away_names.keys():
					shot_name=shot[4]
				else:
					for key in matched_home_names.keys():
						dist=nltk.metrics.edit_distance(key,shot[4])
						dists[dist]=key
					for key in matched_away_names.keys():
						dist=nltk.metrics.edit_distance(key,shot[4])
						dists[dist]=key
					min1=min(dists)
					shot_name=dists[min1]
				# Reminder that the structure of the data is:
				# p_name, p_number, off_team, def_team, quarter, minutes_left, seconds_left,
				# event_type, action_type, shot_distance, x_loc, y_loc, shot_made, 3pt_flag,
				# off_p1, off_p2, off_p3, off_p4, off_p5, def_p1, def_p2, def_p3, def_p4, 
				# def_p5, gamebook, season, year, month, day
				temprow=[]
				# Player name, index 0
				temprow.append(shot_name)
				# Game ID, index 1
				temprow.append(shot[1])
				# Offense team, index 2
				if shot_name in matched_home_names.keys():
					temprow.append(home_team)
					temprow.append(away_team)
				# Defense team, index 3
				if shot_name in matched_away_names.keys():
					temprow.append(away_team)
					temprow.append(home_team)
				# Period, index 4
				temprow.append(shot[7])
				# Minutes remaining, index 5
				temprow.append(shot[8])
				# Seconds remaining, index 6
				temprow.append(shot[9])
				# Action type, index 7
				temprow.append(shot[11])
				# Shot type, index 8
				temprow.append(shot[12])
				# distance, index 9
				temprow.append(shot[16])
				# x_loc, index 10
				temprow.append(shot[17])
				# y_loc, index 11
				temprow.append(shot[18])
				# Shot made dummy, index 12
				temprow.append(shot[20])
				# 3pt dummy, index 13
				if shot[12]=="3PT Field Goal":
					temprow.append(1)
				if shot[12]!="3PT Field Goal":
					temprow.append(0)
				if shot[7]==1:
					current_home_starters=q1_home_pbp_starters
					current_away_starters=q1_away_pbp_starters
				if shot[7]==2:
					current_home_starters=q2_home_pbp_starters
					current_away_starters=q2_away_pbp_starters
				if shot[7]==3:
					current_home_starters=q3_home_pbp_starters
					current_away_starters=q3_away_pbp_starters
				if shot[7]==4:
					current_home_starters=q4_home_pbp_starters
					current_away_starters=q4_away_pbp_starters
				if shot[7]==5:
					current_home_starters=ot1_home_pbp_starters
					current_away_starters=ot1_away_pbp_starters
				if shot[7]==6:
					current_home_starters=ot2_home_pbp_starters
					current_away_starters=ot2_away_pbp_starters
				if shot[7]==7:
					current_home_starters=ot3_home_pbp_starters
					current_away_starters=ot3_away_pbp_starters
				#if diagnostics==1:
				#	print "STARTERS"
				#	print "STARTERS"
				#	print q1_home_pbp_starters
				#	print q2_home_pbp_starters
				#	print q3_home_pbp_starters
				#	print q4_home_pbp_starters
				home_players=current_players(current_home_starters,matched_home_names,home_subs,shot[2],shot[7],diagnostics)
				away_players=current_players(current_away_starters,matched_away_names,away_subs,shot[2],shot[7],diagnostics)
				# offensive players, 14:18
				if shot_name in matched_home_names.keys():
					if get_full_name(matched_home_names,home_players[0])=="" or get_full_name(matched_home_names,home_players[1])=="" or get_full_name(matched_home_names,home_players[2])=="" or get_full_name(matched_home_names,home_players[3])=="" or get_full_name(matched_home_names,home_players[4])=="":
						print "BLANK NAME"
						print shot_name
						print home_players
						print matched_home_names
					temprow.append(get_full_name(matched_home_names,home_players[0]))
					temprow.append(get_full_name(matched_home_names,home_players[1]))
					temprow.append(get_full_name(matched_home_names,home_players[2]))
					temprow.append(get_full_name(matched_home_names,home_players[3]))
					temprow.append(get_full_name(matched_home_names,home_players[4]))
					temprow.append(get_full_name(matched_away_names,away_players[0]))
					temprow.append(get_full_name(matched_away_names,away_players[1]))
					temprow.append(get_full_name(matched_away_names,away_players[2]))
					temprow.append(get_full_name(matched_away_names,away_players[3]))
					temprow.append(get_full_name(matched_away_names,away_players[4]))
				# defensive players, 19:23
				if shot_name in matched_away_names.keys():
					temprow.append(get_full_name(matched_away_names,away_players[0]))
					temprow.append(get_full_name(matched_away_names,away_players[1]))
					temprow.append(get_full_name(matched_away_names,away_players[2]))
					temprow.append(get_full_name(matched_away_names,away_players[3]))
					temprow.append(get_full_name(matched_away_names,away_players[4]))
					temprow.append(get_full_name(matched_home_names,home_players[0]))
					temprow.append(get_full_name(matched_home_names,home_players[1]))
					temprow.append(get_full_name(matched_home_names,home_players[2]))
					temprow.append(get_full_name(matched_home_names,home_players[3]))
					temprow.append(get_full_name(matched_home_names,home_players[4]))
				temprow.append(gamebook[9:19])
				temprow.append('2013-2014')
				temprow.append(date.year)
				temprow.append(date.month)
				temprow.append(date.day)
				if diagnostics==1:
					if len(temprow)!=29:
						print temprow
						print shot
				if len(temprow)!=29:
					print 'investigate %s, temprow is wrong length' % (gamebook)
					print 'temprow length is %s' % (len(temprow))
					print temprow
					print shot
					print matched_home_names
					print matched_away_names
					sys.exit()
				holder.append(temprow)
			with open('/Users/austinc/Desktop/Current Work/NBA/shot_data.csv','a') as csvfile:
				writer=csv.writer(csvfile)
				for row in holder:
					writer.writerow(row)
			if diagnostics==0:
				with open('%sprocessed.txt' % (direct),'a') as tempfile:
					tempfile.write("%s\n" % (gamebook))
				os.rename('%s%s' % (direct,gamebook),'/Users/austinc/Desktop/Current Work/NBA/processed_gamebooks/%s' % (gamebook))

def scraper():
	for year in range(2002,2014,1):
		scrape_shots(year)


def scrape_shots(year):
	"""Scrape shot data for every year, every game and stick in csvs"""
	y2=int(str(year)[2:])
	y3=y2+1
	if y2==99:
		y3=0
	season=str(year)+"-"+str("%02d" % (y3,))
	for gameid in range(1,1231,1):
		game="002"+"%02d" % (y2,)+"%05d" % (gameid,)
		nba_call_url='http://stats.nba.com/stats/shotchartdetail?Season=%s&SeasonType=Regular%%20Season&TeamID=0&PlayerID=0&GameID=%s&Outcome=&Location=&Month=0&SeasonSegment=&DateFrom=&Dateto=&OpponentTeamID=0&VsConference=&VsDivision=&Position=&RookieYear=&GameSegment=&Period=0&LastNGames=0&ContextMeasure=FGA' % (season,game)
		print nba_call_url
		plays=urllib2.urlopen(nba_call_url)
		data=json.load(plays)
		with open('/Users/austinc/Desktop/Current Work/NBA/%s_shot_data.csv' % (year),'a') as csvfile:
			writer=csv.writer(csvfile)
			for row in data['resultSets'][0]['rowSet']:
				writer.writerow(row)


def scrape_shots_all():
	"""Scrape shot data for every year, every game and stick in csvs"""
	with open('/Users/austinc/Desktop/all_shot_data.csv','rU') as csvfile:
		reader=csv.reader(csvfile)
		data1=[row for row in reader]
	games=[]
	for row in data1:
		games.append(row[0])
	for year in range(2014,2015,1):
		all_shots=[]
		print year
		y2=int(str(year)[2:])
		y3=y2+1
		if y2==99:
			y3=0
		season=str(year)+"-"+str("%02d" % (y3,))
		for gameid in range(1,1250,1):
			if gameid not in games:
				game="002"+"%02d" % (y2,)+"%05d" % (gameid,)
				if game not in games:
					nba_call_url='http://stats.nba.com/stats/shotchartdetail?Season=%s&SeasonType=Regular%%20Season&TeamID=0&PlayerID=0&GameID=%s&Outcome=&Location=&Month=0&SeasonSegment=&DateFrom=&Dateto=&OpponentTeamID=0&VsConference=&VsDivision=&Position=&RookieYear=&GameSegment=&Period=0&LastNGames=0&ContextMeasure=FGA' % (season,game)
					#nba_box_url='http://stats.nba.com/stats/boxscore?StartPeriod=0&EndPeriod=0&StartRange=0&EndRange=0&RangeType=0&GameID=%s' % (game)
					print game
					plays=urllib2.urlopen(nba_call_url)
					#box=urllib2.urlopen(nba_box_url)
					try:
						data=json.load(plays)
					except:
						print 'DATA DID NOT LOAD'
						data=json.load({"resource":"shotchartdetail","parameters":{"LeagueID":null,"Season":"1996-97","SeasonType":"Regular Season","TeamID":0,"PlayerID":0,"GameID":"0029601987","Outcome":null,"Location":null,"Month":0,"SeasonSegment":null,"DateFrom":null,"DateTo":null,"OpponentTeamID":0,"VsConference":null,"VsDivision":null,"Position":null,"RookieYear":null,"GameSegment":null,"Period":0,"LastNGames":0,"ClutchTime":null,"AheadBehind":null,"PointDiff":null,"RangeType":null,"StartPeriod":null,"EndPeriod":null,"StartRange":null,"EndRange":null,"ContextFilter":"","ContextMeasure":"FGA"},"resultSets":[{"name":"Shot_Chart_Detail","headers":["GRID_TYPE","GAME_ID","GAME_EVENT_ID","PLAYER_ID","PLAYER_NAME","TEAM_ID","TEAM_NAME","PERIOD","MINUTES_REMAINING","SECONDS_REMAINING","EVENT_TYPE","ACTION_TYPE","SHOT_TYPE","SHOT_ZONE_BASIC","SHOT_ZONE_AREA","SHOT_ZONE_RANGE","SHOT_DISTANCE","LOC_X","LOC_Y","SHOT_ATTEMPTED_FLAG","SHOT_MADE_FLAG"],"rowSet":[]},{"name":"LeagueAverages","headers":["GRID_TYPE","SHOT_ZONE_BASIC","SHOT_ZONE_AREA","SHOT_ZONE_RANGE","FGA","FGM","FG_PCT"],"rowSet":[["League Averages","Above the Break 3","Back Court(BC)","Back Court Shot",85,2,0.024],["League Averages","Above the Break 3","Center(C)","24+ ft.",2961,1004,0.339],["League Averages","Above the Break 3","Left Side Center(LC)","24+ ft.",6391,2096,0.328],["League Averages","Above the Break 3","Right Side Center(RC)","24+ ft.",4938,1713,0.347],["League Averages","Backcourt","Back Court(BC)","Back Court Shot",207,9,0.043],["League Averages","In The Paint (Non-RA)","Center(C)","8-16 ft.",4311,1896,0.44],["League Averages","In The Paint (Non-RA)","Center(C)","Less Than 8 ft.",14430,6313,0.437],["League Averages","In The Paint (Non-RA)","Left Side(L)","8-16 ft.",1893,781,0.413],["League Averages","In The Paint (Non-RA)","Right Side(R)","8-16 ft.",1741,714,0.41],["League Averages","Left Corner 3","Left Side(L)","24+ ft.",3068,1214,0.396],["League Averages","Mid-Range","Center(C)","16-24 ft.",7169,2906,0.405],["League Averages","Mid-Range","Center(C)","8-16 ft.",1668,710,0.426],["League Averages","Mid-Range","Left Side Center(LC)","16-24 ft.",9900,4050,0.409],["League Averages","Mid-Range","Left Side(L)","16-24 ft.",9842,4158,0.422],["League Averages","Mid-Range","Left Side(L)","8-16 ft.",13794,5376,0.39],["League Averages","Mid-Range","Right Side Center(RC)","16-24 ft.",11226,4357,0.388],["League Averages","Mid-Range","Right Side(R)","16-24 ft.",9029,3715,0.411],["League Averages","Mid-Range","Right Side(R)","8-16 ft.",12668,5036,0.398],["League Averages","Restricted Area","Center(C)","Less Than 8 ft.",70575,38643,0.548],["League Averages","Right Corner 3","Right Side(R)","24+ ft.",2689,1079,0.401]]}]})
					#boxscore=json.load(box)
					#month=boxscore['resultSets'][0]['rowSet'][0][5][4:6]
					#day=boxscore['resultSets'][0]['rowSet'][0][5][6:8]
					teams=list(set([row[6] for row in data['resultSets'][0]['rowSet']]))
					for row in data['resultSets'][0]['rowSet']:
						# (gameid, player, offense team, defense team, 3pt, made, year, regular/post (0/1), quarter, second remaining, x, y, month, day)
						three=0
						if row[12]=='3PT Field Goal':
							three=1
						if row[6]==teams[0]:
							temp=[game,row[4],teams[0],teams[1],three,row[20],year,0,row[7],row[8]*60+row[9],row[17],row[18]]
						if row[6]==teams[1]:
							temp=[game,row[4],teams[1],teams[0],three,row[20],year,0,row[7],row[8]*60+row[9],row[17],row[18]]
						all_shots.append(temp)
		for gameid in range(1,407,1):
			if gameid not in games:
				game="004"+"%02d" % (y2,)+"%05d" % (gameid,)
				if game not in games:
					nba_call_url='http://stats.nba.com/stats/shotchartdetail?Season=%s&SeasonType=Playoffs&TeamID=0&PlayerID=0&GameID=%s&Outcome=&Location=&Month=0&SeasonSegment=&DateFrom=&Dateto=&OpponentTeamID=0&VsConference=&VsDivision=&Position=&RookieYear=&GameSegment=&Period=0&LastNGames=0&ContextMeasure=FGA' % (season,game)
					#nba_box_url='http://stats.nba.com/stats/boxscore?StartPeriod=0&EndPeriod=0&StartRange=0&EndRange=0&RangeType=0&GameID=%s' % (game)
					print game
					plays=urllib2.urlopen(nba_call_url)
					#box=urllib2.urlopen(nba_box_url)
					try:
						data=json.load(plays)
					except:
						print 'DATA DID NOT LOAD'
						data=json.load({"resource":"shotchartdetail","parameters":{"LeagueID":null,"Season":"1996-97","SeasonType":"Regular Season","TeamID":0,"PlayerID":0,"GameID":"0029601987","Outcome":null,"Location":null,"Month":0,"SeasonSegment":null,"DateFrom":null,"DateTo":null,"OpponentTeamID":0,"VsConference":null,"VsDivision":null,"Position":null,"RookieYear":null,"GameSegment":null,"Period":0,"LastNGames":0,"ClutchTime":null,"AheadBehind":null,"PointDiff":null,"RangeType":null,"StartPeriod":null,"EndPeriod":null,"StartRange":null,"EndRange":null,"ContextFilter":"","ContextMeasure":"FGA"},"resultSets":[{"name":"Shot_Chart_Detail","headers":["GRID_TYPE","GAME_ID","GAME_EVENT_ID","PLAYER_ID","PLAYER_NAME","TEAM_ID","TEAM_NAME","PERIOD","MINUTES_REMAINING","SECONDS_REMAINING","EVENT_TYPE","ACTION_TYPE","SHOT_TYPE","SHOT_ZONE_BASIC","SHOT_ZONE_AREA","SHOT_ZONE_RANGE","SHOT_DISTANCE","LOC_X","LOC_Y","SHOT_ATTEMPTED_FLAG","SHOT_MADE_FLAG"],"rowSet":[]},{"name":"LeagueAverages","headers":["GRID_TYPE","SHOT_ZONE_BASIC","SHOT_ZONE_AREA","SHOT_ZONE_RANGE","FGA","FGM","FG_PCT"],"rowSet":[["League Averages","Above the Break 3","Back Court(BC)","Back Court Shot",85,2,0.024],["League Averages","Above the Break 3","Center(C)","24+ ft.",2961,1004,0.339],["League Averages","Above the Break 3","Left Side Center(LC)","24+ ft.",6391,2096,0.328],["League Averages","Above the Break 3","Right Side Center(RC)","24+ ft.",4938,1713,0.347],["League Averages","Backcourt","Back Court(BC)","Back Court Shot",207,9,0.043],["League Averages","In The Paint (Non-RA)","Center(C)","8-16 ft.",4311,1896,0.44],["League Averages","In The Paint (Non-RA)","Center(C)","Less Than 8 ft.",14430,6313,0.437],["League Averages","In The Paint (Non-RA)","Left Side(L)","8-16 ft.",1893,781,0.413],["League Averages","In The Paint (Non-RA)","Right Side(R)","8-16 ft.",1741,714,0.41],["League Averages","Left Corner 3","Left Side(L)","24+ ft.",3068,1214,0.396],["League Averages","Mid-Range","Center(C)","16-24 ft.",7169,2906,0.405],["League Averages","Mid-Range","Center(C)","8-16 ft.",1668,710,0.426],["League Averages","Mid-Range","Left Side Center(LC)","16-24 ft.",9900,4050,0.409],["League Averages","Mid-Range","Left Side(L)","16-24 ft.",9842,4158,0.422],["League Averages","Mid-Range","Left Side(L)","8-16 ft.",13794,5376,0.39],["League Averages","Mid-Range","Right Side Center(RC)","16-24 ft.",11226,4357,0.388],["League Averages","Mid-Range","Right Side(R)","16-24 ft.",9029,3715,0.411],["League Averages","Mid-Range","Right Side(R)","8-16 ft.",12668,5036,0.398],["League Averages","Restricted Area","Center(C)","Less Than 8 ft.",70575,38643,0.548],["League Averages","Right Corner 3","Right Side(R)","24+ ft.",2689,1079,0.401]]}]})
					#boxscore=json.load(box)
					#month=boxscore['resultSets'][0]['rowSet'][0][5][4:6]
					#day=boxscore['resultSets'][0]['rowSet'][0][5][6:8]
					teams=list(set([row[6] for row in data['resultSets'][0]['rowSet']]))
					for row in data['resultSets'][0]['rowSet']:
						# (gameid, player, offense team, defense team, 3pt, made, year, regular/post (0/1), quarter, second remaining, x, y)
						three=0
						if row[12]=='3PT Field Goal':
							three=1
						if row[6]==teams[0]:
							temp=[game,row[4],teams[0],teams[1],three,row[20],year,1,row[7],row[8]*60+row[9],row[17],row[18]]
						if row[6]==teams[1]:
							temp=[game,row[4],teams[1],teams[0],three,row[20],year,1,row[7],row[8]*60+row[9],row[17],row[18]]
						all_shots.append(temp)
		with open('/Users/austinc/Desktop/all_shot_data.csv','a') as csvfile:
			writer=csv.writer(csvfile)
			for row in all_shots:
				writer.writerow(row)


def scraper_dleague():
	for year in range(2003,2014,1):
		dleague_scrape_shots(year)

def dleague_scrape_shots(year):
	"""Scrape shot data for every year, every game and stick in csvs"""
	y2=int(str(year)[2:])
	y3=y2+1
	if y2==99:
		y3=0
	season=str(year)+"-"+str("%02d" % (y3,))
	for gameid in range(1,1231,1):
		game="202"+"%02d" % (y2,)+"%05d" % (gameid,)
		nba_call_url='http://stats.nbadleague.com/stats/shotchartdetail?Season=%s&LeagueID=20&SeasonType=Regular%%20Season&TeamID=0&PlayerID=0&GameID=%s&Outcome=&Location=&Month=0&SeasonSegment=&DateFrom=&Dateto=&OpponentTeamID=0&VsConference=&VsDivision=&Position=&RookieYear=&GameSegment=&Period=0&LastNGames=0&ContextMeasure=FGA' % (season,game)
		print nba_call_url
		plays=urllib2.urlopen(nba_call_url)
		data=json.load(plays)
		with open('/Users/austinc/Desktop/Current Work/NBA/%s_dleague_shot_data.csv' % (year),'a') as csvfile:
			writer=csv.writer(csvfile)
			for row in data['resultSets'][0]['rowSet']:
				writer.writerow(row)


def match_names(short_names,long_names,diagnostics):
	"""This function matches the abbreviated names used in NBA.com gamebooks to the longer
	names used in box scores and the NBA.com API, which will be used to retrieve shot data.
	It returns a nested dictionary. The first level is the names of the teams. The second
	layer is the long name of a player and the corresponding abbreviated name."""
	roster_dic={}
	shorter=[]
	if diagnostics==1:
		print "SHORT_NAMES"
		print short_names
	for long_n in long_names:
		distances=[]
		temp=[]
		for short_n in short_names:
			if short_n.split(" ")[-1] in long_n[-len(short_n):]:
				temp.append(short_n)
		if len(temp)==0 or len(temp)>1:
			if len(temp)>1:
				dists=[]
				for short_n in temp:
					dists.append(float(nltk.metrics.edit_distance(long_n,short_n))/len(long_n))
				mini=min(dists)
				roster_dic[long_n]=temp[dists.index(mini)]
				if diagnostics==1:
					print short_names[dists.index(mini)]
			if len(temp)==0:
				dists=[]
				for short_n in short_names:
					dists.append(float(nltk.metrics.edit_distance(long_n,short_n))/len(long_n))
				mini=min(dists)
				roster_dic[long_n]=short_names[dists.index(mini)]
		if len(temp)==1:
			roster_dic[long_n]=temp[0]
	return roster_dic



def current_players(starters,matched_names,subs,event_id,period,diagnostics):
	"""This function determines who the current players are on both sides of the court using
	the sub lists. It returns a single list of two lists. Each list gives one team's players
	at the given timestamp. The teams are not in order - they get oriented back in the process
	gamebooks function."""
	if diagnostics==1:
		print "EVENT_ID"
		print event_id
	players=list(starters)
	subs=[pattern for pattern in subs if int(pattern[3])==int(period)]
	subs=[pattern for pattern in subs if int(pattern[0])<int(event_id)]
	if diagnostics==1:
		print starters
		print subs
	for pattern in subs:
		sub_in=pattern[1]
		sub_out=pattern[2]
		if sub_out in players:
			players[players.index(sub_out)]=sub_in
			if diagnostics==1:
				print players
		else:
			dists=[]
			for name in players:
				dists.append(nltk.metrics.edit_distance(sub_out,name)/len(sub_out))
			mini=min(dists)
			sub_out=players[dists.index(mini)]
			if diagnostics==1:
				print sub_out
				print dists
			temp=[]
			for key in matched_names.keys():
				temp.append(matched_names[key])
			dists=[]
			for name in temp:
				dists.append(nltk.metrics.edit_distance(sub_out,name)/len(sub_out))
			mini=min(dists)
			temp.pop(dists.index(mini))
			dists=[]
			for player in temp:
				dists.append(nltk.metrics.edit_distance(sub_in,player)/len(sub_in))
			mini=min(dists)
			sub_in=temp[dists.index(mini)]
			players[players.index(sub_out)]=sub_in
	return players



def create_shot_csv(player_name,team,type,defense_flag,yearstart=0,monthstart=0,daystart=0,yearend=0,monthend=0,dayend=0,season='2013-2014',smooth=0):
	"""Creates various kinds of csv shot chart files. Player name needs to match that provided in 
	NBA gamebooks exactly. Team needs to match gamebooks too. If type is 0, returns stats for when 
	the player is in the game. If type is 1, returns stats for when the player is not in the game. 
	If type is 2, returns in vs out differentials. If type is 3, returns stats when player is in 
	game vs average. If defense_flag is 0, returns player's own offensive stats. If defense_flag 
	is 1, returns defensive stats. If defense_flag is 2, returns player's team's offensive stats. 
	All the datestarts and dateends let you specify a date range you want to work with, mostly for 
	players who change teams. This isn't really working right now though so I suggest sticking to
	season. Specify it as "2013-2014" or likewise."""
	with open("/Users/austinc/Desktop/Current Work/NBA/shot_data.csv",'rU') as csvfile:
		reader=csv.reader(csvfile)
		shots=[row for row in reader]
	shots=[shot for shot in shots if shot[25]==season]
	print shots[0:5]
	if type==-1:
		# league-wide debugging
		shots_temp=[[shot[0],int(shot[11]),int(shot[10]),int(shot[12]),int(shot[13])] for shot in shots]
		csv_data=circle_chunk(shots_temp,smooth=smooth)
	if type==0:
		# return stats for when players is in the game
		if defense_flag==0:
			# returns player's own offensive stats
			shots_temp=[shot for shot in shots if shot[0]==player_name]
			shots_temp=[[shot[0],shot[10],shot[11],shot[12]] for shot in shots_temp]
			# columns are: name,x_loc,y_loc,shot_made
			csv_data=chunk(shots_temp)
		if defense_flag==1:
			# returns player's defensive stats
			shots_temp=[shot for shot in shots if shot[3].lower()==team.lower()]
			shots_temp=[shot for shot in shots if player_name in shot[19:24]]
			shots_temp=[[player_name,int(shot[11]),int(shot[10]),int(shot[12]),int(shot[13])] for shot in shots_temp]
			print len(shots_temp)
			print shots_temp[:5]
			csv_data=circle_chunk(shots_temp,smooth=smooth)
		if defense_flag==2:
			# returns player's team's offensive stats (not including player himself)
			shots_temp=[shot for shot in shots if shot[2].lower()==team.lower()]
			shots_temp=[shot for shot in shots_temp if player_name in shot[14:19]]
			shots_temp=[shot for shot in shots_temp if shot[0]!=player_name]
			shots_temp=[[player_name,shot[10],shot[11],shot[12]] for shot in shots_temp]
			csv_data=chunk(shots_temp)
	if type==1:
		# return stats for when player is not in the game
		if defense_flag==0:
			shots_temp=[shot for shot in shots if shot[2].lower()==team.lower()]
			shots_temp=[shot for shot in shots_temp if player_name not in shot[14:19]]
			shots_temp=[[player_name,shot[10],shot[11],shot[12]] for shot in shots_temp]
			csv_data=chunk(shots_temp)
		if defense_flag==1:
			shots_temp=[shot for shot in shots if shot[3].lower()==team.lower()]
			shots_temp=[shot for shot in shots_temp if player_name not in shot[19:24]]
			shots_temp=[[player_name,int(shot[11]),int(shot[10]),int(shot[12]),int(shot[13])] for shot in shots_temp]
			print len(shots_temp)
			print shots_temp[:5]
			csv_data=circle_chunk(shots_temp,smooth=smooth)
		if defense_flag==2:
			print "Use type 1, defense_flag 0 to get a team's offensive production when a certain player sits."
	if type==2:
		# returns in vs out differentials
		if defense_flag==0:
			# This only sorta makes sense but what I'm going to have this one do is give on court COUNTING player vs off-court offense differentials
			shots_temp=[shot for shot in shots if shot[2].lower()==team.lower()]
			shots_in=[shot for shot in shots_temp if player_name in shot[14:19]]
			shots_out=[shot for shot in shots_temp if player_name not in shot[14:19]]
			csv_data_in=chunk(shots_in)
			csv_data_out=chunk(shots_out)
			csv_data=[]
			for index,block in enumerate(data_in):
				csv_data.append(['"%s"' % (float(csv_data_out[index][0])-float(csv_data_in[index][0])),'"%s"' % (int(csv_data_out[index][1])-int(csv_data_in[index][1]))])
		if defense_flag==1:
			# This one will compare opposing team fg% when player is in game to opposing team fg% when player is out of game
			shots_temp=[shot for shot in shots if shot[3].lower()==team.lower()]
			print shots_temp[0:5]
			shots_in=[shot for shot in shots_temp if player_name in shot[19:24]]
			shots_out=[shot for shot in shots_temp if player_name not in shot[19:24]]
			shots_in=[[player_name,int(shot[11]),int(shot[10]),int(shot[12])] for shot in shots_in]
			shots_out=[[player_name,int(shot[11]),int(shot[10]),int(shot[12])] for shot in shots_out]
			csv_data_in=circle_chunk(shots_in)
			csv_data_out=circle_chunk(shots_out)
			print csv_data_in[17]
			print csv_data_out[17]
			csv_data=compare_sig(csv_data_in,csv_data_out)
		if defense_flag==2:
			# This one will compare team fg% NOT COUNTING player when player is on court to team fg% when player is off court. 
			pass
	if type==3:
		# returns in game vs leaguewide average
		if defense_flag==0:
			# This is probably the only one I'll ever use. The Kirk Goldsberry chart, basically.
			pass
		if defense_flag==1:
			# Doesn't make a lot of sense. Opponent fg% with player in game against league wide average fg% I'll implement this later maybe.
			pass
		if defense_flag==2:
			# I guess this sorta makes sense? Team fg% not including player himself with player on court vs leaguewide average fg%. No, this is kinda dumb.  I'll implement this later.
			pass
	with open("/Users/austinc/Desktop/Current Work/NBA/%s_type_%sdefenseflag_%s.csv" % (player_name,type,defense_flag),'w') as csvfile:
		writer=csv.writer(csvfile)
		for row in csv_data:
			writer.writerow(row)


def output_averages(year):
	with open("/Users/austinc/Desktop/Current Work/NBA/%s_shot_data.csv" % (year),'rU') as csvfile:
		reader=csv.reader(csvfile)
		shots=[row for row in reader]
	for row in shots:
		if row[12]=="3PT Field Goal":
			row[12]=1
		else:
			row[12]=0
	all_shots=[['all',int(shot[18]),int(shot[17]),int(shot[20]),int(shot[12])] for shot in shots]
	made_fgs=len([shot for shot in all_shots if shot[3]==1])
	made_3s=len([shot for shot in all_shots if shot[4]==1 & shot[3]==1])
	pps=(2*made_fgs+made_3s)/len(all_shots)
	print made_fgs
	print made_3s
	print len(all_shots)
	print pps
	average_data=circle_chunk2(all_shots)
	with open("/Users/austinc/Desktop/average_%s.csv" % (year),'w') as csvfile:
		writer=csv.writer(csvfile)
		for row in average_data:
			writer.writerow(row)


def goldsberry_allyears():
	for year in range(1996,2014,1):
		print ""
		print ""
		print year
		full_goldsberry(year)

def full_goldsberry(year):
	with open("/Users/austinc/Desktop/Current Work/NBA/%s_shot_data.csv" % (year),'rU') as csvfile:
		reader=csv.reader(csvfile)
		shots=[row for row in reader]
	for row in shots:
		if row[12]=="3PT Field Goal":
			row[12]=1
		else:
			row[12]=0
	all_shots=[['all',int(shot[18]),int(shot[17]),int(shot[20]),int(shot[12])] for shot in shots]
	made_fgs=len([shot for shot in all_shots if shot[3]==1])
	made_3s=len([shot for shot in all_shots if shot[4]==1 & shot[3]==1])
	pps=(2*made_fgs+made_3s)/len(all_shots)
	print made_fgs
	print made_3s
	print len(all_shots)
	print pps
	average_data=circle_chunk2(all_shots)
	players=[]
	for shot in shots:
		players.append(shot[4])
	for player in set(players):
		print player
		goldsberry(shots,player,average_data,year,pps)

def goldsberry(shots,player,average_data,year,averagepps):
	"""Creates the Goldberry chart (csv) for given player"""
	shots_temp=[shot for shot in shots if shot[4]==player]
	shots_temp=[['',int(shot[18]),int(shot[17]),int(shot[20]),int(shot[12])] for shot in shots_temp]
	# columns are: blank (for circle_chunk,y_loc,x_loc,shot_made,3pt)
	player_data=circle_chunk2(shots_temp)
	# x_center, y_center, number of shots, number of made shots, region, player name, smoothed fg%, region fg%, relative prop of shots, region shots, region made, total_shots, pps
	csv_data=[]
	for i,region in enumerate(player_data):
		csv_data.append([region[0],region[1],region[2],float(region[3])-float(average_data[i][3]),float(region[3]),region[4],(len([shot for shot in shots_temp if math.sqrt((region[0]+5-shot[1])**2+(region[1]+5-shot[2])**2)<20]))/len(shots_temp),region[5]-averagepps,(len([shot for shot in shots_temp if math.sqrt((region[0]+5-shot[1])**2+(region[1]+5-shot[2])**2)<50]))/len(shots_temp)])
	sorted_chart=sorted(csv_data, key=itemgetter(2,6))
	sorted_chart=sorted_chart[-201:]
	sorted_chart.reverse()
	sorted_chart=[[shot[0],shot[1],shot[2],round(shot[3],4),round(shot[4],4),shot[5],round(shot[6],4),round(shot[7],4),round(shot[8],4)] for shot in sorted_chart]
	with open("/Users/austinc/Desktop/Current Work/NBA/years/goldsberry_%s/pshot_%s.csv" % (year,player),'w') as csvfile:
		writer=csv.writer(csvfile)
		for row in sorted_chart:
			writer.writerow(row)

def dleague_allyears():
	for year in range(2007,2014,1):
		print ""
		print ""
		print year
		full_dleague(year)

def full_dleague(year):
	with open("/Users/austinc/Desktop/Current Work/NBA/%s_dleague_shot_data.csv" % (year),'rU') as csvfile:
		reader=csv.reader(csvfile)
		shots=[row for row in reader]
	for row in shots:
		if row[12]=="3PT Field Goal":
			row[12]=1
		else:
			row[12]=0
	all_shots=[['all',int(shot[18]),int(shot[17]),int(shot[20]),int(shot[12])] for shot in shots]
	made_fgs=len([shot for shot in all_shots if shot[3]==1])
	made_3s=len([shot for shot in all_shots if shot[4]==1 & shot[3]==1])
	pps=(2*made_fgs+made_3s)/len(all_shots)
	print made_fgs
	print made_3s
	print len(all_shots)
	print pps
	average_data=circle_chunk2(all_shots)
	players=[]
	for shot in shots:
		players.append(shot[4])
	for player in set(players):
		print player
		dleague(shots,player,average_data,year,pps)

def dleague(shots,player,average_data,year,averagepps):
	"""Creates the Goldberry chart (csv) for given player"""
	shots_temp=[shot for shot in shots if shot[4]==player]
	shots_temp=[['',int(shot[18]),int(shot[17]),int(shot[20]),int(shot[12])] for shot in shots_temp]
	# columns are: blank (for circle_chunk,y_loc,x_loc,shot_made,3pt)
	player_data=circle_chunk2(shots_temp)
	# x_center, y_center, number of shots, number of made shots, region, player name, smoothed fg%, region fg%, relative prop of shots, region shots, region made, total_shots, pps
	csv_data=[]
	for i,region in enumerate(player_data):
		csv_data.append([region[0],region[1],region[2],float(region[3])-float(average_data[i][3]),float(region[3]),region[4],(len([shot for shot in shots_temp if math.sqrt((region[0]+5-shot[1])**2+(region[1]+5-shot[2])**2)<20]))/len(shots_temp),region[5]-averagepps,(len([shot for shot in shots_temp if math.sqrt((region[0]+5-shot[1])**2+(region[1]+5-shot[2])**2)<50]))/len(shots_temp)])
	sorted_chart=sorted(csv_data, key=itemgetter(2,6))
	sorted_chart=sorted_chart[-201:]
	sorted_chart.reverse()
	sorted_chart=[[shot[0],shot[1],shot[2],round(shot[3],4),round(shot[4],4),shot[5],round(shot[6],4),round(shot[7],4),round(shot[8],4)] for shot in sorted_chart]
	with open("/Users/austinc/Desktop/Current Work/NBA/dleague_years/%s/pshot_%s.csv" % (year,player),'w') as csvfile:
		writer=csv.writer(csvfile)
		for row in sorted_chart:
			writer.writerow(row)

def full_NCAA():
	with open("/Users/austinc/Desktop/Current Work/NBA/NCAA_2013-2014.csv",'rU') as csvfile:
		reader=csv.reader(csvfile)
		shots=[row for row in reader]
	for row in shots:
		if row[12]=="3PT Field Goal":
			row[12]=1
		else:
			row[12]=0
	all_shots=[['all',float(shot[18]),float(shot[17]),float(shot[20]),float(shot[12])] for shot in shots]
	made_fgs=len([shot for shot in all_shots if shot[3]==1])
	made_3s=len([shot for shot in all_shots if shot[4]==1 and shot[3]==1])
	pps=(2*made_fgs+made_3s)/len(all_shots)
	print made_fgs
	print made_3s
	print len(all_shots)
	print pps
	average_data=circle_chunk3(all_shots)
	players=[]
	for shot in shots:
		players.append(shot[4])
	for player in set(players):
		temp=[shot for shot in shots if shot[4]==player]
		if len(temp)>0:
			print player
			NCAA(shots,player,average_data,pps)

def NCAA(shots,player,average_data,averagepps):
	"""Creates the Goldberry chart (csv) for given player"""
	shots_temp=[shot for shot in shots if shot[4]==player]
	shots_temp=[['',float(shot[18]),float(shot[17]),float(shot[20]),float(shot[12])] for shot in shots_temp]
	# columns are: blank (for circle_chunk,y_loc,x_loc,shot_made,3pt)
	player_data=circle_chunk3(shots_temp)
	# x_center, y_center, number of shots, number of made shots, region, player name, smoothed fg%, region fg%, relative prop of shots, region shots, region made, total_shots, pps
	csv_data=[]
	for i,region in enumerate(player_data):
		csv_data.append([region[0],region[1],region[2],float(region[3])-float(average_data[i][3]),float(region[3]),region[4],(len([shot for shot in shots_temp if math.sqrt((region[0]+5-shot[1])**2+(region[1]+5-shot[2])**2)<20]))/len(shots_temp),region[5]-averagepps,(len([shot for shot in shots_temp if math.sqrt((region[0]+5-shot[1])**2+(region[1]+5-shot[2])**2)<50]))/len(shots_temp)])
	sorted_chart=sorted(csv_data, key=itemgetter(2,6))
	sorted_chart=sorted_chart[-201:]
	sorted_chart.reverse()
	sorted_chart=[[shot[0],shot[1],shot[2],round(shot[3],4),round(shot[4],4),shot[5],round(shot[6],4),round(shot[7],4),round(shot[8],4)] for shot in sorted_chart]
	with open("/Users/austinc/Desktop/Current Work/NBA/NCAA/pshot_%s.csv" % (player.replace("&nbsp;"," ")),'w') as csvfile:
		writer=csv.writer(csvfile)
		for row in sorted_chart:
			writer.writerow(row)


	
def chunk(shots_temp):
	"""Takes rows organized as: [p_name,x_loc,y_loc,shot_made] and turns them into the appropriate 
	187 row csv for visualization"""
	point_array=[[45,42],[89,42],[133,42],[177,42],[221,42],[265,42],[309,42],[353,42],[397,42],[441,42],[485,42],[529,42],[573,42],[617,42],[661,42],[705,42],[750,42],[45,84],[89,84],[133,84],[177,84],[221,84],[265,84],[309,84],[353,84],[397,84],[441,84],[485,84],[529,84],[573,84],[617,84],[661,84],[705,84],[750,84],[45,126],[89,126],[133,126],[177,126],[221,126],[265,126],[309,126],[353,126],[397,126],[441,126],[485,126],[529,126],[573,126],[617,126],[661,126],[705,126],[750,126],[45,168],[89,168],[133,168],[177,168],[221,168],[265,168],[309,168],[353,168],[397,168],[441,168],[485,168],[529,168],[573,168],[617,168],[661,168],[705,168],[750,168],[45,210],[89,210],[133,210],[177,210],[221,210],[265,210],[309,210],[353,210],[397,210],[441,210],[485,210],[529,210],[573,210],[617,210],[661,210],[705,210],[750,210],[45,254],[89,254],[133,254],[177,254],[221,254],[265,254],[309,254],[353,254],[397,254],[441,254],[485,254],[529,254],[573,254],[617,254],[661,254],[705,254],[750,254],[45,298],[89,298],[133,298],[177,298],[221,298],[265,298],[309,298],[353,298],[397,298],[441,298],[485,298],[529,298],[573,298],[617,298],[661,298],[705,298],[750,298],[45,342],[89,342],[133,342],[177,342],[221,342],[265,342],[309,342],[353,342],[397,342],[441,342],[485,342],[529,342],[573,342],[617,342],[661,342],[705,342],[750,342],[45,386],[89,386],[133,386],[177,386],[221,386],[265,386],[309,386],[353,386],[397,386],[441,386],[485,386],[529,386],[573,386],[617,386],[661,386],[705,386],[750,386],[45,430],[89,430],[133,430],[177,430],[221,430],[265,430],[309,430],[353,430],[397,430],[441,430],[485,430],[529,430],[573,430],[617,430],[661,430],[705,430],[750,430],[45,474],[89,474],[133,474],[177,474],[221,474],[265,474],[309,474],[353,474],[397,474],[441,474],[485,474],[529,474],[573,474],[617,474],[661,474],[705,474],[750,474]]
	shots_temp=[[shot[0],int(shot[1])+250,int(shot[2])+40,shot[3]] for shot in shots_temp]
	shots_temp=[[shot[0],float(shot[1])*1.5,float(shot[2])*1.5,shot[3]] for shot in shots_temp]
	print shots_temp[:5]
	pname=shots_temp[0][0]
	output=[]
	x=0
	y=0
	i=0
	while i<187:
		shot_block=[]
		for shot in shots_temp:
			if (shot[1]>=x and shot[1]<point_array[i][0]) and (shot[2]>=y and shot[2]<point_array[i][1]):
				shot_block.append(shot)
		hits=0
		for shot in shot_block:
			if int(shot[3])==1:
				hits=hits+1
		try:
			percentage=hits/len(shot_block)
		except:
			percentage=0
		# Experimenting with relative volume
		volume=len(shot_block)/len(shots_temp)
		output.append(['"%s"' % (percentage),'"%s"' % (volume),'"%s"' % (pname),'"%s"' % (len(shot_block))])
		x=point_array[i][0]
		if x==750:
			x=0
			y=point_array[i][1]
		i=i+1
	return output


def circle_chunk(shots_temp,smooth=0,quotes=1,bin_per=.08,regions=0):
	"""New chunking routine, to chunk shots into 16 mostly semi-circular zones. Rows come in organized
	as: [p_name,x_loc,y_loc,shot_made,3pt_flag].  It returns 1,500 locations - these are 1 foot x 1 foot. Each
	location in a zone, however, will have the same fg%. Court locations have domain -40 < x < 310 and range
	-250 < y < 250. Returns an output list like so: [sw_x,sw_y,ne_x,ne_y,#shots,fg%,p_name]"""
	total_shots=len(shots_temp)
	bin_size=total_shots*bin_per
	print 'bin-size'
	print bin_size
	shots_bemp=[shot for shot in shots_temp if shot[3]==1]
	print len(shots_bemp)
	output=[]
	p_name=shots_temp[0][0]
	box_matrix=point_matrix()
	shots_t=0
	for box in box_matrix:
		x_center=box[0][0]+5
		y_center=box[0][1]+5
		shots2=[shot for shot in shots_temp if int(shot[1])>=box[0][0] and int(shot[1])<box[1][0] and int(shot[2])>=box[0][1] and int(shot[2])<box[1][1]]
		shots_t=shots_t+len(shots2)
		num_shots=len(shots2)
		made_shots=len([shot for shot in shots2 if shot[3]==1])
		smooth_fg=0
		if smooth==1:
			# nearest 8% routine
			if num_shots>=bin_size:
				smooth_fg=num_shots/made_shots
			if num_shots<bin_size:
				find_x_shots=(bin_size-num_shots)+1
				dists=[]
				two_regions=[12,11,10,9,8,7,6,3,2,1,0]
				three_regions=[13,14,15,16,4,5]
				if int(box[2][0]) in three_regions:
					dist_shots=[shot for shot in shots_temp if shot[4]==1]
				if int(box[2][0]) in two_regions:
					dist_shots=[shot for shot in shots_temp if shot[4]==0]
				dist_shots=[shot for shot in dist_shots if math.sqrt((x_center-shot[1])**2+(y_center-shot[2])**2)<70] 
				for shot in dist_shots:
					dist=math.sqrt((x_center-shot[1])**2+(y_center-shot[2])**2)
					dists.append([dist,shot[3]])
				sorted_dists = sorted(dists, key=lambda place:place[0])
				fill_shots=sorted_dists[0:int(find_x_shots)]
				try:
					largest_dist=sorted_dists[0:int(find_x_shots)][-1][0]
				except:
					largest_dist=0
				shots_made_smooth=made_shots
				for shot in fill_shots:
						shots_made_smooth=shots_made_smooth+shot[1]
				num_shots_smooth=num_shots+len(fill_shots)
				try:
					smooth_fg=shots_made_smooth/num_shots_smooth
				except: 
					smooth_fg=0
		output.append([box[0][0],box[0][1],box[1][0],box[1][1],num_shots,made_shots,box[2][0],p_name,smooth_fg,largest_dist])
		# x_low, y_low, x_high, y_high, number of shots, number of made shots, region, player name, smoothed fg%
	#for shot in shots_temp:
	#	shot.append(0)
	#	for box in point_matrix:
	#		if int(shot[1])>=box[0][0] and int(shot[1])<box[1][0] and int(shot[2])>=box[0][1] and int(shot[2])<box[1][1]:
	#			shot[4]=1
	#	if shot[4]==0:
	#		print shot
	# The above is a diagnostic that checks to see if there are shots that aren't getting assigned to a
	# box. It will spit out a bunch of half-court shots.  Not really necessary anymore.
	total=0
	#for line in output:
	#	total=total+line[4]
	#print total
	# Also a diagnostic
	for region in range(0,17):
		temp_shots=[area for area in output if area[6]==region]
		region_shots=0
		region_made=0
		for area in temp_shots:
			region_shots=region_shots+area[4]
			region_made=region_made+area[5]
		try:
			fgper=region_made/region_shots
		except:
			fgper=0
		for area in output:
			if area[6]==region:
				area.append(fgper)
				area.append(region_shots)
				area.append(region_made)
	print output[0:5]
	if quotes==1:
		final_output=[['"%s"' % (area[0]+5),'"%s"' % (area[1]+5),'"%s"' % (area[4]),'"%s"' % (area[5]),'"%s"' % (area[6]),'"%s"' % (area[7]),'"%s"' % (area[8]),'"%s"' % (area[9]),'"%s"' % (area[4]/total_shots),'"%s"' % (area[10]),'"%s"' % (area[11]),'"%s"' % (total_shots)] for area in output]
		# x_center, y_center, number of shots, number of made shots, region, player name, smoothed fg%, region fg%, relative prop of shots, region shots, region made, total_shots
		return final_output
	if quotes==0:
		final_output=[[area[0]+5,area[1]+5,area[4],area[5],area[6],area[7],area[8],area[9],area[4]/total_shots,area[10],area[11],total_shots] for area in output]
		# x_center, y_center, number of shots, number of made shots, region, player name, smoothed fg%, region fg%, relative prop of shots, region shots, region made, total_shots
		return final_output



def circle_chunk2(shots_temp,bin_per=.08,regions=0):
	"""New New chunking routine, to chunk shots into 16 mostly semi-circular zones. Rows come in organized
	as: [p_name,x_loc,y_loc,shot_made,3pt_flag].  It returns 1,500 locations - these are 1 foot x 1 foot. Each
	location in a zone, however, will have the same fg%. Court locations have domain -40 < x < 310 and range
	-250 < y < 250. Returns an output list like so: [sw_x,sw_y,ne_x,ne_y,#shots,fg%,p_name]"""
	total_shots=len(shots_temp)
	bin_size=total_shots*bin_per
	output=[]
	p_name=shots_temp[0][0]
	box_matrix=point_matrix()
	shots_t=0
	for box in box_matrix:
		x_center=box[0][0]+5
		y_center=box[0][1]+5
		shots2=[shot for shot in shots_temp if int(shot[1])>=box[0][0] and int(shot[1])<box[1][0] and int(shot[2])>=box[0][1] and int(shot[2])<box[1][1]]
		# shots_t=shots_t+len(shots2)
		num_shots=len(shots2)
		# made_shots=len([shot for shot in shots2 if shot[3]==1])
		smooth_fg=0
		# nearest 8% routine
		# if num_shots>=bin_size:
		# 	smooth_fg=made_shots/num_shots
		# if num_shots<bin_size or num_shots>=bin_size:
		# 	find_x_shots=bin_size
		dists=[]
			# two_regions=[12,11,10,9,8,7,6,3,2,1,0]
			# three_regions=[13,14,15,16,4,5]
			# if int(box[2][0]) in three_regions:
			# 	dist_shots=[shot for shot in shots_temp if shot[4]==1]
			# if int(box[2][0]) in two_regions:
			# 	dist_shots=[shot for shot in shots_temp if shot[4]==0]
		dist_shots=[shot for shot in shots_temp]
		dist_shots=[shot for shot in dist_shots if math.sqrt((x_center-shot[1])**2+(y_center-shot[2])**2)<50] 
		for shot in dist_shots:
			dist=math.sqrt((x_center-shot[1])**2+(y_center-shot[2])**2)
			dists.append([dist,shot[3]])
		sorted_dists = sorted(dists, key=lambda place:place[0])
		# fill_shots=sorted_dists[0:int(find_x_shots)]
		fill_shots=sorted_dists
		shots_made_smooth=0
		for shot in fill_shots:
			shots_made_smooth=shots_made_smooth+(shot[1]*(1/sqrt(shot[0])))
		num_shots_smooth=0
		for shot in fill_shots:
			num_shots_smooth=num_shots_smooth+(1/sqrt(shot[0]))
		try:
			smooth_fg=shots_made_smooth/num_shots_smooth
		except: 
			smooth_fg=0
		three_regions=[13,14,15,16,4,5]
		if int(box[2][0]) in three_regions:
			pps_made_smooth=shots_made_smooth*1.5
		if int(box[2][0]) not in three_regions:
			pps_made_smooth=shots_made_smooth
		try: 
			smooth_pps=2*pps_made_smooth/num_shots_smooth
		except:
			smooth_pps=0
		output.append([box[0][0],box[0][1],num_shots,smooth_fg,find_region(box[0][0]+5,box[0][1]+5),smooth_pps])
	return output



def circle_chunk3(shots_temp):
	total_shots=len(shots_temp)
	#bin_size=total_shots*bin_per
	output=[]
	p_name=shots_temp[0][0]
	box_matrix=NCAA_point_matrix()
	shots_t=0
	for box in box_matrix:
		x_center=(box[0][0]+box[1][0])/2
		y_center=(box[0][1]+box[1][1])/2
		shots2=[shot for shot in shots_temp if int(shot[1])>=box[0][0] and int(shot[1])<box[1][0] and int(shot[2])>=box[0][1] and int(shot[2])<box[1][1]]
		# shots_t=shots_t+len(shots2)
		num_shots=len(shots2)
		# made_shots=len([shot for shot in shots2 if shot[3]==1])
		smooth_fg=0
		# nearest 8% routine
		# if num_shots>=bin_size:
		# 	smooth_fg=made_shots/num_shots
		# if num_shots<bin_size or num_shots>=bin_size:
		# 	find_x_shots=bin_size
		dists=[]
			# two_regions=[12,11,10,9,8,7,6,3,2,1,0]
			# three_regions=[13,14,15,16,4,5]
			# if int(box[2][0]) in three_regions:
			# 	dist_shots=[shot for shot in shots_temp if shot[4]==1]
			# if int(box[2][0]) in two_regions:
			# 	dist_shots=[shot for shot in shots_temp if shot[4]==0]
		dist_shots=[shot for shot in shots_temp]
		dist_shots=[shot for shot in dist_shots if math.sqrt((x_center-shot[1])**2+(y_center-shot[2])**2)<50] 
		for shot in dist_shots:
			dist=math.sqrt((x_center-shot[1])**2+(y_center-shot[2])**2)
			dists.append([dist,shot[3]])
		sorted_dists = sorted(dists, key=lambda place:place[0])
		# fill_shots=sorted_dists[0:int(find_x_shots)]
		fill_shots=sorted_dists
		shots_made_smooth=0
		for shot in fill_shots:
			shots_made_smooth=shots_made_smooth+(shot[1]*(1/sqrt(shot[0])))
		num_shots_smooth=0
		for shot in fill_shots:
			num_shots_smooth=num_shots_smooth+(1/sqrt(shot[0]))
		try:
			smooth_fg=shots_made_smooth/num_shots_smooth
		except: 
			smooth_fg=0
		#three_regions=[13,14,15,16,4,5]
		#if int(box[2][0]) in three_regions:
		#	pps_made_smooth=shots_made_smooth*1.5
		#if int(box[2][0]) not in three_regions:
		#	pps_made_smooth=shots_made_smooth
		#try: 
		#	smooth_pps=2*pps_made_smooth/num_shots_smooth
		#except:
		#	smooth_pps=0
		output.append([box[0][0],box[0][1],num_shots,smooth_fg,0,0])
	return output


def find_region(x,y):
	region=-1
	if (x**2)+(y**2)<=6400 and y<0:
		region=0
	if (x**2)+(y**2)<=6400 and y>=0:
		region=1
	if (x**2)+(y**2)>6400 and (x**2)+(y**2)<=25600 and y>x and x>=-52.5 and y>0:
		region=2
	if (x**2)+(y**2)>6400 and (x**2)+(y**2)<=25600 and y<-x and x>=-52.5 and y<0:
		region=3
	if x>=-52.5 and x<77.5 and y<-220 and y>=-250:
		region=4
	if x>=-52.5 and x<77.5 and y>220 and y<=250:
		region=5
	if (x**2)+(y**2)>6400 and (x**2)+(y**2)<=25600 and abs(x)>=abs(y):
		region=6
	if (x**2)+(y**2)>25600 and x<77.5 and x>=-52.5 and y<=220 and y>0:
		region=7
	if (x**2)+(y**2)>25600 and x<77.5 and x>=-52.5 and y>=-220 and y<0:
		region=8
	if (x**2)+(y**2)>25600 and (x**2)+(y**2)<56406.25 and x>=77.5 and y>0 and y>(2/3)*x:
		region=9
	if (x**2)+(y**2)>25600 and (x**2)+(y**2)<56406.25 and x>=77.5 and y<0 and y<(2/3)*-x:
		region=10
	if (x**2)+(y**2)>25600 and (x**2)+(y**2)<56406.25 and x>=77.5 and y>0 and y<=(2/3)*x:
		region=11
	if (x**2)+(y**2)>25600 and (x**2)+(y**2)<56406.25 and x>=77.5 and y<=0 and y>=(2/3)*-x:
		region=12
	if (x**2)+(y**2)>=56406.25 and y>0 and y>=x and x>=77.5:
		region=13
	if (x**2)+(y**2)>=56406.25 and y<0 and y<=-x and x>=77.5:
		region=14
	if (x**2)+(y**2)>=56406.25 and y>0 and y<x and x>=77.5:
		region=15
	if (x**2)+(y**2)>=56406.25 and y<0 and y>-x and x>=77.5:
		region=16
	#if region==-1:
	#	print x
	#	print y
	return region


def compare_sig(in_data,out_data):
	"""Determines if the difference between two given shot grids is significant. If it's not, returns that block as
	["0","0"] so that it doesn't get visualized at all."""
	temp=[]
	i=0
	print in_data[17]
	print out_data[17]
	while i<1750:
		n_in=float(in_data[i][8].replace('"',''))
		n_out=float(out_data[i][8].replace('"',''))
		p_in=float(in_data[i][6].replace('"',''))
		p_out=float(out_data[i][6].replace('"',''))
		prop_in=float(in_data[i][7].replace('"',''))
		prop_out=float(in_data[i][7].replace('"',''))
		region=in_data[i][4]
		if n_in>0 and n_out>0 and p_in>0 and p_out>0:
			se_in=.5/math.sqrt(n_in)
			se_out=.5/math.sqrt(n_out)
			overall_se=math.sqrt((se_in**2)+(se_out**2))
			t=(p_in-p_out)/overall_se
		if n_in==0 or n_out==0 or p_in==0 or p_out==0:
			t=0
		if t>=.6:
			se_prop_in=float(.5/math.sqrt(float(in_data[i][10].replace('"',''))))
			se_prop_out=float(.5/math.sqrt(float(in_data[i][10].replace('"',''))))
			print se_prop_in
			print se_prop_out
			print region
			overall_prop_se=math.sqrt((se_prop_in**2)+(se_prop_out**2))
			t2=(prop_in-prop_out)/overall_prop_se
			print t2
			if t2>=.2:
				print 'hit'
				# print in_data[i]
				# print out_data[i]
				temp.append([in_data[i][0],out_data[i][1],'"%s"' % (int(in_data[i][2].replace('"',''))-int(out_data[i][2].replace('"',''))),'"%s"' % (int(in_data[i][3].replace('"',''))-int(out_data[i][3].replace('"',''))),'"0"','"0"','"%s"' % (int(in_data[i][6].replace('"',''))-int(out_data[i][6].replace('"',''))),'"%s"' % (int(in_data[i][7].replace('"',''))-int(out_data[i][7].replace('"',''))),'"0"','"0"','"0"'])
				# x_center, y_center, number of shots, number of made shots, region, player name, region fg%, relative prop of shots, region shots, region made, total shots
			if t2<.2:
				temp.append([in_data[i][0],out_data[i][1],'"0"','"0"',in_data[i][4],'"0"','"0"','"0"','"0"','"0"','"0"'])
				# x_center, y_center, number of shots, number of made shots, region, player name, region fg%, relative prop of shots, region shots, region made, total shots
		if t<.6:
			temp.append([in_data[i][0],out_data[i][1],'"0"','"0"',in_data[i][4],'"0"','"0"','"0"','"0"','"0"','"0"'])
			# x_center, y_center, number of shots, number of made shots, region, player name, region fg%, relative prop of shots, region shots, region made, total shots
		i=i+1
	print temp[17]
	return temp


# base code from here: http://stackoverflow.com/questions/8251876/getting-dict-key-using-dict-value-in-python
def get_full_name(player_dict, short_name):
	keys=""
	for key,value in player_dict.items():
		if value == short_name:
			return key
	dists=[]
	shorts=player_dict.items()
	for short in shorts:
		dists.append(float(nltk.metrics.edit_distance(short,short_name))/len(short_name))
		mini=min(dists)
		player_short=shorts[dists.index(mini)]
		for key,value in player_dict.items():
			if value==player_short:
				return key


def adjusted_geo_def(team):
	"""Creates csv for a player's defense adjusted by fellow defenders and fg per of offensive player"""
	with open("/Users/austinc/Desktop/Current Work/NBA/shot_data.csv",'rU') as csvfile:
		reader=csv.reader(csvfile)
		shots=[row for row in reader]
	team_shots=[shot for shot in shots if shot[3].lower()==team.lower()]
	# First, loop through every shot taken against the team and associate it with the fg% of the player who took it on the closest 8% of all shots
	for t_shot in team_shots:
		player=t_shot[0]
		x_center=int(t_shot[10])
		y_center=int(t_shot[11])
		player_shots1=[[int(shot[10]),int(shot[11]),int(shot[12]),int(shot[13])] for shot in shots if shot[0]==player]
		print len(player_shots1),
		player_shots=[shot for shot in player_shots1 if shot[3]==int(t_shot[13])]
		print len(player_shots),
		player_shots=[shot for shot in player_shots if math.sqrt((x_center-shot[0])**2+(y_center-shot[1])**2)<100]
		print len(player_shots)
		# structure is: x, y, made, 3pt
		for p_shot in player_shots:
			dist=math.sqrt((int(t_shot[10])-p_shot[0])**2+(int(t_shot[11])-p_shot[1])**2)
			p_shot.append(dist)
		sorted_dists = sorted(player_shots, key=lambda place:place[4])
		sorted_dists = sorted_dists[0:int(len(player_shots1)/12.5)]
		if len(sorted_dists)<15:
			t_shot.append("OMIT")
		else:
			try:
				fg_per=len([shot for shot in sorted_dists if shot[2]==1])/len(sorted_dists)
			except:
				print x_center
				print y_center
				print sorted_dists
				print t_shot
				print "ERROR"
			t_shot.append(fg_per)
	# now that t_shot is complete, chunk up the shots for each regression. First, eliminate areas of the floor
	# where team did not face shots (less than 0.05%) In each spot they did face the requisite volume, chunk
	# up maybe 5% of volume and regress. This is just the point matrix code from earlier (creates grid).
	defense_players=[]
	for t_shot in team_shots:
		defense_players.append(t_shot[19])
		defense_players.append(t_shot[20])
		defense_players.append(t_shot[21])
		defense_players.append(t_shot[22])
		defense_players.append(t_shot[23])
	players_w_15per=[]
	for player in set(defense_players):
		games=0
		for p in defense_players:
			if p==player:
				games=games+1
		if float(games/(len(defense_players)/5))>0.15:
			players_w_15per.append(player)
	shots[0].append('offensive player fg%')
	for player in players_w_15per:
		shots[0].append(player)
	for t_shot in team_shots:
		for player in players_w_15per:
			if player in t_shot[19:24]:
				t_shot.append(1)
			else:
				t_shot.append(0)
	with open("/Users/austinc/Desktop/Current Work/NBA/%s_regready.csv" % (team),'w') as csvfile:
		writer=csv.writer(csvfile)
		writer.writerow(shots[0])
		for row in team_shots:
			writer.writerow(row)

	#point_matrix=[]
	#output=[]
	#x=-40
	#y=-250
	#while y<250:
	#	temp=[[],[]]
	#	temp[0].append(x)
	#	temp[0].append(y)
	#	temp[1].append(x+10)
	#	temp[1].append(y+10)
	#	point_matrix.append(temp)
	#	x=x+10
	#	if x==310:
	#		x=-40
	#		y=y+10
	# grid created. Now chunk up.

def adjusted_geo_def_all():
	"""Creates csv of all players/teams ready for regression analysis"""
	with open("/Users/austinc/Desktop/Current Work/NBA/shot_data.csv",'rU') as csvfile:
		reader=csv.reader(csvfile)
		shots=[row for row in reader]
	team_shots=[shot for shot in shots[1:]]
	# First, loop through every shot taken against the team and associate it with the fg% of the player who took it on the closest 8% of all shots
	for t_shot in team_shots:
		player=t_shot[0]
		x_center=int(t_shot[10])
		y_center=int(t_shot[11])
		player_shots1=[[int(shot[10]),int(shot[11]),int(shot[12]),int(shot[13])] for shot in shots if shot[0]==player]
		print len(player_shots1),
		player_shots=[shot for shot in player_shots1 if shot[3]==int(t_shot[13])]
		print len(player_shots),
		player_shots=[shot for shot in player_shots if math.sqrt((x_center-shot[0])**2+(y_center-shot[1])**2)<100]
		print len(player_shots)
		# structure is: x, y, made, 3pt
		for p_shot in player_shots:
			dist=math.sqrt((int(t_shot[10])-p_shot[0])**2+(int(t_shot[11])-p_shot[1])**2)
			p_shot.append(dist)
		sorted_dists = sorted(player_shots, key=lambda place:place[4])
		sorted_dists = sorted_dists[0:int(len(player_shots1)/12.5)]
		if len(sorted_dists)<15:
			t_shot.append("OMIT")
		else:
			try:
				fg_per=len([shot for shot in sorted_dists if shot[2]==1])/len(sorted_dists)
			except:
				print x_center
				print y_center
				print sorted_dists
				print t_shot
				print "ERROR"
			t_shot.append(fg_per)
	# now that t_shot is complete, chunk up the shots for each regression. First, eliminate areas of the floor
	# where team did not face shots (less than 0.05%) In each spot they did face the requisite volume, chunk
	# up maybe 5% of volume and regress. This is just the point matrix code from earlier (creates grid).
	defense_players=[]
	offense_players=[]
	for t_shot in team_shots:
		defense_players.append(t_shot[19])
		defense_players.append(t_shot[20])
		defense_players.append(t_shot[21])
		defense_players.append(t_shot[22])
		defense_players.append(t_shot[23])
		offense_players.append(t_shot[18])
		offense_players.append(t_shot[17])
		offense_players.append(t_shot[16])
		offense_players.append(t_shot[15])
		offense_players.append(t_shot[14])
	players_w_15per=[]
	offense_w_15per=[]
	#for player in set(defense_players):
	#	games=0
	#	for p in defense_players:
	#		if p==player:
	#			games=games+1
	#	if float(games/(len(defense_players)/150))>0.15:
	#		players_w_15per.append(player)
	#for player in set(offense_players):
	#	games=0
	#	for p in offense_players:
	#		if p==player:
	#			games=games+1
	#	if float(games/(len(offense_players)/150))>0.15:
	#		offense_w_15per.append(player)
	offense_w_15per=set(offense_players)
	players_w_15per=set(defense_players)
	shots[0].append('offensive player fg%')
	for player in players_w_15per:
		shots[0].append('def_%s' % (player))
	for t_shot in team_shots:
		for player in players_w_15per:
			if player in t_shot[19:24]:
				t_shot.append(1)
			else:
				t_shot.append(0)
	for player in offense_w_15per:
		shots[0].append('off_%s' % (player))
	for t_shot in team_shots:
		for player in offense_w_15per:
			if player in t_shot[14:19] and player!=t_shot[0]:
				t_shot.append(1)
			else:
				t_shot.append(0)
	with open("/Users/austinc/Desktop/Current Work/NBA/all_regready.csv",'w') as csvfile:
		writer=csv.writer(csvfile)
		writer.writerow(shots[0])
		for row in team_shots:
			writer.writerow(row)



def team_defense(team):
	"""Creates a csv for a team's defense"""
	with open("/Users/austinc/Desktop/Current Work/NBA/shot_data.csv",'rU') as csvfile:
		reader=csv.reader(csvfile)
		shots=[row for row in reader]
	team_shots=[shot for shot in shots if shot[3].lower()==team.lower()]
	team_shots=[[team,int(shot[11]),int(shot[10]),int(shot[12]),int(shot[13])] for shot in team_shots]
	# y-loc, x-loc, shot_made,3flag
	all_shots=[['all',int(shot[11]),int(shot[10]),int(shot[12]),int(shot[13])] for shot in shots[1:]]
	team_data=circle_chunk2(team_shots)
	average_data=circle_chunk2(all_shots)
	# x_center, y_center, number of shots, number of made shots, region, player name, smoothed fg%, region fg%, relative prop of shots, region shots, region made, total_shots
	# ([box[0][0],box[0][1],num_shots,smooth_fg,find_region(box[0][0]+5,box[0][1]+5),smooth_pps])
	csv_data=[]
	for i,region in enumerate(team_data):
		csv_data.append([region[0],region[1],region[2],float(region[3])-float(average_data[i][3]),float(region[3]),region[4],(len([shot for shot in team_shots if math.sqrt((region[0]+5-shot[1])**2+(region[1]+5-shot[2])**2)<20]))/len(team_shots)])
		# x,y,num_shots,fg_comparison,fg%,region,nearby_shots,pps_over_average
	sorted_chart=sorted(csv_data, key=itemgetter(2,6))
	sorted_chart=sorted_chart[-501:]
	sorted_chart.reverse()
	sorted_chart=[[shot[0],shot[1],shot[2],shot[3],shot[4],shot[5],shot[6]] for shot in sorted_chart]
	with open("/Users/austinc/Desktop/Current Work/NBA/%s_defense.csv" % (team),'w') as csvfile:
		writer=csv.writer(csvfile)
		for row in sorted_chart:
			writer.writerow(row)


def all_team_defense():
	"""Creates a csv for a team's defense"""
	with open("/Users/austinc/Desktop/Current Work/NBA/shot_data.csv",'rU') as csvfile:
		reader=csv.reader(csvfile)
		shots=[row for row in reader]
	teams=[row[2].lower() for row in shots[1:]]
	teams=set(teams)
	for team in teams:
		team_defense(team)


def team_medium():
	"""Finds per of midrange shots taken by each team and per made, pps"""
	with open("/Users/austinc/Desktop/Current Work/NBA/shot_data.csv",'rU') as csvfile:
		reader=csv.reader(csvfile)
		shots=[row for row in reader]
	teams=[row[2].lower() for row in shots[1:]]
	teams=set(teams)
	for team in teams:
		team_mid=[]
		team_3=[]
		team_close=[]
		team_shots=[shot for shot in shots[1:] if shot[2].lower()==team]
		for shot in team_shots:
			regiona=find_region(int(shot[11]),int(shot[10]))
			if regiona==2 or regiona==3 or regiona==6 or regiona==7 or regiona==8 or regiona==9 or regiona==10 or regiona==11 or regiona==12:
				team_mid.append(shot)
			if regiona==0 or regiona==1:
				team_close.append(shot)
			if regiona==4 or regiona==5 or regiona>12:
				team_3.append(shot)
		mid_taken=len(team_mid)
		close_taken=len(team_close)
		three_taken=len(team_3)
		mid_made=0
		close_made=0
		three_made=0
		for shot in team_mid:
			mid_made=mid_made+int(shot[12])
		for shot in team_close:
			close_made=close_made+int(shot[12])
		for shot in team_3:
			three_made=three_made+int(shot[12])
		print team,
		print ',',
		print close_taken,
		print ',',
		print close_made,
		print ',',
		print (float(close_made)/float(close_taken))*2,
		print ',',
		print mid_taken,
		print ',',
		print mid_made,
		print ',',
		print (float(mid_made)/float(mid_taken))*2,
		print ',',
		print three_taken,
		print ',',
		print three_made,
		print ',',
		print (float(three_made)/float(three_taken))*3,
		print ',',
		print len([shot for shot in team_shots if find_region(int(shot[11]),int(shot[10]))==0]),
		print ',',
		print len([shot for shot in team_shots if find_region(int(shot[11]),int(shot[10]))==1]),
		print ',',
		print len([shot for shot in team_shots if find_region(int(shot[11]),int(shot[10]))==2]),
		print ',',
		print len([shot for shot in team_shots if find_region(int(shot[11]),int(shot[10]))==3]),
		print ',',
		print len([shot for shot in team_shots if find_region(int(shot[11]),int(shot[10]))==4]),
		print ',',
		print len([shot for shot in team_shots if find_region(int(shot[11]),int(shot[10]))==5]),
		print ',',
		print len([shot for shot in team_shots if find_region(int(shot[11]),int(shot[10]))==6]),
		print ',',
		print len([shot for shot in team_shots if find_region(int(shot[11]),int(shot[10]))==7]),
		print ',',
		print len([shot for shot in team_shots if find_region(int(shot[11]),int(shot[10]))==8]),
		print ',',
		print len([shot for shot in team_shots if find_region(int(shot[11]),int(shot[10]))==9]),
		print ',',
		print len([shot for shot in team_shots if find_region(int(shot[11]),int(shot[10]))==10]),
		print ',',
		print len([shot for shot in team_shots if find_region(int(shot[11]),int(shot[10]))==11]),
		print ',',
		print len([shot for shot in team_shots if find_region(int(shot[11]),int(shot[10]))==12]),
		print ',',
		print len([shot for shot in team_shots if find_region(int(shot[11]),int(shot[10]))==13]),
		print ',',
		print len([shot for shot in team_shots if find_region(int(shot[11]),int(shot[10]))==14]),
		print ',',
		print len([shot for shot in team_shots if find_region(int(shot[11]),int(shot[10]))==15]),
		print ',',
		print len([shot for shot in team_shots if find_region(int(shot[11]),int(shot[10]))==16]),
		print ',',
		print len([shot for shot in team_shots if find_region(int(shot[11]),int(shot[10]))==0 and int(shot[12])==1]),
		print ',',
		print len([shot for shot in team_shots if find_region(int(shot[11]),int(shot[10]))==1 and int(shot[12])==1]),
		print ',',
		print len([shot for shot in team_shots if find_region(int(shot[11]),int(shot[10]))==2 and int(shot[12])==1]),
		print ',',
		print len([shot for shot in team_shots if find_region(int(shot[11]),int(shot[10]))==3 and int(shot[12])==1]),
		print ',',
		print len([shot for shot in team_shots if find_region(int(shot[11]),int(shot[10]))==4 and int(shot[12])==1]),
		print ',',
		print len([shot for shot in team_shots if find_region(int(shot[11]),int(shot[10]))==5 and int(shot[12])==1]),
		print ',',
		print len([shot for shot in team_shots if find_region(int(shot[11]),int(shot[10]))==6 and int(shot[12])==1]),
		print ',',
		print len([shot for shot in team_shots if find_region(int(shot[11]),int(shot[10]))==7 and int(shot[12])==1]),
		print ',',
		print len([shot for shot in team_shots if find_region(int(shot[11]),int(shot[10]))==8 and int(shot[12])==1]),
		print ',',
		print len([shot for shot in team_shots if find_region(int(shot[11]),int(shot[10]))==9 and int(shot[12])==1]),
		print ',',
		print len([shot for shot in team_shots if find_region(int(shot[11]),int(shot[10]))==10 and int(shot[12])==1]),
		print ',',
		print len([shot for shot in team_shots if find_region(int(shot[11]),int(shot[10]))==11 and int(shot[12])==1]),
		print ',',
		print len([shot for shot in team_shots if find_region(int(shot[11]),int(shot[10]))==12 and int(shot[12])==1]),
		print ',',
		print len([shot for shot in team_shots if find_region(int(shot[11]),int(shot[10]))==13 and int(shot[12])==1]),
		print ',',
		print len([shot for shot in team_shots if find_region(int(shot[11]),int(shot[10]))==14 and int(shot[12])==1]),
		print ',',
		print len([shot for shot in team_shots if find_region(int(shot[11]),int(shot[10]))==15 and int(shot[12])==1]),
		print ',',
		print len([shot for shot in team_shots if find_region(int(shot[11]),int(shot[10]))==16 and int(shot[12])==1])



def team_geog_def(team):
	"""For a team, outputs csvs for each player available with contributions to defense controlling
	for other defensive players, location and fg per of offensive player."""
	coef_dic={}
	with open("/Users/austinc/Desktop/Current Work/NBA/all_regready.csv",'rU') as csvfile:
		reader=csv.reader(csvfile)
		shots=[row for row in reader]
	team_shot=[row for row in shots if row[3].lower()==team.lower() or row[3].lower()=="def_team"]
	team_shots=[row for row in team_shot if row[29]!="OMIT"]
	header=[]
	# find all defensive players
	for row_header in team_shots[0][30:]:
		if row_header[0]=='o':
			start_offensive=team_shots[0].index(row_header)
			break
	team_players=[]
	for defensive_player in team_shots[0][30:start_offensive]:
		count=0
		for row in team_shots[1:]:
			count=count+int(row[team_shots[0].index(defensive_player)])
		if count>0:
			print count,
			print defensive_player
		if count>1000:
			team_players.append(defensive_player)
	headers=team_shots[0]
	shot_data=[[shot[3],shot[11],shot[10],shot[12],shot[13],shot[29]] for shot in team_shots[1:]]
	# def_team, x-loc, y-loc, made, 3pt, shooter fg%
	bin_size=len(shot_data)*.08
	for shot in shot_data:
		if shot[0]==team.upper():
			shot.append(1)
		else:
			shot.append(0)
	for shot in shot_data:
		shot.append(float(shot[3])-float(shot[5]))
	# def_team, x-loc, y-loc, shot_made, 3pt, offensive fg%, home_game, dep_var
	shot_data=[[float(shot[7]),int(shot[1]),int(shot[2]),int(shot[4]),int(shot[6])] for shot in shot_data]
	# dep_var, x-loc, y-loc, 3pt, home_game
	shot_data=array(shot_data)
	defensive_player_rows=[]
	for player in team_players:
		defensive_player_rows.append(team_shots[0].index(player))
	shots2=array(team_shots[1:])
	for index in defensive_player_rows:
		shot_data=numpy.hstack((shot_data,shots2[:,index].reshape(len(shots2),1)))
	# so now shot_data is: dep_var, x-loc, y-loc, 3pt, home_game, dplayer1, dplayer2, ...
	locations=point_matrix()
	shots_t=0
	coefficient_matrix=[]
	ses_matrix=[]
	#print shot_data[0]
	# This next part is the actual regression
	for box in locations:
		x_center=box[0][0]+5
		y_center=box[0][1]+5
		shots_box=[shot for shot in shot_data if float(shot[1])>=x_center-5 and float(shot[1])<x_center+5 and float(shot[2])>=y_center-5 and float(shot[2])<y_center+5]
		shots_t=shots_t+len(shots_box)
		num_shots=len(shots_box)
		smooth_fg=0
		# nearest 8% routine
		if num_shots>=bin_size:
			reg_shots=numpy.float_(shots_box)
		if num_shots<bin_size:
			find_x_shots=(bin_size-num_shots)+1
			dists=[]
			two_regions=[12,11,10,9,8,7,6,3,2,1,0]
			three_regions=[13,14,15,16,4,5]
			short_regions=[0,1]
			if int(box[2][0]) in three_regions:
				dist_shots=[shot for shot in shot_data if float(shot[3])==1]
			if int(box[2][0]) in two_regions:
				dist_shots=[shot for shot in shot_data if float(shot[3])==0]
				if int(box[2][0]) in short_regions:
					dist_shots=[shot for shot in dist_shots if math.sqrt(float(shot[1])**2+float(shot[2])**2)<80]
				if int(box[2][0]) not in short_regions:
					dist_shots=[shot for shot in dist_shots if math.sqrt(float(shot[1])**2+float(shot[2])**2)>=80]
			dist_shots=[shot for shot in dist_shots if math.sqrt((x_center-float(shot[1]))**2+(y_center-float(shot[2]))**2)<120]
			distances=[]
			for index, shot in enumerate(dist_shots):
				dist=math.sqrt((x_center-float(shot[1]))**2+(y_center-float(shot[2]))**2)
				# print shot[1],shot[2],x_center,y_center,dist
				distances.append(dist)
			distances=numpy.float_(distances)
			dist_shots = numpy.float_(dist_shots)
			if len(dist_shots)>0:
				dist_shots=numpy.hstack((dist_shots,distances.reshape(len(distances),1)))
				sorted_dists = dist_shots[dist_shots[:,-1].argsort()]
				fill_shots=sorted_dists[0:int(find_x_shots)]
			#except:
			#	fill_shots=[0]
			try:
				reg_shots=array([shot for shot in fill_shots])
			except:
				reg_shots=[0]
		if len(reg_shots)>=70:
			X=array([shot[4:-1] for shot in reg_shots])	
			# Home variable will be first coefficient, [1:] will be players
			Y=array(reg_shots)[:,0]
			clf=linear_model.LinearRegression()
			clf.fit(X,Y)
			coefficients=clf.coef_[1:]
			# code from this stackoverflow answer: http://stackoverflow.com/questions/20938154/standard-errors-for-multivariate-regression-coefficients
			MSE=numpy.mean((Y-clf.predict(X).T)**2)
			var_est=MSE*numpy.diag(numpy.linalg.pinv(numpy.dot(X.T,X)))
			SE_est=numpy.sqrt(var_est)
			# end snippet
			ses=SE_est[1:]
		if len(reg_shots)<70:
			coefficients=[]
			ses=[]
			for player in team_players:
				coefficients.append(0)
			for player in team_players:
				ses.append(0)
		coefficient_matrix.append(coefficients)
		ses_matrix.append(ses)
	# find shot volume from each location for each player
	volume_matrix=[]
	for box in locations:
		x_center=box[0][0]+5
		y_center=box[0][1]+5
		volumes=[]
		for player in team_players:
			pshots=[shot for shot in shot_data if float(shot[1])>=x_center-5 and float(shot[1])<x_center+5 and float(shot[2])>=y_center-5 and float(shot[2])<y_center+5]
			pshots=[shot for shot in pshots if float(shot[team_players.index(player)+5])==1]
			volumes.append(len(pshots))
		volume_matrix.append(volumes)
	final_output=[]
	# Get range effects from regression on each team_player. shots[9] is distance, shots[13] is 3pt_flag
	shot_types=[[int(shot[9]),int(shot[13])] for shot in shots[1:]]
	for index,shot in enumerate(shot_types):
		for player_index in defensive_player_rows:
			shot.append(shots[index+1][player_index])
			# now we have a list of all shots with: [distance,3pt,def_p1,def_p2,...]
	# get y variables: dummies for close, mid, or 3 point shot.
	y_close=[]
	y_mid=[]
	y_3=[]
	range_coefs=[]
	for shot in shot_types:
		if shot[0]<=8:
			y_close.append(1)
			y_mid.append(0)
			y_3.append(0)
		if shot[0]>8:
			y_close.append(0)
			if shot[1]==0:
				y_3.append(0)
				y_mid.append(1)
			if shot[1]==1:
				y_3.append(1)
				y_mid.append(0)
	print len(y_close)
	print len(y_mid)
	print len(y_3)
	# close regression
	Y=array(y_close).reshape(len(y_close),1)
	X=array([shot[2:] for shot in shot_types])
	clf=linear_model.LinearRegression()
	clf.fit(X,Y)
	range_coefs.append(clf.coef_)
	# mid regression
	Y=array(y_mid).reshape(len(y_mid),1)
	clf=linear_model.LinearRegression()
	print len(X)
	print len(Y)
	clf.fit(X,Y)
	range_coefs.append(clf.coef_)
	# 3 regression
	Y=array(y_3).reshape(len(y_3),1)
	clf=linear_model.LinearRegression()
	clf.fit(X,Y)
	range_coefs.append(clf.coef_)
	print range_coefs
	# Put volume and regression coefficients together and create chart for each player
	for index, player in enumerate(team_players):
		player_chart=[]
		total_volume=0
		for box in volume_matrix:
			total_volume=total_volume+box[index]
		for index2,box in enumerate(locations):
			try:
				if volume_matrix[index2][index]/total_volume>0.0010:
					output=[box[0][0],box[0][1],volume_matrix[index2][index],coefficient_matrix[index2][index],ses_matrix[index2][index]]
					player_chart.append(output)
			except:
				pass
		sorted_chart=sorted(player_chart, key=lambda place:place[2])
		sorted_chart=sorted_chart[-251:]
		sorted_chart.append([range_coefs[0][0][index],range_coefs[1][0][index],range_coefs[2][0][index]])
		with open('/Users/austinc/Desktop/Current Work/NBA/%s_coeffs.csv' % (player),'w') as csvfile:
			writer=csv.writer(csvfile)
			for row in sorted_chart:
				writer.writerow(row)
	
	

def point_matrix():
	point_matrix=[]
	output=[]
	x=-52.5
	y=-250
	while y<250:
		temp=[[],[],[]]
		temp[0].append(x)
		temp[0].append(y)
		temp[1].append(x+10)
		temp[1].append(y+10)
		temp[2].append(find_region(x+5,y+5))
		point_matrix.append(temp)
		x=x+10
		if x==267.5:
			x=-52.5
			y=y+10
	return point_matrix
		# [x_min,y_min],[x_max,y_max],region


def NCAA_point_matrix():
	point_matrix=[[[-52.5,-250],[-38.3333333333333,-235.833333333333]],[[-52.5,-235.833333333333],[-38.3333333333333,-221.666666666667]],[[-52.5,-221.666666666667],[-38.3333333333333,-207.5]],[[-52.5,-207.5],[-38.3333333333333,-192.5]],[[-52.5,-192.5],[-38.3333333333333,-178.333333333333]],[[-52.5,-178.333333333333],[-38.3333333333333,-164.166666666667]],[[-52.5,-164.166666666667],[-38.3333333333333,-150]],[[-52.5,-150],[-38.3333333333333,-135.833333333333]],[[-52.5,-135.833333333333],[-38.3333333333333,-121.666666666667]],[[-52.5,-121.666666666667],[-38.3333333333333,-106.666666666667]],[[-52.5,-106.666666666667],[-38.3333333333333,-92.5]],[[-52.5,-92.5],[-38.3333333333333,-78.3333333333333]],[[-52.5,-78.3333333333333],[-38.3333333333333,-64.1666666666667]],[[-52.5,-64.1666666666667],[-38.3333333333333,-50]],[[-52.5,-50],[-38.3333333333333,-35.8333333333333]],[[-52.5,-35.8333333333333],[-38.3333333333333,-21.6666666666667]],[[-52.5,-21.6666666666667],[-38.3333333333333,-7.5]],[[-52.5,-7.5],[-38.3333333333333,6.66666666666667]],[[-52.5,6.66666666666667],[-38.3333333333333,21.6666666666667]],[[-52.5,21.6666666666667],[-38.3333333333333,35.8333333333333]],[[-52.5,35.8333333333333],[-38.3333333333333,50]],[[-52.5,50],[-38.3333333333333,64.1666666666667]],[[-52.5,64.1666666666667],[-38.3333333333333,78.3333333333333]],[[-52.5,78.3333333333333],[-38.3333333333333,92.5]],[[-52.5,92.5],[-38.3333333333333,106.666666666667]],[[-52.5,106.666666666667],[-38.3333333333333,120.833333333333]],[[-52.5,120.833333333333],[-38.3333333333333,135]],[[-52.5,135],[-38.3333333333333,150]],[[-52.5,150],[-38.3333333333333,164.166666666667]],[[-52.5,164.166666666667],[-38.3333333333333,178.333333333333]],[[-52.5,178.333333333333],[-38.3333333333333,192.5]],[[-52.5,192.5],[-38.3333333333333,206.666666666667]],[[-52.5,206.666666666667],[-38.3333333333333,221.666666666667]],[[-52.5,221.666666666667],[-38.3333333333333,235.833333333333]],[[-52.5,235.833333333333],[-38.3333333333333,250]],[[-38.3333333333333,-250],[-24.1666666666667,-235.833333333333]],[[-38.3333333333333,-235.833333333333],[-24.1666666666667,-221.666666666667]],[[-38.3333333333333,-221.666666666667],[-24.1666666666667,-207.5]],[[-38.3333333333333,-207.5],[-24.1666666666667,-192.5]],[[-38.3333333333333,-192.5],[-24.1666666666667,-178.333333333333]],[[-38.3333333333333,-178.333333333333],[-24.1666666666667,-164.166666666667]],[[-38.3333333333333,-164.166666666667],[-24.1666666666667,-150]],[[-38.3333333333333,-150],[-24.1666666666667,-135.833333333333]],[[-38.3333333333333,-135.833333333333],[-24.1666666666667,-121.666666666667]],[[-38.3333333333333,-121.666666666667],[-24.1666666666667,-106.666666666667]],[[-38.3333333333333,-106.666666666667],[-24.1666666666667,-92.5]],[[-38.3333333333333,-92.5],[-24.1666666666667,-78.3333333333333]],[[-38.3333333333333,-78.3333333333333],[-24.1666666666667,-64.1666666666667]],[[-38.3333333333333,-64.1666666666667],[-24.1666666666667,-50]],[[-38.3333333333333,-50],[-24.1666666666667,-35.8333333333333]],[[-38.3333333333333,-35.8333333333333],[-24.1666666666667,-21.6666666666667]],[[-38.3333333333333,-21.6666666666667],[-24.1666666666667,-7.5]],[[-38.3333333333333,-7.5],[-24.1666666666667,6.66666666666667]],[[-38.3333333333333,6.66666666666667],[-24.1666666666667,21.6666666666667]],[[-38.3333333333333,21.6666666666667],[-24.1666666666667,35.8333333333333]],[[-38.3333333333333,35.8333333333333],[-24.1666666666667,50]],[[-38.3333333333333,50],[-24.1666666666667,64.1666666666667]],[[-38.3333333333333,64.1666666666667],[-24.1666666666667,78.3333333333333]],[[-38.3333333333333,78.3333333333333],[-24.1666666666667,92.5]],[[-38.3333333333333,92.5],[-24.1666666666667,106.666666666667]],[[-38.3333333333333,106.666666666667],[-24.1666666666667,120.833333333333]],[[-38.3333333333333,120.833333333333],[-24.1666666666667,135]],[[-38.3333333333333,135],[-24.1666666666667,150]],[[-38.3333333333333,150],[-24.1666666666667,164.166666666667]],[[-38.3333333333333,164.166666666667],[-24.1666666666667,178.333333333333]],[[-38.3333333333333,178.333333333333],[-24.1666666666667,192.5]],[[-38.3333333333333,192.5],[-24.1666666666667,206.666666666667]],[[-38.3333333333333,206.666666666667],[-24.1666666666667,221.666666666667]],[[-38.3333333333333,221.666666666667],[-24.1666666666667,235.833333333333]],[[-38.3333333333333,235.833333333333],[-24.1666666666667,250]],[[-24.1666666666667,-250],[-10,-235.833333333333]],[[-24.1666666666667,-235.833333333333],[-10,-221.666666666667]],[[-24.1666666666667,-221.666666666667],[-10,-207.5]],[[-24.1666666666667,-207.5],[-10,-192.5]],[[-24.1666666666667,-192.5],[-10,-178.333333333333]],[[-24.1666666666667,-178.333333333333],[-10,-164.166666666667]],[[-24.1666666666667,-164.166666666667],[-10,-150]],[[-24.1666666666667,-150],[-10,-135.833333333333]],[[-24.1666666666667,-135.833333333333],[-10,-121.666666666667]],[[-24.1666666666667,-121.666666666667],[-10,-106.666666666667]],[[-24.1666666666667,-106.666666666667],[-10,-92.5]],[[-24.1666666666667,-92.5],[-10,-78.3333333333333]],[[-24.1666666666667,-78.3333333333333],[-10,-64.1666666666667]],[[-24.1666666666667,-64.1666666666667],[-10,-50]],[[-24.1666666666667,-50],[-10,-35.8333333333333]],[[-24.1666666666667,-35.8333333333333],[-10,-21.6666666666667]],[[-24.1666666666667,-21.6666666666667],[-10,-7.5]],[[-24.1666666666667,-7.5],[-10,6.66666666666667]],[[-24.1666666666667,6.66666666666667],[-10,21.6666666666667]],[[-24.1666666666667,21.6666666666667],[-10,35.8333333333333]],[[-24.1666666666667,35.8333333333333],[-10,50]],[[-24.1666666666667,50],[-10,64.1666666666667]],[[-24.1666666666667,64.1666666666667],[-10,78.3333333333333]],[[-24.1666666666667,78.3333333333333],[-10,92.5]],[[-24.1666666666667,92.5],[-10,106.666666666667]],[[-24.1666666666667,106.666666666667],[-10,120.833333333333]],[[-24.1666666666667,120.833333333333],[-10,135]],[[-24.1666666666667,135],[-10,150]],[[-24.1666666666667,150],[-10,164.166666666667]],[[-24.1666666666667,164.166666666667],[-10,178.333333333333]],[[-24.1666666666667,178.333333333333],[-10,192.5]],[[-24.1666666666667,192.5],[-10,206.666666666667]],[[-24.1666666666667,206.666666666667],[-10,221.666666666667]],[[-24.1666666666667,221.666666666667],[-10,235.833333333333]],[[-24.1666666666667,235.833333333333],[-10,250]],[[-10,-250],[4.16666666666667,-235.833333333333]],[[-10,-235.833333333333],[4.16666666666667,-221.666666666667]],[[-10,-221.666666666667],[4.16666666666667,-207.5]],[[-10,-207.5],[4.16666666666667,-192.5]],[[-10,-192.5],[4.16666666666667,-178.333333333333]],[[-10,-178.333333333333],[4.16666666666667,-164.166666666667]],[[-10,-164.166666666667],[4.16666666666667,-150]],[[-10,-150],[4.16666666666667,-135.833333333333]],[[-10,-135.833333333333],[4.16666666666667,-121.666666666667]],[[-10,-121.666666666667],[4.16666666666667,-106.666666666667]],[[-10,-106.666666666667],[4.16666666666667,-92.5]],[[-10,-92.5],[4.16666666666667,-78.3333333333333]],[[-10,-78.3333333333333],[4.16666666666667,-64.1666666666667]],[[-10,-64.1666666666667],[4.16666666666667,-50]],[[-10,-50],[4.16666666666667,-35.8333333333333]],[[-10,-35.8333333333333],[4.16666666666667,-21.6666666666667]],[[-10,-21.6666666666667],[4.16666666666667,-7.5]],[[-10,-7.5],[4.16666666666667,6.66666666666667]],[[-10,6.66666666666667],[4.16666666666667,21.6666666666667]],[[-10,21.6666666666667],[4.16666666666667,35.8333333333333]],[[-10,35.8333333333333],[4.16666666666667,50]],[[-10,50],[4.16666666666667,64.1666666666667]],[[-10,64.1666666666667],[4.16666666666667,78.3333333333333]],[[-10,78.3333333333333],[4.16666666666667,92.5]],[[-10,92.5],[4.16666666666667,106.666666666667]],[[-10,106.666666666667],[4.16666666666667,120.833333333333]],[[-10,120.833333333333],[4.16666666666667,135]],[[-10,135],[4.16666666666667,150]],[[-10,150],[4.16666666666667,164.166666666667]],[[-10,164.166666666667],[4.16666666666667,178.333333333333]],[[-10,178.333333333333],[4.16666666666667,192.5]],[[-10,192.5],[4.16666666666667,206.666666666667]],[[-10,206.666666666667],[4.16666666666667,221.666666666667]],[[-10,221.666666666667],[4.16666666666667,235.833333333333]],[[-10,235.833333333333],[4.16666666666667,250]],[[4.16666666666667,-250],[18.3333333333333,-235.833333333333]],[[4.16666666666667,-235.833333333333],[18.3333333333333,-221.666666666667]],[[4.16666666666667,-221.666666666667],[18.3333333333333,-207.5]],[[4.16666666666667,-207.5],[18.3333333333333,-192.5]],[[4.16666666666667,-192.5],[18.3333333333333,-178.333333333333]],[[4.16666666666667,-178.333333333333],[18.3333333333333,-164.166666666667]],[[4.16666666666667,-164.166666666667],[18.3333333333333,-150]],[[4.16666666666667,-150],[18.3333333333333,-135.833333333333]],[[4.16666666666667,-135.833333333333],[18.3333333333333,-121.666666666667]],[[4.16666666666667,-121.666666666667],[18.3333333333333,-106.666666666667]],[[4.16666666666667,-106.666666666667],[18.3333333333333,-92.5]],[[4.16666666666667,-92.5],[18.3333333333333,-78.3333333333333]],[[4.16666666666667,-78.3333333333333],[18.3333333333333,-64.1666666666667]],[[4.16666666666667,-64.1666666666667],[18.3333333333333,-50]],[[4.16666666666667,-50],[18.3333333333333,-35.8333333333333]],[[4.16666666666667,-35.8333333333333],[18.3333333333333,-21.6666666666667]],[[4.16666666666667,-21.6666666666667],[18.3333333333333,-7.5]],[[4.16666666666667,-7.5],[18.3333333333333,6.66666666666667]],[[4.16666666666667,6.66666666666667],[18.3333333333333,21.6666666666667]],[[4.16666666666667,21.6666666666667],[18.3333333333333,35.8333333333333]],[[4.16666666666667,35.8333333333333],[18.3333333333333,50]],[[4.16666666666667,50],[18.3333333333333,64.1666666666667]],[[4.16666666666667,64.1666666666667],[18.3333333333333,78.3333333333333]],[[4.16666666666667,78.3333333333333],[18.3333333333333,92.5]],[[4.16666666666667,92.5],[18.3333333333333,106.666666666667]],[[4.16666666666667,106.666666666667],[18.3333333333333,120.833333333333]],[[4.16666666666667,120.833333333333],[18.3333333333333,135]],[[4.16666666666667,135],[18.3333333333333,150]],[[4.16666666666667,150],[18.3333333333333,164.166666666667]],[[4.16666666666667,164.166666666667],[18.3333333333333,178.333333333333]],[[4.16666666666667,178.333333333333],[18.3333333333333,192.5]],[[4.16666666666667,192.5],[18.3333333333333,206.666666666667]],[[4.16666666666667,206.666666666667],[18.3333333333333,221.666666666667]],[[4.16666666666667,221.666666666667],[18.3333333333333,235.833333333333]],[[4.16666666666667,235.833333333333],[18.3333333333333,250]],[[18.3333333333333,-250],[32.5,-235.833333333333]],[[18.3333333333333,-235.833333333333],[32.5,-221.666666666667]],[[18.3333333333333,-221.666666666667],[32.5,-207.5]],[[18.3333333333333,-207.5],[32.5,-192.5]],[[18.3333333333333,-192.5],[32.5,-178.333333333333]],[[18.3333333333333,-178.333333333333],[32.5,-164.166666666667]],[[18.3333333333333,-164.166666666667],[32.5,-150]],[[18.3333333333333,-150],[32.5,-135.833333333333]],[[18.3333333333333,-135.833333333333],[32.5,-121.666666666667]],[[18.3333333333333,-121.666666666667],[32.5,-106.666666666667]],[[18.3333333333333,-106.666666666667],[32.5,-92.5]],[[18.3333333333333,-92.5],[32.5,-78.3333333333333]],[[18.3333333333333,-78.3333333333333],[32.5,-64.1666666666667]],[[18.3333333333333,-64.1666666666667],[32.5,-50]],[[18.3333333333333,-50],[32.5,-35.8333333333333]],[[18.3333333333333,-35.8333333333333],[32.5,-21.6666666666667]],[[18.3333333333333,-21.6666666666667],[32.5,-7.5]],[[18.3333333333333,-7.5],[32.5,6.66666666666667]],[[18.3333333333333,6.66666666666667],[32.5,21.6666666666667]],[[18.3333333333333,21.6666666666667],[32.5,35.8333333333333]],[[18.3333333333333,35.8333333333333],[32.5,50]],[[18.3333333333333,50],[32.5,64.1666666666667]],[[18.3333333333333,64.1666666666667],[32.5,78.3333333333333]],[[18.3333333333333,78.3333333333333],[32.5,92.5]],[[18.3333333333333,92.5],[32.5,106.666666666667]],[[18.3333333333333,106.666666666667],[32.5,120.833333333333]],[[18.3333333333333,120.833333333333],[32.5,135]],[[18.3333333333333,135],[32.5,150]],[[18.3333333333333,150],[32.5,164.166666666667]],[[18.3333333333333,164.166666666667],[32.5,178.333333333333]],[[18.3333333333333,178.333333333333],[32.5,192.5]],[[18.3333333333333,192.5],[32.5,206.666666666667]],[[18.3333333333333,206.666666666667],[32.5,221.666666666667]],[[18.3333333333333,221.666666666667],[32.5,235.833333333333]],[[18.3333333333333,235.833333333333],[32.5,250]],[[32.5,-250],[46.6666666666667,-235.833333333333]],[[32.5,-235.833333333333],[46.6666666666667,-221.666666666667]],[[32.5,-221.666666666667],[46.6666666666667,-207.5]],[[32.5,-207.5],[46.6666666666667,-192.5]],[[32.5,-192.5],[46.6666666666667,-178.333333333333]],[[32.5,-178.333333333333],[46.6666666666667,-164.166666666667]],[[32.5,-164.166666666667],[46.6666666666667,-150]],[[32.5,-150],[46.6666666666667,-135.833333333333]],[[32.5,-135.833333333333],[46.6666666666667,-121.666666666667]],[[32.5,-121.666666666667],[46.6666666666667,-106.666666666667]],[[32.5,-106.666666666667],[46.6666666666667,-92.5]],[[32.5,-92.5],[46.6666666666667,-78.3333333333333]],[[32.5,-78.3333333333333],[46.6666666666667,-64.1666666666667]],[[32.5,-64.1666666666667],[46.6666666666667,-50]],[[32.5,-50],[46.6666666666667,-35.8333333333333]],[[32.5,-35.8333333333333],[46.6666666666667,-21.6666666666667]],[[32.5,-21.6666666666667],[46.6666666666667,-7.5]],[[32.5,-7.5],[46.6666666666667,6.66666666666667]],[[32.5,6.66666666666667],[46.6666666666667,21.6666666666667]],[[32.5,21.6666666666667],[46.6666666666667,35.8333333333333]],[[32.5,35.8333333333333],[46.6666666666667,50]],[[32.5,50],[46.6666666666667,64.1666666666667]],[[32.5,64.1666666666667],[46.6666666666667,78.3333333333333]],[[32.5,78.3333333333333],[46.6666666666667,92.5]],[[32.5,92.5],[46.6666666666667,106.666666666667]],[[32.5,106.666666666667],[46.6666666666667,120.833333333333]],[[32.5,120.833333333333],[46.6666666666667,135]],[[32.5,135],[46.6666666666667,150]],[[32.5,150],[46.6666666666667,164.166666666667]],[[32.5,164.166666666667],[46.6666666666667,178.333333333333]],[[32.5,178.333333333333],[46.6666666666667,192.5]],[[32.5,192.5],[46.6666666666667,206.666666666667]],[[32.5,206.666666666667],[46.6666666666667,221.666666666667]],[[32.5,221.666666666667],[46.6666666666667,235.833333333333]],[[32.5,235.833333333333],[46.6666666666667,250]],[[46.6666666666667,-250],[60.8333333333333,-235.833333333333]],[[46.6666666666667,-235.833333333333],[60.8333333333333,-221.666666666667]],[[46.6666666666667,-221.666666666667],[60.8333333333333,-207.5]],[[46.6666666666667,-207.5],[60.8333333333333,-192.5]],[[46.6666666666667,-192.5],[60.8333333333333,-178.333333333333]],[[46.6666666666667,-178.333333333333],[60.8333333333333,-164.166666666667]],[[46.6666666666667,-164.166666666667],[60.8333333333333,-150]],[[46.6666666666667,-150],[60.8333333333333,-135.833333333333]],[[46.6666666666667,-135.833333333333],[60.8333333333333,-121.666666666667]],[[46.6666666666667,-121.666666666667],[60.8333333333333,-106.666666666667]],[[46.6666666666667,-106.666666666667],[60.8333333333333,-92.5]],[[46.6666666666667,-92.5],[60.8333333333333,-78.3333333333333]],[[46.6666666666667,-78.3333333333333],[60.8333333333333,-64.1666666666667]],[[46.6666666666667,-64.1666666666667],[60.8333333333333,-50]],[[46.6666666666667,-50],[60.8333333333333,-35.8333333333333]],[[46.6666666666667,-35.8333333333333],[60.8333333333333,-21.6666666666667]],[[46.6666666666667,-21.6666666666667],[60.8333333333333,-7.5]],[[46.6666666666667,-7.5],[60.8333333333333,6.66666666666667]],[[46.6666666666667,6.66666666666667],[60.8333333333333,21.6666666666667]],[[46.6666666666667,21.6666666666667],[60.8333333333333,35.8333333333333]],[[46.6666666666667,35.8333333333333],[60.8333333333333,50]],[[46.6666666666667,50],[60.8333333333333,64.1666666666667]],[[46.6666666666667,64.1666666666667],[60.8333333333333,78.3333333333333]],[[46.6666666666667,78.3333333333333],[60.8333333333333,92.5]],[[46.6666666666667,92.5],[60.8333333333333,106.666666666667]],[[46.6666666666667,106.666666666667],[60.8333333333333,120.833333333333]],[[46.6666666666667,120.833333333333],[60.8333333333333,135]],[[46.6666666666667,135],[60.8333333333333,150]],[[46.6666666666667,150],[60.8333333333333,164.166666666667]],[[46.6666666666667,164.166666666667],[60.8333333333333,178.333333333333]],[[46.6666666666667,178.333333333333],[60.8333333333333,192.5]],[[46.6666666666667,192.5],[60.8333333333333,206.666666666667]],[[46.6666666666667,206.666666666667],[60.8333333333333,221.666666666667]],[[46.6666666666667,221.666666666667],[60.8333333333333,235.833333333333]],[[46.6666666666667,235.833333333333],[60.8333333333333,250]],[[60.8333333333333,-250],[75,-235.833333333333]],[[60.8333333333333,-235.833333333333],[75,-221.666666666667]],[[60.8333333333333,-221.666666666667],[75,-207.5]],[[60.8333333333333,-207.5],[75,-192.5]],[[60.8333333333333,-192.5],[75,-178.333333333333]],[[60.8333333333333,-178.333333333333],[75,-164.166666666667]],[[60.8333333333333,-164.166666666667],[75,-150]],[[60.8333333333333,-150],[75,-135.833333333333]],[[60.8333333333333,-135.833333333333],[75,-121.666666666667]],[[60.8333333333333,-121.666666666667],[75,-106.666666666667]],[[60.8333333333333,-106.666666666667],[75,-92.5]],[[60.8333333333333,-92.5],[75,-78.3333333333333]],[[60.8333333333333,-78.3333333333333],[75,-64.1666666666667]],[[60.8333333333333,-64.1666666666667],[75,-50]],[[60.8333333333333,-50],[75,-35.8333333333333]],[[60.8333333333333,-35.8333333333333],[75,-21.6666666666667]],[[60.8333333333333,-21.6666666666667],[75,-7.5]],[[60.8333333333333,-7.5],[75,6.66666666666667]],[[60.8333333333333,6.66666666666667],[75,21.6666666666667]],[[60.8333333333333,21.6666666666667],[75,35.8333333333333]],[[60.8333333333333,35.8333333333333],[75,50]],[[60.8333333333333,50],[75,64.1666666666667]],[[60.8333333333333,64.1666666666667],[75,78.3333333333333]],[[60.8333333333333,78.3333333333333],[75,92.5]],[[60.8333333333333,92.5],[75,106.666666666667]],[[60.8333333333333,106.666666666667],[75,120.833333333333]],[[60.8333333333333,120.833333333333],[75,135]],[[60.8333333333333,135],[75,150]],[[60.8333333333333,150],[75,164.166666666667]],[[60.8333333333333,164.166666666667],[75,178.333333333333]],[[60.8333333333333,178.333333333333],[75,192.5]],[[60.8333333333333,192.5],[75,206.666666666667]],[[60.8333333333333,206.666666666667],[75,221.666666666667]],[[60.8333333333333,221.666666666667],[75,235.833333333333]],[[60.8333333333333,235.833333333333],[75,250]],[[75,-250],[89.1666666666667,-235.833333333333]],[[75,-235.833333333333],[89.1666666666667,-221.666666666667]],[[75,-221.666666666667],[89.1666666666667,-207.5]],[[75,-207.5],[89.1666666666667,-192.5]],[[75,-192.5],[89.1666666666667,-178.333333333333]],[[75,-178.333333333333],[89.1666666666667,-164.166666666667]],[[75,-164.166666666667],[89.1666666666667,-150]],[[75,-150],[89.1666666666667,-135.833333333333]],[[75,-135.833333333333],[89.1666666666667,-121.666666666667]],[[75,-121.666666666667],[89.1666666666667,-106.666666666667]],[[75,-106.666666666667],[89.1666666666667,-92.5]],[[75,-92.5],[89.1666666666667,-78.3333333333333]],[[75,-78.3333333333333],[89.1666666666667,-64.1666666666667]],[[75,-64.1666666666667],[89.1666666666667,-50]],[[75,-50],[89.1666666666667,-35.8333333333333]],[[75,-35.8333333333333],[89.1666666666667,-21.6666666666667]],[[75,-21.6666666666667],[89.1666666666667,-7.5]],[[75,-7.5],[89.1666666666667,6.66666666666667]],[[75,6.66666666666667],[89.1666666666667,21.6666666666667]],[[75,21.6666666666667],[89.1666666666667,35.8333333333333]],[[75,35.8333333333333],[89.1666666666667,50]],[[75,50],[89.1666666666667,64.1666666666667]],[[75,64.1666666666667],[89.1666666666667,78.3333333333333]],[[75,78.3333333333333],[89.1666666666667,92.5]],[[75,92.5],[89.1666666666667,106.666666666667]],[[75,106.666666666667],[89.1666666666667,120.833333333333]],[[75,120.833333333333],[89.1666666666667,135]],[[75,135],[89.1666666666667,150]],[[75,150],[89.1666666666667,164.166666666667]],[[75,164.166666666667],[89.1666666666667,178.333333333333]],[[75,178.333333333333],[89.1666666666667,192.5]],[[75,192.5],[89.1666666666667,206.666666666667]],[[75,206.666666666667],[89.1666666666667,221.666666666667]],[[75,221.666666666667],[89.1666666666667,235.833333333333]],[[75,235.833333333333],[89.1666666666667,250]],[[89.1666666666667,-250],[103.333333333333,-235.833333333333]],[[89.1666666666667,-235.833333333333],[103.333333333333,-221.666666666667]],[[89.1666666666667,-221.666666666667],[103.333333333333,-207.5]],[[89.1666666666667,-207.5],[103.333333333333,-192.5]],[[89.1666666666667,-192.5],[103.333333333333,-178.333333333333]],[[89.1666666666667,-178.333333333333],[103.333333333333,-164.166666666667]],[[89.1666666666667,-164.166666666667],[103.333333333333,-150]],[[89.1666666666667,-150],[103.333333333333,-135.833333333333]],[[89.1666666666667,-135.833333333333],[103.333333333333,-121.666666666667]],[[89.1666666666667,-121.666666666667],[103.333333333333,-106.666666666667]],[[89.1666666666667,-106.666666666667],[103.333333333333,-92.5]],[[89.1666666666667,-92.5],[103.333333333333,-78.3333333333333]],[[89.1666666666667,-78.3333333333333],[103.333333333333,-64.1666666666667]],[[89.1666666666667,-64.1666666666667],[103.333333333333,-50]],[[89.1666666666667,-50],[103.333333333333,-35.8333333333333]],[[89.1666666666667,-35.8333333333333],[103.333333333333,-21.6666666666667]],[[89.1666666666667,-21.6666666666667],[103.333333333333,-7.5]],[[89.1666666666667,-7.5],[103.333333333333,6.66666666666667]],[[89.1666666666667,6.66666666666667],[103.333333333333,21.6666666666667]],[[89.1666666666667,21.6666666666667],[103.333333333333,35.8333333333333]],[[89.1666666666667,35.8333333333333],[103.333333333333,50]],[[89.1666666666667,50],[103.333333333333,64.1666666666667]],[[89.1666666666667,64.1666666666667],[103.333333333333,78.3333333333333]],[[89.1666666666667,78.3333333333333],[103.333333333333,92.5]],[[89.1666666666667,92.5],[103.333333333333,106.666666666667]],[[89.1666666666667,106.666666666667],[103.333333333333,120.833333333333]],[[89.1666666666667,120.833333333333],[103.333333333333,135]],[[89.1666666666667,135],[103.333333333333,150]],[[89.1666666666667,150],[103.333333333333,164.166666666667]],[[89.1666666666667,164.166666666667],[103.333333333333,178.333333333333]],[[89.1666666666667,178.333333333333],[103.333333333333,192.5]],[[89.1666666666667,192.5],[103.333333333333,206.666666666667]],[[89.1666666666667,206.666666666667],[103.333333333333,221.666666666667]],[[89.1666666666667,221.666666666667],[103.333333333333,235.833333333333]],[[89.1666666666667,235.833333333333],[103.333333333333,250]],[[103.333333333333,-250],[117.5,-235.833333333333]],[[103.333333333333,-235.833333333333],[117.5,-221.666666666667]],[[103.333333333333,-221.666666666667],[117.5,-207.5]],[[103.333333333333,-207.5],[117.5,-192.5]],[[103.333333333333,-192.5],[117.5,-178.333333333333]],[[103.333333333333,-178.333333333333],[117.5,-164.166666666667]],[[103.333333333333,-164.166666666667],[117.5,-150]],[[103.333333333333,-150],[117.5,-135.833333333333]],[[103.333333333333,-135.833333333333],[117.5,-121.666666666667]],[[103.333333333333,-121.666666666667],[117.5,-106.666666666667]],[[103.333333333333,-106.666666666667],[117.5,-92.5]],[[103.333333333333,-92.5],[117.5,-78.3333333333333]],[[103.333333333333,-78.3333333333333],[117.5,-64.1666666666667]],[[103.333333333333,-64.1666666666667],[117.5,-50]],[[103.333333333333,-50],[117.5,-35.8333333333333]],[[103.333333333333,-35.8333333333333],[117.5,-21.6666666666667]],[[103.333333333333,-21.6666666666667],[117.5,-7.5]],[[103.333333333333,-7.5],[117.5,6.66666666666667]],[[103.333333333333,6.66666666666667],[117.5,21.6666666666667]],[[103.333333333333,21.6666666666667],[117.5,35.8333333333333]],[[103.333333333333,35.8333333333333],[117.5,50]],[[103.333333333333,50],[117.5,64.1666666666667]],[[103.333333333333,64.1666666666667],[117.5,78.3333333333333]],[[103.333333333333,78.3333333333333],[117.5,92.5]],[[103.333333333333,92.5],[117.5,106.666666666667]],[[103.333333333333,106.666666666667],[117.5,120.833333333333]],[[103.333333333333,120.833333333333],[117.5,135]],[[103.333333333333,135],[117.5,150]],[[103.333333333333,150],[117.5,164.166666666667]],[[103.333333333333,164.166666666667],[117.5,178.333333333333]],[[103.333333333333,178.333333333333],[117.5,192.5]],[[103.333333333333,192.5],[117.5,206.666666666667]],[[103.333333333333,206.666666666667],[117.5,221.666666666667]],[[103.333333333333,221.666666666667],[117.5,235.833333333333]],[[103.333333333333,235.833333333333],[117.5,250]],[[117.5,-250],[131.666666666667,-235.833333333333]],[[117.5,-235.833333333333],[131.666666666667,-221.666666666667]],[[117.5,-221.666666666667],[131.666666666667,-207.5]],[[117.5,-207.5],[131.666666666667,-192.5]],[[117.5,-192.5],[131.666666666667,-178.333333333333]],[[117.5,-178.333333333333],[131.666666666667,-164.166666666667]],[[117.5,-164.166666666667],[131.666666666667,-150]],[[117.5,-150],[131.666666666667,-135.833333333333]],[[117.5,-135.833333333333],[131.666666666667,-121.666666666667]],[[117.5,-121.666666666667],[131.666666666667,-106.666666666667]],[[117.5,-106.666666666667],[131.666666666667,-92.5]],[[117.5,-92.5],[131.666666666667,-78.3333333333333]],[[117.5,-78.3333333333333],[131.666666666667,-64.1666666666667]],[[117.5,-64.1666666666667],[131.666666666667,-50]],[[117.5,-50],[131.666666666667,-35.8333333333333]],[[117.5,-35.8333333333333],[131.666666666667,-21.6666666666667]],[[117.5,-21.6666666666667],[131.666666666667,-7.5]],[[117.5,-7.5],[131.666666666667,6.66666666666667]],[[117.5,6.66666666666667],[131.666666666667,21.6666666666667]],[[117.5,21.6666666666667],[131.666666666667,35.8333333333333]],[[117.5,35.8333333333333],[131.666666666667,50]],[[117.5,50],[131.666666666667,64.1666666666667]],[[117.5,64.1666666666667],[131.666666666667,78.3333333333333]],[[117.5,78.3333333333333],[131.666666666667,92.5]],[[117.5,92.5],[131.666666666667,106.666666666667]],[[117.5,106.666666666667],[131.666666666667,120.833333333333]],[[117.5,120.833333333333],[131.666666666667,135]],[[117.5,135],[131.666666666667,150]],[[117.5,150],[131.666666666667,164.166666666667]],[[117.5,164.166666666667],[131.666666666667,178.333333333333]],[[117.5,178.333333333333],[131.666666666667,192.5]],[[117.5,192.5],[131.666666666667,206.666666666667]],[[117.5,206.666666666667],[131.666666666667,221.666666666667]],[[117.5,221.666666666667],[131.666666666667,235.833333333333]],[[117.5,235.833333333333],[131.666666666667,250]],[[131.666666666667,-250],[145.833333333333,-235.833333333333]],[[131.666666666667,-235.833333333333],[145.833333333333,-221.666666666667]],[[131.666666666667,-221.666666666667],[145.833333333333,-207.5]],[[131.666666666667,-207.5],[145.833333333333,-192.5]],[[131.666666666667,-192.5],[145.833333333333,-178.333333333333]],[[131.666666666667,-178.333333333333],[145.833333333333,-164.166666666667]],[[131.666666666667,-164.166666666667],[145.833333333333,-150]],[[131.666666666667,-150],[145.833333333333,-135.833333333333]],[[131.666666666667,-135.833333333333],[145.833333333333,-121.666666666667]],[[131.666666666667,-121.666666666667],[145.833333333333,-106.666666666667]],[[131.666666666667,-106.666666666667],[145.833333333333,-92.5]],[[131.666666666667,-92.5],[145.833333333333,-78.3333333333333]],[[131.666666666667,-78.3333333333333],[145.833333333333,-64.1666666666667]],[[131.666666666667,-64.1666666666667],[145.833333333333,-50]],[[131.666666666667,-50],[145.833333333333,-35.8333333333333]],[[131.666666666667,-35.8333333333333],[145.833333333333,-21.6666666666667]],[[131.666666666667,-21.6666666666667],[145.833333333333,-7.5]],[[131.666666666667,-7.5],[145.833333333333,6.66666666666667]],[[131.666666666667,6.66666666666667],[145.833333333333,21.6666666666667]],[[131.666666666667,21.6666666666667],[145.833333333333,35.8333333333333]],[[131.666666666667,35.8333333333333],[145.833333333333,50]],[[131.666666666667,50],[145.833333333333,64.1666666666667]],[[131.666666666667,64.1666666666667],[145.833333333333,78.3333333333333]],[[131.666666666667,78.3333333333333],[145.833333333333,92.5]],[[131.666666666667,92.5],[145.833333333333,106.666666666667]],[[131.666666666667,106.666666666667],[145.833333333333,120.833333333333]],[[131.666666666667,120.833333333333],[145.833333333333,135]],[[131.666666666667,135],[145.833333333333,150]],[[131.666666666667,150],[145.833333333333,164.166666666667]],[[131.666666666667,164.166666666667],[145.833333333333,178.333333333333]],[[131.666666666667,178.333333333333],[145.833333333333,192.5]],[[131.666666666667,192.5],[145.833333333333,206.666666666667]],[[131.666666666667,206.666666666667],[145.833333333333,221.666666666667]],[[131.666666666667,221.666666666667],[145.833333333333,235.833333333333]],[[131.666666666667,235.833333333333],[145.833333333333,250]],[[145.833333333333,-250],[160,-235.833333333333]],[[145.833333333333,-235.833333333333],[160,-221.666666666667]],[[145.833333333333,-221.666666666667],[160,-207.5]],[[145.833333333333,-207.5],[160,-192.5]],[[145.833333333333,-192.5],[160,-178.333333333333]],[[145.833333333333,-178.333333333333],[160,-164.166666666667]],[[145.833333333333,-164.166666666667],[160,-150]],[[145.833333333333,-150],[160,-135.833333333333]],[[145.833333333333,-135.833333333333],[160,-121.666666666667]],[[145.833333333333,-121.666666666667],[160,-106.666666666667]],[[145.833333333333,-106.666666666667],[160,-92.5]],[[145.833333333333,-92.5],[160,-78.3333333333333]],[[145.833333333333,-78.3333333333333],[160,-64.1666666666667]],[[145.833333333333,-64.1666666666667],[160,-50]],[[145.833333333333,-50],[160,-35.8333333333333]],[[145.833333333333,-35.8333333333333],[160,-21.6666666666667]],[[145.833333333333,-21.6666666666667],[160,-7.5]],[[145.833333333333,-7.5],[160,6.66666666666667]],[[145.833333333333,6.66666666666667],[160,21.6666666666667]],[[145.833333333333,21.6666666666667],[160,35.8333333333333]],[[145.833333333333,35.8333333333333],[160,50]],[[145.833333333333,50],[160,64.1666666666667]],[[145.833333333333,64.1666666666667],[160,78.3333333333333]],[[145.833333333333,78.3333333333333],[160,92.5]],[[145.833333333333,92.5],[160,106.666666666667]],[[145.833333333333,106.666666666667],[160,120.833333333333]],[[145.833333333333,120.833333333333],[160,135]],[[145.833333333333,135],[160,150]],[[145.833333333333,150],[160,164.166666666667]],[[145.833333333333,164.166666666667],[160,178.333333333333]],[[145.833333333333,178.333333333333],[160,192.5]],[[145.833333333333,192.5],[160,206.666666666667]],[[145.833333333333,206.666666666667],[160,221.666666666667]],[[145.833333333333,221.666666666667],[160,235.833333333333]],[[145.833333333333,235.833333333333],[160,250]],[[160,-250],[174.166666666667,-235.833333333333]],[[160,-235.833333333333],[174.166666666667,-221.666666666667]],[[160,-221.666666666667],[174.166666666667,-207.5]],[[160,-207.5],[174.166666666667,-192.5]],[[160,-192.5],[174.166666666667,-178.333333333333]],[[160,-178.333333333333],[174.166666666667,-164.166666666667]],[[160,-164.166666666667],[174.166666666667,-150]],[[160,-150],[174.166666666667,-135.833333333333]],[[160,-135.833333333333],[174.166666666667,-121.666666666667]],[[160,-121.666666666667],[174.166666666667,-106.666666666667]],[[160,-106.666666666667],[174.166666666667,-92.5]],[[160,-92.5],[174.166666666667,-78.3333333333333]],[[160,-78.3333333333333],[174.166666666667,-64.1666666666667]],[[160,-64.1666666666667],[174.166666666667,-50]],[[160,-50],[174.166666666667,-35.8333333333333]],[[160,-35.8333333333333],[174.166666666667,-21.6666666666667]],[[160,-21.6666666666667],[174.166666666667,-7.5]],[[160,-7.5],[174.166666666667,6.66666666666667]],[[160,6.66666666666667],[174.166666666667,21.6666666666667]],[[160,21.6666666666667],[174.166666666667,35.8333333333333]],[[160,35.8333333333333],[174.166666666667,50]],[[160,50],[174.166666666667,64.1666666666667]],[[160,64.1666666666667],[174.166666666667,78.3333333333333]],[[160,78.3333333333333],[174.166666666667,92.5]],[[160,92.5],[174.166666666667,106.666666666667]],[[160,106.666666666667],[174.166666666667,120.833333333333]],[[160,120.833333333333],[174.166666666667,135]],[[160,135],[174.166666666667,150]],[[160,150],[174.166666666667,164.166666666667]],[[160,164.166666666667],[174.166666666667,178.333333333333]],[[160,178.333333333333],[174.166666666667,192.5]],[[160,192.5],[174.166666666667,206.666666666667]],[[160,206.666666666667],[174.166666666667,221.666666666667]],[[160,221.666666666667],[174.166666666667,235.833333333333]],[[160,235.833333333333],[174.166666666667,250]],[[174.166666666667,-250],[188.333333333333,-235.833333333333]],[[174.166666666667,-235.833333333333],[188.333333333333,-221.666666666667]],[[174.166666666667,-221.666666666667],[188.333333333333,-207.5]],[[174.166666666667,-207.5],[188.333333333333,-192.5]],[[174.166666666667,-192.5],[188.333333333333,-178.333333333333]],[[174.166666666667,-178.333333333333],[188.333333333333,-164.166666666667]],[[174.166666666667,-164.166666666667],[188.333333333333,-150]],[[174.166666666667,-150],[188.333333333333,-135.833333333333]],[[174.166666666667,-135.833333333333],[188.333333333333,-121.666666666667]],[[174.166666666667,-121.666666666667],[188.333333333333,-106.666666666667]],[[174.166666666667,-106.666666666667],[188.333333333333,-92.5]],[[174.166666666667,-92.5],[188.333333333333,-78.3333333333333]],[[174.166666666667,-78.3333333333333],[188.333333333333,-64.1666666666667]],[[174.166666666667,-64.1666666666667],[188.333333333333,-50]],[[174.166666666667,-50],[188.333333333333,-35.8333333333333]],[[174.166666666667,-35.8333333333333],[188.333333333333,-21.6666666666667]],[[174.166666666667,-21.6666666666667],[188.333333333333,-7.5]],[[174.166666666667,-7.5],[188.333333333333,6.66666666666667]],[[174.166666666667,6.66666666666667],[188.333333333333,21.6666666666667]],[[174.166666666667,21.6666666666667],[188.333333333333,35.8333333333333]],[[174.166666666667,35.8333333333333],[188.333333333333,50]],[[174.166666666667,50],[188.333333333333,64.1666666666667]],[[174.166666666667,64.1666666666667],[188.333333333333,78.3333333333333]],[[174.166666666667,78.3333333333333],[188.333333333333,92.5]],[[174.166666666667,92.5],[188.333333333333,106.666666666667]],[[174.166666666667,106.666666666667],[188.333333333333,120.833333333333]],[[174.166666666667,120.833333333333],[188.333333333333,135]],[[174.166666666667,135],[188.333333333333,150]],[[174.166666666667,150],[188.333333333333,164.166666666667]],[[174.166666666667,164.166666666667],[188.333333333333,178.333333333333]],[[174.166666666667,178.333333333333],[188.333333333333,192.5]],[[174.166666666667,192.5],[188.333333333333,206.666666666667]],[[174.166666666667,206.666666666667],[188.333333333333,221.666666666667]],[[174.166666666667,221.666666666667],[188.333333333333,235.833333333333]],[[174.166666666667,235.833333333333],[188.333333333333,250]],[[188.333333333333,-250],[202.5,-235.833333333333]],[[188.333333333333,-235.833333333333],[202.5,-221.666666666667]],[[188.333333333333,-221.666666666667],[202.5,-207.5]],[[188.333333333333,-207.5],[202.5,-192.5]],[[188.333333333333,-192.5],[202.5,-178.333333333333]],[[188.333333333333,-178.333333333333],[202.5,-164.166666666667]],[[188.333333333333,-164.166666666667],[202.5,-150]],[[188.333333333333,-150],[202.5,-135.833333333333]],[[188.333333333333,-135.833333333333],[202.5,-121.666666666667]],[[188.333333333333,-121.666666666667],[202.5,-106.666666666667]],[[188.333333333333,-106.666666666667],[202.5,-92.5]],[[188.333333333333,-92.5],[202.5,-78.3333333333333]],[[188.333333333333,-78.3333333333333],[202.5,-64.1666666666667]],[[188.333333333333,-64.1666666666667],[202.5,-50]],[[188.333333333333,-50],[202.5,-35.8333333333333]],[[188.333333333333,-35.8333333333333],[202.5,-21.6666666666667]],[[188.333333333333,-21.6666666666667],[202.5,-7.5]],[[188.333333333333,-7.5],[202.5,6.66666666666667]],[[188.333333333333,6.66666666666667],[202.5,21.6666666666667]],[[188.333333333333,21.6666666666667],[202.5,35.8333333333333]],[[188.333333333333,35.8333333333333],[202.5,50]],[[188.333333333333,50],[202.5,64.1666666666667]],[[188.333333333333,64.1666666666667],[202.5,78.3333333333333]],[[188.333333333333,78.3333333333333],[202.5,92.5]],[[188.333333333333,92.5],[202.5,106.666666666667]],[[188.333333333333,106.666666666667],[202.5,120.833333333333]],[[188.333333333333,120.833333333333],[202.5,135]],[[188.333333333333,135],[202.5,150]],[[188.333333333333,150],[202.5,164.166666666667]],[[188.333333333333,164.166666666667],[202.5,178.333333333333]],[[188.333333333333,178.333333333333],[202.5,192.5]],[[188.333333333333,192.5],[202.5,206.666666666667]],[[188.333333333333,206.666666666667],[202.5,221.666666666667]],[[188.333333333333,221.666666666667],[202.5,235.833333333333]],[[188.333333333333,235.833333333333],[202.5,250]],[[202.5,-250],[216.666666666667,-235.833333333333]],[[202.5,-235.833333333333],[216.666666666667,-221.666666666667]],[[202.5,-221.666666666667],[216.666666666667,-207.5]],[[202.5,-207.5],[216.666666666667,-192.5]],[[202.5,-192.5],[216.666666666667,-178.333333333333]],[[202.5,-178.333333333333],[216.666666666667,-164.166666666667]],[[202.5,-164.166666666667],[216.666666666667,-150]],[[202.5,-150],[216.666666666667,-135.833333333333]],[[202.5,-135.833333333333],[216.666666666667,-121.666666666667]],[[202.5,-121.666666666667],[216.666666666667,-106.666666666667]],[[202.5,-106.666666666667],[216.666666666667,-92.5]],[[202.5,-92.5],[216.666666666667,-78.3333333333333]],[[202.5,-78.3333333333333],[216.666666666667,-64.1666666666667]],[[202.5,-64.1666666666667],[216.666666666667,-50]],[[202.5,-50],[216.666666666667,-35.8333333333333]],[[202.5,-35.8333333333333],[216.666666666667,-21.6666666666667]],[[202.5,-21.6666666666667],[216.666666666667,-7.5]],[[202.5,-7.5],[216.666666666667,6.66666666666667]],[[202.5,6.66666666666667],[216.666666666667,21.6666666666667]],[[202.5,21.6666666666667],[216.666666666667,35.8333333333333]],[[202.5,35.8333333333333],[216.666666666667,50]],[[202.5,50],[216.666666666667,64.1666666666667]],[[202.5,64.1666666666667],[216.666666666667,78.3333333333333]],[[202.5,78.3333333333333],[216.666666666667,92.5]],[[202.5,92.5],[216.666666666667,106.666666666667]],[[202.5,106.666666666667],[216.666666666667,120.833333333333]],[[202.5,120.833333333333],[216.666666666667,135]],[[202.5,135],[216.666666666667,150]],[[202.5,150],[216.666666666667,164.166666666667]],[[202.5,164.166666666667],[216.666666666667,178.333333333333]],[[202.5,178.333333333333],[216.666666666667,192.5]],[[202.5,192.5],[216.666666666667,206.666666666667]],[[202.5,206.666666666667],[216.666666666667,221.666666666667]],[[202.5,221.666666666667],[216.666666666667,235.833333333333]],[[202.5,235.833333333333],[216.666666666667,250]],[[216.666666666667,-250],[230.833333333333,-235.833333333333]],[[216.666666666667,-235.833333333333],[230.833333333333,-221.666666666667]],[[216.666666666667,-221.666666666667],[230.833333333333,-207.5]],[[216.666666666667,-207.5],[230.833333333333,-192.5]],[[216.666666666667,-192.5],[230.833333333333,-178.333333333333]],[[216.666666666667,-178.333333333333],[230.833333333333,-164.166666666667]],[[216.666666666667,-164.166666666667],[230.833333333333,-150]],[[216.666666666667,-150],[230.833333333333,-135.833333333333]],[[216.666666666667,-135.833333333333],[230.833333333333,-121.666666666667]],[[216.666666666667,-121.666666666667],[230.833333333333,-106.666666666667]],[[216.666666666667,-106.666666666667],[230.833333333333,-92.5]],[[216.666666666667,-92.5],[230.833333333333,-78.3333333333333]],[[216.666666666667,-78.3333333333333],[230.833333333333,-64.1666666666667]],[[216.666666666667,-64.1666666666667],[230.833333333333,-50]],[[216.666666666667,-50],[230.833333333333,-35.8333333333333]],[[216.666666666667,-35.8333333333333],[230.833333333333,-21.6666666666667]],[[216.666666666667,-21.6666666666667],[230.833333333333,-7.5]],[[216.666666666667,-7.5],[230.833333333333,6.66666666666667]],[[216.666666666667,6.66666666666667],[230.833333333333,21.6666666666667]],[[216.666666666667,21.6666666666667],[230.833333333333,35.8333333333333]],[[216.666666666667,35.8333333333333],[230.833333333333,50]],[[216.666666666667,50],[230.833333333333,64.1666666666667]],[[216.666666666667,64.1666666666667],[230.833333333333,78.3333333333333]],[[216.666666666667,78.3333333333333],[230.833333333333,92.5]],[[216.666666666667,92.5],[230.833333333333,106.666666666667]],[[216.666666666667,106.666666666667],[230.833333333333,120.833333333333]],[[216.666666666667,120.833333333333],[230.833333333333,135]],[[216.666666666667,135],[230.833333333333,150]],[[216.666666666667,150],[230.833333333333,164.166666666667]],[[216.666666666667,164.166666666667],[230.833333333333,178.333333333333]],[[216.666666666667,178.333333333333],[230.833333333333,192.5]],[[216.666666666667,192.5],[230.833333333333,206.666666666667]],[[216.666666666667,206.666666666667],[230.833333333333,221.666666666667]],[[216.666666666667,221.666666666667],[230.833333333333,235.833333333333]],[[216.666666666667,235.833333333333],[230.833333333333,250]],[[230.833333333333,-250],[245,-235.833333333333]],[[230.833333333333,-235.833333333333],[245,-221.666666666667]],[[230.833333333333,-221.666666666667],[245,-207.5]],[[230.833333333333,-207.5],[245,-192.5]],[[230.833333333333,-192.5],[245,-178.333333333333]],[[230.833333333333,-178.333333333333],[245,-164.166666666667]],[[230.833333333333,-164.166666666667],[245,-150]],[[230.833333333333,-150],[245,-135.833333333333]],[[230.833333333333,-135.833333333333],[245,-121.666666666667]],[[230.833333333333,-121.666666666667],[245,-106.666666666667]],[[230.833333333333,-106.666666666667],[245,-92.5]],[[230.833333333333,-92.5],[245,-78.3333333333333]],[[230.833333333333,-78.3333333333333],[245,-64.1666666666667]],[[230.833333333333,-64.1666666666667],[245,-50]],[[230.833333333333,-50],[245,-35.8333333333333]],[[230.833333333333,-35.8333333333333],[245,-21.6666666666667]],[[230.833333333333,-21.6666666666667],[245,-7.5]],[[230.833333333333,-7.5],[245,6.66666666666667]],[[230.833333333333,6.66666666666667],[245,21.6666666666667]],[[230.833333333333,21.6666666666667],[245,35.8333333333333]],[[230.833333333333,35.8333333333333],[245,50]],[[230.833333333333,50],[245,64.1666666666667]],[[230.833333333333,64.1666666666667],[245,78.3333333333333]],[[230.833333333333,78.3333333333333],[245,92.5]],[[230.833333333333,92.5],[245,106.666666666667]],[[230.833333333333,106.666666666667],[245,120.833333333333]],[[230.833333333333,120.833333333333],[245,135]],[[230.833333333333,135],[245,150]],[[230.833333333333,150],[245,164.166666666667]],[[230.833333333333,164.166666666667],[245,178.333333333333]],[[230.833333333333,178.333333333333],[245,192.5]],[[230.833333333333,192.5],[245,206.666666666667]],[[230.833333333333,206.666666666667],[245,221.666666666667]],[[230.833333333333,221.666666666667],[245,235.833333333333]],[[230.833333333333,235.833333333333],[245,250]],[[245,-250],[259.166666666667,-235.833333333333]],[[245,-235.833333333333],[259.166666666667,-221.666666666667]],[[245,-221.666666666667],[259.166666666667,-207.5]],[[245,-207.5],[259.166666666667,-192.5]],[[245,-192.5],[259.166666666667,-178.333333333333]],[[245,-178.333333333333],[259.166666666667,-164.166666666667]],[[245,-164.166666666667],[259.166666666667,-150]],[[245,-150],[259.166666666667,-135.833333333333]],[[245,-135.833333333333],[259.166666666667,-121.666666666667]],[[245,-121.666666666667],[259.166666666667,-106.666666666667]],[[245,-106.666666666667],[259.166666666667,-92.5]],[[245,-92.5],[259.166666666667,-78.3333333333333]],[[245,-78.3333333333333],[259.166666666667,-64.1666666666667]],[[245,-64.1666666666667],[259.166666666667,-50]],[[245,-50],[259.166666666667,-35.8333333333333]],[[245,-35.8333333333333],[259.166666666667,-21.6666666666667]],[[245,-21.6666666666667],[259.166666666667,-7.5]],[[245,-7.5],[259.166666666667,6.66666666666667]],[[245,6.66666666666667],[259.166666666667,21.6666666666667]],[[245,21.6666666666667],[259.166666666667,35.8333333333333]],[[245,35.8333333333333],[259.166666666667,50]],[[245,50],[259.166666666667,64.1666666666667]],[[245,64.1666666666667],[259.166666666667,78.3333333333333]],[[245,78.3333333333333],[259.166666666667,92.5]],[[245,92.5],[259.166666666667,106.666666666667]],[[245,106.666666666667],[259.166666666667,120.833333333333]],[[245,120.833333333333],[259.166666666667,135]],[[245,135],[259.166666666667,150]],[[245,150],[259.166666666667,164.166666666667]],[[245,164.166666666667],[259.166666666667,178.333333333333]],[[245,178.333333333333],[259.166666666667,192.5]],[[245,192.5],[259.166666666667,206.666666666667]],[[245,206.666666666667],[259.166666666667,221.666666666667]],[[245,221.666666666667],[259.166666666667,235.833333333333]],[[245,235.833333333333],[259.166666666667,250]],[[259.166666666667,-250],[273.333333333333,-235.833333333333]],[[259.166666666667,-235.833333333333],[273.333333333333,-221.666666666667]],[[259.166666666667,-221.666666666667],[273.333333333333,-207.5]],[[259.166666666667,-207.5],[273.333333333333,-192.5]],[[259.166666666667,-192.5],[273.333333333333,-178.333333333333]],[[259.166666666667,-178.333333333333],[273.333333333333,-164.166666666667]],[[259.166666666667,-164.166666666667],[273.333333333333,-150]],[[259.166666666667,-150],[273.333333333333,-135.833333333333]],[[259.166666666667,-135.833333333333],[273.333333333333,-121.666666666667]],[[259.166666666667,-121.666666666667],[273.333333333333,-106.666666666667]],[[259.166666666667,-106.666666666667],[273.333333333333,-92.5]],[[259.166666666667,-92.5],[273.333333333333,-78.3333333333333]],[[259.166666666667,-78.3333333333333],[273.333333333333,-64.1666666666667]],[[259.166666666667,-64.1666666666667],[273.333333333333,-50]],[[259.166666666667,-50],[273.333333333333,-35.8333333333333]],[[259.166666666667,-35.8333333333333],[273.333333333333,-21.6666666666667]],[[259.166666666667,-21.6666666666667],[273.333333333333,-7.5]],[[259.166666666667,-7.5],[273.333333333333,6.66666666666667]],[[259.166666666667,6.66666666666667],[273.333333333333,21.6666666666667]],[[259.166666666667,21.6666666666667],[273.333333333333,35.8333333333333]],[[259.166666666667,35.8333333333333],[273.333333333333,50]],[[259.166666666667,50],[273.333333333333,64.1666666666667]],[[259.166666666667,64.1666666666667],[273.333333333333,78.3333333333333]],[[259.166666666667,78.3333333333333],[273.333333333333,92.5]],[[259.166666666667,92.5],[273.333333333333,106.666666666667]],[[259.166666666667,106.666666666667],[273.333333333333,120.833333333333]],[[259.166666666667,120.833333333333],[273.333333333333,135]],[[259.166666666667,135],[273.333333333333,150]],[[259.166666666667,150],[273.333333333333,164.166666666667]],[[259.166666666667,164.166666666667],[273.333333333333,178.333333333333]],[[259.166666666667,178.333333333333],[273.333333333333,192.5]],[[259.166666666667,192.5],[273.333333333333,206.666666666667]],[[259.166666666667,206.666666666667],[273.333333333333,221.666666666667]],[[259.166666666667,221.666666666667],[273.333333333333,235.833333333333]],[[259.166666666667,235.833333333333],[273.333333333333,250]],[[273.333333333333,-250],[287.5,-235.833333333333]],[[273.333333333333,-235.833333333333],[287.5,-221.666666666667]],[[273.333333333333,-221.666666666667],[287.5,-207.5]],[[273.333333333333,-207.5],[287.5,-192.5]],[[273.333333333333,-192.5],[287.5,-178.333333333333]],[[273.333333333333,-178.333333333333],[287.5,-164.166666666667]],[[273.333333333333,-164.166666666667],[287.5,-150]],[[273.333333333333,-150],[287.5,-135.833333333333]],[[273.333333333333,-135.833333333333],[287.5,-121.666666666667]],[[273.333333333333,-121.666666666667],[287.5,-106.666666666667]],[[273.333333333333,-106.666666666667],[287.5,-92.5]],[[273.333333333333,-92.5],[287.5,-78.3333333333333]],[[273.333333333333,-78.3333333333333],[287.5,-64.1666666666667]],[[273.333333333333,-64.1666666666667],[287.5,-50]],[[273.333333333333,-50],[287.5,-35.8333333333333]],[[273.333333333333,-35.8333333333333],[287.5,-21.6666666666667]],[[273.333333333333,-21.6666666666667],[287.5,-7.5]],[[273.333333333333,-7.5],[287.5,6.66666666666667]],[[273.333333333333,6.66666666666667],[287.5,21.6666666666667]],[[273.333333333333,21.6666666666667],[287.5,35.8333333333333]],[[273.333333333333,35.8333333333333],[287.5,50]],[[273.333333333333,50],[287.5,64.1666666666667]],[[273.333333333333,64.1666666666667],[287.5,78.3333333333333]],[[273.333333333333,78.3333333333333],[287.5,92.5]],[[273.333333333333,92.5],[287.5,106.666666666667]],[[273.333333333333,106.666666666667],[287.5,120.833333333333]],[[273.333333333333,120.833333333333],[287.5,135]],[[273.333333333333,135],[287.5,150]],[[273.333333333333,150],[287.5,164.166666666667]],[[273.333333333333,164.166666666667],[287.5,178.333333333333]],[[273.333333333333,178.333333333333],[287.5,192.5]],[[273.333333333333,192.5],[287.5,206.666666666667]],[[273.333333333333,206.666666666667],[287.5,221.666666666667]],[[273.333333333333,221.666666666667],[287.5,235.833333333333]],[[273.333333333333,235.833333333333],[287.5,250]],[[287.5,-250],[301.666666666667,-235.833333333333]],[[287.5,-235.833333333333],[301.666666666667,-221.666666666667]],[[287.5,-221.666666666667],[301.666666666667,-207.5]],[[287.5,-207.5],[301.666666666667,-192.5]],[[287.5,-192.5],[301.666666666667,-178.333333333333]],[[287.5,-178.333333333333],[301.666666666667,-164.166666666667]],[[287.5,-164.166666666667],[301.666666666667,-150]],[[287.5,-150],[301.666666666667,-135.833333333333]],[[287.5,-135.833333333333],[301.666666666667,-121.666666666667]],[[287.5,-121.666666666667],[301.666666666667,-106.666666666667]],[[287.5,-106.666666666667],[301.666666666667,-92.5]],[[287.5,-92.5],[301.666666666667,-78.3333333333333]],[[287.5,-78.3333333333333],[301.666666666667,-64.1666666666667]],[[287.5,-64.1666666666667],[301.666666666667,-50]],[[287.5,-50],[301.666666666667,-35.8333333333333]],[[287.5,-35.8333333333333],[301.666666666667,-21.6666666666667]],[[287.5,-21.6666666666667],[301.666666666667,-7.5]],[[287.5,-7.5],[301.666666666667,6.66666666666667]],[[287.5,6.66666666666667],[301.666666666667,21.6666666666667]],[[287.5,21.6666666666667],[301.666666666667,35.8333333333333]],[[287.5,35.8333333333333],[301.666666666667,50]],[[287.5,50],[301.666666666667,64.1666666666667]],[[287.5,64.1666666666667],[301.666666666667,78.3333333333333]],[[287.5,78.3333333333333],[301.666666666667,92.5]],[[287.5,92.5],[301.666666666667,106.666666666667]],[[287.5,106.666666666667],[301.666666666667,120.833333333333]],[[287.5,120.833333333333],[301.666666666667,135]],[[287.5,135],[301.666666666667,150]],[[287.5,150],[301.666666666667,164.166666666667]],[[287.5,164.166666666667],[301.666666666667,178.333333333333]],[[287.5,178.333333333333],[301.666666666667,192.5]],[[287.5,192.5],[301.666666666667,206.666666666667]],[[287.5,206.666666666667],[301.666666666667,221.666666666667]],[[287.5,221.666666666667],[301.666666666667,235.833333333333]],[[287.5,235.833333333333],[301.666666666667,250]],[[301.666666666667,-250],[315.833333333333,-235.833333333333]],[[301.666666666667,-235.833333333333],[315.833333333333,-221.666666666667]],[[301.666666666667,-221.666666666667],[315.833333333333,-207.5]],[[301.666666666667,-207.5],[315.833333333333,-192.5]],[[301.666666666667,-192.5],[315.833333333333,-178.333333333333]],[[301.666666666667,-178.333333333333],[315.833333333333,-164.166666666667]],[[301.666666666667,-164.166666666667],[315.833333333333,-150]],[[301.666666666667,-150],[315.833333333333,-135.833333333333]],[[301.666666666667,-135.833333333333],[315.833333333333,-121.666666666667]],[[301.666666666667,-121.666666666667],[315.833333333333,-106.666666666667]],[[301.666666666667,-106.666666666667],[315.833333333333,-92.5]],[[301.666666666667,-92.5],[315.833333333333,-78.3333333333333]],[[301.666666666667,-78.3333333333333],[315.833333333333,-64.1666666666667]],[[301.666666666667,-64.1666666666667],[315.833333333333,-50]],[[301.666666666667,-50],[315.833333333333,-35.8333333333333]],[[301.666666666667,-35.8333333333333],[315.833333333333,-21.6666666666667]],[[301.666666666667,-21.6666666666667],[315.833333333333,-7.5]],[[301.666666666667,-7.5],[315.833333333333,6.66666666666667]],[[301.666666666667,6.66666666666667],[315.833333333333,21.6666666666667]],[[301.666666666667,21.6666666666667],[315.833333333333,35.8333333333333]],[[301.666666666667,35.8333333333333],[315.833333333333,50]],[[301.666666666667,50],[315.833333333333,64.1666666666667]],[[301.666666666667,64.1666666666667],[315.833333333333,78.3333333333333]],[[301.666666666667,78.3333333333333],[315.833333333333,92.5]],[[301.666666666667,92.5],[315.833333333333,106.666666666667]],[[301.666666666667,106.666666666667],[315.833333333333,120.833333333333]],[[301.666666666667,120.833333333333],[315.833333333333,135]],[[301.666666666667,135],[315.833333333333,150]],[[301.666666666667,150],[315.833333333333,164.166666666667]],[[301.666666666667,164.166666666667],[315.833333333333,178.333333333333]],[[301.666666666667,178.333333333333],[315.833333333333,192.5]],[[301.666666666667,192.5],[315.833333333333,206.666666666667]],[[301.666666666667,206.666666666667],[315.833333333333,221.666666666667]],[[301.666666666667,221.666666666667],[315.833333333333,235.833333333333]],[[301.666666666667,235.833333333333],[315.833333333333,250]]]
	return point_matrix


def league_geog_def():
	"""Specification tested regression for the whole league."""
	coef_dic={}
	with open("/Users/austinc/Desktop/Current Work/NBA/all_regready.csv",'rU') as csvfile:
		reader=csv.reader(csvfile)
		shots=[row for row in reader]
	team_shots=[row for row in shots if row[29]!="OMIT"]
	header=[]
	# find all defensive players
	for row_header in team_shots[0][30:]:
		if row_header[0]=='o':
			start_offensive=team_shots[0].index(row_header)
			break
	# These two lists hold the names of the defensive and offensive player variable dummies
	team_players=[]
	off_players=[]
	for defensive_player in team_shots[0][30:start_offensive]:
		count=0
		for row in team_shots[1:]:
			count=count+int(row[team_shots[0].index(defensive_player)])
		if count>=1000:
			team_players.append(defensive_player)
			print count,
			print defensive_player
	for offensive_player in team_shots[0][start_offensive:]:
		count=0
		for row in team_shots[1:]:
			count=count+int(row[team_shots[0].index(offensive_player)])
		if count>=1000:
			off_players.append(offensive_player)
			print count,
			print offensive_player
	headers=team_shots[0]
	shot_data=[[shot[3],shot[11],shot[10],shot[12],shot[13],shot[29]] for shot in team_shots[1:]]
	# def_team, x-loc, y-loc, made, 3pt, shooter fg%
	bin_size=10000
	for shot in shot_data:
		if shot[0]==shot[0].upper():
			shot.append(1)
		else:
			shot.append(0)
	for shot in shot_data:
		shot.append(float(shot[3])-float(shot[5]))
	# def_team, x-loc, y-loc, shot_made, 3pt, offensive fg%, home_game, dep_var
	shot_data=[[float(shot[7]),int(shot[1]),int(shot[2]),int(shot[4]),int(shot[6])] for shot in shot_data]
	# dep_var, x-loc, y-loc, 3pt, home_game
	shot_data=array(shot_data)
	# get indexes for each of the offensive/defensive player variables
	defensive_player_rows=[]
	offensive_player_rows=[]
	for player in team_players:
		defensive_player_rows.append(team_shots[0].index(player))
	for player in off_players:
		offensive_player_rows.append(team_shots[0].index(player))
	shots2=array(team_shots[1:])
	for index in defensive_player_rows:
		shot_data=numpy.hstack((shot_data,shots2[:,index].reshape(len(shots2),1)))
	for index in offensive_player_rows:
		shot_data=numpy.hstack((shot_data,shots2[:,index].reshape(len(shots2),1)))
	# so now shot_data is: dep_var, x-loc, y-loc, 3pt, home_game, dplayer1, dplayer2, ... oplayer1, oplayer2 ...
	locations=point_matrix()
	shots_t=0
	coefficient_matrix=[]
	ses_matrix=[]
	#print shot_data[0]
	# This next part is the actual regression
	two_regions=[12,11,10,9,8,7,6,3,2,1,0]
	three_regions=[13,14,15,16,4,5]
	short_regions=[0,1]
	for box in locations:
		x_center=box[0][0]+5
		y_center=box[0][1]+5
		print x_center,y_center
		shots_box=[shot for shot in shot_data if float(shot[1])>=x_center-5 and float(shot[1])<x_center+5 and float(shot[2])>=y_center-5 and float(shot[2])<y_center+5]
		shots_t=shots_t+len(shots_box)
		num_shots=len(shots_box)
		smooth_fg=0
		# nearest 8% routine
		if num_shots>=bin_size:
			reg_shots=numpy.float_(shots_box)
		if num_shots<bin_size:
			find_x_shots=(bin_size-num_shots)+1
			dists=[]
			if int(box[2][0]) in three_regions:
				dist_shots=[shot for shot in shot_data if float(shot[3])==1]
			if int(box[2][0]) in two_regions:
				dist_shots=[shot for shot in shot_data if float(shot[3])==0]
				if int(box[2][0]) in short_regions:
					dist_shots=[shot for shot in dist_shots if math.sqrt(float(shot[1])**2+float(shot[2])**2)<80]
				if int(box[2][0]) not in short_regions:
					dist_shots=[shot for shot in dist_shots if math.sqrt(float(shot[1])**2+float(shot[2])**2)>=80]
			dist_shots=[shot for shot in dist_shots if math.sqrt((x_center-float(shot[1]))**2+(y_center-float(shot[2]))**2)<120]
			distances=[]
			for index, shot in enumerate(dist_shots):
				dist=math.sqrt((x_center-float(shot[1]))**2+(y_center-float(shot[2]))**2)
				# print shot[1],shot[2],x_center,y_center,dist
				distances.append(dist)
			distances=numpy.float_(distances)
			dist_shots = numpy.float_(dist_shots)
			if len(dist_shots)>0:
				dist_shots=numpy.hstack((dist_shots,distances.reshape(len(distances),1)))
				sorted_dists = dist_shots[dist_shots[:,-1].argsort()]
				fill_shots=sorted_dists[0:10000]
			#except:
			#	fill_shots=[0]
			try:
				reg_shots=array([shot for shot in fill_shots])
			except:
				reg_shots=[0]
		if len(reg_shots)>=1000:
			X=array([shot[4:-1] for shot in reg_shots])	
			# Home variable will be first coefficient, [1:] will be players
			Y=array(reg_shots)[:,0]
			clf=linear_model.LinearRegression(fit_intercept=False)
			clf.fit(X,Y)
			coefficients=clf.coef_[1:]
			# code from this stackoverflow answer: http://stackoverflow.com/questions/20938154/standard-errors-for-multivariate-regression-coefficients
			MSE=numpy.mean((Y-clf.predict(X).T)**2)
			var_est=MSE*numpy.diag(numpy.linalg.pinv(numpy.dot(X.T,X)))
			SE_est=numpy.sqrt(var_est)
			# end snippet
			ses=SE_est[1:]
		if len(reg_shots)<1000:
			coefficients=[]
			ses=[]
			for player in team_players:
				coefficients.append(0)
			for player in team_players:
				ses.append(0)
		coefficient_matrix.append(coefficients)
		ses_matrix.append(ses)
	# find shot volume from each location for each player
	volume_matrix=[]
	for box in locations:
		x_center=box[0][0]+5
		y_center=box[0][1]+5
		pshots=[shot for shot in shot_data if float(shot[1])>=x_center-5 and float(shot[1])<x_center+5 and float(shot[2])>=y_center-5 and float(shot[2])<y_center+5]
		volumes=[]
		for player in team_players:
			volumes.append(len([shot for shot in pshots if float(shot[team_players.index(player)+5])==1]))
		volume_matrix.append(volumes)
	final_output=[]
	# Get range effects from regression on each team_player. shots[9] is distance, shots[13] is 3pt_flag
	shot_types=[[int(shot[9]),int(shot[13])] for shot in shots[1:]]
	for index,shot in enumerate(shot_types):
		for player_index in defensive_player_rows:
			shot.append(shots[index+1][player_index])
		for player_index in offensive_player_rows:
			shot.append(shots[index+1][player_index])
			# now we have a list of all shots with: [distance,3pt,def_p1,def_p2,...]
	# get y variables: dummies for close, mid, or 3 point shot.
	y_close=[]
	y_mid=[]
	y_3=[]
	range_coefs=[]
	for shot in shot_types:
		if shot[0]<=8:
			y_close.append(1)
			y_mid.append(0)
			y_3.append(0)
		if shot[0]>8:
			y_close.append(0)
			if shot[1]==0:
				y_3.append(0)
				y_mid.append(1)
			if shot[1]==1:
				y_3.append(1)
				y_mid.append(0)
	# close regression
	Y=array(y_close).reshape(len(y_close),1)
	X=array([shot[2:] for shot in shot_types])
	clf=linear_model.LinearRegression()
	clf.fit(X,Y)
	range_coefs.append(clf.coef_)
	# mid regression
	Y=array(y_mid).reshape(len(y_mid),1)
	clf=linear_model.LinearRegression()
	clf.fit(X,Y)
	range_coefs.append(clf.coef_)
	# 3 regression
	Y=array(y_3).reshape(len(y_3),1)
	clf=linear_model.LinearRegression()
	clf.fit(X,Y)
	range_coefs.append(clf.coef_)
	# Put volume and regression coefficients together and create chart for each player
	for index, player in enumerate(team_players):
		player_chart=[]
		total_volume=0
		for box in volume_matrix:
			total_volume=total_volume+box[index]
		for index2,box in enumerate(locations):
			output=[box[0][0],box[0][1],volume_matrix[index2][index],coefficient_matrix[index2][index],ses_matrix[index2][index]]
			player_chart.append(output)
		sorted_chart=sorted(player_chart, key=lambda place:place[2])
		sorted_chart=sorted_chart[-251:]
		sorted_chart.append([range_coefs[0][0][index],range_coefs[1][0][index],range_coefs[2][0][index]])
		with open('/Users/austinc/Desktop/Current Work/NBA/%s_coeffs.csv' % (player),'w') as csvfile:
			writer=csv.writer(csvfile)
			for row in sorted_chart:
				writer.writerow(row)


def league_geog_def_teamcepts():
	"""Specification tested regression for the whole league."""
	coef_dic={}
	with open("/Users/austinc/Desktop/Current Work/NBA/all_regready.csv",'rU') as csvfile:
		reader=csv.reader(csvfile)
		shots=[row for row in reader]
	team_shots=[row for row in shots if row[29]!="OMIT"]
	header=[]
	# find all defensive players
	for row_header in team_shots[0][30:]:
		if row_header[0]=='o':
			start_offensive=team_shots[0].index(row_header)
			break
	# These two lists hold the names of the defensive and offensive player variable dummies
	team_players=[]
	off_players=[]
	for defensive_player in team_shots[0][30:start_offensive]:
		count=0
		for row in team_shots[1:]:
			count=count+int(row[team_shots[0].index(defensive_player)])
		if count>=1000:
			team_players.append(defensive_player)
			print count,
			print defensive_player
	for offensive_player in team_shots[0][start_offensive:]:
		count=0
		for row in team_shots[1:]:
			count=count+int(row[team_shots[0].index(offensive_player)])
		if count>=1000:
			off_players.append(offensive_player)
			print count,
			print offensive_player
	headers=team_shots[0]
	shot_data=[[shot[3],shot[11],shot[10],shot[12],shot[13],shot[29]] for shot in team_shots[1:]]
	# def_team, x-loc, y-loc, made, 3pt, shooter fg%
	bin_size=10000
	for shot in shot_data:
		if shot[0]==shot[0].upper():
			shot.append(1)
		else:
			shot.append(0)
	for shot in shot_data:
		shot.append(float(shot[3])-float(shot[5]))
	# def_team, x-loc, y-loc, shot_made, 3pt, offensive fg%, home_game, dep_var
	shot_data=[[shot[0],float(shot[7]),int(shot[1]),int(shot[2]),int(shot[4]),int(shot[6])] for shot in shot_data]
	# def_team, dep_var, x-loc, y-loc, 3pt, home_game
	shot_data=array(shot_data)
	# get indexes for each of the offensive/defensive player variables
	defensive_player_rows=[]
	offensive_player_rows=[]
	for player in team_players:
		defensive_player_rows.append(team_shots[0].index(player))
	for player in off_players:
		offensive_player_rows.append(team_shots[0].index(player))
	shots2=array(team_shots[1:])
	for index in defensive_player_rows:
		shot_data=numpy.hstack((shot_data,shots2[:,index].reshape(len(shots2),1)))
	for index in offensive_player_rows:
		shot_data=numpy.hstack((shot_data,shots2[:,index].reshape(len(shots2),1)))
	# so now shot_data is: def_team, dep_var, x-loc, y-loc, 3pt, home_game, dplayer1, dplayer2, ... oplayer1, oplayer2 ...
	for team in teamlist[1:]:
		team_matrix=[]
		for shot in shot_data:
			if shot[0].lower()==team.lower():
				team_matrix.append(1)
			else:
				team_matrix.append(0)
		team_matrix=array(team_matrix)
		shot_data=numpy.hstack((shot_data,team_matrix.reshape(len(team_matrix),1)))
	shot_data=shot_data[:,1:]
	# so now shot_data is: dep_var, x-loc, y-loc, 3pt, home_game, dplayer1, dplayer2, ... oplayer1, oplayer2 ... teamdummy1, teamdummy2, ...
	locations=point_matrix()
	shots_t=0
	coefficient_matrix=[]
	ses_matrix=[]
	#print shot_data[0]
	# This next part is the actual regression
	two_regions=[12,11,10,9,8,7,6,3,2,1,0]
	three_regions=[13,14,15,16,4,5]
	short_regions=[0,1]
	locations2=[[[27.5, 60], [37.5, 70], [1]]]
	for box in locations:
		x_center=box[0][0]+5
		y_center=box[0][1]+5
		print x_center,y_center
		shots_box=[shot for shot in shot_data if float(shot[1])>=x_center-5 and float(shot[1])<x_center+5 and float(shot[2])>=y_center-5 and float(shot[2])<y_center+5]
		shots_t=shots_t+len(shots_box)
		num_shots=len(shots_box)
		smooth_fg=0
		# nearest 8% routine
		if num_shots>=bin_size:
			reg_shots=numpy.float_(shots_box)
		if num_shots<bin_size:
			find_x_shots=(bin_size-num_shots)+1
			dists=[]
			if int(box[2][0]) in three_regions:
				dist_shots=[shot for shot in shot_data if float(shot[3])==1]
			if int(box[2][0]) in two_regions:
				dist_shots=[shot for shot in shot_data if float(shot[3])==0]
				if int(box[2][0]) in short_regions:
					dist_shots=[shot for shot in dist_shots if math.sqrt(float(shot[1])**2+float(shot[2])**2)<80]
				if int(box[2][0]) not in short_regions:
					dist_shots=[shot for shot in dist_shots if math.sqrt(float(shot[1])**2+float(shot[2])**2)>=80]
			dist_shots=[shot for shot in dist_shots if math.sqrt((x_center-float(shot[1]))**2+(y_center-float(shot[2]))**2)<120]
			distances=[]
			for index, shot in enumerate(dist_shots):
				dist=math.sqrt((x_center-float(shot[1]))**2+(y_center-float(shot[2]))**2)
				# print shot[1],shot[2],x_center,y_center,dist
				distances.append(dist)
			distances=numpy.float_(distances)
			dist_shots = numpy.float_(dist_shots)
			if len(dist_shots)>0:
				dist_shots=numpy.hstack((dist_shots,distances.reshape(len(distances),1)))
				sorted_dists = dist_shots[dist_shots[:,-1].argsort()]
				fill_shots=sorted_dists[0:10000]
			#except:
			#	fill_shots=[0]
			try:
				reg_shots=array([shot for shot in fill_shots])
			except:
				reg_shots=[0]
		if len(reg_shots)>=1000:
			X=array([shot[4:-1] for shot in reg_shots])	
			# Home variable will be first coefficient, [1:] will be players
			Y=array(reg_shots)[:,0]
			clf=linear_model.LinearRegression(fit_intercept=False)
			clf.fit(X,Y)
			coefficients=clf.coef_[1:]
			# code from this stackoverflow answer: http://stackoverflow.com/questions/20938154/standard-errors-for-multivariate-regression-coefficients
			MSE=numpy.mean((Y-clf.predict(X).T)**2)
			var_est=MSE*numpy.diag(numpy.linalg.pinv(numpy.dot(X.T,X)))
			SE_est=numpy.sqrt(var_est)
			# end snippet
			ses=SE_est[1:]
		if len(reg_shots)<1000:
			coefficients=[]
			ses=[]
			for player in team_players:
				coefficients.append(0)
			for player in team_players:
				ses.append(0)
		coefficient_matrix.append(coefficients)
		ses_matrix.append(ses)
	# find shot volume from each location for each player
	volume_matrix=[]
	for box in locations:
		x_center=box[0][0]+5
		y_center=box[0][1]+5
		pshots=[shot for shot in shot_data if float(shot[1])>=x_center-5 and float(shot[1])<x_center+5 and float(shot[2])>=y_center-5 and float(shot[2])<y_center+5]
		print len(pshots)
		volumes=[]
		for player in team_players:
			volumes.append(len([shot for shot in pshots if float(shot[team_players.index(player)+5])==1]))
		print volumes
		volume_matrix.append(volumes)
	final_output=[]
	# Get range effects from regression on each team_player. shots[9] is distance, shots[13] is 3pt_flag
	shot_types=[[int(shot[9]),int(shot[13])] for shot in shots[1:]]
	for index,shot in enumerate(shot_types):
		for player_index in defensive_player_rows:
			shot.append(shots[index+1][player_index])
		for player_index in offensive_player_rows:
			shot.append(shots[index+1][player_index])
			# now we have a list of all shots with: [distance,3pt,def_p1,def_p2,...]
	# get y variables: dummies for close, mid, or 3 point shot.
	y_close=[]
	y_mid=[]
	y_3=[]
	range_coefs=[]
	for shot in shot_types:
		if shot[0]<=8:
			y_close.append(1)
			y_mid.append(0)
			y_3.append(0)
		if shot[0]>8:
			y_close.append(0)
			if shot[1]==0:
				y_3.append(0)
				y_mid.append(1)
			if shot[1]==1:
				y_3.append(1)
				y_mid.append(0)
	print len(shot_types[2])
	# close regression
	Y=array(y_close).reshape(len(y_close),1)
	X=array([shot[2:] for shot in shot_types])
	clf=linear_model.LinearRegression()
	clf.fit(X,Y)
	range_coefs.append(clf.coef_)
	# mid regression
	Y=array(y_mid).reshape(len(y_mid),1)
	clf=linear_model.LinearRegression()
	clf.fit(X,Y)
	range_coefs.append(clf.coef_)
	# 3 regression
	Y=array(y_3).reshape(len(y_3),1)
	clf=linear_model.LinearRegression()
	clf.fit(X,Y)
	range_coefs.append(clf.coef_)
	# Put volume and regression coefficients together and create chart for each player
	for index, player in enumerate(team_players):
		player_chart=[]
		total_volume=0
		print volume_matrix
		for box in volume_matrix:
			total_volume=total_volume+box[index]
		for index2,box in enumerate(locations):
			output=[box[0][0],box[0][1],volume_matrix[index2][index],coefficient_matrix[index2][index],ses_matrix[index2][index]]
			player_chart.append(output)
		sorted_chart=sorted(player_chart, key=lambda place:place[2])
		sorted_chart=sorted_chart[-251:]
		sorted_chart.append([range_coefs[0][0][index],range_coefs[1][0][index],range_coefs[2][0][index]])
		with open('/Users/austinc/Desktop/Current Work/NBA/%s_coeffs_teamcepts.csv' % (player),'w') as csvfile:
			writer=csv.writer(csvfile)
			for row in sorted_chart:
				writer.writerow(row)

def blergh():
	league_geog_def()
	league_geog_def_teamcepts()

def scrape_NCAA():
	url='http://www.cbssports.com/collegebasketball/teams'
	teampage=urllib2.urlopen(url).read()
	team_finder=re.compile('<a href="/collegebasketball/teams/page/(.*?)">')
	teams=team_finder.findall(teampage)
	print teams
	all_games=[]
	for team in teams:
		url='http://www.cbssports.com/collegebasketball/teams/schedule/%s' % (team)
		print url
		games=urllib2.urlopen(url).read()
		gameid_find=re.compile('<td  align="center"><A HREF="/collegebasketball/gametracker/recap/(.*?)">')
		full_games=gameid_find.findall(games)
		for game in full_games:
			all_games.append(game)
	with open('/Users/austinc/Desktop/Current Work/NBA/NCAA_games.csv','w') as csvfile:
		writer=csv.writer(csvfile)
		for row in set(all_games):
			writer.writerow([row])

def scrape_shots_NCAA():
	with open("/Users/austinc/Desktop/Current Work/NBA/NCAA_games.csv",'rU') as csvfile:
		reader=csv.reader(csvfile)
		games=[row for row in reader]
	with open("/Users/austinc/Desktop/Current Work/NBA/NCAA_scraped_games.csv",'rU') as csvfile:
		reader=csv.reader(csvfile)
		finished_games=[row for row in reader]
	games=[game[0] for game in games]
	scraped_games=[game[0] for game in finished_games]
	newgames=[game for game in games if game not in scraped_games]
	for game in newgames:
		print game
		url='http://www.cbssports.com/collegebasketball/gametracker/live/%s' % (game)
		game_data=urllib2.urlopen(url).read()
		shot_finder=re.compile('(0|1),([0-9]{1,2}:[0-9]{2}|[0-9]{1,2}.[0-9]{1}),(1|2),([0-9]{7}),(.*?),(0|1),(.*?),(.*?),([0-9]{1,2})')
		# home,time,period,player,type,made,xpos,ypos,distance
		full_games=shot_finder.findall(game_data)
		# home,time,period,player,type,made,xpos,ypos,distance
		# 0,19:49,1,2019048,3,0,-2,39,4
		full_games=[shot for shot in full_games if shot[4]!="11" and shot[4]!="12" and shot[4]!="10" and shot[4]!="17" and shot[4]!="18" and shot[4]!="13" and shot[4]!="14" and shot[4]!="15" and shot[4]!="16"]
		player_finder=re.compile('([0-9]{7}):(.*?&nbsp;.*?),')
		players=player_finder.findall(game_data)
		# print player_finder
		shots=[]
		# three line is 20 feet, 9 inches
		for shot in full_games:
			fg="2"
			if int(shot[8])>20:
				fg="3PT Field Goal"
			if int(shot[0])==0:
				shots.append([shot[4],shot[0],shot[1],shot[2],shot[3],shot[8],shot[2],'','','','','',fg,'','','','',int(shot[6])*10,(41.75-abs(int(shot[7])))*10,'',shot[5]])
				# shot type, home or away, clock time, ???NOT SURE???, player name, "???NOT SURE???, half, blanks.... fg .... x, y, made
			if int(shot[0])==1:
				shots.append([shot[4],shot[0],shot[1],shot[2],shot[3],shot[8],shot[2],'','','','','',fg,'','','','',-int(shot[6])*10,(41.75-abs(int(shot[7])))*10,'',shot[5]])
		print players
		for shot in shots:
			for player in players:
				if player[0]==shot[4]:
					shot[4]=player[1]
		if len(shots)>0:
			print shots[0]
		with open('/Users/austinc/Desktop/Current Work/NBA/NCAA_2013-2014.csv','a') as csvfile:
			writer=csv.writer(csvfile)
			for row in shots:
				writer.writerow(row)
		with open('/Users/austinc/Desktop/Current Work/NBA/NCAA_scraped_games.csv','a') as csvfile:
			writer=csv.writer(csvfile)
			writer.writerow([game])


# # loading darryl's data
# function load_data():
# 	data=pd.read_csv('/Users/austinc/Desktop/ESPN/shots_with_lineups_2011_2012.csv')
# 	data.head()






