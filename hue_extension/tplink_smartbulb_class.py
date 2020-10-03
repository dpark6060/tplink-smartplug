#!/usr/bin/env python3
#
# TP-Link Wi-Fi Smart Plug Protocol Client
# For use with TP-Link HS-100 or HS-110
#
# by Lubomir Stroetmann
# Copyright 2016 softScheck GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import sys
import socket
import argparse
from struct import pack
import time
import json
from itertools import cycle
import random
import pprint
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import csv

import simpleaudio as sa
import wave
import progressbar
import os
import logging

progressbar.streams.wrap_stderr()
logging.basicConfig()


lst = ['a', 'b', 'c']



version = 0.3


messages = ['Initiating Scan...Scanning....',
            'Party Levels Low.',
            'Searching for good vibes',
            'Calculating chance of tequila',
            'Identifying mood',
            'Engaging in amp-up protocol',
            'Finding Hypeman',
            'Identifying Party People',
            'Eliminating Buzz Kills',
            'Initiate Mood Booster Subroutine',
            'Identifying optimal party subroutine']

message_times = [0.25,
                 3,
                 1,
                 0.5,
                 0.25,
                 0.25,
                 1,
                 0.25,
                 2,
                 1,
                 0.5]


def progress_bar(message, duration):
    
    sleep = duration/100.0
    print(message)
    for i in progressbar.progressbar(range(100), redirect_stdout=True):
        time.sleep(sleep)



# Check if hostname is valid
def validHostname(hostname):
    try:
        socket.gethostbyname(hostname)
    except socket.error:
        print("Invalid hostname.")
    return hostname


# Check if port is valid
def validPort(port):
    try:
        port = int(port)
    except ValueError:
        print("Invalid port number.")

    if ((port <= 1024) or (port > 65535)):
        print("Invalid port number.")

    return port




def encrypt(string):
    key = 171
    result = pack('>I', len(string))
    for i in string:
        a = key ^ ord(i)
        key = a
        result += bytes([a])
    return result


def decrypt(string):
    key = 171
    result = ""
    for i in string:
        a = key ^ i
        key = i
        result += chr(a)
    return result



class tplink_huebulb:
    def __init__(self, ip, port = 9999):
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))
        
        self.hue = 0
        self.brightness = 100
        self.saturation = 100
        
        self.prev_hue = 0
        self.prev_brightness = 0
        self.prev_sat = 0
        
        self.party_hue = 0
        self.party_hues = [0, 120, 240]
        
        self.commands={
            'hue': '{"smartlife.iot.smartbulb.lightingservice": {"transition_light_state": {"hue": ^IN}}}',
            'on': '{"smartlife.iot.smartbulb.lightingservice": {"transition_light_state": {"on_off": 1}}}',
            'off':        '{"smartlife.iot.smartbulb.lightingservice": {"transition_light_state": {"on_off": 0}}}',
            'brightness': '{"smartlife.iot.smartbulb.lightingservice": {"transition_light_state": {"brightness": ^IN}}}',
            'saturation': '{"smartlife.iot.smartbulb.lightingservice": {"transition_light_state": {"saturation": ^IN}}}',
            'color_mode': '{"smartlife.iot.smartbulb.lightingservice": {"transition_light_state": {"saturation": 100, "brightness": 100, "color_temp": 0, "hue": 0}}}',
            'color_temp': '{"smartlife.iot.smartbulb.lightingservice": {"transition_light_state": {"color_temp": ^IN}}}',
            'soft_off': '{"smartlife.iot.smartbulb.lightingservice": {"transition_light_state": {"brightness": 0, "hue": 0 }}}',
            'bright_hue': '{"smartlife.iot.smartbulb.lightingservice": {"transition_light_state": {"hue": ^IN, "brightness": 100}}}'
        }
    
    def status(self):
        
        sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_tcp.settimeout(10)
        sock_tcp.connect((self.ip, self.port))
        sock_tcp.send(encrypt('{"system":{"get_sysinfo":{}}}'))
        data = sock_tcp.recv(2048)
        sock_tcp.close()

        decrypted = decrypt(data[4:])
        dj = json.loads(decrypted)
        pprint.pprint(dj)
        
    
    def reconnect(self):
        self.socket.close()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip, self.port))
    
    def send(self):
        self.socket.send(encrypt(self.cmd))
    
    def set_hue(self, hue):
        self.cmd = self.commands['hue'].replace('^IN', str(hue))
        self.send()
        
        self.prev_hue = self.hue
        self.hue = hue
    
    def set_prev_hue(self):
        self.set_hue(self, self.prev_hue)
    
    def send_command(self, command, val=''):
        if command == 'custom':
            self.cmd = '{"smartlife.iot.smartbulb.lightingservice": {"transition_light_state": '+ val +'}}'
            self.send()
        else:
            self.cmd = self.commands[command].replace('^IN', str(val))
            self.send()
        
        if command == 'hue':
            self.prev_hue = self.hue
            self.hue = val
        elif command == 'brightness':
            self.prev_brightness = self.brightness
            self.brightness = val
        elif command == 'saturation':
            self.prev_saturation = self.saturation
            self.saturation = val
    
    
    def party_once(self):
        party_hue = self.party_hue
        while party_hue == self.party_hue:
            party_hue = random.choice(self.party_hues)
        self.send_command('hue', party_hue)
        self.party_hue = party_hue

        
    def __exit__(self):
        self.socket.close()
        
        
