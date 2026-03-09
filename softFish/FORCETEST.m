%script that parses through my test data for force vs time of the static fish setup, then it saves each force vs. time graph as a figure into my local file
%read in data 
for index=1:.2:4
    figure;  % creates a new figure each loop
    loop_max=0;
    % Round index to 1 decimal place to avoid floating point issues
    roundedIndex = round(index, 1);
    filename = sprintf("C:\\Users\\15405\\OneDrive\\Desktop\\Career\\ETHZ\\ETHZ Work\\HardwareOutput\\%.1f.csv", roundedIndex);
    data = readtable(filename);

    % Extract column 2 as strings, force, row 2 to match with the row for
    % time, and to avoid NaN in metaData
    rawForce = string(data{2:end, 1});

    % Clean: remove 'kg' and whitespace
    cleanForce = str2double(erase(lower(strtrim(rawForce)), "kg"))
    
    %cleans up time data 
    rawTime = string(data{2:end, 2});
    cleanTime=str2double(rawTime)
    
    %plots force vs time for each respective hertz
    plot(cleanTime,cleanForce)
    title(sprintf('%.1f Hz: Time vs Force', roundedIndex));
    xlabel('Time (s)');
    ylabel('Force (kg)');
    % Save figure to its respective folder
    folder = 'C:\Users\15405\OneDrive\Desktop\Career\ETHZ\ETHZ Work\HardwareOutput';
    filenameFig = fullfile(folder, sprintf('%.1f_HZ_TimevsForce.fig', roundedIndex));
    saveas(gcf, filenameFig);
end