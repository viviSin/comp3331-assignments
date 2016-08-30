# COMP3331 Assignment One
# Luke Cusack, z5078476
# August 2016
# RTP over UDP: receiver.py

# Usage: python receiver.py <receiver port> <filename>


import sys, socket, logger
from packet import *


# globals/psuedo "#defines"
STATE_INACTIVE    = 0
STATE_INIT        = 1
STATE_CONNECTED   = 2
STATE_TEARDOWN    = 3

# global variables
debug             = True
receiver_state    = STATE_INACTIVE
receiver_logfile  = "Receiver_log.txt"
receiver_syn_acc  = 0
receiver_ack_acc  = 0


def main():

   global receiver_state
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



   #print "port: #" + str(receiver_port) + "#"
   #print "filename: #" + receiver_filename + "#"

   receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   receiver.bind((receiver_host, receiver_port))

   while True:
      data, sender = receiver.recvfrom(receiver_port)
      p = eval(data)

      sender_host = sender[0]
      sender_port = sender[1]

      if (debug): print "[*] data received! #" + data + "#"
      if (debug): print "\tfrom: " + str(sender)
      if (debug): print "\tstate: " + str(receiver_state)
      if (debug): print ""

      #sender_port = get_src_port(p)
      #print sender_host
      #print sender_port


      if (receiver_state == STATE_INACTIVE):
         # receive first handshake packet, send response

         #if (debug): print "(inactive state)"
         if (is_syn(p) and get_syn_num(p) == 0 and get_ack_num(p) == 0):

            # sender_port = int(get_src_port(p))

            p = create_packet()
            p = set_syn(p)
            p = set_ack(p)
            p = set_syn_num(p, 0)
            p = set_ack_num(p, 1)

            receiver.sendto(str(p), (sender_host, sender_port))
            receiver_state = STATE_INIT

            if (debug): print "handshake #2: R -> S"

      elif (receiver_state == STATE_INIT):
         # received 3rd and last handshake packet
         # state is now considered "connected"

         if (is_ack(p) and get_syn_num(p) == 1 and get_ack_num(p) == 1):
            receiver_state = STATE_CONNECTED
            print "[*] connected to " + sender_host + ":" + str(sender_port)

      elif (receiver_state == STATE_CONNECTED):
   
         if (is_fin(p)):
            if (debug): print "teardown (R): FIN received. sending ACK"
            
            # send ACK packet
            p = create_packet()
            p = set_ack(p)

            receiver.sendto(str(p), (sender_host, sender_port))
            receiver_state = STATE_TEARDOWN

            # send FIN packet
            p = create_packet()
            p = set_fin(p)

            receiver.sendto(str(p), (sender_host, sender_port))

      elif (receiver_state == STATE_TEARDOWN):
         if (is_ack(p)):
            receiver_state = STATE_INACTIVE
            if (debug): print "teardown (R): last packet received. teardown complete. state -> INACTIVE"

main()
