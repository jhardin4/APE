import csv
import cv2
import numpy as np
from skimage.morphology import medial_axis
from matplotlib import pyplot as plt
from scipy.sparse.csgraph import minimum_spanning_tree


def getParameters(test_nbs=[1, 2, 3, 4, 5]):
    params = {}
    name_col = 0
    tip_height_col = 7
    gap_height_col = 10
    gap_width_col = 11
    label_col = 13

    for test_nb in test_nbs:
        csv_name = '../Run{} - Copy.csv'.format(test_nb)
        with open(csv_name) as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader, None)
            assert header[name_col] == "name", "{} != {}".format(
                header[name_col], "name"
            )
            assert header[tip_height_col] == "tiph", "{} != {}".format(
                header[tip_height_col], "tiph"
            )
            assert header[gap_height_col] == "gapVecHeight", "{} != {}".format(
                header[gap_height_col], "gapVecHeight"
            )
            assert header[gap_width_col] == "gapWidth", "{} != {}".format(
                header[gap_width_col], "gapWidth"
            )
            assert header[label_col] == "SpanClass", "{} != {}".format(
                header[label_col], "SpanClass"
            )
            for row in reader:
                name = "../Test {}/{}".format(test_nb, row[name_col])
                params[name] = {
                    "tipHeight": row[tip_height_col],
                    "gapHeight": row[gap_height_col],
                    "gapWidth": row[gap_width_col],
                    "label": row[label_col],
                }
    return params


def showPoly(
    shape,
    rho0,
    theta0,
    rho1,
    theta1,
    c00,
    c01,
    c02,
    c03,
    c04,
    c10,
    c11,
    c12,
    c13,
    c14,
    length,
    img=None,
):

    (m, n) = shape[:2]

    if img is None:
        img = np.zeros((m, n, 3), dtype=np.uint8)

    a = np.cos(theta0)
    b = np.sin(theta0)
    pt00 = (int(rho0 * (a + b * b / a)), 0)
    pt01 = (int(rho0 * (a + b * b / a) - m * b / a), m)
    cv2.line(img, pt00, pt01, (0, 0, 255), 8, cv2.LINE_AA)

    a = np.cos(theta1)
    b = np.sin(theta1)
    pt10 = (int(rho1 * (a + b * b / a)), 0)
    pt11 = (int(rho1 * (a + b * b / a) - m * b / a), m)
    cv2.line(img, pt10, pt11, (255, 0, 0), 8, cv2.LINE_AA)

    p = [np.poly1d([c04, c03, c02, c01, c00]), np.poly1d([c14, c13, c12, c11, c10])]

    t = np.linspace(0, length, 1000)

    coords = np.vstack([p[1](t), p[0](t)]).T.astype(np.int32)

    cv2.polylines(img, [coords], 0, (255, 0, 255), 10)

    plt.imshow(img)
    # plt.show()


def showPolyOne(
    shape,
    rho0,
    rho1,
    theta0,
    theta1,
    end00,
    end01,
    end10,
    end11,
    c0,
    c1,
    c2,
    c3,
    c4,
    img=None,
):

    (m, n) = shape[:2]

    if img is None:
        img = np.zeros((m, n, 3), dtype=np.uint8)

    a = np.cos(theta0)
    b = np.sin(theta0)
    pt00 = (int(rho0 * (a + b * b / a)), 0)
    pt01 = (int(rho0 * (a + b * b / a) - m * b / a), m)
    cv2.line(img, pt00, pt01, (0, 0, 255), 8, cv2.LINE_AA)

    a = np.cos(theta1)
    b = np.sin(theta1)
    pt10 = (int(rho1 * (a + b * b / a)), 0)
    pt11 = (int(rho1 * (a + b * b / a) - m * b / a), m)
    cv2.line(img, pt10, pt11, (255, 0, 0), 8, cv2.LINE_AA)

    p = np.poly1d([c4, c3, c2, c1, c0])

    t = np.linspace(0, 1, 1000)
    u = np.array([end10 - end00, end11 - end01])
    lin = np.linalg.norm(u)
    u /= lin
    v = np.array([-u[1], u[0]])

    coords = (
        lin * (t[:, None] * u[None, ::-1] + p(t)[:, None] * v[None, ::-1])
        + np.array([end01, end00])[None, :]
    ).astype(np.int32)

    cv2.polylines(img, [coords], 0, (255, 0, 255), 10)

    plt.imshow(img)


