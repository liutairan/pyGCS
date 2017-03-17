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

import os
import sys
import time

import wx
import threading
from threading import Thread
from wx.lib.pubsub import pub

import serial
import serial.tools.list_ports

__author__ = "Tairan Liu"
__copyright__ = "Copyright 2017, Tairan Liu"
__credits__ = ["Tairan Liu", "Other Supporters"]
__license__ = "MIT"
__version__ = "0.4-dev"
__maintainer__ = "Tairan Liu"
__email__ = "liutairan2012@gmail.com"
__status__ = "Development"

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

        # Radio
        radioService = wx.StaticText(self, -1, 'Radio Service', pos = (10,70), size = (120,20))
        self.radioSwitch = wx.Button(self, -1, 'OFF', pos = (140,65), size = (60,20))
        self.Bind(wx.EVT_BUTTON,self.OnClickRadioSwitch, self.radioSwitch)

        armService = wx.StaticText(self, -1, 'ARM Service', pos = (10,100), size = (120,20))
        self.armButton1 = wx.Button(self, -1, 'ARM', pos = (140,100), size = (80,20))
        self.Bind(wx.EVT_BUTTON,self.OnClickArmSwitch, self.armButton1)

        # Status
        self.quadLabel1 = wx.StaticText(self, -1, 'QUAD 1', pos = (5,410), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.quadLabel1.SetBackgroundColour((220,220,220))
        self.connectLight1 = wx.StaticText(self, -1, 'NO CON', pos = (5,430), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.connectLight1.SetBackgroundColour((255,0,0))
        self.armLight1 = wx.StaticText(self, -1, 'DISARM', pos = (5,450), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.armLight1.SetBackgroundColour((220,220,220))
        self.levelLight1 = wx.StaticText(self, -1, 'LEVEL', pos = (5,470), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.levelLight1.SetBackgroundColour((220,220,220))
        self.altLight1 = wx.StaticText(self, -1, 'ALT', pos = (5,490), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.altLight1.SetBackgroundColour((220,220,220))
        self.posLight1 = wx.StaticText(self, -1, 'POS', pos = (5,510), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.posLight1.SetBackgroundColour((220,220,220))
        self.navLight1 = wx.StaticText(self, -1, 'NAV', pos = (5,530), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.navLight1.SetBackgroundColour((220,220,220))
        self.gcsLight1 = wx.StaticText(self, -1, 'GCS', pos = (5,550), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.gcsLight1.SetBackgroundColour((220,220,220))
        self.voltageLight1 = wx.StaticText(self, -1, '0.0 V', pos = (5,570), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.voltageLight1.SetBackgroundColour((220,220,220))

        self.quadLabel2 = wx.StaticText(self, -1, 'QUAD 2', pos = (75,410), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.quadLabel2.SetBackgroundColour((220,220,220))
        self.connectLight2 = wx.StaticText(self, -1, 'NO CON', pos = (75,430), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.connectLight2.SetBackgroundColour((255,0,0))
        self.armLight2 = wx.StaticText(self, -1, 'DISARM', pos = (75,450), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.armLight2.SetBackgroundColour((220,220,220))
        self.levelLight2 = wx.StaticText(self, -1, 'LEVEL', pos = (75,470), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.levelLight2.SetBackgroundColour((220,220,220))
        self.altLight2 = wx.StaticText(self, -1, 'ALT', pos = (75,490), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.altLight2.SetBackgroundColour((220,220,220))
        self.posLight2 = wx.StaticText(self, -1, 'POS', pos = (75,510), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.posLight2.SetBackgroundColour((220,220,220))
        self.navLight2 = wx.StaticText(self, -1, 'NAV', pos = (75,530), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.navLight2.SetBackgroundColour((220,220,220))
        self.gcsLight2 = wx.StaticText(self, -1, 'GCS', pos = (75,550), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.gcsLight2.SetBackgroundColour((220,220,220))
        self.voltageLight2 = wx.StaticText(self, -1, '0.0 V', pos = (75,570), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.voltageLight2.SetBackgroundColour((220,220,220))

        self.quadLabel3 = wx.StaticText(self, -1, 'QUAD 3', pos = (145,410), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.quadLabel3.SetBackgroundColour((220,220,220))
        self.connectLight3 = wx.StaticText(self, -1, 'NO CON', pos = (145,430), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.connectLight3.SetBackgroundColour((255,0,0))
        self.armLight3 = wx.StaticText(self, -1, 'DISARM', pos = (145,450), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.armLight3.SetBackgroundColour((220,220,220))
        self.levelLight3 = wx.StaticText(self, -1, 'LEVEL', pos = (145,470), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.levelLight3.SetBackgroundColour((220,220,220))
        self.altLight3 = wx.StaticText(self, -1, 'ALT', pos = (145,490), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.altLight3.SetBackgroundColour((220,220,220))
        self.posLight3 = wx.StaticText(self, -1, 'POS', pos = (145,510), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.posLight3.SetBackgroundColour((220,220,220))
        self.navLight3 = wx.StaticText(self, -1, 'NAV', pos = (145,530), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.navLight3.SetBackgroundColour((220,220,220))
        self.gcsLight3 = wx.StaticText(self, -1, 'GCS', pos = (145,550), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.gcsLight3.SetBackgroundColour((220,220,220))
        self.voltageLight3 = wx.StaticText(self, -1, '0.0 V', pos = (145,570), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.voltageLight3.SetBackgroundColour((220,220,220))

        # Show
        self.Show(True)

    def OnUpdate(self, global_states, other_states):
        # use global_states to update this page
        # global_states will always have 3 elements, if any object is not connected, then a None will hold the place
        # other_states are quad connection information, only used to indicate a quad is connected or not.
        #print('tab one updated')
        #print(global_states)
        #print(other_states)
        try:
            if len(other_states[0]) > 0:
                self.connectLight1.SetLabel('CONN')
                self.connectLight1.SetBackgroundColour((0,255,0))

                # flight modes
                #print(global_obj.flightModes)
                if global_states[0].flightModes['ARM'] == 1:
                    self.armLight1.SetLabel('ARMED')
                    self.armLight1.SetBackgroundColour((255,0,0))
                elif global_states[0].flightModes['ARM'] == 0:
                    self.armLight1.SetLabel('DISARMED')
                    self.armLight1.SetBackgroundColour((0,255,0))
                else:
                    pass

                if global_states[0].flightModes['ANGLE'] == 1:
                    self.levelLight1.SetBackgroundColour((0,255,0))
                elif global_states[0].flightModes['ANGLE'] == 0:
                    self.levelLight1.SetBackgroundColour((255,0,0))
                else:
                    pass

                if global_states[0].flightModes['ALTHOLD'] == 1:
                    self.altLight1.SetBackgroundColour((0,255,0))
                elif global_states[0].flightModes['ALTHOLD'] == 0:
                    self.altLight1.SetBackgroundColour((255,0,0))
                else:
                    pass

                if global_states[0].flightModes['POSHOLD'] == 1:
                    self.posLight1.SetBackgroundColour((0,255,0))
                elif global_states[0].flightModes['POSHOLD'] == 0:
                    self.posLight1.SetBackgroundColour((255,0,0))
                else:
                    pass

                if (global_states[0].flightModes['NAVWP'] == 1) or (global_states[0].flightModes['NAVRTH'] == 1):
                    self.navLight1.SetBackgroundColour((0,255,0))
                elif (global_states[0].flightModes['NAVWP'] == 0) or (global_states[0].flightModes['NAVRTH'] == 1):
                    self.navLight1.SetBackgroundColour((255,0,0))
                else:
                    pass

                if global_states[0].flightModes['GCSNAV'] == 1:
                    self.gcsLight1.SetBackgroundColour((0,255,0))
                elif global_states[0].flightModes['GCSNAV'] == 0:
                    self.gcsLight1.SetBackgroundColour((255,0,0))
                else:
                    pass

                # voltage
                self.voltageLight1.SetLabel(str(global_states[0].msp_analog['vbat']/10.0)+' V')
                if global_states[0].msp_analog['vbat'] >= 114:
                    self.voltageLight1.SetBackgroundColour((0,255,0))
                elif (global_states[0].msp_analog['vbat'] >= 108) and (global_states[0].msp_analog['vbat'] < 114):
                    self.voltageLight1.SetBackgroundColour((255,200,0))
                elif (global_states[0].msp_analog['vbat'] >= 101) and (global_states[0].msp_analog['vbat'] < 108):
                    self.voltageLight1.SetBackgroundColour((255,0,0))
                else:
                    self.voltageLight1.SetBackgroundColour((255,0,0))

                # GPS
                if global_states[0].msp_raw_gps['gps_fix'] == 2:
                    self.deh._currentGPS[0] = [int(global_states[0].msp_raw_gps['gps_lat'])/(10.0**7), int(global_states[0].msp_raw_gps['gps_lon'])/(10.0**7)]
                else:
                    pass # no valid GPS data received, keep last data
            else:
                self.connectLight1.SetBackgroundColour((255,0,0))

            if len(other_states[1]) > 0:
                self.connectLight2.SetLabel('CONN')
                self.connectLight2.SetBackgroundColour((0,255,0))

                if global_states[1].flightModes['ARM'] == 1:
                    self.armLight2.SetLabel('ARMED')
                    self.armLight2.SetBackgroundColour((255,0,0))
                elif global_states[1].flightModes['ARM'] == 0:
                    self.armLight2.SetLabel('DISARM')
                    self.armLight2.SetBackgroundColour((0,255,0))
                else:
                    pass

                if global_states[1].flightModes['ANGLE'] == 1:
                    self.levelLight2.SetBackgroundColour((0,255,0))
                elif global_states[1].flightModes['ANGLE'] == 0:
                    self.levelLight2.SetBackgroundColour((255,0,0))
                else:
                    pass

                if global_states[1].flightModes['ALTHOLD'] == 1:
                    self.altLight2.SetBackgroundColour((0,255,0))
                elif global_states[1].flightModes['ALTHOLD'] == 0:
                    self.altLight2.SetBackgroundColour((255,0,0))
                else:
                    pass

                if global_states[1].flightModes['POSHOLD'] == 1:
                    self.posLight2.SetBackgroundColour((0,255,0))
                elif global_states[1].flightModes['POSHOLD'] == 0:
                    self.posLight2.SetBackgroundColour((255,0,0))
                else:
                    pass

                if (global_states[1].flightModes['NAVWP'] == 1) or (global_states[1].flightModes['NAVRTH'] == 1):
                    self.navLight2.SetBackgroundColour((0,255,0))
                elif (global_states[1].flightModes['NAVWP'] == 0) or (global_states[1].flightModes['NAVRTH'] == 1):
                    self.navLight2.SetBackgroundColour((255,0,0))
                else:
                    pass

                if global_states[1].flightModes['GCSNAV'] == 1:
                    self.gcsLight2.SetBackgroundColour((0,255,0))
                elif global_states[1].flightModes['GCSNAV'] == 0:
                    self.gcsLight2.SetBackgroundColour((255,0,0))
                else:
                    pass

                self.voltageLight2.SetLabel(str(global_states[1].msp_analog['vbat']/10.0)+' V')
                if global_states[1].msp_analog['vbat'] >= 114:
                    self.voltageLight2.SetBackgroundColour((0,255,0))
                elif (global_states[1].msp_analog['vbat'] >= 108) and (global_states[1].msp_analog['vbat'] < 114):
                    self.voltageLight2.SetBackgroundColour((255,200,0))
                elif (global_states[1].msp_analog['vbat'] >= 101) and (global_states[1].msp_analog['vbat'] < 108):
                    self.voltageLight2.SetBackgroundColour((255,0,0))
                else:
                    self.voltageLight2.SetBackgroundColour((255,0,0))
            else:
                self.connectLight2.SetBackgroundColour((255,0,0))

            if len(other_states[2]) > 0:
                self.connectLight3.SetLabel('CONN')
                self.connectLight3.SetBackgroundColour((0,255,0))

                if global_states[2].flightModes['ARM'] == 1:
                    self.armLight3.SetLabel('ARMED')
                    self.armLight3.SetBackgroundColour((255,0,0))
                elif global_states[2].flightModes['ARM'] == 0:
                    self.armLight3.SetLabel('DISARM')
                    self.armLight3.SetBackgroundColour((0,255,0))
                else:
                    pass

                if global_states[2].flightModes['ANGLE'] == 1:
                    self.levelLight3.SetBackgroundColour((0,255,0))
                elif global_states[2].flightModes['ANGLE'] == 0:
                    self.levelLight3.SetBackgroundColour((255,0,0))
                else:
                    pass

                if global_states[2].flightModes['ALTHOLD'] == 1:
                    self.altLight3.SetBackgroundColour((0,255,0))
                elif global_states[2].flightModes['ALTHOLD'] == 0:
                    self.altLight3.SetBackgroundColour((255,0,0))
                else:
                    pass

                if global_states[2].flightModes['POSHOLD'] == 1:
                    self.posLight3.SetBackgroundColour((0,255,0))
                elif global_states[2].flightModes['POSHOLD'] == 0:
                    self.posLight3.SetBackgroundColour((255,0,0))
                else:
                    pass

                if (global_states[2].flightModes['NAVWP'] == 1) or (global_states[2].flightModes['NAVRTH'] == 1):
                    self.navLight3.SetBackgroundColour((0,255,0))
                elif (global_states[2].flightModes['NAVWP'] == 0) or (global_states[2].flightModes['NAVRTH'] == 1):
                    self.navLight3.SetBackgroundColour((255,0,0))
                else:
                    pass

                if global_states[2].flightModes['GCSNAV'] == 1:
                    self.gcsLight3.SetBackgroundColour((0,255,0))
                elif global_states[2].flightModes['GCSNAV'] == 0:
                    self.gcsLight3.SetBackgroundColour((255,0,0))
                else:
                    pass

                self.voltageLight3.SetLabel(str(global_states[2].msp_analog['vbat']/10.0)+' V')
                if global_states[2].msp_analog['vbat'] >= 114:
                    self.voltageLight3.SetBackgroundColour((0,255,0))
                elif (global_states[2].msp_analog['vbat'] >= 108) and (global_states[2].msp_analog['vbat'] < 114):
                    self.voltageLight3.SetBackgroundColour((255,200,0))
                elif (global_states[2].msp_analog['vbat'] >= 101) and (global_states[2].msp_analog['vbat'] < 108):
                    self.voltageLight3.SetBackgroundColour((255,0,0))
                else:
                    self.voltageLight3.SetBackgroundColour((255,0,0))
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

    def OnClickRadioSwitch(self, event):
        if self.radioSwitch.GetLabel() == 'OFF':
            print('Radio ON')
            self.deh.radioOn = 1
            self.radioSwitch.SetLabel('ON')
        elif self.radioSwitch.GetLabel() == 'ON':
            print('Radio OFF')
            self.deh.radioOn = 0
            self.radioSwitch.SetLabel('OFF')
        else:
            pass

    def OnClickArmSwitch(self, event):
        if self.armButton1.GetLabel() == 'ARM':
            print('ARM')
            self.deh.radioOn = 3
            self.armButton1.SetLabel('DISARM')
        elif self.armButton1.GetLabel() == 'DISARM':
            print('DISARM')
            self.deh.radioOn = 1
            self.armButton1.SetLabel('ARM')
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
            # Quad 1
            self.armLight1.SetBackgroundColour((220,220,220))
            self.levelLight1.SetBackgroundColour((220,220,220))
            self.altLight1.SetBackgroundColour((220,220,220))
            self.posLight1.SetBackgroundColour((220,220,220))
            self.navLight1.SetBackgroundColour((220,220,220))
            self.gcsLight1.SetBackgroundColour((220,220,220))
            self.voltageLight1.SetBackgroundColour((220,220,220))
            self.voltageLight1.SetLabel('0.0 V')
            # Quad 2
            self.armLight2.SetBackgroundColour((220,220,220))
            self.levelLight2.SetBackgroundColour((220,220,220))
            self.altLight2.SetBackgroundColour((220,220,220))
            self.posLight2.SetBackgroundColour((220,220,220))
            self.navLight2.SetBackgroundColour((220,220,220))
            self.gcsLight2.SetBackgroundColour((220,220,220))
            self.voltageLight2.SetBackgroundColour((220,220,220))
            self.voltageLight2.SetLabel('0.0 V')
            # Quad 3
            self.armLight3.SetBackgroundColour((220,220,220))
            self.levelLight3.SetBackgroundColour((220,220,220))
            self.altLight3.SetBackgroundColour((220,220,220))
            self.posLight3.SetBackgroundColour((220,220,220))
            self.navLight3.SetBackgroundColour((220,220,220))
            self.gcsLight3.SetBackgroundColour((220,220,220))
            self.voltageLight3.SetBackgroundColour((220,220,220))
            self.voltageLight3.SetLabel('0.0 V')

            self.deh.serialOn = False
        else:
            pass
