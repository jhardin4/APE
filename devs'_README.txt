The deconvolver.py is the translation layer used to gain information about a print job from gcode.

    There exists a class getape in deconvolver.py which contains multiple functions used to deconvolve gcode.  These funcions have defult values stored in __init__.  __init__ calles these values from import_ape.py.

    __init__ is set up in such a way that multithreading can be implimented easily.  It must be passed call_file.  call_file is either a file path to a gcode or 'auto'.

    If __init__ is passed 'auto' it will look at the folder Print_With_APE and use the most recent file changed or created.  This is done by calling runape.findfile under run_ape.py.

        findfile will, when passed fileortime as either 'file' or 'time', find the youngest file in the directory and return either the time of its latest modification or the file name.
            findfile DOES NOT rely on run_ape.py's __init__ to run and cache a modification time for the youngest file in a given folder.  This could easily become recursive so be careful when modifying.
            Here, __init__ must have a folder specified and findfile must have fileortime specified.

        When __init__ is passed 'auto', it will always find Print_With_APE in the users home directory in all operating systems IFF the program is run properly bacause start_ape.py will detect OS type and run an initial install *intelligently* such that there will always be a Print_With_APE folder in the users home directory.
            *intelligently* means that a check of what components are needed and an install of any that do, but none that don't, will take place.

    Functions:

        run is a placeholder for multithreading if required in the future.

        point gathers spatial data for any line of gcode and returns it in a list of dictionaries with structure [ { X : #, Y : #, Z : # }, { X : #, Y : #, Z : # } ... ].  Defults to X : 0, Y : 0, Z : 0 internally (calculation defult) and Empty : Empty externally (output defult).
            point requires call_file, implicitorexplicitaxes, implicitorexplicittravel, lineorlayer, line_start, line_end, UI_line, past_line
                call_file: the file path to the gcode to be read from
                implicitorexplicitaxes: must be given 'implicit' or 'explicit' and is used to handle gcode which uses global or relative coordinates.  Defults to 'explicit' or golbal.
                implicitorexplicittravel: must be given 'implicit' or 'explicit' and is used to handle printer firmware which uses global or relative coordinates.  Defults to 'explicit' or global.
                lineorlayer: must be given 'line' or 'layer' and is used to determine if point is to read from line # "line_start" to line # "line_end" or from layer # "line_start" to layer # "line_end".  Defults to 'line'.
                line_start: # used to decide what line to start deconvolution on. Can be passed 'start' which will use numberoflines from import_ape to determine the first line in the file.  Defults to 0.
                line_end: # used to decide what line to end deconvolution on.  Can be passed 'end' which will use numberoflines from import_ape.py to determine the ending line in the file.  Defults to 1000.
                    numberoflines currently defults to using start at line 0 and will count the lines in the file to determine the final line.  Must be passed a file path and startorend.  startorend can be 'start' or 'end' and will determine if numberoflines outputs 0 or counts the number of lines in call_file and returns the final line number.
                UI_line: must be given 'yes' or 'no'.  'no' makes point ignore all lines which do not contain spatial information where as 'yes' makes point place a dictionary { Empty : Empty } in each line it read which does not contain spatial information.  Defults to 'no'.
                past_line: must be given a dictionary containing at least { X : #, Y : #, Z : # } or 'Empty'.  Used to retain previus spatial information used for deconvolving from gcode to apecode.  Defults to 'Empty'.
            point currently expects all spatial information to be contained in a G1 command.  It is capable of dealing with all possible variations of this command including comments on that line.

        hotend gathers tool data and DOES know what tool and material is being used.  This is purposeful so that multiplexers can be used in conjunction with oneanother and with multiple heads congruently.  hotend returns a list of dictionaries with structure [ { H : #, SF : #, BF : #, TC : str, T : #, MX : #, MXA : str, D : # }, { H : #, SF : #, BF : #, TC : str, T : #, MX : #, MXA : str, D : # } ... ].  Defults to H : 0, SF : 0, BF : 0, TC : '', T : 1, MX : 1, MXA : '', D : 0 internally (calculation defult) and Empty : Empty externally (output defult).
            hotend requires call_file, lineorlayer, line_start, line_end, initialize, UI_line, past_line
                call_file: the file path to the gcode to be read from
                lineorlayer: must be given 'line' or 'layer' and is used to determine if point is to read from line # "line_start" to line # "line_end" or from layer # "line_start" to layer # "line_end".  Defults to 'line'.
                line_start: # used to decide what line to start deconvolution on. Can be passed 'start' which will use numberoflines from import_ape to determine the first line in the file.  Defults to 0.
                line_end: # used to decide what line to end deconvolution on.  Can be passed 'end' which will use numberoflines from import_ape.py to determine the ending line in the file.  Defults to 1000.
                    numberoflines currently defults to using start at line 0 and will count the lines in the file to determine the final line.  Must be passed a file path and startorend.  startorend can be 'start' or 'end' and will determine if numberoflines outputs 0 or counts the number of lines in call_file and returns the final line number.
                initialize: must be given 'yes' or 'no'.  initialize will set line_start to 0 and line_end to 100 if passed 'yes' and will do nothing if passed 'no'.  If set to 'yes' hotend will output only a single deconvolved line. Used for preheating and initializing the printer.  Defults to 'no'.
                UI_line: must be given 'yes' or 'no'.  'no' makes point ignore all lines which do not contain spatial information where as 'yes' makes point place a dictionary { Empty : Empty } in each line it read which does not contain spatial information.  Defults to 'no'.
                past_line: must be given a dictionary containing at least { H : #, SF : #, BF : #, TC : str, T : #, MX : #, MXA : str, D : # } or 'Empty'.  Used to retain previus tool information used for deconvolving from gcode to apecode.  Defults to 'Empty'.
            hotend expects a gcode meant for a marlin/ramps or duet/reprap based machine.  It can work with kliper enabled machines (preffered as they are by far the most computationally powerful and least buggy).

        extrude gethers extrusion velocity and distance data and returns it in a list of dictionaries with structure [ { E : #, f : #, SetE : # }, { E : #, f : #, SetE : # } ... ].  Defults to Empty : Empty ONLY (for both calculations and output).
            extrude requires call_file, lineorlayer, line_start, line_end, UI_line, past_line
                call_file: the file path to the gcode to be read from
                lineorlayer: must be given 'line' or 'layer' and is used to determine if point is to read from line # "line_start" to line # "line_end" or from layer # "line_start" to layer # "line_end".  Defults to 'line'.
                line_start: # used to decide what line to start deconvolution on. Can be passed 'start' which will use numberoflines from import_ape to determine the first line in the file.  Defults to 0.
                line_end: # used to decide what line to end deconvolution on.  Can be passed 'end' which will use numberoflines from import_ape.py to determine the ending line in the file.  Defults to 1000.
                    numberoflines currently defults to using start at line 0 and will count the lines in the file to determine the final line.  Must be passed a file path and startorend.  startorend can be 'start' or 'end' and will determine if numberoflines outputs 0 or counts the number of lines in call_file and returns the final line number.
                UI_line: must be given 'yes' or 'no'.  'no' makes point ignore all lines which do not contain spatial information where as 'yes' makes point place a dictionary { Empty : Empty } in each line it read which does not contain spatial information.  Defults to 'no'.
                past_line: must be given a dictionary containing at least { E : #, f : #, SetE : # } or 'Empty'.  Used to retain previus extrusion information used for deconvolving from gcode to apecode.  Defults to 'Empty'.

        hotbed gathers environmental data.  At the moment, it only gathers temperature information about the hotbed and enclosure.  extrude assumes machines do not have control over the chamber's atmospheric composition (useful for annealing when this feature becomes implimented).  Returns a list of dictionaries with structure [ { HB : #, HC : # }, { HB : #, HC : # }, ... ].  Defults to HB : 0, HC : 0 internally (calculation defult) and Empty : Empty externally (output defult).
            hotbed requires call_file, lineorlayer, line_start, line_end, initialize, UI_line, past_line
            call_file: the file path to the gcode to be read from
                lineorlayer: must be given 'line' or 'layer' and is used to determine if point is to read from line # "line_start" to line # "line_end" or from layer # "line_start" to layer # "line_end".  Defults to 'line'.
                line_start: # used to decide what line to start deconvolution on. Can be passed 'start' which will use numberoflines from import_ape to determine the first line in the file.  Defults to 0.
                line_end: # used to decide what line to end deconvolution on.  Can be passed 'end' which will use numberoflines from import_ape.py to determine the ending line in the file.  Defults to 1000.
                    numberoflines currently defults to using start at line 0 and will count the lines in the file to determine the final line.  Must be passed a file path and startorend.  startorend can be 'start' or 'end' and will determine if numberoflines outputs 0 or counts the number of lines in call_file and returns the final line number.
                initialize: must be given 'yes' or 'no'.  initialize will set line_start to 0 and line_end to 100 if passed 'yes' and will do nothing if passed 'no'.  If set to 'yes' hotend will output only a single deconvolved line. Used for preheating and initializing the printer.  Defults to 'no'.
                UI_line: must be given 'yes' or 'no'.  'no' makes point ignore all lines which do not contain spatial information where as 'yes' makes point place a dictionary { Empty : Empty } in each line it read which does not contain spatial information.  Defults to 'no'.
                past_line: must be given a dictionary containing at least { H : #, SF : #, BF : #, TC : str, T : #, MX : #, MXA : str, D : # } or 'Empty'.  Used to retain previus tool information used for deconvolving from gcode to apecode.  Defults to 'Empty'.
            hotbed expects a gcode meant for a marlin/ramps or duet/reprap based machine.  It can work with kliper enabled machines (preffered as they are by far the most computationally powerful and least buggy).

        interpoint gathers spatial and extruder data.  interpoint treats the extruder as a 4th axis and keeps velocity data.  This can be used to determine movements made over time as well as impulse, acceleration, and jerk.  Returns a list of dictionaries with structure [ { X : #, Y : #, Z : #, E : #, F : #, SetE : # }, { X : #, Y : #, Z : #, E : #, F : #, SetE : # } ... ].  Defults to X : 0, Y : 0, Z : 0, E : 0, F : 0, SetE : Empty internally (calculation defult) and Empty : Empty externally (output defult).
            interpoint requires call_file, implicitorexplicitaxes, implicitorexplicittravel, lineorlayer, line_start, line_end, UI_line, past_line
                call_file: the file path to the gcode to be read from
                implicitorexplicitaxes: must be given 'implicit' or 'explicit' and is used to handle gcode which uses global or relative coordinates.  Defults to 'explicit' or golbal.
                implicitorexplicittravel: must be given 'implicit' or 'explicit' and is used to handle printer firmware which uses global or relative coordinates.  Defults to 'explicit' or global.
                lineorlayer: must be given 'line' or 'layer' and is used to determine if point is to read from line # "line_start" to line # "line_end" or from layer # "line_start" to layer # "line_end".  Defults to 'line'.
                line_start: # used to decide what line to start deconvolution on. Can be passed 'start' which will use numberoflines from import_ape to determine the first line in the file.  Defults to 0.
                line_end: # used to decide what line to end deconvolution on.  Can be passed 'end' which will use numberoflines from import_ape.py to determine the ending line in the file.  Defults to 1000.
                    numberoflines currently defults to using start at line 0 and will count the lines in the file to determine the final line.  Must be passed a file path and startorend.  startorend can be 'start' or 'end' and will determine if numberoflines outputs 0 or counts the number of lines in call_file and returns the final line number.
                UI_line: must be given 'yes' or 'no'.  'no' makes point ignore all lines which do not contain spatial information where as 'yes' makes point place a dictionary { Empty : Empty } in each line it read which does not contain spatial information.  Defults to 'no'.
                past_line: must be given a dictionary containing at least { X : #, Y : #, Z : #, E : #, F : #, SetE : # OR Empty } or 'Empty'.  Used to retain previus spatial and extruder information used for deconvolving from gcode to apecode.  Defults to 'Empty'.

        hotendUI runs hotend at defult but must be passed initialize and past_line.  Uses file specified in call_file under __init__.

        hotendUI_line runs hotend at defult and deconvolves only the line specified but must be passed line and past_line.  Uses file specified in call_file under __init__.

        hotbedUI runs hotbed at defult but must be passed initialize and past_line.  Uses file specified in call_file under __init__.

        hotbedUI_line runs hotbed at defult and deconvolves only the line specified but must be passed line and past_line.  Uses file specified in call_file under __init__.

        pointUI runs point at defult but must be passed initialize and past_line.  Uses file specified in call_file under __init__.

        pointUI_line runs point at defult and deconvolves only the line specified but must be passed line and past_line.  Uses file specified in call_file under __init__.

        interpointUI runs interpoint at defult but must be passed initialize and past_line.  Uses file specified in call_file under __init__.

        interpointUI_line runs interpoint at defult and deconvolves only the line specified but must be passed line and past_line.  Uses file specified in call_file under __init__.

        extrudeUI runs extrude at defult but must be passed initialize and past_line.  Uses file specified in call_file under __init__.

        extrudeUI_line runs extrude at defult and deconvolves only the line specified but must be passed line and past_line.  Uses file specified in call_file under __init__.




line_interlacer.py
    This module contains a single function, interlace.  It uses the deconvolver functions to deconvolve and weave information from the gcode passed to it into apecode.  This apecode takes the form [ { H : #, SF : #, BF : #, TC : str, T : #, MX : #, MXA : str, D : # }, { HB : #, HC : # }, { X : #, Y : #, Z : #, E : #, F : #, SetE : # }, { H : #, SF : #, BF : #, TC : str, T : #, MX : #, MXA : str, D : # }, { HB : #, HC : # }, { X : #, Y : #, Z : #, E : #, F : #, SetE : # } ] or [ { X : #, Y : #, Z : # }, { X : #, Y : #, Z : # } ]
    Under normal operation, this will never be called unless a gcode which can be deconvolved is detected.
        interlace expects to be passed an argument for fileorlayer, wholeorpointcloud, usememory.
            fileorlayer: must be given 'file' or a # between 0 and the maximum layer number; determines if interlace will deconvolve a whole file or just one layer within that file.
            wholeorpointcloud: must be given 'whole' or 'pointcloud' and makes the output contain all material, environment, tool, and path data if given 'whole' or just path data if 'pointcloud'.
            usememory: must be given 'yes' or 'no' and is used to determine if RAM or storage is used to contain the deconvolved APE code.

start_ape.py
    This module contains checksfile, searchfile, makeshortcut, and installape.  start_ape.py is used to find file paths, create folders and shortcuts, and check the install directory / related folders for existence (not integrety yet).
        checksfile requires no commands to be passed to it.  Its function is to check the install directory and for the existance of the Print_With_APE folder within the correct locations depending on operating system type.  Works on Linux and Windows.
        searchfile requires name and root_folder.  It searches root_folder for a file with name.  It returns the total file path for the specified name under root_folder.  It will search through directories under root_folder of any depth.
            name: must be passed a string which the user wishes to search for.
            root_folder: must be passed a string which the user wishes to search under.
        makeshortcut requires sortcut_name, py_loc, start_in, and icon_loc.  makeshortcut is used to create a microsoft windows compatable shortcut using shell.  It does not work ATM and throws no errors.  Requires debugging.
            shortcut_name:

