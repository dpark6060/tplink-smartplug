
import time

def strobe(groups, on_time, off_time, duration):
    dark = {'saturation':0, 'brightness':0,'transition_period': 0,'color_temp':6000}
    bright = {'saturation':0, 'brightness':100,'transition_period': 0,'color_temp':6000}
    
    now = time.time()
    while time.time() < now+duration:
        [group.set_state(bright) for group in groups]
        time.sleep(on_time)
        [group.set_state(dark) for group in groups]
        time.sleep(off_time)

        