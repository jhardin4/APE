import copy
import math
import matplotlib.pyplot as plt
import csv
import ToolPathGeneration.CompGeo as cg
import json

# Toolpath structure
# {'startpoint': [XY] or [XYZ], 'endpoint': [XY] or [XYZ], 'material' : string}
# {'parse':string}
# All start and end points should be the same dimensionality

# Plot formatting
# {'material':material, 'color': colorcode, 'linestyle': lscode, 'linewidth': linewdith, 'alpha':alphavalue}


# -----------------------------FUNCTIONS---------------------------------#
def TPdeepcopy(toolpath):
    copyTP = []
    for line in toolpath:
        copyTP.append(copy.deepcopy(line))

    return copyTP


def Toolpath2Dto3D(path2D, zvalue):
    # Convert an [XY] toolpath to at [XYZ] toolpath with the same z-value

    # making a working copy of path2D
    path = TPdeepcopy(path2D)
    for line in path:
        linekeys = str(line.keys())
        if 'startpoint' in linekeys:
            line['startpoint']['Z'] = zvalue
            line['endpoint']['Z'] = zvalue

    return path


def plottoolpaths(paths, materials, newfigure=True):
    # paths is of a standard toolpath structure 2D or 3D
    # is of form [identifier, color designator, line style designator, linewidth, alpha]

    # Determine toolpath dimension
    dim = 0
    n = 0
    while dim == 0:
        if n > len(paths) - 1:
            dim = 'none'
        else:
            linekeys = str(paths[n].keys())
            if 'startpoint' in linekeys:
                dim = len(paths[n]['startpoint'])
            n += 1

    # Fail out if nothing is a recognized motion
    if dim == 'none':
        return 'No motions'

    # Create a new figure
    if newfigure:
        if dim == 2:
            plt.figure()

        if dim == 3:
            plt.figure().add_subplot(111, projection='3d')

    for line in paths:
        linekeys = str(line.keys())
        if 'startpoint' in linekeys:
            # get formatting
            for material in materials:
                if line['material'] == material['material']:
                    # 'color': colorcode, 'linestyle': lscode, 'linewidth': linewdith, 'alpha':alphavalue}
                    gcolor = material['color']
                    gls = material['linestyle']
                    gwidth = material['linewidth']
                    galpha = material['alpha']

                    if dim == 2:
                        tempx = [line['startpoint']['X'], line['endpoint']['X']]
                        tempy = [line['startpoint']['Y'], line['endpoint']['Y']]
                        plt.plot(
                            tempx,
                            tempy,
                            color=gcolor,
                            ls=gls,
                            linewidth=gwidth,
                            alpha=galpha,
                        )
                    if dim == 3:
                        tempx = [line['startpoint']['X'], line['endpoint']['X']]
                        tempy = [line['startpoint']['Y'], line['endpoint']['Y']]
                        tempz = [line['startpoint']['Z'], line['endpoint']['Z']]
                        plt.plot(
                            tempx,
                            tempy,
                            tempz,
                            color=gcolor,
                            ls=gls,
                            linewidth=gwidth,
                            alpha=galpha,
                        )


def loadTP_json(filepath):
    with open(filepath, 'r') as TPjson:
        data = json.load(TPjson)

    return data


def saveTP_json(tpath, filepath):
    with open(filepath, 'w') as TPjson:
        json.dump(tpath, TPjson)


def saveTP_csv(tpath, filepath):
    tpathlist = []
    for line in tpath:
        linekeys = str(line.keys())
        if 'startpoint' in linekeys:
            tpathline = []
            for dim in line['startpoint']:
                tpathline.append(dim)
            for dim in line['endpoint']:
                tpathline.append(dim)
            tpathline.append(line['material'])
            tpathlist.append(tpathline)

    if len(tpathlist[0]) == 5:
        headers = ['startX', 'startY', 'endX', 'endY', 'material']

    if len(tpathlist[0]) == 7:
        headers = ['startX', 'startY', 'startZ', 'endX', 'endY', 'endZ', 'material']

    with open(filepath, mode='w', newline='') as TPcsv:
        writer = csv.writer(TPcsv)
        writer.writerow(headers)
        writer.writerows(tpathlist)


