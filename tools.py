

def clear_square(inmap, pos, radius, dest):
	for y in range(-radius, radius+1):
		for x in range(-radius, radius+1):
			try:
				inmap[pos[1]+y][pos[0]+x] = dest
			except:
				pass
	#return inmap

def linear_interp(begin, end):
	total_steps = end[0]-begin[0]

	init_x = begin[0]
	init_y = begin[1]

	end_x = end[0]
	end_y = end[1]

	diff_x = end_x - init_x
	diff_y = end_y - init_y

	step_x = diff_x / total_steps
	step_y = diff_y / total_steps


	final_steps = []

	for x in range((total_steps)):
		final_steps.append( [int(init_x + (step_x * x)), int(init_y + (step_y * x))])

	return final_steps

def compkernal(inmap, pos, kernal):
	radius = int(len(kernal)/2)
	width = len(inmap[0]) -1
	height = len(inmap) -1
	for y in range(-radius, radius+1):
		for x in range(-radius, radius+1):
			check_x = x + pos[1]
			check_y = y + pos[0]

			if check_x < 0 or check_x > width or check_y < 0 or check_y > height:
				pass
			else:
				try:
					val1 = inmap[check_y][check_x]
					val2 = kernal[y+radius][x+radius]
					if val1 != val2 and val2 != 2:
						return False
				except:
					print(check_y, check_x, x, y, pos, radius, kernal)
					exit()
	return True


def shape_blob(width, height, kernal_list, inmap, outmap, seed):
	for y in range(height):
		for x in range(width):
			if inmap[y][x]:
				for kern in range(len(kernal_list)):
					if compkernal(inmap, [y, x], kernal_list[kern]):
						outmap[ y][x] = seed + kern

def mask_overlay(width, height, inmap, outmap):
	for y in range(height):
		for x in range(width):
			if inmap[y][x] :
				outmap[y][x] = 0

def merge_maps(lower, upper):
	for y in range(len(lower)):
		for x in range(len(lower[0])):
			if upper[y][x]:
				lower[y][x] = upper[y][x]
