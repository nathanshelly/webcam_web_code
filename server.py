import tornado.ioloop, tornado.web, json, base64
from tornado.log import enable_pretty_logging
from tornado import websocket

cam_sockets = []
class cam_socket(websocket.WebSocketHandler):    
	def check_origin(self, origin):
		return True

	def open(self):
		cam_sockets.append(self)
		print 'camera stream opened'

	def on_message(self, message):
		if message:
			message = json.loads(message)
			print message

	def on_close(self):
		cam_sockets.remove(self)
		print 'camera stream closed'

class aud_socket(websocket.WebSocketHandler):    
	def check_origin(self, origin):
		return True

	def open(self):
		print 'audio stream opened'

	def on_message(self, message):
		if message:
			message = json.loads(message)
			print message

	def on_close(self):
		print 'audio stream closed'

class source_audio_socket(websocket.WebSocketHandler):    
	def check_origin(self, origin):
		return True

	def open(self):
		print 'audio socket to source opened'

	def on_message(self, message):
		if message:
			print message

	def on_close(self):
		print 'audio socket to source closed'

class post_image(tornado.web.RequestHandler):
	def post(self):
		body = self.request.body
		if self.request.headers["message-type"] == "image-bin":
			print 'got image'
			f = open("images/cam_feed.jpg","wb")
			f.write(body)
			f.close()
			for websocket in cam_sockets:
					websocket.write_message('hi')	

		elif self.request.headers["message-type"] == "test":
			print body
		else:
			print "No image sent"

def make_app():
	handlers = [(r"/camera_socket", cam_socket), (r"/audio_socket", aud_socket), (r"/source_audio_socket", source_audio_socket), (r"/post_image", post_image)]
	return tornado.web.Application(handlers)

if __name__ == "__main__":
	enable_pretty_logging()
	app = make_app()
	app.listen(8000, address='127.0.0.1')
	tornado.ioloop.IOLoop.current().start()