def toolpcut(toolpath, boundry, keepoutside, distancetol, angletol):
    # Makes deepcopy of toolpath which will hold the motions that will survive the cut in some form
    temppath1 = TPdeepcopy(toolpath)

    # Construct boundary
    boundry_cycle = boundry[:]
    boundry_cycle.append(boundry[0])

    # Track number of lines cut
    cuts = 0  # initialize the number of lines cut

    # find and remove motion completely outside the region
    # Iterate through each line by line number
    for line in range(0, len(toolpath)):
        linekeys = str(toolpath[line].keys())
        # check if this is a motion line
        if 'startpoint' in linekeys:
            intersections = []  # reset intersections
            point1all = 0  # reset all intersect indicator for start point
            point2all = 0  # reset all intersect indicator for end point

            # check if the end points of a particular motion are within the region
            # pointinregion counts points on boundary as NOT in region
            inregion1 = cg.pointinregion(
                toolpath[line]['startpoint'], boundry, distancetol, angletol
            )
            inregion2 = cg.pointinregion(
                toolpath[line]['endpoint'], boundry, distancetol, angletol
            )

            # Collect intersection with boundary that are not colinear
            for b in range(0, len(boundry)):
                borderwall = [boundry_cycle[b], boundry_cycle[b + 1]]
                toolpathline = [
                    toolpath[line]['startpoint'],
                    toolpath[line]['endpoint'],
                ]
                intest = cg.LineSegIntersect2D(
                    toolpathline, borderwall, distancetol, angletol
                )
                # Look for true intersections
                dimlist = list(boundry[0].keys())
                if dimlist[0] in intest:
                    intersections.append(intest)

            # print('Before ' +str(intersections))
            # remove repeats
            tempintest = []
            for element in intersections:
                unique = True
                for unique_element in tempintest:
                    if cg.ptalmostequal(unique_element, element, distancetol):
                        unique = False

                if unique:
                    tempintest.append(element)

            intersections = tempintest
            # print('After ' +str(intersections))
            # check for point intersections with boundary
            # make copies of the intersection list
            tempintest1 = copy.deepcopy(intersections)
            tempintest2 = copy.deepcopy(intersections)
            # reset cut trackers
            cuts1 = 0
            cuts2 = 0

            if len(intersections) != 0:
                # iterate though intersection list
                for w in range(0, len(intersections)):
                    # check for intersections that are equal to the end points of motion
                    if cg.ptalmostequal(
                        toolpath[line]['startpoint'], intersections[w], distancetol
                    ):
                        # remove intersections from copy1 which are identical to start point
                        del tempintest1[w - cuts1]
                        cuts1 = cuts1 + 1
                    if cg.ptalmostequal(
                        toolpath[line]['endpoint'], intersections[w], distancetol
                    ):
                        # remove intersections from copy2 which are idential to end point
                        del tempintest2[w - cuts2]
                        cuts2 = cuts2 + 1
                # If copy1 or copy2 lists are empty then set indicator for endpoint intesection with boundary
                if len(tempintest1) == 0:
                    point1all = 1
                if len(tempintest2) == 0:
                    point2all = 1

            # A motion to be completely removed must have one of the following
            # 1. inregion1 and inregion2 = outvalue and there are no intersections
            # 2. outvalue = 1 and inregion1 or inregion2 = outvalue and all intersection equal the end point where inregion = 0
            # 3. outvalue = 0 and all intersections equal one of the motion endpoints
            '''
            keepoutside  inregion1  inregion2  point1all  point2all  len(intersections)==0
                T           T          T           0         0              T
                F           F          F           0         0              T
                F           F          F
            '''
            # if both of the he endpoints of the motion are in the region being removed
            if inregion1 == keepoutside and inregion2 == keepoutside:
                # remove motions satisfying condition 1 (no intersection)
                if len(intersections) == 0:
                    del temppath1[line - cuts]
                    cuts = cuts + 1
                # remove motions satisfying condition 3 (only applied when keeping inside)
                elif keepoutside is False:
                    # if one end is outside the region and the other is in the border though counted as being outside
                    if (point1all == 1 and point2all == 0) or (
                        point1all == 0 and point2all == 1
                    ):
                        del temppath1[line - cuts]
                        cuts = cuts + 1
            # remove motions satisfy condition 2
            if keepoutside is True:
                if inregion1 is False and inregion2 is True and point1all == 1:
                    del temppath1[line - cuts]
                    cuts = cuts + 1
                if inregion1 is True and inregion2 is False and point2all == 1:
                    del temppath1[line - cuts]
                    cuts = cuts + 1
                '''
                if inregion1 == False and inregion2 == False and len(tempintest1) == 1 and cg.ptalmostequal(toolpath[line]['endpoint'], tempintest1[0], distancetol) :
                    del(temppath1[line-cuts])
                    cuts = cuts + 1
                '''
    # Make another working copy to clean any complicating pointing
    temppath2 = copy.deepcopy(temppath1)
    motionadds = 0  # initialize the number of lines added

    # Cut back intersecting lines
    for line in range(0, len(temppath1)):
        # Check for intersections with boundary
        intersections = []
        for b in range(0, len(boundry)):
            borderwall = [boundry_cycle[b], boundry_cycle[b + 1]]
            temppath1line = [temppath1[line]['startpoint'], temppath1[line]['endpoint']]
            intest = cg.LineSegIntersect2D(
                temppath1line, borderwall, distancetol, angletol
            )
            # Construct list of intersections, both normal and colinear
            if intest != 'none':
                intersections.append(intest)
        # Break up motion across boundry
        # check if motion intersects
        inregion1 = cg.pointinregion(
            temppath1[line]['startpoint'], boundry, distancetol, angletol
        )
        inregion2 = cg.pointinregion(
            temppath1[line]['endpoint'], boundry, distancetol, angletol
        )
        # print(inregion1,inregion2, p,q)
        if intersections != []:

            # line startin boundry and moving out of printed region should have already been removed

            # Collect all intersection including colinear ones
            newintersections = []
            dimlist = list(boundry[0].keys())
            for e in range(0, len(intersections)):
                if dimlist[0] in intersections[e]:
                    newintersections.append(intersections[e])
                elif intersections[e][0] == 'colinear':
                    newintersections.append(intersections[e][1])
                    newintersections.append(intersections[e][2])

            intersections = newintersections

            # sort by distance from startpoint
            intersections.sort(
                key=lambda x: (
                    x[dimlist[0]] - temppath1[line]['startpoint'][dimlist[0]]
                )
                ** 2
                + (x[dimlist[1]] - temppath1[line]['startpoint'][dimlist[1]]) ** 2
            )
            # check if motion starts in boundry or on edge then set starting state of motion
            # print(str(intersections[0]) +' ' + str(temppath1[line]['startpoint']))
            if inregion1 is True or cg.ptalmostequal(
                intersections[0], temppath1[line]['startpoint'], distancetol
            ):
                start = not keepoutside
            else:
                start = keepoutside
            # if start of motion is on boundry then remove that point from the intercept list to avoid double counting it
            # print(intersections)

            # if the motion starts on
            if start is True:
                # add the start point to the pointlist
                pointlist = [temppath1[line]['startpoint']]
            # if the motion starts off
            else:
                pointlist = []

            # add all the remaining intersection points that are not equal to the end or start points
            for e in range(0, len(intersections)):
                if (
                    not cg.ptalmostequal(
                        intersections[e], temppath1[line]['startpoint'], distancetol
                    )
                ) and (
                    not cg.ptalmostequal(
                        intersections[e], temppath1[line]['endpoint'], distancetol
                    )
                ):
                    pointlist.append(intersections[e])

            # add the motion end point
            pointlist.append(temppath1[line]['endpoint'])

            # sort the list based on distance from start of motion
            dimlist = list(pointlist[0].keys())
            pointlist.sort(
                key=lambda x: (
                    x[dimlist[0]] - temppath1[line]['startpoint'][dimlist[0]]
                )
                ** 2
                + (x[dimlist[1]] - temppath1[line]['startpoint'][dimlist[1]]) ** 2
            )

            # remove repeated values
            newpointlist = [pointlist[0]]
            cuts = 0
            for e in range(1, len(pointlist)):
                if not cg.ptalmostequal(pointlist[e], pointlist[e - 1], distancetol):
                    newpointlist.append(pointlist[e])
            pointlist = newpointlist
            # print(pointlist)
            # print(inregion1, start, pointlist)
            for i in range(0, len(pointlist)):
                # Alternate lines
                if i % 2 == 1:
                    # modify the first line
                    if i == 1:
                        temppath2[line + motionadds]['startpoint'] = pointlist[i - 1]
                        temppath2[line + motionadds]['endpoint'] = pointlist[i]
                    else:
                        tempmotion = {
                            'startpoint': pointlist[i - 1],
                            'endpoint': pointlist[i],
                            'material': temppath2[line + motionadds]['material'],
                        }
                        temppath2.insert(line + 1 + motionadds, tempmotion)
                        motionadds = motionadds + 1

    return temppath2


