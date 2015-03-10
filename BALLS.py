#  BALLS.py by QQHeresATissue
#  Background Alert for Lucrative Loot Script 
#
#  EVE log parser that plays a chime
#  when a rare rat deals damage to you.
#  AFK away and listen for ding.
#
#  Written in python for you Alex....
#
#########################################

import time
import sys
import os
from datetime import datetime, timedelta, date
import platform

count = 0

ver = "0.8"

# setup our log file watcher, only open it once and update when a new line is written
def watch(fn, words):
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
              print "%r - Sites done (or something is wrong)" % (time.strftime('%H:%M:%S'))
              
              if which_os == "Linux":
                os.system("aplay -q ~/Downloads/sites_done.wav")
      
              elif which_os == "Windows":
                winsound.Beep(750, 500), winsound.Beep(750, 500)

              elif which_os == "Darwin":
                print('\a')
                print('\a')
                print('\a')

              done_count = 0
            time.sleep(0.5)


# Are we on windows or linux?
which_os = platform.system()

if which_os == "Linux":
  # Wine default path
  logdir = os.path.join( "/home", os.getenv('USER'), "EVE", "logs", "Gamelogs" )

elif which_os == "Windows":
  # Win 7 default log path
  logdir = os.path.join( "C:/", "Users", os.getenv('USERNAME'), "Documents", "EVE", "logs", "Gamelogs" )
  # extra import to play the beep
  import winsound

elif which_os == "Darwin":
  # os.getenv doesn't seem to work here...
  import getpass
  # OSX default log path
  hostile_logdir = os.path.join( "/Users", getpass.getuser(), "Library", "Application Support", "EVE Online", "p_drive", "User", "My Documents", "EVE", "logs", "Chatlogs" )

else:

  print "What fucking OS are you running?"

# sort by date
tmp = sorted([ f for f in os.listdir(logdir) if f.startswith('201')])

# grab the most recent file
fn = os.path.join( logdir, tmp[-1] )

print "\nBackground Alert for Lucrative Loot Script v%s by QQHeresATissue\n" % (ver)

print "parsing from %s" % tmp[-1]

# triggers to look for in the log file
words = [ "Dread Guristas", \
          "Dark Blood", \
          "True Sansha", \
          "Shadow Serpentis", \
          "Sentient", \
          "Domination",\
          "Estamel Tharchon", \
          "Vepas Minimala", \
          "Thon Eney", \
          "Kaikka Peunato", \
          "Gotan Kreiss", \
          "Hakim Stormare",\
          "Mizuro Cybon", \
          "Tobias Kruzhor", \
          "Ahremen Arkah", \
          "Draclira Merlonne", \
          "Raysere Giant",\
          "Tairei Namazoth", \
          "Brokara Ryver", \
          "Chelm Soran", \
          "Selynne Mardakar", \
          "Vizan Ankonin", \
          "Brynn Jerdola",\
          "Cormack Vaaja", \
          "Setele Schellan", \
          "Tuvan Orth", \
          "Warp scramble attempt" ]

false_pos = [ "following items", \
              "question" ]

for hit_word, hit_sentence in watch(fn, words):

  if not any(false_word in hit_sentence for false_word in false_pos):

    if count < 1:
      count = count + 1
      # log the combat lines involving the spawn
      print "%r - %r ALERT!!" % (time.strftime('%H:%M:%S'), hit_word)
      # debug statement
      # print "%r" % (hit_sentence)
     
      # play a tone to get attention
      if which_os == "Linux":
        os.system("aplay -q ~/Downloads/beep.wav")
      
      elif which_os == "Windows":
        winsound.Beep(500, 500), winsound.Beep(500, 500), winsound.Beep(500, 500)

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
