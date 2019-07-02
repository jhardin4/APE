import ctypes as ct
import time
from enum import Enum
import collections
from multiprocessing import Queue, Process, Value


_AXES = ['X', 'Y', 'ZZ1', 'ZZ2', 'ZZ3', 'ZZ4', 'R', 'I', 'J']
_Z_AXES = ['ZZ1', 'ZZ2', 'ZZ3', 'ZZ4']
_AXIS_INDEX = {'Y': 0, 'YY': 1, 'X': 2, 'ZZ1': 6, 'ZZ2': 7, 'ZZ3': 8, 'ZZ4': 9}
_DEFAULT_RAPID_SPEED = {'Y': 50, 'X': 50, 'ZZ1': 20, 'ZZ2': 20, 'ZZ3': 20, 'ZZ4': 20}
_NUM_TASKS = 4

A3200_is_Open = False
A3200Lib = None
handle = None


class MotionException(Exception):
    def __init__(self, source, message, level, controller=None):
        self.source = source
        self.message = message
        self.level = level
        if controller is not None:
            bf = 100
            empty = ''
            for i in range(bf):
                empty += ' '
            errorString = ct.c_buffer(empty.encode('utf-8'))
            bufferSize = ct.c_int(bf)
            controller.A3200Lib.A3200GetLastErrorString(errorString, bufferSize)
            print(errorString.value)


class Axis_Mask(Enum):
    '''
    Meant to represent the c enums in the A3200 Library
    '''

    # All available axis masks.
    # No axes selected.
    AXISMASK_None = (0,)

    Y = ((1 << 0),)  # 1
    YY = ((1 << 1),)  # 2
    X = ((1 << 2),)  # 4
    ZZ1 = ((1 << 6),)  # 8
    ZZ2 = ((1 << 7),)  # 16
    ZZ3 = ((1 << 8),)  # 32
    ZZ4 = ((1 << 9),)  # 64
    # A      = (1 <<  7), #128

    # Maximum number of axes selected.
    AXISMASK_All = 0xFFFFFFFF

    '''
    Unimplemented axis_masks

	AXISMASK_08 = (1 <<  8), #256
	AXISMASK_09 = (1 <<  9), #512

	AXISMASK_10 = (1 << 10), #1024
	AXISMASK_11 = (1 << 11), #2048
	AXISMASK_12 = (1 << 12),
	AXISMASK_13 = (1 << 13),
	AXISMASK_14 = (1 << 14),
	AXISMASK_15 = (1 << 15),
	AXISMASK_16 = (1 << 16),
	AXISMASK_17 = (1 << 17),
	AXISMASK_18 = (1 << 18),
	AXISMASK_19 = (1 << 19),

	AXISMASK_20 = (1 << 20),
	AXISMASK_21 = (1 << 21),
	AXISMASK_22 = (1 << 22),
	AXISMASK_23 = (1 << 23),
	AXISMASK_24 = (1 << 24),
	AXISMASK_25 = (1 << 25),
	AXISMASK_26 = (1 << 26),
	AXISMASK_27 = (1 << 27),
	AXISMASK_28 = (1 << 28),
	AXISMASK_29 = (1 << 29),

	AXISMASK_30 = (1 << 30),
	AXISMASK_31 = (1 << 31),
        '''

    @classmethod
    def get_mask(cls, axes):
        '''
        Returns the sum of Axes masks for a given list of axes.
        '''
        # check if axes is iterable and not a string
        if isinstance(axes, collections.Iterable) and type(axes) is not str:
            mask = 0
            for ax in axes:
                try:
                    mask += cls[ax].value[0]
                except KeyError:
                    print("Invalid axis: {}".format(ax))
            return ct.c_ulong(mask)
        else:
            try:
                return ct.c_ulong(cls[axes].value[0])
            except KeyError:
                print("Invalid axis: {}".format(axes))
                return 0


def name_to_index(name):
    if type(name) is str:
        # return _AXIS_INDEX[name]
        # see if someone put an index in a string:
        try:
            return int(name)
        except ValueError:
            try:
                return _AXIS_INDEX[name]
            except KeyError:
                print("invalid axis")

    else:
        # assume it's a proper index
        return name


def coords_to_basic(axes, coords, move_type='linear', percision=3, min_move=0.0005):
    '''
    Take a list of coordinate values and translate to a string of aerobasic.

    Coordinated Execution may be limited to four axes due to ITAR restrictions.

    Input:
        axes: a list of the axes to make the moves on eg ['x', 'y', 'z']
        coords: list of lists of distances eg [[1, 2, 3], [2, 3, 4]]
        move_type: a list of the aerobasic movement types/commands eg 'linear' or 'cw'
        percision: the percision to which to round the move coordinates
        min_move: moves on axes smaller than this will not be included in the command
    output:
        a string containing the movement command(s)
    '''
    command = ""
    # ensure that we're dealing with a list of coordinates and not a single coord
    if not isinstance(axes, collections.Iterable) or type(axes) is str:
        axes = [axes]
        coords = [coords]
    # check to see if we're using the default linear moves
    if move_type == 'linear':
        g = ['linear' for a in axes]
    else:
        g = move_type
    for j in range(len(coords)):
        line = g
        eol = '\n'
        for i in range(len(axes)):
            # check to make sure it is a valid axis
            if axes[i] in _AXES:
                if abs(coords[j][i]) > min_move:  # cut out axes which are nearly zero
                    line += "{a} {v:0.{p}f} ".format(
                        a=axes[i], v=coords[j][i], p=percision
                    )
            else:
                if 'F' or 'f' in axes[i]:
                    eol = "F{v:0.{p}f}".format(coords[j][i], p=percision) + eol
        line += eol
        command += line
    return command


