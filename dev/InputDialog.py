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

import math
import time
import struct

import numpy
import matplotlib

__author__ = "Tairan Liu"
__copyright__ = "Copyright 2017, Tairan Liu"
__credits__ = ["Tairan Liu", "Other Supporters"]
__license__ = "MIT"
__version__ = "0.4-dev"
__maintainer__ = "Tairan Liu"
__email__ = "liutairan2012@gmail.com"
__status__ = "Development"

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


