import tornado.ioloop, tornado.web, json
from tornado.log import enable_pretty_logging
from tornado import websocket

class socket(websocket.WebSocketHandler):    
	def check_origin(self, origin):
		return True

	def open(self):
		print 'websocket opened'

	def on_message(self, message):
		if message:
			message = utilities.convert(json.loads(message))
			print message

	def on_close(self):
		print 'websocket closed'

class post_test(tornado.web.RequestHandler):
	def post(self):
		print 'hi'
		print self.get_body_argument("message")

def make_app():
	handlers = [(r"/ws", socket), (r"/post_test", post_test)]
	return tornado.web.Application(handlers)

if __name__ == "__main__":
	enable_pretty_logging()
	app = make_app()
	# app.listen(443, ssl_options={"certfile": "map.crt", "keyfile": "map.key", })
	app.listen(8000, address='127.0.0.1')
	tornado.ioloop.IOLoop.current().start()
