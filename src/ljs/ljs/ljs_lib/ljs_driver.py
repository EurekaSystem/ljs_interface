import ctypes
import faulthandler
import os
import time
from pathlib import Path

import numpy as np
from PIL import Image
from loguru import logger

from . import LJSwrap

faulthandler.enable()

TRG_READY = 0x0020  # Bitmask for the trigger ready status.


class LJSDriver:

    def __init__(self, address, port=24691, high_speed_port=24692, y_line_interpolation=1):
        """ Questa fa questo

        :param str address: it must be a valid ipv4 address ex. 192.168.1.1
        :param port: normal port to camera default 24691
        :param high_speed_port:
        :param yline_interpolation: value from 1 to 8 represents how much line scan
        """
        # properties
        self._device_id = 0
        self.address = address
        self.high_speed_port_no = high_speed_port  # Port No. for high-speed
        self.y_line_interpolation = y_line_interpolation  # Port No. for high-speed
        self.port_no = port  # Port No. for high-speed
        self.scan_timeout = 50  # Timeout value for the acquiring image

        self._acquisition_completed = False
        self._scanned_y_size = 0
        self._processing_timeout = False
        self._acquisition_timeout = False
        self.z_val = []
        self.lumi_val = []
        self.connection_status = 0
        self.x_size = 0
        self.y_size = 0

        self.__profinfo = None

        # unpack address
        _address = self.address.split('.')

        # check input data
        if (self.y_line_interpolation < 1) or (self.y_line_interpolation > 8):
            logger.error('yline_interpolation must be between 1 and 8')
            raise Exception('')

        if not len(_address):
            logger.error('address must be a valid ipv4 address')
            raise Exception('')

        # set LJS ethernet configuration
        self._ethernet_config = LJSwrap.LJS8IF_ETHERNET_CONFIG()
        self._ethernet_config.abyIpAddress[0] = int(_address[0])
        self._ethernet_config.abyIpAddress[1] = int(_address[1])
        self._ethernet_config.abyIpAddress[2] = int(_address[2])
        self._ethernet_config.abyIpAddress[3] = int(_address[3])
        self._ethernet_config.wPortNo = self.port_no

    def init_scan_data(self):
        self._acquisition_completed = False
        self._scanned_y_size = 0
        self._processing_timeout = False
        self._acquisition_timeout = False
        self.z_val = []
        self.lumi_val = []
        self.x_size = 0
        self.y_size = 0

    def scan(self, save_format, base_path, img_base_name):
        """

        """

        # Start ethernet communication
        logger.debug(f"Start connection")
        self.init_scan_data()

        res = LJSwrap.LJS8IF_EthernetOpen(0, self._ethernet_config)
        if res != 0:
            logger.error(f"Failed to connect to the controller, Error: {res}")
            LJSwrap.LJS8IF_CommunicationClose(self._device_id)
            raise Exception('Connection failed')
        else:
            logger.debug(f"Connection established")

        # Initialize Hi-Speed Communication
        logger.debug(f"Initialize high speed communication")
        my_callback_s_a = LJSwrap.LJS8IF_CALLBACK_SIMPLE_ARRAY(self._callback_s_a)
        res = LJSwrap.LJS8IF_InitializeHighSpeedDataCommunicationSimpleArray(
            self._device_id,
            self._ethernet_config,
            self.high_speed_port_no,
            my_callback_s_a,
            0
        )
        if res != 0:
            logger.error(f"Failed initialize high speed communication, Error: {res}")
            LJSwrap.LJS8IF_FinalizeHighSpeedDataCommunication(self._device_id)
            LJSwrap.LJS8IF_CommunicationClose(self._device_id)
            raise Exception('initialization heigh speed communication failed')
        else:
            logger.debug("Height speed communication initialized")

        # Start Hi-Speed Communication
        logger.debug(f"Start high speed communication")
        req = LJSwrap.LJS8IF_HIGH_SPEED_PRE_START_REQ()
        req.bySendPosition = 2
        self.__profinfo = LJSwrap.LJS8IF_HEIGHT_IMAGE_INFO()

        res = LJSwrap.LJS8IF_PreStartHighSpeedDataCommunication(self._device_id, req, False, self.__profinfo)
        if res != 0:
            logger.error(f"Failed pre-start high speed communication, Error: {res}")
            LJSwrap.LJS8IF_FinalizeHighSpeedDataCommunication(self._device_id)
            LJSwrap.LJS8IF_CommunicationClose(self._device_id)
            raise Exception('pre-start high speed communication failed')

        res = LJSwrap.LJS8IF_StartHighSpeedDataCommunication(self._device_id)
        if res != 0:
            logger.error(f"Failed start high speed communication, Error: {res}")
            LJSwrap.LJS8IF_FinalizeHighSpeedDataCommunication(self._device_id)
            LJSwrap.LJS8IF_CommunicationClose(self._device_id)
            raise Exception('start high speed communication failed')
        else:
            logger.debug("Height speed communication started")

        # Initialize result data
        self.x_size = self.__profinfo.wXPointNum
        self.y_size = self.__profinfo.wYLineNum
        self.z_val = [0] * self.x_size * self.y_size
        self.lumi_val = [0] * self.x_size * self.y_size

        # Check laser status before send trigger
        status = ctypes.c_ushort()
        start_time = time.time()
        wait_trigger_sec = 0
        while True:
            LJSwrap.LJS8IF_GetAttentionStatus(self._device_id, status)
            if status.value & TRG_READY:
                break
            wait_trigger_sec = time.time() - start_time
            if wait_trigger_sec > self.scan_timeout:
                break

        # Send trigger to the camera
        logger.debug(f"Send trigger to the camera")
        res = LJSwrap.LJS8IF_Trigger(self._device_id)
        if res != 0:
            logger.error(f"Failed send trigger to camera, Error: {res}")
            LJSwrap.LJS8IF_StopHighSpeedDataCommunication(self._device_id)
            LJSwrap.LJS8IF_FinalizeHighSpeedDataCommunication(self._device_id)
            LJSwrap.LJS8IF_CommunicationClose(self._device_id)
            raise Exception('failed trigger')

        # wait for the image acquisition complete
        start_time = time.time()
        while True:
            if self._acquisition_completed:
                break
            if time.time() - start_time > self.scan_timeout - wait_trigger_sec:
                self._acquisition_timeout = True
                logger.error(f"Acquisition timeout")
                raise Exception('acquisition timeout')

        # Close connection
        LJSwrap.LJS8IF_FinalizeHighSpeedDataCommunication(self._device_id)
        LJSwrap.LJS8IF_CommunicationClose(self._device_id)

        if self.y_line_interpolation > 1:
            # Interpolation
            tmp = np.reshape(self.z_val, (self.y_size, self.x_size))
            tmp = np.tile(tmp, self.y_line_interpolation)
            self.z_val = tmp.reshape(self.y_size * self.y_line_interpolation * self.x_size)

            tmp = np.reshape(self.lumi_val, (self.y_size, self.x_size))
            tmp = np.tile(tmp, self.y_line_interpolation)
            self.lumi_val = tmp.reshape(self.y_size * self.y_line_interpolation * self.x_size)

            # Update the profile information
            self.__profinfo.wYLineNum *= self.y_line_interpolation
            self.y_size = self.__profinfo.wYLineNum
            self.__profinfo.dwPitchY = int(self.__profinfo.dwPitchY / self.y_line_interpolation)

        logger.debug("----------------------------------------")
        logger.debug(f"Luminance output     : {self.__profinfo.byLuminanceOutput}")
        logger.debug(f"Number of X points   : {self.__profinfo.wXPointNum}")
        logger.debug(f"Number of Y lines    : {self.__profinfo.wYLineNum}")
        logger.debug(f"X pitch in micrometer: {self.__profinfo.dwPitchX / 100.0}")
        logger.debug(f"Y pitch in micrometer: {self.__profinfo.dwPitchY / 100.0}")
        logger.debug(f"Z pitch in micrometer: {self.__profinfo.dwPitchZ / 100.0}")
        logger.debug(f"Processing Timeout   : {self._processing_timeout}")
        logger.debug("----------------------------------------")

        if save_format == 'tif':
            self.tif_render(base_path, img_base_name)
        elif save_format == 'dump':
            self.np_dump(base_path, img_base_name)
        elif save_format == 'raw':
            return {"luminance_data": self.lumi_val, "depth_data": self.z_val}

    def tif_render(self, base_path='./', base_name='img', render_luminance_image=True, render_depth_image=True):

        _path = Path(base_path)
        _path.mkdir(parents=True, exist_ok=True)
        os.chmod(_path, 0o777)
        print(_path.resolve())

        if render_depth_image:
            _img = Image.new('I;16', (self.x_size, self.y_size))
            _img.putdata(np.asarray(self.z_val, dtype=np.uint16))
            _img.save(f'{base_path}/{base_name}_depth.tif')

        if render_luminance_image:
            _img = Image.new('L', (self.x_size, self.y_size))
            _img.putdata(np.asarray(self.lumi_val, dtype=np.uint16))
            _img.save(f'{base_path}/{base_name}_lum.tif')

    def np_dump(self, base_path='./', base_name='img', render_luminance_image=True, render_depth_image=True):

        if render_depth_image:
            np.asarray(self.z_val, dtype=np.uint16).dump(f'{base_path}{base_name}_depth')

        if render_luminance_image:
            np.asarray(self.lumi_val, dtype=np.uint16).dump(f'{base_path}{base_name}_lum')

    def _callback_s_a(self, p_header, p_height, p_lumi, luminance_enable, xpointnum, profnum, notify, user):
        try:
            if notify == 0 or notify == 0x10000:
                if profnum != 0:
                    if not self._acquisition_completed and not self._acquisition_timeout:
                        self._processing_timeout = p_header.contents.byProcTimeout > 0
                        for i in range(xpointnum * profnum):
                            self.z_val[i] = p_height[i]
                            if luminance_enable == 1:
                                self.lumi_val[i] = p_lumi[i]

                        self._scanned_y_size = profnum
                        self._acquisition_completed = True

            if notify == 1:
                self.connection_status = 0
        except Exception as e:
            logger.exception(e)
        return

#
# scanner = LJSDriver('10.97.6.35')
# scanner.scan('tif', './', 'test')
