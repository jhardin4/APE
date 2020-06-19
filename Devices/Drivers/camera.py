import cv2
import numpy as np 
from pyueye import ueye
from .ueye_codes import get_codes, invert_dict, error_codes
import threading
import time

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
        err = ueye.is_ExitCamera(self.camera)
        if err == ueye.IS_SUCCESS:
            self.status = 'closed'
        else:
            self.status = 'did not close'

    def __str__(self):
        return self.message + ', ' + self.ueye_error

class UEye(object):
    def __init__(self, cam_id, name):
    
        self._cam = ueye.HIDS(cam_id)
        self._cam_name = name
        self._sInfo = ueye.SENSORINFO()
        self._sFPS = ueye.DOUBLE()
        self._connect()

        # Query additional information about the sensor type used in the camera
        err = ueye.is_GetSensorInfo(self._cam, self._sInfo)
        if err != ueye.IS_SUCCESS:
            raise CameraException(self._cam, 'ueye>close>GetSensorInfo>', err)

        # Reset camera to default settings
        err = ueye.is_ResetToDefault(self._cam)
        if err != ueye.IS_SUCCESS:
            raise CameraException(self._cam, 'ueye>close>ResetToDefault>', err)
        
        # Set display mode to DIB
        err = ueye.is_SetDisplayMode(self._cam, ueye.IS_SET_DM_DIB)
        if err != ueye.IS_SUCCESS:
            raise CameraException(self._cam, 'ueye>close>SetDisplayMode>', err)
        
        # Core Camera Variables
        self._width = ueye.INT(self._sInfo.nMaxWidth.value)
        self._height = ueye.INT(self._sInfo.nMaxHeight.value)
        self._pitch = ueye.INT()
        self._ppc_img_mem = ueye.c_mem_p()
        self._mem_id = ueye.INT()
        self._nBitsPerPixel = ueye.INT()
        self._m_nColorMode = ueye.INT()
        self._bytes_per_pixel = ueye.INT()
        self._video_capture = False
        self._done_saving = True

        # Allicate memory for frames
        self._allocate_memory()

        # Start collection of frames
        self.start_video_capture()

        # Get frames per second
        err = ueye.is_GetFramesPerSecond(self._cam, self._sFPS)
        if err != ueye.IS_SUCCESS:
            raise CameraException(self._cam, 'ueye>close>GetFramesPerSecond>', err)

        # Start new thread to save frame
        threading.Thread(target = self._update).start()
    
    def _update(self):
        self.frame = self.get_video_frame()

    def close(self):
        # Wait to make sure video file is saved completely
        while not self._done_saving:
            pass
        self._deallocate_memory()
        err = ueye.is_ExitCamera(self._cam)
        if err != ueye.IS_SUCCESS:
            raise CameraException(self._cam, 'ueye>close>', err)

    def _connect(self):
        err = ueye.is_InitCamera(self._cam, None)
        if err != ueye.IS_SUCCESS:
            err = ueye.is_EnableAutoExit(self._cam, 1)
        if err != ueye.IS_SUCCESS:
            raise CameraException(self._cam, 'ueye>_connect>', err)

    def start_feed(self):
        self.feed_live = True
        threading.Thread(target = self._feed_loop).start()

    def stop_feed(self):
        self.feed_live = False

    def start_record(self, path):
        while not self._done_saving:
            pass
        self.record_live = True
        self._done_saving = False
        threading.Thread(target = self._record_loop, args=(path,)).start()

    def stop_record(self):
        self.record_live = False

    def _record_loop(self,path):
        videoFrames = []
        frametime = []
        while self.record_live:
            startTime = time.time()
            videoFrames.append(np.copy(self.frame[:,:,:3]))
            frametime.append(time.time()-startTime)

        framerate = round(1/np.mean(frametime))
        out = cv2.VideoWriter(path, 0, int(framerate), (int(self._width),int(self._height)))
        for frame in videoFrames:
            out.write(frame)
        out.release()
        self._done_saving = True

    def _feed_loop(self):
        #https://stackoverflow.com/questions/27006462/opencv-imshow-window-cannot-be-reused-when-called-within-a-thread
        while self.feed_live:
            resize = self._resize_keep_aspect(self.frame,width=640)
            cv2.imshow(self._cam_name, resize)
            cv2.waitKey(1)

    def _resize_keep_aspect(self,image, width=None, height=None):
        (h, w) = image.shape[:2]

        if width is None and height is None:
            return image
        if width is None:
            r = height / float(h)
            dim = (int(w * r), height)
        else:
            r = width / float(w)
            dim = (width, int(h * r))
        return cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

    def start_video_capture(self):
        # Activates the camera's live video mode (free run mode)
        err = ueye.is_CaptureVideo(self._cam, ueye.IS_WAIT)
        if err != ueye.IS_SUCCESS:
            raise CameraException(self._cam, 'ueye>video_capture>', err, False)
        
        err = ueye.is_InquireImageMem(
            self._cam,
            self._ppc_img_mem,
            self._mem_id,
            self._width,
            self._height,
            self._nBitsPerPixel,
            self._pitch,
        )
        if err != ueye.IS_SUCCESS:
            raise CameraException(self._cam, 'ueye>video_capture>', err, False)
        self._video_capture = True

    def save_image(self, path):
        if path.split('.')[-1] == 'png':
            cv2.imwrite(path, self.frame[:,:,:3],[cv2.IMWRITE_PNG_COMPRESSION,0])
        elif path.split('.')[-1] == 'jpeg':
            cv2.imwrite(path, self.frame[:,:,:3],[cv2.IMWRITE_JPEG_QUALITY,100])
        else:
            raise CameraException(self._cam, 'ueye>save_image>image type not supported')

    def get_video_frame(self):
        array = ueye.get_data(
            self._ppc_img_mem,
            self._width,
            self._height,
            self._nBitsPerPixel,
            self._pitch,
            copy=False,
        )
        frame = np.reshape(
            array, (int(self._height), int(self._width), int(self._bytes_per_pixel))
        )
        return frame

    def auto_configure(self, auto_reference=70):
        ueye.is_SetAutoParameter(self._cam, ueye.IS_SET_AUTO_WB_ONCE,ueye.DOUBLE(1),ueye.DOUBLE(0))
        ueye.is_SetAutoParameter(self._cam, ueye.IS_SET_AUTO_BRIGHTNESS_ONCE,ueye.DOUBLE(1),ueye.DOUBLE(0))
        ueye.is_SetAutoParameter(self._cam,ueye.IS_SET_AUTO_REFERENCE, ueye.DOUBLE(auto_reference), ueye.DOUBLE(0))
        ueye.is_SetAutoParameter(self._cam, ueye.IS_SET_ENABLE_AUTO_WHITEBALANCE,ueye.DOUBLE(1),ueye.DOUBLE(0))
        ueye.is_SetAutoParameter(self._cam, ueye.IS_SET_ENABLE_AUTO_GAIN,ueye.DOUBLE(1),ueye.DOUBLE(0))
        err= ueye.is_SetAutoParameter(self._cam, ueye.IS_SET_ENABLE_AUTO_SHUTTER,ueye.DOUBLE(1),ueye.DOUBLE(0))
        if err != ueye.IS_SUCCESS:
            raise CameraException(self._cam, 'ueye>auto_parameters>', err)
        
        WB_status = ueye.DOUBLE(1.0)
        gain_status = ueye.DOUBLE(1.0)
        shutter_status = ueye.DOUBLE(1.0)
        while WB_status or gain_status or shutter_status:
            ueye.is_SetAutoParameter(self._cam, ueye.IS_GET_ENABLE_AUTO_WHITEBALANCE,WB_status,ueye.DOUBLE(0))
            ueye.is_SetAutoParameter(self._cam, ueye.IS_GET_ENABLE_AUTO_GAIN,gain_status,ueye.DOUBLE(0))
            ueye.is_SetAutoParameter(self._cam, ueye.IS_GET_ENABLE_AUTO_SHUTTER,shutter_status,ueye.DOUBLE(0))

    def configure(self, parameters):
        # Exposure varies by camera: 0.020ms to 69.847 for UI-3250 model (check uEye cockpit for specifics)
        # Gain (master) can be set between 0-100
        # Black level can be set between 0-255
        # Gamma can be set between 0.01 and 10

        #Set dict keys to all lower case
        parameters = dict((k.lower(),v) for k,v in parameters.items())

        if 'exposure' in parameters:
            #Doesn't do anything
            err = ueye.is_Exposure(self._cam, ueye.IS_EXPOSURE_CMD_SET_EXPOSURE, ueye.DOUBLE(parameters['exposure']), ueye.sizeof(ueye.DOUBLE(parameters['exposure'])))
            if err != ueye.IS_SUCCESS:
                raise CameraException(self._cam, 'ueye>configure>exposure>', err)
        
        if 'gain' in parameters:
            err = ueye.is_SetHardwareGain(self._cam, ueye.INT(parameters['gain']), ueye.IS_IGNORE_PARAMETER,ueye.IS_IGNORE_PARAMETER,ueye.IS_IGNORE_PARAMETER)
            if err != ueye.IS_SUCCESS:
                raise CameraException(self._cam, 'ueye>configure>gain>', err)

        if 'black_level' in parameters:
            err = ueye.is_Blacklevel(self._cam, ueye.IS_BLACKLEVEL_CMD_SET_OFFSET, ueye.INT(parameters['black_level']),ueye.sizeof(ueye.INT(parameters['black_level'])))
            if err != ueye.IS_SUCCESS:
                raise CameraException(self._cam, 'ueye>configure>black_level>', err)

        if 'gamma' in parameters:
            # Digital gamma correction
            err = ueye.is_Gamma(self._cam, ueye.IS_GAMMA_CMD_SET, ueye.INT(int(parameters['gamma']*100)),ueye.sizeof(ueye.INT(int(parameters['gamma']*100))))
            if err != ueye.IS_SUCCESS:
                raise CameraException(self._cam, 'ueye>configure>gamma>', err) 

    def load_parameters(self, path):
        # Load parameters from file
        # Taken from: https://stackoverflow.com/questions/56461431/error-loading-ueye-camera-configuration-file-with-pyueye
        pParam = ueye.wchar_p()
        pParam.value = path
        err = ueye.is_ParameterSet(self._cam, ueye.IS_PARAMETERSET_CMD_LOAD_FILE, pParam, 0)
        if err != ueye.IS_SUCCESS:
            raise CameraException(self._cam, 'ueye>load_parameters>', err)

    def save_parameters(self, path):
        # Save parameters to file
        pParam = ueye.wchar_p()
        pParam.value = path
        err = ueye.is_ParameterSet(self._cam, ueye.IS_PARAMETERSET_CMD_SAVE_FILE, pParam, 0)
        if err != ueye.IS_SUCCESS:
            raise CameraException(self._cam, 'ueye>save_parameters>', err)

    def _allocate_memory(self):
        # Allocates memory on the PC and camera

        # Set the right color mode
        if int.from_bytes(self._sInfo.nColorMode.value, byteorder='big') == ueye.IS_COLORMODE_BAYER:
            # setup the color depth to the current windows setting
            ueye.is_GetColorDepth(self._cam, self._nBitsPerPixel, self._m_nColorMode)
            self._bytes_per_pixel = self._nBitsPerPixel / 8

        elif int.from_bytes(self._sInfo.nColorMode.value, byteorder='big') == ueye.IS_COLORMODE_CBYCRY:
            # for color camera models use RGB32 mode
            self._m_nColorMode = ueye.IS_CM_BGRA8_PACKED
            self._nBitsPerPixel = ueye.INT(32)
            self._bytes_per_pixel = self._nBitsPerPixel / 8

        elif int.from_bytes(self._sInfo.nColorMode.value, byteorder='big') == ueye.IS_COLORMODE_MONOCHROME:
            # for color camera models use RGB32 mode
            self._m_nColorMode = ueye.IS_CM_MONO8
            self._nBitsPerPixel = ueye.INT(8)
            self._bytes_per_pixel = self._nBitsPerPixel / 8

        else:
            # for monochrome camera models use Y8 mode
            self._m_nColorMode = ueye.IS_CM_MONO8
            self._nBitsPerPixel = ueye.INT(8)
            self._bytes_per_pixel = self._nBitsPerPixel / 8

        # allocate memory for an image
        err = ueye.is_AllocImageMem(
            self._cam,
            self._width,
            self._height,
            self._nBitsPerPixel,
            self._ppc_img_mem,
            self._mem_id,
        )
        if err != ueye.IS_SUCCESS:
            raise CameraException(self._cam, 'ueye>_allocate_memory>', err)

        # make the image memory 'active'
        err = ueye.is_SetImageMem(self._cam, self._ppc_img_mem, self._mem_id)
        if err != ueye.IS_SUCCESS:
            raise CameraException(self._cam, 'ueye>_allocate_memory>', err)

    def _deallocate_memory(self):
        if self._ppc_img_mem is None:
            return
        # Releases an image memory that was allocated using is_AllocImageMem() and removes it from the driver management
        err = ueye.is_FreeImageMem(self._cam, self._ppc_img_mem, self._mem_id)
        if err != ueye.IS_SUCCESS:
            raise CameraException(self._cam, 'ueye>_deallocate_memory>', err)
        self._ppc_img_mem = None

if __name__ == '__main__':
    try:
        cam = UEye(cam_id=0,name='cam0')
        print("Connected to camera")
        
        cam.start_feed()
        print("Started live feed")

        cam.auto_configure()
        print("Auto configured camera")

        cam.save_parameters('auto_config.ini')
        print("Saved configuration to file")

        cam.configure({'exposure':40.0,'gain': 50, 'black_level':200, 'gamma':1.0})
        print("Manually configured the camera")

        cam.load_parameters('auto_config.ini')
        print("Loaded configuration to file")
        
        cam.start_record('video_test_1.avi')
        print("Started rec 1")
        time.sleep(5)
        cam.save_image('image_test_1.png')
        print("Took and saved image 1")
        time.sleep(5)
        cam.stop_record()
        print("Stopped rec 1")
        
        cam.start_record('video_test_2.avi')
        print("Started rec 2")
        time.sleep(5)
        cam.save_image('image_test_2.png')
        print("Took and saved image 2")
        time.sleep(5)
        cam.stop_record()
        print("Stopped rec 2")

        cam.stop_feed()
        print("Stopped live feed")

        cam.close()
        print("Dicsonnected from camera")

    except CameraException as ce:
        print(ce)