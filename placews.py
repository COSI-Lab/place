from gevent import monkey
monkey.patch_all()

import gevent
from geventwebsocket import WebSocketServer, WebSocketApplication, Resource

import socket, json, traceback
import bitmap

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

	def on_message(self, msg):
		try:
			msg = json.loads(msg)
			if msg['act'] == 'place':
				bitmap.place_pixel(msg['x'], msg['y'], msg['color'])
				so.sendto(json.dumps({
					'ev': 'place', 'x': msg['x'], 'y': msg['y'], 'color': msg['color']
				}), ('localhost', 42960))
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
