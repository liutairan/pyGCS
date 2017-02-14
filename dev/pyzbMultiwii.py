#!/usr/bin/env python

import serial, time, struct
from xbee import ZigBee
#from pyzigbee import ZigBee
import signal
from contextlib import contextmanager

class TimeoutException(Exception): pass

@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException, "Timed out!"
    signal.signal(signal.SIGALRM, signal_handler)
    #signal.alarm(seconds)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.alarm(0)

def message_received(data):
    print(len(data))



class MultiWii:

    # Multiwii MSP Commands
    API_VERSION = 1
    FC_VARIANT = 2
    FC_VERSION = 3
    BOARD_INFO = 4
    BUILD_INFO = 5
    
    MSP_INAV_PID = 6
    MSP_SET_INAV_PID = 7
    
    MSP_NAME = 10
    MSP_SET_NAME = 11
    
    NAV_POSHOLD = 12
    SET_NAV_POSHOLD = 13
    
    MODE_RANGES = 34    # MSP_MODE_RANGES    out message         Returns all mode ranges
    SET_MODE_RANGE = 35 # MSP_SET_MODE_RANGE in message          Sets a single mode range
    
    MSP_FEATURE = 36
    MSP_SET_FEATURE = 37
    
    MSP_BOARD_ALIGNMENT = 38
    MSP_SET_BOARD_ALIGNMENT = 39
    
    MSP_RX_CONFIG = 44
    MSP_SET_RX_CONFIG = 45
    
    MSP_ADJUSTMENT_RANGES = 52
    MSP_SET_ADJUSTMENT_RANGE = 53
    
    MSP_SONAR_ALTITUDE = 58      # SONAR cm
    
    MSP_PID_CONTROLLER = 59
    MSP_SET_PID_CONTROLLER = 60
    
    MSP_ARMING_CONFIG = 61         # out message         Returns auto_disarm_delay and disarm_kill_switch parameters
    MSP_SET_ARMING_CONFIG = 62     # in message          Sets auto_disarm_delay and disarm_kill_switch parameters
    
    REBOOT = 68    # in message reboot settings
    
    MSP_LOOP_TIME = 73 # out message         Returns FC cycle time i.e looptime parameter
    MSP_SET_LOOP_TIME = 74 # in message          Sets FC cycle time i.e looptime parameter

    MSP_FAILSAFE_CONFIG = 75 # out message         Returns FC Fail-Safe settings
    MSP_SET_FAILSAFE_CONFIG = 76 #in message          Sets FC Fail-Safe settings

    MSP_RXFAIL_CONFIG = 77 # out message         Returns RXFAIL settings
    MSP_SET_RXFAIL_CONFIG = 78 # in message          Sets RXFAIL settings
    
    
    IDENT = 100
    STATUS = 101
    RAW_IMU = 102
    SERVO = 103
    MOTOR = 104
    RC = 105
    RAW_GPS = 106
    COMP_GPS = 107
    ATTITUDE = 108
    ALTITUDE = 109
    ANALOG = 110
    RC_TUNING = 111
    PID = 112
    BOX = 113
    MISC = 114
    MOTOR_PINS = 115
    BOXNAMES = 116
    PIDNAMES = 117
    WP = 118
    BOXIDS = 119
    #SERVO_CONFIGURATIONS = 120
    CONTROL = 120
    #RC_RAW_IMU = 121  # Where is this code?
    NAV_STATUS = 121
    NAV_CONFIG = 122
    MSP_3D = 124
    MSP_RC_DEADBAND = 125
    MSP_SENSOR_ALIGNMENT = 126

    MSP_STATUS_EX = 150    # out message         cycletime, errors_count, CPU load, sensor present etc
    MSP_SENSOR_STATUS = 151    # out message         Hardware sensor status
    MSP_UID = 160    # out message         Unique device ID

    GPSSVINFO = 164
    GPSSTATISTICS = 166
    
    RADIO = 199
    SET_RAW_RC = 200
    SET_RAW_GPS = 201  # in message          fix, numsat, lat, lon, alt, speed
    SET_PID = 202      # in message          P I D coeff (9 are used currently)
    SET_BOX = 203
    SET_RC_TUNING = 204
    ACC_CALIBRATION = 205
    MAG_CALIBRATION = 206
    SET_MISC = 207
    RESET_CONF = 208
    SET_WP = 209
    SELECT_SETTING = 210
    #SWITCH_RC_SERIAL = 210
    SET_HEAD = 211
    #IS_SERIAL = 211
    MSP_SET_SERVO_CONFIGURATION = 212
    MSP_SET_MOTOR = 214
    MSP_SET_NAV_CONFIG = 215
    MSP_SET_3D = 217
    MSP_SET_RC_DEADBAND = 218
    MSP_SET_RESET_CURR_PID = 219
    MSP_SET_SENSOR_ALIGNMENT = 220
    
    MSP_ACC_TRIM = 240    # out message         get acc angle trim values
    MSP_SET_ACC_TRIM = 239    # in message          set acc angle trim values
    MSP_SERVO_MIX_RULES = 241    # out message         Returns servo mixer configuration
    MSP_SET_SERVO_MIX_RULE = 242    # in message          Sets servo mixer configuration
    MSP_SET_4WAY_IF = 245    # in message          Sets 4way interface


    EEPROM_WRITE = 250
    DEBUG = 254

    INFO_WP = 400

    """Class initialization"""
    def __init__(self, serPort):

        """Global variables of data"""
        self.msp_api_version = {'msp_protocol_version':0,'api_version_major':0,'api_version_minor':0}
        self.msp_board_info = {'board_identifier':'','hardware_revision':0}
        self.msp_ident = {'version':0, 'multitype':0, 'msp_version':0, 'capability':0}
        
        self.msp_misc = {'intPowerTrigger1':0, 'conf_minthrottle':0, 'maxthrottle':0, 'mincommand':0, 'failsafe_throttle':0, 'plog_arm_counter':0, 'plog_lifetime':0, 'conf_mag_declination':0, 'conf_vbatscale':0, 'conf_vbatlevel_warn1':0, 'conf_vbatlevel_warn2':0, 'conf_vbatlevel_crit':0}
        
        self.sensor_flags = {'hardware':0, 'pitot':0, 'sonar':0, 'gps':0, 'mag':0, 'baro':0, 'acc':0}
        
        self.msp_altitude = {'estalt':0, 'vario':0}
        self.msp_sonar_altitude = {'sonar_altitude':0}
        self.msp_raw_gps = {'gps_fix':0, 'gps_numsat':0, 'gps_lat':0, 'gps_lon':0, 'gps_altitude':0, 'gps_speed':0, 'gps_ground_course':0, 'gps_hdop':0}
        self.msp_attitude = {'angx':0, 'angy':0, 'heading':0}
        
        self.msp_wp = {'wp_no':0, 'action':0, 'lat':0, 'lon':0, 'altitude':0, 'p1':0, 'p2':0, 'p3':0, 'flag':0}
        
        self.msp_nav_status = {'gps_mode':0, 'nav_mode':0, 'action':0, 'wp_number':0, 'nav_error':0, 'target_bearing':0}
        
        self.msp_nav_config = {'flag1':0, 'flag2':0, 'wp_radius':0, 'safe_wp_distance':0, 'nav_max_altitude':0, 'nav_speed_max':0, 'nav_speed_min':0, 'crosstrack_gain':0, 'nav_bank_max':0, 'rth_altitude':0, 'land_speed':0, 'fence':0, 'max_wp_number':0}
        
        self.msp_radio = {'rxerrors':0, 'fixed_errors':0, 'localrssi':0, 'remrssi':0, 'txbuf':0, 'noise':0, 'remnoise':0}
        
        self.msp_comp_gps = {'range':0, 'direction':0, 'update':0}
        
        self.msp_rc_tuning = {'rc_rate':0, 'rc_expo':0, 'rollpitchrate':0, 'yawrate':0, 'dynthrpid':0, 'throttle_mid':0, 'throttle_expo':0}
        
        self.msp_analog = {'vbat':0, 'powermetersum':0, 'rssi':0, 'amps':0}
        
        self.nav_poshold = {'nav_user_control_mode':0, 'nav_max_speed':0, 'nav_max_climb_rate':0, 'nav_manual_speed':0, 'nav_manual_climb_rate':0, 'nav_mc_bank_angle':0, 'nav_use_midthr_for_althold':0, 'nav_mc_hover_thr':0, 'reserved':[0,0,0,0,0,0,0,0]}
        
        self.rcChannels = {'roll':0,'pitch':0,'yaw':0,'throttle':0,'aux1':0,'aux2':0,'aux3':0,'aux4':0,'elapsed':0,'timestamp':0}
        self.rawIMU = {'ax':0,'ay':0,'az':0,'gx':0,'gy':0,'gz':0,'mx':0,'my':0,'mz':0,'elapsed':0,'timestamp':0}
        self.motor = {'m1':0,'m2':0,'m3':0,'m4':0,'elapsed':0,'timestamp':0}
        self.attitude = {'angx':0,'angy':0,'heading':0,'elapsed':0,'timestamp':0}
        self.message = {'angx':0,'angy':0,'heading':0,'roll':0,'pitch':0,'yaw':0,'throttle':0,'elapsed':0,'timestamp':0}
        self.msp_status = {'cycleTime':0,'i2cError':0,'activeSensors':0,'flightModeFlags':0,'profile':0}
        self.msp_status_ex = {'cycletime':0, 'i2cError':0, 'activeSensors':0, 'flightModeFlags':0, 'profile':0, 'averageSystemLoadPercent':0, 'armingFlags':0}
        
        self.msp_sensor_status = {'hardware_health':0, 'gyro':0, 'acce':0, 'comp':0, 'baro':0, 'gps':0, 'range':0, 'pitot':0}
        self.msp_loop_time = {'looptime':0}
        self.activeBoxes = []
        self.flightModes = {'ARM':0,'ANGLE':0,'HORIZON':0,'FAILSAFE':0,'ALTHOLD':0}
        self.armStatus = {'OK_TO_ARM':0, 'PREVENT_ARMING':0, 'ARMED':0, 'WAS_EVER_ARMED':0, 'BLOCK_UAV_NOT_LEVEL':0, 'BLOCK_SENSORS_CALIB':0, 'BLOCK_SYSTEM_OVERLOAD':0, 'BLOCK_NAV_SAFETY':0, 'BLOCK_COMPASS_NOT_CALIB':0, 'BLOCK_ACC_NOT_CALIB':0, 'UNUSED':0, 'BLOCK_HARDWARE_FAILURE':0}
        
        self.missionLists = []
        self.tempMission = []
        
        self.temp = ();
        self.temp2 = ();
        self.elapsed = 0
        self.PRINT = 1

        self.ser = serial.Serial()
        self.ser.port = serPort
        self.ser.baudrate = 115200
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.parity = serial.PARITY_NONE
        self.ser.stopbits = serial.STOPBITS_ONE
        self.ser.timeout = 1
        self.ser.xonxoff = False
        self.ser.rtscts = False
        self.ser.dsrdtr = False
        self.ser.writeTimeout = 2
        self.zb = ZigBee(self.ser)
        """Time to wait until the board becomes operational"""
        wakeup = 3
        try:
            self.ser.open()
            
            if self.PRINT:
                print "Waking up board on "+self.ser.port+"..."
            for i in range(1,wakeup):
                if self.PRINT:
                    print wakeup-i
                    time.sleep(1)
                else:
                    time.sleep(1)
            
        except Exception, error:
            print "\n\nError opening "+self.ser.port+" port.\n"+str(error)+"\n\n"

    def flushSerial(self):
        self.ser.flushInput()
        self.ser.flushOutput()

    def stopDevice(self):
        self.zb.halt()
        self.ser.close()

    """Function to receive a data packet from the board"""
    def getData(self, data_length, send_code, send_data, frameid='\x01', d_addr_long='\x00\x00\x00\x00\x00\x00\xFF\xFF', d_addr='\xFF\xFE'): #
        try:
            start = time.time()
            totaldata = self.requestData(data_length, send_code, send_data, frameid, d_addr_long, d_addr)
            datalength = struct.unpack('<B', totaldata[3])[0]
            cmd = struct.unpack('<B', totaldata[4])[0]
            data = totaldata[5:]

            elapsed = time.time() - start
            if cmd == MultiWii.ATTITUDE:
                temp = struct.unpack('<'+'h'*(datalength/2)+'B',data)
                self.attitude['angx']=float(temp[0]/10.0)
                self.attitude['angy']=float(temp[1]/10.0)
                self.attitude['heading']=float(temp[2])
                self.attitude['elapsed']=round(elapsed,3)
                self.attitude['timestamp']="%0.2f" % (time.time(),)
                self.msp_attitude['angx'] = float(temp[0]/10.0)
                self.msp_attitude['angy'] = float(temp[1]/10.0)
                self.msp_attitude['heading'] = float(temp[2])
                #return self.attitude
            elif cmd == MultiWii.RC:           # checked
                temp = struct.unpack('<'+'h'*(datalength/2)+'B',data)
                self.rcChannels['roll']=temp[0]
                self.rcChannels['pitch']=temp[1]
                self.rcChannels['yaw']=temp[2]
                self.rcChannels['throttle']=temp[3]
                self.rcChannels['aux1'] = temp[4]
                self.rcChannels['aux2'] = temp[5]
                self.rcChannels['aux3'] = temp[6]
                self.rcChannels['aux4'] = temp[7]
                # to do aux
                self.rcChannels['elapsed']=round(elapsed,3)
                self.rcChannels['timestamp']="%0.2f" % (time.time(),)
                #return self.rcChannels
            elif cmd == MultiWii.RAW_IMU:       # checked
                temp = struct.unpack('<'+'h'*(datalength/2)+'B',data)
                self.rawIMU['ax']=float(temp[0])
                self.rawIMU['ay']=float(temp[1])
                self.rawIMU['az']=float(temp[2])
                self.rawIMU['gx']=float(temp[3])
                self.rawIMU['gy']=float(temp[4])
                self.rawIMU['gz']=float(temp[5])
                self.rawIMU['mx']=float(temp[6])
                self.rawIMU['my']=float(temp[7])
                self.rawIMU['mz']=float(temp[8])
                self.rawIMU['elapsed']=round(elapsed,3)
                self.rawIMU['timestamp']="%0.2f" % (time.time(),)
                #return self.rawIMU
            elif cmd == MultiWii.MOTOR:
                temp = struct.unpack('<'+'h'*(datalength/2)+'B',data)
                self.motor['m1']=float(temp[0])
                self.motor['m2']=float(temp[1])
                self.motor['m3']=float(temp[2])
                self.motor['m4']=float(temp[3])
                self.motor['elapsed']="%0.3f" % (elapsed,)
                self.motor['timestamp']="%0.2f" % (time.time(),)
                return self.motor
            elif cmd == MultiWii.STATUS:
                temp = struct.unpack('<3HI2B',data)
                self.msp_status['cycleTime'] = temp[0]
                self.msp_status['i2cError'] = temp[1]
                self.msp_status['activeSensors'] = temp[2]
                self.msp_status['flightModeFlags'] = temp[3]
                self.msp_status['profile'] = temp[4]
            elif cmd == MultiWii.MSP_STATUS_EX:       # checked
                temp = struct.unpack('<3HIB2HB',data)
                self.msp_status_ex['cycletime'] = temp[0]
                self.msp_status_ex['i2cError'] = temp[1]
                self.msp_status_ex['activeSensors'] = temp[2]
                self.msp_status_ex['flightModeFlags'] = temp[3]
                self.msp_status_ex['profile'] = temp[4]
                self.msp_status_ex['averageSystemLoadPercent'] = temp[5]
                self.msp_status_ex['armingFlags'] = temp[6]
                #self.parseSensorStatus(self.msp_status_ex['activeSensors'])
            elif cmd == MultiWii.MSP_SENSOR_STATUS:
                temp = struct.unpack('<9B',data)
                # to do

            elif cmd == MultiWii.MSP_LOOP_TIME:
                temp = struct.unpack('<H',data)
                self.msp_loop_time['looptime'] = temp[0]

            elif cmd == MultiWii.API_VERSION:
                temp = struct.unpack('<3B',data)
                self.msp_api_version['msp_protocol_version'] = temp[0]
                self.msp_api_version['api_version_major'] = temp[1]
                self.msp_api_version['api_version_minor'] = temp[2]
            elif cmd == MultiWii.BOARD_INFO:
                temp = struct.unpack('<'+'b'*(datalength-2) + 'H',data)
                self.msp_board_info['board_identifier'] = temp[0]
                self.msp_board_info['hardware_revision'] = temp[1]

            elif cmd == MultiWii.IDENT:
                temp = struct.unpack('<3BI',data)
                self.msp_ident['version'] = temp[0]
                self.msp_ident['multitype'] = temp[1]
                self.msp_ident['msp_version'] = temp[2]
                self.msp_ident['capability'] = temp[3]

            elif cmd == MultiWii.MISC:
                temp = struct.unpack('<6HIH4B',data) # not right
                self.msp_misc['intPowerTrigger1'] = temp[0]
                self.msp_misc['maxthrottle'] = temp[2]
                self.msp_misc['mincommand'] = temp[3]
                # to do
            elif cmd == MultiWii.ALTITUDE:         # may not working
                temp = struct.unpack('<IHB',data)
                self.msp_altitude['estalt'] = temp[0]
                self.msp_altitude['vario'] = temp[1]

            elif cmd == MultiWii.RADIO:
                temp = struct.unpack('<2H6B',data)
                self.msp_radio['rxerrors'] = temp[0]
                self.msp_radio['fixed_errors'] = temp[1]
                self.msp_radio['localrssi'] = temp[2]
                self.msp_radio['remrssi'] = temp[3]
                self.msp_radio['txbuf'] = temp[4]
                self.msp_radio['noise'] = temp[5]
                self.msp_radio['remnoise'] = temp[6]

            elif cmd == MultiWii.MSP_SONAR_ALTITUDE: # checked
                temp = struct.unpack('<iB',data)
                self.msp_sonar_altitude['sonar_altitude'] = temp[0]

            elif cmd == MultiWii.ANALOG:          # checked, vbat:109
                temp = struct.unpack('<B3HB',data)
                self.msp_analog['vbat'] = temp[0]
                self.msp_analog['powermetersum'] = temp[1]
                self.msp_analog['rssi'] = temp[2]
                self.msp_analog['amps'] = temp[3]
            elif cmd == MultiWii.MODE_RANGES:
                # not working,
                # because the data feedback should be '3c2B'+'80B'+'B',
                # longer than the permitted length of XBEE S2 AT ROUTER (84 Bytes).
                # So the data is separated to 2 frames.
                # But there are only two bytes (one byte for real range data, one byte for checksum) in the second frame,
                # so it does not worth to wait for another frame.
                #print(datalength)
                #print(len(data))
                temp = struct.unpack('<'+'B'*(len(data)),data)
                print(temp)
                # to do
            elif cmd == MultiWii.MSP_ADJUSTMENT_RANGES:
                pass
                # to do
            elif cmd == MultiWii.BOXIDS: # checked
                #print('right')
                #print(datalength)
                #print(len(data))
                temp = struct.unpack('<'+'B'*datalength + 'B',data)
                self.activeBoxes = list(temp)
                #print(temp)
                # to do
            elif cmd == MultiWii.RAW_GPS:
                temp = struct.unpack('<2B2I4H',data)
                # to do
            elif cmd == MultiWii.COMP_GPS:
                temp = struct.unpack('<2HB',data)
                # to do
            elif cmd == MultiWii.NAV_STATUS:
                temp = struct.unpack('<5BH',data)
                # to do
            elif cmd == MultiWii.GPSSVINFO:
                temp = struct.unpack('<5B',data)
                # to do
            elif cmd == MultiWii.GPSSTATISTICS:
                temp = struct.unpack('<H3I3H',data)
                # to do
            elif cmd == MultiWii.MSP_FEATURE:
                temp = struct.unpack('<I',data)
                # to do
            elif cmd == MultiWii.MSP_BOARD_ALIGNMENT:
                temp = struct.unpack('<3H',data)
                # to do
            elif cmd == MultiWii.MSP_RX_CONFIG:
                pass
                # to do
            elif cmd == MultiWii.MSP_FAILSAFE_CONFIG:
                pass
                # to do
            elif cmd == MultiWii.MSP_RXFAIL_CONFIG:
                pass
                # to do
            elif cmd == MultiWii.MSP_SENSOR_ALIGNMENT:
                temp = struct.unpack('<3B',data)
                # to do
            elif cmd == MultiWii.WP:
                temp = struct.unpack('<2B3i3h2B',data)
                self.tempMission = list(temp)
            else:
                return "No return error!"
        except Exception, error:
            print(Exception)
            print error
            pass

    def requestData(self, data_length, send_code, send_data, frameid='\x01', d_addr_long='\x00\x00\x00\x00\x00\x00\xFF\xFF', d_addr='\xFF\xFE'):
        rec_data = ''
        while True:
            self.sendCMDNew(data_length, send_code, send_data, frameid, d_addr_long, d_addr)
            try:
                with time_limit(0.005):   # 0.005
                    if send_code == MultiWii.MODE_RANGES:
                        rec_data = self.readZBMsg(1)
                    else:
                        rec_data = self.readZBMsg(1)
            except:
                #print('Time out')
                pass

            validation = self.preCheckReadData(rec_data, send_code, send_data)
            if validation == True:
                break
            else:
                pass
        return rec_data

    def readZBMsg(self, framenum=1):
        tempdata = ''
        if framenum == 1:
            packet = self.zb.wait_read_frame()
            if packet['id'] == 'tx_status':
                pass
            elif packet['id'] == 'rx':
                tempdata = packet['rf_data']
        elif framenum == 2:
            i = 0
            tempframedata = ''
            while i < 2:
                packet = self.zb.wait_read_frame()
                if packet['id'] == 'tx_status':
                    pass
                elif packet['id'] == 'rx':
                    tempframedata = packet['rf_data']
                    tempdata = tempdata + tempframedata
                    i = i + 1
        else:
            pass

        return tempdata

    def preCheckReadData(self, rec_data, send_code, send_data):
        header = rec_data[0:3]
        if header == '$M>':
            pass
        else:
            return False
        if send_code == MultiWii.MODE_RANGES:
            if len(rec_data) >= 17:
                return True
            else:
                return False
        else:
            if len(rec_data) >= 5:
                return True
            else:
                return False

    # input field "data" must be in a list
    def sendCMDNew(self, data_length, send_code, send_data, frameid='\x01', d_addr_long='\x00\x00\x00\x00\x00\x00\xFF\xFF', d_addr='\xFF\xFE'):
        checksum = 0
        total_data = ['$', 'M', '<', data_length, send_code] + send_data
        cmd = send_code
        #print(cmd)
        if data_length == 0:
            for i in struct.pack('<2B', *total_data[3:len(total_data)]):
                checksum = checksum ^ ord(i)
            total_data.append(checksum)
            try:
                tempdata = struct.pack('<3c3B', *total_data)
                #print((tempdata).encode('hex'))
                b = None
                b = self.zb.send('tx', frame_id = frameid, dest_addr_long = d_addr_long, dest_addr=d_addr, data=tempdata)
            except Exception, error:
                pass
        elif data_length > 0:
            if cmd == MultiWii.SET_RAW_RC:
                for i in struct.pack('<2B%dH' % len(send_data), *total_data[3:len(total_data)]):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempdata = struct.pack('<3c2B%dHB' % len(send_data), *total_data)
                    b = None
                    b = self.zb.send('tx', frame_id = frameid, dest_addr_long = d_addr_long, dest_addr = d_addr, data = tempdata)
                except Exception, error:
                    pass
            elif cmd == MultiWii.WP:
                for i in struct.pack('<3B', *total_data[3:len(total_data)]):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempdata = struct.pack('<3c4B', *total_data)
                    b = None
                    b = self.zb.send('tx', frame_id = frameid, dest_addr_long = d_addr_long, dest_addr = d_addr, data = tempdata)
                except Exception, error:
                    print(error)
            elif cmd == MultiWii.SET_WP:
                for i in struct.pack('<2B2B3i3hB', *total_data[3:len(total_data)]):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempdata = struct.pack('<3c4B3i3h2B', *total_data)
                    b = None
                    b = self.zb.send('tx', frame_id = frameid, dest_addr_long = d_addr_long, dest_addr = d_addr, data = tempdata)
                except Exception, error:
                    print(Exception,error)
        else:
            pass


    def parseSensorStatus(self, sensorStatus):
        temp = format(sensorStatus, '016b')
        self.sensor_flags['hardware'] = int(temp[0])
        self.sensor_flags['pitot'] = int(temp[9])
        self.sensor_flags['sonar'] = int(temp[11])
        self.sensor_flags['gps'] = int(temp[12])
        self.sensor_flags['mag'] = int(temp[13])
        self.sensor_flags['baro'] = int(temp[14])
        self.sensor_flags['acc'] = int(temp[15])

    def parseArmingFlags(self, armflag):
        temp = format(armflag, '016b')
        self.armStatus['OK_TO_ARM'] = temp[15]
        self.armStatus['PREVENT_ARMING'] = temp[14]
        self.armStatus['ARMED'] = temp[13]
        self.armStatus['WAS_EVER_ARMED'] = temp[12]
        self.armStatus['BLOCK_UAV_NOT_LEVEL'] = temp[7]
        self.armStatus['BLOCK_SENSORS_CALIB'] = temp[6]
        self.armStatus['BLOCK_SYSTEM_OVERLOAD'] = temp[5]
        self.armStatus['BLOCK_NAV_SAFETY'] = temp[4]
        self.armStatus['BLOCK_COMPASS_NOT_CALIB'] = temp[3]
        self.armStatus['BLOCK_ACC_NOT_CALIB'] = temp[2]
        self.armStatus['UNUSED'] = temp[1]
        self.armStatus['BLOCK_HARDWARE_FAILURE'] = temp[0]

    def parseFlightModeFlags(self, activeboxes, flightModeFlags):
        if len(activeboxes) == 0:
            return False
        else:
            temp = format(flightModeFlags, '032b')
            armInd = activeboxes.index(0)
            angleInd = activeboxes.index(1)
            horizonInd = activeboxes.index(2)
            altholdInd = activeboxes.index(3)
            failsafeInd = activeboxes.index(27)
            self.flightModes['ARM'] = int(temp[31-armInd])
            self.flightModes['ANGLE'] = int(temp[31-angleInd])
            self.flightModes['HORIZON'] = int(temp[31-horizonInd])
            self.flightModes['ALTHOLD'] = int(temp[31-altholdInd])
            self.flightModes['FAILSAFE'] = int(temp[31-failsafeInd])
            return True

    # upload mission will automatically download the mission and compare it
    def uploadMission(self, mission, frameid='\x01', d_addr_long='\x00\x00\x00\x00\x00\x00\xFF\xFF', d_addr='\xFF\xFE'):
        while True:
            self.sendCMDNew(21, MultiWii.SET_WP, mission, frameid, d_addr_long, d_addr)
            index = mission[0]
            tempRecMission = self.downloadMission(index, frameid, d_addr_long, d_addr)
            uploadStatus = self.checkMissionUpload(mission, tempRecMission)
            if uploadStatus == True:
                break
            else:
                pass

    def checkMissionUpload(self, missionSend, missionRec):
        if missionSend == missionRec[:-1]:
            return True
        else:
            return False

    def uploadMissions(self, missionList, frameid='\x01', d_addr_long='\x00\x00\x00\x00\x00\x00\xFF\xFF', d_addr='\xFF\xFE'):
        for i in range(len(missionList)):
            self.uploadMission(missionList[i], frameid, d_addr_long, d_addr)

    # all_missions is a list: [{},{},{}], inside the list are dicts.
    # {'frameid':0, 'dest_addr_long':'', 'dest_addr':'', 'missionlist':[]}
    def uploadAllMissions(self, all_missions):
        for i in range(len(all_missions)):
            tempSendMission = all_missions[i]
            temp_frameid = tempSendMission['frameid']
            temp_d_addr_long = tempSendMission['dest_addr_long']
            temp_d_addr = tempSendMission['dest_addr']
            temp_missionList = tempSendMission['missionlist']
            self.uploadMissions(temp_missionList, temp_frameid, temp_d_addr_long, temp_d_addr)

    def downloadMission(self, id, frameid='\x01', d_addr_long='\x00\x00\x00\x00\x00\x00\xFF\xFF', d_addr='\xFF\xFE'):
        mission = []
        while True:
            self.getData(1, MultiWii.WP,[id], frameid, d_addr_long, d_addr)
            if len(self.tempMission) > 0:
                if self.tempMission[0] == id:
                    mission = self.tempMission
                    break
        return mission

    def downloadMissions(self, frameid='\x01', d_addr_long='\x00\x00\x00\x00\x00\x00\xFF\xFF', d_addr='\xFF\xFE'):
        missionList = []
        i = 1
        while True:
            flag = 0
            tempRecMission = self.downloadMission(i, frameid, d_addr_long, d_addr)
            missionList.append(tempRecMission)
            print(tempRecMission)
            flag = tempRecMission[8]
            if flag == 165:
                break
            else:
                i = i +1

        return missionList

    # targets is a list: [{},{},{}], inside the list are dicts.
    # {'frameid':0, 'dest_addr_long':'', 'dest_addr':''}
    def downloadAllMissions(self, targets):
        for i in range(len(targets)):
            tempTarget = targets[i]
            temp_frameid = tempTarget['frameid']
            temp_d_addr_long = tempTarget['dest_addr_long']
            temp_d_addr = tempTarget['dest_addr']
            print('start download for: ' + ''.join("{:02x}".format(ord(c)) for c in temp_d_addr_long))
            self.downloadMissions(temp_frameid, temp_d_addr_long,temp_d_addr)
