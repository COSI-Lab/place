from flask import Flask, request, g, render_template, make_response
from flask.json import jsonify
from flask_sockets import Sockets
import mmap, math, json, sys, socket, struct

WIDTH = 500
HEIGHT = 500
BYTES_PER_PIXEL = 0.5
BITS_PER_PIXEL = int(8 * BYTES_PER_PIXEL)

def aton(h):
	return struct.unpack('>I', socket.inet_aton(h))[0]

def ntoa(i):
	return socket.inet_ntoa(struct.pack('>I', i))

ALLOWED_SUBNET = aton('0.0.0.0')
ALLOWED_MASK = aton('0.0.0.0')

def check_priv():
	host = aton(request.environ['REMOTE_ADDR'])
	if request.method == 'POST' and ALLOWED_SUBNET != (ALLOWED_MASK & host):
		resp = make_response('Modification not permitted.')
		resp.status_code = 403
		return resp

BITMAP_FILE = open('/var/www/place/bitmap', 'r+b')
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

app = Flask('place')

so = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
so.connect(('localhost', 42960))

@app.route('/bitmap')
def view_bitmap():
	response = make_response(BITMAP[:])
	response.headers['Content-type'] = 'application/octet-stream'
	return response

@app.route('/bitmap/width')
def view_width():
	response = make_response(str(WIDTH))
	response.headers['Content-type'] = 'text/plain'
	return response

@app.route('/bitmap/height')
def view_height():
	response = make_response(str(HEIGHT))
	response.headers['Content-type'] = 'text/plain'
	return response

@app.route('/api/place', methods=['GET', 'POST'])
def view_place():
	try:
		resp = check_priv()
		if resp is not None:
			return resp
		if request.headers['Content-type'] == 'application/json':
			req = json.loads(request.data)
			try:
				place_pixel(req['x'], req['y'], req['color'])
			except Exception:
				import traceback
				response = make_response(traceback.format_exc())
				response.status_code = 500
			else:
				response = make_response(render_template('api_place.txt', **req))
				so.send(json.dumps({'ev': 'place', 'x': req['x'], 'y': req['y'], 'color': req['color']}))
			response.headers['Content-type'] = 'text/plain'
			return response
		else:
			return 'bad content type'
	except Exception:
		import traceback
		return traceback.format_exc()

@app.route('/')
def view_root():
	return render_template('root.html')
