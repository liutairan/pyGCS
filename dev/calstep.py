import math

_EARTHPIX = 268435456  # Number of pixels in half the earth's circumference at zoom = 21
_DEGREE_PRECISION = 6  # Number of decimal places for rounding coordinates
_TILESIZE = 640        # Larget tile we can grab without paying
_GRABRATE = 4          # Fastest rate at which we can download tiles without paying

_pixrad = _EARTHPIX / math.pi

def _local_tile_step(_centerLat, _centerLon, ntiles=3):   # the output stands for: at current lat & lon & zoom level, 640 pixels equivalent to how many degree of lat/lon; or the tile has how many degree of lat/lon
    latitude = _centerLat
    longitude = _centerLon
    zoomlevel = 21
    
    lonpix = _EARTHPIX + longitude * math.radians(_pixrad)
    sinlat = math.sin(math.radians(latitude))
    latpix = _EARTHPIX - _pixrad * math.log((1 + sinlat)/(1 - sinlat)) / 2
    
    _latStep = abs(_pix_to_lat(0, latpix, ntiles, _TILESIZE, zoomlevel) - _pix_to_lat(1, latpix, ntiles, _TILESIZE, zoomlevel))
    _lonStep = abs(_pix_to_lon(0, lonpix, ntiles, _TILESIZE, zoomlevel) - _pix_to_lon(1, lonpix, ntiles, _TILESIZE, zoomlevel))
    return _latStep, _lonStep

def _pixels_to_degrees(pixels, zoom):
    return pixels * 2 ** (21 - zoom)

def _pix_to_lon(j, lonpix, ntiles, _TILESIZE, zoom):
    return math.degrees((lonpix + _pixels_to_degrees(((j)-ntiles/2)*_TILESIZE, zoom) - _EARTHPIX) / _pixrad)

def _pix_to_lat(k, latpix, ntiles, _TILESIZE, zoom):
    return math.degrees(math.pi/2 - 2 * math.atan(math.exp(((latpix + _pixels_to_degrees((k-ntiles/2)*_TILESIZE, zoom)) - _EARTHPIX) / _pixrad)))

def _roundto(value, digits):
    return int(value * 10**digits) / 10.**digits

def main():
    '''
    for i in range(33):
        lat = 20.0 + i*0.5
        lon = -180.0 #+ i*5.0
        latStep, lonStep = _local_tile_step(lat,lon)
        print(lat, lon, latStep, lonStep)
    '''
    latitude = 0
    longitude = 0
    for i in range(200000):
        sinlat = math.sin(math.radians(latitude))
        latpix = _EARTHPIX - _pixrad * math.log((1 + sinlat)/(1 - sinlat)) / 2
        newlat = _pix_to_lat(0, latpix, 3, 640, 21)
        #print(newlat)
        latitude = newlat
    print(latitude)
    print('finish inc')
    for i in range(200000):
        sinlat = math.sin(math.radians(latitude))
        latpix = _EARTHPIX - _pixrad * math.log((1 + sinlat)/(1 - sinlat)) / 2
        newlat = _pix_to_lat(2, latpix, 3, 640, 21)
        #print(newlat)
        latitude = newlat
    print(latitude)
    print('finish dec')


if __name__ == "__main__":
    main()
