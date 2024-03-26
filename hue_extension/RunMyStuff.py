import tplink_smartbulb_class_udp as sb




#bulbs = sb.Bulb.all()

bulbs = sb.Bulb.all()
#bulbs = sb.Bulb.all()
#ips = [b.addr[0] for b in bulbs]

[b.color_mode() for b in bulbs]
[b.set_state({'brightness': 100}) for b in bulbs]

#bgroups=[["entr_hue_01"], ["lvrm_hue_01", "lvrm_hue_02"], ["hwkt_hue_02","hwkt_hue_01"],["hwbr_hue_01","hwbr_hue_02"], ["bdrm_hue_02", "bdrm_hue_01"]]
#
# bulb_groups = []
# for names in bgroups:
#     subgroup=[]
#     for name in names:
#         subgroup.extend([b.addr[0] for b in bulbs if b.name == name])
#
#     bulb_groups.append(sb.bulb_group(subgroup))
bulb_groups=[]
for b in bulbs:
    bulb_groups.append(sb.bulb_group([b.addr[0]]))
spaces_groups = sb.space_group(bulb_groups)


spaces_groups.party()