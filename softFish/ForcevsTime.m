filename = '/home/srl-slim-tim/ForceTest/ForceTest2/20250806_1222_f0.1Hz_force_test_data.csv';

% Extract text between 'f' and 'Hz'
freqStr = extractBetween(filename, 'f', 'Hz');  % This returns a string array between f and hZ

% Convert to double
freq = str2double(freqStr);
freqFormatted = sprintf('%.1f', freq);
% Display
disp(freqFormatted);



%could use a string to find it % <-- Replace with actual test frequency (Hz)
roundedIndex = round(freq); % This is used for naming the file

% ==== READ DATA ====
data = readtable(filename);

% ==== CLEAN FORCE DATA (Column 1) ====
rawForce = string(data{2:end, 1});
cleanForce = str2double(erase(lower(strtrim(rawForce)), "kg"));

% ==== CLEAN TIME DATA (Column 2) ====
rawTime = string(data{2:end, 2});
cleanTime = str2double(strtrim(rawTime));
firstTime = cleanTime(1);
cleanTime=cleanTime-firstTime %removes offset from first

% ==== PLOT ====
figure;
plot(cleanTime, cleanForce, 'LineWidth', 1.5);
title(sprintf('%.1f Hz: Time vs Force', freq));
xlabel('Time (s)');
ylabel('Force (kg)');
grid on;

% ==== SAVE FIGURE ====
outputFolder = '/home/srl-slim-tim/ForceTest/ForceGraphs';
if ~exist(outputFolder, 'dir')
mkdir(outputFolder);
end

figName = sprintf('%d_HZ_TimevsForce.fig', roundedIndex);
savefig(fullfile(outputFolder, figName));



