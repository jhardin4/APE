import Devices

roseda = Devices.Roseda('roseda')
log = ''
log += roseda.Connect(key_file=r'C:\Users\GyroSpectus\Desktop\PythonGCPTest\rxms-roseda-945957c94ba8.json')
log += roseda.Upload(ufile=r'C:\Users\GyroSpectus\Desktop\PythonGCPTest\1592852764UPLOAD_ME.tar')
pause = input('Press Enter when ready for next step.')
log += roseda.Download()
log += roseda.Disconnect()

print(log)