# COMP3331 Assignment One
# Luke Cusack, z5078476
# August, September 2016
# Packet handling interface


# globals/psuedo "#defines"

# positions within the list
SEQ_NUM     = 0
ACK_NUM     = 1
FLAGS       = 2
MESSAGE     = 3

# flags
SYN_FLAG    = 0b0001
ACK_FLAG    = 0b0010
FIN_FLAG    = 0b0100
DATA_FLAG   = 0b1000


# create packet
def create_packet():
   packet = [0, 0, 0, 0, 0, 0]
   return packet


# set and get seq/ack numbers
def set_seq_num(packet, value):
   packet[SEQ_NUM] = value
   return packet

def set_ack_num(packet, value):
   packet[ACK_NUM] = value
   return packet

def get_seq_num(packet):
   return packet[SEQ_NUM]

def get_ack_num(packet):
   return packet[ACK_NUM]


# set and check flags
def set_syn(packet):
   # print "set syn"
   packet[FLAGS] |= SYN_FLAG
   return packet

def set_ack(packet):
   # print "set ack"
   packet[FLAGS] |= ACK_FLAG
   return packet

def set_fin(packet):
   # print "set fin"
   packet[FLAGS] |= FIN_FLAG
   return packet

def set_data(packet):
   # print "set data"
   packet[FLAGS] |= DATA_FLAG
   return packet

def is_syn(packet):
   # print "is syn?"
   result = packet[FLAGS] & SYN_FLAG
   return result == SYN_FLAG

def is_ack(packet):
   # print "is ack?"
   result = packet[FLAGS] & ACK_FLAG
   return result == ACK_FLAG

def is_fin(packet):
   # print "is fin?"
   result = packet[FLAGS] & FIN_FLAG
   return result == FIN_FLAG

def is_data(packet):
   # print "is data?"
   result = packet[FLAGS] & DATA_FLAG
   return result == DATA_FLAG

def get_flags(packet):
   flags = ""

   if (is_syn(packet)):
      flags += "S"
   if (is_ack(packet)):
      flags += "A"
   if (is_fin(packet)):
      flags += "F"
   if (is_data(packet)):
      flags += "D"

   return flags


# set and get applicaton data/message
def add_data(packet, message):
   # print "add msg"
   packet[MESSAGE] = message
   return packet

def get_data(packet):
   # print "get msg"
   return str(packet[MESSAGE])
