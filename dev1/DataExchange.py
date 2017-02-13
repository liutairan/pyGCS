

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

class WorkerProcess(multiprocessing.Process):

    def __init__(self, port, addresslist, result_queue):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        self.serialPort = port
        self.addressList = addresslist
        self.sch = SerialCommunication(self.serialPort, self.addressList)
        self.result_queue = result_queue
    
    def run(self):
        while not self.exit.is_set():
            self.sch.RegularLoadInfo()
            self.result_queue.put(self.sch.rawData)
            time.sleep(0.1)
        print "Exited"

    def shutdown(self):
        print "Shutdown initiated"
        try:
            self.sch.stopSerial()
        except Exception:
            print(Exception)
        self.exit.set()


class DataExchange(object):
    def __init__(self):
        self._observers = []
        self._addressList = [[],[],[]]
        self._serialPort = ''
        self._serialOn = False
        self.workerSerial = None
        self._rawData = None
        self.result = multiprocessing.Queue()
        self.timer = None

    def bind_to(self, callback):
        self._observers.append(callback)

    # addr
    def get_addressList(self):
        return self._addressList

    def set_addressList(self, value):
        self._addressList = value
        print(self._addressList)

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
            self.workerSerial = WorkerProcess(self.serialPort, self.addressList, self.result)
            self.workerSerial.daemon = True
            self.workerSerial.start()
            self.timer = Timer(0.5, self.OnUpdate, ())
            self.timer.daemon = True
            self.timer.start()
            pass

        elif self.serialOn == False:
            self.workerSerial.shutdown()
            self.timer.cancel()
            self.timer = None
            pass

    serialOn = property(get_serialOn, set_serialOn)

    def get_rawData(self):
        return self._rawData

    def set_rawData(self, value):
        self._rawData = value
        print('get new data')
        print(self._rawData)

    rawData = property(get_rawData, set_rawData)

    def OnUpdate(self):
        while True:
            try:
                temp = self.result.get()
                for callback in self._observers:
                    callback(temp)
            except Queue.Empty:
                pass
