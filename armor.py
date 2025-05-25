ess_need = [[0,50,150,350,700,1200],[0,100,300,650,1250,2250],[0,75,225,475,875,1575],[0,50,150,350,700,1200]]

#price
base = 7
frag = 200
ess = 0.33
master_star = [930,1100,1925,4000,7000]
potato = 10
fuming = 105
g6 = 900
p6 = 360
reju = 3.6
r3k = 912

#stat
part = 3
star = 5
potato_num = 10
fuming_num = 5
g6ed = 0
p6ed = 0
gem = 0
master = 0
rejued = 1
r3ked = 1

print(base+8*frag+ess_need[part-1][star]*ess+potato*potato_num+fuming*fuming_num+g6ed*g6+p6ed*p6+gem*500+sum(master_star[:master])+r3ked*r3k+rejued*reju*16)
