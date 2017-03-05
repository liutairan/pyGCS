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
from SerialCom import SerialCommunication
from DataExchange import DataExchange
from TabOne import TabOne
from TabTwo import TabTwo
from TabThree import TabThree
from TabFour import TabFour

import math
import time
import struct

import numpy
import matplotlib
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from PIL import Image
from Map import Map

#from GSMPy import GSMPy

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


class MainFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(MainFrame, self).__init__(*args, **kw)

        # Data exchange handle
        self.dataExchangeHandle = DataExchange()

        # Mouse states
        self.inWindowFlag = 0
        self.inMapFlag = 0
        self.leftDown = 0
        self.rightDown = 0
        self.shiftDown = 0
        self.currentTab = 0

        # Map Info
        self._width = 640
        self._height = 640


        self._originLat  =  30.408158 #37.7913838
        self._originLon = -91.179533 #-79.44398934

        self._zoom = 19
        self._maptype = 'hybrid' #'roadmap'

        self._homeLat = self._originLat
        self._homeLon = self._originLon

        self._dX = 0
        self._dY = 0

        self.waypoints = []

        self.InitUI()

    def InitUI(self):
        self.pnl = wx.Panel(self)
        self.SetSize((1150,670))
        self.SetTitle("GCS")
        self.SetClientSize((1150,670))
        self.Center()

        # Events
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_IDLE,self.OnIdle)

        self.pnl.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.pnl.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.pnl.SetFocus()
        #pnl.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        #pnl.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        #self.Bind(wx.EVT_CONTEXT_MENU, self.OnContext)

        # Panel Elements
        # Create Empty Image to preload
        self.mapHandle = Map(self._originLat, self._originLon, self._zoom, self._width, self._height)
        self.mapImage = self.mapHandle.retImage
        self.imageCtrl = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(self.mapImage), pos=(0, 0))

        # Bind Mouse Events
        self.imageCtrl.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.imageCtrl.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.imageCtrl.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseRightDown)
        self.imageCtrl.Bind(wx.EVT_RIGHT_UP, self.OnMouseRightUp)
        self.imageCtrl.Bind(wx.EVT_MOTION, self.OnMotion)
        self.imageCtrl.Bind(wx.EVT_MOUSEWHEEL, self.OnScroll)
        self.imageCtrl.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterMap)
        self.imageCtrl.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveMap)

        self.pnl.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.pnl.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.pnl.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseRightDown)
        self.pnl.Bind(wx.EVT_RIGHT_UP, self.OnMouseRightUp)
        self.pnl.Bind(wx.EVT_MOTION, self.OnMotion)
        #self.Bind(wx.EVT_MOUSEWHEEL, self.OnScroll)
        self.pnl.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
        self.pnl.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

        self.imageCtrl.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.imageCtrl.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        # Tabs
        self.nb = wx.Notebook(self.pnl, pos = (642,0), size = (510, 635))

        self.tab1 = TabOne(self.nb, self.dataExchangeHandle)
        self.tab2 = TabTwo(self.nb, self.dataExchangeHandle)
        self.tab3 = TabThree(self.nb, self.dataExchangeHandle)
        self.tab4 = TabFour(self.nb, self.dataExchangeHandle)

        # Add the windows to tabs and name them.
        self.nb.AddPage(self.tab1, "Overview")
        self.nb.AddPage(self.tab2, "Quad 1")
        self.nb.AddPage(self.tab3, "Quad 2")
        self.nb.AddPage(self.tab4, "Quad 3")

        self.nb.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.nb.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)

        self.nb.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.nb.Bind(wx.EVT_KEY_UP, self.OnKeyUp)

        self.tab1.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.tab1.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.tab2.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.tab2.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.tab3.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.tab3.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.tab4.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.tab4.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        #
        #self.imageCtrl.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        #self.imageCtrl.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        # Button Events
        #buttonStaticBox = wx.StaticBox(pnl, -1, 'Buttons', pos = (645,0), size = (300,240))
        #flightStaticBox = wx.StaticBox(pnl, -1, 'Flight Data', pos = (645,245), size = (300,240))

        # Buttons
        self.incZoomButton = wx.Button(self.pnl, -1, '+', pos = (2, 642), size = (25,20))
        self.Bind(wx.EVT_BUTTON, self.OnIncZoom, self.incZoomButton)
        self.decZoomButton = wx.Button(self.pnl, -1, '-', pos = (27, 642), size = (25,20))
        self.Bind(wx.EVT_BUTTON, self.OnDecZoom, self.decZoomButton)
        self.autoZoomButton = wx.Button(self.pnl, -1, 'Auto Zoom', pos = (55, 642), size = (85,20))
        self.Bind(wx.EVT_BUTTON, self.OnAutoZoom, self.autoZoomButton)
        # Show
        self.Show(True)

    def OnQuitApp(self, event):
        self.Close()

    def OnPageChanged(self, event):
        self.currentTab = event.GetSelection()
        self.dataExchangeHandle.serialMode = self.currentTab
        event.Skip()

    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.nb.GetSelection()
        #print 'OnPageChanging, old:%d, new:%d, sel:%d\n' % (old, new, sel)
        event.Skip()


    def OnKeyDown(self, event):
        keyNumber = event.GetKeyCode()
        print(keyNumber)
        if keyNumber == wx.WXK_SHIFT:
            self.shiftDown = 1

    def OnKeyUp(self, event):
        keyNumber = event.GetKeyCode()
        if keyNumber == 27:
            self.Close()
        elif keyNumber == wx.WXK_SHIFT:
            self.shiftDown = 0

    def OnIncZoom(self, event):
        self._zoom = self._zoom + 1
        self.mapHandle.zoom(1)
        self.Refresh()

    def OnDecZoom(self, event):
        self._zoom = self._zoom - 1
        self.mapHandle.zoom(-1)
        self.Refresh()

    def OnAutoZoom(self, event):
        # auto select the zoom level so that all the waypoints are shown in the frame
        #self._zoom = self._zoom - 1
        #self.mapHandle.zoom(-1)
        self.Refresh()

    def OnSize(self, event):
        event.Skip()
        self.Refresh()

    def OnPaint(self, event):
        self.mapImage = self.mapHandle.retImage
        tempImage = wx.BitmapFromImage(self.mapImage)
        self.dc = wx.MemoryDC(tempImage)

        self.dc.SetPen(wx.Pen("BLACK", style = wx.TRANSPARENT))

        try:
            for dev in range(3):
                self.dc.SetPen(wx.Pen("BLACK", style = wx.TRANSPARENT))
                tempList = self.dataExchangeHandle._waypointLists[dev]
                if len(tempList) > 0:
                    for i in range(len(tempList)):
                        tempWP = tempList[i]
                        x,y = self.mapHandle.GPStoImagePos(tempWP['lat'], tempWP['lon'])
                        if i == 0:
                            self.dc.SetBrush(wx.Brush("BLUE", wx.SOLID))
                            self.dc.DrawCircle(x, y, 7)
                            self.dc.DrawText(str(dev+1), x, y)
                        else:
                            self.dc.SetBrush(wx.Brush("RED", wx.SOLID))
                            self.dc.DrawCircle(x, y, 7)
                    for i in range(len(tempList)):
                        if i < len(tempList)-1:
                            tempWP = tempList[i]
                            x,y = self.mapHandle.GPStoImagePos(tempWP['lat'], tempWP['lon'])
                            tempWP_next = tempList[i+1]
                            x_n,y_n = self.mapHandle.GPStoImagePos(tempWP_next['lat'], tempWP_next['lon'])
                            self.dc.SetPen(wx.Pen(wx.Colour(dev*60,255,255-dev*60), 1))
                            self.dc.DrawLines(((x, y),(x_n, y_n)))
                        else:
                            tempWP = tempList[i]
                            x,y = self.mapHandle.GPStoImagePos(tempWP['lat'], tempWP['lon'])
                            tempWP_next = tempList[0]
                            x_n,y_n = self.mapHandle.GPStoImagePos(tempWP_next['lat'], tempWP_next['lon'])
                            self.dc.SetPen(wx.Pen(wx.RED, 1))
                            self.dc.DrawLines(((x,y),(x_n, y_n)))
                else:
                    pass
        except:
            pass
        self.dc.SelectObject(wx.NullBitmap)
        self.imageCtrl.SetBitmap(tempImage)

    def OnIdle(self,event):
        self.Refresh(False)

    def OnEnterWindow(self, event):
        #print('Enter Window')
        self.inWindowFlag = 1

    def OnEnterMap(self, event):
        #print('Enter Map')
        self.pnl.SetFocus()
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
        self.mouseX, self.mouseY = event.GetPosition()
        _point_lat, _point_lon = self.mapHandle.PostoGPS(self.mouseX, self.mouseY)
        _point_x, _point_y = self.mapHandle.GPStoImagePos(_point_lat, _point_lon)
        #print(self.currentTab)
        if self.currentTab == 1:
            self.tab2.OnAdd(_point_lat, _point_lon)
        if self.currentTab == 2:
            self.tab3.OnAdd(_point_lat, _point_lon)
        if self.currentTab == 3:
            self.tab4.OnAdd(_point_lat, _point_lon)
        self.Refresh()


    def OnMouseRightUp(self, event):
        #print('right up')
        self.rightDown = 0

    def OnMotion(self, event):
        x, y = event.GetPosition()
        #print(x,y)
        if self.inMapFlag == 1 and self.leftDown == 1:
            dx = x-self.mouseX
            dy = y-self.mouseY
            self.mapHandle.move(dx, dy)
            self.Refresh()

    def OnScroll(self, event):
        dlevel = event.GetWheelRotation()
        #self.mapHandle.zoom(dlevel/20)
        # +: Down/Left, -: Up/Right
        self.Refresh()

    def InPointArea(self, x, y):
        if self.currentTab == 1:
            pass
        if self.currentTab == 2:
            pass
        if self.currentTab == 3:
            pass

def main():
    map = wx.App()
    MainFrame(None)
    map.MainLoop()

if __name__ == "__main__":
    main()
