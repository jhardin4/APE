import copy
import math
from ToolPathGeneration import CompGeo as cg
from ToolPathGeneration import ToolPathTools as tpt


# -----------------------------FUNCTIONS---------------------------------#
def basearray(apara, bpara, cpara, mmax, nmax):
    # point_array is a symmetric hexagonal lattice with side length of apara,
    # width of bpara, and steeple height of cpara
    # the pattern is propogated for mmax point in x and nmax points in y

    point_array = []
    for m in range(0, mmax):
        point_array_line = []
        for n in range(0, nmax):
            point_array_line.append(
                [
                    (m * bpara / 2),
                    (
                        n * ((2 * apara + 2 * cpara) / 2)
                        + (-2 * cpara) / 4
                        + (-1) ** (n - m) * ((2 * cpara) / 4)
                    ),
                ]
            )
        point_array.append(point_array_line)

    return point_array


def throughpath(border, tlayers, ltl, zpos, material, matslide):
    through_path = []
    through_z = zpos - (tlayers - 1) / tlayers * ltl
    center = {
        'X': sum([border[n]['X'] for n in range(0, len(border))]) / len(border),
        'Y': sum([border[n]['Y'] for n in range(0, len(border))]) / len(border),
    }
    through_path.append(
        {
            'startpoint': {'X': center['X'], 'Y': center['Y'], 'Z': through_z},
            'endpoint': {'X': border[0]['X'], 'Y': border[0]['Y'], 'Z': through_z},
            'material': material,
        }
    )
    bordercycle = border[:]
    bordercycle.append(border[0])
    for t in range(0, tlayers):
        # run around the border for all layers
        for p in range(0, len(border)):
            startpoint = {
                'X': bordercycle[p]['X'],
                'Y': bordercycle[p]['Y'],
                'Z': through_z,
            }
            endpoint = {
                'X': bordercycle[p + 1]['X'],
                'Y': bordercycle[p + 1]['Y'],
                'Z': through_z,
            }
            through_path.append(
                {'startpoint': startpoint, 'endpoint': endpoint, 'material': material}
            )
        # move up for each layer but the last
        if t != (tlayers - 1):
            through_path.append(
                {
                    'startpoint': {
                        'X': border[0]['X'],
                        'Y': border[0]['Y'],
                        'Z': through_z,
                    },
                    'endpoint': {
                        'X': border[0]['X'],
                        'Y': border[0]['Y'],
                        'Z': through_z + ltl / tlayers,
                    },
                    'material': material,
                }
            )
            through_z = through_z + ltl / tlayers
    # Minimize spiking by runing the border three more times
    for t in range(0, 3):
        for p in range(0, len(border)):
            startpoint = {
                'X': bordercycle[p]['X'],
                'Y': bordercycle[p]['Y'],
                'Z': through_z,
            }
            endpoint = {
                'X': bordercycle[p + 1]['X'],
                'Y': bordercycle[p + 1]['Y'],
                'Z': through_z,
            }
            through_path.append(
                {'startpoint': startpoint, 'endpoint': endpoint, 'material': matslide}
            )

    return through_path


def hexpt2toolpath(point_matrix, material, materialslide):
    toolpath = []

    # X-oriented waves
    for n in range(0, len(point_matrix[0])):
        for m in range(1, len(point_matrix)):
            toolpath.append(
                {
                    'startpoint': tpt.list2XY(point_matrix[m - 1][n]),
                    'endpoint': tpt.list2XY(point_matrix[m][n]),
                    'material': material,
                }
            )

    # Y-oriented waves
    for k in range(0, math.floor(len(point_matrix) / 2)):
        n = 1
        m = 2 * k
        t = 2
        while m < len(point_matrix) and n < len(point_matrix[0]):
            if t == 1:
                toolpath.append(
                    {
                        'startpoint': tpt.list2XY(point_matrix[m + 1][n]),
                        'endpoint': tpt.list2XY(point_matrix[m][n]),
                        'material': materialslide,
                    }
                )
                n = n + 1
                t = t + 1
            elif t == 2:
                toolpath.append(
                    {
                        'startpoint': tpt.list2XY(point_matrix[m][n - 1]),
                        'endpoint': tpt.list2XY(point_matrix[m][n]),
                        'material': material,
                    }
                )
                m = m + 1
                t = t + 1
            elif t == 3:
                toolpath.append(
                    {
                        'startpoint': tpt.list2XY(point_matrix[m - 1][n]),
                        'endpoint': tpt.list2XY(point_matrix[m][n]),
                        'material': materialslide,
                    }
                )
                n = n + 1
                t = t + 1
            elif t == 4:
                toolpath.append(
                    {
                        'startpoint': tpt.list2XY(point_matrix[m][n - 1]),
                        'endpoint': tpt.list2XY(point_matrix[m][n]),
                        'material': material,
                    }
                )
                m = m - 1
                t = 1

    return toolpath


