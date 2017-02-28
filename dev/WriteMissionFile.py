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
import sys

__author__ = "Tairan Liu"
__copyright__ = "Copyright 2017, Tairan Liu"
__credits__ = ["Tairan Liu", "Other Supporters"]
__license__ = "MIT"
__version__ = "0.4-dev"
__maintainer__ = "Tairan Liu"
__email__ = "liutairan2012@gmail.com"
__status__ = "Development"

def WriteMissionFile(inputPath, dataList):
    tempOutData = dataList
    _to_write = ""
    for i in range(len(tempOutData)):
        _temp_list = tempOutData[i]
        _temp_line = str(_temp_list['id']) + ',' + str(_temp_list['type']) + ',' + str(_temp_list['lat']) + ',' + str(_temp_list['lon']) + ',' + str(_temp_list['alt']) + ',' + str(_temp_list['p1']) + ',' + str(_temp_list['p2']) + ',' + str(_temp_list['p3']) + '\n'
        _to_write = _to_write + _temp_line
    with open(inputPath, 'w') as outf:
        outf.write(_to_write)
