import numpy as np
import math
import pygame
import time
import threading
import matplotlib.pyplot as plt

def metronome(bpm, length_of_stim):  #in beats per minute and lengthofstim is seconds
    #max bpm is __ as given actual stim length of ___ms as you can only fit around 6 stims in a 
    # second.
    actual_stim_length = 300 #ms
    max_bpm = 60*math.floor(1000/actual_stim_length)

    if (bpm > max_bpm):
        print("max metronome bpm is " + str(max_bpm))
        return

    # determine wait time between pulses
    milliseconds_per_beat = 60000/bpm
    milliseconds_wait = milliseconds_per_beat - actual_stim_length

    total_repeats = math.floor(length_of_stim*1000/milliseconds_wait) # det

    for i in range(total_repeats):
        # start stim command
        print("stim started")
        # wait for actual_stim_length
        # turn off stim        
        print("stim stopped")
        #wait for milliseconds_wait

def play_rhythm(ems_serial, contact_ser, actual_stim_length, count_in_substr, rhythm_substr, \
    repeats, bpm, ems_flag, audio_flag, metronome_intro_flag, audio_pre_display_flag, audio_repeats, samp_period_ms, delay_val):
    reading_results = [] # a list that is written to by the thread that is the contact
    x_value_results = []
    max_bpm = math.floor(30000/actual_stim_length) #how many eighthnote pulses could you fit into a minute without overlapping?

    if (bpm > max_bpm):
        print("max metronome bpm is " + str(max_bpm))
        return
    if delay_val > actual_stim_length:
        print("delay_value more than stim length")

    #determine pulse+wait length
    milliseconds_per_eighthnote = 30000/bpm
    milliseconds_wait = milliseconds_per_eighthnote - actual_stim_length

    ## start reading thread ##
    len_pres = milliseconds_per_eighthnote*(len(count_in_substr) + (audio_repeats+repeats) * len(rhythm_substr)) + delay_val
    read_thread = threading.Thread(target=read_contact_trace, args= (contact_ser, len_pres, samp_period_ms, reading_results, x_value_results))
    read_thread.start()

    ### metronome count in ### # with EMS activation. This gives the rhythm measurement system a way to determine how off the tapping is.
    if metronome_intro_flag:
        for i in range(len(count_in_substr)):
            if (count_in_substr[i] == '1'): # this is a note
                if ems_flag:
                    command_bytes = "xC1I100T" +str(actual_stim_length) + "G \n" # metronome intro
                    byt_com = bytes(command_bytes, encoding='utf8')
                    ems_serial.write(byt_com)
                if audio_flag:
                    time.sleep(delay_val/1000)
                    pygame.mixer.music.play()
                    time.sleep((actual_stim_length-delay_val)/1000)
                time.sleep(milliseconds_wait/1000)
            elif(count_in_substr[i] == '0'): # rest
                if audio_flag:
                    pygame.mixer.music.stop()
                    time.sleep(milliseconds_per_eighthnote/1000)

    ### rhythm audio display ###
    if audio_pre_display_flag:
        for i in range(audio_repeats): # present the rhythm with appropriate number of repeats
            for j in range(len(rhythm_substr)):  # go through each eighthnote in the pattern
                if (rhythm_substr[j] == '1'): # this is a note
                    time.sleep(delay_val/1000)
                    pygame.mixer.music.play()
                    time.sleep((actual_stim_length-delay_val)/1000)
                    time.sleep(milliseconds_wait/1000)
                elif(rhythm_substr[j] == '0'): # rest
                    pygame.mixer.music.stop()
                    time.sleep(milliseconds_per_eighthnote/1000)
                else:
                    print("malformed rhythm pattern: " + rhythm_substr)
                    break

    

    for i in range(repeats): # present the rhythm with appropriate number of repeats
        for j in range(len(rhythm_substr)):  # go through each eighthnote in the pattern
            if (rhythm_substr[j] == '1'): # this is a note
                if ems_flag:
                    command_bytes = "xC1I100T" +str(actual_stim_length) + "G \n"
                    byt_com = bytes(command_bytes, encoding='utf8')
                    ems_serial.write(byt_com)
                    print("stim on")
                time.sleep(delay_val/1000)
                if audio_flag:
                    pygame.mixer.music.play()
                time.sleep((actual_stim_length-delay_val)/1000)
                time.sleep(milliseconds_wait/1000)
                pygame.mixer.music.stop()
            elif(rhythm_substr[j] == '0'): # rest
                pygame.mixer.music.stop()
                time.sleep(milliseconds_per_eighthnote/1000)
            else:
                print("malformed rhythm pattern: " + rhythm_substr)
                break

    read_thread.join()

    return reading_results, x_value_results

