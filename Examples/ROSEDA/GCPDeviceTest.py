import Devices
from os import path
import time

kfile = "/home/james_hardin_11/Desktop/jhardin-repos-1sud/Keys/rxms-roseda-eb7721e580d1.json"
proclog_path = "/jhardin-repos-1sud/ROSEDA_looptest/15813_new_proclog.json"
image_path = "/jhardin-repos-1sud/ROSEDA_looptest/100P_SESY_50PSI_02-09-2020-S9.png"
runtic_path = "/jhardin-repos-1sud/ROSEDA_looptest/new_RunTicket.json"
bucket = "rxms-roseda-data-jhardin"
gs_proclog_path = path.split(proclog_path)[1]
gs_image_path = path.split(image_path)[1]
gs_runtic_path = path.split(runtic_path)[1]
target = [0]
t0 = time.time()
GCP = Devices.GoogleCloudPlatform("GCP")
log = ""
log += GCP.Connect(key_file=kfile)
log += GCP.storage_upload(bucket=bucket, gs_path=gs_proclog_path, loc_path=proclog_path)
log += GCP.storage_upload(bucket=bucket, gs_path=gs_image_path, loc_path=image_path)
log += GCP.storage_upload(bucket=bucket, gs_path=gs_runtic_path, loc_path=runtic_path)

waiting = True
while waiting:
    time.sleep(10)
    log += GCP.storage_getList(bucket=bucket, address=target)
    num_files = len(target[0])
    if num_files > 0:
        downloadable = ["DOWNLOAD_ME" in n for n in target[0]]
        if all(downloadable):
            for file in target[0]:
                local_path = path.join("Data", path.split(file)[1])
                log += GCP.storage_download(bucket=bucket, gs_path=file, loc_path=local_path)
                log += GCP.storage_delete(bucket=bucket, gs_path=file)
            waiting = False


print(log)
dt = time.time() - t0
print(f"Execution took {dt} s")