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
import time
import math
import threading
import numpy
import cStringIO
import urllib
import matplotlib
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import PIL
from PIL import Image
import wx

try:
    from apikey import _key
except:
    _key = ''

__author__ = "Tairan Liu"
__copyright__ = "Copyright 2017, Tairan Liu"
__credits__ = ["Tairan Liu", "Other Supporters"]
__license__ = "MIT"
__version__ = "0.6-dev"
__maintainer__ = "Tairan Liu"
__email__ = "liutairan2012@gmail.com"
__status__ = "Development"


_EARTHPIX = 268435456  # Number of pixels in half the earth's circumference at zoom = 21
_DEGREE_PRECISION = 6  # Number of decimal places for rounding coordinates
_TILESIZE = 640        # Larget tile we can grab without paying
_GRABRATE = 4          # Fastest rate at which we can download tiles without paying

_pixrad = _EARTHPIX / math.pi

class Map(object):
    def __init__(self, lat=30.4081580, lon=-91.1795330, level=20, width=640, height=640):
        self._width = width
        self._height = height

        self._maptype = "hybrid" #'roadmap'
        self._zoomlevel = level

        self._originLat =  30.4081580  # 37.7913838
        self._originLon = -91.1795330  #-79.44398934
        self.latlonDict = {'21':{'lat':[],'lon':[]}, '20':{'lat':[],'lon':[]}, '19':{'lat':[],'lon':[]},
                           '18':{'lat':[],'lon':[]}, '17':{'lat':[],'lon':[]}, '16':{'lat':[],'lon':[]},
                           '15':{'lat':[],'lon':[]}, '14':{'lat':[],'lon':[]}, '13':{'lat':[],'lon':[]},
                           '12':{'lat':[],'lon':[]}, '11':{'lat':[],'lon':[]}, '10':{'lat':[],'lon':[]},
                           '9':{'lat':[],'lon':[]}, '8':{'lat':[],'lon':[]}, '7':{'lat':[],'lon':[]},
                           '6':{'lat':[],'lon':[]}, '5':{'lat':[],'lon':[]}, '4':{'lat':[],'lon':[]}
                           }
        self._init_tile_index()

        self._homeLat = lat
        self._homeLon = lon

        self._centerLat = lat
        self._centerLon = lon

        self._iterationX = 0
        self._iterationY = 0

        self._dX = 0
        self._dY = 0

        self._cachepath = 'mapscache/'

        self.retImage = wx.EmptyImage(self._width, self._height)
        try:
            self.initLoad()
        except:
            pass

    def get_maptype(self):
        return self._maptype

    def set_maptype(self, value):
        self._maptype = value

    maptype = property(get_maptype, set_maptype)

    def get_zoomlevel(self):
        return self._zoomlevel

    def set_zoomlevel(self, value):
        self._zoomlevel = value

    zoomlevel = property(get_zoomlevel, set_zoomlevel)

    def get_cachepath(self):
        return self._cachepath

    def set_cachepath(self, value):
        self._cachepath = value

    cachepath = property(get_cachepath, set_cachepath)

    def initLoad(self):
        self.loadImage()

    def _init_tile_index(self):
        for templevel in range(9,22):
            # level number: templevel
            iter_steps = 2 ** (templevel-9)
            latDict = []
            latitude = self._originLat
            latDict.append(latitude)
            for i in range(iter_steps):
                sinlat = math.sin(math.radians(latitude))
                latpix = _EARTHPIX - _pixrad * math.log((1 + sinlat)/(1 - sinlat)) / 2
                newlat = self._pix_to_lat(0, latpix, 3, 640, int(templevel))
                latitude = newlat
                latDict.append(latitude)
            latitude = self._originLat
            for i in range(iter_steps):
                sinlat = math.sin(math.radians(latitude))
                latpix = _EARTHPIX - _pixrad * math.log((1 + sinlat)/(1 - sinlat)) / 2
                newlat = self._pix_to_lat(2, latpix, 3, 640, int(templevel))
                latitude = newlat
                latDict.append(latitude)
            self.latlonDict[str(int(templevel))]['lat'] = sorted(latDict)

            lonDict = []
            longitude = self._originLon
            lonDict.append(longitude)
            for i in range(iter_steps):
                lonpix = _EARTHPIX + longitude * math.radians(_pixrad)
                newlon = self._pix_to_lon(0, lonpix, 3, 640, int(templevel))
                longitude = newlon
                lonDict.append(longitude)
            longitude = self._originLon
            for i in range(iter_steps):
                lonpix = _EARTHPIX + longitude * math.radians(_pixrad)
                newlon = self._pix_to_lon(2, lonpix, 3, 640, int(templevel))
                longitude = newlon
                lonDict.append(longitude)
            self.latlonDict[str(int(templevel))]['lon'] = sorted(lonDict)


    def _pos_to_tile_index(self, lat, lon, zoomlevel):
        level_dict = str(int(zoomlevel))
        nearLat = sorted(enumerate(self.latlonDict[level_dict]['lat']), key=lambda x: abs(x[1]-lat))
        nearLon = sorted(enumerate(self.latlonDict[level_dict]['lon']), key=lambda x: abs(x[1]-lon))
        x = nearLon[0]
        y = nearLat[0]
        return x,y

    def move(self, dx, dy):
        latStep, lonStep = self._local_tile_step()
        local_dx_to_lon = dx/(_TILESIZE*1.0) * lonStep
        local_dy_to_lat = dy/(_TILESIZE*1.0) * latStep
        self._centerLat = self._centerLat + local_dy_to_lat
        self._centerLon = self._centerLon - local_dx_to_lon
        self.loadImage()

    def _local_tile_step(self, ntiles=3):   # the output stands for: at current lat & lon & zoom level, 640 pixels equivalent to how many degree of lat/lon; or the tile has how many degree of lat/lon
        latitude = self._centerLat
        longitude = self._centerLon

        lonpix = _EARTHPIX + longitude * math.radians(_pixrad)
        sinlat = math.sin(math.radians(latitude))
        latpix = _EARTHPIX - _pixrad * math.log((1 + sinlat)/(1 - sinlat)) / 2

        _latStep = abs(self._pix_to_lat(0, latpix, ntiles, _TILESIZE, self.zoomlevel) - self._pix_to_lat(2, latpix, ntiles, _TILESIZE, self.zoomlevel)) /2
        _lonStep = abs(self._pix_to_lon(0, lonpix, ntiles, _TILESIZE, self.zoomlevel) - self._pix_to_lon(2, lonpix, ntiles, _TILESIZE, self.zoomlevel)) /2
        return _latStep, _lonStep

    def loadImage(self):
        #print('load')
        try:
            needIndex = self.localLoadImage()
            if len(needIndex) == 0:
                print('Exist')
                pass
            elif len(needIndex) > 0:
                print('Not exist')
                #print(needIndex)
                self.webLoadImage(needIndex)
                newNeedIndex = self.localLoadImage()
            else:
                print('Error: Unknown state.')
        except:
            pass


    def zoom(self, dlevel):
        self.zoomlevel = self.zoomlevel + int(dlevel)
        if self.zoomlevel > 21:
            self.zoomlevel = 21
        elif self.zoomlevel < 9:
            self.zoomlevel = 9
        self.loadImage()


    def updateMap(self):
        pass

    def _pixels_to_degrees(self, pixels, zoom):
        return pixels * 2 ** (21 - zoom)

    def _pix_to_lon(self, j, lonpix, ntiles, _TILESIZE, zoom):
        return math.degrees((lonpix + self._pixels_to_degrees(((j)-ntiles/2)*_TILESIZE, zoom) - _EARTHPIX) / _pixrad)

    def _pix_to_lat(self, k, latpix, ntiles, _TILESIZE, zoom):
        return math.degrees(math.pi/2 - 2 * math.atan(math.exp(((latpix + self._pixels_to_degrees((k-ntiles/2)*_TILESIZE, zoom)) - _EARTHPIX) / _pixrad)))

    def _roundto(self, value, digits):
        return int(value * 10**digits) / 10.**digits

    def _grab_tile(self, lat, lon, zoom, maptype, _TILESIZE, sleeptime):
        urlbase = 'https://maps.googleapis.com/maps/api/staticmap?center=%f,%f&zoom=%d&maptype=%s&size=%dx%d&format=jpg'
        urlbase = urlbase + '&key=' + _key
        # full feature: center, scale, size, style, maptype, zoom, ..., key
        scale = 2
        specs = lat, lon, zoom, maptype, _TILESIZE, _TILESIZE
        filename = 'mapscache/' + ('%f_%f_%d_%s_%d_%d' % specs) + '.jpg'
        tile = None
        if os.path.isfile(filename):
            tile = PIL.Image.open(filename)
        else:
            url = urlbase % specs
            result = urllib.urlopen(url).read()
            tile = PIL.Image.open(cStringIO.StringIO(result))
            if not os.path.exists('mapscache'):
                os.mkdir('mapscache')
            tile.save(filename)
            time.sleep(sleeptime) # limit download speed
        return tile

    # PIL image to wx image
    def PilImageToWxImage(self, myPilImage, copyAlpha=True ) :
        hasAlpha = myPilImage.mode[ -1 ] == 'A'
        if copyAlpha and hasAlpha :  # Make sure there is an alpha layer copy.
            myWxImage = wx.EmptyImage( *myPilImage.size )
            myPilImageCopyRGBA = myPilImage.copy()
            myPilImageCopyRGB = myPilImageCopyRGBA.convert( 'RGB' )    # RGBA --> RGB
            myPilImageRgbData =myPilImageCopyRGB.tostring()
            myWxImage.SetData( myPilImageRgbData )
            myWxImage.SetAlphaData( myPilImageCopyRGBA.tostring()[3::4] )  # Create layer and insert alpha values.
        else :    # The resulting image will not have alpha.
            myWxImage = wx.EmptyImage( *myPilImage.size )
            myPilImageCopy = myPilImage.copy()
            myPilImageCopyRGB = myPilImageCopy.convert( 'RGB' )    # Discard any alpha from the PIL image.
            myPilImageRgbData =myPilImageCopyRGB.tostring()
            myWxImage.SetData( myPilImageRgbData )
        return myWxImage


    def GPStoImagePos(self, tempLat, tempLon):
        latStep, lonStep = self._local_tile_step()
        temp_point_x = ((tempLon - self._centerLon)/lonStep*(1.0*_TILESIZE) + 320)
        temp_point_y = (320 - (tempLat - self._centerLat)/latStep*(1.0*_TILESIZE))
        point_x = int(temp_point_x)
        point_y = int(temp_point_y)
        if (temp_point_x - int(temp_point_x)) >= 0.5:
            point_x = int(temp_point_x + 1)
        if (temp_point_y - int(temp_point_y)) >= 0.5:
            point_y = int(temp_point_y + 1)
        return point_x,point_y


    def PostoGPS(self, x, y):
        latStep, lonStep = self._local_tile_step()
        local_x_to_lon = (x-320)/(_TILESIZE*1.0) * lonStep
        local_y_to_lat = (y-320)/(_TILESIZE*1.0) * latStep
        point_lon = self._centerLon + local_x_to_lon
        point_lat = self._centerLat - local_y_to_lat
        return point_lat,point_lon

    def localLoadImage(self):
        localMap, missingMap = self._findLocalImage()
        if len(missingMap) > 0:
            return missingMap
        elif len(localMap) == 9:
            #print(localMap)
            tempimage1, edge_tile_center = self._stitchImages(localMap)
            tempimage2 = self._cropImage(tempimage1,edge_tile_center)
            self.retImage = self.PilImageToWxImage(tempimage2)
            return []
        else:
            print('Wrong image number')

    def _findLocalImage(self):
        areas = []
        try:
            with open('mapcache.txt', 'r') as inf:
                temp1 = inf.readlines()
                if len(temp1) > 0:
                    for temp2 in temp1:
                        if len(temp2) > 0:
                            temp3 = temp2.split()
                            areas.append([float(temp3[0]), float(temp3[1]), int(temp3[2]), temp3[3], int(temp3[4]), int(temp3[5])])
        except:
            pass
        try:
            local, missing = self._findImages(areas)
            #print(local)
            return local, missing
        except:
            pass

    def _findImages(self, areaList):
        lat = self._centerLat
        lon = self._centerLon
        zoom = self.zoomlevel
        x,y = self._pos_to_tile_index(lat, lon, zoom)
        x_ind = x[0]
        y_ind = y[0]
        x_pos = x[1]
        y_pos = y[1]
        missingTiles = []
        waitingTiles = [(x_ind-1, y_ind+1), (x_ind, y_ind+1), (x_ind+1, y_ind+1), (x_ind-1, y_ind), (x_ind, y_ind), (x_ind+1, y_ind), (x_ind-1, y_ind-1), (x_ind, y_ind-1), (x_ind+1, y_ind-1)]
        localTiles = []

        if len(areaList) == 0:
            for i in range(len(waitingTiles)):
                missingTiles.append((zoom, waitingTiles[i][0], waitingTiles[i][1]))
            return localTiles, missingTiles
        else:
            for i in range(9):
                tocheck = waitingTiles[i]
                res = list(filter(lambda x: (zoom == x[2]) and (tocheck[0] == x[4]) and (tocheck[1] == x[5]), areaList))
                if len(res) == 0:
                    missingTiles.append((zoom, tocheck[0], tocheck[1]))
                else:
                    localTiles.append((zoom, tocheck[0], tocheck[1]))
            return localTiles, missingTiles

    def _stitchImages(self, localTiles):
        ntiles = 3
        bigsize = ntiles * _TILESIZE
        bigimage = self._new_image(bigsize, bigsize)
        min_lat = self._centerLat
        max_lat = self._centerLat
        min_lon = self._centerLon
        max_lon = self._centerLon
        for i in range(len(localTiles)):
            row_num = int(i/3)
            col_num = i % 3
            x_ind = localTiles[i][1]
            y_ind = localTiles[i][2]
            lat = self.latlonDict[str(int(self.zoomlevel))]['lat'][y_ind]
            lon = self.latlonDict[str(int(self.zoomlevel))]['lon'][x_ind]
            lat_rounded = self._roundto(lat, 6)
            lon_rounded = self._roundto(lon, 6)
            if lat_rounded > max_lat:
                max_lat = lat_rounded
            if lat_rounded < min_lat:
                min_lat = lat_rounded
            if lon_rounded > max_lon:
                max_lon = lon_rounded
            if lon_rounded < min_lon:
                min_lon = lon_rounded

            strLat = str(lat_rounded)
            strLon = str(lon_rounded)
            tempName = strLat+'_'+strLon+'_'+str(self.zoomlevel)+'_'+self.maptype+'_'+str(self._width)+'_'+str(self._height)+'.jpg'
            tile = Image.open('mapscache/'+tempName)
            bigimage.paste(tile, (col_num*_TILESIZE, row_num*_TILESIZE))
        return bigimage, [max_lat, min_lat, min_lon, max_lon]

    def _cropImage(self, origin_image, border):
        north = border[0]
        south = border[1]
        west = border[2]
        east = border[3]
        image_center_lat = 0.5*(north + south)
        image_center_lon = 0.5*(west + east)
        tile_length_lat = 0.5*(north - south)
        tile_length_lon = 0.5*(east - west)

        dx = int((self._centerLon - image_center_lon)/tile_length_lon *640.0)
        dy = int((self._centerLat - image_center_lat)/tile_length_lat *640.0)
        northwest_x = 640 + dx
        northwest_y = 640 - dy
        new_image = origin_image.crop((northwest_x,northwest_y, northwest_x+640, northwest_y+640))
        return new_image

    def webLoadImage(self, toDownloadList):
        for i in range(len(toDownloadList)):
            self._downloadTile(toDownloadList[i])

    def _downloadTile(self, tileIndex):
        zoomlevel = tileIndex[0]
        x = tileIndex[1]
        y = tileIndex[2]
        lat = self.latlonDict[str(int(zoomlevel))]['lat'][x]
        lon = self.latlonDict[str(int(zoomlevel))]['lon'][y]
        lat_rounded = self._roundto(lat, 6)
        lon_rounded = self._roundto(lon, 6)
        self._grab_tile(lat_rounded, lon_rounded, zoomlevel, self.maptype, _TILESIZE, 1./_GRABRATE)
        strOut = str(lat_rounded)+' '+str(lon_rounded)+' '+ str(zoomlevel)+' '+ self.maptype +' '+str(x)+' '+str(y)+'\n'
        with open('mapcache.txt', 'at') as outf:
            outf.write(strOut)


    def _getBigImage(self, radius_meters=None, default_ntiles=3):
        latitude = self._centerLat
        longitude = self._centerLon
        zoom = self.zoomlevel
        pixels_per_meter = 2**zoom / (156543.03392 * math.cos(math.radians(latitude)))

        # number of tiles required to go from center latitude to desired radius in meters
        ntiles = default_ntiles if radius_meters is None else int(round(2 * pixels_per_meter / (_TILESIZE /2./ radius_meters)))

        lonpix = _EARTHPIX + longitude * math.radians(_pixrad)
        sinlat = math.sin(math.radians(latitude))
        latpix = _EARTHPIX - _pixrad * math.log((1 + sinlat)/(1 - sinlat)) / 2

        bigsize = ntiles * _TILESIZE # 3 * 640 pixels
        bigimage = self._new_image(bigsize, bigsize)

        for j in range(ntiles):
            lon = self._pix_to_lon(j, lonpix, ntiles, _TILESIZE, zoom)
            for k in range(ntiles):
                lat = self._pix_to_lat(k, latpix, ntiles, _TILESIZE, zoom)
                tile = self._grab_tile(lat, lon, zoom, self.maptype, _TILESIZE, 1./_GRABRATE)
                bigimage.paste(tile, (j*_TILESIZE,k*_TILESIZE))

        tempwest = self._pix_to_lon(0, lonpix, ntiles, _TILESIZE, zoom)
        tempeast = self._pix_to_lon(ntiles-1, lonpix, ntiles, _TILESIZE, zoom)

        tempnorth = self._pix_to_lat(0, latpix, ntiles, _TILESIZE, zoom)
        tempsouth = self._pix_to_lat(ntiles-1, latpix, ntiles, _TILESIZE, zoom)

        west = self._roundto(tempwest,7)
        east = self._roundto(tempeast,7)
        north = self._roundto(tempnorth,7)
        south = self._roundto(tempsouth,7)

        strOut = str(latitude)+' '+str(longitude)+' '+ str(zoom)+' '+ self.maptype+' '+str(north)+' '+str(south)+' '+str(west)+' '+str(east)+'\n'
        with open('mapcache.txt', 'at') as outf:
            outf.write(strOut)
        return bigimage, (north,west), (south,east)


    def _new_image(self, width, height):
        return PIL.Image.new('RGB', (width, height))

    '''
    def _findLocalImage(self): # check whether the map exists locally
        path = 'mapscache/'
        keyWordLList = []
        fileList = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if len(file) > 10:
                    fileList.append(file)
                    temp1 = file[:-4]
                    temp2 = temp1.split('_')
                    keyWordLList.append(temp2)
        if len(keyWordLList) == 0:
            return [0]
        groups, keywords = self._groupLists(keyWordLList, [2,3])

        if len(groups) >0: # some maps exist
            areas = []
            with open('mapcache.txt', 'r') as inf:
                temp1 = inf.readlines()
                for temp2 in temp1:
                    if len(temp2) > 0:
                        temp3 = temp2.split()
                        areas.append([float(temp3[0]), float(temp3[1]), int(temp3[2]), temp3[3]], int(temp3[4]), int(temp3[5]))
            #print(keywords)
            temp = self._check
            temp = self._inAreas(areas)
            if temp >= 0: #in one local map
                print('Wait to load')
                img = self._stitchMaps(fileList, areas[temp])
                return [1, img]
            else: # not in local map
                #print(temp)
                return [0]
        else:  # no map exist
            return [0]
    '''

    def _groupLists(self, lists, key=[2,3]):
        totalNum = len(lists)
        fieldNum = len(lists[0])
        tempGroup = []
        keyWordList = []
        if len(key) == 0:
            print('Empty Key List')
        elif len(key) == 2:
            for temp1 in key:
                if temp1 > fieldNum-1:
                    print('Invalid Key')
                    break

            for temp2 in lists:
                if [temp2[key[0]], temp2[key[1]]] in keyWordList: # This keyword exists
                    groupNum = keyWordList.index([temp2[key[0]], temp2[key[1]]])
                    tempGroup[groupNum].append(temp2)
                else: # This keyword not exists
                    groupNum = len(keyWordList)
                    keyWordList.append([temp2[key[0]], temp2[key[1]]])
                    tempGroup.append([temp2])
        else:
            print('Not Support Currently')
            pass

        return tempGroup, keyWordList

    def _inArea(self, lat, lon, border):
        if (lat >= border[1]) and (lat <= border[0]) and (lon >= border[2]) and (lon <= border[3]):
            return 1
        else:
            return 0

    def _inAreas(self, areaList):
        for i in range(len(areaList)):
            temp1 = areaList[i]
            zoomLevel = temp1[2]
            latStep = (temp1[4]-temp1[5])/2
            lonStep = (temp1[7]-temp1[6])/2

            temp2 = self._inArea(self._centerLat, self._centerLon, temp1[4:8])
            if temp2 == 1:
                if self.zoomlevel == zoomLevel:
                    return i
                else:
                    return -1
            else:
                return -1

    def _stitchMaps(self, filelist, area):
        latStep = (area[4]-area[5])/2
        lonStep = (area[7]-area[6])/2
        newLat = self._centerLat
        newLon = self._centerLon
        #print(latStep,lonStep)
        lats = [self._roundto(area[4],6), self._roundto(float(area[0]),6), self._roundto(area[5],6)]
        lons = [self._roundto(area[6],6), self._roundto(float(area[1]),6), self._roundto(area[7],6)]
        strLats = ["%.6f" % lats[0], "%.6f" % lats[1], "%.6f" % lats[2]]
        strLons = ["%.6f" % lons[0], "%.6f" % lons[1], "%.6f" % lons[2]]

        path = 'mapscache/'
        fileNames = []
        for i in range(3):
            for j in range(3):
                tempName = strLats[i]+'_'+strLons[j]+'_'+str(self.zoomlevel)+'_'+self.maptype+'_'+str(self._width)+'_'+str(self._height)+'.jpg'
                fileNames.append(tempName)

        bigImage = PIL.Image.new('RGB', (3*self._width, 3*self._height))

        for i in range(len(fileNames)):
            file = fileNames[i]
            j = int(i/3)
            k = i % 3
            if file in filelist:
                tile = Image.open(path+file)
                #print(tile)
                bigImage.paste(tile, (k*self._width, j*self._height))
            else:
                pass
        #bigImage.save('Test.jpg')

        north = float(area[0]) + 3.0*latStep/2.0
        west = float(area[1]) - 3.0*lonStep/2.0
        fetchPointX = int((newLon - west)/lonStep*640.0)
        fetchPointY = int(-(newLat - north)/latStep*640.0)
        #print(fetchPointX,fetchPointY)
        tempBox = (fetchPointX-320, fetchPointY-320, fetchPointX+320, fetchPointY+320)
        #tempBox = (0,0, 200, 200)
        winImage = bigImage.crop(tempBox)
        #winImage.show()
        #winImage.save('Test2.jpg', "JPEG")

        return winImage


    def _getProperty(self, lists):
        mapType = lists[0][3]
        zoomLevel = int(lists[0][2])
        centerLatList = []
        centerLonList = []
        for templist in lists:
            centerLatList.append(float(templist[0]))
            centerLonList.append(float(templist[1]))
        tempborder = self.getBorder(centerLatList, centerLonList)
        border = tempborder[0:4]
        maxBorder = tempborder[4:8]
        step = tempborder[8: 10]
        return [mapType, zoomLevel, border, maxBorder, step]

    def _getBorder(self, latList, lonList):
        minLatCenter = min(latList)
        maxLatCenter = max(latList)
        minLonCenter = min(lonList)
        maxLonCenter = max(lonList)
        latStep = (maxLatCenter-minLatCenter)/3.0
        lonStep = (maxLonCenter-minLonCenter)/3.0
        leftBorder = minLonCenter-lonStep/2.0
        rightBorder = maxLonCenter+lonStep/2.0
        upBorder = maxLatCenter+latStep/2.0
        downBorder = minLatCenter+latStep/2.0
        #print(latStep, lonStep)
        return [minLonCenter, maxLonCenter, maxLatCenter, minLatCenter, leftBorder, rightBorder, upBorder, downBorder, latStep, lonStep]

    def _requiredMap(self, waypoints):
        if len(waypoints) > 0:
            maxLat = waypoints[0][0]
            minLat = waypoints[0][0]
            centerLat = waypoints[0][0]
            maxLon = waypoints[0][1]
            minLon = waypoints[0][1]
            centerLat = waypoints[0][1]

            for i in range(len(waypoints)):
                if waypoints[i][0] > maxLat:
                    maxLat = waypoints[i][0]
                if waypoints[i][0] < minLat:
                    minLat = waypoints[i][0]
                if waypoints[i][1] > maxLon:
                    maxLon = waypoints[i][1]
                if waypoints[i][1] < minLon:
                    minLon = waypoints[i][1]
            centerLat = (maxLat+minLat)/2.0
            centerLon = (maxLon+minLon)/2.0
            latSize = abs(maxLat-minLat)
            lonSize = abs(maxLon-minLon)
            zoomLevel = 21
            zoomFlag = 1
            while zoomFlag and (zoomLevel >= 3):
                latStep, lonStep = self._local_tile_step()
                if (latSize < latStep) and (lonSize < lonStep):
                    zoomFlag = 0
                else:
                    zoomLevel = zoomLevel - 1
            lat = centerLat
            lon = centerLon
            zoomlevel = zoomLevel
            print('Zoom Level: '+str(zoomlevel))
        return lat, lon, zoomlevel
