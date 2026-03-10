import argparse
import csv
import os
import matplotlib.pyplot as plt

def main():
    parser = argparse.ArgumentParser(description="Plot System ID data from CSV.")
    parser.add_argument("--file", type=str, required=True, help="Name or path of the CSV data file.")
    args = parser.parse_args()

    file_path = args.file
    # Check if file exists, or if it is inside the 'data' directory
    if not os.path.exists(file_path):
        if os.path.exists(os.path.join('data', file_path)):
            file_path = os.path.join('data', file_path)
        else:
            print(f"Error: File '{file_path}' not found.")
            return

    # Extract info from filename for the title
    filename_only = os.path.basename(file_path)
    title_info = filename_only.replace(".csv", "")
    
    # Data storage
    time_data = []
    cmd_vel = []
    meas_vel = []
    meas_pos = []
    meas_load = []
    
    # Load data from CSV
    print(f"Loading data from {file_path}...")
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            time_data.append(float(row['Time (s)']))
            cmd_vel.append(float(row['Commanded Vel (raw)']))
            meas_pos.append(float(row['Measured Pos (raw)']))
            meas_vel.append(float(row['Measured Vel (raw)']))
            meas_load.append(float(row['Measured Load (raw)']))

    # Create the plot figure
    print("Generating plots...")
    fig, axs = plt.subplots(3, 1, figsize=(10, 10), sharex=True)
    fig.suptitle(f"System ID Data: {title_info}", fontsize=14)

    # Plot 1: Commanded vs Measured Velocity
    axs[0].plot(time_data, cmd_vel, label="Commanded Vel (raw)", linestyle='--', color='blue')
    axs[0].plot(time_data, meas_vel, label="Measured Vel (raw)", alpha=0.8, color='cyan')
    axs[0].set_ylabel("Velocity")
    axs[0].set_title("Commanded vs Measured Velocity")
    axs[0].legend(loc="upper right")
    axs[0].grid(True)

    # Plot 2: Measured Position
    axs[1].plot(time_data, meas_pos, label="Measured Pos (raw)", color='orange')
    axs[1].set_ylabel("Position")
    axs[1].set_title("Raw Measured Position")
    axs[1].legend(loc="upper right")
    axs[1].grid(True)

    # Plot 3: Measured Load (Torque)
    axs[2].plot(time_data, meas_load, label="Measured Load (raw)", color='green')
    axs[2].set_ylabel("Load (Torque)")
    axs[2].set_xlabel("Time (s)")
    axs[2].set_title("Measured Load / Torque")
    axs[2].legend(loc="upper right")
    axs[2].grid(True)

    plt.tight_layout()
    
    # Save the plot nicely organized in the 'plots' folder
    plots_dir = "plots"
    os.makedirs(plots_dir, exist_ok=True)
    plot_filename = os.path.join(plots_dir, f"plot_{title_info}.png")
    
    plt.savefig(plot_filename)
    print(f"Success! Plot saved nicely to: {plot_filename}")

if __name__ == "__main__":
    main()