def dict_coords_to_basic(coords, percision=3, min_move=0.0005):
    '''
    Take a list of dictionary coordinate values and translate to a string of aerobasic.

    This allows for arbitrary specification of coordinates at each move, nessecary
        if using more than 4 axes.

    Input:
        coords: list of dict items eg [{'move_type': 'linear', 'X': 1, 'Y': 2, 'F': 3}]
        percision: the percision to which to round the move coordinates
        min_move: moves on axes smaller than this will not be included in the command
    output:
        a string containing the movement command(s)
    '''
    command = ""
    if isinstance(coords, collections.Iterable) and type(coords) is not dict:
        for coord in coords:
            if 'move_type' in coord.keys():
                line = coord['move_type']
            else:
                line = "Linear "
            eol = '\n'
            for axis, value in coord.items():
                if axis in _AXES:
                    if abs(value) > min_move:  # cut out axes which are nearly zero
                        line += "{a} {v:0.{p}f} ".format(a=axis, v=value, p=percision)
                else:
                    if 'F' or 'f' in axis:
                        eol = "F{v:0.{p}f}".format(v=value, p=percision) + eol
            line += eol
            command += line
    else:
        if 'move_type' in coord.keys():
            line = coord['move_type']
        else:
            line = "Linear "
        eol = '\n'
        for axis, value in coord.items():
            line = "Linear "
            eol = '\n'
            for axis, value in coord.items():
                if axis in _AXES:
                    if abs(value) > min_move:  # cut out axes which are nearly zero
                        line += "{a} {v:0.{p}f} ".format(a=axis, v=value, p=percision)
                else:
                    if 'F' or 'f' in axis:
                        eol = "F{v:0.{p}f}".format(v=value, p=percision) + eol
            line += eol
            command += line
        line += eol
        command += line
    return command


def sort_axes(axes, distances):
    '''
    Sorts axes and distances in order of the axis indicies specified in _AXIS_INDEX.

    Input:
        axes: list of axes in string or int(index) format
        distances: the distances you wish to travel along axes, ordered respective of
            axes.
    Output: (sorted_axes, sorted_distances)
        sorted_axes: list of the axis strings or indicies sorted as specified
        sorted_distances: list of distances sorted respective of axes
    '''
    sortedaxes = []
    sorteddistances = []
    inserted = False
    if type(axes[0]) is str:
        for a, d in zip(axes, distances):
            if len(sortedaxes) > 0:
                inserted = False
                # scan through the list and figure out where to stick the latest axis
                for i in range(len(sortedaxes)):
                    if _AXIS_INDEX[a] < _AXIS_INDEX[sortedaxes[i]] and not inserted:
                        sortedaxes.insert(i, a)
                        sorteddistances.insert(i, d)
                        inserted = True
                if not inserted:
                    # add element to the end
                    sortedaxes.append(a)
                    sorteddistances.append(d)
            else:
                # for first element
                sortedaxes.append(a)
                sorteddistances.append(d)
    else:
        # assume axes are specified by index number
        for a, d in zip(axes, distances):
            if len(sortedaxes) > 0:
                inserted = False
                # scan through the list and figure out where to stick the latest axis
                for i in range(len(sortedaxes)):
                    if a < sortedaxes[i] and not inserted:
                        sortedaxes.insert(i, a)
                        sorteddistances.insert(i, d)
                        inserted = True
                if not inserted:
                    # add element to the end
                    sortedaxes.append(a)
                    sorteddistances.append(d)
            else:
                # for first element
                sortedaxes.append(a)
                sorteddistances.append(d)
    return sortedaxes, sorteddistances


