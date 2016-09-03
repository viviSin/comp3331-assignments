# COMP3331 Assignment One
# Luke Cusack, z5078476
# August 2016
# RTP over UDP: PLD.py - PLD module


import logger, random, socket, time
#from sender import socket


debug             = True

HOST_SENDR        = 0
HOST_RECVR        = 1

DIR_SENT          = 0
DIR_RECV          = 1
DIR_DROP          = 2

def handle(r, packet, current_time, receiver_host, receiver_port, pdrop):

   random.seed(time.time())
   random_num = random.random()

   if (random_num > pdrop):
      # send packet
      r.sendto(str(packet), (receiver_host, receiver_port))
      logger.log(HOST_SENDR, current_time, DIR_SENT, packet)
      if (debug): print "pld (" + str(pdrop) + "): sent"

   else:
      
      # drop packet
      logger.log(HOST_SENDR, current_time, DIR_DROP, packet)
      if (debug): print "pld (" + str(pdrop) + "): dropped"
