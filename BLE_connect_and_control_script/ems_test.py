import numpy as np
import math
import time
import threading
import matplotlib.pyplot as plt
import vlc

# current best settings: 155 ms. 10 intensity. bpm 110. never double up strokes direct. You can triple stroke indirect tho.

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
    repeats, bpm, ems_flag, audio_flag, metronome_intro_flag, audio_pre_display_flag, audio_repeats,  \
        samp_period_ms, delay_val):
        # mammoth function that should be broken up. takes in serial objects, rhythm parameters,
        # whether the EMS and the audio should be turned on, whether there should be a metronome intro,
        # sample period, and measured delay value. Plays the rhythm in audio and EMS and runs threading
        # to listen to user results.
    reading_results = [] # a list that is written to by the thread that is the contact
    x_value_results = []
    max_bpm = math.floor(30000/actual_stim_length) #how many eighthnote pulses could you fit into a 
    #minute without overlapping?

    if (bpm > max_bpm):
        print("max metronome bpm is " + str(max_bpm))
        return
    # if delay_val > actual_stim_length:
    #     print("delay_value more than stim length !")
    #     return

    #determine pulse+wait length
    milliseconds_per_eighthnote = 30000/bpm
    milliseconds_wait = milliseconds_per_eighthnote - actual_stim_length

    ## start reading thread ##
    len_pres = milliseconds_per_eighthnote*(len(count_in_substr) + (audio_repeats+repeats) *  \
        len(rhythm_substr)) + delay_val
    
    audio_onset_times = []
    stim_onset_times = []
    time_naught = time.time()
    read_thread = threading.Thread(target=read_contact_trace, args= (contact_ser, len_pres,  \
        samp_period_ms, reading_results, x_value_results, time_naught))
    read_thread.start()
    time_naught = time.time()

    predisplay_EMS_rhythm_str = '0'*len(rhythm_substr)

    ## metronome count in ### # with EMS activation. This gives the rhythm measurement system a way 
    # to determine how off the tapping is.
    rhythm_display_flag = 1
    ems_thread = threading.Thread(target=run_rhythm_ems, args= (rhythm_display_flag, ems_serial, time_naught,  \
        [], audio_repeats, predisplay_EMS_rhythm_str, actual_stim_length, milliseconds_wait, milliseconds_per_eighthnote, \
             metronome_intro_flag, count_in_substr, audio_pre_display_flag, audio_repeats)) # this plays nothing to kill time because you want to give the person a chance to learn the rhythm without ems.
    audio_thread= threading.Thread(target=run_rhythm_audio, args= (rhythm_display_flag, [],time_naught, audio_repeats, \
        rhythm_substr,  milliseconds_wait, milliseconds_per_eighthnote, metronome_intro_flag, count_in_substr, audio_pre_display_flag, audio_repeats))
        
    ems_thread.start()
    time.sleep(delay_val/1000)
    audio_thread.start()
    ems_thread.join()
    audio_thread.join()
    read_thread.join()
    audio_onset_times_ms = [1000 * item for item in audio_onset_times]
    stim_onset_times_ms = [1000 * item for item in stim_onset_times]

    return reading_results, x_value_results, audio_onset_times_ms, stim_onset_times_ms

    # if metronome_intro_flag:
    #     for i in range(len(count_in_substr)):
    #         if (count_in_substr[i] == '1'): # this is a note
    #             if ems_flag:
    #                 command_bytes = "xC1I100T" +str(actual_stim_length) + "G \n" # metronome intro
    #                 byt_com = bytes(command_bytes, encoding='utf8')
    #                 ems_serial.write(byt_com)
    #                 stim_onset_times.append(time.time()-time_naught)
    #             time.sleep(delay_val/1000)
    #             if audio_flag:
    #                 audio_onset_times.append(time.time()-time_naught)
    #                 fourfourty_tone.play()
    #             time.sleep((actual_stim_length-delay_val)/1000)
    #             time.sleep(milliseconds_wait/1000)
    #             fourfourty_tone.stop()
    #         elif(count_in_substr[i] == '0'): # rest
    #             if audio_flag:
    #                 fourfourty_tone.stop()
    #                 time.sleep(milliseconds_per_eighthnote/1000)

    ### rhythm audio display ###
    # if audio_pre_display_flag:
    #     for i in range(audio_repeats): # present the rhythm with appropriate number of repeats
    #         for j in range(len(rhythm_substr)):  # go through each eighthnote in the pattern
    #             if (rhythm_substr[j] == '1'): # this is a note
    #                 time.sleep(delay_val/1000)
    #                 audio_onset_times.append(time.time()-time_naught)
    #                 fourfourty_tone.play()
    #                 time.sleep((actual_stim_length-delay_val)/1000)
    #                 time.sleep(milliseconds_wait/1000)
    #                 fourfourty_tone.stop()
    #             elif(rhythm_substr[j] == '0'): # rest
    #                 fourfourty_tone.stop()
    #                 time.sleep(milliseconds_per_eighthnote/1000)
    #             else:
    #                 print("malformed rhythm pattern: " + rhythm_substr)
    #                 break

    # for i in range(repeats): # present the rhythm with appropriate number of repeats
    #     for j in range(len(rhythm_substr)):  # go through each eighthnote in the pattern
    #         if (rhythm_substr[j] == '1'): # this is a note
    #             if ems_flag:
    #                 command_bytes = "xC1I100T" +str(actual_stim_length) + "G \n"
    #                 byt_com = bytes(command_bytes, encoding='utf8')
    #                 stim_onset_times.append(time.time() - time_naught)
    #                 ems_serial.write(byt_com)
    #                 print("stim on")
    #             time.sleep(delay_val/1000)
    #             if audio_flag:
    #                 audio_onset_times.append(time.time() - time_naught)
    #                 fourfourty_tone.play()
    #             time.sleep(milliseconds_wait-delay_val)/1000)
    #             fourfourty_tone.stop()
    #         elif(rhythm_substr[j] == '0'): # rest
    #             fourfourty_tone.stop()
    #             time.sleep(milliseconds_per_eighthnote/1000)
    #         else:
    #             print("malformed rhythm pattern: " + rhythm_substr)
    #             break

