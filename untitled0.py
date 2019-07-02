# -*- coding: utf-8 -*-
"""
Created on Mon May 27 07:41:08 2019

@author: casey
"""

#import json
#
## read file
#with open('C:/Users/casey/OneDrive/Desktop/APE GUI/Logs/copy.json', 'r') as myfile:
#    data=myfile.read()



import json
from pprint import pprint

with open('C:/Users/casey/OneDrive/Desktop/APE GUI/Logs/1558733917Apparatus.json') as f:
    data = json.load(f)

pprint(data)