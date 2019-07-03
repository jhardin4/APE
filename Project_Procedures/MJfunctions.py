import cv2
import numpy as np
from matplotlib import pyplot as plt
import utils  # kevins utils
import skimage
import scipy
import scipy.ndimage
from skimage import morphology
from skimage.morphology import disk

import pickle
import time
import sys


def LABsegmenter(imgf, imgi, samplename, path, save):
    # this function takes in the initial and final images and returns a segmented

    # imgf = rgb final image
    # imgi = rgb initial image

    print('Beginning Initial Segmentation')

    # can also read in paths if we want
    if path is True:
        # pathf = 'B:\\Lab\\Spanning\\Spanning Data\\2018_12_07\\Test 1\\samplex02y007final.tif'
        # pathi = 'B:\\Lab\\Spanning\\Spanning Data\\2018_12_07\\Test 1\\samplex02y007.tif'
        imgf = cv2.imread(imgf, cv2.IMREAD_COLOR)
        imgi = cv2.imread(imgi, cv2.IMREAD_COLOR)

    imgf = cv2.cvtColor(
        imgf, cv2.COLOR_RGB2BGR
    )  # no clue why RGB gets red in as BGR but anyways...
    LAB_imgf = skimage.color.rgb2lab(imgf)  # convert to LAB
    # LAB_img = cv2.convertScaleAbs(LAB_img) not necessary

    # repeat for initials
    imgi = cv2.cvtColor(
        imgi, cv2.COLOR_RGB2BGR
    )  # no clue why RGB gets red in as BGR but anyways...
    LAB_imgi = skimage.color.rgb2lab(imgi)  # convert to LAB

    threshf = (
        (LAB_imgf[:, :, 0] > 0)
        & (LAB_imgf[:, :, 0] < 31)
        & (LAB_imgf[:, :, 1] > 0)
        & (LAB_imgf[:, :, 1] < 100)
        & (LAB_imgf[:, :, 2] > -106)
        & (LAB_imgf[:, :, 2] < -3)
    )

    threshi = (
        (LAB_imgi[:, :, 0] > 0)
        & (LAB_imgi[:, :, 0] < 31)
        & (LAB_imgi[:, :, 1] > 0)
        & (LAB_imgi[:, :, 1] < 100)
        & (LAB_imgi[:, :, 2] > -106)
        & (LAB_imgi[:, :, 2] < -3)
    )

    # now fill in internal holes
    threshf = scipy.ndimage.binary_fill_holes(threshf).astype(bool)
    threshi = scipy.ndimage.binary_fill_holes(threshi).astype(bool)

    subtracted = threshf.astype(int) - threshi.astype(int)
    subtracted = subtracted.clip(min=0)

    # filter out small objects
    subtracted = morphology.remove_small_objects(
        np.array(subtracted, bool), 10000, connectivity=1
    )
    # morphological closing operation (dilate then erode)
    subtracted = skimage.morphology.closing(subtracted, selem=disk(32))

    binary_img = subtracted

    if save is True:

        plt.imsave(
            'Data\\' + str(round(time.time())) + samplename + '_LABseg' + '.tif',
            binary_img,
        )

    print('Done w/ Initial Segmentation')

    return binary_img