def run_rhythm_ems(rhythm_display_flag, ems_serial, time_naught, stim_onset_times, repeats, rhythm_substr, actual_stim_length, \
     milliseconds_wait, milliseconds_per_eighthnote, metronome_intro_flag, count_in_substr, audio_pre_display_flag, pre_repeats):
    if metronome_intro_flag:
        for j in range(len(count_in_substr)):  # go through each eighthnote in the pattern
            if (count_in_substr[j] == '1'): # this is a note
                command_bytes = "xC1I100T" +str(actual_stim_length) + "G \n"
                byt_com = bytes(command_bytes, encoding='utf8')
                stim_onset_times.append(time.time() - time_naught)
                ems_serial.write(byt_com)
                print("stim on")
                time.sleep(milliseconds_wait/1000)
                fourfourty_tone.stop()
            elif(count_in_substr[j] == '0'): # rest
                time.sleep(milliseconds_per_eighthnote/1000)
            else:
                print("malformed rhythm pattern: " + rhythm_substr)
                break
    
    if audio_pre_display_flag:
        for i in range(pre_repeats): # present the rhythm with appropriate number of repeats
            for j in range(len(rhythm_substr)):  # go through each eighthnote in the pattern
                time.sleep(milliseconds_per_eighthnote/1000)

    if rhythm_display_flag:
        for i in range(repeats): # present the rhythm with appropriate number of repeats
            for j in range(len(rhythm_substr)):  # go through each eighthnote in the pattern
                if (rhythm_substr[j] == '1'): # this is a note
                    command_bytes = "xC1I100T" +str(actual_stim_length) + "G \n"
                    byt_com = bytes(command_bytes, encoding='utf8')
                    stim_onset_times.append(time.time() - time_naught)
                    ems_serial.write(byt_com)
                    print("stim on")
                    time.sleep(milliseconds_wait/1000)
                    fourfourty_tone.stop()
                elif(rhythm_substr[j] == '0'): # rest
                    time.sleep(milliseconds_per_eighthnote/1000)
                else:
                    print("malformed rhythm pattern: " + count_in_substr)
                    break

