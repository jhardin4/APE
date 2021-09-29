from Core import Procedure
import json, random, time, os
from Procedures import User_Consol_Input

class ROSEDA_getResults(Procedure):
    def Prepare(self):
        self.name = "ROSEDA_getResults"
        self.requirements["bucket"] = {
            "source": "direct",
            "address": "",
            "value": "",
            "desc": "GCP bucket to interact with"
        }
        self.requirements["run_ticket"] = {
            "source": "direct",
            "address": "",
            "value": "",
            "desc": "local path to run ticket"
        }
        self.requirements["proclog"] = {
            "source": "direct",
            "address": "",
            "value": "",
            "desc": "local path to procedure log"
        }
        self.requirements["image"] = {
            "source": "direct",
            "address": "",
            "value": "",
            "desc": "local path to image"
        }
        self.requirements["results_address"] = {
            "source": "apparatus",
            "address": "",
            "value": [
                "information",
                "ProcedureData",
                "ROSEDA_getResults",
                "result",
            ],
            "desc": "Apparatus Address to store information in",
        }
        self.apparatus.createAppEntry(self.requirements["results_address"]["value"])
        self.userinput = User_Consol_Input(self.apparatus, self.executor)

    def Plan(self):
        # Determine if the GCP Device is operating in this thread
        GCP_name = self.apparatus.findDevice(descriptors="GCP")
        if GCP_name == "No devices met requirments":
            sneaker_net = True
        else:
            sneaker_net = False
            com_type = self.apparatus.getValue(["devices", GCP_name, "addresstype"])
    
            # Setup the communication variables
            if com_type == "pointer":
                temp_target = [0]
                address = temp_target
                addresstype = "pointer"
            elif com_type == "zmqNode":
                address = {"global": "appa", "AppAddress": self.target}
                addresstype = "zmqNode_AppAddress"

        # This pattern assumes a run with multiple ROSEDA_TestMaterial procs
        # and associated image. It also assume you only want to send the most
        # recent

        # Handle proclog by picking out the right ROSEDA_TestMaterial and
        # Camera_Capture_Image entries in proclog
        # Get the proclog data
        if self.proclog == "":
            old_proclog_data = self.apparatus.getLog()
        else:
            with open(self.proclog) as file:
                old_proclog_data = json.load(file)
        # Find the latest ROSEDA_TestMaterial
        old_proclog_data.reverse()

        roseda_lines = []
        camera_lines = []
        found_first_roseda = False
        found_last_roseda = False
        found_first_camera = False
        found_last_camera = False

        for m, line in enumerate(old_proclog_data):
            num_arrows = len(line) - 1
            proc = line[-1]
            if proc["name"] == "ROSEDA_TestMaterial" and not found_last_roseda:
                roseda_base_arrows = num_arrows-1
                roseda_lines = []
                roseda_lines.append(["->", proc])
                found_last_roseda = True
            elif proc["name"] in "ROSEDA_TestMaterial" and found_last_roseda:
                roseda_lines.append(["->", proc])
                found_first_roseda = True
            elif (proc["name"] == "Camera_Capture_Image" and
                  not found_last_camera and
                  not found_first_roseda):
                camera_base_arrows = num_arrows-1
                camera_lines = []
                camera_lines.append(["->", proc])
                found_last_camera = True
            elif (proc["name"] == "Camera_Capture_Image" and
                  found_last_camera and
                  not found_first_roseda):
                camera_lines.append(["->", proc])
                found_first_camera = True
                # Bookmark the proc holding image data
                image_line = proc
                # This means it will reset the camera_lines if at finds another
                found_last_camera = False
            elif found_last_roseda and not found_first_roseda:
                roseda_lines.append(line[roseda_base_arrows:])
            elif found_last_camera:
                camera_lines.append(line[camera_base_arrows:])

        proclog_data = [*camera_lines, *roseda_lines]
        proclog_data.reverse()

        # Handle image
        if self.image == "":
            self.image = image_line["requirements"]["file"]["value"]

        # Handle runticket
        # Get runticket data
        if self.run_ticket == "":
            old_run_ticket_data = self.apparatus.getTicket()
        else:
            with open(self.run_ticket) as file:
                old_run_ticket_data = json.load(file)

        # remove all image and end ticket lines 
        run_ticket_data = []
        for line in old_run_ticket_data:
            if "end_ticket" in line:
                pass
            elif "image" in line:
                pass
            else:
                run_ticket_data.append(line)
        # add in fake end_ticket, image, and workticket_key entries
        rand_number = random.randint(0, 99999999) / 10**8
        workticket_keys = {"rxms-roseda-AIRheoCalc": {"report": self.bucket}}
        workticket_entry = {"workticket_keys": workticket_keys, "ticket_time": rand_number}
        run_ticket_data.append({"image": self.image, "ticket_time": rand_number})
        run_ticket_data.append(workticket_entry)
        run_ticket_data.append({"end_ticket": rand_number})

        # Make Files
        time_stamp = round(time.time())
        proc_file_name = f"{time_stamp}_proclog.json"
        proc_file_path = os.path.join("Data", proc_file_name)
        with open(proc_file_path, mode="w") as file:
            json.dump(proclog_data, file)

        runtic_file_name = f"{time_stamp}_RunTicket.json"
        runtic_file_path = os.path.join("Data", runtic_file_name)
        with open(runtic_file_path, mode="w") as file:
            json.dump(run_ticket_data, file)

        file_list = [self.image, proc_file_path, runtic_file_path]
        if sneaker_net:
            message = f"Upload to {self.bucket} the following files:"
            for file in file_list:
                message += f"\n{file}"
            message += "\nThen put the DOWNLOAD ME file in the Data directory"
            message += " and type the file name below."
            default = ""
            self.userinput.Do({"message": message, "default": default})
            results_file_path = os.path.join("Data", self.userinput.response)
        else:
            details = {"bucket": self.bucket, "gs_path": proc_file_path, "loc_path": proc_file_path}
            self.DoEproc(GCP_name, "storage_upload", details)
            details = {"bucket": self.bucket, "gs_path": self.image, "loc_path": self.image}
            self.DoEproc(GCP_name, "storage_upload", details)
            details = {"bucket": self.bucket, "gs_path": runtic_file_path, "loc_path": runtic_file_path}
            self.DoEproc(GCP_name, "storage_upload", details)

            waiting = True
            # This loop probably won't work with zmqNodes
            while waiting:
                # This needs to be switched to a system dwell
                time.sleep(10)
                self.DoEproc(GCP_name, "storage_getList", {"bucket": self.bucket, "address": address})
                num_files = len(address[0])
                if num_files > 0:
                    downloadable = ["DOWNLOAD_ME" in n for n in address[0]]
                    if all(downloadable):
                        for file in address[0]:
                            results_file_path = os.path.join("Data", os.path.split(file)[1])
                            details = {"bucket": self.bucket, "gs_path": file, "loc_path": results_file_path}
                            self.DoEproc(GCP_name, "storage_download", details)
                            details = {"bucket": self.bucket, "gs_path": file}
                            self.DoEproc(GCP_name, "storage_delete", details)
                        waiting = False            
        # Rename Runticket to prvent automation issues
        os.rename(runtic_file_path, runtic_file_path.replace("RunTicket", "Run_Ticket"))
        # Open file and put data in target location
        with open(results_file_path) as file:
            results_data = json.load(file)
        self.apparatus.setValue(self.results_address, results_data)
        