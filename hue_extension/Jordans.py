#!/usr/bin/env python3

import socket
import time
import select
import json

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
            '"transition_light_state":', json.dumps(cmd), '}}'
        ))

    @staticmethod
    def new_cmd_str(cmd):
        """ Make a transition command string from the command """
        return ''.join((
            '{"smartlife.iot.smartbulb.lightingservice":{',
            '"transition_light_state":', cmd, '}}'
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
        print(sysinfo)
        self.addr = ip_port
        print(self.addr)
        self.sock = sock
        self.transition_period_ms = 0
        self.name = 'unknown'

        if sysinfo:
            self._read_sysinfo(sysinfo)
        else:
            self.refresh()

    def _read_sysinfo(self, sysinfo):
        
        js = json.loads(sysinfo)['system']['get_sysinfo']

        self.name = js['alias']
        self.power = js['light_state']['on_off'] == 1
        state = js['light_state'] if self.power else js['preferred_state'][0]
        self.state = state

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
        hue_cmd = Bulb.trans_cmd_str({'hue': hue})
        return self.cmd(hue_cmd)

    def onoff(self):
        self.power = not self.power
        value = 1 if self.power else 0
        return self.cmd(Bulb.trans_cmd_str({'on_off': value}))

    def off(self):
        if self.power:
            self.power = False
            return self.cmd(Bulb.trans_cmd_str({'on_off': 0}))

    def cmd(self, cmd_string):
        e = enc(cmd_string)
        self.sock.sendto(e, self.addr)
        #data, addr = self.sock.recvfrom(1024)
        

    def refresh(self):
        self._read_sysinfo(self.cmd(Bulb.SYS_CMD))

    def __str__(self):
        return f"Bulb \"{self.name}\" @ {self.addr[0]}"

    def __repr__(self):
        return f"<{self.__str__()}>"


def nuke():
    bulbs = Bulb.all()
    for b in bulbs:
        print(b)
        b.onoff()
