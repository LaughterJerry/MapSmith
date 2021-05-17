#!/usr/bin/env python

import random
import time
import json
import copy
import pygame
#from tools import events
#from tools import main_file_types

"""
DunGen 5.0

Coding style: Functional
purpose: produce maps for rpg maker mv, w*h in size, x*y number of maps
	each map will overlap with the adjacent maps with transfer points located at the border
	players will be transferred to the next map seamlessly (mv has slight lag for some read >:C)
Implementation:
	[X]first a noise map (x*y) will be created
	[X]next an 2D array (x*w + padding*2,y*h + padding*2)will be generated with noise density determined by the noise map, padding will be walls
	[X]the 2D array will be put through (5) rounds of rules (1,3)
	[X]the 2D array will be put through (4) rounds of rules (2,3)
	[X]the 2D array will then be iterated through and tiles will be appended based on the current configuration of tiles (useage of kernals)
	[X]random logs and flowers and sticks will be dropped in if the random location is grass
	[X]a kernal (w+padding*2, h+padding*2) will be made which will copy all elements of the map onto itself at intervals 
		(w*iterX+padding, h*iterY+padding) for the purpose of making maps overlap
	[X]each kernal once filled will be given transfer events along padding perimeter which will lead to a spot on the neighboring map
		if the source and destination are grass blocks only
	[X]a random map in the center will be given a spawn location for the PC if and only if the spawn location is devoid of all obsticals
	[X]all maps will be saved as json files following the Map###.json format, and the identity of each map will be added to Mapinfos.json
	[ ]Populate world with random encounters, getting harder as you travel farther from spawn

	^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

rules:
	1: tile is a wall if it is a wall and sourrounded by (4) or more walls or by 0 walls
	2: tile is a wall if it is a wall and sourrounded by (5) or more walls
	3: tile is a wall if it is not a wall and sourrounded by 5 or more walls

"""

#selected map type:

Transfer = {"id":1,"name":"EV001","note":"","pages":[{"conditions":{"actorId":1,"actorValid":False,"itemId":1,"itemValid":False,"selfSwitchCh":"A","selfSwitchValid":False,"switch1Id":1,"switch1Valid":False,"switch2Id":1,"switch2Valid":False,"variableId":1,"variableValid":False,"variableValue":0},"directionFix":False,"image":{"characterIndex":0,"characterName":"","direction":2,"pattern":0,"tileId":0},"list":[{"code":201,"indent":0,"parameters":[0,2,9,7,0,2]},{"code":0,"indent":0,"parameters":[]}],"moveFrequency":3,"moveRoute":{"list":[{"code":0,"parameters":[]}],"repeat":True,"skippable":False,"wait":False},"moveSpeed":3,"moveType":0,"priorityType":1,"stepAnime":False,"through":False,"trigger":1,"walkAnime":True}],"x":58,"y":22}
NightTint = {"id":2,"name":"EV002","note":"","pages":[{"conditions":{"actorId":1,"actorValid":False,"itemId":1,"itemValid":False,"selfSwitchCh":"A","selfSwitchValid":False,"switch1Id":1,"switch1Valid":False,"switch2Id":1,"switch2Valid":False,"variableId":1,"variableValid":False,"variableValue":0},"directionFix":False,"image":{"characterIndex":0,"characterName":"","direction":2,"pattern":0,"tileId":0},"list":[{"code":223,"indent":0,"parameters":[[0,0,0,136],60,True]},{"code":0,"indent":0,"parameters":[]}],"moveFrequency":3,"moveRoute":{"list":[{"code":0,"parameters":[]}],"repeat":True,"skippable":False,"wait":False},"moveSpeed":3,"moveType":0,"priorityType":1,"stepAnime":False,"through":False,"trigger":4,"walkAnime":True}],"x":31,"y":20}

leveldata = {"disableDashing":False,"height":80,"parallaxShow":True,"specifyBattleback":False,"encounterList":[],"parallaxLoopX":False,"parallaxLoopY":False,"parallaxSx":0,"parallaxSy":0,"note":"","width":120,"battleback2Name":"","tilesetId":2,"autoplayBgs":False,"autoplayBgm":False,"battleback1Name":"","displayName":"","encounterStep":30,"bgm":{"volume":90,"name":"","pan":0,"pitch":100},"parallaxName":"","bgs":{"volume":90,"name":"","pan":0,"pitch":100},"scrollType":0,"data":[],"events":[None]}