# Images that need a custom parameter input for edge detection
custom_nb = {
    "../Test 1/samplex01y011final.tif": 300,
    "../Test 1/samplex07y011final.tif": 300,
    "../Test 1/samplex08y000final.tif": 300,
    "../Test 1/samplex09y011final.tif": 300,
    "../Test 1/samplex10y000final.tif": 300,
    "../Test 3/samplex00y006final.tif": 900,
    "../Test 4/samplex00y000final.tif": 300,
    "../Test 4/samplex02y002final.tif": 600,
    "../Test 4/samplex00y010final.tif": 300,
    "../Test 4/samplex08y000final.tif": 300,
    "../Test 5/samplex00y000final.tif": 300,
    "../Test 5/samplex00y001final.tif": 300,
    "../Test 5/samplex00y010final.tif": 300,
    "../Test 5/samplex00y011final.tif": 335,
}


def detectVerticalEdges(img, houghParam=500):

    if len(img.shape) > 2:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    (m, n) = img.shape

    # Apply a gaussian filter with large vertical kernel
    img = cv2.GaussianBlur(img, (35, 9), 0)

    # Compute the horizontal gradients and threshold their absolute value
    img = (np.abs(cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=5)) > 100).astype(np.uint8)

    # Dilate image
    kernel = np.ones((3, 3), np.uint8)
    img = cv2.dilate(img, kernel)

    # Detect lines
    lines = cv2.HoughLines(img, 1, np.pi / 180, houghParam)

    line_clusters = []

    if lines is not None:
        for i in range(0, len(lines)):
            rho = lines[i][0][0]
            theta = lines[i][0][1]
            # Only keep desired orientation
            if theta < 0.06 and theta > 0.03:
                a = np.cos(theta)
                b = np.sin(theta)

                x = rho * (a + b * b / a) - m * b / a / 2
                cluster_id = None
                for k, cluster in enumerate(line_clusters):
                    # Check if line can be added to an existing cluster and exit loop if so
                    if np.abs(x - cluster['mean']) < 150:
                        cluster_id = k
                        break
                # If line can be added to an existing cluster, do it
                if cluster_id is not None:
                    le = len(line_clusters[cluster_id]['list'])
                    line_clusters[cluster_id]['list'].append((rho, theta))
                    line_clusters[cluster_id]['mean'] = (
                        line_clusters[cluster_id]['mean'] * le + x
                    ) / (le + 1)
                # Otherwise, create a new cluster
                else:
                    line_clusters.append({'list': [(rho, theta)], 'mean': x})

    # Compute lines mean per cluster
    for cluster in line_clusters:
        cluster['rho'] = np.mean([el[0] for el in cluster['list']])
        cluster['theta'] = np.mean([el[1] for el in cluster['list']])

    # Return cluster
    return line_clusters


def detectGap(img, lines):
    (m, n) = img.shape[:2]
    lines.sort(key=lambda e: np.abs(e['mean'] - n / 2))
    return sorted(lines[:2], key=lambda e: e['mean']), lines[2:]