def cleanpaths(toolpath, distancetol):
    # Clean up tool paths after cutting
    # Remove dead motions
    cleanedpath0 = copy.deepcopy(toolpath)

    for p in range(0, len(toolpath)):
        qcuts = 0
        for q in range(0, len(toolpath[p])):
            if cg.ptalmostequal(toolpath[p][q][0], toolpath[p][q][1], distancetol):
                del cleanedpath0[p][q - qcuts]
                qcuts = qcuts + 1

    cleanedpath1 = copy.deepcopy(cleanedpath0)

    # remove empty paths
    pcuts = 0
    for p in range(0, len(cleanedpath0)):
        if cleanedpath0[p] == []:
            del cleanedpath1[p - pcuts]
            pcuts = pcuts + 1

    # Seperate broken baths into independent paths
    cleanedpath2 = copy.deepcopy(cleanedpath1)
    padds = 0
    for p in range(0, len(cleanedpath1)):
        t = 1
        for q in range(1, len(cleanedpath1[p])):
            if len(cleanedpath2) > 1:
                if not cg.ptalmostequal(
                    cleanedpath2[p + padds][t - 1][1],
                    cleanedpath2[p + padds][t][0],
                    distancetol,
                ):
                    # construct residual
                    temppath = []
                    for r in range(t, len(cleanedpath2[p + padds])):
                        temppath.append(cleanedpath2[p + padds].pop(t))
                    cleanedpath2.insert(p + padds + 1, temppath)
                    padds = padds + 1
                    t = 0
                t = t + 1

    # Remove non-printing toolpaths
    cleanedpath3 = copy.deepcopy(cleanedpath2)
    pcut = 0
    for p in range(0, len(cleanedpath2)):
        psum = 0
        for q in range(0, len(cleanedpath2[p])):
            psum = psum + cleanedpath2[p][q][2]
        if psum == 0:
            del cleanedpath3[p - pcut]
            pcut = pcut + 1
    return cleanedpath3


