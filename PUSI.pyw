#  PUSI.py
#  Python User Servicing Interface
#  Controller script to PENIS and BALLS
#  AFK away and listen for a ding.
#
#  Written in python for you Alex....
#
# Copyright (c) 2015, QQHeresATissue <QQHeresATissue@gmail.com>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
###############################################################################

from time import gmtime
import time
from threading import *
import sys
from datetime import datetime, timedelta, date
import re
import json
import os
import platform
from utils import EVEDir

# Do initial checks, code taken from Pyfa... cause that shit rocks
if sys.version_info < (2,6) or sys.version_info > (3,0):
	print("PUSI requires python 2.7\nExiting.")
	time.sleep(10)
	sys.exit(1)

	try:
		import wxversion
	except ImportError:
		print("Cannot find wxPython\nYou can download wxPython (2.8) from http://www.wxpython.org/")
		time.sleep(10)
		sys.exit(1)
	try:
		wxversion.select('2.8')
	except wxversion.VersionError:
		try:
			wxversion.ensureMinimal('2.8')
		except wxversion.VersionError:
			print("Installed wxPython version doesn't meet requirements.\nYou can download wxPython (2.8) from http://www.wxpython.org/")
			time.sleep(10)
			sys.exit(1)
		else:
			print("wxPython 2.8 not found; attempting to use newer version, expect errors")

import wx
import wx.media

# suppress nerd speak
sys.tracebacklimit = 0

# set a version
ver = "0.7"

ID_PENIS_START = wx.NewId()
ID_BALLS_START = wx.NewId()

# Get current working direcroty
pusi_dir = os.path.dirname(__file__)

# Set wav names
hostile_sound = os.path.join( pusi_dir, "sounds", "hostile.wav")
done_sound = os.path.join( pusi_dir, "sounds", "sites_done.wav")
tags_and_ammo = os.path.join ( pusi_dir, "sounds", "cash_money.wav")

# Are we on windows or linux?
which_os = platform.system()

if which_os == "Windows":
	import winsound
	from winsound import PlaySound, SND_FILENAME

# Setup a class for text redirection
class RedirectText(object):
	def __init__(self,aWxTextCtrl):
		self.out=aWxTextCtrl

	# Write string to wx window
	def write(self,string):
		wx.CallAfter(self.out.AppendText, string)