def getFrame(img, lines):
    lines, _ = detectGap(img, lines)
    (m, n) = img.shape[:2]
    rho0 = lines[0]['rho']
    c0 = np.cos(lines[0]['theta'])
    s0 = np.sin(lines[0]['theta'])
    x0 = rho0 * (c0 + s0 * s0 / c0)
    y0 = 0
    rho1 = lines[1]['rho']
    c1 = np.cos(lines[1]['theta'])
    s1 = np.sin(lines[1]['theta'])
    x1 = rho1 * (c1 + s1 * s1 / c1) - m * s1 / c1
    y1 = m
    rho2 = x0 * s0 - y0 * c0
    x2 = (rho1 * c0 + rho2 * s1) / (c1 * c0 + s1 * s0)
    y2 = (rho1 * s0 - rho2 * c1) / (c1 * c0 + s1 * s0)
    rho3 = x1 * s1 - y1 * c1
    x3 = (rho0 * c1 + rho3 * s0) / (c1 * c0 + s1 * s0)
    y3 = (rho0 * s1 - rho3 * c0) / (c1 * c0 + s1 * s0)

    return [(x0, y0), (x2, y2), (x1, y1), (x3, y3)]


def reframe(img, lines, drawFrame=False):
    (m, n) = img.shape[:2]
    frame = getFrame(img, lines)
    [(x0, y0), (x2, y2), (x1, y1), (x3, y3)] = frame

    if drawFrame:
        cv2.line(
            img, (int(x0), int(y0)), (int(x2), int(y2)), (255, 0, 0), 8, cv2.LINE_AA
        )
        cv2.line(
            img, (int(x1), int(y1)), (int(x3), int(y3)), (255, 0, 0), 8, cv2.LINE_AA
        )
        cv2.line(
            img, (int(x0), int(y0)), (int(x3), int(y3)), (255, 0, 0), 8, cv2.LINE_AA
        )
        cv2.line(
            img, (int(x2), int(y2)), (int(x1), int(y1)), (255, 0, 0), 8, cv2.LINE_AA
        )
    frame_lines = [
        ((int(x0), int(y0)), (int(x2), int(y2))),
        ((int(x1), int(y1)), (int(x3), int(y3))),
        ((int(x0), int(y0)), (int(x3), int(y3))),
        ((int(x2), int(y2)), (int(x1), int(y1))),
    ]

    new_x0 = int((x0 + x3) / 2)
    new_y0 = 0
    new_x1 = int((x1 + x2) / 2)
    new_y1 = m
    new_x2 = new_x1
    new_y2 = 0
    # new_x3 = new_x0
    new_y3 = m
    new_frame = [(new_x0, new_y0), (new_x2, new_y2), (x1, new_y1), (x3, new_y3)]
    M = cv2.getPerspectiveTransform(
        np.array(frame).astype(np.float32), np.array(new_frame).astype(np.float32)
    )
    M_inv = cv2.getPerspectiveTransform(
        np.array(new_frame).astype(np.float32), np.array(frame).astype(np.float32)
    )
    return (
        img,
        cv2.warpPerspective(img, M, dsize=(n, m)),
        new_x0,
        new_x1,
        M,
        M_inv,
        frame_lines,
    )