def DistXYundulation(pointarray, apara, bpara, cpara, magx, magy):

    phasex = -math.pi / 3
    phasey = -apara / (apara + cpara) / 2 * math.pi

    point_darray = copy.deepcopy(pointarray)

    for m in range(0, len(point_darray)):
        for n in range(0, len(point_darray[m])):
            point_darray[m][n] = [
                point_darray[m][n][0]
                + magx
                * math.sin(2 * math.pi * point_darray[m][n][0] / 3 / bpara + phasex),
                point_darray[m][n][1]
                + magy
                * math.sin(
                    2 * math.pi * point_darray[m][n][1] / (2 * apara + 2 * cpara)
                    + phasey
                ),
            ]
    return point_darray


def DistXYundulationFull(pointarray, apara, bpara, cpara, phasex, phasey, magx, magy):

    point_darray = copy.deepcopy(pointarray)

    for m in range(0, len(point_darray)):
        for n in range(0, len(point_darray[m])):
            point_darray[m][n] = [
                point_darray[m][n][0]
                + magx
                * math.sin(2 * math.pi * point_darray[m][n][0] / 3 / bpara + phasex),
                point_darray[m][n][1]
                + magy
                * math.sin(
                    2 * math.pi * point_darray[m][n][1] / (2 * apara + 2 * cpara)
                    + phasey
                ),
            ]
    return point_darray


def hexcellborder(hexptarray, mint, nint, offset):
    connectionlines = []
    connectionlines.append([hexptarray[mint][nint], hexptarray[mint - 1][nint]])
    connectionlines.append([hexptarray[mint + 1][nint], hexptarray[mint + 1][nint - 1]])
    connectionlines.append([hexptarray[mint + 2][nint], hexptarray[mint + 3][nint]])
    connectionlines.append(
        [hexptarray[mint + 2][nint + 1], hexptarray[mint + 3][nint + 1]]
    )
    connectionlines.append(
        [hexptarray[mint + 1][nint + 1], hexptarray[mint + 1][nint + 2]]
    )
    connectionlines.append([hexptarray[mint][nint + 1], hexptarray[mint - 1][nint + 1]])
    '''
    plt.figure()
    for l in range(0,len(connectionlines)):
        plt.plot([connectionlines[l][0][0],connectionlines[l][1][0]],[connectionlines[l][0][1],connectionlines[l][1][1]])
    '''
    points = []
    for l in range(0, len(connectionlines)):
        if connectionlines[l][1][0] == connectionlines[l][0][0]:
            points.append(
                {
                    'X': connectionlines[l][1][0],
                    'Y': (connectionlines[l][1][1] - connectionlines[l][0][1])
                    / abs(connectionlines[l][1][1] - connectionlines[l][0][1])
                    * offset
                    + connectionlines[l][0][1],
                }
            )
        else:
            mtemp = (connectionlines[l][1][1] - connectionlines[l][0][1]) / (
                connectionlines[l][1][0] - connectionlines[l][0][0]
            )
            xtemp = (
                offset
                / (1 + mtemp ** 2) ** 0.5
                * (connectionlines[l][1][0] - connectionlines[l][0][0])
                / abs(connectionlines[l][1][0] - connectionlines[l][0][0])
                + connectionlines[l][0][0]
            )
            ytemp = (xtemp - connectionlines[l][0][0]) * mtemp + connectionlines[l][0][
                1
            ]
            points.append({'X': xtemp, 'Y': ytemp})

    return points


