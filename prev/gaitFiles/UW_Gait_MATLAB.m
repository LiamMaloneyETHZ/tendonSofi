%% gait params
cycles_per_exp = 20;

gait_para.Amp = 50; % Angular amplitude lateral wave
gait_para.spFreq = 0.8; % number of waves along the body (spatial frequency lateral wave)
gait_para.tmFreq = 15.0; % temporal frequency (Hz)

passiveness = 0; %  value from 0(fully active) to 1(fully passive)
LargeTorqueStopQ = false;
LargeTorqueReactionQ = false;

control_mode = 2;

% Data Byte Length
LEN_PRO_GOAL_POSITION        = 4;
LEN_PRO_PRESENT_POSITION     = 4;
LEN_PRO_PRESENT_LOAD         = 2;

NUM_BODY_SERVOS             = 6;
ID                          = 1:NUM_BODY_SERVOS;
COMM_SUCCESS                = 0;            % Communication Success result value
COMM_TX_FAIL                = -1001;        % Communication Tx Failed

%these look unused
DXL_MAXIMUM_MOVING_SPEED    = 0;            % Dynamixel maximum moving speed value
DXL_MOVING_STATUS_THRESHOLD = 10;           % Dynamixel moving status threshold

dxl_comm_result = COMM_TX_FAIL;             % Communication result
dxl_error = 0;                              % Dynamixel error
dxl_present_position = [];                  % Present position
dxl_present_load = [];                      % Present load
dxl_present_time = [];                      % Present time

POS_0_DEG                   = load('pos_0.mat').POS_0_DEG;
POS_OFFSET                  = POS_0_DEG + 18171*cos(0.5903);
POS_MAX                     = zeros(1,NUM_BODY_SERVOS);
POS_MIN                     = zeros(1,NUM_BODY_SERVOS);

extra_to_give = 1000;

for k = 1:NUM_BODY_SERVOS/2
    POS_MIN(2*k) = -18171*cos(-90/180*pi/2 + 0.5903) + POS_OFFSET(2*k)-extra_to_give;
    POS_MAX(2*k-1) = -18171*cos(90/180*pi/2 + 0.5903) + POS_OFFSET(2*k-1)-extra_to_give;
    
    POS_MIN(2*k-1) = -18171*cos(-90/180*pi/2 + 0.5903) + POS_OFFSET(2*k-1)-extra_to_give;
    POS_MAX(2*k) = -18171*cos(-(-90)/180*pi/2 + 0.5903) + POS_OFFSET(2*k)-extra_to_give;
end

% Initialize Groupbulkread Structs
group_num_read_position = groupSyncRead(port_num, PROTOCOL_VERSION, ADDR_PRO_PRESENT_POSITION, LEN_PRO_PRESENT_POSITION);
group_num_read_load = groupSyncRead(port_num, PROTOCOL_VERSION, ADDR_PRO_PRESENT_LOAD, LEN_PRO_PRESENT_LOAD);
group_num_write = groupSyncWrite(port_num, PROTOCOL_VERSION, ADDR_PRO_GOAL_POSITION, LEN_PRO_GOAL_POSITION);
dxl_addparam_result = false;                % AddParam result
dxl_getdata_result = false;                 % GetParam result

%% Gait definition, motor position trajectory generation
% Serpenoid wave parameters
A = gait_para.Amp; % Angular amplitude lateral wave
omega_s = gait_para.spFreq; % number of waves along the body / spatial frequency lateral wave
N = NUM_BODY_SERVOS/2; % Number of joints
omega_t = gait_para.tmFreq; % Hz / temporal frequency

fraction = passiveness * 2 - 1;
gamma = fraction * gait_para.Amp;

t = 0; % initialize time
dt = 0.001; %.001 time steps
angle = []; % motor angles for lateral wave
motor_pos_decimal = []; % motor positions for lateral wave
motor_pos_hex = []; % motor positions for lateral wave
full_cycle_steps = (1/omega_t)/dt; % timesteps for one full cycle
all_steps = full_cycle_steps*cycles_per_exp; % timesteps for all cycles

for k = 1:N
    for i = 1:all_steps
        angle(k,i) = A*sin(2*pi*omega_s*(k)/(N) - 2*pi*omega_t*t);
        
        % ------ hardcoded angle correction ------
%         if angle(k,i) <= 0
%             angle(k,i) = angle(k,i)+angle(k,i)*25/90;
%         end
        % ----------------------------------------
        motor_pos_decimal_original(2*k-1,i) = -18171*cos(angle(k,i)/180*pi/2 + 0.5903) + POS_OFFSET(2*k-1);
        motor_pos_decimal_original(2*k,i) = -18171*cos(-angle(k,i)/180*pi/2 + 0.5903) + POS_OFFSET(2*k);

        if control_mode == 1
            motor_pos_decimal(2*k-1,i) = motor_pos_decimal_original(2*k-1,i);
            motor_pos_decimal(2*k,i) = motor_pos_decimal_original(2*k,i);
        elseif control_mode == 2
            motor_pos_decimal(2*k-1,i) = motor_pos_decimal_original(2*k-1,i);
            motor_pos_decimal(2*k,i) = motor_pos_decimal_original(2*k,i);
            if i >= 2
                if angle(k,i) >= -gamma% LEFT
                    motor_pos_decimal(2*k,i) = -18171*cos(-(-gamma)/180*pi/2 + 0.5903) + POS_OFFSET(2*k) - 150*abs(angle(k,i)-(-gamma));
                end
                if angle(k,i) <= gamma% RIGHT
                    motor_pos_decimal(2*k-1,i) = -18171*cos((gamma)/180*pi/2 + 0.5903) + POS_OFFSET(2*k-1) - 150*abs(angle(k,i)-(gamma));
                end
