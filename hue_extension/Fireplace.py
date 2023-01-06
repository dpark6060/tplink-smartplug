import time
import random
import numpy as np
import matplotlib.pyplot as pl
import scipy as sp
from scipy.stats import poisson
import tplink_smartbulb_class_udp as sb
bgroups=[["entr_hue_01"], ["lvrm_hue_01", "lvrm_hue_02"], ["hwkt_hue_02","hwkt_hue_01"],["hwbr_hue_01","hwbr_hue_02"], ["bdrm_hue_02", "bdrm_hue_01"]]


class Fireplace:
    def __init__(self, bulbs, hues=None, brights=None, hue_pdiff=10, bright_pdiff=10, mx_speed=400, mn_speed=100):
        if hues is None:
            hues = list(range(35))
        if brights is None:
            brights = list(range(5, 30))

        self.hue_pdiff = hue_pdiff
        self.bright_pdiff = bright_pdiff

        self.mx_speed = mx_speed
        self.mn_speed = mn_speed

        self.bulbs = bulbs
        self.hues = hues
        self.hue_span = max(hues) - min(hues)

        self.brights = brights

        self.min_bright = min(brights)
        self.max_bright = max(brights)
        self.max_hue = max(self.hues)
        self.min_hue = min(self.hues)
        self.bright_span = self.max_bright - self.min_bright
        print(self.bright_span)

        for b in bulbs:
            hue = random.choice(self.hues)
            bright = random.choice(self.brights)
            b.set_state({'hue': hue, 'brightness': bright})
            b.current_hue = hue
            b.current_bright = bright

    def pick_next_hue_old(self, bulb):

        hue_flicker = int(self.hue_span * self.hue_pdiff / 100)
        bright_flicker = int(self.bright_span * self.bright_pdiff / 100)

        if random.random() > 0.5:
            pn = 1
        else:
            pn = -1

        current_hue = bulb.current_hue
        current_bright = bulb.current_bright

        new_hue = current_hue + pn * hue_flicker
        new_bright = current_bright + pn * bright_flicker

        new_bright = self.equalize_brightness(new_hue, new_bright)

        if new_hue > max(self.hues) or new_hue < min(self.hues):
            new_hue = current_hue + -1 * pn * hue_flicker
        if new_bright > self.max_bright or new_bright < self.min_bright:
            new_bright = random.choice(self.brights)

        speed = random.choice(list(range(self.mn_speed, self.mx_speed)))

        bulb.set_state({'hue': new_hue, 'brightness': new_bright, 'transition_period': speed})
        bulb.current_hue = new_hue
        bulb.current_bright = new_bright
        # time.sleep(speed/1000)
        time.sleep(0.004)

    def equalize_brightness_old(self, hue, bright):

        b = -0.03
        adj_bright = bright + b * (hue - 15)
        # print(adj_bright)
        return (int(adj_bright))

    def equalize_brightness(self, hue, bright):
        new_bright = (48.7 + -1.46 * bright + 0.0255 * (bright ** 2) + -1.66E-04 * (bright ** 3) + 3.72E-07 * (
                    bright ** 4))
        norm_bright = new_bright / 50
        new_bright = norm_bright * new_bright
        return (int(new_bright))

    def fireplace(self, sleep=0.05):

        print('\n\n\n\n')
        fireplace_bulbs = []
        for b in self.bulbs:
            print(b)
            bulb_dict = {'bulb': b,
                         'hue_change': 1,
                         'bright_change': 1,
                         'next_hue': 1,
                         'next_bright': 1,
                         'current_hue': 1,
                         'current_bright': 1}

            fireplace_bulbs.append(bulb_dict)

        for b in fireplace_bulbs:
            print(b)
            bulb = b['bulb']
            bulb.refresh()
            b['current_hue'] = bulb.current_hue
            b['current_bright'] = bulb.current_bright

        fps = 50
        wait = 1.0 / fps

        while True:
            now = time.time()
            for b in fireplace_bulbs:

                if now > b['next_hue']:
                    change, next_time = self.pick_next_hue_change(b['hue_change'], wait)
                    b['next_hue'] = next_time
                    b['hue_change'] = change

                if now > b['next_bright']:
                    change, next_time = self.pick_next_bright_change(b['bright_change'], wait)
                    b['next_bright'] = next_time
                    b['bright_change'] = change

                new_hue = b['current_hue'] + b['hue_change']
                new_bright = b['current_bright'] + b['bright_change']

                b['current_hue'] = new_hue
                b['current_bright'] = new_bright

                if new_hue > self.max_hue:
                    new_hue = self.max_hue
                    b['current_hue'] = new_hue
                    print('hue max')
                elif new_hue < self.min_hue:
                    print('hue min')
                    new_hue = self.min_hue
                    b['current_hue'] = new_hue

                if new_bright > self.max_bright:
                    print('bright_max')
                    new_bright = self.max_bright
                    b['current_bright'] = new_bright
                elif new_bright < self.min_bright:
                    print('bright min')
                    new_bright = self.min_bright
                    b['current_bright'] = new_bright

                new_bright = self.equalize_brightness(new_hue, new_bright)
                cmd = {'transition_period': 0}

                if new_bright != b['current_bright']:
                    cmd['brightness'] = int(new_bright)
                if new_hue != b['current_hue']:
                    cmd['hue'] = int(new_hue)

                # cmd = {'hue': new_hue, 'brightness': new_bright, 'transition_period':0}

                b['bulb'].set_state(cmd)

            #
            time.sleep(wait)
            # print(1 / (time.time() - now))

    def pick_next_hue_change(self, ch, wait):
        hps = int(random.random() * 3) * wait
        if random.random() > 0.5:
            hps *= -1

        next_hue = time.time() + random.random() * 6

        return (hps, next_hue)

    def pick_next_bright_change(self, cb, wait):

        bps = int(random.random() * 5) * wait
        if random.random() > 0.6:
            bps *= -1

        next_bright = time.time() + random.random() * 3

        return (bps, next_bright)

    def fireplace_old(self, sleep=0.05):

        for b in self.bulbs:
            b['hue_rate'] = 0

        while True:
            [self.pick_next_hue(bulb) for bulb in self.bulbs]
            time.sleep(sleep)

    def pick_next_hue(self, bulb):
        pass



def generate_flicker_interval_poisson():
    flicker_rage_hz = poisson.rvs(4, size=1) + 0.5
    flicker_time_ms  = 1.0 / flicker_rage_hz * 1000
    return int(flicker_time_ms)

def generate_command():
    brightness = int(np.random.rand()*50)+25
    fade = generate_flicker_interval_poisson()
    command = {'brightness': brightness,'transition_period': fade}
    return command,fade




bulbs = sb.Bulb.all()
bulb_group = sb.bulb_group([b.addr[0] for b in bulbs if b.name in ["bdrm_hue_02", "bdrm_hue_01"]])
while True:
    command,fade=generate_command()
    bulb_group.set_state(command)
    time.sleep(fade/1000.0)