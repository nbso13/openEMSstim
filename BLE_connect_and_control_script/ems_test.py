from subprocess import Popen, PIPE
import subprocess
import shlex
import numpy as np
import math
import pygame
import time

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




def play_rhythm(bluetooth, actual_stim_length, rhythm_substr, repeats, bpm, ems_flag, audio_flag, metronome_intro_flag, audio_pre_display_flag, delay_val):
    
    max_bpm = math.floor(30000/actual_stim_length) #how many eighthnote pulses could you fit into a minute without overlapping?
    audio_repeats = 2

    if (bpm > max_bpm):
        print("max metronome bpm is " + str(max_bpm))
        return
    if delay_val > actual_stim_length:
        print("delay_value more than stim length")

    #determine pulse+wait length
    milliseconds_per_eighthnote = 30000/bpm
    milliseconds_wait = milliseconds_per_eighthnote - actual_stim_length

    ### metronome count in ###
    if metronome_intro_flag:
        count_in_substr = '10101010'
        for i in range(len(count_in_substr)):
            if (count_in_substr[i] == '1'): # this is a note
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
                    command_bytes = "xC1I100T" +str(actual_stim_length) + "G"
                    byt_com = bytes(command_bytes, encoding='utf8')
                    bluetooth.write(byt_com)
                    print("stim on")
                time.sleep(delay_val/1000)
                if audio_flag:
                    pygame.mixer.music.play()
                time.sleep((actual_stim_length-delay_val)/1000)
                time.sleep(milliseconds_wait/1000)
            elif(rhythm_substr[j] == '0'): # rest
                pygame.mixer.music.stop()
                time.sleep(milliseconds_per_eighthnote/1000)
            else:
                print("malformed rhythm pattern: " + rhythm_substr)
                break




# command_str = "C0I100T750G"

pygame.mixer.init()
pygame.mixer.music.load("440Hz_44100Hz_16bit_05sec.mp3")



#### read and write to arduino ###
import serial
import time
# port = '/dev/ttys000'
port = '/dev/tty.usbserial-18DNB483'
bluetooth = serial.Serial(port, 115200)
bluetooth.flushInput()
bluetooth.write(b"2")

# input("adjust ems channel 1 intensity to 3")

######## calibrate EMS timing #######

# set up participant in tapping position

# send 10 tap commands and record relative times of initial contact

# compute mean and variance of delays (ideally low variance (and low mean))

# save mean delay value as 
MEASURED_DELAY = 100 #ms

##### TRAINING PROCEDURE WITH EMS #######

# audio metronome playing

# introduce rhythm in context of metronome


# rhythm audio

# rhythm audio with EMS
#### test serial delay ####
while(bluetooth.in_waiting):
    print(bluetooth.readline().decode("utf-8"))



rhythm_substr = "010010011010100"
repeats = 4
bpm = 100
ems_flag = 1
audio_flag = 1
audio_pre_display_flag = 1
metronome_intro_flag = 1
delay_val = MEASURED_DELAY
# lengths = range(220, 260, 20)
# intensities = range(1, 10)

actual_stim_length = 250


# for length in lengths:
#     actual_stim_length = length #ms
#     for intensity in intensities:
#         print(" Length: "+ str(length) + ", intensity: " + str(intensity))
#         out = input("Recorded prev values? Changed intensity?")
#         if out == "stop":
#             break
#         else:
play_rhythm(bluetooth, actual_stim_length, rhythm_substr, repeats, bpm, ems_flag, audio_flag, metronome_intro_flag, audio_pre_display_flag, delay_val)
        


bluetooth.close()
print("done")
# subprocess.call(["blueutil", "-p", "0"])
# subprocess.call(["blueutil", "-p", "1"])

# #reset bluetooth
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
#     bluetooth.write(b"e")
#     time.sleep(1)
#     bluetooth.write(b"r")
#     time.sleep(1)
    # input_data = bluetooth.read(8)
    # print(input_data.decode())






# address = "00-1E-C0-42-85-FF"
# perif_id = '2001D755-B5B0-4253-A363-3132B0F93E71'
# service = '454D532D-5365-7276-6963-652D424C4531' #read write?

### test play rhythm