def toolpathplotter3D(toolpath):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Z (mm)')
    # check if the structure is already a single list
    depth = 0
    temp = 0
    # if it is a single toolpath then each element has 3 components (2 points and a material) and the first two of those elements also has 3 (XYZ)
    for p in range(0, len(toolpath)):
        if not (
            len(toolpath[p]) == 3
            and len(toolpath[p][0]) == 3
            and len(toolpath[p][1]) == 3
        ):
            temp = temp + 1
    # if this is not true for even one element then there is a problem.  It is probably jsut a dimensionality of the matrix
    depth = math.ceil(temp / len(toolpath))

    # List of tool paths
    temp = 0
    total = 0
    if depth == 1:
        for p in range(0, len(toolpath)):
            for q in range(0, len(toolpath[p])):
                total = total + len(toolpath[p])
                if not (
                    len(toolpath[p][q]) == 3
                    and len(toolpath[p][q][0]) == 3
                    and len(toolpath[p][q][1]) == 3
                ):
                    temp = temp + 1
        depth = depth + math.ceil(temp / total)

    # A layer with multiple toolpaths in each layer
    temp = 0
    total = 0
    if depth == 2:
        for p in range(0, len(toolpath)):
            for q in range(0, len(toolpath[p])):
                for r in range(0, len(toolpath[p][q])):
                    total = total + len(toolpath[p][q])
                    if not (
                        len(toolpath[p][q][r]) == 3
                        and len(toolpath[p][q][r][0]) == 3
                        and len(toolpath[p][q][r][1]) == 3
                    ):
                        temp = temp + 1
        depth = depth + math.ceil(temp / total)

    if not (depth == 0 or depth == 1 or depth == 2):
        # print(depth)
        return 'wrong structure'
    # convert to a single depth structure
    if depth == 1:
        newtoolpath = []
        for p in range(0, len(toolpath)):
            for q in range(0, len(toolpath[p])):
                newtoolpath.append(toolpath[p][q])

        toolpath = newtoolpath
    if depth == 2:
        newtoolpath = []
        for p in range(0, len(toolpath)):
            for q in range(0, len(toolpath[p])):
                for r in range(0, len(toolpath[p][q])):
                    newtoolpath.append(toolpath[p][q][r])

        toolpath = newtoolpath

    for h in range(0, len(toolpath)):
        xtemp = [toolpath[h][0][0], toolpath[h][1][0]]
        ytemp = [toolpath[h][0][1], toolpath[h][1][1]]
        ztemp = [toolpath[h][0][2], toolpath[h][1][2]]
        if toolpath[h][2] == 0 or toolpath[h][2] == 0.5:
            ax.plot(xtemp, ytemp, ztemp, color='r', ls=":", linewidth=1, alpha=0.5)
        elif toolpath[h][2] == 1:
            ax.plot(xtemp, ytemp, ztemp, color='b', linewidth=5, alpha=0.2)
        elif toolpath[h][2] == 2:
            ax.plot(xtemp, ytemp, ztemp, color='k', linewidth=1, alpha=1)

    # plt.show()
    # plt.savefig('Step5.png',dpi = 600 )