def read_contact_trace(ser,  len_rhythm_presentation_ms, samp_period_ms, readings_list, x_values_list):
    time_start= time.time()
    check_repeats = int(np.floor((len_rhythm_presentation_ms/samp_period_ms)))
    measured_periods = []
    print("thread begun")
    for i in range(check_repeats):
        out = ser.readline().decode('utf-8')
        # if int(out)>0:
        #     print(out)
        readings_list.append(int(out[:-2]))
        time_measured = time.time()
        time.sleep(samp_period_ms/1000)
        x_values_list.append(1000*(time_measured-time_start)) #from seconds to milliseconds
    print("done reading trace")
    # print("mean samp period and stdv: " + str(mean_contact_samp_period) + " +/- " + str(stdv_contact_samp_period))
    return readings_list, x_values_list

def rhythm_string_to_stim_trace_and_audio_trace(count_in_substr, rhythm_substr,  actual_stim_length, bpm, repeats, samp_period, delay):
    # takes in the count-in string, the actual rhythm string, the length of stimulation in ms, beats per minute,
    # stim repeats number, requested sample period of resulting trace (in ms). Returns stim_trace numpy array
    # with 0 values for time points of no stim and 1000 values for stim. This is offset /delay/ amount in ms
    # from audio stimulus (also returned in same size array). Final value returned is a time array, steps in 
    # samp_period.
    milliseconds_per_eighthnote = 30000/bpm
    array_len_per_eighthnote = int(np.floor(milliseconds_per_eighthnote/samp_period))
    delay_array_len = int(np.floor(delay/samp_period))
    actual_stim_len_array_indices = int(np.floor(actual_stim_length/samp_period))
    eighthnotes_pres = len(count_in_substr) + (audio_repeats+repeats) * len(rhythm_substr)
    trace_array_len = array_len_per_eighthnote * eighthnotes_pres + delay_array_len
    stim_trace = np.zeros((trace_array_len,))
    audio_trace = np.zeros((trace_array_len,))
    x_array = np.arange(0, trace_array_len) * samp_period

    for i in range(len(count_in_substr)): # write in count-in traces.
        if count_in_substr[i] == '1':
            stim_begin_ind = i * array_len_per_eighthnote
            stim_end_ind = stim_begin_ind + actual_stim_len_array_indices
            stim_trace[stim_begin_ind:stim_end_ind] = 1
            audio_begin_ind = stim_begin_ind+delay_array_len
            audio_end_ind = audio_begin_ind + array_len_per_eighthnote
            audio_trace[audio_begin_ind:audio_end_ind] = 1

    start_index_audio = len(count_in_substr) * array_len_per_eighthnote + delay_array_len

    if audio_repeats > 0:
        for i in range(audio_repeats): # write the audio trace for any audio pre-stim presentation
            for j in range(len(rhythm_substr)):
                if rhythm_substr[j] == '1':
                    audio_begin_ind = start_index_audio + (j * array_len_per_eighthnote)
                    audio_end_ind = audio_begin_ind + array_len_per_eighthnote
                    audio_trace[audio_begin_ind:audio_end_ind] = 1
            start_index_audio = start_index_audio + (array_len_per_eighthnote * len(rhythm_substr))
    
    start_index_stim = array_len_per_eighthnote * (len(count_in_substr) + (audio_repeats * len(rhythm_substr)))

    for i in range(repeats): # now writing for actual rhythm display and actuation
        for j in range(len(rhythm_substr)):
            if rhythm_substr[j] == '1':
                stim_begin_ind = start_index_stim + (j * array_len_per_eighthnote)
                stim_end_ind = stim_begin_ind + actual_stim_len_array_indices
                stim_trace[stim_begin_ind:stim_end_ind] = 1
                audio_begin_ind = stim_begin_ind+delay_array_len
                audio_end_ind = audio_begin_ind + array_len_per_eighthnote
                audio_trace[audio_begin_ind:audio_end_ind] = 1
                audio_trace[audio_end_ind] = 0
        start_index_stim = start_index_stim + (array_len_per_eighthnote * len(rhythm_substr))
    
    return stim_trace, audio_trace, x_array

def plot_contact_trace_and_rhythm(reading_list, contact_x_values, stim_trace, audio_trace, x_array, samp_period):
    fig, ax = plt.subplots()
    ax.plot(contact_x_values, reading_list)
    ax.set_yticks(np.arange(0, 500, 100))
    ax.set_xticks(np.arange(0, (len(reading_list) * samp_period), 10000))
    ax.plot(x_array, stim_trace*np.max(reading_list))
    ax.plot(x_array, audio_trace*np.max(reading_list))
    ax.legend(["contact trace", "stim trace", "audio trace"])
    plt.show()


# example: command_str = "C0I100T750G \n"

### load sound ##
pygame.mixer.init()
pygame.mixer.music.load("440Hz_44100Hz_16bit_05sec.mp3")