def getLongestPath(skel):
    skel_idx = np.indices(skel.shape)[:, skel]
    X = np.linalg.norm(skel_idx[:, :, None] - skel_idx[:, None, :], axis=0)
    Tcsr = minimum_spanning_tree(X)
    Tcsr_bool = Tcsr.astype(bool)
    p = Tcsr.shape[0]
    idx = np.arange(Tcsr[0, :].shape[1])
    explored = {0: 0}
    frontier = []

    mask = Tcsr_bool[0, :].A.flatten().astype(bool) + Tcsr_bool[
        :, 0
    ].A.flatten().astype(bool)
    neighbors = idx[mask]
    values = Tcsr[0, :].A.flatten()[mask] + Tcsr[:, 0].A.flatten()[mask]
    for i in range(len(neighbors)):
        frontier.append((0, neighbors[i], values[i]))
    while frontier:
        (p, q, v) = frontier.pop()
        explored[q] = explored[p] + v
        mask = Tcsr_bool[q, :].A.flatten().astype(bool) + Tcsr_bool[
            :, q
        ].A.flatten().astype(bool)
        neighbors = idx[mask]
        values = Tcsr[q, :].A.flatten()[mask] + Tcsr[:, q].A.flatten()[mask]
        for i in range(len(neighbors)):
            if neighbors[i] not in explored:
                frontier.append((q, neighbors[i], v))

    n1 = max(explored, key=explored.get)
    explored = {n1: (None, 0)}
    frontier = []

    mask = Tcsr_bool[n1, :].A.flatten().astype(bool) + Tcsr_bool[
        :, n1
    ].A.flatten().astype(bool)
    neighbors = idx[mask]
    values = Tcsr[n1, :].A.flatten()[mask] + Tcsr[:, n1].A.flatten()[mask]
    for i in range(len(neighbors)):
        frontier.append((n1, neighbors[i], values[i]))
    while frontier:
        (p, q, v) = frontier.pop()
        explored[q] = (p, explored[p][1] + v)
        mask = Tcsr_bool[q, :].A.flatten().astype(bool) + Tcsr_bool[
            :, q
        ].A.flatten().astype(bool)
        neighbors = idx[mask]
        values = Tcsr[q, :].A.flatten()[mask] + Tcsr[:, q].A.flatten()[mask]
        for i in range(len(neighbors)):
            if neighbors[i] not in explored:
                frontier.append((q, neighbors[i], v))

    n = max(explored, key=lambda k: explored[k][1])
    path = []
    while n is not None:
        path.append(n)
        n = explored[n][0]

    return skel_idx[:, path]


def getNearestPointOnLine(pt, line):
    a = np.cos(line["theta"])
    b = np.sin(line["theta"])
    c = -line["rho"]

    return (b * (b * pt[0] - a * pt[1]) - a * c, a * (a * pt[1] - b * pt[0]) - b * c)


def cutPathAtEdges(path_idx, line1, line2, offset=0):
    paths = []
    edgesCross = []

    newPath = []
    edge1Cross, edge2Cross = False, False

    for k in range(path_idx.shape[1]):
        i = path_idx[0, k]
        j = path_idx[1, k]
        if (
            getNearestPointOnLine((j, i), line1)[0] <= j + offset
            and getNearestPointOnLine((j, i), line2)[0] >= j - offset
        ):
            if newPath == [] and k > 0:
                # Get the previous points
                iPrev = path_idx[0, k - 1]
                jPrev = path_idx[1, k - 1]

                # Check if it is left of the left edge:
                if getNearestPointOnLine((jPrev, iPrev), line1)[0] > jPrev + offset:
                    # Define the parameters of the crossed line
                    a = np.cos(line1["theta"])
                    b = np.sin(line1["theta"])
                    c = -line1["rho"]
                    edge1Cross = True
                    # print("Setting edge1Cross to true")
                # Otherwise it is right of the right edge
                else:
                    a = np.cos(line2["theta"])
                    b = np.sin(line2["theta"])
                    c = -line2["rho"]
                    edge2Cross = True
                    # print("Setting edge2Cross to true")

                # Find the point at the intersection of the cross line and add it to the path
                iInt = (a * (i * jPrev - j * iPrev) + c * (i - iPrev)) / (
                    (jPrev - j) * a + (iPrev - i) * b
                )
                jInt = (b * (j * iPrev - i * jPrev) + c * (j - jPrev)) / (
                    (jPrev - j) * a + (iPrev - i) * b
                )
                print(
                    "Entering path: {}, {}, {}".format(
                        jInt, iInt, a * jInt - b * iInt + c
                    )
                )
                iInt = int(iInt)
                jInt = int(jInt)

                newPath.append((iInt, jInt))

            newPath.append((i, j))
        else:
            if newPath:
                # Check if this point is left of the left edge:
                if getNearestPointOnLine((j, i), line1)[0] > j + offset:
                    # Define the parameters of the crossed line
                    a = np.cos(line1["theta"])
                    b = np.sin(line1["theta"])
                    c = -line1["rho"]
                    edge1Cross = True
                    # print("Setting edge1Cross to true")
                # Otherwise it is right of the right edge
                else:
                    a = np.cos(line2["theta"])
                    b = np.sin(line2["theta"])
                    c = -line2["rho"]
                    edge2Cross = True
                    # print("Setting edge2Cross to true")

                # Get the previous points
                iPrev = path_idx[0, k - 1]
                jPrev = path_idx[1, k - 1]

                # Find the point at the intersection of the cross line and add it to the path
                iInt = (a * (i * jPrev - j * iPrev) + c * (i - iPrev)) / (
                    (jPrev - j) * a + (iPrev - i) * b
                )
                jInt = (b * (j * iPrev - i * jPrev) + c * (j - jPrev)) / (
                    (jPrev - j) * a + (iPrev - i) * b
                )
                print(
                    "Exiting path: {}, {}, {}".format(
                        jInt, iInt, a * jInt - b * iInt + c
                    )
                )
                iInt = int(iInt)
                jInt = int(jInt)

                newPath.append((iInt, jInt))

                if newPath[0][1] > newPath[-1][-1]:
                    newPath = newPath[::-1]
                paths.append(np.array(newPath).T)
                edgesCross.append((edge1Cross, edge2Cross))
                newPath = []
                edge1Cross, edge2Cross = False, False

    if newPath:
        if newPath[0][1] > newPath[-1][-1]:
            newPath = newPath[::-1]
        paths.append(np.array(newPath).T)
        edgesCross.append((edge1Cross, edge2Cross))

    return paths, edgesCross