print(Transfer["id"])
print(type(Transfer["id"]))

start = time.time()

map_width = 100
map_height = 100
padding = 25
world_width = 10
world_height = 10
density_range = 20
density_base = 100#60# for rpg map
plant_density = 30

final_world_height = map_height*world_height+padding*2
final_world_width = map_width*world_width+padding*2

leveldata = leveldata
leveldata["height"] = map_height + padding*2
leveldata["width"] = map_width + padding * 2

map_info_template = {"id":0,"expanded":False,"name":"","order":3,"parentId":0,"scrollX":1737,"scrollY":1113}

mapinfo = [None]

#A kernal provides a pattern which can be followed to match data
#true = 1, false = 0, don't matter = 2


kernals=[
[[1,1,1],[1,1,1],[1,1,1]], #7664 #2048
[[0,1,1],[1,1,1],[1,1,1]], 
[[1,1,0],[1,1,1],[1,1,1]],
[[0,1,0],[1,1,1],[1,1,1]],

[[1,1,1],[1,1,1],[1,1,0]], #7668
[[0,1,1],[1,1,1],[1,1,0]],
[[1,1,0],[1,1,1],[1,1,0]],
[[0,1,0],[1,1,1],[1,1,0]],


[[1,1,1],[1,1,1],[0,1,1]], #7672
[[0,1,1],[1,1,1],[0,1,1]],
[[1,1,0],[1,1,1],[0,1,1]],
[[0,1,0],[1,1,1],[0,1,1]],

[[1,1,1],[1,1,1],[0,1,0]], #7676
[[0,1,1],[1,1,1],[0,1,0]],
[[1,1,0],[1,1,1],[0,1,0]],
[[0,1,0],[1,1,1],[0,1,0]],

[[2,1,1],[0,1,1],[2,1,1]], #7680
[[2,1,0],[0,1,1],[2,1,1]],
[[2,1,1],[0,1,1],[2,1,0]],
[[2,1,0],[0,1,1],[2,1,0]],

[[2,0,2],[1,1,1],[1,1,1]], #7684
[[2,0,2],[1,1,1],[1,1,0]],
[[2,0,2],[1,1,1],[0,1,1]],
[[2,0,2],[1,1,1],[0,1,0]],

[[1,1,2],[1,1,0],[1,1,2]], #7688
[[1,1,2],[1,1,0],[0,1,2]],
[[0,1,2],[1,1,0],[1,1,2]],
[[0,1,2],[1,1,0],[0,1,2]],

[[1,1,1],[1,1,1],[2,0,2]], #7692
[[0,1,1],[1,1,1],[2,0,2]],
[[1,1,0],[1,1,1],[2,0,2]],
[[0,1,0],[1,1,1],[2,0,2]],

[[2,1,2],[0,1,0],[2,1,2]], #7696
[[2,0,2],[1,1,1],[2,0,2]],
[[2,0,2],[0,1,1],[2,1,1]],
[[2,0,2],[0,1,1],[2,1,0]],

[[2,0,2],[1,1,0],[1,1,2]], #7700
[[2,0,2],[1,1,0],[0,1,2]],
[[1,1,2],[1,1,0],[2,0,2]],
[[0,1,2],[1,1,0],[2,0,2]],

[[2,1,1],[0,1,1],[2,0,2]], #7705
[[2,1,0],[0,1,1],[2,0,2]],
[[2,0,2],[0,1,0],[2,1,2]],
[[2,0,2],[0,1,1],[2,0,2]],
[[2,1,2],[0,1,0],[2,0,2]], #7709
[[2,0,2],[1,1,0],[2,0,2]],
[[2,0,2],[0,1,0],[2,0,2]],
]



emptykernal = [
[2,0,0,0,0,0,2],
[0,0,0,0,0,0,0],
[0,0,0,0,0,0,0],
[2,0,0,0,0,0,2],
[2,0,0,0,0,0,2],
[2,2,0,0,0,2,2],
[2,2,2,2,2,2,2]
]

shadowkernals = [[
[2,2,0,2,2],
[2,1,0,2,2],
[2,1,0,2,2],
[2,2,2,2,2],
[2,2,2,2,2]
]]

