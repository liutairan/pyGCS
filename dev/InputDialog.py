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


