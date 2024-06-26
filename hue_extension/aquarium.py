import tplink_smartbulb_class_udp as sb
import random
import time


class Aquarium:
    def __init__(self, ips, hues):
        bulbs = [sb.Bulb((ipa, 9999)) for ipa in ips]
        [b.color_mode() for b in bulbs]
        [b.set_state({'brightness':10}) for b in bulbs]
        
        self.bulbs = {b.addr[0]:{'bulb':b, 'rest':0} for b in bulbs}
        
        # For slower bubbly
        # self.hues = hues
        # self.max_fade = 2000
        # self.min_fade = 500
        # self.fade_span = self.max_fade - self.min_fade
        #
        # self.min_rest = 100
        # self.max_rest = 2000
        # self.rest_span = self.max_rest - self.min_rest
        #
        # for faster party
        self.hues = hues
        self.max_fade = 5000
        self.min_fade = 1000
        self.fade_span = self.max_fade - self.min_fade

        self.min_rest = 250
        self.max_rest = 3000
        self.rest_span = self.max_rest - self.min_rest
        
        
    def rand_fade(self):
        return int(random.random()*self.fade_span + self.min_fade)
    
    def rand_rest(self):
        return random.random()*self.rest_span + self.min_rest
      
    def hue_fade_bulb(self, bulb, hue, fade):
        bulb.set_state({'hue': hue, 'transition_period': fade})
        
    def random_fade_and_rest(self, bulb):
        rest = self.rand_rest()
        fade = self.rand_fade()
        hue = random.choice(self.hues)
        
        while hue == bulb.prev_hue:
            hue = random.choice(self.hues)
        
        self.hue_fade_bulb(bulb, hue, fade)
        return(time.time() + rest/1000)
    
    def aquarium(self):
        
        while True:
            now = time.time()
            boc = random.choice(list(self.bulbs.keys()))
            boc = self.bulbs[boc]
            if boc['rest'] < now:
                boc['rest'] = self.random_fade_and_rest(boc['bulb'])
                
        
        

# l = ['192.168.0.137', '192.168.0.157']
# #lr = sb.bulb_group(l)
# 
# l = ['192.168.0.108']
# #hk = sb.bulb_group(l)
# 
# 
# l = ['192.168.0.154']
# #hb = sb.bulb_group(l)
# s
# l = ['192.168.0.107', '192.168.0.153']

# 
# whites = ['192.168.0.172', '192.168.0.182']
# wh = [sb.Bulb((ip, 9999)) for ip in whites]
# [a.set_state({"on_off":0}) for a in wh]
# del wh
# 
# # 
# #wh.set_state({'on_off': 0})
# # #apt.color_mode()
# 



acq_hues = [162, 278, 204, 305, 240, 240, 240, 240,0,20,340,0,20,340,20,340,0]
# 
# # Bulb "kt_hallway_white" @ 192.168.0.172
# # Bulb "kt_hallway_color" @ 192.168.0.108
# # Bulb "livingroom1" @ 192.168.0.157
# # Bulb "br_hallway_color" @ 192.168.0.154
# # Bulb "bedroom 1" @ 192.168.0.107
# # Bulb "br_hallway_white" @ 192.168.0.182
# # Bulb "livingroom2" @ 192.168.0.137
# # Bulb "bedroom 2" @ 192.168.0.153
# 
# ips = ['192.168.0.157', '192.168.0.108', '192.168.0.154', '192.168.0.107', '192.168.0.116', '192.168.0.137','192.168.0.180']
# ips=["192.168.0.116",
# "192.168.0.162",
# "192.168.0.153",
# "192.168.0.157",
# "192.168.0.148",
# "192.168.0.137",
# "192.168.0.172",
# "192.168.0.154",
# "192.168.0.112",
# "192.168.0.180"]

#ips = ["10.16.5.111"]

#bulbs = [sb.Bulb((ip, 9999)) for ip in ips]
bulbs = sb.Bulb.all()
print(bulbs)
#bulbs = sb.Bulb.all()
ips = [b.addr[0] for b in bulbs]

[b.color_mode() for b in bulbs]
[b.set_state({'brightness': 5}) for b in bulbs]
acq_hues = [162, 278, 204, 305, 240, 240, 240, 240,0,20,340,0,20,340,20,340,0]

acq_hues = [0, 120, 162, 278, 204, 305, 240, 340]
# 
# ips = [b.addr[0] for b in bulbs]
#ips = ['192.168.0.137', '192.168.0.157','192.168.0.154','192.168.0.112','192.168.0.180','192.168.0.108','192.168.0.107', '192.168.0.153','192.168.0.148']
aq = Aquarium(ips, acq_hues)



aq.aquarium()