# COMP3331 Assignment One
# Luke Cusack, z5078476
# August, September 2016
# RTP over UDP: sender.py

# usage: python sender.py receiver_host_ip receiver_port file.txt MWS MSS timeout pdrop seed


import sys, time, timeit, socket, logger, random, PLD
from packet import *


# globals/psuedo "#defines"
STATE_FINISHED    = -1
STATE_INACTIVE    = 0
STATE_INIT        = 1
STATE_CONNECTED   = 2
STATE_TEARDOWN    = 3

HOST_SENDR        = 0
HOST_RECVR        = 1

DIR_SENT          = 0
DIR_RECV          = 1
DIR_DROP          = 2

# global variables
debug             = True
sender_state      = STATE_INACTIVE
sender_start_time = 0
host              = HOST_SENDR


def main():
   
   global sender_start_time
   global host

   if (not debug):

      # defensive programming-- validating arguments
      if (len(sys.argv) != 9):
         sys.exit("usage: python sender.py receiver_host_ip receiver_port file.txt MWS MSS timeout pdrop seed")

      if (not sys.argv[2].isdigit()) or (not sys.argv[2].isdigit()) or (not sys.argv[2].isdigit()) or (not sys.argv[2].isdigit()) or (not sys.argv[2].isdigit()):
         sys.exit("usage: python sender.py receiver_host_ip receiver_port file.txt MWS MSS timeout pdrop seed")

      receiver_host	   = sys.argv[1]
      receiver_port	   = sys.argv[2]
      sender_filename	= sys.argv[3]
      sender_mws	      = sys.argv[4]
      sender_mss	      = sys.argv[5]
      sender_timeout	   = sys.argv[6]
      sender_pdrop	   = sys.argv[7]
      sender_seed	      = sys.argv[8]

   else:
      receiver_host	   = "localhost"
      receiver_port	   = 7999
      sender_filename	= "wot"
      sender_mws	      = 5
      sender_mss	      = 2
      sender_timeout	   = 3
      sender_pdrop	   = 0
      sender_seed	      = time.time()


   # seed
   random_seed = random.seed(sender_seed)


   # catch current time
   sender_start_time = time.time()


   # initialise log files
   logger.create_new()
   

   # create socket
   receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   receiver.settimeout(sender_timeout)


   # perform handshake
   handshake(receiver, receiver_host, receiver_port, sender_timeout)
   check_state(STATE_CONNECTED, "could not handshake")


   # read file, perform rdt
   buffer = read_file(sender_filename)
   rdt(receiver, receiver_host, receiver_port, buffer, sender_mss, sender_mws, sender_timeout, random_seed, sender_pdrop)


   # teardown connection
   teardown(receiver, receiver_host, receiver_port)
   check_state(STATE_FINISHED, "could not teardown")


   # generate final statistics
   logger.do_stats_sendr()

   print "\ndone. goodbye"


# perform three-way handshake
def handshake(receiver, receiver_host, receiver_port, sender_timeout):
   global sender_state

   check_state(STATE_INACTIVE, "trying to connect when state != inactive")

   # create packet
   p = create_packet()
   p = set_syn(p)

   # send SYN packet
   receiver.sendto(str(p), (receiver_host, receiver_port))
   logger.log(host, current_time(), DIR_SENT, p)
   sender_state = STATE_INIT

   if (debug): print "handshake #1 sent"

   try:
      response, addr = receiver.recvfrom(1024)
      p = eval(response)
      logger.log(host, current_time(), DIR_RECV, p)

      if (debug): print "response received: #" + response + "#"

      if (is_syn(p) and is_ack(p) and get_seq_num(p) == 0 and get_ack_num(p) == 1):
         p = create_packet()
         p = set_ack(p)
         p = set_seq_num(p, 1)
         p = set_ack_num(p, 1)

         # send 3rd packet: ACK (with no payload data)
         receiver.sendto(str(p), (receiver_host, receiver_port))
         logger.log(host, current_time(), DIR_SENT, p)
         sender_state = STATE_CONNECTED

         print "[*] connected to " + receiver_host + ":" + str(receiver_port)

      else:
         print "[*] handshake error, response: " + response
         sys.exit()

   except socket.timeout:
      print "[*] timed out. could not connect to " + receiver_host + ":" + str(receiver_port)
      sys.exit()



# open/read file
def read_file(filename):

   try:
      file_descriptor = open(filename, "r")
      buffer = file_descriptor.read()
      file_descriptor.close()
   except:
      sys.exit("fatal: no such file " + filename + " " + e)

   return buffer