class A3200:
    def __init__(self, handle=None, default_task=1, debug=False):
        if handle is None:
            self.A3200_is_Open = False
            self.handle, self.A3200Lib = self.connect()
            if self.handle is not None:
                self.A3200_is_open = True
            else:
                self.A3200_is_open = False
        else:
            # Get the library
            self.A3200Lib = ct.WinDLL(
                r"C:\Program Files (x86)\Aerotech\A3200\CLibrary\Bin64\A3200C64.dll"
            )
            # test connection

            # set the handle
            self.handle = handle
            self.A3200_is_open = True
        # set this so that the other functions can use it as a default.
        self.task = default_task
        # self.motion_mode = 'incremental'
        # self.incremental()
        self.debug = debug
        self.default_speed = 10
        self.queue_status = [Value('i', 0) for j in range(_NUM_TASKS)]

    def enable(self, axes, task=-1):
        '''
        Enable the axes specified in axes.

        task- taskID
        axes- axismask, array or string of axes

        returns true (1) if successful.
        '''
        if self.A3200_is_Open:
            # sum the axes
            ax_mask = Axis_Mask.get_mask(axes)
            if task < 0:
                return self.A3200Lib.A3200MotionEnable(self.handle, self.task, ax_mask)
            else:
                return self.A3200Lib.A3200MotionEnable(self.handle, task, ax_mask)

    def disable(self, axes, task=-1):
        '''
        disable the axes specified in axes.

        task- taskID
        axes- axismask, array or string of axes

        returns true (1) if successful.
        '''
        if self.A3200_is_Open:
            # sum the axes
            ax_mask = Axis_Mask.get_mask(axes)
        if task < 0:
            return self.A3200Lib.A3200MotionDisable(self.handle, self.task, ax_mask)
        else:
            return self.A3200Lib.A3200MotionDisable(self.handle, task, ax_mask)

    def home(self, axes, task=-1):
        '''
        Homes the axes specified in axes.

        task- taskID
        axes- axismask, array or string of axes

        returns true (1) if successful.
        '''
        if self.A3200_is_Open:
            # sum the axes
            ax_mask = Axis_Mask.get_mask(axes)
            if task < 0:
                return self.A3200Lib.A3200MotionHome(self.handle, self.task, ax_mask)
            else:
                return self.A3200Lib.A3200MotionHome(self.handle, task, ax_mask)

    def abort(self, axes):
        '''
        Aborts the motion on the specified axes, returns when abort starts.

        axes- axismask, array or string of axes

        returns true (1) if successful.
        '''
        if self.A3200_is_Open:
            # sum the axes
            ax_mask = Axis_Mask.get_mask(axes)
            return self.A3200Lib.A3200MotionAbort(self.handle, ax_mask)

    def rapid(self, axes, distance, speed=None, task=-1):
        '''
        Make a linear coordinated point to point motion on axes a specifed distance.

        Note: will fail (not execute) if more than four axes are specified and ITAR controls
                        are enabled.

        Input:
            axes: a list of axes or string containing one axis
            distance: the distances to move along the axes, in the same respective order
            speed: the speed each axis should move at in the same order
                    if not specified, defaults to the max speed.
            task: task to execute the move on
        Returns:
            1 if successful
        '''
        if self.A3200_is_Open:
            # need to convert distance into an array structure
            if isinstance(distance, collections.Iterable):
                # need to arrange the distances in order of the axis index
                sort_ax, sort_dist = sort_axes(axes, distance)
                d = (ct.c_double * len(sort_dist))()
                for i in range(len(sort_dist)):
                    d[i] = ct.c_double(sort_dist[i])
            else:
                d = ct.c_double(distance)
            if speed is not None:
                # same things for the speed
                if isinstance(speed, collections.Iterable):
                    # need to arrange the distances in order of the axis index
                    sort_ax, sort_dist = sort_axes(axes, speed)
                    v = (ct.c_double * len(sort_dist))()
                    for i in range(len(sort_dist)):
                        v[i] = ct.c_double(sort_dist[i])
                else:
                    v = ct.c_double(speed)
            else:
                # use default max speeds if it is not specified
                if isinstance(distance, collections.Iterable):
                    s = []
                    for a in sort_ax:
                        s.append(_DEFAULT_RAPID_SPEED[a])
                    v = (ct.c_double * len(sort_dist))()
                    for i in range(len(sort_ax)):
                        v[i] = ct.c_double(s[i])
                else:
                    v = ct.c_double(_DEFAULT_RAPID_SPEED[axes])
            # sum the axes
            ax_mask = Axis_Mask.get_mask(axes)
            if task < 0:
                return self.A3200Lib.A3200MotionRapid(
                    self.handle, self.task, ax_mask, d, v
                )
            else:
                return self.A3200Lib.A3200MotionRapid(self.handle, task, ax_mask, d, v)

    def linear(self, axes, distance, task=-1):
        '''
        Make a linear coordinated point to point motion on axes a specifed distance.

        Note: will fail (not execute) if more than four axes are specified and ITAR controls
                        are enabled.

        Input:
            axes: a list of axes or string containing one axis
            distance: the distances to move along the axes, in the same respective order
            task: task to execute the move on
        '''
        if self.A3200_is_Open:
            # need to convert distance into an array structure
            if isinstance(distance, collections.Iterable):
                # need to arrange the distances in order of the axis index
                sort_ax, sort_dist = sort_axes(axes, distance)
                d = (ct.c_double * len(sort_dist))()
                for i in range(len(sort_dist)):
                    d[i] = ct.c_double(sort_dist[i])
            else:
                d = ct.c_double(distance)
            # sum the axes
            ax_mask = Axis_Mask.get_mask(axes)
            if task < 0:
                task = self.task
            success = bool(
                self.A3200Lib.A3200MotionLinear(self.handle, task, ax_mask, d)
            )
            if not success:
                raise MotionException(
                    'A3200->linear->',
                    'Aerotech Command Fail ({})'.format(success),
                    'estop',
                )

    def linear_velocity(self, axes, distance, speed, task=-1):
        '''
        Make a linear coordinated point to point motion on axes a specifed distance.

        Note: will fail (not execute) if more than four axes are specified and ITAR controls
                        are enabled.

        Input:
            axes: a list of axes or string containing one axis
            distance: the distances to move along the axes, in the same respective order
            task: task to execute the move on
        '''
        if self.A3200_is_Open:
            # need to convert distance into an array structure
            if isinstance(distance, collections.Iterable):
                # need to arrange the distances in order of the axis index
                sort_ax, sort_dist = sort_axes(axes, distance)
                d = (ct.c_double * len(sort_dist))()
                for i in range(len(sort_dist)):
                    d[i] = ct.c_double(sort_dist[i])
            else:
                d = ct.c_double(distance)
            # sum the axes
            ax_mask = Axis_Mask.get_mask(axes)
            s = ct.c_double(speed)
            if task < 0:
                success = bool(
                    self.A3200Lib.A3200MotionLinearVelocity(
                        self.handle, self.task, ax_mask, d, s
                    )
                )
            else:
                success = bool(
                    self.A3200Lib.A3200MotionLinearVelocity(
                        self.handle, task, ax_mask, d, s
                    )
                )
            if not success:
                raise MotionException(
                    'A3200->linear_velocity->', 'Aerotech Command Fail', 'estop'
                )
            return success

    def freerun(self, axis, speed, task=-1):
        '''
        Set the axis into freerun mode at speed.

        Input:
            axis: an axis on which to operate
            speed: the speed at which to run
            task: the task to operate on, defaults to self.task
        Return:
            1 if successful
        '''
        if self.A3200_is_Open:
            axis_index = name_to_index(axis)
            f = ct.c_double(speed)
            if task < 0:
                return self.A3200Lib.A3200MotionFreeRun(
                    self.handle, self.task, axis_index, f
                )
            else:
                return self.A3200Lib.A3200MotionFreeRun(
                    self.handle, task, axis_index, f
                )

    def stop_freerun(self, axis, task=-1):
        '''
        Stops the axis which is freerunning.

        Input:
            axis: an axis on which to operate
            speed: the speed at which to run
            task: the task to operate on, defaults to self.task
        Return:
            1 if successful
        '''
        if self.A3200_is_Open:
            axis_index = name_to_index(axis)
            if task < 0:
                return self.A3200Lib.A3200MotionFreeRunStop(
                    self.handle, self.task, axis_index
                )
            else:
                return self.A3200Lib.A3200MotionFreeRunStop(
                    self.handle, task, axis_index
                )

    def absolute_move(
        self, axes, distance=None, speed=None, task=-1, block_till_done=True
    ):
        '''
        Makes a linear motion in absolute (printer) coordinates.
        Note: NOT COORDINATED, MAY NOT BLOCK *see below

        Inputs:
            Axes: list of strings or dict {'X': float(distance)}
            distance: list of values if Axes is list
            speed: float of the speed you wish ALL axes to move
            task: task to operate on or -1 for default
            *block_till_done: if true, the method will block till motion on axes is done
        *if non-blocking, the stage will move to the final target position of all the
            consecutive abs_move and inc_move commands
        '''
        # check if we have a dictionary arg
        if task < 0:
            task = self.task
        if distance is None and type(axes) is dict:
            distance = [axes[k] for k in axes.keys()]
            axes = [k for k in axes.keys()]
        # move one ax at a time
        success = True
        for ax, dist in zip(axes, distance):
            ax_mask = name_to_index(ax)
            d = ct.c_double(dist)
            if speed is None:
                speed = self.default_speed
            s = ct.c_double(speed)
            if self.debug:
                print(ax_mask, d, s)
            success = success and bool(
                self.A3200Lib.A3200MotionMoveAbs(self.handle, task, ax_mask, d, s)
            )
        if not success:
            raise MotionException(
                'A3200.absolute_move->', 'Aerotech Command Fail', 'estop', self
            )
        # block python execution till the move completes
        if block_till_done:
            for ax in axes:
                self.wait_for_move_done(ax)

    def incremental_move(
        self, axes, distance=None, speed=None, task=-1, block_till_done=True
    ):
        '''
        Makes a linear motion in absolute (printer) coordinates.
        Note: NOT COORDINATED, MAY NOT BLOCK *see below

        Inputs:
            Axes: list of strings or dict {'X': float(distance)}
            distance: list of values if Axes is list
            speed: float of the speed you wish ALL axes to move
            task: task to operate on or -1 for default
            *block_till_done: if true, the method will block till motion on axes is done

        *if non-blocking, the stage will move to the final target position of all the
            consecutive abs_move and inc_move commands
        '''
        # check if we have a dictionary arg
        if task < 0:
            task = self.task
        if distance is None and type(axes) is dict:
            distance = [axes[k] for k in axes.keys()]
            axes = [k for k in axes.keys()]
        # move one ax at a time
        success = True
        for ax, dist in zip(axes, distance):
            ax_mask = name_to_index(ax)
            d = ct.c_double(dist)
            if speed is None:
                speed = self.default_speed
            s = ct.c_double(speed)
            if self.debug:
                print(ax_mask, d, s)
            success = success and bool(
                self.A3200Lib.A3200MotionMoveInc(self.handle, task, ax_mask, d, s)
            )
        if not success:
            raise MotionException(
                'A3200.incremental_move->', 'Aerotech Command Fail', 'estop', self
            )
        # block python execution till the move completes
        if block_till_done:
            for ax in axes:
                self.wait_for_move_done(ax)

    def wait_for_move_done(self, axes, mode='move_done', timeout=-1):
        if self.A3200_is_Open:

            if 'in_position' in mode:
                wait_mode = ct.c_ulong(1)
            else:
                wait_mode = ct.c_ulong(0)
            timeout = ct.c_int(timeout)
            ax_mask = Axis_Mask.get_mask(axes)
            ret_timeout = ct.c_bool(False)
            success = self.A3200Lib.A3200MotionWaitForMotionDone(
                self.handle, ax_mask, wait_mode, timeout, ct.byref(ret_timeout)
            )

            return success, ret_timeout.value

    def cmd_exe(self, command, task=-1, ret=False):
        '''
        Execute an aerobasic command.

        Inputs:
            command: a string containing the command as it would be writen in aerobasic
            task:    the task to run the command on, defaults to self.task
            ret:     specify the return type, defaults to no return

        Returns:
            the specified return type for the command (NYI)
        '''

        if self.A3200_is_Open:
            cmd = ct.c_buffer(command.encode('utf-8'))
            # cmd = ct.wintypes.LPCSTR(command.encode('utf-8'))
            if task < 0:
                success = self.A3200Lib.A3200CommandExecute(
                    self.handle, self.task, cmd, None
                )
            else:
                success = self.A3200Lib.A3200CommandExecute(
                    self.handle, task, cmd, None
                )
            return bool(success), str(cmd.value)

    ######IO Functions ######

    def AI(self, axis, channel, task=-1):
        '''
        returns the value of analog input channel on axis

        Input:
            Channel- DWORD (int)
            axis-    axis mask string or integer index
        Output:
            (success/fail, value)
        '''
        if self.A3200_is_Open:
            if task < 0:
                task = self.task
            if self.queue_status[task].value == 1:
                raise MotionException(
                    'A3200.AI', 'AI Does not function in Queue Mode!', 'e-stop'
                )
            a = ct.c_int(name_to_index(axis))
            c = ct.c_int(channel)
            if not hasattr(self, 'AI_return'):
                self.AI_return = ct.c_double(0)
            s = self.A3200Lib.A3200IOAnalogInput(
                self.handle, task, c, a, ct.byref(self.AI_return)
            )
            if not bool(s):
                raise MotionException('A3200.AI', 'AI function Failed', 'e-stop')
            return self.AI_return.value

    def AO(self, axis, channel, value, task=-1):
        '''
        Sets the AO channel on axis to value.

        Input:
            Channel- DWORD (int)
            axis-   axis mask string or integer index
            value - float specifying the output voltage
        Output:
            returns 1 if successful
        '''
        if self.A3200_is_Open:
            a = ct.c_int(name_to_index(axis))
            c = ct.wintypes.DWORD(channel)
            v = ct.c_double(value)
            if task < 0:
                return self.A3200Lib.A3200IOAnalogOutput(
                    self.handle, self.task, c, a, v
                )
            else:
                return self.A3200Lib.A3200IOAnalogOutput(self.handle, task, c, a, v)

    def DI(self, axis, bit, task=-1):
        '''
        returns the value of the digital bit on axis

        Input:
            Channel- DWORD (int)
            axis-    axis mask string or integer index
            task: task to run the query on
        Output:
            (s, v)
            s - 1  if successful
            v - the True/False::1/0 value of the bit
        '''
        if self.A3200_is_Open:
            a = ct.c_int(name_to_index(axis))
            c = ct.wintypes.DWORD(bit)
            ret = ct.wintypes.DWORD()
            if task < 0:
                s = self.A3200Lib.A3200IODigitalInput(
                    self.handle, self.task, c, a, ct.byref(ret)
                )
            else:
                s = self.A3200Lib.A3200IODigitalInput(
                    self.handle, self.task, c, a, ct.byref(ret)
                )
            return s, bool(ret.value)

    def DO(self, axis, bit, value, task=-1):
        '''
        Sets the digital out bit on axis to value.

        Input
            Channel- DWORD (int)
            axis-    axis mask string or integer index
            value:   Boolean or int value to set the bit
        Output
            1 if successful
        '''
        if self.A3200_is_Open:
            a = ct.c_int(name_to_index(axis))
            c = ct.c_int(bit)
            if type(value) is bool:
                value = int(value)
            v = ct.c_int(value)
            if task < 0:
                return self.A3200Lib.A3200IODigitalOutput(
                    self.handle, self.task, c, a, v
                )
            else:
                return self.A3200Lib.A3200IODigitalOutput(self.handle, task, c, a, v)

    ##### Queue Functions #####

    def enable_queue_mode(self, task=-1):
        if task < 0:
            task = self.task
        if self.queue_status[task].value == 0:
            if self.A3200Lib.A3200ProgramInitializeQueue(self.handle, task):
                self.queue_status[task].value = 1
                self.queue_return = Queue()
                self.queue_process = Process(
                    target=queue_monitor,
                    args=(task, self.queue_status[task], self.queue_return),
                )
                self.queue_process.start()
                self.queue_return.put(
                    'Started Queue monitor process on task {}'.format(task)
                )
                return True

    def disable_queue_mode(self, task=-1, wait_till_empty=True):
        '''
        Disable Queue Mode on task.

        Inputs:
                Task: Default if -1
                Wait_till_empty: Waits till the queue is empty to exit.
        '''
        if task < 0:
            task = self.task
        if self.queue_status[task].value > 0:
            time.sleep(1)
            self.set_task_variable(50, [0])
            if self.debug:
                print(
                    'start',
                    self.get_queue_depth(),
                    'status',
                    self.queue_status[task].value,
                )
            #
            if wait_till_empty:
                while self.get_queue_depth() > 1:
                    if self.debug:
                        print(
                            'Waiting for the Queue to Empty, {} items left.'.format(
                                self.get_queue_depth()
                            )
                        )
                    time.sleep(0.25)
            self.queue_status[task].value = 0
            time.sleep(1)
            self.set_task_variable(50, [0])
            self.queue_process.join()
            return bool(self.A3200Lib.A3200ProgramStop(self.handle, self.task))

    def get_queue_depth(self, task=-1):
        '''
        Query and return the queue depth on the task.
        '''
        if self.queue_status[task].value > 0:
            count = ct.c_double()
            # self.A3200Lib.A3200StatusGetItem.argtypes = [ct.c_void_p, ct.wintypes.WORD, ct.wintypes.DWORD, ct.wintypes.DWORD, ct.POINTER(ct.c_double)]
            item_index = ct.c_int32(self.task)
            item_code = ct.c_int32(325)
            extra = ct.c_int32(0)
            success = self.A3200Lib.A3200StatusGetItem(
                self.handle, item_index, item_code, extra, ct.byref(count)
            )
            return int(count.value)
        else:
            # the task is not in Queue Mode, return 0
            return 0

    def put_command(self, command, args, task=-1):
        self.command_queue[self.task].put((command, args))

    def simple_queue_manager(self, task=-1, wait_mode='pause', loop_delay=0.025):
        if task < 0:
            task = self.task
        while self.queue_status[task] == 1:
            while not self.cmd_queue[task].empty():
                cmd = self.cmd_queue[task].get(self.loop_delay)

            success, depth = self.get_queue_depth(task)
            if success:
                if depth < 1:
                    if not self.program_paused[task]:
                        self.program_pause(task)
                else:
                    if self.program_paused[task]:
                        self.program_start(task)
            time.sleep(self.loop_delay)

    def program_start(self, task=-1):
        if task < 0:
            task = self.task
        return bool(self.A3200Lib.A3200ProgramStart(self.handle, task))

    def program_pause(self, task=-1):
        if task < 0:
            task = self.task
        return bool(self.A3200Lib.A3200ProgramPause(self.handle, task))

    ###### Status Functions ######

    def get_position(self, axes, return_type=list):
        '''
        Get the program position feedback of axes.

        For some reason only works simultaineously with X, Y or individual ZZ# axes
        Input:
            axes: list of axes to query the position of
            returntype: preferred returntype, list or dict
        Output:
            list or dict of the axis program position feedback, None if unsuccessful
        '''
        if self.A3200_is_Open:
            ax = {}
            if type(axes) is list:
                for a in axes:
                    ax[a] = name_to_index(a)
            else:
                ax[axes] = name_to_index(axes)

            n = ct.wintypes.DWORD(1)
            s = 107
            item_code = ct.wintypes.DWORD(s)
            s = 0
            extras = ct.wintypes.DWORD(s)
            ret = ct.c_double()

            values = {}
            for k in ax.keys():
                item_index = ct.wintypes.WORD(ax[k])
                s = self.A3200Lib.A3200StatusGetItem(
                    self.handle, item_index, item_code, extras, ct.byref(ret)
                )
                if s == 1:
                    values[k] = ret.value
            if self.debug:
                print(values)
            if s == 1:
                if type(axes) is str:
                    # ie if we just have one axis
                    return values[axes]
                else:
                    if return_type is list:
                        return [values[i] for i in axes]
                    else:
                        return values
            else:
                return None

    def is_move_done(self, axis, mode='done'):
        '''
        Polls axis and returns false untill the move is done.
        '''
        modes = {'done': 1 << 22, 'in pos': 1 << 22}
        if mode not in modes.keys():
            mode = 'done'

        ax = name_to_index(axis)
        item_code = ct.c_uint(modes[mode])
        s = 0
        extras = ct.wintypes.DWORD(s)
        ret = ct.c_double()

        item_index = ct.wintypes.WORD(ax)
        s = self.A3200Lib.A3200StatusGetItem(
            self.handle, item_index, item_code, extras, ct.byref(ret)
        )
        return s, ret.value

    def absolute(self, task=-1):
        '''
        Sets the motion to absolute mode
        '''
        s = 0
        if task < 0:
            task = self.task
        s = self.A3200Lib.A3200MotionSetupAbsolute(self.handle, task)
        if s == 1:
            self.motion_mode = 'absolute'
        else:
            raise MotionException('A3200.absolute', 'command failed', 'e-stop')
        return s

    def incremental(self, task=-1):
        '''
        Sets the motion to incremental mode
        '''
        s = 0
        if task < 0:
            task = self.task
        s = self.A3200Lib.A3200MotionSetupIncremental(self.handle, task)
        if s == 1:
            self.motion_mode = 'incremental'
        else:
            raise MotionException('A3200.absolute', 'command failed', 'e-stop')
        return s

    def setup_functions(self):
        '''
        Some functions require arg and return types to be set, this function does so.
        '''
        self.A3200Lib.A3200MotionLinear.argtypes = [
            ct.c_void_p,
            ct.c_uint,
            ct.c_ulong,
            ct.POINTER(ct.c_double),
        ]
        self.A3200Lib.A3200MotionLinear.restypes = ct.c_bool
        self.A3200Lib.A3200CommandExecute.argtypes = [
            ct.c_void_p,
            ct.c_uint,
            ct.wintypes.LPCSTR,
            ct.POINTER(ct.c_double),
        ]
        self.A3200Lib.A3200CommandExecute.restypes = ct.c_bool
        self.A3200Lib.A3200VariableSetTaskString.argtypes[
            ct.c_void_p, ct.c_uint, ct.wintypes.DWORD, ct.wintypes.LPCSTR
        ]
        self.A3200Lib.A3200VariableSetTaskString.restypes = ct.c_bool
        self.A3200Lib.A3200VariableSetGlobalString.argtypes[
            ct.c_void_p, ct.c_uint, ct.wintypes.DWORD, ct.wintypes.LPCSTR
        ]
        self.A3200Lib.A3200VariableSetTaskString.restypes = ct.c_bool
        self.A3200Lib.A3200VariableGetTaskString.argtypes[
            ct.c_void_p,
            ct.c_uint,
            ct.wintypes.DWORD,
            ct.wintypes.LPSTR,
            ct.wintypes.DWORD,
        ]
        self.A3200Lib.A3200VariableGetTaskString.restypes = ct.c_bool
        self.A3200Lib.A3200VariableSetValueByName.argtypes[
            ct.c_void_p, ct.c_uint, ct.wintypes.LPCSTR, ct.c_double
        ]

    def connect(self):
        '''
        Connect to the A3200 and return a handle.

        Returns None if not successful.
        '''
        if not self.A3200_is_Open:
            self.A3200Lib = ct.WinDLL(
                r"C:\Program Files (x86)\Aerotech\A3200\CLibrary\Bin64\A3200C64.dll"
            )
            self.handle = ct.c_void_p()
            if self.A3200Lib.A3200Connect(ct.byref(self.handle)):
                # print('success')
                self.A3200_is_Open = True
                return self.handle, self.A3200Lib
            else:
                self.A3200_is_Open = False
                raise MotionException('A3200->connect', 'Failed to connect', 'estop')
                return None
        else:
            # if already open, just return the handly and lib handle
            return self.A3200Lib, self.handle

    def disconnect(self):
        '''
        Disconnect from the A3200

        Return 1 if successful.
        '''
        if self.A3200_is_Open:
            return self.A3200Lib.A3200Disconnect(self.handle)

    def get_task_variable(self, index, count=1, task=-1):
        '''
        Get a range of (count) task variable(s) starting at index.

        Input:
            Index: integer describing the start of the range
            Count: the length of the range
            Task:  The task whose variable you wish to poll, if not specified, uses the default of the A3200 instance
        Returns:
            List of the requested variables (float type) or None if the function fails
        '''
        if self.A3200_is_Open:
            variables = (ct.c_double * count)()
            c_index = ct.wintypes.DWORD(index)
            c_count = ct.wintypes.DWORD(count)
            if task < 0:
                success = self.A3200Lib.A3200VariableGetTaskDoubles(
                    self.handle, self.task, c_index, variables, c_count
                )
            else:
                success = self.A3200Lib.A3200VariableGetTaskDoubles(
                    self.handle, task, c_index, variables, c_count
                )
            if success == 1:
                return [v for v in variables]
            else:
                return None

    def set_task_variable(self, index, variables, task=-1):
        '''
        Set a range of (count) task variable(s) starting at index.

        Input:
            Index: integer describing the start of the range
            Variables: list of the varaibles to set
            Task:  The task whose variable you wish to poll, if not specified, uses the default of the A3200 instance
        Returns:
            List of the requested variables (float type) or None if the function fails
        '''
        if self.A3200_is_Open:
            try:
                c_variables = (ct.c_double * len(variables))(*variables)
                c_count = ct.c_int(len(variables))
            except TypeError:
                c_variables = (ct.c_double * 1)(*[variables])
                c_count = ct.c_int(1)
            c_index = ct.c_int(index)
            if task < 0:
                return self.A3200Lib.A3200VariableSetTaskDoubles(
                    self.handle, self.task, c_index, c_variables, c_count
                )
            else:
                return self.A3200Lib.A3200VariableSetTaskDoubles(
                    self.handle, task, c_index, c_variables, c_count
                )

    def get_global_variable(self, index, count=1):
        '''
        Get a range of (count) task variable(s) starting at index.

        Input:
            Index: integer describing the start of the range
            Count: the length of the range
            Task:  The task whose variable you wish to poll, if not specified, uses the default of the A3200 instance
        Returns:
            List of the requested variables (float type) or None if the function fails
        '''
        if self.A3200_is_Open:
            variables = (ct.c_double * count)()
            c_index = ct.wintypes.DWORD(index)
            c_count = ct.wintypes.DWORD(count)
            success = self.A3200Lib.A3200VariableGetGlobalDoubles(
                self.handle, c_index, variables, c_count
            )
            if success == 1:
                return [v for v in variables]
            else:
                return None

    def set_global_variable(self, index, variables, count=1):
        '''
        Set a range of (count) Global variable(s) starting at index.

        Input:
            Index: integer describing the start of the range
            Variables: list of the varaibles to set
        Returns:
            1 if sucessful, 0 otherwise
        '''
        if self.A3200_is_Open:
            try:
                c_variables = (ct.c_double * len(variables))(*variables)
                c_count = ct.c_int(len(variables))
            except TypeError:
                c_variables = (ct.c_double * 1)(*[variables])
                c_count = ct.c_int(1)
            c_index = ct.c_int(index)
            return self.A3200Lib.A3200VariableSetGlobalDoubles(
                self.handle, c_index, c_variables, c_count
            )

    def get_task_string(self, index, length=50, task=-1):
        '''
        Get a task string at index.

        Input:
            index: integer index for the string to get
            length: the length of the string, need only be longer than the length
            task: the task from which to pull the string, uses the instance task if not specified
        Returns:
            the string encoded as utf8 or None if it fails
        '''
        if self.A3200_is_Open:
            c_string = ct.create_string_buffer(b' ' * (length))
            c_index = ct.wintypes.DWORD(index)
            c_length = ct.wintypes.DWORD(length)
            if task < 0:
                success = self.A3200Lib.A3200VariableGetTaskString(
                    self.handle, self.task, c_index, c_string, c_length
                )
            else:
                success = self.A3200Lib.A3200VariableGetTaskString(
                    self.handle, task, c_index, c_string, c_length
                )
            if success == 1:
                return c_string.value
            else:
                return None

    def set_task_string(self, index, string, task=-1):
        '''
        Set a task string at index.

        Input:
            index: integer index for the string to set
            task: the task from which to set the string, uses the instance task if not specified
        Returns:
            1 if successful, 0 otherwise
        '''
        if self.A3200_is_Open:
            c_string = ct.create_string_buffer(string.encode('utf8'))
            c_index = ct.wintypes.DWORD(index)
            if task < 0:
                return self.A3200Lib.A3200VariableSetTaskString(
                    self.handle, self.task, c_index, c_string
                )
            else:
                return self.A3200Lib.A3200VariableSetTaskString(
                    self.handle, task, c_index, c_string
                )

    def get_global_string(self, index, length=50):
        '''
        Get a global string at index.

        Input:
            index: integer index for the string to get
            length: the length of the string, need only be longer than the length
        Returns:
            the string encoded as utf8 or None if it fails
        '''
        if self.A3200_is_Open:
            c_string = ct.create_string_buffer(b' ' * (length))
            c_index = ct.wintypes.DWORD(index)
            c_length = ct.wintypes.DWORD(length)
            success = self.A3200Lib.A3200VariableGetGlobalString(
                self.handle, c_index, c_string, c_length
            )
            if success == 1:
                return c_string.value
            else:
                return None

    def set_global_string(self, index, string):
        '''
        Set a global string at index.

        Input:
            index: integer index for the string to set
            string: the python string to set
        Returns:
            1 if successful, 0 otherwise
        '''
        if self.A3200_is_Open:
            c_string = ct.create_string_buffer(string.encode('utf8'))
            c_index = ct.wintypes.DWORD(index)
            return self.A3200Lib.A3200VariableSetGlobalString(
                self.handle, c_index, c_string
            )

    def set_variable(self, name, value, task=-1):
        '''
        Not yet functional....
        '''
        c_name = ct.create_string_buffer(name.encode('utf8'))
        c_value = ct.c_double(value)
        return self.A3200Lib.A3200VariableSetValueByName(
            self.handle, self.task, c_name, c_value
        )


