import argparse
import csv
import os
import matplotlib.pyplot as plt

# Enable LaTeX for text rendering
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"]
})

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
            
            # Phase wrap the position (Dynamixel XL430 is 4096 pulses/rev)
            raw_pos = float(row['Measured Pos (raw)'])
            meas_pos.append(raw_pos % 4096)
            
            meas_vel.append(float(row['Measured Vel (raw)']))
            meas_load.append(float(row['Measured Load (raw)']))

    # Create the plot figure
    print("Generating plots...")
    
    # Scientific paper style sizes
    mm = 1 / 25.4
    fig, axs = plt.subplots(3, 1, figsize=(88*mm, 120*mm), sharex=True)
    
    # We remove the suptitle as it usually isn't in paper figures, 
    # but you can add it back if you want.
    
    # Plot 1: Commanded vs Measured Velocity
    axs[0].plot(time_data, cmd_vel, linestyle='--', color="tab:blue", label='Cmd Vel')
    axs[0].plot(time_data, meas_vel, linestyle='-', color="tab:orange", alpha=0.8, label='Meas Vel')
    axs[0].set_ylabel("Velocity")
    axs[0].legend(loc="upper center", ncol=2, fancybox=True, bbox_to_anchor=(0.5, 1.35))
    axs[0].grid(True)

    # Plot 2: Measured Position (Phase Wrapped)
    axs[1].plot(time_data, meas_pos, linestyle='-', color="tab:green", label='Meas Pos')
    axs[1].set_ylabel("Pos (Wrapped 0-4095)")
    axs[1].legend(loc="upper center", ncol=1, fancybox=True, bbox_to_anchor=(0.5, 1.25))
    axs[1].grid(True)

    # Plot 3: Measured Load (Torque)
    axs[2].plot(time_data, meas_load, linestyle='-', color="tab:red", label='Meas Load')
    axs[2].set_ylabel("Load (Torque)")
    axs[2].set_xlabel("Time (s)")
    axs[2].legend(loc="upper center", ncol=1, fancybox=True, bbox_to_anchor=(0.5, 1.25))
    axs[2].grid(True)

    # Adjust layout to prevent legends from overlapping
    plt.subplots_adjust(hspace=0.5)
    
    # Save the plot nicely organized in the 'plots' folder
    plots_dir = "plots"
    os.makedirs(plots_dir, exist_ok=True)
    
    plot_filename_png = os.path.join(plots_dir, f"plot_{title_info}.png")
    plot_filename_pdf = os.path.join(plots_dir, f"plot_{title_info}.pdf")
    
    fig.savefig(plot_filename_png, dpi=300, bbox_inches="tight")
    fig.savefig(plot_filename_pdf, bbox_inches="tight")
    plt.close(fig)
    
    print(f"Success! Plots saved nicely to:\n  - {plot_filename_png}\n  - {plot_filename_pdf}")

if __name__ == "__main__":
    main()