def helixpath(
    start,
    perimeter,
    pitch,
    overlap,
    zcurrent,
    ltl,
    helixid,
    history,
    distancetol,
    angletol,
    helixmat,
    supmat,
):
    # start - the start position on the perimeter though not necessarily a point in perimeter
    # perimenter - list of points that define the XY perimenter of the helix in CCW
    # pitch - the radian per layer
    # overlap - radian overlap with previous layer
    # zcurrent - zheight of current layer
    # ltl - layer to layer spacing
    # helixid - indentifier for the data specific to a individual helix
    # history - data for all helixes
    # distancetol and angletol - dimensional tolerances
    # Average pf points is used as center. This will generate errors if points are paritcularly imbalanced

    center = {
        'X': sum([perimeter[n]['X'] for n in range(0, len(perimeter))])
        / len(perimeter),
        'Y': sum([perimeter[n]['Y'] for n in range(0, len(perimeter))])
        / len(perimeter),
    }
    # print(str(center))
    if cg.pointinregion(center, perimeter, distancetol, angletol) is False:
        return 'Too concave'

    # find the maximum distance between the center and a point on the perimeter
    radius = max(
        [
            (perimeter[n]['X'] - center['X']) ** 2
            + (perimeter[n]['Y'] - center['Y']) ** 2
            for n in range(0, len(perimeter))
        ]
    )

    # construct overlap cycle
    perimeter_cycle = tpt.TPdeepcopy(perimeter)
    perimeter_cycle.append(perimeter_cycle[0])
    # Convert into 3D perimeter
    for p in range(0, len(perimeter)):
        perimeter_cycle[p]['Z'] = zcurrent
    # print(str(perimeter_cycle))
    # Structural first-pass
    toolpath1 = []
    # Conductive
    toolpath2 = []
    # Structural second-pass
    toolpath3 = []
    # Next history
    newhistory = []

    # check if this is first call of helixpath for this specific helic
    if len(history) == helixid:
        # Start angle
        startangle = math.atan2((start['Y'] - center['Y']), (start['X'] - center['X']))
        # End angle
        endangle = startangle + pitch
        # angle at new overlap point
        overlap_startangle = endangle - (pitch / abs(pitch)) * overlap
        first = 1

    else:
        # last point of the history motion
        start = history[helixid][len(history[helixid]) - 1]['endpoint']
        # Start angle of this call
        startangle = math.atan2((start['Y'] - center['Y']), (start['X'] - center['X']))
        # End angle of this call
        endangle = startangle + pitch
        # angle at new overlap point
        overlap_startangle = endangle - (pitch / abs(pitch)) * overlap
        first = 0
        # append the motion from the previous layer
        for h in range(0, len(history[helixid])):
            toolpath2.append(history[helixid][h])
            # print(toolpath2)

    # Collect the intersecions with the perimeter and the associatated peritmeter segment
    # start point and perimeter section
    startray = [
        center,
        {
            'X': radius * 1.1 * math.cos(startangle) + center['X'],
            'Y': radius * 1.1 * math.sin(startangle) + center['Y'],
        },
    ]
    intersections = []
    for s in range(0, len(perimeter)):
        periline = [
            {'X': perimeter_cycle[s]['X'], 'Y': perimeter_cycle[s]['Y']},
            {'X': perimeter_cycle[s + 1]['X'], 'Y': perimeter_cycle[s + 1]['Y']},
        ]
        inter = cg.LineSegIntersect2D(startray, periline, distancetol, angletol)
        dimlist = list(perimeter[0].keys())
        if inter != 'none':
            if dimlist[0] in inter:
                intersections.append([inter, s])
            elif inter[0] == 'colinear':
                intersections.append([inter[1], s])
                intersections.append([inter[2], s])

    # find intersection point closest to known start
    # print(intersections)
    # for i in range(0,len(intersections)):
    #    if ptalmostequal([intersections[i][0][0],intersections[i][0][1]], [start[0],start[1]],distancetol):
    #        startpoint = intersections[i]
    # startpoint[0].append(zcurrent)
    intersections.sort(
        key=lambda x: (x[0]['X'] - start['X']) ** 2 + (x[0]['Y'] - start['Y']) ** 2
    )
    startpoint = intersections[0]
    startpoint[0]['Z'] = zcurrent
    # print(toolpath2)
    # end point and perimeter section
    endray = [
        center,
        {
            'X': radius * 1.1 * math.cos(endangle) + center['X'],
            'Y': radius * 1.1 * math.sin(endangle) + center['Y'],
        },
    ]
    intersections = []
    for s in range(0, len(perimeter)):
        inter = cg.LineSegIntersect2D(
            endray, [perimeter_cycle[s], perimeter_cycle[s + 1]], distancetol, angletol
        )
        if inter != 'none':
            if dimlist[0] in inter:
                intersections.append([inter, s])
            elif inter[0] == 'colinear':
                intersections.append([inter[1], s])
                intersections.append([inter[2], s])
    # find intersection point closest to the center
    intersections.sort(
        key=lambda x: (x[0]['X'] - center['X']) ** 2 + (x[0]['Y'] - center['Y']) ** 2
    )
    endpoint = intersections[0]
    endpoint[0]['Z'] = zcurrent
    # print(toolpath2)
    # overlap point an perimeter section
    overlapray = [
        center,
        {
            'X': radius * 1.1 * math.cos(overlap_startangle) + center['X'],
            'Y': radius * 1.1 * math.sin(overlap_startangle) + center['Y'],
        },
    ]
    intersections = []
    for s in range(0, len(perimeter)):
        inter = cg.LineSegIntersect2D(
            overlapray,
            [perimeter_cycle[s], perimeter_cycle[s + 1]],
            distancetol,
            angletol,
        )
        if inter != 'none':
            if dimlist[0] in inter:
                intersections.append([inter, s])
            elif inter[0] == 'colinear':
                intersections.append([inter[1], s])
                intersections.append([inter[2], s])
    # find intersection point closest to the center
    intersections.sort(
        key=lambda x: (x[0]['X'] - center['X']) ** 2 + (x[0]['Y'] - center['Y']) ** 2
    )
    overlappoint = intersections[0]
    overlappoint[0]['Z'] = zcurrent
    # Use the information above to construct the tool paths

    startsegment = startpoint[1]
    opass = 0
    epass = 0
    # print(startangle)
    # print(startpoint)
    # print(overlap_startangle)
    # print(overlappoint)
    # print(endangle)
    # print(endpoint)

    for s in range(0, len(perimeter)):
        # Determine the segment of perimeter is being investigated, starting with start segment
        segment = round((startsegment + (pitch / abs(pitch)) * s) % len(perimeter))
        # Determine start point for this motion
        if toolpath2 == []:
            lstartpoint = startpoint[0]
        else:
            if s == 0:
                toolpath2.append(
                    {
                        'startpoint': toolpath2[len(toolpath2) - 1]['endpoint'],
                        'endpoint': startpoint[0],
                        'material': helixmat,
                    }
                )
            lstartpoint = toolpath2[len(toolpath2) - 1]['endpoint']

        # print (lstartpoint)
        # if the overlap point has not been passed yet
        if opass == 0:
            # if the overlap point is in this segment
            if overlappoint[1] == segment:
                if (pitch / abs(pitch)) > 0:
                    sidestart2overlap = cg.linelength(
                        perimeter_cycle[segment], overlappoint[0]
                    )
                    sidestart2start = cg.linelength(
                        perimeter_cycle[segment], lstartpoint
                    )
                else:
                    sidestart2overlap = cg.linelength(
                        perimeter_cycle[segment + 1], overlappoint[0]
                    )
                    sidestart2start = cg.linelength(
                        perimeter_cycle[segment + 1], lstartpoint
                    )

                if sidestart2overlap > sidestart2start:
                    toolpath2.append(
                        {
                            'startpoint': lstartpoint,
                            'endpoint': overlappoint[0],
                            'material': helixmat,
                        }
                    )
                    opass = 1
                    lstartpoint = overlappoint[0]
            # if the overlap point is not in this segment
            else:
                if (pitch / abs(pitch)) > 0:
                    toolpath2.append(
                        {
                            'startpoint': lstartpoint,
                            'endpoint': perimeter_cycle[segment + 1],
                            'material': helixmat,
                        }
                    )
                else:
                    toolpath2.append(
                        {
                            'startpoint': lstartpoint,
                            'endpoint': perimeter_cycle[segment],
                            'material': helixmat,
                        }
                    )
        if opass == 1 and epass == 0:
            # if the end point is in this segment
            if endpoint[1] == segment:
                toolpath2.append(
                    {
                        'startpoint': lstartpoint,
                        'endpoint': endpoint[0],
                        'material': helixmat,
                    }
                )
                newhistory.append(
                    {
                        'startpoint': lstartpoint,
                        'endpoint': endpoint[0],
                        'material': helixmat,
                    }
                )
                epass = 1
            # if the overlap point is not in this segment
            else:
                if (pitch / abs(pitch)) > 0:
                    toolpath2.append(
                        {
                            'startpoint': lstartpoint,
                            'endpoint': perimeter_cycle[segment + 1],
                            'material': helixmat,
                        }
                    )
                    newhistory.append(
                        {
                            'startpoint': lstartpoint,
                            'endpoint': perimeter_cycle[segment + 1],
                            'material': helixmat,
                        }
                    )
                else:
                    toolpath2.append(
                        {
                            'startpoint': lstartpoint,
                            'endpoint': perimeter_cycle[segment],
                            'material': helixmat,
                        }
                    )
                    newhistory.append(
                        {
                            'startpoint': lstartpoint,
                            'endpoint': perimeter_cycle[segment],
                            'material': helixmat,
                        }
                    )
    if first == 1:
        history.append(newhistory)
        # print(helixid, newhistory)
        return toolpath2

    # Construct first structural part
    # old overlap point an perimeter section
    if len(history[helixid]) == 1:
        ooverlappt = history[helixid][0]['startpoint']
    else:
        ooverlappt = history[helixid][0]['startpoint']

    ooverlapangle = math.atan2(
        ooverlappt['Y'] - center['Y'], ooverlappt['X'] - center['X']
    )
    ooverlapray = [
        center,
        {
            'X': radius * 1.1 * math.cos(ooverlapangle) + center['X'],
            'Y': radius * 1.1 * math.sin(ooverlapangle) + center['Y'],
        },
    ]

    intersections = []
    for s in range(0, len(perimeter)):
        inter = cg.LineSegIntersect2D(
            ooverlapray,
            [perimeter_cycle[s], perimeter_cycle[s + 1]],
            distancetol,
            angletol,
        )
        if inter != 'none':
            if dimlist[0] in inter:
                intersections.append([inter, s])
            elif inter[0] == 'colinear':
                intersections.append([inter[1], s])
                intersections.append([inter[2], s])
    # find intersection point closest to known start
    # for i in range(0,len(intersections)):
    #    if ptalmostequal([intersections[i][0][0],intersections[i][0][1]], [ooverlappt[0],ooverlappt[1]],distancetol):
    #        ooverlappoint = intersections[i]
    # ooverlappoint[0].append(zcurrent)
    intersections.sort(
        key=lambda x: (x[0]['X'] - ooverlappt['X']) ** 2
        + (x[0]['Y'] - ooverlappt['Y']) ** 2
    )
    ooverlappoint = intersections[0]
    ooverlappoint[0]['Z'] = zcurrent

    # print (ooverlappoint)
    startsegment = startpoint[1]
    oopass = 0
    # print(perimeter_cycle)
    for s in range(0, len(perimeter) + 1):
        # Determine the segment of perimeter is being investigated, starting with start segment
        segment = round((startsegment + (pitch / abs(pitch)) * s) % len(perimeter))
        # print(segment)
        # Determine start point for this motion
        if toolpath1 == []:
            lstartpoint = startpoint[0]
        else:
            lstartpoint = toolpath1[len(toolpath1) - 1]['endpoint']
        # if the overlap point has not been passed yet
        if oopass == 0:
            # if the overlap point is in this segment
            if ooverlappoint[1] == segment:
                if (pitch / abs(pitch)) > 0:
                    sidestart2overlap = cg.linelength(
                        perimeter_cycle[segment], overlappoint[0]
                    )
                    sidestart2start = cg.linelength(
                        perimeter_cycle[segment], lstartpoint
                    )
                else:
                    sidestart2overlap = cg.linelength(
                        perimeter_cycle[segment + 1], overlappoint[0]
                    )
                    sidestart2start = cg.linelength(
                        perimeter_cycle[segment + 1], lstartpoint
                    )

                # Check to make sure the order is good
                if sidestart2overlap > sidestart2start:
                    toolpath1.append(
                        {
                            'startpoint': lstartpoint,
                            'endpoint': ooverlappoint[0],
                            'material': supmat,
                        }
                    )
                    oopass = 1
                else:
                    if (pitch / abs(pitch)) > 0:
                        toolpath1.append(
                            {
                                'startpoint': lstartpoint,
                                'endpoint': perimeter_cycle[segment + 1],
                                'material': supmat,
                            }
                        )
                    else:
                        toolpath1.append(
                            {
                                'startpoint': lstartpoint,
                                'endpoint': perimeter_cycle[segment],
                                'material': supmat,
                            }
                        )
            # if the overlap point is not in this segment
            else:
                if (pitch / abs(pitch)) > 0:
                    toolpath1.append(
                        {
                            'startpoint': lstartpoint,
                            'endpoint': perimeter_cycle[segment + 1],
                            'material': supmat,
                        }
                    )
                else:
                    toolpath1.append(
                        {
                            'startpoint': lstartpoint,
                            'endpoint': perimeter_cycle[segment],
                            'material': supmat,
                        }
                    )

    # Construct second structural part
    startsegment = startpoint[1]
    oopass = 0
    for s in range(0, len(perimeter)):
        # Determine the segment of perimeter is being investigated, starting with start segment
        segment = round((startsegment - (pitch / abs(pitch)) * s) % len(perimeter))
        # Determine start point for this motion
        if toolpath3 == []:
            lstartpoint = startpoint[0]
        else:
            lstartpoint = toolpath3[len(toolpath3) - 1]['endpoint']
        # if the overlap point has not been passed yet
        if oopass == 0:
            # if the overlap point is in this segment
            if ooverlappoint[1] == segment:
                toolpath3.append(
                    {
                        'startpoint': lstartpoint,
                        'endpoint': ooverlappoint[0],
                        'material': supmat,
                    }
                )
                oopass = 1
            # if the overlap point is not in this segment
            else:
                if (pitch / abs(pitch)) > 0:
                    toolpath3.append(
                        {
                            'startpoint': lstartpoint,
                            'endpoint': perimeter_cycle[segment],
                            'material': supmat,
                        }
                    )
                else:
                    toolpath3.append(
                        {
                            'startpoint': lstartpoint,
                            'endpoint': perimeter_cycle[segment + 1],
                            'material': supmat,
                        }
                    )
    history[helixid] = newhistory
    # print(helixid, newhistory)
    return [*toolpath1, *toolpath2, *toolpath3]


