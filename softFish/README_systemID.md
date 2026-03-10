# System Identification for Tendon-Actuated Tail

The `systemID_velocity.py` script is designed to perform system identification on the nonlinear tendon-actuated tail mechanism. It allows you to command the Dynamixel motor at a specific target frequency (using velocity control) for a set duration, while recording high-resolution data of the motor's actual position, velocity, and load.

## Prerequisites

Ensure you have your environment set up with the required Dynamixel SDK and other Python dependencies. The motor should be connected to the system.

## How to Use

To run an experiment, you must navigate into the `softFish` directory and execute the script from your terminal using Python, providing the desired `--freq` (in Hz) and `--duration` (in seconds).

### Step 1: Navigate to the directory
```bash
cd softFish/
```

### Step 2: Run the script
Run the script by passing the target frequency and duration flags. For example, to command a 2.0 Hz motion for 10.0 seconds:

```bash
python systemID_velocity.py --freq 2.0 --duration 10.0
```

#### Running a Chirp (Frequency Sweep)
To perform a frequency sweep over time and gather data across a spectrum of frequencies, use the chirp script:

```bash
python systemID_chirp.py --freq_start 0.5 --freq_end 3.0 --duration 30.0
```

### Output

While the script is running, it continuously records data into memory to prevent file I/O operations from slowing down the control loop. 

Once the experiment finishes (or if you manually interrupt it with `Ctrl+C`), the script will automatically stop the motor, disable torque, and save the recorded data to a `.csv` file in the same directory.

The generated CSV file will have a name formatted like:
`sysID_velControl_[FREQ]Hz_[DURATION]s_[YYYY-MM-DD_HH-MM-SS].csv`
*(e.g., `sysID_velControl_2.0Hz_10.0s_2026-03-10_14-30-00.csv`)*
The files will be saved nicely inside a `data/` directory.

**Data logged in the CSV includes:**
*   `Time (s)`: Elapsed time since the start of the experiment.
*   `Target Freq (Hz)`: The frequency you requested.
*   `Commanded Vel (raw)`: The raw velocity command sent to the Dynamixel.
*   `Measured Pos (raw)`: The actual position read from the motor.
*   `Measured Vel (raw)`: The actual velocity read from the motor.
*   `Measured Load (raw)`: The actual load/current read from the motor, which is useful for analyzing tendon tension.

## Visualizing the Data

To automatically plot the results of your experiment, a `plot_systemID.py` script is provided. It reads the generated CSV and creates three subplots: Commanded vs Measured Velocity, Measured Position, and Measured Load (Torque).

Run the plotting script by passing the filename (it will automatically search in the `data/` folder):

```bash
python plot_systemID.py --file sysID_velControl_2.0Hz_10.0s_2026-03-10_14-30-00.csv
```

The script will generate a PNG image of the plot and save it nicely organized inside a `plots/` directory.