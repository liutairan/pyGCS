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

__author__ = "Tairan Liu"
__copyright__ = "Copyright 2017, Tairan Liu"
__credits__ = ["Tairan Liu", "Other Supporters"]
__license__ = "MIT"
__version__ = "0.4-dev"
__maintainer__ = "Tairan Liu"
__email__ = "liutairan2012@gmail.com"
__status__ = "Development"

class QuadStates():
    def __init__(self, frameid, addr_long, addr_short):
        self.frame_id = frameid
        self.address_long = addr_long
        self.address_short = addr_short

        self.msp_api_version = {'msp_protocol_version':0,'api_version_major':0,'api_version_minor':0}
        self.msp_board_info = {'board_identifier':'','hardware_revision':0}
        self.msp_ident = {'version':0, 'multitype':0, 'msp_version':0, 'capability':0}

        self.msp_misc = {'intPowerTrigger1':0, 'conf_minthrottle':0, 'maxthrottle':0, 'mincommand':0, 'failsafe_throttle':0, 'plog_arm_counter':0, 'plog_lifetime':0, 'conf_mag_declination':0, 'conf_vbatscale':0, 'conf_vbatlevel_warn1':0, 'conf_vbatlevel_warn2':0, 'conf_vbatlevel_crit':0}

        self.sensor_flags = {'hardware':0, 'pitot':0, 'sonar':0, 'gps':0, 'mag':0, 'baro':0, 'acc':0}

        self.msp_altitude = {'estalt':0, 'vario':0}
        self.msp_sonar_altitude = {'sonar_altitude':0}

        # GPS
        self.msp_raw_gps = {'gps_fix':0, 'gps_numsat':0, 'gps_lat':0, 'gps_lon':0, 'gps_altitude':0, 'gps_speed':0, 'gps_ground_course':0, 'gps_hdop':0}
        self.msp_comp_gps = {'range':0, 'direction':0, 'update':0}
        self.msp_gps_svinfo = {'gps_hdop':0}
        self.msp_gps_statistics = {'gps_last_message_dt':0, 'gps_errors':0, 'gps_timeouts':0, 'gps_packet_count':0, 'gps_hdop':0, 'gps_eph':0, 'gps_epv':0}

        self.msp_attitude = {'angx':0, 'angy':0, 'heading':0}

        self.msp_wp = {'wp_no':0, 'action':0, 'lat':0, 'lon':0, 'altitude':0, 'p1':0, 'p2':0, 'p3':0, 'flag':0}

        self.msp_nav_status = {'nav_mode':0, 'nav_state':0, 'action':0, 'wp_number':0, 'nav_error':0, 'mag_hold_heading':0}  # 'target_bearing'

        self.msp_nav_config = {'flag1':0, 'flag2':0, 'wp_radius':0, 'safe_wp_distance':0, 'nav_max_altitude':0, 'nav_speed_max':0, 'nav_speed_min':0, 'crosstrack_gain':0, 'nav_bank_max':0, 'rth_altitude':0, 'land_speed':0, 'fence':0, 'max_wp_number':0}

        self.msp_radio = {'rxerrors':0, 'fixed_errors':0, 'localrssi':0, 'remrssi':0, 'txbuf':0, 'noise':0, 'remnoise':0}

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
        self.flightModes = {'ARM':0,'ANGLE':0,'HORIZON':0,'FAILSAFE':0,'ALTHOLD':0,
                            'MAG':0,'HEADFREE':0,'HEADADJ':0,'NAVRTH':0,'POSHOLD':0,
                            'PASSTHRU':0,'HOMERESET':0,'NAVWP':0,'AIRMODE':0,'GCSNAV':0,
                            'HEADINGLOCK':0,'SURFACE':0,'TURNASSIST':0,'NAVLAUNCH':0}

        self.armStatus = {'OK_TO_ARM':0, 'PREVENT_ARMING':0, 'ARMED':0,
                          'WAS_EVER_ARMED':0, 'BLOCK_UAV_NOT_LEVEL':0,
                          'BLOCK_SENSORS_CALIB':0, 'BLOCK_SYSTEM_OVERLOAD':0,
                          'BLOCK_NAV_SAFETY':0, 'BLOCK_COMPASS_NOT_CALIB':0,
                          'BLOCK_ACC_NOT_CALIB':0, 'UNUSED':0, 'BLOCK_HARDWARE_FAILURE':0}

        self.missionList = []
        self.tempMission = []
