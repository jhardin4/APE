# This Device is for interacting with the ROSEDA GCP project and will not work
# for others.

# Only import 'basic' python packages up here.  All others should be imported
# within the methods.
import time
import os
import json

from Devices import Device



class Roseda(Device):
    def __init__(self, name):
        # Run the Device initialization.
        Device.__init__(self, name)
        # Run simulation is controlled by its own
        # Append relevant descriptors
        self.descriptors.append('GCP')
        self.descriptors.append('roseda')
        self.descriptors.append('repository')
        # Defining the elemental procedures
        self.requirements['Connect']['key_file'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'key json',
        }
        self.requirements['Upload'] = {}
        self.requirements['Upload']['ufile'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'file or list of files to be uploaded',
        }

        self.requirements['Download'] = {}
        self.requirements['Download']['address'] = {
            'value': '',
            'source': 'direct',
            'address': '',
            'desc': 'address of the program or pointer to it',
        }
        self.heartbeat = 2
        self.timeout = 60

    def Connect(self, key_file=''):
        bucket_name = 'undefined'
        if not self.simulation:
            from google.cloud import storage
            with open(key_file) as kfile:
                key = json.load(kfile)
            bucket_name = 'rxms-roseda-data-' + key["client_email"].split('@')[0].replace('ape-', '')
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key_file
            self.storage_client = storage.Client()
            self.bucket = self.storage_client.bucket(bucket_name)
        self.addlog(f'{self.name} connected to {bucket_name}')

        return self.returnlog()

    def Upload(self, ufile=''):
        
        if not self.simulation:
            if type(ufile) == str:
                # print(ufile)
                # print(f'{os.path.split(ufile)}')
                blob = self.bucket.blob(os.path.split(ufile)[1])
                blob.upload_from_filename(ufile)
            else:
                for file in ufile:
                    blob = self.bucket.blob(os.path.split(file)[1])
                    blob.upload_from_filename(file)                   

            keep_waiting = True
            time_start = time.time()
            
            while keep_waiting:
                all_blobs = list(self.bucket.list_blobs())
                files_left = 0    
            
                for blob in all_blobs:
                    if 'DOWNLOAD_ME' not in blob.name:
                        files_left += 1
            
                if files_left == 0:
                    keep_waiting = False
            
                if time.time() - time_start > self.timeout:
                    keep_waiting = False
                    raise Exception('Upload timed out')
            
                time.sleep(self.heartbeat)
        self.addlog(f'{self.name} uploaded {ufile}')

        return self.returnlog()

    def Download(self):
        if not self.simulation:
            keep_waiting = True
            time_start = time.time()
            dlist = []
            
            while keep_waiting:
                all_blobs = list(self.bucket.list_blobs())
                found_file = False  
            
                for blob in all_blobs:
                    if 'DOWNLOAD_ME' in blob.name:
                        found_file = True
                        blob.download_to_filename(blob.name.split('/')[-1])
                        blob.delete()
                        dlist.append(blob.name)
                        
                if found_file:
                    keep_waiting = False
            
                if time.time() - time_start > self.timeout:
                    keep_waiting = False
                    raise Exception('Download timed out')
            
                time.sleep(self.heartbeat)
        self.addlog(f'{self.name} downloaded {dlist}')

        return self.returnlog()
