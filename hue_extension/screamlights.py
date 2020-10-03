#!/usr/bin/python

# open a microphone in pyAudio and listen for taps

import pyaudio
import struct
import math
import tplink_smartbulb_class as sb
import time

INITIAL_TAP_THRESHOLD = 0.010
FORMAT = pyaudio.paInt16 
SHORT_NORMALIZE = (1.0/32768.0)
CHANNELS = 1
RATE = 44100  
INPUT_BLOCK_TIME = 0.05
INPUT_FRAMES_PER_BLOCK = int(RATE*INPUT_BLOCK_TIME)
# if we get this many noisy blocks in a row, increase the threshold
OVERSENSITIVE = 15.0/INPUT_BLOCK_TIME                    
# if we get this many quiet blocks in a row, decrease the threshold
UNDERSENSITIVE = 120.0/INPUT_BLOCK_TIME 
# if the noise was longer than this many blocks, it's not a 'tap'
MAX_TAP_BLOCKS = 0.15/INPUT_BLOCK_TIME

def get_loudness(block):
    count = len(block)/2
    format = "%dh"%(count)
    shorts = struct.unpack( format, block )

    # iterate over the block.
    sum_squares = 0.0
    for sample in shorts:
        # sample is a signed short in +/- 32768. 
        # normalize it to 1.0
        n = sample * SHORT_NORMALIZE
        sum_squares += n*n

    return sum_squares

def get_rms( block ):
    # RMS amplitude is defined as the square root of the 
    # mean over time of the square of the amplitude.
    # so we need to convert this string of bytes into 
    # a string of 16-bit samples...

    # we will get one short out for each 
    # two chars in the string.
    count = len(block)/2
    format = "%dh"%(count)
    shorts = struct.unpack( format, block )

    # iterate over the block.
    sum_squares = 0.0
    for sample in shorts:
        # sample is a signed short in +/- 32768. 
        # normalize it to 1.0
        n = sample * SHORT_NORMALIZE
        sum_squares += n*n

    return math.sqrt( sum_squares / count )

class TapTester(object):
    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.stream = self.open_mic_stream()
        self.tap_threshold = INITIAL_TAP_THRESHOLD
        self.noisycount = MAX_TAP_BLOCKS+1 
        self.quietcount = 0 
        self.errorcount = 0
        self.apt = self.create_bulb_group()
        
    def create_bulb_group(self):
        l = ['192.168.0.137', '192.168.0.157']
        lr = sb.bulb_group(l)

        l = '192.168.0.108'
        hk = sb.tplink_huebulb(l)

        l = '192.168.0.154'
        hb = sb.tplink_huebulb(l)

        l = ['192.168.0.107', '192.168.0.153']
        br = sb.bulb_group(l)

        apt = sb.space_group([br, hb, hk, lr])
        return(apt)

    def stop(self):
        self.stream.close()

    def find_input_device(self):
        device_index = None            
        for i in range( self.pa.get_device_count() ):     
            devinfo = self.pa.get_device_info_by_index(i)   
            print( "Device %d: %s"%(i, devinfo["name"]) )

            for keyword in ["mic","input"]:
                if keyword in devinfo["name"].lower():
                    print( "Found an input: device %d - %s"%(i,devinfo["name"]) )
                    device_index = i
                    return device_index

        if device_index == None:
            print( "No preferred input found; using default input device." )

        return device_index

    def open_mic_stream( self ):
        device_index = self.find_input_device()

        stream = self.pa.open(   format = FORMAT,
                                 channels = CHANNELS,
                                 rate = RATE,
                                 input = True,
                                 input_device_index = device_index,
                                 frames_per_buffer = INPUT_FRAMES_PER_BLOCK)

        return stream

    def tapDetected(self):
        print("Tap!")

    def listen(self):
        try:
            block = self.stream.read(INPUT_FRAMES_PER_BLOCK)
        except IOError as e:
            # dammit. 
            self.errorcount += 1
            print( "(%d) Error recording: %s"%(self.errorcount,e) )
            self.stream = self.open_mic_stream()
            self.noisycount = 1
            return

        #amplitude = get_rms( block )
        amplitude = get_loudness(block)
        #print(amplitude)
        # brightness=int((amplitude/0.7)*100)
        # print(brightness)
        # self.apt.send_command('brightness', brightness)
        return(amplitude)
        

if __name__ == "__main__":
    tt = TapTester()
    tt.apt.send_command('brightness',0)
    tt.apt.send_command('color_mode')
    
    
    delay = 0.65
    
    min_amp=999
    max_amp=-999
    span=1
    last=time.time()
    
    span_window = 50
    tt.apt.reconnect()
    for i in range(1,3000):
        try:
            if i%span_window == 0:
                min_amp = 999
                max_amp = -999
                #print('MOD\n\n')
            
            amp = tt.listen()
            if amp > max_amp:
                max_amp = amp
                span = abs(max_amp-min_amp)
                span = span * .75
            elif amp < min_amp:
                min_amp = amp
                span = abs(max_amp-min_amp)
                span=span*.75
                
            
            brightness = int(((amp-min_amp)/span)*100)
            tt.apt.send_command('brightness', brightness)
            
                
            if (time.time()-last > delay):
                tt.apt.party_once()
                last = time.time()
        except:
            tt.apt.reconnect()
