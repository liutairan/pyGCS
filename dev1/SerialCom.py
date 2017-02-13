#!/usr/bin/pythonw
# -*- coding: UTF-8 -*-

import os
from os import walk
import sys
from sys import stdout

import wx
import wx.lib.embeddedimage
import wx.dataview

import logging
import threading
from threading import Thread
from wx.lib.pubsub import pub

import serial
import serial.tools.list_ports
from pyzbMultiwii import MultiWii


import math
import time
import struct

import signal
from contextlib import contextmanager

class TimeoutException(Exception): pass

@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException, "Timed out!"
    signal.signal(signal.SIGALRM, signal_handler)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.alarm(0)

class SerialCommunication(object):
    def __init__(self, port, addrlist):
        self.addressList = addrlist
        self.serialPort = port
        self.board = MultiWii(self.serialPort)
        self._rawData = None
    
    def stopSerial(self):
        self.board.stopDevice()
    
    def transcheck(self):
        print('get data')

    def PreLoadInfo(self):
        for i in range(len(self.addressList)):
            tempAddress = self.addressList[i]
            if len(tempAddress) > 0:
                # do pre check
                print('Device '+str(i+1)+' online')
                self.PreCheck(tempAddress)
                pass
            else:
                print('Device '+str(i+1)+' not online')
                pass
                
    def PreCheck(self, address):
        address_long = address[0]
        address_short = address[1]
        try:
            #self.board.getData(0,MultiWii.ANALOG,[],'0',address_long,address_short)
            self.board.getData(0,MultiWii.MSP_STATUS_EX,[],'\x01',address_long,address_short)
            print(self.board.msp_status_ex)
        except Exception, error:
            print('Failed')
            print(Exception)
            print(error)

    def RegularLoadInfo(self):
        for i in range(len(self.addressList)):
            tempAddress = self.addressList[i]
            if len(tempAddress) > 0:
                print('Device '+str(i+1)+' online')
                try:
                    self.RegularCheck(tempAddress)
                except:
                    print('time out')
                    pass
                pass
            else:
                pass
    
    def RegularCheck(self, address):
        address_long = address[0]
        address_short = address[1]
        try:
            self.board.getData(0,MultiWii.MSP_STATUS_EX,[],'\x01',address_long,address_short)
            self.rawData = self.board.msp_status_ex
            #self.board.sendCMDNew(0,MultiWii.MSP_STATUS_EX,[],'0',address_long,address_short)
            #print(self.board.msp_status_ex)
        except Exception, error:
            print('Failed')
            print(Exception)
            print(error)

    def UploadWPs(self):
        pass

    def DownloadWPs(self):
        pass


    def get_rawData(self):
        return self._rawData

    def set_rawData(self, value):
        self._rawData = value

    rawData = property(get_rawData, set_rawData)