def peakRange(stop, start=0, step=1):
	return range(start,stop+start,step) + range(start,stop+start,step)[::-1]

def wrap(num, max):
	if num < 0:
		return (max-1)+num
	if num > max-1:
		return num-(max-1)
	return num

def generate_odds(density):
	return [1] * density + [0] * (200-density)

### Functions to generate 2D arrays for maps
def generate_noise_map(width, height, selection_list):
	map1 = []
	for y in range(height):
		map1.append([])
		for x in range(width):
			map1[y].append(random.choice( selection_list ))
	return map1

def generate_world_map(width, height, noise_map, noise_map_width, noise_map_height, padding):
	output_map = []

	world_map_width = (width*noise_map_width)+(padding*2)
	world_map_height = (height*noise_map_height)+(padding*2)

	for map_y_pos in range(world_map_height):
		if map_y_pos % 100 == 0:
			print("%s %% done with map..." % (int(map_y_pos * (100.0/world_map_height))))
		output_map.append([])
		for map_x_pos in range(world_map_width):
			if (map_x_pos < padding or map_x_pos >= (world_map_width-padding) or map_y_pos < padding or map_y_pos >= (world_map_height-padding)):
				output_map[map_y_pos].append(1)
			else:
				nmap_x = int((map_x_pos-padding)/width)
				nmap_y = int((map_y_pos-padding)/height)
				density = int(noise_map[ nmap_y ][ nmap_x ])
				odds = generate_odds(density+density_base)
				output_map[map_y_pos].append(random.choice(odds ))

	return output_map

### puts maps through one generation of cellular automata
### this one is for the world maps noise averaging
def noise_generation(inmap):
	curmap = []
	for x in range(len(inmap)):
		curmap.append([])
		for y in range(len(inmap[0])):
			value = 0
			for subx in range(-2,3):
				for suby in range(-2,3):
					curx = wrap(x+subx, len(inmap))
					cury = wrap(y+suby, len(inmap[0]))
					value+=inmap[curx][cury]
			#implementation of rules start here ##############################

			curmap[x].append(value/25.0)

			#and end here ##################################################
	return curmap

### runs a binary on/off ruleset for generating walls
def wall_generation(width, height, inmap, padding, ruleset):
	curmap = []

	for map_y_pos in range(height):
		if map_y_pos % 10 == 0:
			print("%s %% done with generation..." % (int(map_y_pos * (100.0/height))))
		curmap.append([])
		for map_x_pos in range(width):
			if (map_y_pos == 0 or map_y_pos == height-1 or map_x_pos == 0 or map_x_pos == width-1):
				curmap[map_y_pos].append(1)
			else:
				count = (inmap[map_y_pos-1][map_x_pos-1] +
						inmap[map_y_pos-1][map_x_pos] +
						inmap[map_y_pos-1][map_x_pos+1] +
						inmap[map_y_pos][map_x_pos-1] +
						inmap[map_y_pos][map_x_pos+1] +
						inmap[map_y_pos+1][map_x_pos-1] +
						inmap[map_y_pos+1][map_x_pos] +
						inmap[map_y_pos+1][map_x_pos+1])
				wall = (inmap[map_y_pos][map_x_pos] == 1)
				#implementation of rules start here ##############################

				if wall:
					if count >= 4 or count == 0 and ruleset:
						curmap[map_y_pos].append(1)
					elif count >= 5 and not ruleset:
						curmap[map_y_pos].append(1)
					else:
						curmap[map_y_pos].append(0)
				else:
					if count >= 5:
						curmap[map_y_pos].append(1)
					else:
						curmap[map_y_pos].append(0)

	return curmap

def compkernal(inmap, pos, kernal):
	try:
		return (
			(kernal[0][0] in [inmap[pos[0]-1][pos[1]-1],2]) and 
			(kernal[0][1] in [inmap[pos[0]-1][pos[1]],2]) and 
			(kernal[0][2] in [inmap[pos[0]-1][pos[1]+1],2]) and 

			(kernal[1][0] in [inmap[pos[0]][pos[1]-1],2]) and 
			(kernal[1][1] in [inmap[pos[0]][pos[1]],2]) and 
			(kernal[1][2] in [inmap[pos[0]][pos[1]+1],2]) and 

			(kernal[2][0] in [inmap[pos[0]+1][pos[1]-1],2]) and 
			(kernal[2][1] in [inmap[pos[0]+1][pos[1]],2]) and 
			(kernal[2][2] in [inmap[pos[0]+1][pos[1]+1],2])
			)
	except:
		print(pos[0], pos[1])
		print(len(inmap[0]))
		exit()



