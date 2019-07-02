error_codes = '''#define IS_NO_SUCCESS                        -1   // function call failed
                #define IS_SUCCESS                            0   // function call succeeded
                #define IS_INVALID_CAMERA_HANDLE              1   // camera handle is not valid or zero
                #define IS_INVALID_HANDLE                     1   // a handle other than the camera handle is invalid
                
                #define IS_IO_REQUEST_FAILED                  2   // an io request to the driver failed
                #define IS_CANT_OPEN_DEVICE                   3   // returned by is_InitCamera
                #define IS_CANT_CLOSE_DEVICE                  4
                #define IS_CANT_SETUP_MEMORY                  5
                #define IS_NO_HWND_FOR_ERROR_REPORT           6
                #define IS_ERROR_MESSAGE_NOT_CREATED          7
                #define IS_ERROR_STRING_NOT_FOUND             8
                #define IS_HOOK_NOT_CREATED                   9
                #define IS_TIMER_NOT_CREATED                 10
                #define IS_CANT_OPEN_REGISTRY                11
                #define IS_CANT_READ_REGISTRY                12
                #define IS_CANT_VALIDATE_BOARD               13
                #define IS_CANT_GIVE_BOARD_ACCESS            14
                #define IS_NO_IMAGE_MEM_ALLOCATED            15
                #define IS_CANT_CLEANUP_MEMORY               16
                #define IS_CANT_COMMUNICATE_WITH_DRIVER      17
                #define IS_FUNCTION_NOT_SUPPORTED_YET        18
                #define IS_OPERATING_SYSTEM_NOT_SUPPORTED    19
                
                #define IS_INVALID_VIDEO_IN                  20
                #define IS_INVALID_IMG_SIZE                  21
                #define IS_INVALID_ADDRESS                   22
                #define IS_INVALID_VIDEO_MODE                23
                #define IS_INVALID_AGC_MODE                  24
                #define IS_INVALID_GAMMA_MODE                25
                #define IS_INVALID_SYNC_LEVEL                26
                #define IS_INVALID_CBARS_MODE                27
                #define IS_INVALID_COLOR_MODE                28
                #define IS_INVALID_SCALE_FACTOR              29
                #define IS_INVALID_IMAGE_SIZE                30
                #define IS_INVALID_IMAGE_POS                 31
                #define IS_INVALID_CAPTURE_MODE              32
                #define IS_INVALID_RISC_PROGRAM              33
                #define IS_INVALID_BRIGHTNESS                34
                #define IS_INVALID_CONTRAST                  35
                #define IS_INVALID_SATURATION_U              36
                #define IS_INVALID_SATURATION_V              37
                #define IS_INVALID_HUE                       38
                #define IS_INVALID_HOR_FILTER_STEP           39
                #define IS_INVALID_VERT_FILTER_STEP          40
                #define IS_INVALID_EEPROM_READ_ADDRESS       41
                #define IS_INVALID_EEPROM_WRITE_ADDRESS      42
                #define IS_INVALID_EEPROM_READ_LENGTH        43
                #define IS_INVALID_EEPROM_WRITE_LENGTH       44
                #define IS_INVALID_BOARD_INFO_POINTER        45
                #define IS_INVALID_DISPLAY_MODE              46
                #define IS_INVALID_ERR_REP_MODE              47
                #define IS_INVALID_BITS_PIXEL                48
                #define IS_INVALID_MEMORY_POINTER            49
                
                #define IS_FILE_WRITE_OPEN_ERROR             50
                #define IS_FILE_READ_OPEN_ERROR              51
                #define IS_FILE_READ_INVALID_BMP_ID          52
                #define IS_FILE_READ_INVALID_BMP_SIZE        53
                #define IS_FILE_READ_INVALID_BIT_COUNT       54
                #define IS_WRONG_KERNEL_VERSION              55
                
                #define IS_RISC_INVALID_XLENGTH              60
                #define IS_RISC_INVALID_YLENGTH              61
                #define IS_RISC_EXCEED_IMG_SIZE              62
                
                // DirectDraw Mode errors
                #define IS_DD_MAIN_FAILED                    70
                #define IS_DD_PRIMSURFACE_FAILED             71
                #define IS_DD_SCRN_SIZE_NOT_SUPPORTED        72
                #define IS_DD_CLIPPER_FAILED                 73
                #define IS_DD_CLIPPER_HWND_FAILED            74
                #define IS_DD_CLIPPER_CONNECT_FAILED         75
                #define IS_DD_BACKSURFACE_FAILED             76
                #define IS_DD_BACKSURFACE_IN_SYSMEM          77
                #define IS_DD_MDL_MALLOC_ERR                 78
                #define IS_DD_MDL_SIZE_ERR                   79
                #define IS_DD_CLIP_NO_CHANGE                 80
                #define IS_DD_PRIMMEM_NULL                   81
                #define IS_DD_BACKMEM_NULL                   82
                #define IS_DD_BACKOVLMEM_NULL                83
                #define IS_DD_OVERLAYSURFACE_FAILED          84
                #define IS_DD_OVERLAYSURFACE_IN_SYSMEM       85
                #define IS_DD_OVERLAY_NOT_ALLOWED            86
                #define IS_DD_OVERLAY_COLKEY_ERR             87
                #define IS_DD_OVERLAY_NOT_ENABLED            88
                #define IS_DD_GET_DC_ERROR                   89
                #define IS_DD_DDRAW_DLL_NOT_LOADED           90
                #define IS_DD_THREAD_NOT_CREATED             91
                #define IS_DD_CANT_GET_CAPS                  92
                #define IS_DD_NO_OVERLAYSURFACE              93
                #define IS_DD_NO_OVERLAYSTRETCH              94
                #define IS_DD_CANT_CREATE_OVERLAYSURFACE     95
                #define IS_DD_CANT_UPDATE_OVERLAYSURFACE     96
                #define IS_DD_INVALID_STRETCH                97
                
                #define IS_EV_INVALID_EVENT_NUMBER          100
                #define IS_INVALID_MODE                     101
                #define IS_CANT_FIND_FALCHOOK               102
                #define IS_CANT_FIND_HOOK                   102
                #define IS_CANT_GET_HOOK_PROC_ADDR          103
                #define IS_CANT_CHAIN_HOOK_PROC             104
                #define IS_CANT_SETUP_WND_PROC              105
                #define IS_HWND_NULL                        106
                #define IS_INVALID_UPDATE_MODE              107
                #define IS_NO_ACTIVE_IMG_MEM                108
                #define IS_CANT_INIT_EVENT                  109
                #define IS_FUNC_NOT_AVAIL_IN_OS             110
                #define IS_CAMERA_NOT_CONNECTED             111
                #define IS_SEQUENCE_LIST_EMPTY              112
                #define IS_CANT_ADD_TO_SEQUENCE             113
                #define IS_LOW_OF_SEQUENCE_RISC_MEM         114
                #define IS_IMGMEM2FREE_USED_IN_SEQ          115
                #define IS_IMGMEM_NOT_IN_SEQUENCE_LIST      116
                #define IS_SEQUENCE_BUF_ALREADY_LOCKED      117
                #define IS_INVALID_DEVICE_ID                118
                #define IS_INVALID_BOARD_ID                 119
                #define IS_ALL_DEVICES_BUSY                 120
                #define IS_HOOK_BUSY                        121
                #define IS_TIMED_OUT                        122
                #define IS_NULL_POINTER                     123
                #define IS_WRONG_HOOK_VERSION               124
                #define IS_INVALID_PARAMETER                125   // a parameter specified was invalid
                #define IS_NOT_ALLOWED                      126
                #define IS_OUT_OF_MEMORY                    127
                #define IS_INVALID_WHILE_LIVE               128
                #define IS_ACCESS_VIOLATION                 129   // an internal exception occurred
                #define IS_UNKNOWN_ROP_EFFECT               130
                #define IS_INVALID_RENDER_MODE              131
                #define IS_INVALID_THREAD_CONTEXT           132
                #define IS_NO_HARDWARE_INSTALLED            133
                #define IS_INVALID_WATCHDOG_TIME            134
                #define IS_INVALID_WATCHDOG_MODE            135
                #define IS_INVALID_PASSTHROUGH_IN           136
                #define IS_ERROR_SETTING_PASSTHROUGH_IN     137
                #define IS_FAILURE_ON_SETTING_WATCHDOG      138
                #define IS_NO_USB20                         139   // the usb port doesnt support usb 2.0
                #define IS_CAPTURE_RUNNING                  140   // there is already a capture running
                
                #define IS_MEMORY_BOARD_ACTIVATED           141   // operation could not execute while mboard is enabled
                #define IS_MEMORY_BOARD_DEACTIVATED         142   // operation could not execute while mboard is disabled
                #define IS_NO_MEMORY_BOARD_CONNECTED        143   // no memory board connected
                #define IS_TOO_LESS_MEMORY                  144   // image size is above memory capacity
                #define IS_IMAGE_NOT_PRESENT                145   // requested image is no longer present in the camera
                #define IS_MEMORY_MODE_RUNNING              146
                #define IS_MEMORYBOARD_DISABLED             147
                
                #define IS_TRIGGER_ACTIVATED                148   // operation could not execute while trigger is enabled
                #define IS_WRONG_KEY                        150
                #define IS_CRC_ERROR                        151
                #define IS_NOT_YET_RELEASED                 152   // this feature is not available yet
                #define IS_NOT_CALIBRATED                   153   // the camera is not calibrated
                #define IS_WAITING_FOR_KERNEL               154   // a request to the kernel exceeded
                #define IS_NOT_SUPPORTED                    155   // operation mode is not supported
                #define IS_TRIGGER_NOT_ACTIVATED            156   // operation could not execute while trigger is disabled
                #define IS_OPERATION_ABORTED                157
                #define IS_BAD_STRUCTURE_SIZE               158
                #define IS_INVALID_BUFFER_SIZE              159
                #define IS_INVALID_PIXEL_CLOCK              160
                #define IS_INVALID_EXPOSURE_TIME            161
                #define IS_AUTO_EXPOSURE_RUNNING            162
                #define IS_CANNOT_CREATE_BB_SURF            163   // error creating backbuffer surface  
                #define IS_CANNOT_CREATE_BB_MIX             164   // backbuffer mixer surfaces can not be created
                #define IS_BB_OVLMEM_NULL                   165   // backbuffer overlay mem could not be locked  
                #define IS_CANNOT_CREATE_BB_OVL             166   // backbuffer overlay mem could not be created  
                #define IS_NOT_SUPP_IN_OVL_SURF_MODE        167   // function not supported in overlay surface mode  
                #define IS_INVALID_SURFACE                  168   // surface invalid
                #define IS_SURFACE_LOST                     169   // surface has been lost  
                #define IS_RELEASE_BB_OVL_DC                170   // error releasing backbuffer overlay DC  
                #define IS_BB_TIMER_NOT_CREATED             171   // backbuffer timer could not be created  
                #define IS_BB_OVL_NOT_EN                    172   // backbuffer overlay has not been enabled  
                #define IS_ONLY_IN_BB_MODE                  173   // only possible in backbuffer mode 
                #define IS_INVALID_COLOR_FORMAT             174   // invalid color format
                #define IS_INVALID_WB_BINNING_MODE          175   // invalid binning mode for AWB 
                #define IS_INVALID_I2C_DEVICE_ADDRESS       176   // invalid I2C device address
                #define IS_COULD_NOT_CONVERT                177   // current image couldn't be converted
                #define IS_TRANSFER_ERROR                   178   // transfer failed
                #define IS_PARAMETER_SET_NOT_PRESENT        179   // the parameter set is not present
                #define IS_INVALID_CAMERA_TYPE              180   // the camera type in the ini file doesn't match
                #define IS_INVALID_HOST_IP_HIBYTE           181   // HIBYTE of host address is invalid
                #define IS_CM_NOT_SUPP_IN_CURR_DISPLAYMODE  182   // color mode is not supported in the current display mode
                #define IS_NO_IR_FILTER                     183
                #define IS_STARTER_FW_UPLOAD_NEEDED         184   // device starter firmware is not compatible    
                
                #define IS_DR_LIBRARY_NOT_FOUND                     185   // the DirectRender library could not be found
                #define IS_DR_DEVICE_OUT_OF_MEMORY                  186   // insufficient graphics adapter video memory
                #define IS_DR_CANNOT_CREATE_SURFACE                 187   // the image or overlay surface could not be created
                #define IS_DR_CANNOT_CREATE_VERTEX_BUFFER           188   // the vertex buffer could not be created
                #define IS_DR_CANNOT_CREATE_TEXTURE                 189   // the texture could not be created  
                #define IS_DR_CANNOT_LOCK_OVERLAY_SURFACE           190   // the overlay surface could not be locked
                #define IS_DR_CANNOT_UNLOCK_OVERLAY_SURFACE         191   // the overlay surface could not be unlocked
                #define IS_DR_CANNOT_GET_OVERLAY_DC                 192   // cannot get the overlay surface DC 
                #define IS_DR_CANNOT_RELEASE_OVERLAY_DC             193   // cannot release the overlay surface DC
                #define IS_DR_DEVICE_CAPS_INSUFFICIENT              194   // insufficient graphics adapter capabilities
                #define IS_INCOMPATIBLE_SETTING                     195   // Operation is not possible because of another incompatible setting
                #define IS_DR_NOT_ALLOWED_WHILE_DC_IS_ACTIVE        196   // user App still has DC handle.
                #define IS_DEVICE_ALREADY_PAIRED                    197   // The device is already paired
                #define IS_SUBNETMASK_MISMATCH                      198   // The subnetmasks of the device and the adapter differ
                #define IS_SUBNET_MISMATCH                          199   // The subnets of the device and the adapter differ
                #define IS_INVALID_IP_CONFIGURATION                 200   // The IP configuation of the device is invalid
                #define IS_DEVICE_NOT_COMPATIBLE                    201   // The device is incompatible to the driver
                #define IS_NETWORK_FRAME_SIZE_INCOMPATIBLE          202   // The frame size settings of the device and the network adapter are incompatible
                #define IS_NETWORK_CONFIGURATION_INVALID            203   // The network adapter configuration is invalid
                #define IS_ERROR_CPU_IDLE_STATES_CONFIGURATION      204   // The setting of the CPU idle state configuration failed
                #define IS_DEVICE_BUSY                              205   // The device is busy. The operation must be executed again later.
                #define IS_SENSOR_INITIALIZATION_FAILED             206   // The sensor initialization failed'''

