import random
import copy
import tools

def generate_odds(density):
	return [1] * density + [0] * (200-density)

def generate_noise_map(inmap, width, height, selection_list):
	for y in range(height):
		inmap.append([])
		for x in range(width):
			inmap[y].append(random.choice(selection_list))

def cycle_cell(width, height, inmap, padding, ruleset):
	outmap = []
	for map_y_pos in range(height):
		if map_y_pos % 10 == 0:
			print(" %s %% done with cycle..." % (int(map_y_pos * (100.0/height))))
		outmap.append([])
		for map_x_pos in range(width):
			#if (map_y_pos == 0 or map_y_pos == height-1 or map_x_pos == 0 or map_x_pos == width-1):
			#	outmap[map_y_pos].append(inmap[map_y_pos][map_x_pos])
			#else:
			count = 0
			for y in range(-1,2):
				for x in range(-1, 2):
					if x == 0 and y== 0:
						pass
					else:
						try:
							count += inmap[map_y_pos+y][map_x_pos+x]
						except:
							pass
			wall = (inmap[map_y_pos][map_x_pos] == 1)
			if wall:
				if count >= 4 or count == 0 and ruleset:
					outmap[map_y_pos].append(1)
				elif count >=5 and not ruleset:
					outmap[map_y_pos].append(1)
				else:
					outmap[map_y_pos].append(0)
			else:
				if count >= 5:
					outmap[map_y_pos].append(1)
				else:
					outmap[map_y_pos].append(0)
	return outmap

def doubler(inmap, y, x, pad=1):
	if y:
		new_map = [val for val in inmap for _ in (0,1)]
	else:
		new_map = copy.deepcopy(inmap)

	final_map = []

	if x:
		for line in range(len(new_map)):
			new_line = []
			if line % pad:
				new_line = [val for val in new_map[line] for _ in (0,1)]
			else:
				new_line = [copy.deepcopy(new_map[line][0])]
				t_line = [val for val in new_map[line] for _ in (0,1)][:-1]
				new_line += t_line
			final_map.append(new_line)
	else:
		final_map = new_map

	return final_map


def create_organic_map(width, height, density, rounds, shift, double_width=0, double_height=0, double_pad = 1, path = None):
	cur_map = generate_noise_map(width,height,generate_odds(density))

	if path:
		line = tools.linear_interp(path[0], path[1] )
		print(line)

		for point in line:
			tools.clear_square(cur_map, point, 1)

	for cur_round in range(shift):
		cur_map = cycle_cell(width, height, cur_map, 0, True)

	for cur_round in range(rounds-shift):
		cur_map = cycle_cell(width, height, cur_map, 0, False)

	for h in range(double_height):
		cur_map = doubler(cur_map, True, False)

	for w in range(double_width):
		if w == double_width-1:
			cur_map = doubler(cur_map, False, True, double_pad)
		else:
				cur_map = doubler(cur_map, False, True)

	return cur_map


def shape_blob(width, height, kernal_list, inmap, outmap, seed):
	for y in range(height):
		for x in range(width):
			if inmap[y][x]:
				for kern in range(len(kernal_list)):
					if tools.compkernal(inmap, [y, x], kernal_list[kern]):
						outmap[ y * width + x] = seed + kern


def do_rounds(inmap, width, height, rounds, shift):
	for cur_round in range(shift):
		inmap = cycle_cell(width, height, inmap, 0, True)

	for cur_round in range(rounds-shift):
		inmap = cycle_cell(width, height, inmap, 0, False)

	return inmap