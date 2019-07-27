import pickle
import cv2


def loadDictionary(filename):

    dictionary = pickle.load(open((filename + '.pkl'), 'rb'))

    sifted = cv2.xfeatures2d.SIFT_create()
    vbowDictionary = cv2.BOWImgDescriptorExtractor(sifted, cv2.BFMatcher(cv2.NORM_L2))
    vbowDictionary.setVocabulary(dictionary)

    return vbowDictionary
