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
from QuadStates import QuadStates

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
        self.quadObjs = []
        self.CreateObjs()
        self.PreLoadInfo()
    
    def stopSerial(self):
        self.board.stopDevice()

    def CreateObjs(self):
        for i in range(len(self.addressList)):
            if len(self.addressList[i]) > 0:
                self.quadObjs.append(QuadStates('\x01', self.addressList[i][0], self.addressList[i][1]))

    def PreLoadInfo(self):
        for i in range(len(self.quadObjs)):
            tempObj = self.quadObjs[i]
            try:
                self.PreCheck(tempObj)
            except:
                pass
                
    def PreCheck(self, obj):
        try:
            self.board.getData(0,MultiWii.BOXIDS,[],obj)
        except Exception, error:
            print('Failed')
            print(Exception)
            print(error)

    def RegularLoadInfo(self):
        for i in range(len(self.quadObjs)):
            tempObj = self.quadObjs[i]
            try:
                self.RegularCheck(tempObj)
            except:
                pass

    def RegularCheck(self, obj):
        try:
            self.board.getData(0,MultiWii.MSP_STATUS_EX,[],obj)
            self.board.parseSensorStatus(obj)
            self.board.parseFlightModeFlags(obj)
            self.board.getData(0,MultiWii.ATTITUDE,[],obj)
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
