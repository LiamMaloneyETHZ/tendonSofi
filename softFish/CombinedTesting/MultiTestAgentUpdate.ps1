#need to run this in commandshell before running:  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#run this in commandshell to run script: ./MultiTestAgentUpdate.ps1
# Define working directory
#only change is defining a new script (script 1) for the cameracontrol2.py file
#$scriptDir = "C:\Users\15405\OneDrive\Desktop\Career\ETHZ\ETHZ Work\Dynamixel_Control\softFish\CombinedTesting"
$scriptDir = "/home/srl-slim-tim/Dynamixel_Control/softFish/CombinedTesting"
$scriptDir_2 = "/home/srl-slim-tim/Dynamixel_Control/softFish"

#this value will be changed between 1-4 and this will reflect in all other relates files
$frequency = "2.0"

Remove-Item "$scriptDir/stop_signal.txt" -ErrorAction SilentlyContinue
Remove-Item "$scriptDir/camera_started.txt" -ErrorAction SilentlyContinue
Remove-Item "$scriptDir/motor_ended.txt" -ErrorAction SilentlyContinue
Remove-Item "$scriptDir/motor_control_ended.txt" -ErrorAction SilentlyContinue

# Define script names
$script1 = "CameraControl2.py"
$script2 = "ForceTimeSerialComm.py"
$script3 = "positionControl2.py" #had been positionControl

# Start Job 1: Camera control
$job1 = Start-Job { Set-Location $using:scriptDir; python $using:script1 "$using:frequency" }

# Wait for camera start signal file
while (-not (Test-Path "$scriptDir\camera_started.txt")) {
    Start-Sleep -Milliseconds 200
}

Write-Host "Camera started, now starting other jobs..."

# Start Job 2: Force sensor serial logging
$job2 = Start-Job { Set-Location $using:scriptDir; python $using:script2 "$using:frequency" }
Start-Sleep -Seconds .15

# Start Job 3: Motor control (this job will govern when everything ends)
$job3 = Start-Job { Set-Location $using:scriptDir_2; python $using:script3 "$using:frequency" }

# Wait for motor control to finish, not including returning back to the start 
#Wait-Job -Id $job3.Id
while (-not (Test-Path "$scriptDir\motor_control_ended.txt")){
    Start-Sleep -Milliseconds 200
}

# Send signal to stop camera
New-Item -Path "$scriptDir\stop_signal.txt" -ItemType File -Force

Write-Host "Motor control sent stop signal, stopping camera and force logging jobs..."

# Once motor control ends, stop the other jobs
Stop-Job -Id $job1.Id, $job2.Id

# Now wait for job 3 (motor control) to finish naturally
Wait-Job -Id $job3.Id

Write-Host "Motor control finished."

# Get outputs
$output1 = Receive-Job -Id $job1.Id
$output2 = Receive-Job -Id $job2.Id
$output3 = Receive-Job -Id $job3.Id

# Cleanup jobs
Remove-Job -Id $job1.Id, $job2.Id, $job3.Id

# Display outputs
Write-Host "`n=== Output from Job 1 (CameraControl2.py) ==="
Write-Output $output1

Write-Host "`n=== Output from Job 2 (ForceTimeSerialComm.py) ==="
Write-Output $output2

Write-Host "`n=== Output from Job 3 (positionControl2.py) ==="
Write-Output $output3
