#!/usr/bin/env python
# coding: utf-8

# In[1]:


from LogDTClass import LogDT
from MeasureSysConverter import MeasureSysConverter
from datetime import datetime
from ParsePBSEsmCause import parsePBSEsmCause
from PacketBearerInfo import PacketBearerInfo
# In[3]:


def ParsePBD (line, logObj,dictionary):
    length = len(line)
    if 2 < length:
        dataOfPBD = ''
        PBDContextID = 0
        NumberOfContextID = 0
        if line[2] != '':
            NumberOfContextID = int(line[2])
            if NumberOfContextID != 0:
                if(3 < length) and (line[3] != '') :
                    PBDContextID = int(line[3])
                    
        if PBDContextID in dictionary:
            packet = dictionary[PBDContextID]
        else:
            packet = PacketBearerInfo()
            dictionary[PBDContextID] = packet
            packet = dictionary[PBDContextID]
            
        packet.ConnectionEnd = line[1]
        logObj.event = 'Packet Bearer Release'
        logObj.msgType = 'Release'       
        dataOfPBD = "PB Context ID: " + str(PBDContextID)
        
        if packet.ConnectionEnd != '' and packet.ConnectionSetup !='':
            tdelta = datetime.strptime(packet.ConnectionEnd.split('.', 1)[0], '%H:%M:%S') - datetime.strptime(packet.ConnectionSetup.split('.', 1)[0], '%H:%M:%S')        
            Time = float(tdelta.seconds)*1000 #MilliSeconds 
            dataOfPBD += ";PB Connection Failure duration: "+str(Time)
         
        if((3 + NumberOfContextID) < length) and (line[3 + NumberOfContextID] != '') : 
            measureSystem = MeasureSysConverter (int(line[3 + NumberOfContextID]))           
        esmCause = 'Unknown'
        if measureSystem == 'LTE FDD' or measureSystem == 'LTE TDD':
            if((4 + NumberOfContextID) < length) and (line[4 + NumberOfContextID] != '') : 
                esmCause = line[4 + NumberOfContextID]
                esmCause = parsePBSEsmCause(int(esmCause))
        dataOfPBD += ";ESM Cause: " + esmCause
        logObj.modeSystem = measureSystem
        logObj.eventInfo = dataOfPBD             
        return 1