# Main form for graphical PUSI
class pusi(wx.Frame):

	def __init__(self,parent,id):

		# Create the main window with the title PUSI <version number>
		wx.Frame.__init__(self,parent,id,'PUSI %s' % ver, size=(800,340), style = wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))

		#
		self.Bind(wx.EVT_CLOSE, self.Close)

		# Create a panel in the windows
		self.panel = wx.Panel(self)

		# Setup logging early so we see it in the panel
		logbox = wx.TextCtrl(self.panel, wx.ID_ANY, size = (780, 290), pos = (10,40), style = wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)

		# Redirect all printed messages to the panel
		redir=RedirectText(logbox)
		sys.stdout=redir
		sys.stderr=redir

		# Create a start and stop button
		self.penis_start = wx.Button(self.panel, ID_PENIS_START, label="Start PENIS", pos=(530,10), size=(90,25))
		self.balls_start = wx.Button(self.panel, ID_BALLS_START, label="Start BALLS", pos=(10, 10), size=(90,25))

		# Define regions we have systems for in a list
		region_list = [ 'dek', 'brn', 'ftn', 'fade', 'tnl', 'tri', 'vnl', 'vale' ]
		# Create text "Region" before the dropdown box
		wx.StaticText(self.panel, -1, 'Region', (105,15))

		# Create the dropdown box and use DEK as a default selection
		pusi.region_select = wx.ComboBox(self.panel, -1, pos=(150,10), size=(75,25), choices = region_list, style=wx.CB_DROPDOWN)
		pusi.region_select.SetSelection(0)

		# Load triggers from json courtesty of Orestus, Narex Vivari for adding auto complete. 
		self.load_region(pusi.region_select.GetValue());
		pusi.region_select.Bind(wx.EVT_COMBOBOX, self.region_selection_changed, pusi.region_select)

		#Create the system input box
		wx.StaticText(self.panel, -1, 'System', (230, 15))
		pusi.system_select = wx.TextCtrl(self.panel, -1, '', pos=(280,10), size=(120,-1))
		pusi.system_select.Bind(wx.EVT_TEXT, self.system_text_changed, pusi.system_select)

		# Create the range input box
		range_list = [ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10' ]
		wx.StaticText(self.panel, -1, 'Range', (410, 15))
		pusi.range_select = wx.ComboBox(self.panel, -1, '', pos=(450,10), size=(80,25), choices = range_list, style=wx.CB_DROPDOWN)
		pusi.range_select.SetSelection(5)

		# Bind button clicks to events (start|stop)
		self.Bind(wx.EVT_BUTTON, self.penis_run, id=ID_PENIS_START)
		self.Bind(wx.EVT_BUTTON, self.balls_run, id=ID_BALLS_START)

		# Set a watch variable to check later.  If we want the process to stop, self.watch becomes 1
		self.penis_watcher = None
		self.balls_watcher = None

		# Shameless self adversiting
		print "Python User Servicing Interface v%s by QQHeresATissue" % ver

	def region_selection_changed(self, event):
		self.load_region(pusi.region_select.GetValue())

	def system_text_changed(self, event):
		caret = pusi.system_select.GetInsertionPoint()
		partial = pusi.system_select.GetValue()[:caret]
		match = self.match_partial_system(partial)
		if match != None and len(partial) > 0:
			pusi.system_select.ChangeValue(match)
		else:
			pusi.system_select.ChangeValue(partial)
		pusi.system_select.SetInsertionPoint(caret)

	def match_partial_system(self, text):
		for system in pusi.current_region:
			if system['name'].startswith(text):
				return system['name']
		return None

	def load_region(self, region):
		json_data = open(os.path.join( pusi_dir, "regions", "%s.json" % str(region)))
		pusi.current_region = json.load(json_data)
		json_data.close()

	# Setup a functions to start the watcher thread
	def penis_run(self, event):
		if not self.penis_watcher:
			self.penis_watcher = StartPENIS(self)

	def balls_run(self, event):
		if not self.balls_watcher:
			self.balls_watcher = StartBALLS(self)

	def Close(self, event):
		self.Destroy()

# Define watcher thread
class StartPENIS(Thread):

	def __init__(self, threadID):
		Thread.__init__(self)
		# Kill the thread when the main process is exited
		self.daemon = True
		self.threadID = threadID
		self._want_abort = 0
		self.start()

	# setup our log file watcher, only open it once and update when a new line is written
	def hostile_watch(self, logfile):

		fp = open(logfile, 'r')
		while True:

			# remove null padding (lol ccp)
			new = re.sub(r'[^\x20-\x7e]', '', fp.readline())

			if new:
				relevant_system = self.find_system_in_string(new)
				if relevant_system:
					yield (relevant_system, new)
			else:
				time.sleep(0.01)

	# Start the main thread for alerting
	def run(self):

		print "Starting the Potentially Erroneous Nullsec Intelligence System"

		hostile_logdir = EVEDir.chat_logs

		# get region based on our dropdown box selection
		region = pusi.region_select.GetValue()
		# get the system based on our system input
		system = pusi.system_select.GetValue()

		# select identified logs and sort by date
		hostile_tmp = sorted([ f for f in os.listdir(hostile_logdir) if f.startswith("%s.imperium" % str(region))])
		# testing line so we shit up Corp chat not intel chans
		# hostile_tmp = sorted([ f for f in os.listdir(hostile_logdir) if f.startswith('Corp')])

		# grab the most recent file for each log
		logfile = os.path.join( hostile_logdir, hostile_tmp[-1] )

		# ignore status requests and clr reports
		status_words = [ "status",
						"Status",
						"clear",
						"Clear",
						"stat",
						"Stat",
						"clr",
						"Clr",
						"EVE System" ]

		# Print some initial info lines
		print "parsing from - Intel:  %s\n" % (hostile_tmp[-1])

		# if the word matches a trigger, move on
		for related_system, hostile_hit_sentence in self.hostile_watch(logfile):
			#print "%r | %r | %r | %r" % (related_system, self.hostile_words, hostile_hit_sentence)

			# if someone is just asking for status, ignore the hit
			if not any(status_word in hostile_hit_sentence for status_word in status_words):

				# find distance to the reported system
				distance = self.find_system_distance(system, related_system, int(pusi.range_select.GetValue()))
				if distance != None:

					# get the current time for each event
					hit_time = time.strftime('%H:%M:%S')
					# get current date/time in UTC
					utc = time.strftime('[ %Y.%m.%d %H:%M', gmtime())[:17]

					# print the alert
					if which_os == "Windows":
						print "%s - PENIS INTEL ALERT!!\n" % (hit_time)
						print "%r (%s jumps)\n" % (hostile_hit_sentence, distance)
						wx.Yield()
					else:
						print "%s - PENIS INTEL ALERT!!" % (hit_time)
						print "%r (%s jumps)\n" % (hostile_hit_sentence, distance)
						wx.Yield()

					# play a tone to get attention, only if its recent!
					if utc in hostile_hit_sentence:

						if which_os == "Linux":
							os.system("aplay -q %r" % hostile_sound)

						elif which_os == "Windows":
							winsound.PlaySound("%s" % hostile_sound,SND_FILENAME)

						elif which_os == "Darwin":
							print('\a')
							print('\a')
							print('\a')

	def find_system_in_string(self, string):
		for system in pusi.current_region:
			if system['name'] in string:
				return system['name']

		return None

	def find_system_distance(self, start_system, dest_system, range):
		routes_found = []
		# find the distance of all routes from start system to destination system
		self.system_distance_recursive(start_system, dest_system, 0, range, [], routes_found)
		# return shortest path
		return min(routes_found) if len(routes_found) else None

	def system_distance_recursive(self, cur_system, dest_system, distance, range, checked, routes_found):
		# exit if out of range or system is already checked
		if distance > range or cur_system in checked:
			return

		if cur_system == dest_system:
			# destination found, so we don't need to check further connections
			routes_found.append(distance)
			return

		for connected_system in self.get_connected_systems(cur_system):
			# duplicate existing path and append this system
			now_checked = list(checked)
			now_checked.append(cur_system)
			# recursively find distance, if a path exists
			conn_dist = self.system_distance_recursive(connected_system, dest_system, distance + 1, range, now_checked, routes_found)
			if conn_dist >= 0:
				# this system is parth of a path to destination, so add the distance
				routes_found.append(conn_dist)

	def get_connected_systems(self, system):
		# find the system and return its connections. can easily be optimized using a dict if performance is an issue (which it shouldn't be when only checking regions)
		system_data = [x['connections'] for x in pusi.current_region if x['name'] == system]
		# connections across regions exist in the data, but are currently not supported. but people probably don't report cross-region intel anyway
		return system_data[0] if len(system_data) > 0 else []

# Define BALLS watcher thread
class StartBALLS(Thread):

	def __init__(self, threadID):
		Thread.__init__(self)
		# Kill the thread when the main process is exited
		self.daemon = True
		self.threadID = threadID
		self._want_abort = 0
		self.start()

	# setup our log file watcher, only open it once and update when a new line is written
	def balls_watch(self, fn, words):
		done_count = 0

		fp = open(fn, 'r')
		while True:
			new = fp.readline()

			if new:
				done_count = 0
				for word in words:
					if word in new:
						yield (word, new)
			else:
				done_count = done_count + 1
				if done_count > 129:
					print "BALLS Notification"
					print "%r - Sites done (or something is wrong)\n" % (time.strftime('%H:%M:%S'))

					if which_os == "Linux":
						os.system("aplay -q %r" % done_sound)

					elif which_os == "Windows":
						winsound.PlaySound("%s" % done_sound,SND_FILENAME)

					elif which_os == "Darwin":
						print('\a')
						print('\a')
						print('\a')

					done_count = 0

				time.sleep(0.5)

	def run(self):
		count = 0

		logdir = EVEDir.game_logs

		# sort by date
		tmp = sorted([ f for f in os.listdir(logdir) if f.startswith('201')])

		# grab the most recent file
		fn = os.path.join( logdir, tmp[-1] )

		print "\nStarting the Background Alert for Lucrative Loot Script"

		print "parsing from %s\n" % tmp[-1]

		# triggers to look for in the log file
		words = [ "Dread Guristas",
				"Dark Blood",
				"True Sansha",
				"Shadow Serpentis",
				"Sentient",
				"Domination"
				"Estamel Tharchon",
				"Vepas Minimala",
				"Thon Eney",
				"Kaikka Peunato",
				"Gotan Kreiss",
				"Hakim Stormare",
				"Mizuro Cybon",
				"Tobias Kruzhor",
				"Ahremen Arkah",
				"Draclira Merlonne",
				"Raysere Giant",
				"Tairei Namazoth",
				"Brokara Ryver",
				"Chelm Soran",
				"Selynne Mardakar",
				"Vizan Ankonin",
				"Brynn Jerdola",
				"Cormack Vaaja",
				"Setele Schellan",
				"Tuvan Orth",
				"Warp scramble attempt" ]

		# Don't trigger if we are accepting or getting a contract
		false_pos = [ "following items",
					"question" ]

		for hit_word, hit_sentence in self.balls_watch(fn, words):

			if not any(false_word in hit_sentence for false_word in false_pos):

				if count < 1:
					count = count + 1
					# log the combat lines involving the spawn
					print "BALLS ALERT!!"
					print "%r - %r\n" % (time.strftime('%H:%M:%S'), hit_word)
					wx.Yield()
					# debug statement
					# print "%r" % (hit_sentence)

					# play a tone to get attention
					if which_os == "Linux":
						os.system("aplay -q %r" % tags_and_ammo)

					elif which_os == "Windows":
						winsound.PlaySound("%s" % tags_and_ammo,SND_FILENAME)

					elif which_os == "Darwin":
						print('\a')
						print('\a')
						print('\a')

					else:
						print "What fucking system are you running?"
						break

				elif count == 30:
					count = 0
					continue
				else:
					count = count + 1
					continue

if __name__ == '__main__':
	app=wx.App()
	frame=pusi(parent=None,id=-1)
	frame.Show()
	app.MainLoop()