def run_rhythm_audio(rhythm_display_flag, audio_onset_times, time_naught, repeats, rhythm_substr,  milliseconds_wait, \
    milliseconds_per_eighthnote, metronome_intro_flag, count_in_substr, audio_predisplay_flag, pre_repeats):
    met_signal_counter = 0
    if metronome_intro_flag:
        for j in range(len(count_in_substr)):  # go through each eighthnote in the pattern
            # met_signal_counter = met_signal_counter + 1
            # if met_signal_counter == 8:
            #     eighteighty_tone.play()
            #     met_signal_counter = 0
            if (count_in_substr[j] == '1'): # this is a note
                audio_onset_times.append(time.time() - time_naught)
                fourfourty_tone.play()
                time.sleep(milliseconds_wait/1000)
                fourfourty_tone.stop()
            elif(count_in_substr[j] == '0'): # rest
                fourfourty_tone.stop()
                time.sleep(milliseconds_per_eighthnote/1000)
            else:
                print("malformed rhythm pattern: " + count_in_substr)
                break
            # eighteighty_tone.stop()

    if audio_predisplay_flag:
        for i in range(pre_repeats): # present the rhythm with appropriate number of repeats
            for j in range(len(rhythm_substr)):  # go through each eighthnote in the pattern
                met_signal_counter = met_signal_counter + 1
                # if met_signal_counter == 8:
                #     eighteighty_tone.play()
                #     met_signal_counter = 0
                if (rhythm_substr[j] == '1'): # this is a note
                    audio_onset_times.append(time.time() - time_naught)
                    fourfourty_tone.play()
                    time.sleep(milliseconds_wait/1000)
                    fourfourty_tone.stop()
                elif(rhythm_substr[j] == '0'): # rest
                    fourfourty_tone.stop()
                    time.sleep(milliseconds_per_eighthnote/1000)
                else:
                    print("malformed rhythm pattern: " + rhythm_substr)
                    break
                # eighteighty_tone.stop()

    if rhythm_display_flag:
        for i in range(repeats): # present the rhythm with appropriate number of repeats
            for j in range(len(rhythm_substr)):  # go through each eighthnote in the pattern
                for j in range(len(rhythm_substr)):  # go through each eighthnote in the pattern
                    met_signal_counter = met_signal_counter + 1
                    # if met_signal_counter == 8:
                    #     eighteighty_tone.play()
                    #     met_signal_counter = 0
                if (rhythm_substr[j] == '1'): # this is a note
                    audio_onset_times.append(time.time() - time_naught)
                    fourfourty_tone.play()
                    time.sleep(milliseconds_wait/1000)
                    fourfourty_tone.stop()
                elif(rhythm_substr[j] == '0'): # rest
                    fourfourty_tone.stop()
                    time.sleep(milliseconds_per_eighthnote/1000)
                else:
                    print("malformed rhythm pattern: " + rhythm_substr)
                    break
                # eighteighty_tone.stop()



def read_contact_trace(ser,  len_rhythm_presentation_ms, samp_period_ms, readings_list, x_values_list, time_naught_contact_trace):
    # reads from contact detection serial object every sample period. Saves results to a list
    # time.sleep(1)
    # print("thread time since start " + str(time.time()- time_naught))
    check_repeats = int(np.floor((len_rhythm_presentation_ms/samp_period_ms)))
    print("read thread begun")
    while (time.time()-time_naught_contact_trace)*1000 < len_rhythm_presentation_ms:
        if ser.in_waiting:
            out = ser.readline().decode('utf-8')
            time_measured = time.time()
            # if int(out[:-2]) > 5:
            #     print(int(out[:-2]))
            readings_list.append(int(out[:-2]))
            x_values_list.append(1000*(time_measured-time_naught_contact_trace)) #from seconds to milliseconds
    print("done reading trace")
    # print("mean samp period and stdv: " + str(mean_contact_samp_period) + " +/- " + str(stdv_contact_samp_period))
    return readings_list, x_values_list

