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
            #print('pre check')
            while True:
                try:
                    with time_limit(0.5):
                        self.PreCheck(tempObj)
                        print('Warmed up')
                        break
                except:
                    self.stopSerial()
                    print('Time out warm up')
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
            self.board.getData(0,MultiWii.ANALOG,[],obj)
            time.sleep(0.05)
            self.board.getData(0,MultiWii.RAW_GPS,[],obj)
            time.sleep(0.05)
            #self.board.getData(0,MultiWii.GPSSTATISTICS,[],obj)
            #time.sleep(0.05)
        except Exception, error:
            print('Failed')
            print(Exception)
            print(error)

    def RegularLoadOverview(self):
        for i in range(len(self.quadObjs)):
            tempObj = self.quadObjs[i]
            try:
                self.board.getDataLoose(0, MultiWii.MSP_STATUS_EX, [], tempObj, self.quadObjs)
                self.board.getDataLoose(0, MultiWii.ANALOG, [], tempObj, self.quadObjs)
            except:
                pass

    def RegularLoadAllGPS(self):
        for i in range(len(self.quadObjs)):
            tempObj = self.quadObjs[i]
            try:
                self.board.getData(0,MultiWii.RAW_GPS,[],tempObj)
            except:
                pass

    def RegularLoadQuad1(self):
        quadObjId = 0
        tempObj = self.quadObjs[quadObjId]
        try:
            self.board.getData(0,MultiWii.MSP_STATUS_EX,[],tempObj)
            self.board.parseSensorStatus(tempObj)
            self.board.parseFlightModeFlags(tempObj)
            self.board.getData(0,MultiWii.ANALOG,[],tempObj)
        except:
            pass

    def RegularLoadQuad2(self):
        quadObjId = 1
        for i in range(1):
            if len(self.addressList[i]) == 0:
                quadObjId = quadObjId - 1
            else:
                pass
        tempObj = self.quadObjs[quadObjId]
        try:
            self.board.getData(0,MultiWii.MSP_STATUS_EX,[],tempObj)
            self.board.parseSensorStatus(tempObj)
            self.board.parseFlightModeFlags(tempObj)
            self.board.getData(0,MultiWii.ANALOG,[],tempObj)
        except:
            pass

    def RegularLoadQuad3(self):
        quadObjId = 2
        for i in range(1):
            if len(self.addressList[i]) == 0:
                quadObjId = quadObjId - 1
            else:
                pass
        tempObj = self.quadObjs[quadObjId]
        try:
            self.board.getData(0,MultiWii.MSP_STATUS_EX,[],tempObj)
            self.board.parseSensorStatus(tempObj)
            self.board.parseFlightModeFlags(tempObj)
            self.board.getData(0,MultiWii.ANALOG,[],tempObj)
        except:
            pass

    def RegularLoadInfoLoose(self):
        for i in range(len(self.quadObjs)):
            tempObj = self.quadObjs[i]
            try:
                self.board.getDataLoose(0, MultiWii.MSP_STATUS_EX, [], tempObj, self.quadObjs)
                self.board.getDataLoose(0, MultiWii.ANALOG, [], tempObj, self.quadObjs)
                self.board.getDataLoose(0, MultiWii.ATTITUDE,[],tempObj, self.quadObjs)
            except:
                print('Regular load error')
                pass

    def UploadWPs(self, mission_task):
        quadId = mission_task[0] - 10
        mission = mission_task[1]
        quadObjId = quadId - 1

        for i in range(quadId):
            if len(self.addressList[i]) == 0:
                quadObjId = quadObjId - 1
            else:
                pass
        self.quadObjs[quadObjId].missionList = mission
        print("Start uploaded missions. Quad: " + str(quadId))
        self.board.uploadMissions(self.quadObjs[quadObjId])
        print("All missions uploaded successfully. Quad: " + str(quadId))

    def DownloadWPs(self):
        pass


    def get_rawData(self):
        return self._rawData

    def set_rawData(self, value):
        self._rawData = value

    rawData = property(get_rawData, set_rawData)