def getSkeletons(seg):
    # plt.figure()
    # plt.imshow(seg)
    kernel = np.ones((25, 25), np.uint8)
    erosion = cv2.erode(seg, kernel, iterations=1)
    # plt.figure()
    # plt.imshow(erosion)
    # blur = (cv2.GaussianBlur(erosion, (35, 35), 0) > 230).astype(np.uint8)
    # plt.figure()
    # plt.imshow(blur)
    dilation = cv2.dilate(erosion, kernel, iterations=1)
    # plt.figure()
    # plt.imshow(dilation)
    ret, labels = cv2.connectedComponents(dilation)
    skels = []
    for k in range(1, ret):
        skel, distance = medial_axis(labels == k, return_distance=True)
        skels.append(skel)

    return skels


def fitPath(path, deg):
    dists = np.zeros(path.shape[1])
    dists[1:] = np.cumsum(np.linalg.norm(path[:, 1:] - path[:, :-1], axis=0))
    z, residuals, _, _, _ = np.polyfit(dists, path.T, deg, full=True)
    p = [np.poly1d(z[:, 0]), np.poly1d(z[:, 1])]

    t = np.linspace(0, dists[-1], 1000)

    return p, t, [p[1](t), p[0](t)], residuals / path.shape[1], dists[-1]


def fitPathOne(path, deg):
    # Fit the curve to a polynomial along the orientation given by the end points of the path
    # The points coordinates are divided by the distance from the end points of the path
    # so that the polynomial inputs go from 0 to 1
    u = path[:, -1] - path[:, 0]
    lin = np.linalg.norm(u)
    u = u / (lin * lin)
    v = np.array([-u[1], u[0]])
    xs = [np.dot(path[:, k] - path[:, 0], u) for k in range(path.shape[1])]
    ys = [np.dot(path[:, k] - path[:, 0], v) for k in range(path.shape[1])]
    # print("xs: {}".format(xs))
    # print("ys: {}".format(ys))
    # print(xs, ys)
    z, residual, _, _, _ = np.polyfit(xs, ys, deg, full=True)
    p = np.poly1d(z)
    t = np.linspace(0, 1, 1000)

    coords = (
        lin * lin * (t[None, :] * u[::-1, None] + p(t)[None, :] * v[::-1, None])
        + path[::-1, 0:1]
    )

    return z[::-1], coords, residual, lin