def cleanpaths3D(toolpath):
    # Clean up tool paths after cutting
    # Remove dead motions
    cleanedpath0 = copy.deepcopy(toolpath)

    for p in range(0, len(toolpath)):
        qcuts = 0
        for q in range(0, len(toolpath[p])):
            if toolpath[p][q][0] == toolpath[p][q][1]:
                del cleanedpath0[p][q - qcuts]
                qcuts = qcuts + 1

    cleanedpath1 = copy.deepcopy(cleanedpath0)

    # remove empty paths
    pcuts = 0
    for p in range(0, len(cleanedpath0)):
        if cleanedpath0[p] == []:
            del cleanedpath1[p - pcuts]
            pcuts = pcuts + 1

    # Seperate broken baths into independent paths
    cleanedpath2 = copy.deepcopy(cleanedpath1)
    padds = 0
    for p in range(0, len(cleanedpath1)):
        t = 1
        for q in range(1, len(cleanedpath1[p])):
            if len(cleanedpath2) > 1:
                if cleanedpath2[p + padds][t - 1][1] != cleanedpath2[p + padds][t][0]:
                    # construct residual
                    temppath = []
                    for r in range(t, len(cleanedpath2[p + padds])):
                        temppath.append(cleanedpath2[p + padds].pop(t))
                    cleanedpath2.insert(p + padds + 1, temppath)
                    padds = padds + 1
                    t = 0
                t = t + 1

    # Remove non-printing toolpaths
    cleanedpath3 = copy.deepcopy(cleanedpath2)
    pcut = 0
    for p in range(0, len(cleanedpath2)):
        psum = 0
        for q in range(0, len(cleanedpath2[p])):
            psum = psum + cleanedpath2[p][q][2]
        if psum == 0:
            del cleanedpath3[p - pcut]
            pcut = pcut + 1
    return cleanedpath3


