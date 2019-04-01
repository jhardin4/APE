# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 12:14:14 2019

@author: jhardin
"""

from multiprocessing import Process
import time

def testthing():
    while True:
        print('bleh')
        time.sleep(5)
    
    
def main():
    testproc = Process(target=testthing)
    testproc.start()
    print(str(testproc.is_alive()))
    time.sleep(15)
    print(str(testproc.is_alive()))
    testproc.terminate()
    time.sleep(1)
    print(str(testproc.is_alive()))
    

if __name__=='__main__':
    main()