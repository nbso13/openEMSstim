import numpy as np
import math
import time
import xlsxwriter
import random
import matplotlib.pyplot as plt
import datetime
import serial
import time




def play_rhythm(bluetooth, actual_stim_length, rhythm_substr, repeats, bpm, intensity_level):
    
    max_bpm = math.floor(30000/actual_stim_length) #how many eighthnote pulses could you fit into a minute without overlapping?

    if (bpm > max_bpm):
        print("max metronome bpm is " + str(max_bpm))
        return

    #determine pulse+wait length
    milliseconds_per_eighthnote = 30000/bpm
    milliseconds_wait = milliseconds_per_eighthnote - actual_stim_length

    for i in range(repeats): # present the rhythm with appropriate number of repeats
        for j in range(len(rhythm_substr)):  # go through each eighthnote in the pattern
            if (rhythm_substr[j] == '1'): # this is a note
                command_bytes = "xC1I" + str(intensity_level) + "T" + str(actual_stim_length) + "G"
                byt_com = bytes(command_bytes, encoding='utf8')
                bluetooth.write(byt_com)
                print("stim on")
                time.sleep(actual_stim_length/1000)
                time.sleep(milliseconds_wait/1000)
            elif(rhythm_substr[j] == '0'): # rest
                time.sleep(milliseconds_per_eighthnote/1000)
            else:
                print("malformed rhythm pattern: " + rhythm_substr)
                break


#### read and write to arduino ###

# port = '/dev/ttys000'
port = '/dev/tty.usbserial-18DNB483'
bluetooth = serial.Serial(port, 115200)
bluetooth.flushInput()
bluetooth.write(b"2")

input("adjust ems channel intensity to 10!")



### Gathering subject info ###

subject_name = input("subject name?")
now = datetime.datetime.now()
test_time = now.strftime("%Y_%m_%d_%H_%M_%S")
subject_arm = input("subject arm?")
electrode_config = input("electrode config?") #first pair of numbers is coordinates of 1, x and y, second is coordinates of 2. x and y
max_ems_stim_intensity = input("max ems stim intensity?")
pulse_width = input("pulse width?")
pulse_frequency = input("frequency?") #these may be found on the stimulator and are not usually iterated on (using lit values)

rhythm_substr = "10101010"
repeats = 1
bpm = 100

lengths = range(150, 290, 20) #length in ms of stimulation pulse
intensities = range(20, 100, 10) 

label_header = ["subject name", "test time", "subject arm", "electrode config", "rhythm pattern", "bpm", "max_stim_intensity", "pulse width (microsecs)", "frequency (Hz)"]
header_values = [subject_name, test_time, subject_arm, electrode_config, rhythm_substr, bpm, max_ems_stim_intensity, pulse_width, pulse_frequency]
data_header = ["y ax = intensities (%, " + max_ems_stim_intensity + " is max on toolkit stim), x ax = stim lengths (microsecs)"] + [*lengths]

 
### open workbook, define worksheets ###

workbook = xlsxwriter.Workbook(test_time + '_' + subject_name + '.xlsx')
bold = workbook.add_format({'bold': True})
pain_worksheet = workbook.add_worksheet("Pain level") # judged subjectively, 1-10, 1 is barely perceivable sensation, 10 is intense pain, 0 is no sensation.
act_worksheet = workbook.add_worksheet("Actuation level") # judged subjectively, 1-10, 1 is barely visible movement, 10 is complete flexion. 0 is no visible actuation.
speed_worksheet = workbook.add_worksheet("Actuation speed") # judged subjectively, 1-10, 1 is very slow, 10 is very fast. 0 is no actuation.
worksheets = [pain_worksheet, act_worksheet, speed_worksheet]

## write header values ##

for worksheet in worksheets:
    for i in range(len(label_header)):
        worksheet.write(0, i, label_header[i], bold) # write in header values
        worksheet.write(1, i, header_values[i], bold)

    for i in range(len(data_header)):
        worksheet.write(2, i, data_header[i])
    for i in range(len(intensities)):
        worksheet.write(i+3, 0, intensities[i])

# workbook.close()
worksheet_data_begin_indices = [3, 1] # where empty data space begins in each worksheet

## scramble length and intensity test order ##

