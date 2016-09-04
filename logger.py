# COMP3331 Assignment One
# Luke Cusack, z5078476
# August, September 2016
# Logger interface

# <snd/rcv/drop> <time> <type of packet> <seq-number> <number-of- bytes> <ack-number>


import sys, re, glob, os, datetime, time
from packet import *


# global / #define's

HOST_SENDR        = 0
HOST_RECVR        = 1

DIR_SENT          = 0
DIR_RECV          = 1
DIR_DROP          = 2

SENDR_LOG         = "Sender_log.txt"
RECVR_LOG         = "Receiver_log.txt"

STATE_INIT        = 1
STATE_CONNECTED   = 2
STATE_TEARDOWN    = 3

STATS_DIR         = 0
STATS_TIME        = 1
STATS_FLAGS       = 2
STATS_SEQ_NUM     = 3
STATS_NUM_BYTES   = 4
STATS_ACK_NUM     = 5

debug = True


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


# write to file
def log(host, time, direction, packet):
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

   #if (debug):
   #   log_entry += " - strlen: " + str(len(get_data(packet))) + "; #" + get_data(packet) + "#"

   log_entry += "\n"

   if (debug): print "LOGGER HERE. entry: \n" + log_entry

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


# transmission is completed, produce statistics
def do_stats_sendr():

   if (debug): print "[*] Producing Sender statistics"

   # sender stats:
   # - Amount of Data Transferred (in bytes)
   # - Number of Data Segments Sent (excluding retransmissions)
   # - Number of Packets Dropped (by the PLD module)
   # - Number of Packets Delayed (for the extended assignment only)
   # - Number of Retransmitted Segments
   # - Number of Duplicate Acknowledgements received

   bytes_transmitted = 0
   packets_sent      = []
   packets_dropped   = []
   packets_retrans   = []
   acks_recvd        = []
   dup_acks          = 0

   STATE             = STATE_INIT

   # read logfile, collect stats
   try:

      # ignore header lines
      logfile = open(SENDR_LOG, 'r')
      logfile.readline()
      logfile.readline()
      logfile.readline()
      logfile.readline()

      # turn each line into a list to gather stats
      for line in logfile.readlines():

         as_list = re.sub(' +', ',', line.strip()) 
         as_list = as_list.split(',')
         as_list[STATS_TIME]        = int(as_list[STATS_TIME])
         as_list[STATS_SEQ_NUM]     = int(as_list[STATS_SEQ_NUM])
         as_list[STATS_NUM_BYTES]   = int(as_list[STATS_NUM_BYTES])
         as_list[STATS_ACK_NUM]     = int(as_list[STATS_ACK_NUM])

         #print as_list

         if (as_list[STATS_DIR] == "snt"):
            if (as_list[STATS_FLAGS] == "D"):
               STATE = STATE_CONNECTED

               packets_sent.append(as_list[STATS_SEQ_NUM])
               bytes_transmitted += as_list[STATS_NUM_BYTES]

               if (as_list[STATS_SEQ_NUM] in packets_dropped):
                  packets_retrans.append(as_list[STATS_SEQ_NUM])

            elif (as_list[STATS_FLAGS] == "F"):
               STATE = STATE_TEARDOWN

         elif (as_list[STATS_DIR] == "drop"):
            packets_dropped.append(as_list[STATS_SEQ_NUM])

         elif (as_list[STATS_DIR] == "rcv"):
            if (STATE == STATE_CONNECTED):
               if (as_list[STATS_ACK_NUM] in acks_recvd):
                  dup_acks += 1
               acks_recvd.append(as_list[STATS_ACK_NUM])

         #print as_list
         #buffer += line

      logfile.close()
   except:
      print "[*] Error: couldn't open " + SENDR_LOG + " for reading"
      sys.exit()


   # write stats to logfile
   try:
      logfile = open(SENDR_LOG, 'a')
      logfile.write("\n\n")
      logfile.write("Total statistics\n")
      logfile.write(" * Bytes transmitted:       " + str(bytes_transmitted) + "\n")
      logfile.write(" * Packets sent:            " + str(len(packets_sent)) + "\n")
      logfile.write(" * Packets dropped:         " + str(len(packets_dropped)) + "\n")
      logfile.write(" * Packets retransmitted:   " + str(len(packets_retrans)) + "\n")
      logfile.write(" * Duplicate ACKs:          " + str(dup_acks) + "\n")
      logfile.close()
   except:
      print "[*] Error: couldn't open " + SENDR_LOG + " for appending"
      sys.exit()


# transmission is completed, produce statistics
def do_stats_recvr():

   if (debug): print "[*] Producing Receiver statistics"

   # receiver stats:
   # - Amount of Data Received (in bytes)
   # - Number of Data Segments Received
   # - Number of duplicate segments received (if any)

   bytes_recvd       = 0
   packets_recvd     = []
   dup_packets       = 0


   # read logfile, collect stats
   try:
      #STATE             = STATE_INIT

      # open file and ignore header lines
      logfile = open(RECVR_LOG, 'r')
      logfile.readline()
      logfile.readline()
      logfile.readline()
      logfile.readline()


      # turn each line into a list to gather stats
      for line in logfile.readlines():

         as_list = re.sub(' +', ',', line.strip()) 
         as_list = as_list.split(',')
         as_list[STATS_TIME]        = int(as_list[STATS_TIME])
         as_list[STATS_SEQ_NUM]     = int(as_list[STATS_SEQ_NUM])
         as_list[STATS_NUM_BYTES]   = int(as_list[STATS_NUM_BYTES])
         as_list[STATS_ACK_NUM]     = int(as_list[STATS_ACK_NUM])

         #print as_list

         if (as_list[STATS_DIR] == "rcv"):
            if (as_list[STATS_FLAGS] == "D"):
               #STATE = STATE_CONNECTED

               if (as_list[STATS_SEQ_NUM] in packets_recvd):
                  dup_packets += 1

               packets_recvd.append(as_list[STATS_SEQ_NUM])
               bytes_recvd += as_list[STATS_NUM_BYTES]

         #print as_list
         #buffer += line

      logfile.close()

   except:
      print "[*] Error: couldn't open " + RECVR_LOG + " for reading"
      sys.exit()


   # write statistics to logfile
   try:
      logfile = open(RECVR_LOG, 'a')
      logfile.write("\n\n")
      logfile.write("Total statistics\n")
      logfile.write(" * Bytes received:      " + str(bytes_recvd) + "\n")
      logfile.write(" * Packets received:    " + str(len(packets_recvd)) + "\n")
      logfile.write(" * Duplicate packets:   " + str(dup_packets) + "\n")
      logfile.close()
   except:
      print "[*] Error: couldn't open " + RECVR_LOG + " for appending"
      sys.exit()


