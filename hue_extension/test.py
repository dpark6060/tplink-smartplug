import json
import time

hue = 3

command = {"smartlife.iot.smartbulb.lightingservice": {"transition_light_state": {"hue": hue}}}

tick = time.time()
for i in range(10000):
    a=json.dumps(command)
tock = time.time()

print(tock-tick)

command = '{"smartlife.iot.smartbulb.lightingservice": {"transition_light_state": {"hue": ^VAL_IN}}}'

tick = time.time()
for i in range(10000):
    a=command.replace('^VAL_IN', str(hue))
tock = time.time()
print(tock-tick)