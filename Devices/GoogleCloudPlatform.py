# This Device is for interacting with the Google Cloud Platform.  For now
# it only handles some Google Storage Functionality

# Only import "basic" python packages up here.  All others should be imported
# within the methods.
import time
import os
import json

from Devices import Sensor


class GoogleCloudPlatform(Sensor):
    def __init__(self, name):
        # Run the Device initialization.
        Sensor.__init__(self, name)
        # Run simulation is controlled by its own
        # Append relevant descriptors
        self.descriptors.append("GCP")
        # Defining the elemental procedures
        self.requirements["Connect"]["key_file"] = {
            "value": "",
            "source": "apparatus",
            "address": "",
            "desc": "key json",
        }

        self.requirements["storage_upload"] = {}
        self.requirements["storage_upload"]["bucket"] = {
            "value": "",
            "source": "apparatus",
            "address": "",
            "desc": "Storage bucket ot interact with",
        }
        self.requirements["storage_upload"]["gs_path"] = {
            "value": "",
            "source": "apparatus",
            "address": "",
            "desc": "Google Storage path",
        }
        self.requirements["storage_upload"]["loc_path"] = {
            "value": "",
            "source": "apparatus",
            "address": "",
            "desc": "local path",
        }

        self.requirements["storage_download"] = {}
        self.requirements["storage_download"]["bucket"] = {
            "value": "",
            "source": "apparatus",
            "address": "",
            "desc": "Storage bucket ot interact with",
        }
        self.requirements["storage_download"]["gs_path"] = {
            "value": "",
            "source": "apparatus",
            "address": "",
            "desc": "Google Storage path",
        }
        self.requirements["storage_download"]["loc_path"] = {
            "value": "",
            "source": "apparatus",
            "address": "",
            "desc": "local path",
        }

        self.requirements["storage_delete"] = {}
        self.requirements["storage_delete"]["bucket"] = {
            "value": "",
            "source": "apparatus",
            "address": "",
            "desc": "Storage bucket ot interact with",
        }
        self.requirements["storage_delete"]["gs_path"] = {
            "value": "",
            "source": "apparatus",
            "address": "",
            "desc": "Google Storage path",
        }

        self.requirements["storage_getList"] = {}
        self.requirements['storage_getList']['address'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'Address of where to store result',
        }
        self.requirements['storage_getList']['addresstype'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'Type of address',
        }
        self.requirements["storage_getList"]["bucket"] = {
            "value": "",
            "source": "apparatus",
            "address": "",
            "desc": "Storage bucket ot interact with",
        }

    def Connect(self, key_file=""):
        if not self.simulation:
            from google.cloud import storage, bigquery, pubsub_v1
            from google.oauth2 import service_account
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_file
            credentials = service_account.Credentials.from_service_account_file(
                key_file, scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )
            self.bqClient = bigquery.Client(credentials=credentials, project=credentials.project_id,)
            self.gsClient = storage.Client(credentials=credentials, project=credentials.project_id,)
            self.psClient = pubsub_v1.PublisherClient(credentials=credentials,)
        self.addlog(f"{self.name} connected to GCP")

        return self.returnlog()

    def storage_upload(self, bucket="", gs_path="", loc_path=""):
        if not self.simulation:
            outBucket = self.gsClient.bucket(bucket)
            blob = outBucket.blob(gs_path)
            blob.upload_from_filename(loc_path)

        self.addlog(f"{self.name} uploaded {loc_path}")

        return self.returnlog()

    def storage_download(self, bucket="", gs_path="", loc_path=""):
        if not self.simulation:
            outBucket = self.gsClient.bucket(bucket)
            blob = outBucket.blob(gs_path)
            blob.download_to_filename(loc_path)

        self.addlog(f"{self.name} downloaded {loc_path}")

        return self.returnlog()

    def storage_delete(self, bucket="", gs_path=""):
        if not self.simulation:
            outBucket = self.gsClient.bucket(bucket)
            blob = outBucket.blob(gs_path)
            blob.delete()

        self.addlog(f"{self.name} deleted {gs_path}")

        return self.returnlog()

    def storage_getList(self, address="", addresstype="", bucket=""):
        if addresstype == "":
            addresstype = "pointer"
        result = "No postion collected"
        # Get the postion from the driver
        if not self.simulation:
            outBucket = self.gsClient.bucket(bucket)
            result = [r.name for r in outBucket.list_blobs()]

        # Store it at the target location
        self.StoreMeasurement(address, addresstype, result)
        self.addlog(f"{bucket} contains {result}")

        return self.returnlog()