color_modes = '''/*! \brief Raw sensor data, occupies 8 bits */
                #define IS_CM_SENSOR_RAW8           11
                
                /*! \brief Raw sensor data, occupies 16 bits */
                #define IS_CM_SENSOR_RAW10          33
                
                /*! \brief Raw sensor data, occupies 16 bits */
                #define IS_CM_SENSOR_RAW12          27
                
                /*! \brief Raw sensor data, occupies 16 bits */
                #define IS_CM_SENSOR_RAW16          29
                
                /*! \brief Mono, occupies 8 bits */
                #define IS_CM_MONO8                 6
                
                /*! \brief Mono, occupies 16 bits */
                #define IS_CM_MONO10                34
                
                /*! \brief Mono, occupies 16 bits */
                #define IS_CM_MONO12                26
                
                /*! \brief Mono, occupies 16 bits */
                #define IS_CM_MONO16                28
                
                /*! \brief BGR (5 5 5 1), 1 bit not used, occupies 16 bits */
                #define IS_CM_BGR5_PACKED           (3  | IS_CM_ORDER_BGR)
                
                /*! \brief BGR (5 6 5), occupies 16 bits */
                #define IS_CM_BGR565_PACKED         (2  | IS_CM_ORDER_BGR)
                
                /*! \brief BGR and RGB (8 8 8), occupies 24 bits */
                #define IS_CM_RGB8_PACKED           (1  | IS_CM_ORDER_RGB)
                #define IS_CM_BGR8_PACKED           (1  | IS_CM_ORDER_BGR)
                
                /*! \brief BGRA and RGBA (8 8 8 8), alpha not used, occupies 32 bits */
                #define IS_CM_RGBA8_PACKED          (0  | IS_CM_ORDER_RGB)
                #define IS_CM_BGRA8_PACKED          (0  | IS_CM_ORDER_BGR)
                
                /*! \brief BGRY and RGBY (8 8 8 8), occupies 32 bits */
                #define IS_CM_RGBY8_PACKED          (24 | IS_CM_ORDER_RGB)
                #define IS_CM_BGRY8_PACKED          (24 | IS_CM_ORDER_BGR)
                
                /*! \brief BGR and RGB (10 10 10 2), 2 bits not used, occupies 32 bits, debayering is done from 12 bit raw */ 
                #define IS_CM_RGB10_PACKED          (25 | IS_CM_ORDER_RGB)
                #define IS_CM_BGR10_PACKED          (25 | IS_CM_ORDER_BGR)
                
                /*! \brief BGR and RGB (10(16) 10(16) 10(16)), 6 MSB bits not used respectively, occupies 48 bits */
                #define IS_CM_RGB10_UNPACKED        (35 | IS_CM_ORDER_RGB)
                #define IS_CM_BGR10_UNPACKED        (35 | IS_CM_ORDER_BGR)
                
                /*! \brief BGR and RGB (12(16) 12(16) 12(16)), 4 MSB bits not used respectively, occupies 48 bits */
                #define IS_CM_RGB12_UNPACKED        (30 | IS_CM_ORDER_RGB)
                #define IS_CM_BGR12_UNPACKED        (30 | IS_CM_ORDER_BGR)
                
                /*! \brief BGRA and RGBA (12(16) 12(16) 12(16) 16), 4 MSB bits not used respectively, alpha not used, occupies 64 bits */
                #define IS_CM_RGBA12_UNPACKED       (31 | IS_CM_ORDER_RGB)
                #define IS_CM_BGRA12_UNPACKED       (31 | IS_CM_ORDER_BGR)
                
                #define IS_CM_JPEG                  32
                
                /*! \brief YUV422 (8 8), occupies 16 bits */
                #define IS_CM_UYVY_PACKED           12
                #define IS_CM_UYVY_MONO_PACKED      13
                #define IS_CM_UYVY_BAYER_PACKED     14
                
                /*! \brief YCbCr422 (8 8), occupies 16 bits */
                #define IS_CM_CBYCRY_PACKED         23
                
                /*! \brief RGB planar (8 8 8), occupies 24 bits */
                #define IS_CM_RGB8_PLANAR           (1 | IS_CM_ORDER_RGB | IS_CM_FORMAT_PLANAR)
                
                
                #define IS_CM_ALL_POSSIBLE          0xFFFF
                #define IS_CM_MODE_MASK             0x007F
                
                '''

