import os
import numpy as np
from matplotlib.image import imsave
import matplotlib.pyplot as plt

try:
    import pyueye.ueye as pue
except ImportError:
    pue = None  # don't throw an error if uye lib is not installed

from .ueye_codes import get_codes, invert_dict, error_codes


class CameraException(Exception):
    def __init__(self, camera, message='', code=-1, stop=True):
        i_error_codes = invert_dict(get_codes(error_codes))
        self.ueye_error = i_error_codes[code]
        self.message = message
        self.camera = camera
        if stop:
            self.close()
        else:
            self.status = 'running'

    def close(self):
        err = pue.is_ExitCamera(self.camera)
        if err == pue.IS_SUCCESS:
            self.status = 'closed'
        else:
            self.status = 'did not close'

    def __str__(self):
        return self.message + ', ' + self.ueye_error


class UEye(object):
    def __init__(self, cam_id=0, width=2048, height=1088):
        """
        Opens the camera connection and prepares the device for taking images.
        """
        self.image_data = None
        self._color_mode = None
        self._width = width
        self._height = height
        self._ppc_img_mem = None
        self._mem_id = None
        self._pitch = None
        self._c_width = None
        self._c_height = None
        self._c_pixel_bits = None
        self._bytes_per_pixel = 0
        self._video_capture = False

        if pue is None:
            raise RuntimeError(
                'uEye library could not be loaded, check the PYUEYE_DLL_PATH:'
                f' "{os.environ.get("PYUEYE_DLL_PATH", "")}"'
            )

        self._cam = pue.HIDS(cam_id)
        self._connect()
        self._configure_camera()
        self._set_color_mode('rgb8')
        self._allocate_memory()

    def __enter__(self):
        self.__init__()
        return self

    def __exit__(self):
        self.close()

    def close(self):
        self._deallocate_memory()
        err = pue.is_ExitCamera(self._cam)
        if err != pue.IS_SUCCESS:
            raise CameraException(self._cam, 'ueye>close>', err)

    def _set_color_mode(self, mode):
        self._color_mode = ColorMode(mode)
        err = pue.is_SetColorMode(self._cam, self._color_mode.code)
        if err != pue.IS_SUCCESS:
            raise CameraException(
                self._cam, 'ueye>configure_image>_set_color_mode>', err
            )

    def _connect(self):
        err = pue.is_InitCamera(self._cam, None)
        if err != pue.IS_SUCCESS:
            err = pue.is_EnableAutoExit(self._cam, 1)
        if err != pue.IS_SUCCESS:
            raise CameraException(self._cam, 'ueye>_connect>', err)

    def _configure_camera(self, mode='RGB8', **kwargs):
        err = pue.is_SetDisplayMode(self._cam, pue.IS_SET_DM_DIB)
        if err != pue.IS_SUCCESS:
            raise CameraException(
                self._cam, 'ueye>configure_image>set_display_mode>', err
            )
        err = pue.is_SetExternalTrigger(self._cam, pue.IS_SET_TRIGGER_SOFTWARE)
        if err != pue.IS_SUCCESS:
            raise CameraException(self._cam, 'ueye>configure_image>set_trigger>', err)
        err = pue.is_SetHardwareGain(self._cam, 0, 24, 0, 30)
        if err != pue.IS_SUCCESS:
            raise CameraException(
                self._cam, 'ueye>configure_image>set_hardware_gain>', err
            )
        err = pue.is_SetHardwareGamma(self._cam, pue.IS_SET_HW_GAMMA_OFF)
        if err != pue.IS_SUCCESS:
            raise CameraException(
                self._cam, 'ueye>configure_image>set_hardware_gamma>', err
            )
        '''
        black_level = 70
        c_BL = ctypes.c_void_p(black_level)

        err = pue.is_Blacklevel(self.cam, 8, IDS_SUCKS(70), 8)
        if err != pue.IS_SUCCESS:
            raise CameraException(self.cam, 'ueye>configure_image>set_black_level>', err)
        '''

    def _allocate_memory(self):
        """
        Allocates memory on the PC and camera
        """
        # init c-values
        self._c_width = pue.INT(self._width)
        self._c_height = pue.INT(self._height)
        self._c_pixel_bits = pue.INT(self._color_mode.bits_per_pixel)
        self._bytes_per_pixel = self._color_mode.bits_per_pixel / 8

        # the starting memory address for the image, will be returned
        self._ppc_img_mem = pue.c_mem_p()
        # the ID for the allocated image, will be returned
        self._mem_id = pue.INT()

        # allocate memory for an image
        err = pue.is_AllocImageMem(
            self._cam,
            self._c_width,
            self._c_height,
            self._c_pixel_bits,
            self._ppc_img_mem,
            self._mem_id,
        )
        if err != pue.IS_SUCCESS:
            raise CameraException(self._cam, 'ueye>_allocate_memory>', err)

        # make the image memory 'active'
        err = pue.is_SetImageMem(self._cam, self._ppc_img_mem, self._mem_id)
        if err != pue.IS_SUCCESS:
            raise CameraException(self._cam, 'ueye>_allocate_memory>', err)
        # create an array in python to which to copy the image
        self.image_data = np.zeros(
            (self._height, self._width, self._color_mode.channels),
            dtype=self._color_mode.dtype,
        )

    def _deallocate_memory(self):
        if self._ppc_img_mem is None:
            return
        # Releases an image memory that was allocated using is_AllocImageMem() and removes it from the driver management
        err = pue.is_FreeImageMem(self._cam, self._ppc_img_mem, self._mem_id)
        if err != pue.IS_SUCCESS:
            raise CameraException(self._cam, 'ueye>_deallocate_memory>', err)
        self._ppc_img_mem = None

    def capture(self):
        """
        Takes an image from the camera and places it in the computer memory
        """
        err = pue.is_FreezeVideo(
            self._cam, pue.IS_WAIT
        )  # IS_DONT_WAIT  = 0x0000, or IS_GET_LIVE = 0x8000
        if err != pue.IS_SUCCESS:
            raise CameraException(self._cam, 'ueye>capture>', err, False)
        err = pue.is_CopyImageMem(
            self._cam, self._ppc_img_mem, self._mem_id, self.image_data.ctypes.data
        )
        if err != pue.IS_SUCCESS:
            raise CameraException(self._cam, 'ueye>capture>', err, False)

    def save_image(self, path, take_snapshot=True):
        if take_snapshot:
            self.capture()
        imsave(path, self.image_data)

    def start_video_capture(self):
        # Activates the camera's live video mode (free run mode)
        err = pue.is_CaptureVideo(self._cam, pue.IS_DONT_WAIT)
        if err != pue.IS_SUCCESS:
            raise CameraException(self._cam, 'ueye>video_capture', err, False)
        self._pitch = pue.INT()
        err = pue.is_InquireImageMem(
            self._cam,
            self._ppc_img_mem,
            self._mem_id,
            self._c_width,
            self._c_height,
            self._c_pixel_bits,
            self._pitch,
        )
        if err != pue.IS_SUCCESS:
            raise CameraException(self._cam, 'ueye>video_capture', err, False)
        self._video_capture = True

    def get_video_frame(self):
        if not self._video_capture:
            return None

        if pue.IS_SUCCESS:
            array = pue.get_data(
                self._ppc_img_mem,
                self._c_width,
                self._c_height,
                self._c_pixel_bits,
                self._pitch,
                copy=False,
            )
            frame = np.reshape(
                array, (self._height, self._width, self._bytes_per_pixel)
            )
            return frame
        else:
            return None

    #
    # CAMERA AND IMAGE CONFIGURATION FUNCTIONS
    #

    def set_gain(self, master, red, green, blue):
        err = pue.is_SetHardwareGain(self._cam, master, red, green, blue)
        if err != pue.IS_SUCCESS:
            raise CameraException(self._cam, 'ueye>set_gain>', err, False)


