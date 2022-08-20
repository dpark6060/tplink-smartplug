#!/usr/bin/env python3.7

import json
import time
import rapidjson

hue = 3

command = {"smartlife.iot.smartbulb.lightingservice": {"transition_light_state": {"hue": hue, "brightness":100}}}

cmd_string_pre = '{"smartlife.iot.smartbulb.lightingservice": {"transition_light_state":'
cmd_string_post = '}}'




tick = time.time()
for i in range(10000):
    d={}
    d['on_off'] = 0
    d['hue'] = 120
    d['brightness'] = 65
    d['saturation'] = 100
    d['transition_period'] = 0
    cmd = ''.join((cmd_string_pre, json.dumps(d), cmd_string_post))
tock = time.time()
print(cmd)
print(tock-tick)

tick = time.time()
for i in range(10000):
    d={}
    d['on_off'] = 0
    d['hue'] = 120
    d['brightness'] = 65
    d['saturation'] = 100
    d['transition_period'] = 0
    cmd = ''.join((cmd_string_pre, rapidjson.dumps(d), cmd_string_post))
tock = time.time()
print(cmd)
print(tock-tick)


tick = time.time()
for i in range(10000):
    d={}
    d['on_off'] = 0
    d['hue'] = 120
    d['brightness'] = 65
    d['saturation'] = 100
    d['transition_period'] = 0
    a = ','.join([f'"{key}":{val}' for key, val in d.items()])
    cmd = ''.join((cmd_string_pre, a, cmd_string_post))
tock = time.time()
print(cmd)
print(tock-tick)


tick = time.time()
for i in range(10000):
    on_off = 0
    hue = 120
    brightness = 65
    saturation = 100
    transition_period = 0
    
    settings = []
    if on_off:
        settings.append(f'"on_off":{on_off}')
    if hue:
        settings.append(f'"hue":{hue}')
    if brightness:
        settings.append(f'"brightness":{brightness}')
    if saturation:
        settings.append(f'"saturation":{saturation}')
    if transition_period:
        settings.append(f'"transition_period":{transition_period}')
    a=','.join(settings)
    cmd = ''.join((cmd_string_pre, a, cmd_string_post))
tock = time.time()
print(cmd)
print(tock-tick)

# cmd = {'hue':34}
# 
# 
# tick = time.time()
# for i in range(10000):
#     a= '{"smartlife.iot.smartbulb.lightingservice":{"transition_light_state":'+ json.dumps(cmd)+ '}}'
# tock = time.time()
# 
# print(tock-tick)
# 
# command = ''.join((
#             '{"smartlife.iot.smartbulb.lightingservice":{',
#             '"transition_light_state":', json.dumps(cmd), '}}'
#         ))
# 
# tick = time.time()
# for i in range(10000):
#     a= ''.join((
#             '{"smartlife.iot.smartbulb.lightingservice":{',
#             '"transition_light_state":', json.dumps(cmd), '}}'
#         ))
# tock = time.time()
# print(tock-tick)