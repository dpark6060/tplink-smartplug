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
import rapidjson
import dirtyjson
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




GlobalSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def enc(ascii_string):
    key = 0xAB
    bs = bytearray(ascii_string, 'ascii')
    for i, byte in enumerate(bs):
        key = key ^ byte
        bs[i] = key
    return bytes(bs)


def dec(byte_string):
    key = 0xAB
    bs = bytearray(byte_string)
    for i, byte in enumerate(bs):
        bs[i] = key ^ byte
        key = byte
    return bs.decode('ascii')


class Bulb:
    SYS_CMD = '{"system":{"get_sysinfo":{}}}'

    @staticmethod
    def trans_cmd_str(cmd):
        """ Make a transition command string from the command """
        return ''.join((
            '{"smartlife.iot.smartbulb.lightingservice":{',
            '"transition_light_state":', rapidjson.dumps(cmd), '}}'
        ))

    @staticmethod
    def new_cmd_str(cmd):
        """ Make a transition command string from the command """
        return ''.join((
            '{"smartlife.iot.smartbulb.lightingservice":{',
            '"transition_light_state":{', cmd, '}}}'
        ))

    @staticmethod
    def all(timeout=1):
        """ Find all of the lightbulbs on your network. Most respond in
            less than 0.1 seconds
        """
        msg = enc(Bulb.SYS_CMD)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.sendto(msg, ('255.255.255.255', 9999))

        lights = []
        try:
            while True:
                s.settimeout(timeout)
                data, addr = s.recvfrom(1025)
                lights.append(Bulb(addr, sysinfo=dec(data)))

        except socket.timeout:
            pass

        return lights

    def __init__(self, ip_port, sysinfo=None, sock=GlobalSocket):
        print(ip_port)
        #print(sysinfo)
        self.addr = ip_port
        self.sock = sock
        self.transition_period_ms = 0
        self.name = 'unknown'
        self.prev_hue = 0
        

        if sysinfo:
            self._read_sysinfo(sysinfo)
        else:
            self.refresh()

    def _read_sysinfo(self, sysinfo):
        
        print(sysinfo)
        try:
            js = json.loads(sysinfo)
        except Exception:
            print('Adding } 1')
            n=0
            while n < 5:
                sysinfo+='}'
                try:
                    js = json.loads(sysinfo)
                except Exception as e:
                    print('Adding } '+str(n+2))
                    n+=1
                else:
                    break
                

        #print(js)
        if 'system' not in js.keys():
            self.cmd(Bulb.trans_cmd_str({'on_off': 1}))
            time.sleep(0.01)
            sysinfo = self.response_cmd(Bulb.SYS_CMD)
            js = json.loads(sysinfo)
            print(js)
            print(self.addr[0])
            if 'system' not in js.keys():
                self.name = 'unknown'
                self.power = 1
                self.state = 0
                self.current_hue = 0
                return

        js = js['system']['get_sysinfo']

        self.name = js['alias']
        self.power = js['light_state']['on_off'] == 1
        state = js['light_state'] if self.power else js['preferred_state'][0]
        self.state = state
        self.current_hue = state.get('hue')
        self.is_color = js.get('is_color')
        if self.is_color == None:
            self.is_color = 1
        
        
    # def onoff_cmd(self, val):
    #     return(f'"on_off":{val}')
    # 
    # def hue_cmd(self,val):
    #     return(f'"hue":{val}')
    
    def set_state(self, cmds):
        
        if 'hue' in cmds:
            self.prev_hue = self.current_hue
            self.current_hue = cmds['hue']
            
        return self.cmd(Bulb.trans_cmd_str(cmds))
        
    
    def write_state(self, transition_ms=0):
        d = {}
        if self.power:
            d['on_off'] = 1
            d['hue'] = self.hue
            d['saturation'] = self.sat
            d['color_temp'] = self.temp
            d['brightness'] = self.bright
            d['transition_period'] = transition_ms
        else:
            d['on_off'] = 0

        return self.cmd(Bulb.trans_cmd_str(d))

    def hue(self, hue):
        self.prev_hue = self.current_hue
        self.current_hue = hue
        hue_cmd = Bulb.trans_cmd_str({'hue': hue,'transition_period':0})
        return self.cmd(hue_cmd)

    def onoff(self):
        self.power = not self.power
        value = 1 if self.power else 0
        return self.cmd(Bulb.trans_cmd_str({'on_off': value, 'transition_period': 0}))

    def off(self):
        if self.power:
            self.power = False
            return self.cmd(Bulb.trans_cmd_str({'on_off': 0}))
        
    def on(self):
        if not self.power:
            self.power = True
            return self.cmd(Bulb.trans_cmd_str({'on_off': 1}))
    
    def response_cmd(self, cmd_string):
        #print(cmd_string)
        e = enc(cmd_string)
        self.sock.sendto(e, self.addr)
        data, addr = self.sock.recvfrom(2046)
        return(dec(data))
    
    def cmd(self, cmd_string):
        e = enc(cmd_string)
        self.sock.sendto(e, self.addr)
        #data, addr = self.sock.recvfrom(1025)
        #return(data)

    def color_mode(self):
        if self.is_color == 1:
            self.set_state({"on_off":1,"saturation":100,"brightness":100,"color_temp":0,"hue":0})
        else:
            self.off()
        
    def refresh(self):
        self._read_sysinfo(self.response_cmd(Bulb.SYS_CMD))

    def __str__(self):
        return f"Bulb \"{self.name}\" @ {self.addr[0]}"

    def __repr__(self):
        return f"<{self.__str__()}>"
    
    



