# COMP3331 Assignment One
# Luke Cusack, z5078476
# August 2016
# RTP over UDP: PLD.py - PLD module


import logger, random


debug       = True
HOST_SENDR  = 0

def handle(socket, packet, time, receiver_host, receiver_port, random_seed):

   pdrop = round(random.random())

   if (pdrop == 1):
      # send packet
      socket.sendto(str(p), (receiver_host, receiver_port))
      logger.log(HOST_SENDR, time, DIR_SENT, p)
      if (debug): print "pld (" + pdrop + "): sent"

   else:
      logger.log(HOST_SENDR, time, DIR_DROP, p)
      if (debug): print "pld (" + pdrop + "): dropped"
      
   print "PLD"
