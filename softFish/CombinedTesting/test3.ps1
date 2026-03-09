#need to run this in commandshell before running:  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#run this in commandshell to run script: ./MultiTestAgentUpdate.ps1
# Define working directory
#only change is defining a new script (script 1) for the cameracontrol2.py file
#$scriptDir = "C:\Users\15405\OneDrive\Desktop\Career\ETHZ\ETHZ Work\Dynamixel_Control\softFish\CombinedTesting"
$scriptDir = "/home/srl-slim-tim/Dynamixel_Control/softFish/CombinedTesting"
$scriptDir_2 = "/home/srl-slim-tim/Dynamixel_Control/softFish"

#this value will be changed between 1-4 and this will reflect in all other relates files
$frequency = "2.0"

Write-Host "removing old signal files"

Remove-Item "$scriptDir/stop_signal.txt" -ErrorAction SilentlyContinue
Remove-Item "$scriptDir/camera_started.txt" -ErrorAction SilentlyContinue
Remove-Item "$scriptDir/motor_ended.txt" -ErrorAction SilentlyContinue
Remove-Item "$scriptDir/motor_control_ended.txt" -ErrorAction SilentlyContinue

Write-Host "script names"
# Define script names
$script1 = "camtest.py"
$script2 = "ForceTimeSerialComm.py"
$script3 = "positionControl2.py" #had been positionControl

Write-Host "starting camera"
# Start Job 1: Camera control
$job1 = Start-Job { Set-Location $using:scriptDir; python $using:script1 "$using:frequency" }

Write-Host "waiting for starting camera"
# Wait for camera start signal file
while (-not (Test-Path "$scriptDir/camera_started.txt")) {
    Start-Sleep -Milliseconds 200
}

Write-Host "Camera started, now starting other jobs..."

