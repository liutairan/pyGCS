#!/usr/bin/env python

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

import struct
import time
import sched
from threading import Timer
from SerialCom import SerialCommunication

import threading
import wx
from threading import Thread
import multiprocessing
from wx.lib.pubsub import pub

import multiprocessing
from multiprocessing import Process
from multiprocessing import Queue
import Queue
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

class WorkerProcess(multiprocessing.Process):

    def __init__(self, port, addresslist, task_queue, result_queue):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        self.serialPort = port
        self.addressList = addresslist
        self.sch = SerialCommunication(self.serialPort, self.addressList)
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.modeSelection = 0

    def run(self):
        while not self.exit.is_set():
            try:
                with time_limit(0.001):
                    next_task = self.task_queue.get()
            except:
                next_task = 0

            if next_task == 0:
                self.modeSelection = 0
                print(self.modeSelection)
                self.sch.RegularLoadInfoLoose()
                self.result_queue.put(self.sch.quadObjs)
                time.sleep(0.1)
            elif next_task == 1:
                self.modeSelection = 1
                print(self.modeSelection)
                self.modeSelection = 0
            elif next_task == 2:
                self.modeSelection = 2
                print(self.modeSelection)
                self.modeSelection = 0
            elif next_task == 3:
                self.modeSelection = 3
                print(self.modeSelection)
                self.modeSelection = 0
            else:
                pass
        print "Exited"

    def mode(self, value):
        self.modeSelection = value
        #print(self.modeSelection)

    def shutdown(self):
        print("Shutdown initiated")
        try:
            self.sch.stopSerial()
        except Exception:
            print(Exception)
        print('Process stopped')
        self.exit.set()


class DataExchange(object):
    def __init__(self):
        self._observers = []
        self._addressList = [[],[],[]]
        self._waypointLists = [[],[],[]]
        self._serialPort = ''
        self._serialOn = False
        self.workerSerial = None
        self._rawData = None
        self.task = multiprocessing.Queue()
        self.result = multiprocessing.Queue()
        self.timer = None
        self._serialMode = 0

    def bind_to(self, callback):
        self._observers.append(callback)
        #print(self._observers)
        #print((self._observers[0].im_class.__name__))

    # addr
    def get_addressList(self):
        return self._addressList

    def set_addressList(self, value):
        self._addressList = value
        #print('check')
        #print(self._addressList)
        self.OnSwitch()

    addressList = property(get_addressList, set_addressList)

    # serial port
    def get_serialPort(self):
        return self._serialPort

    def set_serialPort(self, value):
        self._serialPort = value

    serialPort = property(get_serialPort, set_serialPort)

    # serial switch
    def get_serialOn(self):
        return self._serialOn

    def set_serialOn(self, value):
        self._serialOn = value
        if self.serialOn == True:
            self.workerSerial = WorkerProcess(self.serialPort, self.addressList, self.task, self.result)
            self.workerSerial.daemon = True
            self.workerSerial.start()
            self.timer = Timer(0.1, self.OnUpdate, ())
            self.timer.daemon = True
            self.timer.start()
            pass

        elif self.serialOn == False:
            self.workerSerial.shutdown()
            self.timer.cancel()
            self.timer = None
            pass

    serialOn = property(get_serialOn, set_serialOn)

    def get_serialMode(self):
        return self._serialMode

    def set_serialMode(self, value):
        self._serialMode = value
        if self.serialOn == True:
            #pass
            self.task.put(self._serialMode)
            #self.workerSerial.mode(self.serialMode)

    serialMode = property(get_serialMode, set_serialMode)

    def get_rawData(self):
        return self._rawData

    def set_rawData(self, value):
        self._rawData = value
        #print('get new data')
        #print(self._rawData)

    rawData = property(get_rawData, set_rawData)

    def OnUpdate(self):
        while True:
            try:
                tempObjList = self.result.get()
                assignObjList = []
                for i in range(len(self.addressList)):
                    if len(self.addressList[i]) > 0:
                        assignObjList.append(tempObjList[0])
                        tempObjList.pop(0)
                    else:
                        assignObjList.append(None)

                for callback in self._observers:
                    subscriberName = callback.im_class.__name__
                    if subscriberName == 'TabOne':
                        callback(assignObjList, self.addressList)
                    elif subscriberName == 'TabTwo':
                        tempObj = assignObjList[0]
                        if tempObj != None:
                            callback(tempObj)
                    elif subscriberName == 'TabThree':
                        tempObj = assignObjList[1]
                        if tempObj != None:
                            callback(tempObj)
                    elif subscriberName == 'TabFour':
                        tempObj = assignObjList[2]
                        if tempObj != None:
                            callback(tempObj)
                    else:
                        pass

            except Queue.Empty:
                pass

    def OnSwitch(self):
        for callback in self._observers:
            subscriberName = callback.im_class.__name__
            if subscriberName == 'TabOne':
                callback(None, self.addressList)