def shadkernal(inmap, pos, kernal):

	kernal_rad = int(len(kernal)/2)

	for kernal_y_pos in range(len(kernal)):
		for kernal_x_pos in range(len(kernal)):
			#try:
			if inmap[int(pos[0]+(kernal_y_pos-kernal_rad))][int(pos[1]+(kernal_x_pos-kernal_rad))] != kernal[kernal_y_pos][kernal_x_pos] and kernal[kernal_y_pos][kernal_x_pos] != 2:
				return False
			#except:
			#	pass#print "herp"#pos[0]+(kernal_y_pos-kernal_rad), pos[1]+(kernal_x_pos-kernal_rad)

	return True

def is_tree(inmap, map_x_pos, map_y_pos, world_map_width):
	if inmap["ground"][map_x_pos+map_y_pos*world_map_width] == 8050 or inmap["ground"][map_x_pos+map_y_pos*world_map_width] == 8056:
		return True
	return False

def convert(inmap, world_map_width, world_map_height):

	world = {
	"ground":[0]*(world_map_width*world_map_height),
	"dgrass":[0]*(world_map_width*world_map_height),
	"object":[0]*(world_map_width*world_map_height),
	"extra1":[0]*(world_map_width*world_map_height),
	"shadow":[0]*(world_map_width*world_map_height),
	"extra2":[0]*(world_map_width*world_map_height),
	}

	print("Making ground...")

	for map_y_pos in range(world_map_height):
		if map_y_pos % 10 == 0:
			print("%s %% done with map..." % (int(map_y_pos * (100.0/world_map_height))))
		for map_x_pos in range(world_map_width):
			if inmap[map_y_pos][map_x_pos] == 1:
				selected = False
				if map_y_pos == 0 or map_x_pos == 0 or map_y_pos == world_map_height-1 or map_x_pos == world_map_width-1:
					world["ground"][map_x_pos+map_y_pos*world_map_width] = (7664)
				else:
					for kernal in range(len(kernals)):
						if compkernal(inmap, [map_y_pos, map_x_pos], kernals[kernal]):
							selected = True
							world["ground"][map_x_pos+map_y_pos*world_map_width] = (7664+kernal)
					if not selected:
						world["ground"][map_x_pos+map_y_pos*world_map_width] = (7664)
			else:
				if inmap[map_y_pos-1][map_x_pos] == 1:
					world["ground"][map_x_pos+map_y_pos*world_map_width] = (8050)
				elif inmap[map_y_pos-2][map_x_pos] == 1:
					world["ground"][map_x_pos+map_y_pos*world_map_width] = (8056)
				else:
					world["ground"][map_x_pos+map_y_pos*world_map_width] = (1552)

	print("Generating temporary map for dark grass...")
	tempmap = []
	for map_y_pos in range(world_map_height):
		tempmap.append([])
		for map_x_pos in range(world_map_width):
			if inmap[map_y_pos][map_x_pos] == 0 and not is_tree(world, map_x_pos-1, map_y_pos, world_map_width):
				if shadkernal(inmap, [map_y_pos,map_x_pos], emptykernal):
					tempmap[map_y_pos].append(1)
				else:
					tempmap[map_y_pos].append(0)
			else:
				tempmap[map_y_pos].append(0)

	print("Populating dark grass layer...")
	#populates dgrass
	for map_y_pos in range(world_map_height):
		if map_y_pos % 10 == 0:
			print("%s %% done with dark grass..." % (int(map_y_pos * (100.0/world_map_height))))
		for map_x_pos in range(world_map_width):
			if map_y_pos == 0 or map_x_pos == 0 or map_y_pos == world_map_height-1 or map_x_pos == world_map_width-1:
				pass
			else:
				for kernal in range(len(kernals)):
					if compkernal(tempmap, [map_y_pos, map_x_pos], kernals[kernal]):
						world["dgrass"][map_x_pos+map_y_pos*world_map_width]=(3920+kernal)

	print("Adding random things for visual appeal...")
	#adds random stuff on the ground
	for map_y_pos in range(world_map_height):
		for map_x_pos in range(world_map_width):
			plant = random.randrange(plant_density)
			if plant == 0 and inmap[map_y_pos][map_x_pos] == 0 and inmap[map_y_pos-1][map_x_pos] != 1 and inmap[map_y_pos-2][map_x_pos] != 1:
				world["object"][map_x_pos+map_y_pos*world_map_width] = random.choice([88,89,90,91,96,97,98,99,92,100,170,171,178,179])

	print("Adding shadows...")
	#adds shadows
	for map_y_pos in range(world_map_height):
		for map_x_pos in range(world_map_width):
			if shadkernal(inmap, [map_y_pos,map_x_pos], shadowkernals[0]):
				world["shadow"][map_x_pos+map_y_pos*world_map_width] = 5
			if world["ground"][map_x_pos+map_y_pos*world_map_width-1] == 8050 or world["ground"][map_x_pos+map_y_pos*world_map_width-1] == 8056:
				if inmap[map_y_pos][map_x_pos] != 1:
					if world["ground"][map_x_pos+map_y_pos*world_map_width] != 8050 and world["ground"][map_x_pos+map_y_pos*world_map_width] != 8056:
						world["shadow"][map_x_pos+map_y_pos*world_map_width] = 5
	return world

