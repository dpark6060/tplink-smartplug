import tplink_smartbulb_class_udp as tp
import time
import random


def set_white(bulbs):
    cmd = {'on_off':1,'brightness':50,'saturation':0,'color_temp':5000}
    [bulb.set_state(cmd) for bulb in bulbs]
    



def flicker(lights,duration):
    now = time.time()
    
    while time.time() < now+duration:
        light = random.choice(lights)
        light.onoff()
        sleep = random.random() * 0.5
        time.sleep(sleep)
        
    
    
def strobe_red(lights):
    
    [light.on() for light in lights]
    time.sleep(0.05)
    [light.color_mode() for light in lights]
    time.sleep(0.05)
    
    dim = {'brightness':0, 'transition_period':0}
    bright = {'brightness':100,'transition_period':0}
    
    time_on = 0.1
    time_off = 0.9
    
    while True:
        [light.set_state(bright) for light in lights]
        time.sleep(time_on)
        [light.set_state(dim) for light in lights]
        time.sleep(time_off)



if __name__ == '__main__':

    bulbs = tp.Bulb.all()
    
    set_white(bulbs)
    flicker(bulbs,5)
    strobe_red(bulbs)