class ColorMode:
    def __init__(self, mode):
        self.mode = mode
        self.code = self._modes[mode]
        if 'mono' in mode:
            self.channels = 1
        else:
            if 'a8' in mode or 'y8' in mode:
                self.channels = 4
            else:
                self.channels = 3
        if '8' in mode:
            self.bits_per_channel = 8
        if '10' in mode:
            self.bits_per_channel = 16
        if '12' in mode:
            self.bits_per_channel = 16
        if '16' in mode:
            self.bits_per_channel = 16

        self.bits_per_pixel = self.channels * self.bits_per_channel
        self.dtype = 'uint{}'.format(int(self.bits_per_channel))
        print(self.dtype)

    @property
    def _modes(self):
        return {
            'mono8': pue.IS_CM_MONO8,
            'mono10': pue.IS_CM_MONO10,
            'mono12': pue.IS_CM_MONO12,
            'mono16': pue.IS_CM_MONO16,
            'raw8': pue.IS_CM_SENSOR_RAW8,
            'raw10': pue.IS_CM_SENSOR_RAW10,
            'raw12': pue.IS_CM_SENSOR_RAW12,
            'raw16': pue.IS_CM_SENSOR_RAW16,
            'rgb8': pue.IS_CM_RGB8_PACKED,
            'rgba8': pue.IS_CM_RGBA8_PACKED,
            'rgby8': pue.IS_CM_RGBY8_PACKED,
            'rgb10': pue.IS_CM_RGB10_PACKED,
            'bgr8': pue.IS_CM_BGR8_PACKED,
            'bgr10': pue.IS_CM_BGR10_PACKED,
            'bgra8': pue.IS_CM_BGRA8_PACKED,
            'bgry8': pue.IS_CM_BGRY8_PACKED,
        }


if __name__ == '__main__':
    try:
        cam = UEye()
        cam.capture()
        plt.imshow(cam.image_data[:, :, :])
        # cam.save_image("C:\\Users\\Engineer\\Documents\\Alex\\test\\img.png")
        cam.close()
    except CameraException as ce:
        print(ce)
    '''
    finally:
        print('closing camera: ', pue.is_ExitCamera(pue.HIDS(0)))
    '''