def rhythm_string_to_stim_trace_and_audio_trace(count_in_substr, rhythm_substr,  actual_stim_length, bpm, repeats,  \
    samp_period, delay):
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

def plot_contact_trace_and_rhythm(reading_list, contact_x_values, stim_trace, audio_trace, x_array, samp_period, legend_labels):
    fig, ax = plt.subplots()
    ax.plot(contact_x_values, reading_list)
    ax.set_yticks(np.arange(0, 500, 100))
    ax.set_xticks(np.arange(0, (len(reading_list) * samp_period), 10000))
    ax.plot(x_array, stim_trace*np.max(reading_list))
    ax.plot(x_array, audio_trace*np.max(reading_list))
    ax.legend(legend_labels)
    plt.ion()
    plt.show()
    plt.draw()
    plt.pause(0.01)

def onset_times_to_traces(audio_onset_times, audio_hold_ms, stim_onset_times, stim_hold_ms, samp_period):
    array_value_audio_hold = int(np.floor(audio_hold_ms/samp_period))
    array_value_stim_time = int(np.floor(stim_hold_ms/samp_period))
    final_time_point = int(np.floor(np.max(audio_onset_times) + audio_hold_ms))
    x_vec = np.arange(0, final_time_point, samp_period)
    audio_trace = np.zeros_like(x_vec)
    stim_trace = np.zeros_like(x_vec)
    for time_val in audio_onset_times:
        array_ind_begin = int(np.floor(time_val/samp_period))
        array_ind_end = array_ind_begin + array_value_audio_hold
        audio_trace[array_ind_begin:array_ind_end] = 1
    for time_val in stim_onset_times:
        array_ind_begin = int(np.floor(time_val/samp_period))
        array_ind_end = array_ind_begin + array_value_stim_time
        stim_trace[array_ind_begin:array_ind_end] = 1
    return x_vec, audio_trace, stim_trace

def trace_to_spike_times(baseline_mean, baseline_sd, reading_results_list, x_values, sd_more_than_multiplier, baseline_subtractor):
    reading_results_array = np.array(reading_results_list)
    x_vals_array = np.array(x_values)
    bool_list = reading_results_array < baseline_subtractor
    reading_results_array[bool_list] = 0 # anything below this baseline is 0'd out
    bool_selector = reading_results_array > baseline_mean + baseline_sd*sd_more_than_multiplier
    time_points = x_vals_array[bool_selector]
    return time_points

def zero_sensor(contact_ser, sleep_len_ms, samp_period_ms):
    print("DON't TOUCH - zeroing")
    time.sleep(0.5)
    initial_outlist = []
    initial_x_results = []
    first_time_naught = time.time()
    read_contact_trace(contact_ser, sleep_len_ms, samp_period_ms, initial_outlist, initial_x_results, \
        first_time_naught)
    baseline_mean = np.mean(np.array(initial_outlist))
    baseline_sd = np.std(np.array(initial_outlist))
    print("Mean basline was "  + str(baseline_mean) + " +/- " + str(baseline_sd))
    print("DONE ZEROING")
    return baseline_mean, baseline_sd

