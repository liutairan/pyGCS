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
from os import walk
import sys
from sys import stdout

import wx
from InputDialog import InputDialog
from ParseMissionFile import ParseMissionFile
from WriteMissionFile import WriteMissionFile

__author__ = "Tairan Liu"
__copyright__ = "Copyright 2017, Tairan Liu"
__credits__ = ["Tairan Liu", "Other Supporters"]
__license__ = "MIT"
__version__ = "0.4-dev"
__maintainer__ = "Tairan Liu"
__email__ = "liutairan2012@gmail.com"
__status__ = "Development"

class TabThree(wx.Panel):
    def __init__(self, parent, DEH):
        wx.Panel.__init__(self, parent)
        self.deh = DEH
        self.deh.bind_to(self.OnUpdate)
        self.addr_long = '\x00\x13\xA2\x00\x40\xC1\x43\x0B'
        self.addr = '\xFF\xFE'
        self._waypointList = []
        self.InitUI()

    def InitUI(self):
        # address and connect
        addressLong = wx.StaticText(self, -1, 'Address Long: 0013A200 40C1430B', pos = (0,10), size = (70,20))
        self.connectButton = wx.Button(self, -1, 'Connect', pos = (280,5), size = (90,20))
        self.Bind(wx.EVT_BUTTON, self.OnClickConnect, self.connectButton)

        # Boxes
        innerStaticBox = wx.StaticBox(self, -1, 'Inner States', pos = (0,30), size = (150,200))
        outerStaticBox = wx.StaticBox(self, -1, 'Outer States', pos = (160,30), size = (150,200))
        sensorStaticBox = wx.StaticBox(self, -1, 'Sensor', pos = (320, 30), size = (70, 200))
        statusLights = wx.StaticBox(self, -1, 'Status', pos = (400,30), size = (70,200))

        # Outer status
        self.lat = wx.StaticText(self, -1, 'Lat: ', pos = (165,45), size = (70,20))
        self.lon = wx.StaticText(self, -1, 'Lon: ', pos = (165,70), size = (70,20))
        self.alt = wx.StaticText(self, -1, 'Alt: ', pos = (165,95), size = (70,20))
        self.numberSat = wx.StaticText(self, -1, 'No. Sat: ', pos = (165,120), size = (70,20))
        self.fixType = wx.StaticText(self, -1, 'Fix Type: ', pos = (165,145), size = (70,20))
        self.hdop = wx.StaticText(self, -1, 'HDOP: ', pos = (165,170), size = (70,20))

        # Inner status
        self.heading = wx.StaticText(self, -1, 'Heading: ', pos = (5,45), size = (140,20))
        self.angx = wx.StaticText(self, -1, 'ANG-X:', pos = (5,70), size = (140,20))
        self.angy = wx.StaticText(self, -1, 'ANG-Y:', pos = (5,95), size = (140,20))

        # Sensors
        self.accLight1 = wx.StaticText(self, -1, 'ACC', pos = (325,45), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.accLight1.SetBackgroundColour((220,220,220))
        self.magLight1 = wx.StaticText(self, -1, 'MAG', pos = (325,65), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.magLight1.SetBackgroundColour((220,220,220))
        self.baroLight1 = wx.StaticText(self, -1, 'BARO', pos = (325,85), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.baroLight1.SetBackgroundColour((220,220,220))
        self.sonarLight1 = wx.StaticText(self, -1, 'SONAR', pos = (325,105), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.sonarLight1.SetBackgroundColour((220,220,220))
        self.gpsLight1 = wx.StaticText(self, -1, 'GPS', pos = (325,125), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.gpsLight1.SetBackgroundColour((220,220,220))
        self.pitotLight1 = wx.StaticText(self, -1, 'PITOT', pos = (325,145), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.pitotLight1.SetBackgroundColour((220,220,220))
        self.hwLight1 = wx.StaticText(self, -1, 'HW', pos = (325,165), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.hwLight1.SetBackgroundColour((220,220,220))

        # Status
        self.quadLabel1 = wx.StaticText(self, -1, 'QUAD 2', pos = (405,43), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)

        self.connectLight1 = wx.StaticText(self, -1, 'NO CON', pos = (405,63), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.connectLight1.SetBackgroundColour((255,0,0))
        self.armLight1 = wx.StaticText(self, -1, 'DISARM', pos = (405,83), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.armLight1.SetBackgroundColour((220,220,220))
        self.levelLight1 = wx.StaticText(self, -1, 'LEVEL', pos = (405,103), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.levelLight1.SetBackgroundColour((220,220,220))
        self.altLight1 = wx.StaticText(self, -1, 'ALT', pos = (405,123), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.altLight1.SetBackgroundColour((220,220,220))
        self.posLight1 = wx.StaticText(self, -1, 'POS', pos = (405,143), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.posLight1.SetBackgroundColour((220,220,220))
        self.navLight1 = wx.StaticText(self, -1, 'NAV', pos = (405,163), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.navLight1.SetBackgroundColour((220,220,220))
        self.gcsLight1 = wx.StaticText(self, -1, 'GCS', pos = (405,183), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.gcsLight1.SetBackgroundColour((220,220,220))
        self.voltLight1 = wx.StaticText(self, -1, '0.0 V', pos = (405,203), size = (60,20),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.voltLight1.SetBackgroundColour((220,220,220))

        # Buttons
        self.editWPButton1 = wx.Button(self, -1, 'Edit', pos = (0,280), size = (50,20))
        self.uploadWPButton1 = wx.Button(self, -1, 'Upload', pos = (55,280), size = (65,20))
        self.Bind(wx.EVT_BUTTON, self.OnClickUploadWPButton, self.uploadWPButton1)
        self.downloadWPButton1 = wx.Button(self, -1, 'Download', pos = (125,280), size = (75,20))
        self.Bind(wx.EVT_BUTTON, self.OnClickDownloadWPButton, self.downloadWPButton1)
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

    def FormatWPs(self, waypointList):
        retList = []
        for i in range(len(waypointList)):
            tempDict = waypointList[i]
            temptype = str(tempDict['type'])
            temptypeId = 0x04
            if temptype == 'WP':
                temptypeId = 0x01
            elif temptype == 'RTH':
                temptypeId = 0x04
            elif temptype == 'POS_UN':
                temptypeId = 0x02
            elif temptype == 'POS_TIME':
                temptypeId = 0x03
            else:
                pass
            tempList = [tempDict['id'],temptypeId,
                        int(tempDict['lat']*(10**7)), int(tempDict['lon']*(10**7)), int(tempDict['alt']),
                        int(tempDict['p1']), int(tempDict['p2']), int(tempDict['p3']), 0x00]
            retList.append(tempList)
        retList[-1][-1] = 0xa5
        return retList

    def OnClickUploadWPButton(self, event):
        if len(self._waypointList) > 0:
            self.deh._waypointLists_air[1] = self.FormatWPs(self._waypointList)
            self.deh.serialMode = 12
        else:
            print('No WP defined.')

    def OnClickDownloadWPButton(self, event):
        self.deh.serialMode = 22

    def OnUpdate(self, global_obj):
        if global_obj.sensor_flags['acc'] == 1:
            self.accLight1.SetBackgroundColour((0,255,0))
        elif global_obj.sensor_flags['acc'] == 0:
            self.accLight1.SetBackgroundColour((255,0,0))
        pass

        if global_obj.sensor_flags['mag'] == 1:
            self.magLight1.SetBackgroundColour((0,255,0))
        elif global_obj.sensor_flags['mag'] == 0:
            self.magLight1.SetBackgroundColour((255,0,0))
        pass

        if global_obj.sensor_flags['baro'] == 1:
            self.baroLight1.SetBackgroundColour((0,255,0))
        elif global_obj.sensor_flags['baro'] == 0:
            self.baroLight1.SetBackgroundColour((255,0,0))
        pass

        if global_obj.sensor_flags['sonar'] == 1:
            self.sonarLight1.SetBackgroundColour((0,255,0))
        elif global_obj.sensor_flags['sonar'] == 0:
            self.sonarLight1.SetBackgroundColour((255,0,0))
        pass

        if global_obj.sensor_flags['gps'] == 1:
            self.gpsLight1.SetBackgroundColour((0,255,0))
        elif global_obj.sensor_flags['gps'] == 0:
            self.gpsLight1.SetBackgroundColour((255,0,0))
        pass

        if global_obj.sensor_flags['pitot'] == 1:
            self.pitotLight1.SetBackgroundColour((0,255,0))
        elif global_obj.sensor_flags['pitot'] == 0:
            self.pitotLight1.SetBackgroundColour((255,0,0))
        pass

        if global_obj.sensor_flags['hardware'] == 0:
            self.hwLight1.SetBackgroundColour((0,255,0))
        elif global_obj.sensor_flags['hardware'] == 1:
            self.hwLight1.SetBackgroundColour((255,0,0))
        pass

        # flight modes
        #print(global_obj.flightModes)
        if global_obj.flightModes['ARM'] == 1:
            self.armLight1.SetLabel('ARMED')
            self.armLight1.SetBackgroundColour((255,0,0))
        elif global_obj.flightModes['ARM'] == 0:
            self.armLight1.SetLabel('DISARM')
            self.armLight1.SetBackgroundColour((0,255,0))
        else:
            pass

        if global_obj.flightModes['ANGLE'] == 1:
            self.levelLight1.SetBackgroundColour((0,255,0))
        elif global_obj.flightModes['ANGLE'] == 0:
            self.levelLight1.SetBackgroundColour((255,0,0))
        else:
            pass

        if global_obj.flightModes['ALTHOLD'] == 1:
            self.altLight1.SetBackgroundColour((0,255,0))
        elif global_obj.flightModes['ALTHOLD'] == 0:
            self.altLight1.SetBackgroundColour((255,0,0))
        else:
            pass

        if global_obj.flightModes['POSHOLD'] == 1:
            self.posLight1.SetBackgroundColour((0,255,0))
        elif global_obj.flightModes['POSHOLD'] == 0:
            self.posLight1.SetBackgroundColour((255,0,0))
        else:
            pass

        if (global_obj.flightModes['NAVWP'] == 1) or (global_obj.flightModes['NAVRTH'] == 1):
            self.navLight1.SetBackgroundColour((0,255,0))
        elif (global_obj.flightModes['NAVWP'] == 0) or (global_obj.flightModes['NAVRTH'] == 1):
            self.navLight1.SetBackgroundColour((255,0,0))
        else:
            pass

        if global_obj.flightModes['GCSNAV'] == 1:
            self.gcsLight1.SetBackgroundColour((0,255,0))
        elif global_obj.flightModes['GCSNAV'] == 0:
            self.gcsLight1.SetBackgroundColour((255,0,0))
        else:
            pass

        self.heading.SetLabel('Heading: '+str(global_obj.msp_attitude['heading']))
        self.angx.SetLabel('ANG-X: '+str(global_obj.msp_attitude['angx']))
        self.angy.SetLabel('ANG-Y: '+str(global_obj.msp_attitude['angy']))

        # Outer states
        self.lat.SetLabel('Lat: '+str(global_obj.msp_raw_gps['gps_lat']))
        self.lon.SetLabel('Lon: '+str(global_obj.msp_raw_gps['gps_lon']))
        self.alt.SetLabel('Alt: '+str(global_obj.msp_raw_gps['gps_altitude']))
        self.numberSat.SetLabel('No. Sat: '+str(global_obj.msp_raw_gps['gps_numsat']))
        self.fixType.SetLabel('Fix Type: '+str(global_obj.msp_raw_gps['gps_fix']))
        self.hdop.SetLabel('HDOP: '+str(global_obj.msp_raw_gps['gps_hdop']))

        self.voltLight1.SetLabel(str(global_obj.msp_analog['vbat']/10.0)+' V')
        if global_obj.msp_analog['vbat'] >= 114:
            self.voltLight1.SetBackgroundColour((0,255,0))
        elif (global_obj.msp_analog['vbat'] >= 108) and (global_obj.msp_analog['vbat'] < 114):
            self.voltLight1.SetBackgroundColour((255,200,0))
        elif (global_obj.msp_analog['vbat'] >= 102) and (global_obj.msp_analog['vbat'] < 108):
            self.voltLight1.SetBackgroundColour((255,0,0))
        else:
            self.voltLight1.SetBackgroundColour((255,0,0))

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
            self._waypointList.append({'id':index+1,
                                       'type':tempList[0],
                                       'lat':float(tempList[1]),
                                       'lon':float(tempList[2]),
                                       'alt':float(tempList[3]),
                                       'p1':int(tempList[4]),
                                       'p2':int(tempList[5]),
                                       'p3':int(tempList[6])
                                       })
            self.deh._waypointLists[1] = self._waypointList
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
            self._waypointList[index] = {'id':index+1,
                                         'type':tempList[0],
                                         'lat':float(tempList[1]),
                                         'lon':float(tempList[2]),
                                         'alt':float(tempList[3]),
                                         'p1':int(tempList[4]),
                                         'p2':int(tempList[5]),
                                         'p3':int(tempList[6])
                                         }
            self.deh._waypointLists[1] = self._waypointList
        dlg.Destroy()

    def OnPopupMenuDelete(self,event, item):
        itemId = event.GetId()
        menu = event.GetEventObject()
        menuItem = menu.FindItemById(itemId)

        index = int(item)-1
        self.wpList.DeleteItem(index)
        for i in range(self.wpList.GetItemCount()):
            self.wpList.SetStringItem(i,0,str(i+1))

        self._waypointList.pop(index)
        for i in range(len(self._waypointList)):
            self._waypointList[i]['id'] = i+1
        self.deh._waypointLists[1] = self._waypointList

    def OnPopupMenuClear(self,event):
        itemId = event.GetId()
        menu = event.GetEventObject()
        menuItem = menu.FindItemById(itemId)
        dlg = wx.MessageDialog(self, "Clear all WPs", "Warning", wx.ICON_EXCLAMATION|wx.YES_NO)
        if dlg.ShowModal() == wx.ID_YES:
            self.wpList.DeleteAllItems()
            self._waypointList = []
            self.deh._waypointLists[1] = self._waypointList
        else:
            pass

    def OnPopupMenuLoad(self,event):
        itemId = event.GetId()
        menu = event.GetEventObject()
        menuItem = menu.FindItemById(itemId)
        wildcard="Text Files (*.txt)|*.txt"
        dlg = wx.FileDialog(self, "Choose a WP File", os.getcwd(), "", wildcard, wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            tempPath = dlg.GetPath()
            tempData = ParseMissionFile(tempPath)
            self._waypointList = tempData
            self.deh._waypointLists[1] = self._waypointList
            self.wpList.DeleteAllItems()
            for i in range(len(self._waypointList)):
                index = self.wpList.InsertStringItem(sys.maxint, str(i+1))
                temp_line_dict = self._waypointList[i]
                tempList = [temp_line_dict['type'], str(temp_line_dict['lat']), str(temp_line_dict['lon']), str(temp_line_dict['alt']),
                            str(temp_line_dict['p1']), str(temp_line_dict['p2']), str(temp_line_dict['p3'])]
                for j in range(7):
                    self.wpList.SetStringItem(i, j+1, tempList[j])

    def OnPopupMenuSave(self,event):
        itemId = event.GetId()
        menu = event.GetEventObject()
        menuItem = menu.FindItemById(itemId)
        wildcard="Text Files (*.txt)|*.txt"
        dlg = wx.FileDialog(self, "Save to WP File", os.getcwd(), "", wildcard, wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            tempPath = dlg.GetPath()
            WriteMissionFile(tempPath, self._waypointList)

    def OnClickConnect(self,event):
        if self.connectButton.GetLabel() == 'Connect':
            print('Quad 2 Connected')
            self.connectButton.SetLabel('Disconnect')
            self.connectLight1.SetLabel('CONN')
            self.connectLight1.SetBackgroundColour((0,255,0))
            self.deh.addressList = [self.deh.addressList[0], [self.addr_long, self.addr], self.deh.addressList[2]]
        elif self.connectButton.GetLabel() == 'Disconnect':
            print('Quad 2 Disconnected')
            self.connectLight1.SetLabel('NO CON')
            self.connectLight1.SetBackgroundColour((255,0,0))
            self.connectButton.SetLabel('Connect')
            self.deh.addressList = [self.deh.addressList[0], [], self.deh.addressList[2]]

    def OnAdd(self, templat, templon):
        tempCount = self.wpList.GetItemCount()
        dlg = InputDialog(self, "Add WP", str(tempCount+1))
        temp2 = str(templat)
        dlg.latText.SetValue(temp2)
        temp3 = str(templon)
        dlg.lonText.SetValue(temp3)

        if dlg.ShowModal() == wx.ID_OK:
            tempList = dlg.GetValue()
            index = self.wpList.InsertStringItem(sys.maxint, str(tempCount+1))
            for i in range(7):
                self.wpList.SetStringItem(index, i+1, tempList[i])
            self._waypointList.append({'id':index+1,
                                       'type':tempList[0],
                                       'lat':float(tempList[1]),
                                       'lon':float(tempList[2]),
                                       'alt':float(tempList[3]),
                                       'p1':int(tempList[4]),
                                       'p2':int(tempList[5]),
                                       'p3':int(tempList[6])
                                       })
            self.deh._waypointLists[1] = self._waypointList
        else:
            pass
        dlg.Destroy()