# colors = {
#     'bedroom2': '192.168.0.107',
#     'bedroom1': '192.168.0.153',
#     'livingroom2': '192.168.0.137',
#     'livingroom1': '192.168.0.157',
#     'br_hall_color': '192.168.0.154',
#     'kt_hall_color': '192.168.0.108'
#     }
# 
# test = tplink_huebulb(colors['livingroom1'])
# test.send_command('hue', 120)

def rotate(l, n):
    return l[n:] + l[:n]


class bulb_group:
    def __init__(self, bulb_ips, name=''):
        self.name = name
        self.bulbs = [tplink_huebulb(ip) for ip in bulb_ips]
        self.nbulbs = len(self.bulbs)
        self.call_time = 0.001*self.nbulbs
        self.party_hue = 0
        self.party_hues = [0, 120, 240]
        self.prev_hue = 0
        self.prev_brightness = 0
        self.prev_sat = 0
        
    def reconnect(self):
        [bulb.reconnect() for bulb in self.bulbs]
    
        
    def send_command(self, command, val=''):
        [bulb.send_command(command, val) for bulb in self.bulbs]
    
    
    
    def rotate_hues(self,hues,delay=0.75):
        hue_cycle = cycle(hues)
        
        while True:
            [bulb.send_command('hue', next(hue_cycle)) for bulb in self.bulbs]
            if len(hues)%self.nbulbs == 0:
                next(hue_cycle)
            time.sleep(delay)
            
    def sweep(self, start_hue,stop_hue, sweep_time):
        ncalls = 100
        delay = sweep_time/ncalls
        dhue = (stop_hue-start_hue)/ncalls
        new_hue = start_hue
        
        for c in range(ncalls):
            self.send_command('hue', new_hue)
            new_hue =int(round(new_hue + dhue))
            time.sleep(delay)
    
    def alternate_flash(self, hue,delay=0.7):
        bulb_cycle = cycle(self.bulbs)
        
        self.send_command('soft_off')
        while True:
            bulb = next(bulb_cycle)
            bulb.send_command('bright_hue',hue)
            time.sleep(delay)
            bulb.send_command('soft_off')
            
    def reconnect(self):
        [bulb.reconnect() for bulb in self.bulbs]
        
        
    def party(self, delay=0.7, hues = None, n=float('inf')):
        
        if not hues:
            hues = self.party_hues
        tick = time.time()
        while n != 0:
            party_hue = random.choice(hues)
            while party_hue == self.party_hue:
                party_hue = random.choice(hues)
            self.send_command('hue', party_hue)
            self.party_hue = party_hue
            time.sleep(delay)
            n -= 1
            tock = time.time()
            if tock - tick > 60*2:
                self.reconnect()
                
                
        
    def party_once(self):
        party_hue = self.party_hue
        while party_hue == self.party_hue:
            party_hue = random.choice(self.party_hues)
        self.send_command('hue', party_hue)
        self.party_hue = party_hue
        
        
    def set_prev_hue(self):
        [bulb.set_prev_hue() for bulb in self.bulbs]
        
        