def measure_delay(ems_serial, contact_ser, actual_stim_length, trial_num, sleep_len, samp_period_ms, sd_more_than_mult, baseline_subtractor):
    
    sleep_len_ms = sleep_len * 1000
    baseline_mean, baseline_sd = zero_sensor(contact_ser, 3*sleep_len_ms, samp_period_ms)

    times_stimmed = []
    reading_results = []
    x_value_results = []
    rand_values = np.divide(np.random.rand(trial_num), 2) #between 0 and 0.5 second random delay
    len_pres = 3000 + (trial_num * sleep_len + np.sum(rand_values)) * 1000 # ms
    time_naught_delay = time.time()
    print("time naught delay: " + str(time_naught_delay))
    read_thread = threading.Thread(target=read_contact_trace, args= (contact_ser, len_pres,  \
        samp_period_ms, reading_results, x_value_results, time_naught_delay))
    time_naught_main = time.time()
    print("time naught main thread: " + str(time_naught_main))
    read_thread.start()
    # time.sleep(1)
    # print("time since start: " + str(time.time() - time_naught_main))
    print("calibrating delay in 3")
    time.sleep(1)
    print("calibrating delay in 2")
    time.sleep(1)
    print("calibrating delay in 1")
    time.sleep(1)
    for i in range(trial_num):
        command_bytes = "xC1I100T" + str(actual_stim_length) + "G \n" # metronome intro
        byt_com = bytes(command_bytes, encoding='utf8')
        ems_serial.write(byt_com)
        times_stimmed.append(time.time()-time_naught_main)
        print("STIM " + str(i))
        time.sleep(sleep_len)
        time.sleep(rand_values[i])
    read_thread.join()

    times_responded_ms = trace_to_spike_times(baseline_mean, baseline_sd, reading_results, x_value_results,  sd_more_than_mult, baseline_subtractor)
    times_stimmed_ms = 1000*np.array(times_stimmed)
    first_responses_post_stim = []
    diffs = []
    for i in range(len(times_stimmed_ms)):
        # get earliest response threshold crossing
        temp = np.copy(times_responded_ms)
        before_bool = np.subtract(times_responded_ms, times_stimmed_ms[i]) < 0 # subtract stimmed time from response times to find
        # only responses after stim. then get bools above 0.
        temp[before_bool] = np.max(times_responded_ms) # set befores to maximum to avoid finding a close one before stim
        first_threshold_cross_post_stim = np.argmin(temp)
        first_responses_post_stim.append(times_responded_ms[first_threshold_cross_post_stim])
        diffs.append(times_responded_ms[first_threshold_cross_post_stim] - times_stimmed_ms[i])
    first_responses_post_stim = np.array(first_responses_post_stim)
    mean_delay = np.mean(diffs)
    std_delay = np.std(diffs)
    return mean_delay, std_delay, first_responses_post_stim, times_stimmed_ms, reading_results, x_value_results



def test_double_stroke(ems_serial, actual_stim_length, bpm):
    temp = 0
    reps = 1
    rhythm = "101001010010101001010010100"
    metronome = 0
    milliseconds_per_eighthnote = 30000/bpm
    milliseconds_wait = milliseconds_per_eighthnote - actual_stim_length
    rhythm_display_flag = 1
    audio_pre_display_flag = 0
    pre_repeats = 0
    run_rhythm_ems(rhythm_display_flag, ems_serial, temp, [], reps, rhythm, actual_stim_length, milliseconds_wait, \
        milliseconds_per_eighthnote, metronome, [], audio_pre_display_flag, pre_repeats)


# example: command_str = "C0I100T750G \n"

### load sound ##

global fourfourty_tone
fourfourty_tone = vlc.MediaPlayer("440Hz_44100Hz_16bit_05sec.mp3"); 
global eighteighty_tone 
eighteighty_tone = vlc.MediaPlayer("880hz.mp3")



#### read and write to arduino ###
import serial
import time
# port = '/dev/ttys000' for bluetooth
port = '/dev/tty.usbserial-18DNB483'
ems_serial = serial.Serial(port, 115200)
ems_serial.flushInput()
ems_serial.write(b"2")


port = '/dev/cu.usbmodem141301'
contact_serial = serial.Serial(port, 9600)


# input("adjust ems channel 1 intensity to 3")

