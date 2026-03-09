%% Force Experienced by Load cell %%
g = 9.81;
F_t = 0.2; % Thrust force in Newtons
L_t = 0.4129; % Distance from pivot to applied thrust force in meters
L_lc = 0.0115; % Distance from pivot to load cell in meters
F_lc = F_t*L_t/L_lc; % Perceived load in Newtons
F_lc_kg = F_lc/g;
fprintf("Perceived Load Cell Load = %.6f N\n", F_lc);
fprintf("Perceived Load Cell Load = %.6f kg\n", F_lc_kg);

%% Conversion from Perceived Load to Real Load %%

F_lc_kg = 5; %This is where load cell data goes

g = 9.81;
L_t = 0.4129; % Distance from pivot to applied thrust force in meters
L_lc = 0.0115; % Distance from pivot to load cell in meters
F_t_kg = F_lc_kg*L_lc/L_t; %outputs thrust force in kg
F_t_N = F_t_kg*g; %converts thrust force to N
fprintf("Thrust Force = %.6f N\n", F_t_N);
fprintf("Thrust Force = %.6f kg\n", F_t_kg);