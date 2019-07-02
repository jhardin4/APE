import pyueye.ueye as pue
import numpy as np
import ueye_codes
import ctypes
from matplotlib.image import imsave
import matplotlib.pyplot as plt

class CameraException(Exception):
    def __init__(self, camera, message = '', code = -1, stop = True):
        i_error_codes = ueye_codes.invert_dict(ueye_codes.get_codes(ueye_codes.error_codes))
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
        
class ueye(object):
    def __init__(self, cam_id = 0):
        '''
        Opens the camera connection and prepares the device for taking images.
        '''
        self.cam = pue.HIDS(cam_id)
        self.connect()
        self.configure_camera()
        self.set_color_mode('rgb8')
        self.allocate_memory()
    
    def __enter__(self):
        self.__init__()
        return self
        
    def __exit__(self):
        self.close()
        
    def connect(self):
        err = pue.is_InitCamera(self.cam, None)
        if err != pue.IS_SUCCESS:
            err = pue.is_EnableAutoExit(self.cam, 1)
        if err != pue.IS_SUCCESS:
            raise CameraException(self.cam, 'ueye>connect>', err)
            
    def close(self):
        err = pue.is_ExitCamera(self.cam)
        if err != pue.IS_SUCCESS:
            raise CameraException(self.cam, 'ueye>close>', err)
                
    def configure_camera(self, mode = 'RGB8', **kwargs):
        err = pue.is_SetDisplayMode(self.cam, pue.IS_SET_DM_DIB)
        if err != pue.IS_SUCCESS:
            raise CameraException(self.cam, 'ueye>configure_image>set_display_mode>', err)
        err = pue.is_SetExternalTrigger(self.cam, pue.IS_SET_TRIGGER_SOFTWARE)
        if err != pue.IS_SUCCESS:
            raise CameraException(self.cam, 'ueye>configure_image>set_trigger>', err)
        err = pue.is_SetHardwareGain(self.cam, 0, 24, 0, 30)
        if err != pue.IS_SUCCESS:
            raise CameraException(self.cam, 'ueye>configure_image>set_hardware_gain>', err)
        err = pue.is_SetHardwareGamma (self.cam, pue.IS_SET_HW_GAMMA_OFF)
        if err != pue.IS_SUCCESS:
            raise CameraException(self.cam, 'ueye>configure_image>set_hardware_gamma>', err)
        '''
        black_level = 70
        c_BL = ctypes.c_void_p(black_level)
        
        err = pue.is_Blacklevel(self.cam, 8, IDS_SUCKS(70), 8)
        if err != pue.IS_SUCCESS:
            raise CameraException(self.cam, 'ueye>configure_image>set_black_level>', err)
        '''
    def set_color_mode(self, mode):
        self.color_mode = ColorMode(mode)
        err = pue.is_SetColorMode(self.cam, self.color_mode.code)
        if err != pue.IS_SUCCESS:
            raise CameraException(self.cam, 'ueye>configure_image>set_color_mode>', err)
        
            
    def allocate_memory(self):
        '''
        Allocates memory on the PC and camera
        '''
        #allocate memory
        self.width = 2048
        self.height = 1088
            
        c_width = ctypes.c_int(self.width)
        c_height = ctypes.c_int(self.height) 
        c_pixel_bits=ctypes.c_int(self.color_mode.bits_per_pixel)
        #the starting memory address for the image, will be returned
        self.ppcImgMem =  pue.c_mem_p()
        #the ID for the allocated image, will be returned
        self.pid = ctypes.c_int()
        
        #allocate memory for an image
        err = pue.is_AllocImageMem(self.cam, 
                             c_width, c_height,  c_pixel_bits, 
                             self.ppcImgMem, 
                             self.pid)
        if err != pue.IS_SUCCESS:
            raise CameraException(self.cam, 'ueye>allocate_memory>', err)
        
        # make the image memory 'active' 
        err = pue.is_SetImageMem(self.cam, self.ppcImgMem, self.pid)
        if err != pue.IS_SUCCESS:
            raise CameraException(self.cam, 'ueye>allocate_memory>', err)
        #create an array in python to which to copy the image
        self.image_data = np.zeros((self.height, self.width, self.color_mode.channels), dtype=self.color_mode.dtype)
        
    def capture(self):
        '''
        Takes an image from the camera and places it in the computer memory
        '''
        err = pue.is_FreezeVideo (self.cam, pue.IS_WAIT)  #IS_DONT_WAIT  = 0x0000, or IS_GET_LIVE = 0x8000
        if err != pue.IS_SUCCESS:
            raise CameraException(self.cam, 'ueye>capture>', err, False)
        err = pue.is_CopyImageMem (self.cam, self.ppcImgMem, self.pid, self.image_data.ctypes.data)
        if err != pue.IS_SUCCESS:
            raise CameraException(self.cam, 'ueye>capture>', err, False)
    
    def save_image(self, path, take_snapshot = True):
        if take_snapshot:
            self.capture()
        imsave(path, self.image_data)
        
    #
    # CAMERA AND IMAGE CONFIGURATION FUNCTIONS
    #
    
    def set_gain(self, master, red, green, blue):
        err = pue.is_SetHardwareGain(self.cam, master, red, green, blue)
        if err != pue.IS_SUCCESS:
            raise CameraException(self.cam, 'ueye>set_gain>', err, False)
            
    
    
    
class ColorMode:
    _modes = {'mono8' : pue.IS_CM_MONO8,
              'mono10': pue.IS_CM_MONO10,
              'mono12': pue.IS_CM_MONO12,
              'mono16': pue.IS_CM_MONO16,
              
              'raw8'  : pue.IS_CM_SENSOR_RAW8,
              'raw10' : pue.IS_CM_SENSOR_RAW10,
              'raw12' : pue.IS_CM_SENSOR_RAW12,
              'raw16' : pue.IS_CM_SENSOR_RAW16,
              
              'rgb8'  : pue.IS_CM_RGB8_PACKED,
              'rgba8' : pue.IS_CM_RGBA8_PACKED,
              'rgby8' : pue.IS_CM_RGBY8_PACKED,
              'rgb10' : pue.IS_CM_RGB10_PACKED,
              
              'bgr8'  : pue.IS_CM_BGR8_PACKED,
              'bgr10' : pue.IS_CM_BGR10_PACKED,
              'bgra8' : pue.IS_CM_BGRA8_PACKED,
              'bgry8' : pue.IS_CM_BGRY8_PACKED
              }
              
    def __init__(self, mode):
        self.mode = mode
        self.code = ColorMode._modes[mode]
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
        
if __name__ == '__main__':
    try:
        cam = ueye()
        cam.capture()
        plt.imshow(cam.image_data[:,:,:])
        #cam.save_image("C:\\Users\\Engineer\\Documents\\Alex\\test\\img.png")
        cam.close()
    except CameraException as ce:
        print(ce)
    '''
    finally:
        print('closing camera: ', pue.is_ExitCamera(pue.HIDS(0)))
    '''    