######## calibrate EMS timing #######

# set up participant in tapping position

# send 10 tap commands and record relative times of initial contact

# compute mean and variance of delays (ideally low variance (and low mean))

# save mean delay value as 

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



rhythm_substr = "00100000100000101000100010000"
count_in_substr = '10001000100010001000100010001000'
repeats = 1
bpm = 115
ems_flag = 1
audio_flag = 1
audio_pre_display_flag = 1
metronome_intro_flag = 1
samp_period_ms = 2 # milliseconds
delay_trial_num = 10
sleep_len = 1 # seconds
sd_more_than_mult = 7
actual_stim_length = 155
audio_repeats = 2
baseline_subtractor = 10 # this is the noise threshold

### testing contact trace read

# while True:
#     out = contact_serial.readline().decode('utf-8')
#     if int(out)>0:
#         print(int(out[:-2]))

### testing parameters ###

out = input("test double stroke sensation?")
if out == 'y':
    contin = True
    while contin:
        test_double_stroke(ems_serial, actual_stim_length, bpm)
        out = input("adjust? a / continue? c")
        if out == 'c':
            contin = False

### MEASURE DELAY \delay_val = MEASURED_DELAY # TUNE THIS TO KASAHARA RESPONSE TIME, GET RESULTS REGARDING AGENCY AND MEASURE TRAINING RESULT

out = input("measure delay? 'y' to measure, enter number otherwise in milliseconds.")
if out == 'y':
    repeat_bool = True

    while(repeat_bool):
        
        delay_mean, delay_std, reaction_onsets, stim_onsets, \
        reading_results, contact_x_values = measure_delay(ems_serial, contact_serial, actual_stim_length, \
            delay_trial_num, sleep_len, samp_period_ms, sd_more_than_mult, baseline_subtractor)
        
        x_vec, reaction_trace, stim_trace = onset_times_to_traces(reaction_onsets, 2, stim_onsets, actual_stim_length, samp_period_ms)
        
        legend_labels = ["raw response trace", "stim trace",  "filtered response trace"]
        plot_contact_trace_and_rhythm(reading_results, contact_x_values, stim_trace, reaction_trace, x_vec,  \
        samp_period_ms, legend_labels)

        out = input("Measured delay was "  + str(delay_mean) + " +/- " + str(delay_std) +  \
            ". y to proceed, n to try again, control C to quit.")
        if out == 'y':
            repeat_bool = False
else:
    delay_mean = int(out)

MEASURED_DELAY = delay_mean

# generate rhythm and audio traces
stim_trace, audio_trace, x_array = rhythm_string_to_stim_trace_and_audio_trace(count_in_substr,  \
    rhythm_substr,  actual_stim_length, bpm, repeats, samp_period_ms, MEASURED_DELAY)

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
reading_list, contact_x_values, audio_onset_times, stim_onset_times = play_rhythm(ems_serial, \
    contact_serial, actual_stim_length, count_in_substr, rhythm_substr, repeats, bpm, ems_flag, \
    audio_flag, metronome_intro_flag, audio_pre_display_flag, audio_repeats, samp_period_ms, MEASURED_DELAY)
reading_list = np.array(reading_list)
contact_x_values = np.array(contact_x_values)
legend_labels = ["contact trace", "stim trace", "audio trace"]
plot_contact_trace_and_rhythm(reading_list, contact_x_values, stim_trace, audio_trace, x_array, samp_period_ms, legend_labels)

audio_hold_len_ms = 30000/bpm

x_vec, audio_trace_fromonset, stim_trace_fromonset = onset_times_to_traces(audio_onset_times, audio_hold_len_ms, \
    stim_onset_times, actual_stim_length, samp_period_ms)

legend_labels = ["contact trace", "stim trace", "audio trace"]
plot_contact_trace_and_rhythm(reading_list, contact_x_values, stim_trace_fromonset, audio_trace_fromonset, x_vec,  \
    samp_period_ms, legend_labels)

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