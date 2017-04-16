import mmap, json

WIDTH = 500
HEIGHT = 500

BYTES_PER_PIXEL = 0.5
BITS_PER_PIXEL = int(8 * BYTES_PER_PIXEL)

BITMAP_FILE = open('/var/tmp/bitmap', 'r+b')
BITMAP_FILE.seek(0, 2)
BITMAP_SIZE = BITMAP_FILE.tell()
BITMAP_FILE.seek(0, 0)
BITMAP = mmap.mmap(
	BITMAP_FILE.fileno(),
	BITMAP_SIZE,
)

def to_indices(x, y):
	x = min((WIDTH, max((0, x))))
	y = min((HEIGHT, max((0, y))))
	idx = (y * WIDTH + x) * BYTES_PER_PIXEL
	byte_idx = int(idx)
	bit_idx = int((idx - byte_idx) * 8)
	return byte_idx, bit_idx

def place_pixel(x, y, col):
	col &= ((1 << BITS_PER_PIXEL) - 1)
	byte_idx, bit_idx = to_indices(x, y)
	mask = ((1 << BITS_PER_PIXEL) - 1) << bit_idx
	BITMAP[byte_idx] = chr(((0xff ^ mask) & ord(BITMAP[byte_idx])) | (col << bit_idx))
	# TODO: Send change to clients

def get_pixel(x, y):
	byte_idx, bit_idx = to_indices(x, y)
	mask = ((1 << BITS_PER_PIXEL) - 1) << bit_idx
	return (ord(BITMAP[byte_idx]) & mask) >> bit_idx

def send_pixel_update(so, x, y, col):
	so.sendto(json.dumps({
		'ev': 'place',
		'x': x, 'y': y,
		'color': col,
	}), ('localhost', 42960))
