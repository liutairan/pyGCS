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
__version__ = "0.4-dev"
__maintainer__ = "Tairan Liu"
__email__ = "liutairan2012@gmail.com"
__status__ = "Development"


_EARTHPIX = 268435456  # Number of pixels in half the earth's circumference at zoom = 21
_DEGREE_PRECISION = 6  # Number of decimal places for rounding coordinates
_TILESIZE = 640        # Larget tile we can grab without paying
_GRABRATE = 4          # Fastest rate at which we can download tiles without paying

_pixrad = _EARTHPIX / math.pi

class Map(object):
    def __init__(self, lat=30.4081580, lon=-91.179533, level=20, width=640, height=640):
        self._width = width
        self._height = height

        self._maptype = "hybrid" #'roadmap'
        self._zoomlevel = level

        self._originLat = lat  # 37.7913838
        self._originLon = lon  #-79.44398934

        self._homeLat = self._originLat
        self._homeLon = self._originLon

        self._centerLat = self._originLat
        self._centerLon = self._originLon

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

    def move(self, dx, dy):
        latStep, lonStep = self._local_tile_step()
        local_dx_to_lon = dx/(_TILESIZE*1.0) * latStep
        local_dy_to_lat = dy/(_TILESIZE*1.0) * lonStep
        self._centerLat = self._centerLat + local_dy_to_lat
        self._centerLon = self._centerLon - local_dx_to_lon
        self.loadImage()
    
    def _local_tile_step(self, ntiles=3):   # the output stands for: at current lat & lon & zoom level, 640 pixels equivalent to how many degree of lat/lon; or the tile has how many degree of lat/lon
        latitude = self._centerLat
        longitude = self._centerLon

        lonpix = _EARTHPIX + longitude * math.radians(_pixrad)
        sinlat = math.sin(math.radians(latitude))
        latpix = _EARTHPIX - _pixrad * math.log((1 + sinlat)/(1 - sinlat)) / 2
    
        _latStep = abs(self._pix_to_lat(0, latpix, ntiles, _TILESIZE, self.zoomlevel) - self._pix_to_lat(1, latpix, ntiles, _TILESIZE, self.zoomlevel))
        _lonStep = abs(self._pix_to_lon(0, lonpix, ntiles, _TILESIZE, self.zoomlevel) - self._pix_to_lon(1, lonpix, ntiles, _TILESIZE, self.zoomlevel))
        return _latStep, _lonStep

    def loadImage(self):
        try:
            state = self.localLoadImage()
            if state == True:
                print('Exist')
                pass
            elif state == False:
                print('Not exist')
                self.webLoadImage()
            else:
                print('Error: Unknown state.')
        except:
            pass


    def zoom(self, dlevel):
        self.zoomlevel = sele.zoomlevel + int(dlevel/2.0)
        self.updateMap()

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
        # full feature: center, size, style, maptype, zoom, ..., key
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

    def InArea(self, lat, lon, border):
        if (lat >= border[1]) and (lat <= border[0]) and (lon >= border[2]) and (lon <= border[3]):
            return 1
        else:
            return 0

    def InAreas(self, handle, areaList):
        for i in range(len(areaList)):
            temp1 = areaList[i]
            zoomLevel = temp1[2]
            latStep = (temp1[4]-temp1[5])/2
            lonStep = (temp1[7]-temp1[6])/2
            temp2 = InArea(handle.lat, handle.lon, temp1[4:8])
            if temp2 == 1:
                if handle.zoom == zoomLevel:
                    return i
                else:
                    return -1
        return -1

    def StitchMaps(self, filelist, handle, area):
        latStep = (area[4]-area[5])/2
        lonStep = (area[7]-area[6])/2
        newLat = handle.lat
        newLon = handle.lon
        #print(latStep,lonStep)
        lats = [roundto(area[4],6), roundto(float(area[0]),6), roundto(area[5],6)]
        lons = [roundto(area[6],6), roundto(float(area[1]),6), roundto(area[7],6)]
        strLats = ["%.6f" % lats[0], "%.6f" % lats[1], "%.6f" % lats[2]]
        strLons = ["%.6f" % lons[0], "%.6f" % lons[1], "%.6f" % lons[2]]
        #print(strLats, strLons)
        path = 'mapscache/'
        fileNames = []
        for i in range(3):
            for j in range(3):
                tempName = strLats[i]+'_'+strLons[j]+'_'+str(handle.zoom)+'_'+handle.maptype+'_'+str(handle.width)+'_'+str(handle.height)+'.jpg'
                fileNames.append(tempName)
        #print(fileNames)
        bigImage = Image.new('RGB', (3*handle.width, 3*handle.height))
        for i in range(len(fileNames)):
            file = fileNames[i]
            j = int(i/3)
            k = i % 3
            if file in filelist:
                tile = Image.open(path+file)
                #print(tile)
                bigImage.paste(tile, (k*handle.width, j*handle.height))
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

    def GPStoImagePos(self, waypoints, tempLat, tempLon, zoomlevel):
        latStep, lonStep = CalStepFromGPS(tempLat, tempLon, zoom = zoomlevel)
        coordinates = []
        for i in range(len(waypoints)):
            x = int((waypoints[i][1]-(tempLon-lonStep/2.0))/lonStep*640.0)
            y = int(-(waypoints[i][0]-(tempLat+latStep/2.0))/latStep*640.0)
            print(x,y)
            coordinates.append([x,y])
        return coordinates

    def PostoGPS(self, x, y):
        pass

    def localLoadImage(self):
        localmap = self._findLocalImage()
        if localmap[0] == 1:
            #print('Exist')
            image = localmap[1]
            self.retImage = self.PilImageToWxImage(image)
            return True
        else:
            return False
        

    def webLoadImage(self):
        bigimage, northwest, southeast = self._getBigImage()
        image = self._cropImage(bigimage)
        self.retImage = self.PilImageToWxImage(image)

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

    def _cropImage(self, origin_image):
        new_image = origin_image.crop((640,640,1280,1280))
        return new_image

    def _new_image(self, width, height):
        return PIL.Image.new('RGB', (width, height))

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
        groups, keywords = self._groupLists(keyWordLList, [2,3])

        if len(groups) >0: # some maps exist
            areas = []
            with open('mapcache.txt', 'r') as inf:
                temp1 = inf.readlines()
                for temp2 in temp1:
                    if len(temp2) > 0:
                        temp3 = temp2.split()
                        areas.append([float(temp3[0]), float(temp3[1]), int(temp3[2]), temp3[3], float(temp3[4]), float(temp3[5]), float(temp3[6]), float(temp3[7])])
            #print(keywords)

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

    def GPStoImagePos(waypoints, tempLat, tempLon, zoomlevel):
        latStep, lonStep = CalStepFromGPS(tempLat, tempLon, zoom = zoomlevel)
        coordinates = []
        for i in range(len(waypoints)):
            x = int((waypoints[i][1]-(tempLon-lonStep/2.0))/lonStep*640.0)
            y = int(-(waypoints[i][0]-(tempLat+latStep/2.0))/latStep*640.0)
            print(x,y)
            coordinates.append([x,y])
        return coordinates


