import ctypes
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.image import imsave
import os


class IDS_Camera():
    
    def __init__(self):
        self.uEyeDll = ctypes.cdll.LoadLibrary("uEye_api.dll") #include full path or copy dll into same folder as .py script
        #connect camera
        self.cam = ctypes.c_uint32(0)
        self.hWnd = ctypes.c_voidp()
        #print(self.uEyeDll.is_ExitCamera(1))
        self.msg = self.uEyeDll.is_InitCamera(ctypes.byref(self.cam), self.hWnd)
        ErrChk = self.uEyeDll.is_EnableAutoExit (self.cam, ctypes.c_uint(1))
        print(ErrChk)
        if not ~ErrChk:
            print ('Camera Not Connected')
            self.connected = False
        else:
            self.connected = True
        if self.connected:
            #color and display mode config
            #set to bitmap mode
            self.uEyeDll.is_SetDisplayMode(ctypes.c_uint32(0))
            #set colormap to 16 bit grey (probably)
            nRet = self.uEyeDll.is_SetColorMode(self.cam, ctypes.c_int(25))
            
            print(nRet)
            IS_SET_TRIGGER_SOFTWARE = ctypes.c_uint(0x1000)
            nRet = self.uEyeDll.is_SetExternalTrigger(self.cam, IS_SET_TRIGGER_SOFTWARE)
            
            #allocate memory
            width_py = 2048
            height_py = 1088
            pixels_py = 32
            
            width = ctypes.c_int(width_py) #convert python values into c++ integers
            height = ctypes.c_int(height_py) 
            bitspixel=ctypes.c_int(pixels_py)
            self.pcImgMem = ctypes.c_char_p() #create placeholder for image memory
            self.pid=ctypes.c_int()
            
            ErrChk = self.uEyeDll.is_AllocImageMem(self.cam, 
                                                   width, height,  bitspixel, 
                                                   ctypes.byref(self.pcImgMem), 
                                                   ctypes.byref(self.pid))
            
            # Get image data    
            ErrChk = self.uEyeDll.is_SetImageMem(self.cam, self.pcImgMem, self.pid)
            self.ImageData = np.ones((height_py,width_py),dtype=np.uint32)
            self.fig = plt.figure()
            self.ax = self.fig.gca()
            #self.im = self.ax.imshow(self.ImageData, animated = False)

    def close_camera(self):
        self.uEyeDll.is_ExitCamera(ctypes.byref(self.cam))

    def snapshot(self):
        if self.connected:
            ErrChk = self.uEyeDll.is_FreezeVideo (self.cam, ctypes.c_int(0x8000))  #IS_DONT_WAIT  = 0x0000, or IS_GET_LIVE = 0x8000
            ErrChk = self.uEyeDll.is_CopyImageMem (self.cam, self.pcImgMem, self.pid, self.ImageData.ctypes.data)
            self.im = self.ax.imshow(self.ImageData)
            #self.im.set_data(self.ImageData)
    
    def save_image(self, path, take_snapshot = True):
        if take_snapshot:
            self.snapshot()
        if self.connected:
            imsave(path, self.ImageData)
    
    def save_png(self, path):
        height = self.ImageData.shape[0]
        width = self.ImageData.shape[1]
        
        buf = self.ImageData.tobytes()
        
        import zlib, struct
        width_byte_4 = width * 4
        raw_data = b''.join(b'\x00' + buf[span:span + width_byte_4]
                            for span in range((height - 1) * width_byte_4, -1, -width_byte_4))
        
        def png_pack(png_tag, data):
            chunk_head = png_tag + data
            return (struct.pack("!I", len(data)) + chunk_head + 
                    struct.pack("!I", 0xFFFFFFFF & zlib.crc32(chunk_head)))
        
        png_data = b''.join([b'\x89PNG\r\n\x1a\n',
                         png_pack(b'IHDR', struct.pack('!2I5B', width, height, 8, 6, 0, 0, 0)),
                         png_pack(b'IDAT', zlib.compress(raw_data, 9)),
                         png_pack(b'IEND', b'')])
        
        with open(path, 'wb') as fd:
            fd.write(png_data)
        

if __name__ == '__main__':
    basepath = 'C:\\Users\\user\\Pictures\\Alex\\2017-10-20-IDS_Test\\'
    #cont = A3200.A3200()
    IDS = IDS_Camera()
    #for i in range(1):
    #    IDS.save_image_2(pjoin(basepath, str(i) + '.png'))
        #IDS.save_png(pjoin(basepath, str(i) + '.png'))
        #cont.linear(['X'], [10])
        #cont.linear(['X'], [-10])
    #print(IDS.cam)
    #cont.disconnect()