def gap_finder(imgi, imgf, binary_img, gap_padding, samplename, path, save):
    # this function takes in the initial image and find the edges
    # this can accept paths or images as matrices... mark path True or False depending on which one
    try:
        print('Finding Gap Edges')

        if path is True:
            pathf = imgf
            pathi = imgi
            # pathb = binary_img
            imgf = cv2.imread(pathf, cv2.IMREAD_COLOR)
            imgi = cv2.imread(pathi, cv2.IMREAD_COLOR)
            # binary_img = cv2.imread(pathb, cv2.IMREAD_GRAYSCALE)

        imgi = cv2.cvtColor(imgi, cv2.COLOR_BGR2RGB)

        lines = utils.detectVerticalEdges(imgi)

        [line1, line2], other_lines = utils.detectGap(imgi, lines)

        (m, n) = imgi.shape[:2]

        a = np.cos(line1['theta'])
        b = np.sin(line1['theta'])
        pt1 = (int(line1['rho'] * (a + b * b / a)), 0)
        pt2 = (int(line1['rho'] * (a + b * b / a) - m * b / a), m)
        # cv2.line(img, pt1, pt2, (0, 0, 255), 8, cv2.LINE_AA)

        a = np.cos(line2['theta'])
        b = np.sin(line2['theta'])
        pt3 = (int(line2['rho'] * (a + b * b / a)), 0)
        pt4 = (int(line2['rho'] * (a + b * b / a) - m * b / a), m)
        # cv2.line(img, pt3, pt4, (255, 0, 0), 8, cv2.LINE_AA)
        pts = np.array([pt1, pt2, pt4, pt3], np.int32)
        # print(pts)
        cv2.polylines(imgi, [pts], True, (0, 255, 255))
        cv2.fillPoly(imgi, [pts], (0, 255, 255))

        # imgi = cv2.cvtColor(imgi, cv2.COLOR_RGB2BGR)

        gap_colored = imgi

        gapThresh = (
            (gap_colored[:, :, 0] == 0)
            & (gap_colored[:, :, 1] == 255)
            & (gap_colored[:, :, 2] == 255)
        )

        if gap_padding == 0:
            _ = gapThresh  # TODO: use gapPadded

        elif gap_padding != 0:
            ind_mat = np.arange(0, gapThresh.shape[0] * gapThresh.shape[1]).reshape(
                (gapThresh.shape)
            )
            gap_inds = ind_mat * gapThresh

            far_left = []
            far_right = []
            for row in range(gap_inds.shape[0]):
                row_indices = gap_inds[row, :]
                # far_right.append(np.max(row_indices))
                far_right.append(
                    (np.unravel_index(row_indices.argmax(), gapThresh.shape[1]))[0]
                )

                row_indices[row_indices == 0] = (
                    gapThresh.shape[0] * gapThresh.shape[1] + 5
                )  # make the zeros something bigger than we could ever possibly get just so zero is never the minimum
                # far_left.append(np.min(row_indices))
                far_left.append(
                    (np.unravel_index(row_indices.argmin(), gapThresh.shape[1]))[0]
                )

            gapExpanded = gap_inds
            gapExpanded[gapExpanded == gapThresh.shape[0] * gapThresh.shape[1] + 5] = 0
            for row in range(gap_inds.shape[0]):
                if far_left[row] - gap_padding <= 0:
                    far_left[row] = gap_padding
                if far_right[row] + gap_padding >= gapThresh.shape[1]:
                    far_right[row] = gapThresh.shape[1] - gap_padding

                gapExpanded[
                    row, (far_left[row] - gap_padding) : (far_right[row] + gap_padding)
                ] = 1

            gapPadded_f = imgf.astype(np.uint8) * np.dstack(
                (gapExpanded, gapExpanded, gapExpanded)
            ).astype(np.uint8)
            gapPadded_thresh = binary_img * gapExpanded

            plt.imshow(binary_img.astype(np.uint8) * gapExpanded.astype(np.uint8))

        if save is True:
            plt.imsave(
                'Data\\'
                + str(round(time.time()))
                + samplename
                + '_gapColored'
                + '.tif',
                gap_colored,
            )
            plt.imsave(
                'Data\\' + str(round(time.time())) + samplename + '_gapPadded' + '.tif',
                gapPadded_f,
            )
            plt.imsave(
                'Data\\' + str(round(time.time())) + samplename + '_segGapPad' + '.tif',
                gapPadded_thresh,
            )

        print('Finished Finding Gap Edges')

    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(
            '\n\n\n\nError on Line: '
            + str(exc_tb.tb_lineno)
            + '     Error Information: '
            + str(sys.exc_info()[:])
        )

    return gapPadded_f, gapPadded_thresh


def resizer(img, scaling_factor, samplename, path, save):
    # this function takes in an image (probably binary for our cases) and reduces the dimensions by the scaling factor

    if path is True:
        path = img
        img = cv2.imread(path, cv2.IMREAD_COLOR)

    width = int(img.shape[1] * scaling_factor)
    height = int(img.shape[0] * scaling_factor)

    resized = skimage.transform.resize(img.astype(bool), (height, width))

    if save is True:
        resized_path = (
            'Data\\'
            + str(round(time.time()))
            + samplename
            + '_resizedGapSegpad'
            + '.tif'
        )
        plt.imsave(resized_path, resized)

    return resized, resized_path


