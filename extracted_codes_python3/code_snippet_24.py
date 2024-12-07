#!/usr/bin/python -u
#
# Project 2 Starter Code
#

import sys
import socket
import time
import datetime
import select
import json

MSG_SIZE = 1500
DATA_SIZE = 1000
TIMEOUT = 30
SEQUENCE = 0
RTO = 1
SLIDING_WINDOW = 100

# Bind to localhost and an ephemeral port
IP_PORT = sys.argv[1]
UDP_IP = IP_PORT[0:IP_PORT.find(":")]
UDP_PORT = int(IP_PORT[IP_PORT.find(":")+1:])
dest = (UDP_IP, UDP_PORT)

# Set up the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(TIMEOUT)

#setup bookkeeping
inFlightCount = 0
packetsInFlight = {}

def log(string):
  sys.stderr.write(datetime.datetime.now().strftime("%H:%M:%S.%f") + " " + string + "\n")

def send_next_packet():
  global SEQUENCE
  global inFlightCount
  global packetsInFlight

  data = sys.stdin.read(DATA_SIZE)
  if (len(data) > 0):
    msgObj = {"sequence": SEQUENCE, "data": data, "ack": False, "eof": False}
    msg = json.dumps(msgObj)
    SEQUENCE += len(data)

    if sock.sendto(msg, dest) < len(msg):
      log("[error] unable to fully send packet")
    else:
      log("[send data] " + str(SEQUENCE) + " (" + str(len(data)) + ")")
      packetsInFlight[msgObj['sequence']] = (msg, time.time()) #pretty sure this give the current time
      inFlightCount += 1
    return True
  else:
    return False

# Send first packet
send_next_packet()

# Now read in data, send packets
# Notes:
# So we can make our sliding window the whole megabyte
# calculating the RTO is the hard part, since we don't know what the delay param is set to
# maybe we just optimize for speed or data, not both
# so we just set the RTO to a low number, we can make it dynamic later if we feel
# So we send out our MB of data -> wait for acks, up to RTO time, then retransmit
# hmm so unsure how bandwidth interacts with a big sliding window,
# do we need to manually throttle how much data we send or will the network do that for us?
# or do we lose data if we try to send more than the bandwidth can handle?
# do I implement 3dup acks rule, where I retransmit if I see 3 acks in a row past my unacked?
# ----------- PSEUDOCODE IDEAS
# while True:
#     if numInFlight < SLIDING_WINDOW:
#         send next packet;
#         add copy of sent packet to our packetsInFlight map (sequence number -> (packet, timeSent))
#         numInFlight++;
#     do a non-blocking receive (maybe set timeout to .001 or something)
#     if it gives us something:
#         is it an ack? -> mark that packet ACK'ed in our map (maybe just remove the entry?)
#         numInFlight--;
#     for every entry in packetsInFlight map:
#         if it's been RTO since timeSent, retransmit, update timeSent in map

#helper that retransmits any packets that have timed out (were sent RTO or more seconds ago)
def maybeRetransmit():
  global packetsInFlight
  for key in packetsInFlight:
    value = packetsInFlight[key]
    msg = value[0] #fir value of tuple is the raw message string to send, complete with headers and data
    timeSent = value[1] #second value of tuple is time sent. Time is the number of seconds past the epoch
    timeElapsed = time.time() - timeSent
    if timeElapsed >= RTO:
      #retransmiit and update the time sent
      log("timeElapsed = " + str(timeElapsed))
      if sock.sendto(msg, dest) < len(msg):
        log("[error] unable to fully send packet")
      else:
        log("[retransmit packet] " + msg)
        packetsInFlight[key] = (msg, time.time())

#helper that does a non-blocking receive, checks for ack, and modifies packetsInFlight as necessary
def listenForAck():
  global packetsInFlight
  global inFlightCount
  readable, writeable, exceptional = select.select([sock], [], [], 0) #writeable and exceptional are not used
  if len(readable) > 0: #if the socket is readable, read it
    result = sock.recvfrom(MSG_SIZE)
    (data, addr) = result
    log("data is" + data)
    try:
      decoded = json.loads(data)
      if decoded['ack'] == 0 or decoded['ack']: #if it's an ack
        log("[recv ack] " + str(decoded['ack']))
        #log("length of the data being acked: " + str(len(packetsInFlight[decoded['ack']][0]['data'])))
        if True:#len(packetsInFlight[decoded['ack']][0]['data']) == decoded['length']:
          #remove the entry for his ACK's sequence number in packetsInFlight
	  temp = packetsInFlight.pop(decoded['ack'], None)
          if not temp:
	    log("ERROR: Tried to remove an entry in packetsInFlight that does not exist")
          else:
            inFlightCount -= 1
    except (ValueError, KeyError, TypeError):
      log("[recv corrupt packet]")
# --------------------

while True:
  listenForAck() #check for acks and process any we find
  if inFlightCount < SLIDING_WINDOW: #if we haven't filled the sliding window yet, send another packet
    if (not send_next_packet()) and (not bool(packetsInFlight)):
        log("we think we're done sending and receiving acks")
	break
  maybeRetransmit() #retransmit any packets that have timed out

# THIS IS THE STARTER CODE CORE LOOP --  IT DOES NOT RUN ANYMORE BUT ITS HERE TO REFERENCE
while False: #cheap way of commenting this stuff out. This used to while True.
  log("ABOUT TO SLEEP")
  result = sock.recvfrom(MSG_SIZE)

  if result:
    (data, addr) = result
    try:
      decoded = json.loads(data)

      # If there is an ack with the proper sequence number, send next packet
      if decoded['ack'] == SEQUENCE:
        log("[recv ack] " + str(SEQUENCE))

        # Try to send next packet; break if no more data
        if (not send_next_packet()):
          break
    except (ValueError, KeyError, TypeError):
      log("[recv corrupt packet]")
  else:
    # we have timed out waiting for packet, should probably retransmit
    log("[error] timeout")
    sys.exit(-1)

sock.sendto(json.dumps({"eof": True, "data": "", "sequence": SEQUENCE, "ack": False}), dest)
sys.exit(0)