def piecemeal(world, final_map, world_map_width, world_y_map, world_x_map, map_height, map_width):

	offset = (world_x_map * map_width) + (world_map_width * world_y_map * map_height)

	keys = ["ground", "dgrass", "object", "extra1", "shadow", "extra2"]

	pos = 0
	for layer in range(6):
		for map_y_pos in range(final_map["height"]):
			if layer == 0:
				final_map["coordmap"].append([])
			for map_x_pos in range(final_map["width"]):
				final_map["data"][pos] = world[keys[layer]][offset + map_x_pos + world_map_width * map_y_pos]
				if layer == 0:
					final_map["coordmap"][map_y_pos].append(world[keys[layer]][offset + map_x_pos + world_map_width * map_y_pos])
				pos += 1


	return final_map

def add_transfer(cur_level_data, cur_x_pos, cur_y_pos, cur_id, map_width, map_height, target_x_pos, target_y_pos, target_map):
	leveldata["events"].append(copy.deepcopy(Transfer))
	leveldata["events"][-1]["id"] = cur_id
	leveldata["events"][-1]["pages"][0]["list"][0]["parameters"][1] = target_map
	leveldata["events"][-1]["pages"][0]["list"][0]["parameters"][2] = target_x_pos
	leveldata["events"][-1]["pages"][0]["list"][0]["parameters"][3] = target_y_pos

	leveldata["events"][-1]["x"] = cur_x_pos
	leveldata["events"][-1]["y"] = cur_y_pos

	return leveldata


print("Generating noise map...")

noise_map = noise_generation(generate_noise_map(world_width, world_height, range(1, density_range)))
"""noise_map = [[60,60,60,60,60,60,60,60,60,60],
			[60,60,60,60,60,30,60,60,60,60],
			[60,60,60,00,30,00,30,30,00,60],
			[60,60,60,30,60,60,60,60,30,60],
			[60,60,60,30,60,60,60,60,30,60],
			[60,30,30,00,60,00,60,60,00,60],
			[60,30,60,30,60,30,60,60,30,60],
			[60,00,30,00,30,30,30,30,00,60],
			[60,60,60,60,60,00,60,60,60,60],
			[60,60,60,60,60,60,60,60,60,60]
			]"""


print("Generating world map...")

world_map = generate_world_map(map_width, map_height, noise_map, world_width, world_height, padding)

print("Running map through cellular rules, first round...")

iterations = 5
for i in range(iterations):
	print("%s %% done" % str(i * (100/iterations)))
	world_map = wall_generation(final_world_width, final_world_height, world_map, padding, True)

print("Running map through cellular rules, second round...")
iterations = 4
for i in range(iterations):
	print("%s %% done" % str(i * (100/iterations)))
	world_map = wall_generation(final_world_width, final_world_height, world_map, padding, False)

print("Converting map to rpg maker mv format...")

converted_world_map = convert(world_map, final_world_width, final_world_height)


print("Turning map into individual map json files...")