def buildexporter_anigif(toolpath, images, rotations, materials):
    framelength = math.floor(len(toolpath) / images)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Z (mm)')
    materials1 = copy.deepcopy(materials)
    for m in range(0, len(materials1)):
        materials1[m]['alpha'] = materials[m]['alpha'] * 0.5
    materials2 = copy.deepcopy(materials1)
    for m in range(0, len(materials2)):
        materials2[m]['alpha'] = materials1[m]['alpha'] * 0.25

    for p in range(0, images):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.set_zlabel('Z (mm)')
        ax.set_zlim([0, 17])
        ax.set_xlim([-5, 60])
        ax.set_ylim([-15, 50])
        plottoolpaths(
            toolpath[: math.floor(0.5 * p * framelength)], materials2, newfigure=False
        )
        plottoolpaths(
            toolpath[
                math.floor(0.5 * p * framelength) : math.floor(0.9 * p * framelength)
            ],
            materials1,
            newfigure=False,
        )
        plottoolpaths(
            toolpath[math.floor(0.9 * p * framelength) : p * framelength],
            materials,
            newfigure=False,
        )
        ax.view_init(elev=30, azim=360 / images * rotations * p)
        tempfname = 'step' + str(p) + '.png'
        plt.savefig(tempfname, dpi=100)
        plt.close()
        plt.clf()


def pntplot2D(points, pcolor='k', newplot=True):
    if newplot:
        plt.figure()
    for element in points:
        try:
            len(element[0])
            pntplot2D(element, pcolor=pcolor, newplot=False)
        except TypeError:
            plt.scatter(element[0], element[1], color=pcolor)


def pntlabel2D(points, index=[], newplot=True):
    if newplot:
        plt.figure()
    for m in range(0, len(points)):
        for n in range(0, len(points[m])):
            label = '(' + str(m) + ',' + str(n) + ')'
            plt.annotate(
                label,
                xy=(points[m][n][0], points[m][n][1]),
                xytext=(7, -3),
                textcoords='offset points',
            )


def plotborder(border, pcolor='k', newplot=True):
    if newplot:
        plt.figure()
    bordercycle = copy.deepcopy(border)
    bordercycle.append(bordercycle[0])
    for p in range(0, len(border)):
        tempx = [bordercycle[p][0], bordercycle[p + 1][0]]
        tempy = [bordercycle[p][1], bordercycle[p + 1][1]]
        plt.plot(tempx, tempy, color=pcolor)


def parse_endofmotion(toolpath, disttol):
    # adds an endofmotion parse at the end of a continuous motion regardless of material
    parsed_TP = []
    prevmotion = []
    lastmotion = 0
    parsecounter = 0
    for l in range(0, len(toolpath)):
        # check if this is a motion line
        linekeys = list(toolpath[l].keys())
        if 'startpoint' in linekeys:
            # Handle search for first motion
            if prevmotion == []:
                prevmotion = toolpath[l]
            # If there is a break in the motions
            elif not cg.ptalmostequal(
                prevmotion['endpoint'], toolpath[l]['startpoint'], disttol
            ):
                parsed_TP.append({'parse': 'endofmotion', 'motion': prevmotion})
                lastmotion += 1

            prevmotion = toolpath[l]
            lastmotion += parsecounter + 1
            parsecounter = 0
            # track position of last motion
        else:
            parsecounter += 1
        parsed_TP.append(toolpath[l])
    # handle last motion
    prevmotion = parsed_TP[lastmotion - 1]
    parsed_TP.insert(lastmotion, {'parse': 'endofmotion', 'motion': prevmotion})

    return parsed_TP