%                 if k > 6
%                     motor_pos_decimal(2*k-1,i) = -18171*cos(0/180*pi/2 + 0.5903) + POS_OFFSET(2*k-1) - 4000;
%                     motor_pos_decimal(2*k,i) = -18171*cos(0/180*pi/2 + 0.5903) + POS_OFFSET(2*k) - 4000;
%                 end
            end
        elseif control_mode == 3
            motor_pos_decimal(2*k-1,i) = motor_pos_decimal_original(2*k-1,i);
            motor_pos_decimal(2*k,i) = motor_pos_decimal_original(2*k,i);
            if i >= 2
                if angle(k,i) - angle(k,i-1) >= 0
                    motor_pos_decimal(2*k,i) = motor_pos_decimal_original(2*k,i) - 4000/A*(A-abs(angle(k,i)));
                else
                    motor_pos_decimal(2*k-1,i) = motor_pos_decimal_original(2*k-1,i) - 4000/A*(A-abs(angle(k,i)));
                end
            end
        elseif control_mode == 4.4
            motor_pos_decimal(2*k-1,i) = motor_pos_decimal_original(2*k-1,i);
            motor_pos_decimal(2*k,i) = motor_pos_decimal_original(2*k,i);
            if i >= 2
                if k > 4
                    motor_pos_decimal(2*k-1,i) = -18171*cos(0/180*pi/2 + 0.5903) + POS_OFFSET(2*k-1) - 4000;
                    motor_pos_decimal(2*k,i) = -18171*cos(0/180*pi/2 + 0.5903) + POS_OFFSET(2*k) - 4000;
                end
            end
        else
            error('!!!Control mode does not exist!!!');
            run('clean_up.m');
        end
        
        t = t+dt;
    end
    t = 0;
end

% % ============= ONLY FOR CALIBRATION =============
% POS_0_DEG = POS_0_DEG - 6000;
% motor_pos_decimal = motor_pos_decimal - 6000;
% POS_MAX = POS_MAX - 6000;
% POS_MIN = POS_MIN - 6000;
% % ================================================

for k = 1:2*N
    for i = 1:size(motor_pos_decimal, 2)
        if motor_pos_decimal(k,i) > POS_MAX(k)
            motor_pos_decimal(k,i) = POS_MAX(k);
        elseif motor_pos_decimal(k,i) < POS_MIN(k)
            motor_pos_decimal(k,i) = POS_MIN(k);
        end
    end
end


%% Initialize motors
run('initialize_motors.m')

%% Zero position check
set_motors_zero;
disp("All motors at position 0, please check tendons...");
% pause;
% pause(5);

%% Loop the gait
command_freq = 0.05;
% MOTORS_NEED_EXTRA = zeros(1, NUM_BODY_SERVOS);
overload_counter = ones(1, NUM_BODY_SERVOS) * -1;
overload_counter_record = overload_counter;

disp("Press any key to initialize shape...");
pause;
index = 1;
set_motors_v2;
disp("Press any key to initialize gait...");
pause;
index = 2;
set_motors_v2;
disp("Press any key to start gait...");
pause;
pause(1);
start_gait = tic;

figure(100);
ButtonHandle = uicontrol('Style', 'PushButton', ...
    'String', 'Stop running', ...
    'Callback', 'delete(gcbf)');   % exit button

for index = 2:all_steps
    start_iter = tic;
    get_motor_feedback_v3;
    
    % ======= examine motor current load ============
    if LargeTorqueReactionQ
        large_load_idx = find(present_load > 700);
        overload_counter = overload_counter - 1;
        if ~isempty(large_load_idx)
            disp('triggered')
            for i = 1:length(large_load_idx)
                overload_counter(large_load_idx(i)) = 30;
            end
        end
        disp(overload_counter);
        overload_counter_record = [overload_counter_record; overload_counter];
    end
    
    if LargeTorqueStopQ
        disp(max(present_load))
        large_load_idx = find(present_load > 950);
        if ~isempty(large_load_idx)
            motor_pos_decimal(:, index) = motor_pos_decimal(:, index) - 1000;
            set_motors_v2;
            disp('!!!Overload protection triggered!!!');
            close(100);
            break;
        end
    end
    % ===============================================
    set_motors_v2;
    time = toc(start_iter);
    pause(max(command_freq-time, 0));
    
    if ~ishandle(ButtonHandle)
        disp('Stopped');
        break;
    end
end
get_motor_feedback_v3;
fbk.dxl_present_position = dxl_present_position;
fbk.dxl_present_load = dxl_present_load;
fbk.dxl_present_time = dxl_present_time;
fbk.overload_counter = overload_counter_record;
if HeadSensorQ
    fbk.dxl_present_head_contact = dxl_present_head_contact;
end
%save_data;



%% Exit
disp("Gait done, press any key to reset motors to zeros...");
pause;
pause(5);
set_motors_zero;
index = index + 1;

pause(3);

run('clean_up.m')
% close all;
% clear;
