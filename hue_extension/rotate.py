import sys
sys.path.append('/Users/davidparker/Documents/Personal/MyWork/Kasa_Lights/tplink-smartplug/hue_extension')
import tplink_smartbulb_class_udp as sb
import itertools
import time


def hue_fade_bulb(bulb, hue, fade):
    bulb.set_state({'hue': hue, 'transition_period': fade})



commands = [{'hue':0,  'fade':0, 'hold':500, 'type':'slow'}, # red
            {'hue':30, 'fade':0, 'hold':500, 'type':'slow'}, # orange
            {'hue':60, 'fade':0, 'hold':500, 'type':'fast'}, # yellow
            {'hue':90, 'fade':0, 'hold':500, 'type':'fast'}, # ygreen
            {'hue':120,'fade':0, 'hold':500, 'type':'slow'}, # green
            #{'hue':150,'fade':0, 'hold':500, 'type':'slow'}, # lime
            {'hue':180,'fade':0, 'hold':500, 'type':'fast'}, # cyan
            {'hue':210,'fade':0, 'hold':500, 'type':'fast'}, # sea
            {'hue':240,'fade':0, 'hold':500, 'type':'slow'}, # blue
            {'hue':270,'fade':0, 'hold':500, 'type':'slow'}, # purp
            {'hue':300,'fade':0, 'hold':500, 'type':'fast'}, # violet
            {'hue':330,'fade':0, 'hold':500, 'type':'fast'}] # rviolet]


total_time = 4000 # milli seconds
n_commands = len(commands)
nfast = len([c for c in commands if c['type']=='fast'])
nslow = len([c for c in commands if c['type']=='slow'])
total_fast = 0.5 * total_time
total_slow = total_time - total_fast
fast_fade = total_fast / nfast
slow_fade = total_slow / nslow

#
# time_remaining = total_time - (fast_fade * nfast)
# slow_fade = time_remaining / nslow

print(fast_fade)
print(slow_fade)
print(nfast*fast_fade + nslow*slow_fade)

for c in commands:
    if c['type'] == 'fast':
        c['fade'] = int(fast_fade)
    elif c['type'] == 'slow':
        c['fade'] = int(slow_fade)

print(commands)






bulbs = sb.Bulb.all()
#bulbs = sb.Bulb.all()
ips = [b.addr[0] for b in bulbs]

[b.color_mode() for b in bulbs]
[b.set_state({'brightness': 10}) for b in bulbs]

fade = 500

for parts in itertools.cycle(commands):

    h = parts['hue']
    f = parts['fade']
    print(parts)
    [hue_fade_bulb(b, h, f) for b in bulbs]
    time.sleep(f/1000.0)




