from gevent import monkey
monkey.patch_all()

import gevent
from geventwebsocket import WebSocketServer, WebSocketApplication, Resource, WebSocketError

import socket, json, traceback
import bitmap

sockets = set()

so = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
so.bind(('localhost', 42960))

def broadcast_thread():
	while True:
		msg, addr = so.recvfrom(4096)
		print('From master:', msg)
		torem = set()
		for sock in sockets:
			try:
				sock.send(msg)
			except WebSocketError:
				torem.add(socK)
			except Exception:
				traceback.print_exc()

		for sock in torem:
			sockets.discard(sock)

class DistApplication(WebSocketApplication):
	def on_open(self):
		print 'Connection from', self.ws
		sockets.add(self.ws)

	def on_message(self, msg):
		print 'From', self.ws, ':', repr(msg)
		if msg is None:
			return
		try:
			msg = json.loads(msg)
			if msg['act'] == 'place':
				bitmap.place_pixel(msg['x'], msg['y'], msg['color'])
				bitmap.send_pixel_update(so, msg['x'], msg['y'], msg['color'])
			else:
				raise ValueError('unknown action')
		except Exception:
			err = traceback.format_exc()
			try:
				self.ws.send(json.dumps({
					'error': err,
				}))
			except Exception:
				print('Double exception while servicing original exception:')
				print(err)
				print('While handling this exception, another exception occured:')
				traceback.print_exc()

	def on_close(self, reason):
		print 'Disconnection from', self.ws, ':', reason
		sockets.discard(self.ws)

gevent.spawn(broadcast_thread)

WebSocketServer(('', 8081), Resource({'/ws': DistApplication})).serve_forever()