display_modes = '''
                #define IS_GET_DISPLAY_MODE                 0x8000

                #define IS_SET_DM_DIB                       1
                #define IS_SET_DM_DIRECT3D                  4
                #define IS_SET_DM_OPENGL                    8
                
                #define IS_SET_DM_MONO                      0x800
                #define IS_SET_DM_BAYER                     0x1000
                #define IS_SET_DM_YCBCR                     0x4000
                '''

image_file_types = '''
                #define IS_IMG_BMP                          0
                #define IS_IMG_JPG                          1
                #define IS_IMG_PNG                          2
                #define IS_IMG_RAW                          4
                #define IS_IMG_TIF                          8
                '''
gamma_modes = '''
                #define IS_GET_HW_GAMMA                     0x8000
                #define IS_GET_HW_SUPPORTED_GAMMA           0x8001
                #define IS_SET_HW_GAMMA_OFF                 0x0000
                #define IS_SET_HW_GAMMA_ON                  0x0001
                '''

gain_modes = '''
                #define IS_GET_MASTER_GAIN                  0x8000
                #define IS_GET_RED_GAIN                     0x8001
                #define IS_GET_GREEN_GAIN                   0x8002
                #define IS_GET_BLUE_GAIN                    0x8003
                #define IS_GET_DEFAULT_MASTER               0x8004
                #define IS_GET_DEFAULT_RED                  0x8005
                #define IS_GET_DEFAULT_GREEN                0x8006
                #define IS_GET_DEFAULT_BLUE                 0x8007
                #define IS_GET_GAINBOOST                    0x8008
                #define IS_SET_GAINBOOST_ON                 0x0001
                #define IS_SET_GAINBOOST_OFF                0x0000
                #define IS_GET_SUPPORTED_GAINBOOST          0x0002
                #define IS_MIN_GAIN                         0
                #define IS_MAX_GAIN                         100
                '''

from re import split

def get_codes(c_defines):
    lines = split('\n', c_defines)
    codes_py = {}
    for line in lines:
        temp = split('#define', line)
        if len(temp) > 1:
            temp2 = temp[1].split()
            try:
                if r'(' in temp2[1]:
                    codes_py[temp2[0]] = int(split('\(', temp2[1])[1])
                else:
                    codes_py[temp2[0]] = int(temp2[1])
            except ValueError:
                codes_py[temp2[0]] = int(temp2[1], 0)
    return codes_py
    
def invert_dict(dictionary):
    r_dict = {}
    for k in dictionary.keys():
        r_dict[dictionary[k]] = k
    return r_dict
