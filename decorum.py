import tools
import kernals

def add_trees(width, height, inmap):
	for y in range(height):
		for x in range(width):
			match = (x%2 == y%2)

			if (y == height-1):
				if inmap[y][x] :
					if match:
						inmap[y][x] = 121
					else:
						inmap[y][x] = 120
				else:
					pass

			else:
				if inmap[y][x] and inmap[y+1][x]:
					if match:
						inmap[y][x] = 115
					else:
						inmap[y][x] = 114
				elif not inmap[y][x] and inmap[y+1][x]:
					if match:
						inmap[y][x] = 112
					else:
						inmap[y][x] = 113
				elif inmap[y][x] and not inmap[y+1][x]:
					if match:
						inmap[y][x] = 121
					else:
						inmap[y][x] = 120
				else:
					pass

def pop_dark_grass(inmap, t_map):
	height = len(inmap)
	width = len(inmap[0])

	for y in range(height):
		t_map.append([])
		for x in range(width):
			if tools.compkernal(inmap, [y, x], kernals.emptykernal):
				t_map[-1].append(1)#dgrass[(y * width) + x ] = 1 #3008
			else:
				t_map[-1].append(0)

def kern_dark_grass(inmap, dgrass):
	height = len(inmap)
	width = len(inmap[0])
	for y in range(height ):
		for x in range(width):
			if inmap[y][x]:
				for kern in range(len(kernals.kernals)):
					if tools.compkernal(inmap, [y, x], kernals.kernals[kern]):
						dgrass[y][x] = 3008 + kern