def shiftarray(array, shiftx, shifty):
    sarray = copy.deepcopy(array)
    for m in range(0, len(array)):
        for n in range(0, len(array[0])):
            sarray[m][n] = [
                array[m][n][0] - array[shiftx][shifty][0],
                array[m][n][1] - array[shiftx][shifty][1],
            ]

    return sarray


def hexpt2toolpath_ground(point_matrix, material):
    toolpath = []
    maxm = len(point_matrix)
    maxn = len(point_matrix[0])
    # postive slope lines
    alternation1 = 1

    for p in range(0, math.floor(maxm / 2)):
        n = 0
        m = 2 * p + 1
        if alternation1 == -1:
            newm = m + 2
            newn = n + 1
            alternation2 = 1
        elif alternation1 == 1:
            newm = m + 1
            newn = n + 0
            alternation2 = -1
        while newn < maxn and newm < maxm:
            toolpath.append(
                {
                    'startpoint': tpt.list2XY(point_matrix[m][n]),
                    'endpoint': tpt.list2XY(point_matrix[newm][newn]),
                    'material': material,
                }
            )
            m = newm
            n = newn
            if alternation2 == -1:
                newm = m + 2
                newn = n + 1
            elif alternation2 == 1:
                newm = m + 1
                newn = n + 0
            alternation2 = -alternation2

    alternation1 = 0
    startm = 0
    startn = 0
    while n < maxn and m < maxm:
        m = startm
        n = startn
        if alternation1 == 0:
            newm = startm + 2
            newn = startn + 1
            alternation2 = 1
        elif alternation1 == 1:
            newm = startm + 1
            newn = startn + 0
            alternation2 = -1
        elif alternation1 == 2:
            newm = startm + 1
            newn = startn + 0
            alternation2 = -1
        while newn < maxn and newm < maxm:
            toolpath.append(
                {
                    'startpoint': tpt.list2XY(point_matrix[m][n]),
                    'endpoint': tpt.list2XY(point_matrix[newm][newn]),
                    'material': material,
                }
            )
            m = newm
            n = newn
            if alternation2 == -1:
                newm = m + 2
                newn = n + 1
            elif alternation2 == 1:
                newm = m + 1
                newn = n + 0
            alternation2 = -alternation2
        if alternation1 == 0:
            startm += 0
            startn += 1
            alternation1 += 1
        elif alternation1 == 1:
            startm += 1
            startn += 1
            alternation1 += 1
        elif alternation1 == 2:
            startm += -1
            startn += 0
            alternation1 = 0

    # negative slope lines
    alternation1 = 1

    for p in range(0, math.floor(maxm / 2)):
        n = 0
        m = 2 * p + 1
        if alternation1 == -1:
            newm = m + 2
            newn = n + 1
            alternation2 = 1
        elif alternation1 == 1:
            newm = m - 1
            newn = n + 0
            alternation2 = -1
        while newn < maxn and newm >= 0:
            toolpath.append(
                {
                    'startpoint': tpt.list2XY(point_matrix[m][n]),
                    'endpoint': tpt.list2XY(point_matrix[newm][newn]),
                    'material': material,
                }
            )
            m = newm
            n = newn
            if alternation2 == -1:
                newm = m - 2
                newn = n + 1
            elif alternation2 == 1:
                newm = m - 1
                newn = n + 0
            alternation2 = -alternation2

    alternation1 = 2
    startm = maxm - 2
    startn = 1

    while n < maxn and m < maxm:
        m = startm
        n = startn
        if alternation1 == 0:
            newm = startm - 2
            newn = startn + 1
            alternation2 = 1
        elif alternation1 == 1:
            newm = startm - 1
            newn = startn + 0
            alternation2 = -1
        elif alternation1 == 2:
            newm = startm - 1
            newn = startn + 0
            alternation2 = -1
        while newn < maxn and newm >= 0:
            toolpath.append(
                {
                    'startpoint': tpt.list2XY(point_matrix[m][n]),
                    'endpoint': tpt.list2XY(point_matrix[newm][newn]),
                    'material': material,
                }
            )
            m = newm
            n = newn
            if alternation2 == -1:
                newm = m - 2
                newn = n + 1
            elif alternation2 == 1:
                newm = m - 1
                newn = n + 0
            alternation2 = -alternation2
        if alternation1 == 0:
            startm += 0
            startn += 1
            alternation1 += 1
        elif alternation1 == 1:
            startm += -1
            startn += 1
            alternation1 += 1
        elif alternation1 == 2:
            startm += 1
            startn += 0
            alternation1 = 0

    # Verticle line
    for p in range(1, maxm - 1):
        n = 0
        m = p
        newn = n + 1
        newm = m
        while newn < maxn:
            toolpath.append(
                {
                    'startpoint': tpt.list2XY(point_matrix[m][n]),
                    'endpoint': tpt.list2XY(point_matrix[newm][newn]),
                    'material': material,
                }
            )
            m = newm
            n = newn
            newn = n + 1
            newm = m

    return toolpath
