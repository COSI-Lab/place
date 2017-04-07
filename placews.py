from gevent import monkey
monkey.patch_all()

import gevent
from geventwebsocket import WebSocketServer, WebSocketApplication, Resource

import socket, json, traceback, hashlib, os, time, binascii
import bitmap

HASH_NAME = 'SHA-256'
HASH_FUNC = hashlib.sha256
DIGEST_SIZE = 256
NONCE_SIZE = 256
MIN_BITS = 512
HARDNESS = 24

REQ_NONCE_TM = 10
REQ_PLACE_TM = 10
DESIRED_PLACE_TM = 30

sockets = set()

so = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
so.bind(('localhost', 42960))

def broadcast_thread():
	while True:
		msg, addr = so.recvfrom(4096)
		print('From master:', msg)
		for sock in sockets:
			try:
				sock.send(msg)
			except Exception:
				traceback.print_exc()

class DistApplication(WebSocketApplication):
	def on_open(self):
		print 'Connection from', self.ws
		sockets.add(self.ws)
		self.hardness = HARDNESS
		self.min_bits = MIN_BITS
		self.nonce = None
		self.last_nonce_time = 0
		self.last_place_time = 0

	def check_nonce(self, resp):
		global HARDNESS

		if self.nonce is None:
			return False
		if len(resp) * 8 < self.min_bits:
			return False
		if not resp.startswith(self.nonce):
			return False
		digest = int(HASH_FUNC(resp).hexdigest(), 16)
		if digest >> (DIGEST_SIZE - self.hardness) != 0:
			return False

		self.nonce = None
		if time.time() < self.last_nonce_time + DESIRED_PLACE_TM:
			self.hardness += 1
			HARDNESS += 1
			print 'Global hardness increased to', HARDNESS
		return True

	def on_message(self, msg):
		try:
			msg = json.loads(msg)
			if msg['act'] == 'place':
				if time.time() < self.last_place_time + REQ_PLACE_TM:
					raise ValueError('Place request sent too soon')
				self.last_place_time = time.time()
				if 'resp' not in msg:
					raise ValueError('No challenge response')
				if not self.check_nonce(msg['resp'].decode('base64')):
					raise ValueError('Bad challenge response')
				bitmap.place_pixel(msg['x'], msg['y'], msg['color'])
				so.sendto(json.dumps({
					'ev': 'place', 'x': msg['x'], 'y': msg['y'], 'color': msg['color']
				}), ('localhost', 42960))
			elif msg['act'] == 'nonce':
				if time.time() < self.last_nonce_time + REQ_NONCE_TM:
					raise ValueError('Nonce request sent too soon')
				self.last_nonce_time = time.time()
				self.nonce = os.urandom(NONCE_SIZE / 8)
				self.ws.send(json.dumps({
					'ev': 'nonce',
					'hash': HASH_NAME,
					'nonce': self.nonce.encode('base64'),
					'hardness': self.hardness,
					'len': self.min_bits,	
				}))
			else:
				raise ValueError('unknown action')
		except Exception:
			self.ws.send(json.dumps({
				'error': traceback.format_exc(),
			}))

	def on_close(self):
		print 'Disconnection from', self.ws
		sockets.discard(self.ws)

gevent.spawn(broadcast_thread)

WebSocketServer(('', 8081), Resource({'/ws': DistApplication})).serve_forever()