def test_process(axis, task, queue_out):
    a = A3200()
    queue_out.put([a.enable_queue_mode(task)])
    queue_out.put([a.cmd_exe('Ramp Rate 1000', task)])
    queue_out.put([a.cmd_exe('CoordinatedAccelLimit = 1000', task)])
    queue_out.put([a.cmd_exe('G108\nF5\nWAIT( $global[0] == 1) 10000', task)])
    f = time.time()
    success, depth = a.get_queue_depth(task)
    num = 0
    while depth < 10 and num < 10:
        num += 1
        queue_out.put([a.linear([axis], [-1], task)])
        success, depth = a.get_queue_depth(task)
        b = time.time()
        queue_out.put([b - f, depth, num])
    queue_out.put([a.cmd_exe('G108\nF5\nWAIT( $global[0] == 2) 10000', task)])
    queue_out.put([a.cmd_exe('Dwell 1', task)])
    while depth > 1:
        success, depth = a.get_queue_depth(task)
        time.sleep(0.05)
    queue_out.put([a.disable_queue_mode(task)])
    queue_out.put('done')
    a.disconnect()


def test_1(axis, task):
    a = A3200()
    a.enable_queue_mode(task)
    a.cmd_exe('Ramp Rate 1000', task)
    a.cmd_exe('CoordinatedAccelLimit = 1000', task)
    a.cmd_exe('G108\nF1\nWAIT( $global[0] == 1) 10000', task)
    a.linear([axis], [-2], task)
    a.linear([axis], [2], task)
    a.cmd_exe('WAIT MOVEDONE 10000', task)
    a.cmd_exe('Dwell 1', task)
    depth = 1
    while depth > 0:
        success, depth = a.get_queue_depth(task)
        time.sleep(0.05)
    a.disable_queue_mode(task)
    a.disconnect()


