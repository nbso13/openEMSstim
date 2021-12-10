
import numpy as np
import time
import serial

# FOR ROBUST POINTER AND MIDDLE ACUTATION - SEE PICTURE IN FOLDER. Use max strength stim for 175 ms. But be careful when adding in ring and pinky

# port = '/dev/ttys000'
port = '/dev/tty.usbserial-18DNB483'
bluetooth = serial.Serial(port, 115200)
bluetooth.flushInput()
bluetooth.write(b"2")
bluetooth.write(b"1")

def execute(bluetooth, command_str, execution_lengths, execution_strengths):
    if command_str == "r":
        ex_stren = execution_strengths[0]-30 #because combines with other stim
        command_bytes_0 = "C0I" + str(ex_stren) + "T" + str(execution_lengths[0]) + "G \n"
        byt_com_0 = bytes(command_bytes_0, encoding='utf8')
        command_bytes_1 = "C1I" + str(execution_strengths[1]) + "T" + str(execution_lengths[1]) + "G \n"
        byt_com_1 = bytes(command_bytes_1, encoding='utf8')
        bluetooth.write(byt_com_1)
        time.sleep(0.005)
        bluetooth.write(byt_com_0)
        
    elif command_str == "s":
        command_bytes_0 = "C0I" + str(execution_strengths[0]) + "T" + str(execution_lengths[0]) + "G \n"
        byt_com_0 = bytes(command_bytes_0, encoding='utf8')
        bluetooth.write(byt_com_0)
    elif command_str == "p":
        time.sleep(1)
    else:
        print("error, command str not recognized.")

def listen(bluetooth):
    for k in range(300):
        if(bluetooth.in_waiting):
            out = bluetooth.readline().decode('utf-8')
            print(out)  
        time.sleep(0.001) 

# scissors electrodes placed with centers one pad length medial of center and one
# pad length up toward hand from base of forearm. at 100% intsensity, ems generator set at 24 intensity and signal time is 205 ms
listen(bluetooth)

input("adjust ems channel intensity to 26!")

leng = [165, 170] # stim len ms
stren = [96, 96]
while True:
    out = input("comm?")
    execute(bluetooth, out, leng, stren)
    listen(bluetooth)
beat = 0.6
delay = 0.1
command_arr = ["r", "p", "s"]
num_trials = 10
for i in range(num_trials):
    choice = np.random.randint(0,3)
    comm = command_arr[choice]
    time.sleep(beat)
    print("schnick")
    time.sleep(beat)
    print("schnack")
    time.sleep(beat)
    print("schnuck")
    time.sleep(beat-delay)
    execute(bluetooth, comm, leng, stren)
    
    listen(bluetooth)
    print(comm)
    input("cont?")
