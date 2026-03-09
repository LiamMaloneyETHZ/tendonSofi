import csv

input_file = "/home/srl-slim-tim/ForceTest/20250805_1620_f0.6Hz_force_test_data.csv"
output_file = "/home/srl-slim-tim/ForceTest/adjusted_20250805_1620_f0.6Hz_force_test_data.csv"



with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
    reader = list(csv.reader(infile))
    writer = csv.writer(outfile)

    # Write header lines unchanged
    writer.writerow(reader[0])  # Frequency and start time
    writer.writerow(reader[1])  # Column headers
    writer.writerow(["Time (s)", "Force (Kg)"])  # Column headers

    data_rows = reader[2:]

    if len(data_rows) < 2:
        print("Not enough data rows to adjust.")
        exit()

    # Use the second data row as the time offset
    t0 = float(data_rows[1][1])  # second row (index 1)

    # Process all rows starting from the second (inclusive)
    for row in data_rows[1:]:
        force_val = row[0]
        adjusted_time = float(row[1]) - t0
        writer.writerow([force_val, adjusted_time])