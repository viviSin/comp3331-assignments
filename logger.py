# COMP3331 Assignment One
# Luke Cusack, z5078476
# August, September 2016
# Logger interface

# <snd/rcv/drop> <time> <type of packet> <seq-number> <number-of- bytes> <ack-number>


import sys, glob, os, datetime, time
from packet import *


# global / #define's
HOST_SENDR  = 0
HOST_RECVR  = 1

DIR_SENT = 0
DIR_RECV = 1
DIR_DROP = 2

SENDR_LOG   = "Sender_log.txt"
RECVR_LOG   = "Receiver_log.txt"


#def current_time():
#   diff = (time.time() - logger_start_time) * 1000
#   return int(diff)


# if any log files exist, rename them to back them up
# create new logfiles
def create_new():
   result = glob.glob(SENDR_LOG)
   result += glob.glob(RECVR_LOG)

   if (len(result) > 0):
      print "[*] Previous logfiles detected. Backing up.."

      for f in result:
         mtime = os.path.getctime(f)
         mtime_readable = datetime.datetime.fromtimestamp(mtime)   
         filename_split = f.split('.', 2)
         new_filename = str(filename_split[0]) + " " + str(mtime_readable) + ".txt"
         print "\t" + f.ljust(20) + " -> ".ljust(7) + new_filename
         os.rename(f, new_filename)
      
      print ""

   try:
      ctime_readable = datetime.datetime.fromtimestamp(time.time())

      logfile = open(SENDR_LOG,'w')
      logfile.write("Sender log file created @ " + str(ctime_readable))
      logfile.write("\n\n")
      logfile.write("dir   time   flags seq  bytes ack\n")
      logfile.write("---------------------------------\n")
      logfile.close()

      logfile = open(RECVR_LOG,'w')
      logfile.write("Receiver log file created @ " + str(ctime_readable))
      logfile.write("\n\n")
      logfile.write("dir   time   flags seq  bytes ack\n")
      logfile.write("---------------------------------\n")
      logfile.close()

   except:
      print "[*] Error in creating new logfiles"
      sys.exit(0)

   print "[*] New logfiles created"

   #global logger_start_time
   #logger_start_time = time.time()


# write to file
def log(host, time, direction, packet):
#def log(host, direction, packet):
   global DIR_SENT
   global HOST_SENDR
   global HOST_RECVR

   if (direction == DIR_SENT):
      direction = "snt"
   elif (direction == DIR_RECV):
      direction = "rcv"
   elif (direction == DIR_DROP):
      direction = "drop"

   log_entry = direction.ljust(6)
   log_entry += str(time).ljust(7)
   log_entry += get_flags(packet).ljust(6)
   log_entry += str(get_seq_num(packet)).ljust(5)
   log_entry += str(len(get_data(packet))).ljust(6)
   log_entry += str(get_ack_num(packet))
   log_entry += "\n"

   print "LOGGER HERE. entry: \n" + log_entry

   # dir  time   flg seq bytes ack
   # snd  34.335 S   121 0  0
   # rcv  34.4   SA  154 0  122
   # snd  34.54  A   122 0  155
   # snd  34.57  D   122 56 155

   if (host == HOST_SENDR):
      try:
         logfile = open(SENDR_LOG, 'a')
         logfile.write(log_entry)
         logfile.close()
      except:
         print "[*] Error: couldn't open " + SENDR_LOG + " for appending"
         sys.exit()


   elif (host == HOST_RECVR):
      try:
         logfile = open(RECVR_LOG, 'a')
         logfile.write(log_entry)
         logfile.close()
      except:
         print "[*] Error: couldn't open " + RECVR_LOG + " for appending"
         sys.exit()


   else:
      print "[*] Error: Unknown host to record log as"
      sys.exit()


# transmission is completed, produce the statistics
def do_stats_sendr():
# sender stats:
# - Amount of Data Transferred (in bytes)
# - Number of Data Segments Sent (excluding retransmissions)
# - Number of Packets Dropped (by the PLD module)
# - Number of Packets Delayed (for the extended assignment only)
# - Number of Retransmitted Segments
# - Number of Duplicate Acknowledgements received
   #global SENDR_LOG
   #global RECVR_LOG

   bytes_transmitted = 0
   packets_sent       = 0
   packets_dropped   = 0
   #packets_delayed   = 0
   packets_retrans   = 0
   dup_acks          = 0

   try:
      logfile = open(SENDR_LOG, 'a')
      logfile.write("\n\n")
      logfile.write("Total statistics\n")
      logfile.write("Bytes transmitted:     " + str(bytes_transmitted) + "\n")
      logfile.write("Packets sent:          " + str(packets_sent) + "\n")
      logfile.write("Packets dropped:       " + str(packets_dropped) + "\n")
      logfile.write("Packets transmitted:   " + str(packets_retrans) + "\n")
      logfile.write("Duplicate ACKs:        " + str(dup_acks) + "\n")
      logfile.close()
   except:
      print "[*] Error: couldn't open " + SENDR_LOG + " for appending"
      sys.exit()


# transmission is completed, produce the statistics
def do_stats_recvr():
   bytes_recvd       = 0
   packets_recvd     = 0
   dup_packets       = 0

   try:
      logfile = open(RECVR_LOG, 'a')
      logfile.write("\n\n")
      logfile.write("Total statistics\n")
      logfile.write("Bytes received:      " + str(bytes_recvd) + "\n")
      logfile.write("Packets received:    " + str(packets_recvd) + "\n")
      logfile.write("Duplicate packets:   " + str(dup_packets) + "\n")
      logfile.close()
   except:
      print "[*] Error: couldn't open " + RECVR_LOG + " for appending"
      sys.exit()


# receiver stats:
# - Amount of Data Received (in bytes)
# - Number of Data Segments Received
# - Number of duplicate segments received (if any)