x = list(enumerate(lengths))
random.shuffle(x)
shuffled_length_indices, shuffled_lengths = zip(*x)

y = list(enumerate(intensities))
random.shuffle(y)
shuffled_intensity_indices, shuffled_intensities = zip(*y)

arr = np.empty((len(intensities), len(lengths)))
arr[:] = np.NaN
data_arr = [arr, arr, arr]

### calibrate user to strongest impulses ###
input("For your reference: this is strongest and longest stim: (enter to play it)")
play_rhythm(bluetooth, lengths[-1], rhythm_substr, repeats, bpm, intensities[-1])

input("By contrast, this is weakest and shortest stim: (enter to play it)")
play_rhythm(bluetooth, lengths[0], rhythm_substr, repeats, bpm, intensities[0])
input("If the first stim was unbearably painful and you cannot stand more stims of the sort, please press 'control C' on Mac to end program and reset max intensity and length as needed. Otherwise, 'enter' to continue.")

### run testing loop ###

input("Stimulations will now be presented, four at a time, sampling stim_length and intensity space. (enter to continue)") 
input("You are to rate: (1) the pain of the stimulation (0 is no sensation, 10 is as painful as the example stimulation), (enter to continue)")
input("(2) the extent to which your finger moved, i.e., 'actuation' (0 is no movement, 10 is the extent to which it moved on the example), (enter to continue)")
input("(3) the speed of actuation (0 is no movement, 1 is very slow, 10 is almost instantaneous activation) (enter to begin trials)")

for i in range(len(shuffled_lengths)):
    actual_stim_length = shuffled_lengths[i] #ms
    data_index_x =shuffled_length_indices[i]
    for j in range(len(shuffled_intensities)):
        actual_intensity = shuffled_intensities[j]
        data_index_y = shuffled_intensity_indices[j]

        print(" Length: "+ str(actual_stim_length) + ", intensity: " + str(actual_intensity))
        play_rhythm(bluetooth, actual_stim_length, rhythm_substr, repeats, bpm, actual_intensity)
        pain_val = input("pain? 0-10")
        actuation_val = input("actuation? 0-10")
        speed_val = input("speed? 0-10")
        values_to_write = [pain_val, actuation_val, speed_val]

        for k in range(len(worksheets)):
            try_again = False
            worksheets[k].write(worksheet_data_begin_indices[0] + data_index_y, worksheet_data_begin_indices[1] + data_index_x, values_to_write[k])
            try:
                data_arr[k][data_index_y, data_index_x] = values_to_write[k]
            except ValueError:
                try_again = True
                break


        if(try_again == True or max(values_to_write) > 10 or min(values_to_write) < 0):
            print("Please be sure to enter a value between 0 and 10 for each inquiry.")
            pain_val = input("pain? 0-10")
            actuation_val = input("actuation? 0-10")
            speed_val = input("speed? 0-10")
            values_to_write = [pain_val, actuation_val, speed_val]
            for k in range(len(worksheets)):
                worksheets[k].write(worksheet_data_begin_indices[0] + data_index_y, worksheet_data_begin_indices[1] + data_index_x, values_to_write[k])
                data_arr[k][data_index_y, data_index_x] = values_to_write[k]

### visualize as heat map at the end ###

fig, axs = plt.subplots(2, 2)
axs[0, 0].imshow(data_arr[1], cmap='hot', interpolation='nearest')
axs[0, 0].set_title('Pain map')
axs[0, 0].set_xticklabels(lengths) 
axs[0, 0].set_yticklabels(intensities) 
axs[0, 1].imshow(data_arr[2], cmap='hot', interpolation='nearest')
axs[0, 1].set_title('Actuation map')
axs[0, 1].set_xticklabels(lengths) 
axs[0, 1].set_yticklabels(intensities)
axs[1, 0].imshow(data_arr[3], cmap='hot', interpolation='nearest')
axs[1, 0].set_title('Speed map')
axs[1, 0].set_xticklabels(lengths) 
axs[1, 0].set_yticklabels(intensities)

for ax in axs.flat:
    ax.set(xlabel='Stim length (ms)', ylabel='Stim intensity (%)')

plt.show()

bluetooth.close()
print("done")

workbook.close()