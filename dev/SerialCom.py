#!/usr/bin/pythonw
# -*- coding: UTF-8 -*-

'''
MIT License

Copyright (c) 2017 Tairan Liu

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

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

__author__ = "Tairan Liu"
__copyright__ = "Copyright 2017, Tairan Liu"
__credits__ = ["Tairan Liu", "Other Supporters"]
__license__ = "MIT"
__version__ = "0.4-dev"
__maintainer__ = "Tairan Liu"
__email__ = "liutairan2012@gmail.com"
__status__ = "Development"

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
            #self.board.getData(0,MultiWii.ATTITUDE,[],obj)
            self.board.getData(0,MultiWii.ANALOG,[],obj)
        except Exception, error:
            print('Failed')
            print(Exception)
            print(error)

    def RegularLoadInfoLoose(self):
        for i in range(len(self.quadObjs)):
            tempObj = self.quadObjs[i]
            try:
                self.board.getDataLoose(0, MultiWii.MSP_STATUS_EX, [], tempObj, self.quadObjs)
                self.board.getDataLoose(0, MultiWii.ANALOG, [], tempObj, self.quadObjs)
            except:
                pass

    def UploadWPs(self):
        pass

    def DownloadWPs(self):
        pass


    def get_rawData(self):
        return self._rawData

    def set_rawData(self, value):
        self._rawData = value

    rawData = property(get_rawData, set_rawData)
