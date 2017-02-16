#!/usr/bin/env python

import os
import sys
import wx
import serial
import math
import time
import threading
import numpy
from os import walk
import matplotlib

from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from PIL import Image

from Map import Map

class MainFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(MainFrame, self).__init__(*args, **kw)
        
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
        self.SetSize((840,640))
        self.SetTitle("Map")
        self.SetClientSize((840,640))
        self.Center()
        
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_IDLE,self.OnIdle)
    
        pnl.Bind(wx.EVT_KEY_UP, self.OnKeyDown)

        # Create Empty Image to preload
        self.mapHandle = Map(self.LATITUDE, self.LONGITUDE, self.ZOOM, self.WIDTH, self.HEIGHT)
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
        
        pnl.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        pnl.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        pnl.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseRightDown)
        pnl.Bind(wx.EVT_RIGHT_UP, self.OnMouseRightUp)
        pnl.Bind(wx.EVT_MOTION, self.OnMotion)
        pnl.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
        pnl.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
        
        self.buttonLoadHome = wx.Button(self, wx.ID_ANY, 'Load Pos', pos = (650, 10), size = (90,30))
        self.Bind(wx.EVT_BUTTON, self.OnLoadHome, id = self.buttonLoadHome.GetId())
        
        self.buttonLoadWaypoints = wx.Button(self, wx.ID_ANY, 'Load Waypoints', pos = (650, 50), size = (90,30))
        self.Bind(wx.EVT_BUTTON, self.OnLoadWaypoints, id = self.buttonLoadWaypoints.GetId())
        
        self.Show(True)

    def OnQuitApp(self, event):
        self.Close()

    def OnLoadHome(self, event):
        tempLat = self.handle.lat
        tempLon = self.handle.lon
        try:
            sc = serial.Serial(port = '/dev/tty.usbserial', baudrate = 115200, timeout = 1)
            sc.flush()
            tempFlag = 1
            while tempFlag:
                temp = sc.readline()
                if temp.find('$GPRMC') == 0 :
                    try:
                        temp2 = temp.split(',')
                        print('Time '+str(temp2[1][0:2])+' '+str(temp2[1][2:4])+' '+str(temp2[1][4:6])+' '+str(temp2[1][7:9])+' ')
                        print('Date '+str(temp2[9][0:2])+' '+str(temp2[9][2:4])+' '+str(temp2[9][4:6])+ ' ')
                        tempLat = float(temp2[3][0:2]) + float(temp2[3][2:-1])*1.0/60.0
                        tempLon = float(temp2[5][0:3]) + float(temp2[5][3:-1])*1.0/60.0
                        tempLon = -tempLon
                        print(float(temp2[3][0:2]) + float(temp2[3][2:-1])*1.0/60.0 )
                        print(float(temp2[5][0:3]) + float(temp2[5][3:-1])*1.0/60.0)
                        tempFlag = 0
                        
                    except:
                        print('Error data format')
                        pass
            sc.close()
        except:
            print('Cannot open serial port.')
        
        '''
        self.handle.lat = tempLat
        self.handle.lon = tempLon
        self.mapImage = PreloadMap(self.handle)
        self.LATITUDE = self.handle.lat
        self.LONGITUDE = self.handle.lon
        '''
        self.Refresh()
        
    def OnLoadWaypoints(self, event):
        try:
            waypoints = [[self.homeLat, self.homeLon]]
            with open('waypoints.txt', 'r') as inf:
                temp1 = inf.readlines()
                for temp2 in temp1:
                    if len(temp2) > 0:
                        temp3 = temp2.split(',')
                        waypoints.append([float(temp3[0]), float(temp3[1])])
            #print(waypoints)
            tempLat, tempLon, zoomlevel = RequiredMap(waypoints)
            try:
                self.handle.lat = tempLat
                self.handle.lon = tempLon
                self.handle.zoom = zoomlevel
                self.mapImage = PreloadMap(self.handle)
                self.LATITUDE = self.handle.lat
                self.LONGITUDE = self.handle.lon
                self.waypoints = waypoints
                self.waypointsOnImage = GPStoImagePos(waypoints, tempLat, tempLon, zoomlevel)
                self.Refresh()
            except:
                print('Failed to load map with waypoints')
        except:
            print('Failed to load waypoints')

    def OnKeyDown(self, event):
        keyNumber = event.GetKeyCode()
        #print(keyNumber)
        if keyNumber == 27:
            self.Close()

    def OnSize(self, event):
        event.Skip()
        self.Refresh()
    
    def OnPaint(self, event):
        self.mapImage = self.mapHandle.retImage
        tempImage = wx.BitmapFromImage(self.mapImage)
        self.dc = wx.MemoryDC(tempImage)

        self.dc.SetPen(wx.Pen("BLACK", style = wx.TRANSPARENT))
        '''
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
        '''
        self.dc.SelectObject(wx.NullBitmap)
        self.imageCtrl.SetBitmap(tempImage)

    
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
            dx = x-self.mouseX
            dy = y-self.mouseY
            self.mapHandle.move(self.dX, self.dY)
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
        self.handle.zoom = self.ZOOM
        #self.goompy = GooMPy(self.WIDTH, self.HEIGHT, self.LATITUDE, self.LONGITUDE, self.ZOOM, self.MAPTYPE)
        self.mapImage = PreloadMap(self.handle)
        '''
        self.Refresh()


def main():
    map = wx.App()
    MainFrame(None)
    map.MainLoop()

if __name__ == "__main__":
    main()