def test_2(axis, task):
    a = A3200()
    a.enable_queue_mode(task)
    a.cmd_exe('Ramp Rate 1000', task)
    a.cmd_exe('CoordinatedAccelLimit = 1000', task)
    a.cmd_exe('G108\nF1\nWAIT( $global[0] == 1) 10000', task)
    a.cmd_exe('$DO[4].ZZ1 = 1', task)
    a.cmd_exe('Dwell 2', task)
    a.cmd_exe('$DO[4].ZZ1 = 0', task)
    a.cmd_exe('Dwell 1', task)
    depth = 1
    while depth > 0:
        success, depth = a.get_queue_depth(task)
        time.sleep(0.05)
    a.disable_queue_mode(task)
    a.disconnect()


def queue_monitor(task, status, return_queue):
    qmon_A3200 = A3200(default_task=task)
    qmon_A3200.A3200Lib.A3200ProgramInitializeQueue(qmon_A3200.handle, task)
    return_queue.put('child_a3200 connected: {} '.format(qmon_A3200.A3200_is_Open))
    bf = 100
    empty = ''
    for i in range(bf):
        empty += ' '
    errorString = ct.c_buffer(empty.encode('utf-8'))
    bufferSize = ct.c_int(bf)
    while status.value != 0:
        depth = qmon_A3200.get_queue_depth(task)
        time.sleep(0.05)
        if depth < 2:
            # suc = qmon_A3200.cmd_exe('Dwell 1', task)
            suc = qmon_A3200.cmd_exe(
                'WAIT(TASKSTATUS({}, DATAITEM_QueueLineCount) > 1) 10000'.format(
                    int(task)
                )
            )
            qmon_A3200.A3200Lib.A3200GetLastErrorString(errorString, bufferSize)
            return_queue.put('{0}, {1}'.format(suc[0], errorString.value))
    status.value = -1