num = 0

System = {"airship":{"bgm":{"name":"Ship3","pan":0,"pitch":100,"volume":90},"characterIndex":3,"characterName":"Vehicle","startMapId":0,"startX":0,"startY":0},"armorTypes":["","General Armor","Magic Armor","Light Armor","Heavy Armor","Small Shield","Large Shield"],"attackMotions":[{"type":0,"weaponImageId":0},{"type":1,"weaponImageId":1},{"type":1,"weaponImageId":2},{"type":1,"weaponImageId":3},{"type":1,"weaponImageId":4},{"type":1,"weaponImageId":5},{"type":1,"weaponImageId":6},{"type":2,"weaponImageId":7},{"type":2,"weaponImageId":8},{"type":2,"weaponImageId":9},{"type":0,"weaponImageId":10},{"type":0,"weaponImageId":11},{"type":0,"weaponImageId":12}],"battleBgm":{"name":"Battle1","pan":0,"pitch":100,"volume":90},"battleback1Name":"Grassland","battleback2Name":"Grassland","battlerHue":0,"battlerName":"Dragon","boat":{"bgm":{"name":"Ship1","pan":0,"pitch":100,"volume":90},"characterIndex":0,"characterName":"Vehicle","startMapId":0,"startX":0,"startY":0},"currencyUnit":"G","defeatMe":{"name":"Defeat1","pan":0,"pitch":100,"volume":90},"editMapId":1,"elements":["","Physical","Fire","Ice","Thunder","Water","Earth","Wind","Light","Darkness"],"equipTypes":["","Weapon","Shield","Head","Body","Accessory"],"gameTitle":"Save Her","gameoverMe":{"name":"Gameover1","pan":0,"pitch":100,"volume":90},"locale":"en_US","magicSkills":[1],"menuCommands":[True,True,True,True,True,True],"optDisplayTp":True,"optDrawTitle":True,"optExtraExp":False,"optFloorDeath":False,"optFollowers":True,"optSideView":False,"optSlipDeath":False,"optTransparent":False,"partyMembers":[1,2,3,4],"ship":{"bgm":{"name":"Ship2","pan":0,"pitch":100,"volume":90},"characterIndex":1,"characterName":"Vehicle","startMapId":0,"startX":0,"startY":0},"skillTypes":["","Magic","Special"],"sounds":[{"name":"Cursor2","pan":0,"pitch":100,"volume":90},{"name":"Decision1","pan":0,"pitch":100,"volume":90},{"name":"Cancel2","pan":0,"pitch":100,"volume":90},{"name":"Buzzer1","pan":0,"pitch":100,"volume":90},{"name":"Equip1","pan":0,"pitch":100,"volume":90},{"name":"Save","pan":0,"pitch":100,"volume":90},{"name":"Load","pan":0,"pitch":100,"volume":90},{"name":"Battle1","pan":0,"pitch":100,"volume":90},{"name":"Run","pan":0,"pitch":100,"volume":90},{"name":"Attack3","pan":0,"pitch":100,"volume":90},{"name":"Damage4","pan":0,"pitch":100,"volume":90},{"name":"Collapse1","pan":0,"pitch":100,"volume":90},{"name":"Collapse2","pan":0,"pitch":100,"volume":90},{"name":"Collapse3","pan":0,"pitch":100,"volume":90},{"name":"Damage5","pan":0,"pitch":100,"volume":90},{"name":"Collapse4","pan":0,"pitch":100,"volume":90},{"name":"Recovery","pan":0,"pitch":100,"volume":90},{"name":"Miss","pan":0,"pitch":100,"volume":90},{"name":"Evasion1","pan":0,"pitch":100,"volume":90},{"name":"Evasion2","pan":0,"pitch":100,"volume":90},{"name":"Reflection","pan":0,"pitch":100,"volume":90},{"name":"Shop1","pan":0,"pitch":100,"volume":90},{"name":"Item3","pan":0,"pitch":100,"volume":90},{"name":"Item3","pan":0,"pitch":100,"volume":90}],"startMapId":1,"startX":8,"startY":6,"switches":["","","","","","","","","","","","","","","","","","","","",""],"terms":{"basic":["Level","Lv","HP","HP","MP","MP","TP","TP","EXP","EXP"],"commands":["Fight","Escape","Attack","Guard","Item","Skill","Equip","Status","Formation","Save","Game End","Options","Weapon","Armor","Key Item","Equip","Optimize","Clear","New Game","Continue",None,"To Title","Cancel",None,"Buy","Sell"],"params":["Max HP","Max MP","Attack","Defense","M.Attack","M.Defense","Agility","Luck","Hit","Evasion"],"messages":{"actionFailure":"There was no effect on %1!","actorDamage":"%1 took %2 damage!","actorDrain":"%1 was drained of %2 %3!","actorGain":"%1 gained %2 %3!","actorLoss":"%1 lost %2 %3!","actorNoDamage":"%1 took no damage!","actorNoHit":"Miss! %1 took no damage!","actorRecovery":"%1 recovered %2 %3!","alwaysDash":"Always Dash","bgmVolume":"BGM Volume","bgsVolume":"BGS Volume","buffAdd":"%1's %2 went up!","buffRemove":"%1's %2 returned to normal!","commandRemember":"Command Remember","counterAttack":"%1 counterattacked!","criticalToActor":"A painful blow!!","criticalToEnemy":"An excellent hit!!","debuffAdd":"%1's %2 went down!","defeat":"%1 was defeated.","emerge":"%1 emerged!","enemyDamage":"%1 took %2 damage!","enemyDrain":"%1 was drained of %2 %3!","enemyGain":"%1 gained %2 %3!","enemyLoss":"%1 lost %2 %3!","enemyNoDamage":"%1 took no damage!","enemyNoHit":"Miss! %1 took no damage!","enemyRecovery":"%1 recovered %2 %3!","escapeFailure":"However, it was unable to escape!","escapeStart":"%1 has started to escape!","evasion":"%1 evaded the attack!","expNext":"To Next %1","expTotal":"Current %1","file":"File","levelUp":"%1 is now %2 %3!","loadMessage":"Load which file?","magicEvasion":"%1 nullified the magic!","magicReflection":"%1 reflected the magic!","meVolume":"ME Volume","obtainExp":"%1 %2 received!","obtainGold":"%1\\G found!","obtainItem":"%1 found!","obtainSkill":"%1 learned!","partyName":"%1's Party","possession":"Possession","preemptive":"%1 got the upper hand!","saveMessage":"Save to which file?","seVolume":"SE Volume","substitute":"%1 protected %2!","surprise":"%1 was surprised!","useItem":"%1 uses %2!","victory":"%1 was victorious!"}},"testBattlers":[{"actorId":1,"equips":[1,1,2,3,0],"level":1},{"actorId":2,"equips":[2,1,2,3,0],"level":1},{"actorId":3,"equips":[3,0,2,3,4],"level":1},{"actorId":4,"equips":[4,0,2,3,4],"level":1}],"testTroopId":4,"title1Name":"Castle","title2Name":"","titleBgm":{"name":"Theme6","pan":0,"pitch":100,"volume":90},"variables":["","","","","","","","","","","","","","","","","","","","",""],"versionId":47172460,"victoryMe":{"name":"Victory1","pan":0,"pitch":100,"volume":90},"weaponTypes":["","Dagger","Sword","Flail","Axe","Whip","Cane","Bow","Crossbow","Gun","Claw","Glove","Spear"],"windowTone":[0,0,0,0]}

