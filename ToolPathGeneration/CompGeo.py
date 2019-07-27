import math

# Set of simple 2D computational geometry functions for working with lines defined by two points
# Point-to-point comparisons are made somwhat fuzzy by a tolerance value in the ptalmostequal function


# -----------------------------FUNCTIONS---------------------------------#
def almostequal(num1, num2, tol):
    # num1 and num2 are numbers
    # tol is the resolution of the difference of those numbers
    # If num1 and num2 are within (exclusive) tol of eachother then it returns TRUE.
    if tol > abs(num1 - num2):
        return True
    else:
        return False


def ptalmostequal(pt1, pt2, tol):
    # pt1 and pt2 can be of any dimensional points
    # tol is the resolution limit for discerning two points
    # If pt1 and pt2 are within (exclusive) tol of each other then it returns TRUE.
    # Calculate distance between points and compare to tolerance
    sumsqr = 0
    for dim in pt1:
        try:
            sumsqr += (pt2[dim] - pt1[dim]) ** 2
        except Exception:
            print('dimension {}'.format(dim))
            print('Point1 {}'.format(pt1))
            print('Point1 {}'.format(pt2))
            raise Exception('exit')
    if sumsqr < tol ** 2:
        return True
    else:
        return False


def linelength(pt1, pt2):
    # pt1 and pt2 are points of the same dimensions
    linelength2 = 0
    for dim in pt1:
        try:
            linelength2 += (pt1[dim] - pt2[dim]) ** 2
        except Exception:
            print('dimension {}'.format(dim))
            print('Point1 {}'.format(pt1))
            print('Point1 {}'.format(pt2))
            raise Exception('exit')
    linelength = linelength2 ** 0.5
    return linelength


def pointline2vector(line):
    vector = {}
    for dim in line[0]:

        try:
            vector[dim] = line[1][dim] - line[0][dim]
        except Exception:
            print('dimension {}'.format(dim))
            print('line {}'.format(line))
            raise Exception('exit')
    return vector


def scalarproduct(line1, line2):
    # pt1 and pt2 are lines defines by two points and are of the same dimension
    vector1 = pointline2vector(line1)
    vector2 = pointline2vector(line2)

    dotproduct = 0
    for dim in vector1:
        try:
            dotproduct += vector1[dim] * vector2[dim]
        except Exception:
            print('dimension {}'.format(dim))
            print('line {}'.format(vector1))
            print('line {}'.format(vector2))
            raise Exception('exit')

    return dotproduct


def smallangle_lines(line1, line2):
    # returns the smaller angle made by two lines
    dotprod = scalarproduct(line1, line2)
    # dotprod = length(line1) * length(line1) * cos(angle between them)
    # the angle is between 0 and 180 degrees depending on the vectorization of the lines in scalarproduct

    len1 = linelength(line1[0], line1[1])
    len2 = linelength(line2[0], line2[1])

    if len1 == 0 or len2 == 0:
        return 'Line length = 0'

    if abs(dotprod) / len1 / len2 > 1:
        return math.acos(1)

    return math.acos(abs(dotprod) / len1 / len2)


