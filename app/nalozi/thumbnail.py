import os,sys,re
from subprocess import Popen, PIPE, STDOUT

def image_size(filename):
	cmd = 'identify ' + filename
	p = Popen(cmd,shell=True,stdin=PIPE,stdout=PIPE,stderr=STDOUT, close_fds=True)
	output = p.stdout.read()
	regex = re.compile(r'([0-9]+)x([0-9]+)')
	
	s = regex.search(output)
	
	if s and len(s.groups()) >= 2:
		width = s.groups()[0]
		height = s.groups()[1]
		return [int(width),int(height)]
	
	return [0,0]

def thumbnail(filename, size='150'):
	# defining path
	size = str(size)
	filehead, filetail = os.path.split(filename)
	basename, format = os.path.splitext(filetail)
	thumbname = basename + '_' + size + format
	
	thumbpath = os.path.join(filehead, thumbname)
    
    # defining the size
    
	try:
		x, y = [int(x) for x in size.split('x')]
	except:
		z = int(size)
		
		image_x, image_y = image_size(filename)
		
		if image_x > image_y:
			x = z
			y = image_y * x / image_x
		else:
			y = z
			x = image_x * y / image_y
    		
	cmd = "convert " + filename + " -resize " + str(x) + "x" + str(y) + " " + thumbpath
    
	try:
		os.system(cmd)
	except:
		return None
	
	return thumbname.strip()
	
	"""# defining the filename and the miniature filename
	
	
	miniature_filename = os.path.join(filehead, miniature)
	if os.path.exists(miniature_filename) and os.path.getmtime(filename)>os.path.getmtime(miniature_filename):
	    os.unlink(miniature_filename)
	# if the image wasn't already resized, resize it
	if not os.path.exists(miniature_filename):
	    image = Image.open(filename)
	    image.thumbnail([x, y], Image.ANTIALIAS)
	    try:
	        image.save(miniature_filename, image.format, quality=90, optimize=1)
	    except:
	        image.save(miniature_filename, image.format, quality=90)
	
	return miniature"""