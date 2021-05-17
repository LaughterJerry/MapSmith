#!/usr/bin/env python

import random
import time
import json
import copy
import pygame

import tools
import cellular
import decorum
import kernals

from itertools import chain

def gen_blank_map(width, height, default):
	outmap = []
	for y in range(height):
		line = []
		for x in range(width):
			line.append(default)
		outmap.append(line)
	return outmap

########### seeds #################
water_seed = 2048
treetop_seed = 7664
path_seed = 2864
d2grass_seed = 3920

########## parameters ##############
width = 120
height = 120
tree_density = 95
water_density = 80
tuft_density = 70

rounds = 9
shift = 5
double_width=1
double_height=0
double_pad = 2

############# object lists #####################
forest_objects = [88, 89, 90, 91, 92,195,182, 95, 87,175, 96, 97, 98, 99,100,171,179,103,188,183, 105,371,107,187,178,170,111,181,102]
water_objects = [191, 190, 189]
winter_objects = [152,153,154,155,156,166,186,159, 167,161,143,163,164,379]

############### data template ###############
data = {"autoplayBgm":False,"autoplayBgs":False,"battleback1Name":"","battleback2Name":"","bgm":{"name":"","pan":0,"pitch":100,"volume":90},"bgs":{"name":"","pan":0,"pitch":100,"volume":90},"disableDashing":False,"displayName":"","encounterList":[],"encounterStep":30,"height":height,"note":"","parallaxLoopX":False,"parallaxLoopY":False,"parallaxName":"","parallaxShow":True,"parallaxSx":0,"parallaxSy":0,"scrollType":0,"specifyBattleback":False,"tilesetId":2,"width":width,"data":[],"events":[None,None]}

################## layers #################
ground = gen_blank_map(width, height, 2816) 
dgrass = gen_blank_map(width, height, 0)
objects = gen_blank_map(width, height, 0)
trees = gen_blank_map(width, height, 0)
shadow = gen_blank_map(width, height, 0)
data6 = gen_blank_map(width, height, 0)

#def draw_line(inmap, x, y, width):


tree_map = []#cellular.create_organic_map(int(width/2), height, density, 9, 5, double_width=1, double_height=0, double_pad = 2, path = ([0,0], [80,80]))
water_map = []
path_map = []
d_2_grass = []

################################ temp functions go here ############################



####################################creating water here##############################

cellular.generate_noise_map(water_map, int(width/2),height,cellular.generate_odds(water_density))
water_map = cellular.do_rounds(water_map, int(width/2), height, rounds, shift)


####################################creating trees here##############################

cellular.generate_noise_map(tree_map, int(width/2),height,cellular.generate_odds(tree_density))

tools.mask_overlay(int(width/2), height, water_map, tree_map)

#carves a path through the  randomly generated noise to form a path through the forest
line = tools.linear_interp([0,60], [80,60])

for point in line:
	tools.clear_square(tree_map, point, 1, 0)

tree_map = cellular.do_rounds(tree_map, int(width/2), height, 0, 9)

for h in range(double_height):
	tree_map = cellular.doubler(tree_map, True, False)

for w in range(double_width):
	if w == double_width-1:
		tree_map = cellular.doubler(tree_map, False, True, double_pad)
	else:
			tree_map = cellular.doubler(tree_map, False, True)

water_map = cellular.doubler(water_map, False, True)


####################################creating paths ###############################

cellular.generate_noise_map(path_map, width,height,cellular.generate_odds(water_density))

line = tools.linear_interp([0,60], [120,60])

for point in line:
	tools.clear_square(path_map, point, 1, 1)

path_map = cellular.do_rounds(path_map, width, height, rounds, shift)
tools.mask_overlay(width, height, water_map, path_map)
tools.shape_blob(width, height, kernals.kernals, path_map, ground, path_seed)

###################################populate with objects###################

for y in range(height):
	for x in range(width):
		if not tree_map[y][x] and not water_map[y][x] and not path_map[y][x] :
			if not random.randrange(20):
				objects[y][x] = random.choice( forest_objects )
		elif not tree_map[y][x] and water_map[y][x] :
			if not random.randrange(20):
				objects[y][x] = random.choice( water_objects )
		else:
			pass

#################################add trees ##########################

decorum.add_trees(width, height, tree_map)

####################################creating dark grass here######################

####################################creating dark grass 2 here##############################

cellular.generate_noise_map(d_2_grass, width,height,cellular.generate_odds(tuft_density))
d_2_grass = cellular.do_rounds(d_2_grass, width, height, rounds, shift)

t_d_grass = []
decorum.pop_dark_grass(tree_map, t_d_grass)

print("generate noise map")

tools.mask_overlay(width, height, water_map, t_d_grass)


tools.mask_overlay(width, height, water_map, d_2_grass)
tools.mask_overlay(width, height, t_d_grass, d_2_grass)



####################################doubling water#####################

for y in ground :
	for x in y:
		if x == 3920:
			print("####", end='')
		else:
			print(x, end='')
	print()



tools.shape_blob(len(water_map[0]), len(water_map), kernals.kernals, water_map, ground, water_seed)
tools.shape_blob(len(d_2_grass[0]), len(d_2_grass), kernals.kernals, d_2_grass, dgrass, d2grass_seed)

decorum.kern_dark_grass(t_d_grass, dgrass)

#tools.merge_maps(dgrass, d_2_grass)



###################################

ground = list(chain.from_iterable(ground))
tree_map = list(chain.from_iterable(tree_map))
dgrass = list(chain.from_iterable(dgrass))

objects = list(chain.from_iterable(objects))
shadow = list(chain.from_iterable(shadow))
data6 = list(chain.from_iterable(data6))

data["data"] = ground + dgrass + objects + tree_map + shadow + data6 

#for y in water_map:
#	for x in y:
#		print(x, end='')
#	print()

thingus = open("Map001.json", "w")
thingus.write(json.dumps(data))
thingus.close()