# for testing purposes only
if __name__ == '__main__':
    __spec__ = None
    a = A3200()
    # print('X {0[0]:0.3f} Y {0[1]:0.3f}'.format(a.get_position(['X', 'Y'])))
    a.enable_queue_mode()
    a.incremental_move(['X', 'Y'], [-10, -10], speed=5)
    for i in range(10):
        print(a.wait_for_move_done('X'))
        time.sleep(0.1)
    print('done')
    a.absolute_move(['X', 'Y'], [-400, -400], speed=5)
    a.disable_queue_mode()
    '''
    queue_out = Queue()
    p = Process(target = test_process, args = ('ZZ1', 1, queue_out))
    p.start()
    r1 = ''
    while 'done' not in r1:
        r1 = queue_out.get(timeout = 3)
        print(r1)
    p.join()
    input()
    '''

    '''
    __spec__ = None

    bf = 100
    empty = ''
    for i in range(bf):
        empty += ' '
    errorString = ct.c_buffer(empty.encode('utf-8'))
    bufferSize = ct.c_int(bf)
    print(a.cmd_exe('F1'))

    a.enable_queue_mode()
    a.set_task_variable(1, [-1])
    try:
        a.linear(['ZZ3'], [-1])
        a.linear(['ZZ3'], [-1])
        a.linear(['ZZ3'], [-1])
        a.linear(['ZZ3'], [-1])
        a.linear(['ZZ3'], [-1])
        a.linear(['ZZ3'], [-1])
        a.linear(['ZZ3'], [-1])
        a.linear(['ZZ3'], [-1])
        a.linear(['ZZ3'], [-1])
        a.linear(['ZZ3'], [-1])
    except:
        print(a.A3200Lib.A3200GetLastErrorString(errorString, bufferSize))
    s = time.time()
    a.wait_for_move_done(['ZZ3'])
    a.set_task_variable(1, [1])
    f = time.time()
    print(f-s)
    time.sleep(1)
    a.disable_queue_mode()


    __spec__ = None
    #a.enable_queue_mode()
    n = 100
    import numpy as np
    v = np.zeros(n)
    s = time.time()
    for i in range(n):
        #a.linear(['ZZ3'], [-5])
        #a.DO('ZZ1', 0, True)
        #a.linear(['ZZ3'], [5])
        #a.DO('ZZ1', 0, False)
        v[i] = a.AI('ZZ2', 0)[1]
    f = time.time()
    print(v)
    print(sum(v)/n, np.std(v), min(v)-max(v))
    print((f - s)/n)
    #a.disable_queue_mode()

    a.set_global_variable(0, [0], 1)
    axes = ['ZZ1', 'ZZ1']
    tasks = [1, 2]
    procs = [Process(target = test_1, args = [axes[0], tasks[0]]),
             Process(target = test_2, args = [axes[1], tasks[1]])]
    for p in procs:
        p.start()
    time.sleep(3)
    a.set_global_variable(0, [1], 1)

    for p in procs:
        p.join()
    '''

    a.disconnect()
    # input()
