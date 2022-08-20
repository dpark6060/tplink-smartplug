import tplink_smartbulb_class_udp as sb
import itertools as il

def get_living_room(bulbs):
    lvrm = [b for b in bulbs if b.name in ["lvrm_hue_01", "lvrm_hue_02"]]
    return lvrm

def get_livingroom_hues(bulbs):
    lvrm = get_living_room(bulbs)
    states = [l.state for l in lvrm]
    return states

def alternate_colors(states, bulbs):
    bulb_order = ["entr_hue_01", "lvrm_hue_01", "lvrm_hue_02", "hwkt_hue_02","hwkt_hue_01","hwbr_hue_01","hwbr_hue_02", "bdrm_hue_02", "bdrm_hue_01"]

    state_cycle = il.cycle(states)
    print([b.name for b in bulbs])

    for b in bulb_order:
        print(b)
        bulb = [blb for blb in bulbs if blb.name == b][0]
        bulb.set_state(next(state_cycle))


def set_apt_to_livingrooms(bulbs):
    [b.refresh() for b in bulbs]
    hues = get_livingroom_hues(bulbs)
    alternate_colors(hues[::-1], bulbs)

def set_apt_to_livingroom(bulbs):
    [b.refresh() for b in bulbs]
    state = [b.state for b in bulbs if b.name=='lvrm_hue_01']
    alternate_colors(state, bulbs)

def set_rainbow(bulbs):
    bulb_order = ["entr_hue_01", "lvrm_hue_01", "lvrm_hue_02", "hwkt_hue_02","hwkt_hue_01","hwbr_hue_01","hwbr_hue_02"]

    nbulbs = len(bulb_order)
    spacing = int(250/(nbulbs-1))
    hues = range(0,250+spacing-1, spacing)
    bh = zip(bulb_order,hues)

    for b,hue in bh:
        bulb = [blb for blb in bulbs if blb.name == b][0]
        bulb.set_state({"hue":hue,"saturation":100,"brightness":100})


# bulbs = sb.Bulb.all()
# for b in bulbs:
#     print(b.addr[0])
#     #b.color_mode()
# print(len(bulbs))

ips=[
"192.168.0.112",
"192.168.0.180",
"192.168.0.107",
"192.168.0.154",
"192.168.0.108",
"192.168.0.148",
"192.168.0.172",
"192.168.0.157",
"192.168.0.137",
"192.168.0.116"]

bulbs = [sb.Bulb((ip, 9999)) for ip in ips]

set_apt_to_livingrooms(bulbs)



