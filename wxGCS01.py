#!/usr/bin/pythonw
# -*- coding: UTF-8 -*-

import os
import sys
import wx
import wx.lib.embeddedimage
import wx.dataview
from threading import Thread
from wx.lib.pubsub import pub

import serial
import serial.tools.list_ports
import math
import time
import threading
import numpy
from os import walk
import matplotlib
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from PIL import Image

#from GSMPy import GSMPy

class InputDialog(wx.Dialog):
    def __init__(self, parent, title, id):
        super(InputDialog, self).__init__(parent, title=title,size=(240,270))
        self.InitUI(id)

    def InitUI(self, id):
        panel=wx.Panel(self)
        
        self.idLabel = wx.StaticText(panel, -1, 'ID', size = (50,20), pos = (20,10))
        self.idText = wx.TextCtrl(panel, size = (90,20), pos = (70,10), style = wx.TE_READONLY)
        self.idText.SetValue(id)
        self.idText.SetEditable(False)
        
        self.typeLabel = wx.StaticText(panel, -1, 'Type', size = (50,20), pos = (20,35))
        WPTypes = ['WP','POS_UN','POS_TIME','RTH','LAND','SET_POI']
        self.type = wx.ComboBox(panel, choices=WPTypes, size = (120,25), pos = (70,35))
        
        self.latLabel = wx.StaticText(panel, -1, 'Lat', size = (50,20), pos = (20,70))
        self.latText = wx.TextCtrl(panel, size = (90,20), pos = (70,70))
        
        self.lonLabel = wx.StaticText(panel, -1, 'Lon', size = (50,20), pos = (20,95))
        self.lonText = wx.TextCtrl(panel, size = (90,20), pos = (70,95))
        
        self.altLabel = wx.StaticText(panel, -1, 'Alt', size = (50,20), pos = (20,120))
        self.altText = wx.TextCtrl(panel, size = (90,20), pos = (70,120))
        
        self.p1Label = wx.StaticText(panel, -1, 'P1', size = (50,20), pos = (20,145))
        self.p1Text = wx.TextCtrl(panel, size = (90,20), pos = (70,145))
        
        self.p2Label = wx.StaticText(panel, -1, 'P2', size = (50,20), pos = (20,170))
        self.p2Text = wx.TextCtrl(panel, size = (90,20), pos = (70,170))
        
        self.p3Label = wx.StaticText(panel, -1, 'P3', size = (50,20), pos = (20,195))
        self.p3Text = wx.TextCtrl(panel, size = (90,20), pos = (70,195))
        
        self.btn = wx.Button(panel,wx.ID_OK,label="OK",size=(50,20),pos=(70,220))
        self.btn = wx.Button(panel,wx.ID_CANCEL,label="CANCEL",size=(70,20),pos=(125,220))

    def GetValue(self):
        dataRet = [self.type.GetValue(), self.latText.GetValue(), self.lonText.GetValue(), self.altText.GetValue(), self.p1Text.GetValue(), self.p2Text.GetValue(), self.p3Text.GetValue()]
        return dataRet

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
            os.system('say Ha')
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
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.workerVoice = None
        self.InitUI()

    def InitUI(self):
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
        
        self.voiceSwitch = wx.Button(self, -1, 'OFF', pos = (340,10), size = (60,20))
        self.Bind(wx.EVT_BUTTON,self.OnClickVoiceSwitch, self.voiceSwitch)
        
        serialPortInfo = list(serial.tools.list_ports.comports())
        serialPorts = []
        for i in range(len(serialPortInfo)):
            serialPorts.append(serialPortInfo[i][0])
        self.serialPortComboBox = wx.ComboBox(self, choices=serialPorts, size = (300,25), pos = (10,100))
        self.connectButton = wx.Button(self, -1, 'Connect', pos = (320,95), size = (90,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.Bind(wx.EVT_BUTTON, self.OnClickSerialConnect, self.connectButton)

        # Status
        quadLabel1 = wx.StaticText(self, -1, 'QUAD 1', pos = (5,410), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        connectLight1 = wx.StaticText(self, -1, 'NO CON', pos = (5,430), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        connectLight1.SetBackgroundColour((255,0,0))
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
        
        quadLabel2 = wx.StaticText(self, -1, 'QUAD 2', pos = (75,410), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        connectLight2 = wx.StaticText(self, -1, 'NO CON', pos = (75,430), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        connectLight2.SetBackgroundColour((255,0,0))
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
        
        quadLabel3 = wx.StaticText(self, -1, 'QUAD 3', pos = (145,410), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        connectLight3 = wx.StaticText(self, -1, 'NO CON', pos = (145,430), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        connectLight3.SetBackgroundColour((255,0,0))
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

    def OnClickVoiceSwitch(self, event):
        #print(self.workerVoice)
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
        elif self.connectButton.GetLabel() == 'Disconnect':
            print('Disconnected')
            self.connectButton.SetLabel('Connect')

class TabTwo(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.InitUI()
        
    def InitUI(self):
        # Boxes
        innerStaticBox = wx.StaticBox(self, -1, 'Inner States', pos = (0,0), size = (150,200))
        outerStaticBox = wx.StaticBox(self, -1, 'Outer States', pos = (160,0), size = (150,200))
        statusLights = wx.StaticBox(self, -1, 'Status', pos = (420,0), size = (70,200))

        lat = wx.StaticText(self, -1, 'Lat', pos = (0,10), size = (70,20))
        lon = wx.StaticText(self, -1, 'Lon', pos = (0,35), size = (70,20))
        alt = wx.StaticText(self, -1, 'Alt', pos = (0,60), size = (70,20))
        heading = wx.StaticText(self, -1, 'Heading', pos = (0,85), size = (70,20))
        
        numberSat = wx.StaticText(self, -1, 'No. Sat', pos = (0,110), size = (70,20))
        '''
        lon
        alt
        heading
        No. Satellites
        Speed
        
        gps mode
        
        tx rx
        cycle
        message
        '''

        # Status
        quadLabel1 = wx.StaticText(self, -1, 'QUAD 1', pos = (425,10), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        connectLight1 = wx.StaticText(self, -1, 'NO CON', pos = (425,30), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        connectLight1.SetBackgroundColour((255,0,0))
        armLight1 = wx.StaticText(self, -1, 'DISARM', pos = (425,50), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        armLight1.SetBackgroundColour((220,220,220))
        levelLight1 = wx.StaticText(self, -1, 'LEVEL', pos = (425,70), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        levelLight1.SetBackgroundColour((220,220,220))
        altLight1 = wx.StaticText(self, -1, 'ALT', pos = (425,90), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        altLight1.SetBackgroundColour((220,220,220))
        posLight1 = wx.StaticText(self, -1, 'POS', pos = (425,110), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        posLight1.SetBackgroundColour((220,220,220))
        navLight1 = wx.StaticText(self, -1, 'NAV', pos = (425,130), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        navLight1.SetBackgroundColour((220,220,220))
        gcsLight1 = wx.StaticText(self, -1, 'GCS', pos = (425,150), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        gcsLight1.SetBackgroundColour((220,220,220))

        # Buttons
        self.editWPButton1 = wx.Button(self, -1, 'Edit', pos = (0,280), size = (50,20))
        self.uploadWPButton1 = wx.Button(self, -1, 'Upload', pos = (55,280), size = (65,20))
        self.downloadWPButton1 = wx.Button(self, -1, 'Download', pos = (125,280), size = (75,20))
        self.startMissionButton1 = wx.Button(self, -1, 'Start', pos = (205,280), size = (60,20))
        self.abortMissionButton1 = wx.Button(self, -1, 'Abort', pos = (270,280), size = (60,20))
        
        # List
        self.wpList = wx.ListCtrl(self, -1, pos = (8,310),size = (480,280), style = wx.LC_REPORT|wx.BORDER_SUNKEN|wx.LC_HRULES|wx.LC_VRULES)
        self.wpList.InsertColumn(0,'ID',width=30)
        self.wpList.InsertColumn(1,'Type',width=70)
        self.wpList.InsertColumn(2,'Lat',width=80)
        self.wpList.InsertColumn(3,'Lon',width=80)
        self.wpList.InsertColumn(4,'Alt',width=60)
        self.wpList.InsertColumn(5,'P1',width=50)
        self.wpList.InsertColumn(6,'P2',width=50)
        self.wpList.InsertColumn(7,'P3',width=50)
        
        # Popup Menu
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.OnListRightClick, self.wpList)
        
        
        # Show
        self.Show(True)

    def OnListRightClick(self,event):
        tempStr = event.GetText()
        if len(tempStr) > 0:
            self.OnContextListItem(event,tempStr)
        else:
            self.OnContextListEmpty(event)
    
    def OnContextListItem(self, event, item):
        if not hasattr(self, "Add"):
            self.itemAdd = wx.NewId()
            self.itemEdit = wx.NewId()
            self.itemDelete = wx.NewId()
            self.itemClear = wx.NewId()
            self.itemLoadFromFile = wx.NewId()
            self.itemSaveAll = wx.NewId()
            
            self.Bind(wx.EVT_MENU, self.OnPopupMenuAdd, id=self.itemAdd)
            self.Bind(wx.EVT_MENU, lambda event: self.OnPopupMenuEdit(event, item), id=self.itemEdit)
            self.Bind(wx.EVT_MENU, lambda event: self.OnPopupMenuDelete(event, item), id=self.itemDelete)
            self.Bind(wx.EVT_MENU, self.OnPopupMenuClear, id=self.itemClear)
            self.Bind(wx.EVT_MENU, self.OnPopupMenuLoad, id=self.itemLoadFromFile)
            self.Bind(wx.EVT_MENU, self.OnPopupMenuSave, id=self.itemSaveAll)
        
        # build the menu
        menu = wx.Menu()
        itemAdd = menu.Append(self.itemAdd, "Add")
        itemEdit = menu.Append(self.itemEdit, "Edit")
        itemDelete = menu.Append(self.itemDelete, "Delete")
        itemClear = menu.Append(self.itemClear, "Clear All")
        itemLoadFromFile = menu.Append(self.itemLoadFromFile, "Load")
        itemSaveAll = menu.Append(self.itemSaveAll, "Save All")
 
        # show the popup menu
        self.PopupMenu(menu)
        menu.Destroy()

    def OnContextListEmpty(self, event):
        if not hasattr(self, "Add"):
            self.itemAdd = wx.NewId()
            self.itemEdit = wx.NewId()
            self.itemDelete = wx.NewId()
            self.itemClear = wx.NewId()
            self.itemLoadFromFile = wx.NewId()
            self.itemSaveAll = wx.NewId()
            
            self.Bind(wx.EVT_MENU, self.OnPopupMenuAdd, id=self.itemAdd)
            self.Bind(wx.EVT_MENU, self.OnPopupMenuLoad, id=self.itemLoadFromFile)
        # build the menu
        menu = wx.Menu()
        itemAdd = menu.Append(self.itemAdd, "Add")
        itemLoadFromFile = menu.Append(self.itemLoadFromFile, "Load")
 
        # show the popup menu
        self.PopupMenu(menu)
        menu.Destroy()

    def OnPopupMenuAdd(self,event):
        itemId = event.GetId()
        menu = event.GetEventObject()
        menuItem = menu.FindItemById(itemId)
        
        tempCount = self.wpList.GetItemCount()
        dlg = InputDialog(self, "Add WP", str(tempCount+1))
        if dlg.ShowModal() == wx.ID_OK:
            tempList = dlg.GetValue()
            index = self.wpList.InsertStringItem(sys.maxint, str(tempCount+1))
            for i in range(7):
                self.wpList.SetStringItem(index, i+1, tempList[i])
        else:
            pass
        dlg.Destroy()

    def OnPopupMenuEdit(self,event,item):
        itemId = event.GetId()
        menu = event.GetEventObject()
        menuItem = menu.FindItemById(itemId)
        #print menuItem.GetLabel()
        dlg = InputDialog(self, "Edit WP", str(int(item)))
        
        temp1 = self.wpList.GetItemText(int(item)-1, col=1)
        dlg.type.SetValue(temp1)
        temp2 = self.wpList.GetItemText(int(item)-1, col=2)
        dlg.latText.SetValue(temp2)
        temp3 = self.wpList.GetItemText(int(item)-1, col=3)
        dlg.lonText.SetValue(temp3)
        temp4 = self.wpList.GetItemText(int(item)-1, col=4)
        dlg.altText.SetValue(temp4)
        temp5 = self.wpList.GetItemText(int(item)-1, col=5)
        dlg.p1Text.SetValue(temp5)
        temp6 = self.wpList.GetItemText(int(item)-1, col=6)
        dlg.p2Text.SetValue(temp6)
        temp7 = self.wpList.GetItemText(int(item)-1, col=7)
        dlg.p3Text.SetValue(temp7)
        
        
        if dlg.ShowModal() == wx.ID_OK:
            tempList = dlg.GetValue()
            index = int(item)-1
            for i in range(7):
                self.wpList.SetStringItem(index, i+1, tempList[i])
        dlg.Destroy()

    def OnPopupMenuDelete(self,event, item):
        itemId = event.GetId()
        menu = event.GetEventObject()
        menuItem = menu.FindItemById(itemId)
        #print menuItem.GetLabel()
        
        self.wpList.DeleteItem(int(item)-1)
        for i in range(self.wpList.GetItemCount()):
            self.wpList.SetStringItem(i,0,str(i+1))

    def OnPopupMenuClear(self,event):
        itemId = event.GetId()
        menu = event.GetEventObject()
        menuItem = menu.FindItemById(itemId)
        dlg = wx.MessageDialog(self, "Clear all WPs", "Warning", wx.ICON_EXCLAMATION|wx.YES_NO)
        if dlg.ShowModal() == wx.ID_YES:
            self.wpList.DeleteAllItems()
        else:
            pass

    def OnPopupMenuLoad(self,event):
        itemId = event.GetId()
        menu = event.GetEventObject()
        menuItem = menu.FindItemById(itemId)
        print menuItem.GetLabel()
        wildcard="Text Files (*.txt)|*.txt"
        dlg = wx.FileDialog(self, "Choose a WP File", os.getcwd(), "", wildcard, wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            tempData = []
            with open(dlg.GetPath(), 'r') as inf:
                tempData = inf.readlines()
    
    def OnPopupMenuSave(self,event):
        itemId = event.GetId()
        menu = event.GetEventObject()
        menuItem = menu.FindItemById(itemId)
        print menuItem.GetLabel()



 
class TabThree(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        t = wx.StaticText(self, -1, "Quad 2", (20,20))
 
class TabFour(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        t = wx.StaticText(self, -1, "Quad 3", (20,20))


class SerialCommunication():
    def __init__(self):
        pass


class MainFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(MainFrame, self).__init__(*args, **kw)

        #self.tbicon = DemoTaskBarIcon(self)

        # Mouse states
        self.inWindowFlag = 0
        self.inMapFlag = 0
        self.leftDown = 0
        self.rightDown = 0
        
        # Map Info
        self.WIDTH = 640
        self.HEIGHT = 640

        
        self.LATITUDE  =  30.408158 #37.7913838
        self.LONGITUDE = -91.179533 #-79.44398934
        
        self.ZOOM = 21
        self.MAPTYPE = 'hybrid' #'roadmap'

        self.homeLat = self.LATITUDE
        self.homeLon = self.LONGITUDE
        
        self.dX = 0
        self.dY = 0
        
        self.waypoints = []
        
        self.InitUI()

    def InitUI(self):
        pnl = wx.Panel(self)
        self.SetSize((1150,640))
        self.SetTitle("GCS")
        self.Center()

        # Events
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_IDLE,self.OnIdle)
        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        #self.Bind(wx.EVT_CONTEXT_MENU, self.OnContext)

        # Panel Elements
        # Create Empty Image to preload
        self.image = wx.EmptyImage(640,640)
        self.imageCtrl = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(self.image), pos=(0, 0))

        # Bind Mouse Events
        self.imageCtrl.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.imageCtrl.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.imageCtrl.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseRightDown)
        self.imageCtrl.Bind(wx.EVT_RIGHT_UP, self.OnMouseRightUp)
        self.imageCtrl.Bind(wx.EVT_MOTION, self.OnMotion)
        self.imageCtrl.Bind(wx.EVT_MOUSEWHEEL, self.OnScroll)
        self.imageCtrl.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterMap)
        self.imageCtrl.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveMap)
        
        pnl.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        pnl.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        pnl.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseRightDown)
        pnl.Bind(wx.EVT_RIGHT_UP, self.OnMouseRightUp)
        pnl.Bind(wx.EVT_MOTION, self.OnMotion)
        #self.Bind(wx.EVT_MOUSEWHEEL, self.OnScroll)
        pnl.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
        pnl.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

        # Tabs
        nb = wx.Notebook(pnl, pos = (642,0), size = (510, 615))
        
        tab1 = TabOne(nb)
        tab2 = TabTwo(nb)
        tab3 = TabThree(nb)
        tab4 = TabFour(nb)

        # Add the windows to tabs and name them.
        nb.AddPage(tab1, "Overview")
        nb.AddPage(tab2, "Quad 1")
        nb.AddPage(tab3, "Quad 2")
        nb.AddPage(tab4, "Quad 3")
        
        # Button Events
        #buttonStaticBox = wx.StaticBox(pnl, -1, 'Buttons', pos = (645,0), size = (300,240))
        #flightStaticBox = wx.StaticBox(pnl, -1, 'Flight Data', pos = (645,245), size = (300,240))
        
        # Show
        self.Show(True)

    def OnQuitApp(self, event):
        self.Close()

    def OnKeyUp(self, event):
        keyNumber = event.GetKeyCode()
        #print(keyNumber)
        if keyNumber == 27:
            self.Close()

    def OnSize(self, event):
        event.Skip()
        self.Refresh()
    
    def OnPaint(self, event):
        w, h = self.GetClientSize()
        
        
        #self.image = self.goompy.getImage()
        #self.image = self.mapImage
        #self.imageCtrl.SetBitmap(wx.BitmapFromImage(PilImageToWxImage(self.image)))
        '''
        self.image = self.mapImage
        tempImage = wx.BitmapFromImage(PilImageToWxImage(self.image))
        self.dc = wx.MemoryDC(tempImage)

        self.dc.SetPen(wx.Pen("BLACK", style = wx.TRANSPARENT))
        
        try:
            if len(self.waypoints) > 0:
                # Points
                for i in range(len(self.waypoints)):
                    if i == 0:
                        self.dc.SetBrush(wx.Brush("BLUE", wx.SOLID))
                        self.dc.DrawCircle(self.waypointsOnImage[i][0], self.waypointsOnImage[i][1],7)
                    else:
                        self.dc.SetBrush(wx.Brush("RED", wx.SOLID))
                        self.dc.DrawCircle(self.waypointsOnImage[i][0], self.waypointsOnImage[i][1],7)
    
                for i in range(len(self.waypoints)):
                    if i < len(self.waypoints)-1:
                        self.dc.SetPen(wx.Pen(wx.GREEN, 1))
                        self.dc.DrawLines(((self.waypointsOnImage[i][0], self.waypointsOnImage[i][1]),(self.waypointsOnImage[i+1][0], self.waypointsOnImage[i+1][1])))
                    else:
                        self.dc.SetPen(wx.Pen(wx.GREEN, 1))
                        self.dc.DrawLines(((self.waypointsOnImage[i][0], self.waypointsOnImage[i][1]),(self.waypointsOnImage[0][0], self.waypointsOnImage[0][1])))
        except:
            pass
        self.dc.SelectObject(wx.NullBitmap)
        self.imageCtrl.SetBitmap(tempImage)
        '''
    
    def OnIdle(self,event):
        self.Refresh(False)

    def OnEnterWindow(self, event):
        #print('Enter Window')
        self.inWindowFlag = 1

    def OnEnterMap(self, event):
        #print('Enter Map')
        self.inMapFlag = 1

    def OnLeaveWindow(self, event):
        #print('Leave Window')
        self.inWindowFlag = 0

    def OnLeaveMap(self, event):
        #print('Leave Map')
        self.inMapFlag = 0

    def OnMouseLeftDown(self, event):
        #print('left down')
        self.leftDown = 1
        self.mouseX, self.mouseY = event.GetPosition()

    def OnMouseLeftUp(self, event):
        #print('left up')
        self.leftDown = 0
    
    def OnMouseRightDown(self, event):
        #print('right down')
        self.rightDown = 1

    def OnMouseRightUp(self, event):
        #print('right up')
        self.rightDown = 0

    def OnMotion(self, event):
        x, y = event.GetPosition()
        if self.inMapFlag == 1 and self.leftDown == 1:
            '''
            dx = x-self.mouseX
            dy = y-self.mouseY
            self.dX = self.dX + dx
            self.dY = self.dY + dy
            #print(x-self.mouseX, y-self.mouseY)
            #self.mouseX = x
            #self.mouseY = y
            latStep, lonStep = CalStepFromGPS(self.handle.lat, self.handle.lon, zoom = self.handle.zoom)
            newLat = self.handle.lat + dy/(1.0*self.HEIGHT)*latStep
            newLon = self.handle.lon - dx/(1.0*self.WIDTH)*lonStep
            self.handle.lat = newLat
            self.handle.lon = newLon
            self.mapImage = PreloadMap(self.handle)
            self.LATITUDE = self.handle.lat
            self.LONGITUDE = self.handle.lon
            #print(self.handle.LATITUDE, self.handle.LONGITUDE)
            '''
            self.Refresh()


    def OnScroll(self, event):
        dlevel = event.GetWheelRotation()
        # +: Down/Left, -: Up/Right
        self.ZOOM = self.ZOOM + dlevel
        if self.ZOOM > 21:
            self.ZOOM = 21
        elif self.ZOOM < 3:
            self.ZOOM = 3
        print(self.ZOOM)
        #self.handle.zoom = self.ZOOM
        #self.goompy = GooMPy(self.WIDTH, self.HEIGHT, self.LATITUDE, self.LONGITUDE, self.ZOOM, self.MAPTYPE)
        #self.mapImage = PreloadMap(self.handle)
        self.Refresh()



def main():
    map = wx.App()
    MainFrame(None)
    map.MainLoop()

if __name__ == "__main__":
    main()



