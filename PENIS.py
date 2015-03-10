#  PENIS.py 
#  Potentially Erroneous Nullsec Intelligence System 
#  EVElog parser that plays a chime when hostiles are 
#  reported in intel. 
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

# import some stuff we need
import time
from time import gmtime
import sys
import os
from datetime import datetime, timedelta, date
import re
import platform
import json

penis_dir = os.path.dirname(__file__)

# suppress nerd speak
sys.tracebacklimit = 0

# what could this be?
ver = "0.10"

# setup our log file watcher, only open it once and update when a new line is written
def hostile_watch(fn, words):
    fp = open(hostile_fn, 'r')
    while True:
        # remove null padding (lol ccp)
        new = re.sub(r'[^\x20-\x7e]', '', fp.readline())

        if new:
            for word in words:
                if word in new:
                    yield (word, new)
        else:
            time.sleep(0.5)

# query the region
region = raw_input("Enter the intel chan identifier (e.g., DEK, BRN, PBF): ")

# query the user for the system they will be in
system = raw_input("Enter the system you will be ratting in: ")

# Are we on windows or linux?
which_os = platform.system()

if which_os == "Linux":
  # Wine default path
  hostile_logdir = os.path.join( "/home", os.getenv('USER'), "EVE", "logs", "Chatlogs" )

elif which_os == "Windows":
  # Win 7 default log path
  hostile_logdir = os.path.join( "C:/", "Users", os.getenv('USERNAME'), "Documents", "EVE", "logs", "Chatlogs" )
  # extra import to play the beep
  import winsound

elif which_os == "Darwin":
  # os.getenv doesn't seem to work here...
  import getpass
  # OSX default log path
  hostile_logdir = os.path.join( "/Users", getpass.getuser(), "Library", "Application Support", "EVE Online", "p_drive", "User", "My Documents", "EVE", "logs", "Chatlogs" )

else:

  print "What fucking OS are you running?"

# select identified logs and sort by date
hostile_tmp = sorted([ f for f in os.listdir(hostile_logdir) if f.startswith('%s.CFC' % region)])
# hostile_tmp = sorted([ f for f in os.listdir(hostile_logdir) if f.startswith('Corp')])

# grab the most recent file for each log
hostile_fn = os.path.join( hostile_logdir, hostile_tmp[-1] )

print "\nPotentially Erroneous Nullsec Intelligence System v%s by QQHeresATissue\n" % (ver)

print "parsing from - \nIntel:  %s\n" % (hostile_tmp[-1])

# triggers to look for in the intel channels.  Read from json files for a specified system
# big thanks to Orestus for getting these together and suggesting the change!!
json_data = open(os.path.join( penis_dir, "systems", "%s.json" % system))

data = json.load(json_data)

hostile_words = data

json_data.close()

# ignore status requests and clr reports
status_words = [ "status", \
                 "Status", \
                 "clear", \
                 "Clear", \
                 "stat", \
                 "Stat", \
                 "clr", \
                 "Clr",
                 "EVE System" ]

# if the word matches a trigger, print the event
for hostile_hit_word, hostile_hit_sentence in hostile_watch(hostile_fn, hostile_words):
  #print "%r | %r | %r | %r" % (hostile_hit_word, hostile_fn, hostile_words, hostile_hit_sentence)

  # if someone is just asking for status, ignore the hit
  if not any(status_word in hostile_hit_sentence for status_word in status_words):
    
    # get the current time for each event
    hit_time = time.strftime('%H:%M:%S')
    # get current date/time in UTC
    utc = time.strftime('[ %Y.%m.%d %H:%M', gmtime())[:17]

    # print the alert
    print "\n%r - %r INTEL ALERT!!" % (hit_time, hostile_hit_word)
    print "%r" % (hostile_hit_sentence)

    # play a tone to get attention, only if its recent!
    if utc in hostile_hit_sentence:

      if which_os == "Linux":
        os.system("aplay -q ~/Downloads/beep.wav")
      
      elif which_os == "Windows":
        winsound.Beep(500, 500), winsound.Beep(500, 500), winsound.Beep(500, 500)

      elif which_os == "Darwin":
        print('\a')
        print('\a')
        print('\a')
