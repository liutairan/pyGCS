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
        
        # Map Info
        self._width = 640
        self._height = 640

        
        self._originLat  =  30.408158 #37.7913838
        self._originLon = -91.179533 #-79.44398934
        
        self._zoom = 21
        self._maptype = 'hybrid' #'roadmap'

        self._homeLat = self._originLat
        self._homeLon = self._originLon
        
        self._dX = 0
        self._dY = 0
        
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
        self.image = wx.EmptyImage(self._width, self._height)
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
        
        tab1 = TabOne(nb, self.dataExchangeHandle)
        tab2 = TabTwo(nb, self.dataExchangeHandle)
        tab3 = TabThree(nb, self.dataExchangeHandle)
        tab4 = TabFour(nb, self.dataExchangeHandle)

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
        #w, h = self.GetClientSize()
        #print(w,h)
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
        #print(x,y)
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
        '''
        self.ZOOM = self.ZOOM + dlevel
        if self.ZOOM > 21:
            self.ZOOM = 21
        elif self.ZOOM < 3:
            self.ZOOM = 3
        print(self.ZOOM)
        '''
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