def SpanningIP(imgf, imgi, samplename, path, save=True):
    # this function condenses the image processing into one place
    try:
        if path is True:
            pathi = imgi
            pathf = imgf
            imgf = cv2.imread(pathf, cv2.IMREAD_COLOR)
            imgi = cv2.imread(pathi, cv2.IMREAD_COLOR)

        # %matplotlib inline
        # plt.imshow(imgf)
        # plt.imshow(imgi)

        binary_img = LABsegmenter(imgf, imgi, samplename, path=False, save=True)

        plt.imshow(binary_img)
        print(binary_img.dtype)

        gap_padding = 200
        gapPadded_f, gapPadded_thresh = gap_finder(
            imgi, imgf, binary_img, gap_padding, samplename, path=False, save=True
        )

        # binary_path = 'Data\\' + str(round(time.time())) + samplename + '_seg' + '.tif'
        # cv2.imwrite( binary_path, binary_img)

        gapped_path = (
            'Data\\' + str(round(time.time())) + samplename + '_gapseg' + '.tif'
        )
        cv2.imwrite(gapped_path, gapPadded_thresh)

        scaling_factor = 0.25
        resized_seg, resized_seg_path = resizer(
            gapped_path, scaling_factor, samplename, path=True, save=True
        )

        print('\nImage Processing Complete!')

    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(
            '\n\n\n\nError on Line: '
            + str(exc_tb.tb_lineno)
            + '     Error Information: '
            + str(sys.exc_info()[:])
        )

    return resized_seg_path
    # return gapped_path
    # return binary_path, gapped_path


# def VBOW_train(Responses, imagelocs, Classifier, filename):
#
# 	#Classifier --> Specify which type of classifier we will use (SVMC, Naive Bayes)
#
# 	imagelocs, Responses = shuffle(imagelocs, Responses)
#
# 	#use all data to build model to predict new samples
# 	train_img = imagelocs
# 	train_resp = Responses
#
# 	#feature types... can try all of these
# 	sift = cv2.xfeatures2d.SIFT_create()
# 	#surf = cv2.xfeatures2d.SURF_create()
# 	#orb = cv2.ORB_create(nfeatures=1500)
#
# 	descriptors_unclustered = []
#
# 	dictionarySize = 500
#
# 	BOW = cv2.BOWKMeansTrainer(dictionarySize)
#
#
# 	#step 1: Get features (SIFT descriptors)
# 	for path in train_img:
# 		img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
# 		kp, descriptor= sift.detectAndCompute(img, None)
# 		if descriptor is None:
# 			pass
# 		else:
# 			BOW.add(descriptor)
#
#
# 	#create dictionary (features of interest)
#
# 	dictionary = BOW.cluster()
#
# 	sifted = cv2.xfeatures2d.SIFT_create()
# 	vbowDictionary = cv2.BOWImgDescriptorExtractor(sifted, cv2.BFMatcher(cv2.NORM_L2))
# 	vbowDictionary.setVocabulary(dictionary)
#
# 	#now make feature histogram (vector) for training images
# 	train_features = []
# 	for path in train_img:
# 		try:
# 			img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
# 			features = vbowDictionary.compute(img, sift.detect(img))
# 			train_features.extend(features)
# 		except:
# 			print(path)
# 			train_features.extend([np.zeros([500, ])])
#
#
#
# 	#SVM Approach
# 	if Classifier == 'svm':
# 		#svm_model = cv2.SVM()
# 		svm_model = cv2.ml.SVM_create()
# 		#create training data
# 		training_stuff = cv2.ml.TrainData_create(	samples, layout, responses[, varIdx[, sampleIdx[, sampleWeights[, varType]]]]	)
# 		svm_model.train(np.array(train_desc), np.array(train_resp))
#
# 		svmc = SVC(gamma='auto')
# 		svmc = svmc.fit(train_features, train_resp)
# 		svmc_train_pred = svmc.predict(train_features)
# 		print("Number of mislabeled points out of a total %d points : %d" % (len(train_features),(train_resp != svmc_train_pred).sum()))
#
# 		#test_features = []
# 		#for path in test_img:
# 		#	try:
# 		#		img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
# 		#		tfeatures = vbowDictionary.compute(img, sift.detect(img))
# 		#		test_features.extend(tfeatures)
# 		#	except:
# 		#		print(path)
# 		#		test_features.extend([np.zeros([500, ])])
# 		#
# 		#svmc_test_pred = gnb_fitted.predict(test_features)
# 		#print("Number of mislabeled points out of a total %d points : %d.... %2.2f percent" % (len(test_features),(test_resp != svmc_test_pred).sum(), 100*(test_resp == svmc_test_pred).sum()/len(test_features)))
# 		#
# 		#confM = confusion_matrix(test_resp, svmc_test_pred)
# 		#confM = confM / confM.astype(np.float).sum(axis=0)
#
# 		clf = svmc
#
#
# 	#Naive Bayes Approach
# 	if Classifier == 'naive bayes':
# 		gnb = GaussianNB()
#
# 		gnb_fitted = gnb.fit(np.array(train_features), np.array(train_resp))
#
# 		train_pred = gnb_fitted.predict(train_features)
# 		print("Number of mislabeled points out of a total %d points : %d" % (len(train_features),(train_resp != train_pred).sum()))
#
#
# 		#test_features = []
# 		#for path in test_img:
# 		#	try:
# 		#		img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
# 		#		tfeatures = vbowDictionary.compute(img, sift.detect(img))
# 		#		test_features.extend(tfeatures)
# 		#	except:
# 		#		print(path)
# 		#		test_features.extend([np.zeros([500, ])])
# 		#
# 		#test_pred = gnb_fitted.predict(test_features)
# 		#print("Number of mislabeled points out of a total %d points : %d" % (len(test_features),(test_resp != test_pred).sum()))
# 		#
# 		#confM = confusion_matrix(test_resp, test_pred)
# 		#confM = confM / confM.astype(np.float).sum(axis=0)
#
# 		clf = gnb_fitted
#
#
#
# 	return clf


