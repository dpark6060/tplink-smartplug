
import time
import random


class Strobe:
    def __init__(self, groups):
        self.groups = groups
        
    def strobe(self, on_time, off_time, duration):
        dark = {'saturation':0, 'brightness':0,'transition_period': 0,'color_temp':6000}
        bright = {'saturation':0, 'brightness':100,'transition_period': 0,'color_temp':6000}
        
        now = time.time()
        while time.time() < now+duration:
            [group.set_state(bright) for group in self.groups]
            time.sleep(on_time)
            [group.set_state(dark) for group in self.groups]
            time.sleep(off_time)



class color_breathe:
    
    def __init__(self, bulbs, hues, mxf=8000, mnf=500, mxr=5000, mnr=500):
        [b.color_mode() for b in bulbs]

        self.bulbs = {b.addr[0]: {'bulb': b, 'rest': 0} for b in bulbs}

        self.hues = hues
        self.max_fade = mxf
        self.min_fade = mnf
        self.fade_span = self.max_fade - self.min_fade

        self.min_rest = mnr
        self.max_rest = mxr
        self.rest_span = self.max_rest - self.min_rest

    def rand_fade(self):
        return int(random.random() * self.fade_span + self.min_fade)

    def rand_rest(self):
        return random.random() * self.rest_span + self.min_rest

    def hue_fade_bulb(self, bulb, hue, fade):
        bulb.set_state({'hue': hue, 'transition_period': fade})

    def random_fade_and_rest(self, bulb):
        rest = self.rand_rest()
        fade = self.rand_fade()
        hue = random.choice(self.hues)

        while hue == bulb.prev_hue:
            hue = random.choice(self.hues)

        self.hue_fade_bulb(bulb, hue, fade)
        return (time.time() + rest / 1000)

    def aquarium(self):

        while True:
            now = time.time()
            boc = random.choice(list(self.bulbs.keys()))
            boc = self.bulbs[boc]
            if boc['rest'] < now:
                boc['rest'] = self.random_fade_and_rest(boc['bulb'])
                


class Fireplace:
    def __init__(self, bulbs, hues=None, brights=None, hue_pdiff=10, bright_pdiff=10, mx_speed=400, mn_speed=100):
        if hues is None:
            hues = list(range(30))
        if brights is None:
            brights = list(range(10,25))
        
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
        self.bright_span = self.max_bright - self.min_bright
        print(self.bright_span)
       
        
        
        for b in bulbs:
            hue = random.choice(self.hues)
            bright = random.choice(self.brights)
            b.set_state({'hue':hue,'brightness':bright})
            b.current_hue = hue
            b.current_bright = bright
        
    def pick_next_hue(self, bulb):
        
        
        
        hue_flicker = int(self.hue_span*self.hue_pdiff/100)
        bright_flicker = int(self.bright_span*self.bright_pdiff/100)
        
        if random.random() > 0.5:
            pn = 1
        else:
            pn = -1
        
        current_hue = bulb.current_hue
        current_bright = bulb.current_bright
        
        new_hue = current_hue + pn*hue_flicker
        new_bright = current_bright + pn*bright_flicker

        new_bright = self.equalize_brightness(new_hue, new_bright)
        
        if new_hue > max(self.hues) or new_hue < min(self.hues):
            new_hue = current_hue + -1*pn*hue_flicker
        if new_bright > self.max_bright or new_bright < self.min_bright:
            new_bright = random.choice(self.brights)

        speed = random.choice(list(range(self.mn_speed, self.mx_speed)))
        
        bulb.set_state({'hue':new_hue, 'brightness':new_bright, 'transition_period': speed})
        bulb.current_hue = new_hue
        bulb.current_bright = new_bright
        #time.sleep(speed/1000)
        time.sleep(0.004)
    
    def equalize_brightness(self, hue,bright):

        b=-0.01
        adj_bright = bright + b*(hue-15)
        #print(adj_bright)
        return(int(adj_bright))


    def fireplace(self,sleep=0.05):
        while True:
            [self.pick_next_hue(bulb) for bulb in self.bulbs]
            time.sleep(sleep)
        
        
        
        
        
        
        