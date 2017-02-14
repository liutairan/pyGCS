import os
import sys
import time

import wx
import threading
from threading import Thread
from wx.lib.pubsub import pub

import serial
import serial.tools.list_ports

class WorkerVoiceThread(threading.Thread):
    def __init__(self, notify_window, id):
        threading.Thread.__init__(self)
        self.id = id
        self.counter = 0
        self._notify_window = notify_window
        self.abort = False
    
    def run(self):
        while not self.abort:
            self.counter += 1
            print('Working on '+str(self.id))
            os.system('say Hello world')
            wx.PostEvent(self._notify_window, DataEvent(self.counter, self.id))
            time.sleep(1)
    
    def stop(self):
        self.abort = True


class DataEvent(wx.PyEvent):
    def __init__(self, data, id):
        wx.PyEvent.__init__(self)
        self.SetEventType(id)
        self.data = data


class TabOne(wx.Panel):
    def __init__(self, parent, DEH):
        wx.Panel.__init__(self, parent)
        self.workerVoice = None
        self.workerSerial = None
        self.deh = DEH
        self.deh.bind_to(self.OnUpdate)
        self.InitUI()

    def InitUI(self):
        '''
        # Boxes
        buttonStaticBox = wx.StaticBox(self, -1, 'Functions', pos = (0,0), size = (345,95))
        quadsStaticBox = wx.StaticBox(self, -1, 'Quad Status', pos = (0,395), size = (285,210))
        
        # Buttons
        self.editWPButton1 = wx.Button(self, -1, 'Edit', pos = (0,10), size = (50,20))
        self.uploadWPButton1 = wx.Button(self, -1, 'Upload', pos = (55,10), size = (65,20))
        self.downloadWPButton1 = wx.Button(self, -1, 'Download', pos = (125,10), size = (75,20))
        self.startMissionButton1 = wx.Button(self, -1, 'Start', pos = (205,10), size = (60,20))
        self.abortMissionButton1 = wx.Button(self, -1, 'Abort', pos = (270,10), size = (60,20))
        
        self.editWPButton2 = wx.Button(self, -1, 'Edit', pos = (0,35), size = (50,20))
        self.uploadWPButton2 = wx.Button(self, -1, 'Upload', pos = (55,35), size = (65,20))
        self.downloadWPButton2 = wx.Button(self, -1, 'Download', pos = (125,35), size = (75,20))
        self.startMissionButton2 = wx.Button(self, -1, 'Start', pos = (205,35), size = (60,20))
        self.abortMissionButton2 = wx.Button(self, -1, 'Abort', pos = (270,35), size = (60,20))
        
        self.editWPButton3 = wx.Button(self, -1, 'Edit', pos = (0,60), size = (50,20))
        self.uploadWPButton3 = wx.Button(self, -1, 'Upload', pos = (55,60), size = (65,20))
        self.downloadWPButton3 = wx.Button(self, -1, 'Download', pos = (125,60), size = (75,20))
        self.startMissionButton3 = wx.Button(self, -1, 'Start', pos = (205,60), size = (60,20))
        self.abortMissionButton3 = wx.Button(self, -1, 'Abort', pos = (270,60), size = (60,20))
        '''
        
        serialPortInfo = list(serial.tools.list_ports.comports())
        serialPorts = []
        for i in range(len(serialPortInfo)):
            serialPorts.append(serialPortInfo[i][0])
        self.serialPortComboBox = wx.ComboBox(self, choices=serialPorts, size = (300,25), pos = (10,10))
        self.Bind(wx.EVT_COMBOBOX, self.OnChoosePort, self.serialPortComboBox)
        
        self.connectButton = wx.Button(self, -1, 'Connect', pos = (320,5), size = (90,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.Bind(wx.EVT_BUTTON, self.OnClickSerialConnect, self.connectButton)
        
        # Voice
        voiceService = wx.StaticText(self, -1, 'Voice Service', pos = (10,40), size = (120,20))
        self.voiceSwitch = wx.Button(self, -1, 'OFF', pos = (140,35), size = (60,20))
        self.Bind(wx.EVT_BUTTON,self.OnClickVoiceSwitch, self.voiceSwitch)

        # Status
        self.quadLabel1 = wx.StaticText(self, -1, 'QUAD 1', pos = (5,410), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.quadLabel1.SetBackgroundColour((220,220,220))
        self.connectLight1 = wx.StaticText(self, -1, 'NO CON', pos = (5,430), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.connectLight1.SetBackgroundColour((255,0,0))
        armLight1 = wx.StaticText(self, -1, 'DISARM', pos = (5,450), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        armLight1.SetBackgroundColour((220,220,220))
        levelLight1 = wx.StaticText(self, -1, 'LEVEL', pos = (5,470), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        levelLight1.SetBackgroundColour((220,220,220))
        altLight1 = wx.StaticText(self, -1, 'ALT', pos = (5,490), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        altLight1.SetBackgroundColour((220,220,220))
        posLight1 = wx.StaticText(self, -1, 'POS', pos = (5,510), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        posLight1.SetBackgroundColour((220,220,220))
        navLight1 = wx.StaticText(self, -1, 'NAV', pos = (5,530), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        navLight1.SetBackgroundColour((220,220,220))
        gcsLight1 = wx.StaticText(self, -1, 'GCS', pos = (5,550), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        gcsLight1.SetBackgroundColour((220,220,220))
        
        self.quadLabel2 = wx.StaticText(self, -1, 'QUAD 2', pos = (75,410), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.quadLabel2.SetBackgroundColour((220,220,220))
        self.connectLight2 = wx.StaticText(self, -1, 'NO CON', pos = (75,430), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.connectLight2.SetBackgroundColour((255,0,0))
        armLight2 = wx.StaticText(self, -1, 'DISARM', pos = (75,450), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        armLight2.SetBackgroundColour((220,220,220))
        levelLight2 = wx.StaticText(self, -1, 'LEVEL', pos = (75,470), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        levelLight2.SetBackgroundColour((220,220,220))
        altLight2 = wx.StaticText(self, -1, 'ALT', pos = (75,490), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        altLight2.SetBackgroundColour((220,220,220))
        posLight2 = wx.StaticText(self, -1, 'POS', pos = (75,510), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        posLight2.SetBackgroundColour((220,220,220))
        navLight2 = wx.StaticText(self, -1, 'NAV', pos = (75,530), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        navLight2.SetBackgroundColour((220,220,220))
        gcsLight2 = wx.StaticText(self, -1, 'GCS', pos = (75,550), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        gcsLight2.SetBackgroundColour((220,220,220))
        
        self.quadLabel3 = wx.StaticText(self, -1, 'QUAD 3', pos = (145,410), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.quadLabel3.SetBackgroundColour((220,220,220))
        self.connectLight3 = wx.StaticText(self, -1, 'NO CON', pos = (145,430), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.connectLight3.SetBackgroundColour((255,0,0))
        armLight3 = wx.StaticText(self, -1, 'DISARM', pos = (145,450), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        armLight3.SetBackgroundColour((220,220,220))
        levelLight3 = wx.StaticText(self, -1, 'LEVEL', pos = (145,470), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        levelLight3.SetBackgroundColour((220,220,220))
        altLight3 = wx.StaticText(self, -1, 'ALT', pos = (145,490), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        altLight3.SetBackgroundColour((220,220,220))
        posLight3 = wx.StaticText(self, -1, 'POS', pos = (145,510), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        posLight3.SetBackgroundColour((220,220,220))
        navLight3 = wx.StaticText(self, -1, 'NAV', pos = (145,530), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        navLight3.SetBackgroundColour((220,220,220))
        gcsLight3 = wx.StaticText(self, -1, 'GCS', pos = (145,550), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        gcsLight3.SetBackgroundColour((220,220,220))
        
        # Show
        self.Show(True)

    def OnUpdate(self, global_states, other_states):
        # use global_states to update this page
        #print('tab one updated')
        #print(global_states)
        #print(other_states)
        try:
            if len(other_states[0]) > 0:
                self.connectLight1.SetBackgroundColour((0,255,0))
            else:
                self.connectLight1.SetBackgroundColour((255,0,0))
            if len(other_states[1]) > 0:
                self.connectLight2.SetBackgroundColour((0,255,0))
            else:
                self.connectLight2.SetBackgroundColour((255,0,0))
            if len(other_states[2]) > 0:
                self.connectLight3.SetBackgroundColour((0,255,0))
            else:
                self.connectLight3.SetBackgroundColour((255,0,0))
        except:
            pass

    def OnChoosePort(self, event):
        self.deh.serialPort = self.serialPortComboBox.GetValue()

    def OnClickVoiceSwitch(self, event):
        if self.voiceSwitch.GetLabel() == 'OFF':
            print('ON')
            self.voiceSwitch.SetLabel('ON')
            if not self.workerVoice:
                EVT_ID_VALUE = wx.NewId()
                self.workerVoice = WorkerVoiceThread(self, EVT_ID_VALUE)
                self.workerVoice.daemon = True
                self.workerVoice.start()
        elif self.voiceSwitch.GetLabel() == 'ON':
            print('OFF')
            self.voiceSwitch.SetLabel('OFF')
            if self.workerVoice:
                self.workerVoice.stop()
                del(self.workerVoice)
                self.workerVoice = None
        else:
            pass

    def OnClickSerialConnect(self, event):
        if self.connectButton.GetLabel() == 'Connect':
            print('Connected')
            self.connectButton.SetLabel('Disconnect')
            self.deh.serialOn = True
        elif self.connectButton.GetLabel() == 'Disconnect':
            print('Disconnected')
            self.connectButton.SetLabel('Connect')
            self.deh.serialOn = False
        else:
            pass
