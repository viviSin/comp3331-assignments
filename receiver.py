# COMP3331 Assignment One
# Luke Cusack, z5078476
# August, September 2016
# RTP over UDP: receiver.py

# Usage: python receiver.py <receiver port> <filename>


import sys, socket, logger, time
from packet import *


# globals/psuedo "#defines"
STATE_INACTIVE       = 0
STATE_INIT           = 1
STATE_CONNECTED      = 2
STATE_TEARDOWN       = 3

HOST_SENDR           = 0
HOST_RECVR           = 1

DIR_SENT             = 0
DIR_RECV             = 1
DIR_DROP             = 2

# global variables
debug                = True
receiver_state       = STATE_INACTIVE
receiver_syn_acc     = 0
receiver_ack_acc     = 0
receiver_start_time  = 0
host                 = HOST_RECVR


def main():

   global receiver_state
   global host
   global receiver_start_time

   if (debug): print "receiver state: " + str(receiver_state)

   if (not debug):
      # defensive programming-- validating arguments
      if (len(sys.argv) != 3):
         sys.exit("usage: python receiver.py <receiver port> <filename>")

      if (not sys.argv[1].isdigit()):
         sys.exit("usage: python receiver.py <receiver port> <filename>")

      receiver_host        = "localhost"
      receiver_port        = sys.argv[1]
      receiver_filename    = sys.argv[2]

   else:
      receiver_host        = "localhost"
      receiver_port        = 7999
      receiver_filename    = "wot-out"



   receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   receiver.bind((receiver_host, receiver_port))

   while True:
      data, sender = receiver.recvfrom(receiver_port)
      p = eval(data)
   
      if (receiver_state == STATE_INACTIVE):
         print "RESETTING START TIME"
         receiver_start_time = time.time()

      logger.log(host, current_time(), DIR_RECV, p)


      sender_host = sender[0]
      sender_port = sender[1]

      if (debug): print "[*] data received! #" + data + "#"
      if (debug): print "\tfrom: " + str(sender)
      if (debug): print "\tstate: " + str(receiver_state)
      if (debug): print ""


      if (receiver_state == STATE_INACTIVE):
         # receive first handshake packet, send response

         if (is_syn(p) and get_seq_num(p) == 0 and get_ack_num(p) == 0):

            p = create_packet()
            p = set_syn(p)
            p = set_ack(p)
            p = set_seq_num(p, 0)
            p = set_ack_num(p, 1)

            receiver.sendto(str(p), (sender_host, sender_port))
            logger.log(host, current_time(), DIR_SENT, p)

            receiver_state = STATE_INIT

            if (debug): print "handshake #2: R -> S"

      elif (receiver_state == STATE_INIT):
         # received 3rd and last handshake packet
         # state is now considered "connected"

         if (is_ack(p) and get_seq_num(p) == 1 and get_ack_num(p) == 1):
            receiver_state = STATE_CONNECTED
            print "[*] connected to " + sender_host + ":" + str(sender_port)

      elif (receiver_state == STATE_CONNECTED):
   
         if (is_data(p)):
            # get data out of packet
            # write to file
            # send ACK

            buffer = get_data(p)
            append_to_file(receiver_filename, buffer)

            seq_num = get_seq_num(p)

            p = create_packet()
            p = set_ack(p)
            p = set_ack_num(p, seq_num + 1)

            receiver.sendto(str(p), (sender_host, sender_port))
            logger.log(host, current_time(), DIR_SENT, p)

         if (is_fin(p)):
            if (debug): print "teardown (R): FIN received. sending ACK"
            
            # send ACK packet
            p = create_packet()
            p = set_ack(p)

            receiver.sendto(str(p), (sender_host, sender_port))
            logger.log(host, current_time(), DIR_SENT, p)

            receiver_state = STATE_TEARDOWN

            # send FIN packet
            p = create_packet()
            p = set_fin(p)

            receiver.sendto(str(p), (sender_host, sender_port))
            logger.log(host, current_time(), DIR_SENT, p)

      elif (receiver_state == STATE_TEARDOWN):

         if (is_ack(p)):
            # teardown complete
            receiver_state = STATE_INACTIVE

            # rdt finish, generate statistics
            logger.do_stats_recvr()

            if (debug): print "teardown (R): last packet received. teardown complete. state -> INACTIVE"


## helper functions


# append buffer to file
def append_to_file(filename, buffer):
   try:
      file_descriptor = open(filename, "a")
      file_descriptor.write(buffer)
      file_descriptor.close()
   except:
      sys.exit("[*] fatal: append to file exception to " + filename)

   return buffer


# get current time elapsed
def current_time():
   diff = (time.time() - receiver_start_time) * 1000
   if (debug): print "CURRENT TIME CALLED: " + str(int(diff))
   if (debug): print "\t" + (str(time.time())) + " - " + str(receiver_start_time)
   return int(diff)

main()
