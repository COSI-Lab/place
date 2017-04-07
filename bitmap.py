import mmap

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

def place_pixel(x, y, col):
	col &= ((1 << BITS_PER_PIXEL) - 1)
	x = min((WIDTH, max((0, x))))
	y = min((HEIGHT, max((0, y))))
	idx = (y * WIDTH + x) * BYTES_PER_PIXEL
	byte_idx = int(idx)
	bit_idx = int((idx - byte_idx) * 8)
	mask = ((1 << BITS_PER_PIXEL) - 1) << bit_idx
	BITMAP[byte_idx] = chr(((0xff ^ mask) & ord(BITMAP[byte_idx])) | (col << bit_idx))
	# TODO: Send change to clients