def LineIntersect2D(line1, line2, angletol):
    # line1 and line 2 are infinite lines defined by two points
    # angletol is the cutoff to determine if the lines are parallel
    # USES SMALL ANGLE ASSUMPTION FOR COS
    # If the lines are parallel, it returns 'parallel'
    # If one of the lines is actually a point, it returns 'none'.
    # If the lines are not parallel, then it returns the intercept

    # Calculate length of the line
    len1 = linelength(line1[0], line1[1])
    len2 = linelength(line2[0], line2[1])

    # check to see if one of the lines is actually a point.  If so, return 'none'.
    if len1 == 0 or len2 == 0:
        return 'none'

    # Calculate Scalar product
    angle = smallangle_lines(line1, line2)

    if almostequal(angle, 0, angletol):
        return 'parallel'
    try:
        # break out components
        dimlist = list(line1[0].keys())
        x1 = line1[0][dimlist[0]]
        x2 = line1[1][dimlist[0]]
        x3 = line2[0][dimlist[0]]
        x4 = line2[1][dimlist[0]]
        y1 = line1[0][dimlist[1]]
        y2 = line1[1][dimlist[1]]
        y3 = line2[0][dimlist[1]]
        y4 = line2[1][dimlist[1]]

        # calculate intercepts
        xint = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / (
            (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        )
        yint = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / (
            (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        )
    except Exception:
        print(str(line1))
        print(str(line2))
        raise Exception('exit')
    inter = {dimlist[0]: xint, dimlist[1]: yint}
    return inter


def LineSegIntersect2D(line1, line2, distancetol, angletol):
    # Generate case information
    #
    # print(str(line1)+ ' '+str(line2))
    inter = LineIntersect2D(line1, line2, angletol)

    # REMOVE SINGLE POINT 'LINES'
    if inter == 'none':
        return 'none'

    # HANDLE PARALLEL BUT NOT COLINEAR LINES

    # Check for 'easy' cases of verticle and horizontal lines
    if inter == 'parallel':
        # Calulate angle with vertical and horizontal unit vectors
        for dim in line1[0]:
            try:
                dimlist = list(line1[0].keys())
                unitvector = {dimlist[0]: 0, dimlist[1]: 0}
                unitvector[dim] = 1
                angletest = smallangle_lines(
                    line1, [{dimlist[0]: 0, dimlist[1]: 0}, unitvector]
                )

                if almostequal(angletest, 0, angletol):
                    # note them as 'colinear' if they have indentical dim values
                    # otherwise retun 'none'
                    for otherdim in line1[0]:
                        if otherdim != dim:
                            if almostequal(
                                line1[0][otherdim], line2[0][otherdim], distancetol
                            ):
                                inter = 'colinear'
                            else:
                                return 'none'
            except Exception:
                print(str(line1))
                print(str(line2))
                raise Exception('exit')

    if inter == 'parallel':
        try:
            # Construct equation of line1 in from mpara * x + bpara = y
            dimlist = list(line1[0].keys())
            mpara = (line1[0][dimlist[1]] - line1[1][dimlist[1]]) / (
                line1[0][dimlist[0]] - line1[1][dimlist[0]]
            )
            # bpara = line1[0][1] - mpara*line1[0][0]
            # Construct perpenticular line through center of line1
            # mperp * x + bperp = y
            mperp = -1 / mpara
            center1 = {
                dimlist[0]: (line1[0][dimlist[0]] + line1[1][dimlist[0]]) / 2,
                dimlist[1]: (line1[0][dimlist[1]] + line1[1][dimlist[1]]) / 2,
            }
            bperp = center1[dimlist[1]] - mperp * center1[dimlist[0]]
            # pick two points on the line to define it, say x= 0 and x =1
            perpline = [
                {dimlist[0]: 0, dimlist[1]: bperp},
                {dimlist[0]: 1, dimlist[1]: 1 * mperp + bperp},
            ]
            # find the interscept between that line and
            interceptwline2 = LineIntersect2D(line2, perpline, angletol)
            # Check is the intercepts of the perpendicular line with line1 and line2 are the same in a relevant region (center of line)
            # THIS IS AN ASSUMPTION AND MIGHT LEAD TO ERRORS BECAUSE LINES ARE ONLY APPROXIAMETLY PARALLEL
            if ptalmostequal(center1, interceptwline2, distancetol):
                inter = 'colinear'
            else:
                return 'none'
        except Exception:
            print('line1 ' + str(line1))
            print('line2 ' + str(line2))
            raise Exception('exit')
    # no 'parallel' values should exist at this point

    # HANDLE COLINEAR LINES
    ptlist = [[line1[0], 1], [line1[1], 1], [line2[0], 2], [line2[1], 2]]

    if inter == 'colinear':
        # Sort by distance from one end

        # Determine point with lowest X then Y
        # Since points are colinear, lowest X then Y should be the same as the lowest Y then X

        # Check to see if line in verticle, all X values are the same
        dimlist = list(line1[0].keys())
        unitvector = {dimlist[0]: 0, dimlist[1]: 1}
        angletest = smallangle_lines(
            line1, [{dimlist[0]: 0, dimlist[1]: 0}, unitvector]
        )
        lowpoint = []
        if almostequal(angletest, 0, angletol):
            # collect all Y values
            yvalues = [ptlist[n][0][dimlist[1]] for n in range(0, len(ptlist))]
            # find the index of minimum y value
            lowindex = yvalues.index(min(yvalues))
            # assign that point to lowpoint
            lowpoint = ptlist[lowindex][0]
        else:
            # collect all X values
            xvalues = [ptlist[n][0][dimlist[0]] for n in range(0, len(ptlist))]
            # find the index of minimum X value
            lowindex = xvalues.index(min(xvalues))
            # assign that point to lowpoint
            lowpoint = ptlist[lowindex][0]

        # perform sort by absolute distance from lowpoint
        ptlist.sort(
            key=lambda x: (x[0][dimlist[1]] - lowpoint[dimlist[1]]) ** 2
            + (x[0][dimlist[0]] - lowpoint[dimlist[0]]) ** 2
        )

        # Deal with identical point situations where the order could get confused by rounding errors

        # if the middle two points are equal
        if ptalmostequal(ptlist[1][0], ptlist[2][0], distancetol):
            # Check is they are part of the same initial line
            if ptlist[1][1] == ptlist[2][1]:
                # Treat as small line embedded in larger line if they are
                return ['colinear', ptlist[1][0], ptlist[2][0]]
            else:
                # treat as a normal intersection
                return ptlist[1][0]

        # if the lowest two points are equal
        if ptalmostequal(ptlist[0][0], ptlist[1][0], distancetol):
            # Check is they are part of the same initial line
            if ptlist[0][1] == ptlist[1][1]:
                # treat as non-intersection small lines
                return 'none'
            else:
                return ['colinear', ptlist[1][0], ptlist[2][0]]

        # if the highest two points are equal
        if ptalmostequal(ptlist[2][0], ptlist[3][0], distancetol):
            # Check is they are part of the same initial line
            if ptlist[2][1] == ptlist[3][1]:
                # treat as non-intersection small lines
                return 'none'
            else:
                return ['colinear', ptlist[1][0], ptlist[2][0]]

        # all other cases where points in ptlist aren't equal

        # if the sources of the points alternate then there is an overlap region
        if ptlist[0][1] != ptlist[1][1]:
            return ['colinear', ptlist[1][0], ptlist[2][0]]
        else:
            return 'none'

    ptlist = [line1[0], line1[1], line2[0], line2[1]]
    dimlist = list(line1[0].keys())
    inter1 = 0
    inter2 = 0
    for point in line1:
        # Is inter an end point of the line?
        # print( str(inter) + ' ' + str(point) )
        if ptalmostequal(inter, point, distancetol):
            inter1 = 1

        linex = [line1[0][dimlist[0]], line1[1][dimlist[0]]]
        liney = [line1[0][dimlist[1]], line1[1][dimlist[1]]]
        # Is the point in the XY range set by the points?
        if (min(linex) - distancetol) <= inter[dimlist[0]] <= (
            max(linex) + distancetol
        ) and (min(liney) - distancetol) <= inter[dimlist[1]] <= (
            max(liney) + distancetol
        ):
            inter1 = 1

    for point in line2:
        # Is inter an end point of the line?
        if ptalmostequal(inter, point, distancetol):
            inter2 = 1

        linex = [line2[0][dimlist[0]], line2[1][dimlist[0]]]
        liney = [line2[0][dimlist[1]], line2[1][dimlist[1]]]
        # Is the point in the XY range set by the points?
        if (min(linex) - distancetol) <= inter[dimlist[0]] <= (
            max(linex) + distancetol
        ) and (min(liney) - distancetol) <= inter[dimlist[1]] <= (
            max(liney) + distancetol
        ):
            inter2 = 1

    # print(str(inter1) + str(inter2))
    if inter1 == 1 and inter2 == 1:
        return inter

    return 'none'


def pointinregion(point, region, distancetol, angletol):
    # Checks if a point is in some boundary defined by the line between consecutive points in region (region).
    # Points on the edge are NOT considered in the region.
    # Uses a quick rectangular exclusion followed by a ray tracing method
    try:
        dimlist = list(point.keys())
        dimx = dimlist[0]
        dimy = dimlist[1]
    except Exception:
        print(str(point))
        raise Exception('exit')
    # define bounding box
    # box (minx,maxx, miny, maxy)
    try:
        minx = min([region[g][dimx] for g in range(0, len(region))])
        maxx = max([region[g][dimx] for g in range(0, len(region))])
        miny = min([region[g][dimy] for g in range(0, len(region))])
        maxy = max([region[g][dimy] for g in range(0, len(region))])
    except Exception:
        print(str(region))
        raise Exception('exit')

    box = [minx, maxx, miny, maxy]
    # print(str(box))
    # check if point is outside of boxed region
    if (
        (point[dimx] < box[0])
        or (point[dimx] > box[1])
        or (point[dimy] < box[2])
        or (point[dimy] > box[3])
    ):
        # exclude points that are obviously out
        return False

    # sets a frame around the system
    # this frame is used as limits of the the rays/lines traversing the boundary
    frame_factor = 0.2  # fractional increase in linear dimensions of box
    # frame has the same center as box
    fminx = box[0] - frame_factor / 2 * (box[1] - box[0])
    fmaxx = box[1] + frame_factor / 2 * (box[1] - box[0])
    fminy = box[2] - frame_factor / 2 * (box[3] - box[2])
    fmaxy = box[3] + frame_factor / 2 * (box[3] - box[2])
    frame = [fminx, fmaxx, fminy, fmaxy]

    # construct 3 lines colinear with point and going between the x-extents of the boundry
    # One line line is horizontal and the other two are rotated by an irrational number of degrees
    # The goal is to prevent the all three from being colinear  with a boundary line

    rays = []

    # horizontal line
    rays.append(
        [{dimx: frame[0], dimy: point[dimy]}, {dimx: frame[1], dimy: point[dimy]}]
    )

    # line that is rotated by e degrees (y = mx + c)
    m = math.tan(math.exp(1) * math.pi / 180)
    c = point[dimy] - m * point[dimx]
    rays.append(
        [
            {dimx: frame[0], dimy: m * frame[0] + c},
            {dimx: frame[1], dimy: m * frame[1] + c},
        ]
    )

    # line that is rotated by -e degrees (y = mx + c)
    m = -m
    c = point[dimy] - m * point[dimx]
    rays.append(
        [
            {dimx: frame[0], dimy: m * frame[0] + c},
            {dimx: frame[1], dimy: m * frame[1] + c},
        ]
    )

    # build matrix for cycling through region edges so that each two points is an edge of the region
    regioncycle = region[:]
    regioncycle.append(region[0])
    # print(str(regioncycle))

    # Look at each ray
    for r in range(0, len(rays)):

        # collect all region intercepts with a particular ray
        intercepts = []
        for b in range(0, len(region)):
            bedge = [regioncycle[b], regioncycle[b + 1]]
            inter = LineSegIntersect2D(bedge, rays[r], distancetol, angletol)
            # print(str(inter))
            # If there is a an intercept AND it is NOT colinear then add it to the intercepts list
            if dimx in inter:
                intercepts.append(inter)
                # if this interscept is a point, then it counts as being on the boundary
                if ptalmostequal(inter, point, distancetol):
                    # print('here')
                    return False

        # remove repeated intercepts
        # repeat intercepts can occur at vertices

        # sort to get identical values to neighbor
        # print (intercepts)
        intercepts.sort(key=lambda x: x[dimx])
        intercepts.sort(key=lambda x: x[dimy])
        newintercepts = intercepts[:]
        # print(str(intercepts))
        # cut out repeats
        cuts = 0
        for l in range(1, len(intercepts)):
            if ptalmostequal(newintercepts[l - cuts - 1], intercepts[l], distancetol):
                del newintercepts[l - cuts]
                cuts = cuts + 1

        # Count the number of intercepts with lower x-values
        intercepts = newintercepts
        # print(str(intercepts))

        negints = 0
        for n in range(0, len(intercepts)):
            if intercepts[n][dimx] < point[dimx]:
                negints = negints + 1

        # Count the number of intercepts with lower x-values
        posints = 0
        for n in range(0, len(intercepts)):
            if intercepts[n][dimx] > point[dimx]:
                posints = posints + 1

        # Calulate odd/even behavior of intercepts
        # Even on both sides means point is outside and value is 0
        # Odd on both side menas point is inside and value is 1
        # Ray intersection with vertices can generate 0, 0.5, or 1
        rays[r].append((negints % 2 + posints % 2) / 2)

    # Average the odd/even behavior of the three rays
    # If all agree and are correct, then value will be 0 or 1
    # If one is wrong but the other two are correct then the value 1/3 or 2/3
    # If two or more are wrong, then this method will fail
    # print(str(negints) + ' ' + str(posints))
    # print(str(rays))
    evaluation = sum([rays[j][2] for j in range(0, len(rays))]) / len(rays)
    # print(str(evaluation))
    if evaluation > 0.5:
        return True
    else:
        # print('here')
        return False