# perform reliable data transfer
def rdt(receiver, receiver_host, receiver_port, buffer, sender_mss, 
   sender_mws, sender_timeout, seed, sender_pdrop):

   global debug
   file_sent      = False
   window         = []
   window_base    = 0
   next_segment   = 0

   while (file_sent == False):
      # fill window, send packets
      # wait for responses
      # receive ACKs, remove from window, inc window base

      # fill window up to MWS, send packets
      while (len(window) < sender_mws) and (next_segment < len(buffer)):

         next_segment = window_base + (sender_mss * len(window))

         if (next_segment < len(buffer)):
            window.append(next_segment)

            # send packet
            p = new_data_packet(buffer, next_segment, sender_mss)
            PLD.handle(receiver, p, current_time(), receiver_host, receiver_port, seed, sender_pdrop)

      
      # wait for ACKs
      try:
         response, addr = receiver.recvfrom(1024)
         p = eval(response)
         logger.log(host, current_time(), DIR_RECV, p)

         if (debug): print "response received: #" + response + "#"

         # get ACK num, remove from window
         if (is_ack(p)):
            ack_num = get_ack_num(p)

            if (ack_num >= len(buffer)):
               file_sent = True
            else:
               i = 0

               while (i < len(window)):
                  if (window[i] < ack_num):
                     del window[i]
                  i += 1

               # get new base
               window_base = window[0]

         else:
            if (debug): print "[*] error: received non-ack packet during rdt"

      except socket.timeout:

         print "[*] timed out. resend window to " + receiver_host + ":" + str(receiver_port)

         i = 0

         # resend all packets in the window
         while (i < len(window)):
            p = new_data_packet(buffer, window[i], sender_mss)
            PLD.handle(receiver, p, current_time(), receiver_host, receiver_port, seed, sender_pdrop)
            i += 1;


# teardown connection
def teardown(receiver, receiver_host, receiver_port):
   global sender_state

   sender_seq_acc = 0
   sender_ack_acc = 0

   check_state(STATE_CONNECTED, "trying to teardown when state != connected")

   p = create_packet()
   p = set_fin(p) 
   p = set_seq_num(p, sender_seq_acc)
   p = set_ack_num(p, sender_ack_acc)

   # send FIN packet
   receiver.sendto(str(p), (receiver_host, receiver_port))
   logger.log(host, current_time(), DIR_SENT, p)
   sender_state = STATE_TEARDOWN

   if (debug): print "teardown #1 sent"

   while (sender_state != STATE_FINISHED):
      
      try:
         response, addr = receiver.recvfrom(1024)
         p = eval(response)
         logger.log(host, current_time(), DIR_RECV, p)

         if (debug): print "response received: #" + response + "#"


         # receive ACK packet from sender
         # no response to be given. wait for sender's FIN packet
         if (sender_state == STATE_TEARDOWN and is_ack(p) and 
            not is_syn(p) and not is_fin(p) and not is_data(p)):

            sender_state = STATE_INACTIVE
            print "[*] teardown complete " + receiver_host + ":" + str(receiver_port)
            
            if (debug): print "teardown (S): received ACK from sender. state -> INACTIVE"

         # received FIN packet from sender
         # send ACK, move state to STATE_FINISHED
         elif (sender_state == STATE_INACTIVE and is_fin(p) and 
            not is_syn(p) and not is_ack(p) and not is_data(p)):

            p = create_packet()
            p = set_ack(p)
            p = set_seq_num(p, sender_seq_acc)
            p = set_ack_num(p, sender_ack_acc)

            receiver.sendto(str(p), (receiver_host, receiver_port))
            logger.log(host, current_time(), DIR_SENT, p)
            sender_state = STATE_FINISHED

            if (debug): print "teardown (S): received last packet (FIN\
               from sender). state -> FINISHED"
            
         else:
            print "[*] teardown error. state: " + str(sender_state) + ", response: " + response
            sys.exit()

      except socket.timeout:
         print "[*] timed out. could not teardown " + receiver_host + ":" + str(receiver_port)
         sys.exit()


## helper functions


# get current time elapsed
def current_time():
   diff = (time.time() - sender_start_time) * 1000
   return int(diff)


# check current state against expected state
def check_state(state, error_msg):
   if (sender_state != state):
      print "[*] error: sender state != " + str(state) + ". " + error_msg
      sys.exit()


# create new data packet
def new_data_packet(buffer, next_segment, mss):
   p = create_packet()
   p = set_seq_num(p, next_segment)
   p = set_data(p)

   if ((next_segment + mss) < len(buffer)):
      p = add_data(p, buffer[next_segment:next_segment+mss])
   else:
      p = add_data(p, buffer[next_segment:])

   return p


# call main
main()
