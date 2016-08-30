
# COMP3331 Assignment One
# Luke Cusack, z5078476
# August 2016
# RTP over UDP: sender.py

# usage: python sender.py receiver_host_ip receiver_port file.txt MWS MSS timeout pdrop seed


import sys, getopt, socket, logger
from packet import *


# globals/psuedo "#defines"
STATE_FINISHED    = -1
STATE_INACTIVE    = 0
STATE_INIT        = 1
STATE_CONNECTED   = 2
STATE_TEARDOWN    = 3

# global variables
debug             = True
sender_state      = STATE_INACTIVE
sender_logfile    = "Sender_log.txt"
sender_syn_acc    = 0
sender_ack_acc    = 0


def main():

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
      sender_mws	      = -1
      sender_mss	      = 1
      sender_timeout	   = 3
      sender_pdrop	   = -1
      sender_seed	      = -1

   # create socket
   receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   receiver.settimeout(sender_timeout)


   # perform handshake
   handshake(receiver, receiver_host, receiver_port, sender_timeout)
   check_state(STATE_CONNECTED, "could not handshake")

   #if (sender_state != STATE_CONNECTED):
   #   print "[*] could not connect to " + receiver_host + ":" + str(receiver_port)
   #   sys.exit()

   # read file, perform rdt
   # buffer = readFile(sender_filename)
   #rdt(receiver, receiver_host, receiver_port, buffer, sender_mss, sender_timeout)

   teardown(receiver, receiver_host, receiver_port)
   check_state(STATE_FINISHED, "could not teardown")

   #if (state != STATE_INACTIVE):
   #   print "[*] could not teardown"
   #   sys.exit

   print "\ndone. goodbye"

def teardown(receiver, receiver_host, receiver_port):
   global sender_state
   global sender_syn_acc
   global sender_ack_acc

   check_state(STATE_CONNECTED, "trying to teardown when state != connected")

   p = create_packet()
   p = set_fin(p) 
   p = set_syn_num(p, sender_syn_acc)
   p = set_ack_num(p, sender_ack_acc)

   # send FIN packet
   receiver.sendto(str(p), (receiver_host, receiver_port))
   sender_state = STATE_TEARDOWN

   if (debug): print "teardown #1 sent"

   while (sender_state != STATE_FINISHED):
      try:
         response, addr = receiver.recvfrom(1024)
         p = eval(response)

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
            p = set_syn_num(p, sender_syn_acc)
            p = set_ack_num(p, sender_ack_acc)

            receiver.sendto(str(p), (receiver_host, receiver_port))
            sender_state = STATE_FINISHED

            if (debug): print "teardown (S): received last packet (FIN\
               from sender). state -> FINISHED"
            
         else:
            print "[*] teardown error. state: " + str(sender_state) + ", response: " + response
            sys.exit()

      except socket.timeout:
         print "[*] timed out. could not teardown " + receiver_host + ":" + str(receiver_port)
         sys.exit()
   

def check_state(state, error_msg):
   if (sender_state != state):
      print "[*] error: sender state != " + str(state) + ". " + error_msg
      sys.exit()

def handshake(receiver, receiver_host, receiver_port, sender_timeout):
   global sender_state

   check_state(STATE_INACTIVE, "trying to connect when state != inactive")

   #if (sender_state != STATE_INACTIVE):
   #   print "[*] error: trying to connect when state != inactive"
   #   sys.exit


   #sender_host = receiver.getsockname()[0]
   #sender_port = receiver.getsockname()[1]
   #print receiver.getsockname()

   # create packet
   p = create_packet()
   p = set_syn(p)

   #p = set_dest_port(p, receiver_port)
   #p = set_src_port(p, sender_port)

   # send SYN packet
   receiver.sendto(str(p), (receiver_host, receiver_port))
   sender_state = STATE_INIT

   if (debug): print "handshake #1 sent"

   try:
      response, addr = receiver.recvfrom(1024)
      p = eval(response)

      if (debug): print "response received: #" + response + "#"
      #if (debug): print "bits: " + str(bin(p[2]))


      if (is_syn(p) and is_ack(p) and get_syn_num(p) == 0 and get_ack_num(p) == 1):
         p = create_packet()
         p = set_ack(p)
         p = set_syn_num(p, 1)
         p = set_ack_num(p, 1)

         # send 3rd packet: ACK (with no payload data)
         receiver.sendto(str(p), (receiver_host, receiver_port))
         sender_state = STATE_CONNECTED
         print "[*] connected to " + receiver_host + ":" + str(receiver_port)

      else:
         print "[*] handshake error, response: " + response
         sys.exit()

   except socket.timeout:
      print "[*] timed out. could not connect to " + receiver_host + ":" + str(receiver_port)
      sys.exit()



def readFile(filename):

   try:
      file_descriptor = open(filename, "r")
      buffer = file_descriptor.read()
      file_descriptor.close()
   except:
      sys.exit("fatal: no such file " + filename + " " + e)

   buffer = buffer.rstrip()   # TODO remove

   return buffer


def rdt(receiver_host, receiver_port, buffer, sender_mss, 
      sender_timeout):

   # create a socket object
   receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   receiver.settimeout(sender_timeout)

   # send data
   p = create_packet()
   print p[4]
   print str(p)
   p[4] = "something"
   print p[4]
   p = add_msg(p, str(buffer))
   print p

   #receiver.sendto(str(buffer), (receiver_host, receiver_port))
   receiver.sendto(str(p), (receiver_host, receiver_port))

   # receive data
   try:
      response, addr = receiver.recvfrom(1024)
      if (debug): print "response received: #" + response + "#"

   except socket.timeout:
      print "timed out"


main()
