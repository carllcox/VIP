from PIL import Image, ImageFilter
import sys

def origin(file_name):
	img = Image.open(file_name)
	save_loc = 'modified/'
	img.convert('RGB').save(save_loc + file_name)

def crop(file_name, quad):
	img = Image.open(file_name)
	width, height = img.size
	x1 = y1 = 0
	x2 = width/2
	y2 = height/2
	if quad % 2 == 0:
		x1 = width/2
		x2 = width
	if quad > 2:
		y1 = height/2
		y2 = height
	area = (x1, y1, x2, y2)
	cropped_img = img.crop(area)
	save_loc = 'modified/'
	cropped_img.convert('RGB').save(save_loc + file_name)

def blur(file_name, quads, b):
	img = Image.open(file_name)
	width, height = img.size
	for quad in quads:
		x1 = y1 = 0
		x2 = width/2
		y2 = height/2
		if quad % 2 == 0:
			x1 = width/2
			x2 = width
		if quad > 2:
			y1 = height/2
			y2 = height
		coords = (x1, y1, x2, y2)
		cropped_img = img.crop(coords)
		blurred_img = cropped_img.filter(ImageFilter.GaussianBlur(radius=b))
		img.paste(blurred_img, coords)
		save_loc = 'modified/'
		img.convert('RGB').save(save_loc + file_name)

if __name__ == "__main__":
	file_name = sys.argv[1]
	request = sys.argv[2]
	if request == "original":
		origin(file_name)
	elif request == "show":
		quadrants = sys.argv[3]
		crop(file_name, int(quadrants))
	elif request == "blur":
		quadrants = sys.argv[3].split(",")
		blur_intensity = sys.argv[4]
		quadrants = [int(x) for x in quadrants]
		blur(file_name, quadrants, int(blur_intensity))