def loadDictionary(filename):

    dictionary = pickle.load(open((filename + '.pkl'), 'rb'))

    sifted = cv2.xfeatures2d.SIFT_create()
    vbowDictionary = cv2.BOWImgDescriptorExtractor(sifted, cv2.BFMatcher(cv2.NORM_L2))
    vbowDictionary.setVocabulary(dictionary)

    return vbowDictionary


def VBOW_class(model, seg_path):
    # this function imputs a model and the path to a segmented image and returns the class...

    # print('Made it here')

    vbowDictionary = loadDictionary('gap4Dictionary')

    # print('But what about here?')

    try:
        # find sift features of image
        sift = cv2.xfeatures2d.SIFT_create()
        img = cv2.imread(seg_path, cv2.IMREAD_GRAYSCALE)
        # find corresponding "visual words"
        tfeatures = vbowDictionary.compute(img, sift.detect(img))
        # test_features.extend(tfeatures)
    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(
            '\n\n\n\nError on Line: '
            + str(exc_tb.tb_lineno)
            + '     Error Information: '
            + str(sys.exc_info()[:])
        )
        print('Failure to Find Features:')
        print(seg_path)

    classification = model.predict(tfeatures)

    return classification


def saveModel(model, filename):
    # this function pickles (serializes) & saves a model so that we can load it later (w/o re-building) and predict
    # model --> trained sklearn model
    # filename --> name of file w/0 file type suffix (.pkl)
    try:
        pickle.dump(model, open((filename + '.pkl'), 'wb'))
        print('Model Save Successful')
    except Exception:
        print('Model Save Unsuccessful!!!!!!!!!!!!!!!!!!!!')


def loadModel(filename):
    # this function loads pickled model & deserializes it so we can use ti for predictions
    # filename --> name of file w/o file type suffix (.pkl)
    try:
        model = pickle.load(open((filename + '.pkl'), 'rb'))
        print('Model Load Successful')
        time.sleep(0.05)
    except Exception:
        print('Error Loading Model!!!!!!!!!!!!!!!!!!!!!!!')
        return None

    return model


def LHCgenerator(Nparams, Nsamples, criterion):
    # latin hypercube sample generation
    # Nparams = # parameteres
    # Nsamples = # samples
    # criterion tells us how to distribute the samples... Options : 'center', 'maximin', 'certermaximin', 'correlation'
    from pyDOE import lhs

    samples = lhs(Nparams, Nsamples, criterion, iterations=50)

    return samples


def gaussSampler(Nparams, Nsamples, maxSD):
    # gaussian samples of parameters from 0 mean, 1 SD single variate gaussian... Anything more than 3 SD's from mean will be rounded back to 3. This is same as sampling from multivariate gaussian with identity covariance. Idea is we will map +maxSD to the max parameter value & -maxSD to the min value & explore a finite parameter range centered on value most of interest (suspected ideal value)

    maxSD = abs(maxSD)
    samples = np.zeros([Nsamples, Nparams])

    for i in range(Nparams):
        normal_samples = np.random.normal(0, 1, Nsamples)
        samples[:, i] = normal_samples

    samples[samples > maxSD] = maxSD
    samples[samples < -maxSD] = -maxSD

    return samples