def printSkeleton(img, skel, c=(255, 255, 0)):
    skel_idx = np.indices(skel.shape)[:, skel]
    for k in range(skel_idx.shape[1]):
        i, j = skel_idx[:, k]
        img[i - 10 : i + 10, j - 10 : j + 10, :] = c


def printPath(img, path, c=(255, 0, 255), w=10):
    cv2.polylines(img, [np.array(path, dtype=np.int32)[[1, 0], :].T], 0, c, w)


def getPoly(img_path, img, seg, draw=False):

    (m, n) = img.shape[:2]

    if img_path in custom_nb:
        lines = detectVerticalEdges(img, custom_nb[img_path])
    else:
        lines = detectVerticalEdges(img)

    [line1, line2], lines = detectGap(img, lines)
    skels = getSkeletons(seg)

    # print("{} lines found".format(len(lines)))
    # print("{} skeletons found".format(len(skels)))

    if draw:
        for line in lines:
            a = np.cos(line['theta'])
            b = np.sin(line['theta'])
            pt1 = (int(line['rho'] * (a + b * b / a)), 0)
            pt2 = (int(line['rho'] * (a + b * b / a) - m * b / a), m)
            cv2.line(img, pt1, pt2, (0, 255, 0), 8, cv2.LINE_AA)

        a = np.cos(line1['theta'])
        b = np.sin(line1['theta'])
        pt1 = (int(line1['rho'] * (a + b * b / a)), 0)
        pt2 = (int(line1['rho'] * (a + b * b / a) - m * b / a), m)
        cv2.line(img, pt1, pt2, (0, 0, 255), 8, cv2.LINE_AA)

        a = np.cos(line2['theta'])
        b = np.sin(line2['theta'])
        pt1 = (int(line2['rho'] * (a + b * b / a)), 0)
        pt2 = (int(line2['rho'] * (a + b * b / a) - m * b / a), m)
        cv2.line(img, pt1, pt2, (255, 0, 0), 8, cv2.LINE_AA)

    paths = []
    for skel in skels:
        # printSkeleton(img, skel)
        paths.append(getLongestPath(skel))

    cutPaths = []
    edgesCrosses = []
    for path in paths:
        # print("Before cuttin: {}".format(path.shape))
        if draw:
            printPath(img, path)
        newPaths, edgesCross = cutPathAtEdges(path, line1, line2)
        # print("After cuttin: {}".format([path.shape for path in newPaths]))
        for path in newPaths:
            # printPath(img, path, c=np.nditer(cv2.cvtColor(np.uint8([[[np.random.randint(181), 255, 255]]]), cv2.COLOR_HSV2RGB)), w=10)
            if draw:
                printPath(img, path, c=(255, 255, 100), w=12)
        cutPaths += newPaths
        edgesCrosses += edgesCross

    # ps = []
    # coords = []
    # rs = []
    # dists = []
    # for path in cutPaths:
    #     p, t, coord, r, dist = fitPath(path, min([4, path.shape[1]-1]))
    #     ps.append(p)
    #     coords.append(np.array(coord, dtype=np.int32).T)
    #     rs.append(r)
    #     dists.append(dist)

    # # Order by decreasing distance
    # dists, ps, coords, rs = zip(*sorted(list(zip(dists, ps, coords, rs)), reverse=True))

    ps = []
    coords = []
    rs = []
    dists = []
    pathEnds = []
    for path in cutPaths:
        p, coord, r, dist = fitPathOne(path, min([4, path.shape[1] - 1]))
        ps.append(p)
        coords.append(np.array(coord, dtype=np.int32).T)
        rs.append(r)
        dists.append(dist)
        pathEnds.append((path[:, 0], path[:, -1]))

    if cutPaths:
        # Order by decreasing distance
        dists, ps, coords, rs, edgesCrosses, pathEnds = zip(
            *sorted(
                list(zip(dists, ps, coords, rs, edgesCrosses, pathEnds)), reverse=True
            )
        )

    return ps, coords, rs, dists, edgesCrosses, pathEnds, line1, line2, lines