class bulb_group:
    def __init__(self, bulb_ips, name=''):
        print(bulb_ips)
        self.name = name
        self.bulbs = [Bulb((ip, 9999)) for ip in bulb_ips]
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
    
    def alternate_flash(self, hue,delay=0.1):
        bulb_cycle = cycle(self.bulbs)
        
        self.send_command('soft_off')
        while True:
            bulb = next(bulb_cycle)
            bulb.send_command('bright_hue',hue)
            time.sleep(delay)
            bulb.send_command('soft_off')
            
    def reconnect(self):
        [bulb.reconnect() for bulb in self.bulbs]
        
        
    def party(self, delay=0.05, hues = None, n=float('inf')):
        
        if not hues:
            hues = self.party_hues
        tick = time.time()
        print('partying')
        while n != 0:
            
            party_hue = random.choice(hues)
            
            while party_hue == self.party_hue:
                party_hue = random.choice(hues)
                #print(f'party_hue = {party_hue}')
                
            self.hue(party_hue)
            self.party_hue = party_hue
            time.sleep(delay)
            n -= 1
            tock = time.time()
            
            if tock - tick > 60*2:
                self.reconnect()
                
    def set_state(self,cmds):
        [bulb.set_state(cmds) for bulb in self.bulbs]
        
    def party_once(self):
        party_hue = self.party_hue
        while party_hue == self.party_hue:
            party_hue = random.choice(self.party_hues)
        self.hue(party_hue)
        self.party_hue = party_hue
        
    def hue(self, hue):
        [bulb.hue(hue) for bulb in self.bulbs]

    def set_prev_hue(self):
        [bulb.set_prev_hue() for bulb in self.bulbs]
    
    def color_mode(self):
        
        [bulb.color_mode() for bulb in self.bulbs]

    def test_breathe(self, hue, tp):
        [bulb.test_breathe(hue, tp) for bulb in self.bulbs]

    def test_bright(self, bright, tp):
        [bulb.test_bright(bright,tp) for bulb in self.bulbs]

        
class space_group:
    def __init__(self, devices_list):
        self.groups = devices_list
        self.party_hues = list(range(0,359,30)) 
    
    def reconnect(self):
        [g.reconnect() for g in self.groups]
        
    def send_command(self, command, value=''):
        [g.send_command(command, value) for g in self.groups]
    
    def pulse(self, delay=0.1, n=float('inf')):
        self.send_command('off')
        
        while n > 0:
            for group in self.groups:
                group.send_command('on')
                time.sleep(delay)
                group.send_command('off')
                n -= 1

    def soft_pulse(self, delay=0.1, n=float('inf')):
        self.send_command('on')
        self.send_command('brightness',0)
        hues = cycle(self.party_hues)
        i=0
        while n > 0:
            hue=next(hues)
            self.send_command('brightness', 0)
            
            for group in self.groups:
                group.send_command('bright_hue', hue)
                time.sleep(delay)
                group.send_command('brightness', 0)
                
                
            n -= 1

    def soft_pulse_backlight(self, backlight, backlight_brightness,
                             pulselight, delay=0.5, n=float('inf')):
        
        bl_command = '{"transition_period": 0, "hue": '+ str(backlight) + ',"brightness": '+ str(backlight_brightness)+'}'
        pl_command = '{"transition_period": 0, "hue": '+ str(pulselight) + ',"brightness": '+ str(100)+'}'
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
        total_time = 11.2
        delay = total_time/ntypes
        for i in progressbar.progressbar(range(ntypes)):
                logging.error(f'{lines[i]}')
                time.sleep(delay)

        self.party()


    def party(self, delay=0.1):
        while True:
            [group.party_once() for group in self.groups]
            time.sleep(delay)
            
    def test_breathe(self, hue, tp):
        [group.test_breathe(hue, tp) for group in self.groups]
        
    def test_bright(self, bright, tp):
        [group.test_bright(bright, tp) for group in self.groups]
    
    def party_once(self):
        [group.party_once() for group in self.groups]
    
    def color_mode(self):
        [group.color_mode() for group in self.groups]
        
    def timed_pulse(self, transition=1000, delay=0.1, interval=5, n=float('inf')):
        
        hues = cycle([0, 120, 240])
       
        
        while n > 0:
            hue = next(hues)
            tick = time.time()
            for group in self.groups:
                group.test_breathe(hue, transition)
                time.sleep(delay)
                
            tock = time.time()
            while tock-tick < interval:
                time.sleep(0.05)
                tock = time.time()
            
        
    def set_state(self,cmds):
        [group.set_state(cmds) for group in self.groups]
            