System["startMapId"] = (world_width/2) + world_width * (world_height/2)
System["titleBgm"]["name"] = "Theme2"
System["titleBgm"]["pitch"] = 70
System["title1Name"] = "CrossedSwords"
System["title2Name"] = "Medieval"
System["gameTitle"] = "Infinite Dark Forest"


for song in range(len(System["sounds"])):
	System["sounds"][song]["volume"] = 40

leveldata["encounterList"] = []
leveldata["encounterList"].append({"regionSet":[],"troopId":1,"weight":5})
leveldata["encounterList"].append({"regionSet":[],"troopId":2,"weight":5})
leveldata["encounterList"].append({"regionSet":[],"troopId":3,"weight":5})
leveldata["encounterList"].append({"regionSet":[],"troopId":4,"weight":5})

leveldata["bgm"] = {"name":"Field1","pan":0,"pitch":60,"volume":55}
leveldata["autoplayBgm"] = True
leveldata["battleback1Name"] = "Meadow"
leveldata["battleback2Name"] = "Forest"
leveldata["disableDashing"] = True
leveldata["specifyBattleback"] = True


for world_y_map in range(world_height):
	for world_x_map in range(world_width):
		num += 1
		print("Generating map number %s json file template..." % (str(num).zfill(3)))

		name = "MAP%s" % (str(num).zfill(3))
		temp = copy.deepcopy(map_info_template)
		temp["id"] = num
		temp["order"] = num
		temp["name"] = name
		mapinfo.append(temp)
		del(temp)

		leveldata["data"] = [0] * ((map_width+padding*2) * (map_height+padding*2) * 6)
		leveldata["coordmap"] = []
		leveldata["events"] = []
		leveldata["events"].append(None)
		leveldata["events"].append(NightTint )

		#leveldata["events"].append(events.Image)
		#leveldata["events"][-1]["id"] = 2
		#leveldata["events"][-1]["pages"][0]["list"][0]["parameters"][1] = "Menu"

		leveldata = piecemeal(converted_world_map, leveldata, final_world_width, world_y_map, world_x_map, map_height, map_width)

		print("generating transfer points...")

		count = 2

		#first check if current map has a map above it
		#if y != 0

		#transfer to above map
		if world_y_map != 0:
			for map_x_pos in range(padding-2, map_width+padding+1):
				if leveldata["coordmap"][padding-1][map_x_pos] == 1552 and leveldata["coordmap"][padding-2][map_x_pos] == 1552:
					count += 1
					add_transfer(leveldata, map_x_pos, padding-1, count, map_width, map_height, map_x_pos, map_height + padding-1, (world_x_map+1) + (world_y_map-1)*world_width)

		#transfer to below map
		if world_y_map != world_height-1:
			for map_x_pos in range(padding-2, map_width+padding+2):
				if leveldata["coordmap"][map_height+padding][map_x_pos] == 1552 and leveldata["coordmap"][map_height+padding+1][map_x_pos] == 1552:
					count += 1
					add_transfer(leveldata, map_x_pos, map_height+padding, count, map_width, map_height, map_x_pos, padding, (world_x_map+1) + (world_y_map+1)*world_width)

		#transfer to left map
		if world_x_map != 0:
			for map_y_pos in range(padding-2, map_height+padding+2):
				if leveldata["coordmap"][map_y_pos][padding] == 1552 and leveldata["coordmap"][map_y_pos][padding-1] == 1552:
					count += 1
					add_transfer(leveldata, padding, map_y_pos, count, map_width, map_height, map_width+padding, map_y_pos, (world_x_map) + (world_y_map)*world_width)
		
		#transfer to right map
		if world_x_map != world_width-1:
			for map_y_pos in range(padding-2, map_height+padding+2):
				if leveldata["coordmap"][map_y_pos][map_width+padding+1] == 1552 and leveldata["coordmap"][map_y_pos][map_width+padding+2] == 1552:
					count += 1
					add_transfer(leveldata, map_width+padding+1, map_y_pos, count, map_width, map_height, padding+1, map_y_pos, (world_x_map+2) + (world_y_map)*world_width)
		
		print("setting player starting position...")
		if System["startMapId"] == world_x_map + world_y_map * world_width:
			for suby in range(int(map_height/2),map_height):
				if leveldata["coordmap"][suby][int(map_width/2)] == 1552:
					System["startX"] = int(map_width/2)
					System["startY"] = suby
					break


		print("Saving map as json file...")

		open("output/Map%s.json" % (str(num).zfill(3)),"w").write(json.dumps(leveldata))


#System["startX"] = 40
#System["startY"] = 40

open("output/System.json","w").write(json.dumps(System))

print("Saving map info...")

open("output/MapInfos.json","w").write(json.dumps(mapinfo))


print("Map successfully generated! have a nice day :D")

print(time.time() - start)




screen = pygame.display.set_mode((map_width * world_width + padding * 2,map_height * world_height + padding * 2))

for y in range(map_height * world_height + padding * 2):
	for x in range(map_width * world_width + padding * 2):
		if world_map[y][x]:
			screen.set_at((x,y), (0,100,0))
		else:
			screen.set_at((x,y), (0,200,0))

#pygame.display.flip()
pygame.display.update()

#outputs the image to an image file
pygame.image.save(screen, "example.png")










