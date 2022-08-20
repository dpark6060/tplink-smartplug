#!/usr/bin/python

# open a microphone in pyAudio and listen for taps

import pyaudio
import struct
import math
import tplink_smartbulb_class as sb
import time
import pyaudio
import numpy as np
import logging
from itertools import cycle

log=logging.getLogger()
log.setLevel('INFO')

CHUNK = 2**10
RATE = 44100
#CHUNK = int(0.1*RATE)


p = pyaudio.PyAudio()
info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')

for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))




p=pyaudio.PyAudio()
stream=p.open(format=pyaudio.paInt16,channels=1,rate=RATE,input=True,
              frames_per_buffer=CHUNK,input_device_index=1)

def listen(stream):
    
    data = np.frombuffer(stream.read(CHUNK,exception_on_overflow=False),dtype=np.int16)
    peak=np.average(np.abs(data))*2
    return(peak)


def close(stream,p):
    stream.stop_stream()
    stream.close()
    p.terminate()



if __name__ == "__main__":

    l = ['192.168.0.137', '192.168.0.157']
    lr = sb.bulb_group(l)

    l = '192.168.0.108'
    hk = sb.tplink_huebulb(l)

    l = '192.168.0.154'
    hb = sb.tplink_huebulb(l)

    l = ['192.168.0.107', '192.168.0.153']
    br = sb.bulb_group(l)

    # apt = sb.bulb_group(['192.168.0.137', '192.168.0.157','192.168.0.108','192.168.0.154','192.168.0.107', '192.168.0.153'])

    #apt = sb.space_group([br, hb, hk, lr])
    apt = sb.space_group([lr,hk,hb,br])
    backlight = 240
    backlight_brightness = 100
    
    apt.send_command('on')
    apt.send_command('hue', backlight)
    apt.send_command('brightness', backlight_brightness)

    
    min_amp=99999
    max_amp=-99999
    span=1
    last=time.time()
    
    hues = cycle([0,120,140])
    hues 
    
    span_window = 50
    old_brightness=0
    brightness = 50
    delay = 5
    for i in range(1, 3000):
        try:
            # if i%span_window == 0:
            #     min_amp = 999
            #     max_amp = -999
            #     #print('MOD\n\n')
            
            amp = listen(stream)
            if amp > max_amp*.98:
                print(f'boop - {amp} \t {max_amp}')
                
                if amp > max_amp:
                    max_amp = amp
                apt.soft_pulse_backlight(backlight, backlight_brightness,
                                     0, delay=0.1, n=1)
            else:
                max_amp = max_amp *0.99
            
        
            #apt.send_command('brightness', brightness)
            print(brightness)
            
        
            #time.sleep(0.05)
            # if (time.time()-last > delay):
            #     hue = next(hues)
            #     apt.test_breathe(hue, 0)
            #     last = time.time()
            #     
        except Exception as e:
            log.exception(e)
            apt.reconnect()
            stream.stop_stream()
            stream.close()
            stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True,
                            frames_per_buffer=CHUNK, input_device_index=1)
            print('\n\n\n')