import optparse, math, mmap, socket, time
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
parser.add_option('-R', '--replace', dest='replace', type=int, help='Replace only this color')
parser.add_option('-d', '--delay', dest='delay', default=0.1, type=float, help='Delay between pixel places (when sending updates)')
parser.add_option('-n', '--no-update', dest='no_update', action='store_true', help='Don\'t send updates to clients (bypasses delay)')
opts, args = parser.parse_args()

so = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

for y in range(opts.y, opts.y + opts.height):
	for x in range(opts.x, opts.x + opts.width):
		if (opts.replace is None) or bitmap.get_pixel(x, y) == opts.replace:
			bitmap.place_pixel(x, y, opts.fill)
		if not opts.no_update:
			bitmap.send_pixel_update(so, x, y, opts.fill)
			time.sleep(opts.delay)