def firstmotion(toolpath, startindex):
    m = startindex
    motion = False
    while motion is False:
        linekeys = list(toolpath[m].keys())
        if 'startpoint' in linekeys:
            motion = True
        m = m + 1
        if m == len(toolpath):
            return 'none found'
    return m - 1


def parse_startofmotion(toolpath, startline='none', findstart=True):
    # adds a startofmotion parse at the beginning of a continuous motion regardless of material using "endofmotion" parses
    parsed_TP = TPdeepcopy(toolpath)
    parseadds = 0
    prev_endofmotion = startline

    if findstart:
        # find first motion
        prev_endofmotion = max(0, firstmotion(toolpath, 0) - 1)

    for l in range(0, len(toolpath)):
        # check if this is a parse line
        linekeys = list(toolpath[l].keys())
        if 'parse' in linekeys:
            if toolpath[l]['parse'] == 'endofmotion':
                nextmotion = firstmotion(toolpath, prev_endofmotion)
                startmotion = toolpath[nextmotion]
                parsed_TP.insert(
                    prev_endofmotion + parseadds + 1,
                    {'parse': 'startofmotion', 'motion': startmotion},
                )
                parseadds += 1
                prev_endofmotion = l

    return parsed_TP


def parse_changemat(toolpath):
    # adds a changemat into motions defined according to endofmotion
    parsed_TP = []
    prevline = []
    for line in toolpath:
        linekeys = str(line.keys())
        # handle first line
        if prevline == []:
            prevline = line
        elif 'startpoint' in linekeys:
            plinekeys = list(prevline.keys())
            if 'startpoint' in plinekeys:
                if prevline['material'] != line['material']:
                    parsed_TP.append(
                        {
                            'parse': 'changemat',
                            'startmotion': prevline,
                            'endmotion': line,
                        }
                    )
        prevline = line
        parsed_TP.append(line)

    return parsed_TP


def parse_heirarchy(toolpath, heirarchy):
    parsed_TP = []
    storedlines = []
    for line in toolpath:
        linekeys = list(line.keys())
        # store up parse lines until there is a move line
        if 'parse' in linekeys:
            storedlines.append(line)
        # Once there is a move line, append the parsed lines in the correct order
        else:
            if len(storedlines) == 1:
                parsed_TP.append(storedlines[0])
                storedlines = []
            elif len(storedlines) > 1:
                for ptype in heirarchy:
                    for parse in storedlines:
                        if parse['parse'] == ptype:
                            parsed_TP.append(parse)
                storedlines = []
            parsed_TP.append(line)
    # clean up the stored parse statements
    for ptype in heirarchy:
        for parse in storedlines:
            if parse['parse'] == ptype:
                parsed_TP.append(parse)

    return parsed_TP


def parse_runs(proclist, motionname, task=1):
    # adds a changemat into motions defined according to endofmotion
    parsed_TP = []
    loadedline = False
    for line in proclist:
        if 'device' in line and line['device'] == motionname:
            loadedline = True
        elif loadedline:
            parsed_TP.append({'device': motionname, 'process': 'Run', 'task': task})
            loadedline = False
        parsed_TP.append(line)

    return parsed_TP


def replace_mat(old_mat, new_mat, toolpath):
    for line in toolpath:
        linekeys = list(line.keys())
        if 'material' in linekeys:
            if line['material'] == old_mat:
                line['material'] = new_mat


def expandpoints(toolpath, pointkeys, dimkeys):
    expandedTP = []
    for line in toolpath:
        linekeys = list(line.keys())
        for pointkey in pointkeys:
            if pointkey in linekeys:
                n = 0
                expandedpoint = {}
                for dimkey in dimkeys:
                    expandedpoint[dimkey] = line[pointkey][n]
                    n += 1
                line[pointkey] = expandedpoint
        expandedTP.append(line)
    return expandedTP


def list2XY(XYlist):
    point = {}
    dimlist = ['X', 'Y']
    for l in range(0, len(XYlist)):
        point[dimlist[l]] = XYlist[l]

    return point
