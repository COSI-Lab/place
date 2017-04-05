import optparse, math

parser = optparse.OptionParser()
parser.add_option('-W', '--width', dest='width', type=int, help='Width of the canvas.')
parser.add_option('-H', '--height', dest='height', type=int, help='Height of the canvas.')
parser.add_option('-b', '--bpp', dest='bpp', default=0.5, type=float, help='Bytes per pixel.')
parser.add_option('-F', '--fill', dest='fill', default=0, type=int, help='Fill with this pixel.')
opts, args = parser.parse_args()

open('/var/www/place/bitmap', 'wb').write(chr(17 * opts.fill) * int(math.ceil(opts.width * opts.height * opts.bpp)))