class space_group:
    def __init__(self, devices_list):
        self.groups = devices_list
    
    def reconnect(self):
        [g.reconnect() for g in self.groups]
        
    def send_command(self, command, value=''):
        [g.send_command(command, value) for g in self.groups]
    
    def pulse(self, delay=0.5, n=float('inf')):
        self.send_command('off')
        
        while n > 0:
            for group in self.groups:
                group.send_command('on')
                time.sleep(delay)
                group.send_command('off')
                n -= 1

    def soft_pulse(self, delay=0.5, n=float('inf')):
        self.send_command('on')
        self.send_command('brightness',0)

        while n > 0:
            self.send_command('brightness', 0)
            for group in self.groups:
                group.send_command('brightness', 100)
                time.sleep(delay)
                group.send_command('brightness', 0)
                
            n -= 1

    def soft_pulse_backlight(self, backlight, backlight_brightness,
                             pulselight, delay=0.5, n=float('inf')):
        
        self.send_command('on')
        self.send_command('hue', backlight)
        self.send_command('brightness', backlight_brightness)
        bl_command = '{"hue": '+ str(backlight) + ',"brightness": '+ str(backlight_brightness)+'}'
        pl_command = '{"hue": '+ str(pulselight) + ',"brightness": '+ str(100)+'}'
        print(bl_command)
        print(pl_command)
        
        while n > 0:
            self.send_command('custom', bl_command)

            for group in self.groups:
                group.send_command('custom', pl_command)
                time.sleep(delay)
                group.send_command('custom', bl_command)

            n -= 1
            
    def every_other(self,hue1, hue2, n=1, delay=0.3):
        
        subg1 = self.groups[::2]
        subg2 = self.groups[1::2]
        
        while n > 0:
            [s.send_command('hue', hue1) for s in subg1]
            [s.send_command('hue', hue2) for s in subg2]
            hue1, hue2 = [hue2,hue1]
            time.sleep(delay)
            n-=1

    def fun_party(self):
        os.environ['WRAP_STDERR'] = 'true'
        path_to_file = 'data/PartyStart.wav'
        wave_read = wave.open(path_to_file, 'rb')
        audio_data = wave_read.readframes(wave_read.getnframes())
        num_channels = wave_read.getnchannels()
        bytes_per_sample = wave_read.getsampwidth()
        sample_rate = wave_read.getframerate()

        wave_obj = sa.WaveObject(audio_data, num_channels, bytes_per_sample, sample_rate)
        play_obj = wave_obj.play()

        self.send_command('color_mode')
        for m, t in zip(messages, message_times):
            progress_bar(m, t)
            
        self.send_command('hue',240)
        
        party_list = 'data/dancetypes.txt'
        partyfile = open(party_list,'r')
        lines = partyfile.readlines()
        lines = [l.rstrip() for l in lines]
        ntypes = len(lines)
        total_time = 10.75
        delay = total_time/ntypes
        for i in progressbar.progressbar(range(ntypes)):
                logging.error(f'{lines[i]}')
                time.sleep(delay)

        self.party()


    def party(self):
        [group.party() for group in self.groups]
    # colors = {
    #     'bedroom2': '192.168.0.107',
    #     'bedroom1': '192.168.0.153',
    #     'livingroom2': '192.168.0.137', - close to hw
    #     'livingroom1': '192.168.0.157', - close to door
    #     'br_hall_color': '192.168.0.154',
    #     'kt_hall_color': '192.168.0.108'
    #     }
    
    def party_once(self):
        [group.party_once() for group in self.groups]
        
        
        


