import wx

class TabTwo(wx.Panel):
    def __init__(self, parent, DEH):
        wx.Panel.__init__(self, parent)
        self.deh = DEH
        self.deh.bind_to(self.OnUpdate)
        self.addr_long = '\x00\x13\xA2\x00\x40\xC1\x43\x06'
        self.addr = '\xFF\xFE'
        #self.sch.addressList[0] = [self.addr_long, self.addr]   # For debug, remove later
        self.InitUI()

    def InitUI(self):
        # address and connect
        addressLong = wx.StaticText(self, -1, 'Address Long: 0013A200 40C1430F', pos = (0,10), size = (70,20))
        self.connectButton = wx.Button(self, -1, 'Connect', pos = (280,5), size = (90,20))
        self.Bind(wx.EVT_BUTTON, self.OnClickConnect, self.connectButton)
        # Boxes
        innerStaticBox = wx.StaticBox(self, -1, 'Inner States', pos = (0,30), size = (150,200))
        outerStaticBox = wx.StaticBox(self, -1, 'Outer States', pos = (160,30), size = (150,200))
        statusLights = wx.StaticBox(self, -1, 'Status', pos = (420,0), size = (70,200))

        # Outer status
        lat = wx.StaticText(self, -1, 'Lat: ', pos = (165,45), size = (70,20))
        lon = wx.StaticText(self, -1, 'Lon: ', pos = (165,70), size = (70,20))
        alt = wx.StaticText(self, -1, 'Alt: ', pos = (165,95), size = (70,20))
        numberSat = wx.StaticText(self, -1, 'No. Sat: ', pos = (165,120), size = (70,20))
        
        # Inner status
        heading = wx.StaticText(self, -1, 'Heading: ', pos = (0,45), size = (70,20))
        
        
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

    def OnUpdate(self, global_states):
        print('tab two updated')
        print(global_states)
        pass
    
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

    def OnClickConnect(self,event):
        if self.connectButton.GetLabel() == 'Connect':
            print('Quad 1 Connected')
            self.connectButton.SetLabel('Disconnect')
            self.deh.addressList[0] = [self.addr_long, self.addr]
        elif self.connectButton.GetLabel() == 'Disconnect':
            print('Quad 1 Disconnected')
            self.connectButton.SetLabel('Connect')
            self.deh.addressList[0] = []