#### read and write to arduino ###
import serial
import time
# port = '/dev/ttys000' for bluetooth
port = '/dev/tty.usbserial-18DNB483'
ems_serial = serial.Serial(port, 115200)
ems_serial.flushInput()
ems_serial.write(b"2")


port = '/dev/cu.usbmodem143401'
contact_serial = serial.Serial(port, 9600)


# input("adjust ems channel 1 intensity to 3")

######## calibrate EMS timing #######

# set up participant in tapping position

# send 10 tap commands and record relative times of initial contact

# compute mean and variance of delays (ideally low variance (and low mean))

# save mean delay value as 
MEASURED_DELAY = 50 #ms TUNE THIS VALUE A LA KASAHARA - MEASURE CHANGE IN AGENCY AND PERFORMANCE

##### TRAINING PROCEDURE WITH EMS #######

# audio metronome playing

# introduce rhythm in context of metronome


# rhythm audio

def listen(ems_serial):
    for k in range(300):
        if(ems_serial.in_waiting):
            out = ems_serial.readline().decode('utf-8')
            print(out)  
        time.sleep(0.001) 

listen(ems_serial)



rhythm_substr = "010010011010100"
count_in_substr = '10001000100010001000100010001000'
repeats = 1
bpm = 100
ems_flag = 1
audio_flag = 1
audio_pre_display_flag = 0
metronome_intro_flag = 1
delay_val = MEASURED_DELAY # TUNE THIS TO KASAHARA RESPONSE TIME, GET RESULTS REGARDING AGENCY AND MEASURE TRAINING RESULT
samp_period_ms = 2 # milliseconds

actual_stim_length = 160
audio_repeats = 0

# generate rhythm and audio traces
stim_trace, audio_trace, x_array = rhythm_string_to_stim_trace_and_audio_trace(count_in_substr, rhythm_substr,  actual_stim_length, bpm, repeats, samp_period_ms, MEASURED_DELAY)


# fig, ax = plt.subplots()
# ax.set_yticks(np.arange(0, 1000, 100))
# ax.set_xticks(np.arange(0, (len(stim_trace) * samp_period_ms), 10000))
# ax.plot(x_array, stim_trace)
# ax.plot(x_array, audio_trace)
# ax.legend([ "stim trace", "audio trace"])
# plt.show()

## TESTING GRAPHING AND CONTACT TRACING 
# milliseconds_per_eighthnote = 30000/bpm
# len_pres = milliseconds_per_eighthnote*(len(count_in_substr) + (audio_repeats+repeats) * len(rhythm_substr)) + delay_val
# reading_list = []
# reading_list = read_contact_trace(contact_serial, len_pres, samp_period_ms, reading_list)
# reading_list = np.array(reading_list)
# plot_contact_trace_and_rhythm(reading_list, stim_trace, audio_trace, x_array, samp_period_ms)


# play rhythm and conduct test
reading_list, contact_x_values = play_rhythm(ems_serial, contact_serial, actual_stim_length, count_in_substr, rhythm_substr, repeats, bpm, ems_flag, audio_flag, metronome_intro_flag, audio_pre_display_flag, audio_repeats, samp_period_ms, delay_val)
reading_list = np.array(reading_list)
contact_x_values = np.array(contact_x_values)
plot_contact_trace_and_rhythm(reading_list, contact_x_values, stim_trace, audio_trace, x_array, samp_period_ms)


contact_serial.close()
ems_serial.close()
print("done")







# subprocess.call(["blueutil", "-p", "0"])
# subprocess.call(["blueutil", "-p", "1"])

# #reset ems_serial
# subprocess.call(["blueutil", "-p", "0"])
# subprocess.call(["blueutil", "-p", "1"])

# command_str = "ble-serial -d 2001D755-B5B0-4253-A363-3132B0F93E71 -w 454d532d-5374-6575-6572-756e672d4348 -r 454d532d-5374-6575-6572-756e672d4348"
# # command_str = "ls -l"
# # connect using ble-serial script
# #second number is write characteristic and third is read. Find these
#    # by calling ble-scan -d DEVICE_ID and look for notify service/characteristic.

# print(command_str)
# process = Popen(shlex.split(command_str)) #stdout=PIPE, stderr=None, shell=True
# text = process.communicate()[0]
# print(text)

# time.sleep(3) #wait for connection to work



# for i in range(5):
#     # print("ping")
#     ems_serial.write(b"e")
#     time.sleep(1)
#     ems_serial.write(b"r")
#     time.sleep(1)
    # input_data = ems_serial.read(8)
    # print(input_data.decode())






# address = "00-1E-C0-42-85-FF"
# perif_id = '2001D755-B5B0-4253-A363-3132B0F93E71'
# service = '454D532D-5365-7276-6963-652D424C4531' #read write?

### test play rhythm