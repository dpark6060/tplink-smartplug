import json
import time

hue = 3

command = {"smartlife.iot.smartbulb.lightingservice": {"transition_light_state": {"hue": hue,"brightness":100}}}

tick = time.time()
for i in range(10000):
    
    a=json.dumps(command)
tock = time.time()
print(a)
print(tock-tick)

command = '{"smartlife.iot.smartbulb.lightingservice": {"transition_light_state": {"hue": ^VAL_IN1,"brightness": ^VAL_IN2}}}'

brightness =100
tick = time.time()
for i in range(10000):
    a=command.replace('^VAL_IN1', str(hue)).replace('^VAL_IN2', str(brightness))
tock = time.time()
print(tock-tick)
print(a)

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