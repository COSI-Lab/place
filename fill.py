import optparse, math, mmap
import bitmap

parser = optparse.OptionParser(conflict_handler='resolve')
parser.add_option('-x', dest='x', type=int, help='Starting X coordinate.')
parser.add_option('-y', dest='y', type=int, help='Starting Y coordinate.')
parser.add_option('-w', '--width', dest='width', type=int, help='Width of the fill area.')
parser.add_option('-h', '--height', dest='height', type=int, help='Height of the fill area.')
parser.add_option('-W', '--WIDTH', dest='WIDTH', type=int, help='Width of the canvas.')
parser.add_option('-H', '--HEIGHT', dest='HEIGHT', type=int, help='Height of the canvas.')
parser.add_option('-b', '--bpp', dest='bpp', type=float, default=0.5, help='Bytes per pixel.')
parser.add_option('-F', '--fill', dest='fill', default=0, type=int, help='Fill with this pixel.')
opts, args = parser.parse_args()

f = open('bitmap', 'r+b')
f.seek(0, 2)
m = mmap.mmap(f.fileno(), f.tell())

for y in range(opts.y, opts.y + opts.height):
	for x in range(opts.x, opts.x + opts.width):
		bitmap.place_pixel(x, y, opts.fill)
