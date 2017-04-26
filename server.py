import tornado.ioloop, tornado.web, json, base64, numpy as np
from tornado.log import enable_pretty_logging
from tornado import websocket
from array import array

cam_sockets = []
browser_audio_sockets = []
audio_packet_list = [] # list of numpy arrays of chunk size

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
		browser_audio_sockets.append(self)
		a = np.fromfile('temp.bin', dtype=np.int16)[:800]
		a = np.concatenate((a,a,a,a,a,a))
		a = np.concatenate((a,a,a,a,a,a))
		print len(a)
		to_send = {'type':'audio-array', 'array': a.tolist()}
		self.write_message(json.dumps(to_send))
		print "Sent audio data"

	def on_message(self, message):
		if message:
			message = json.loads(message)
			print message

	def on_close(self):
		browser_audio_sockets.remove(self)
		print 'audio stream closed'

class source_audio_socket(websocket.WebSocketHandler):    
	def check_origin(self, origin):
		return True

	def open(self):
		print 'audio socket to source opened'

	def on_message(self, message):
		print 'message testing'
		print message
		if message:
			print 'Message received:'
			print message
			print 'Message length: ', len(message)
			audio_array = np.frombuffer(message, dtype=np.int16)
			# f = open("temp.bin","wb")
			# f.write(message)
			# f.close()
			#audio_array = np.fromfile("temp.bin", dtype=uint16, count=10)
			#print audio_array
			#hex_list = [ord(elem) for elem in message]
			#audio_chunk = array('h', hex_list)
			#print audio_chunk
			#for character in message:
			#	audio_buffer.append(int(character))
			#print 'Current audio buffer: '
			#print audio_buffer

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
		elif self.request.headers["message-type"] == "audio-term":
			print "Received Termination Request"
			global audio_packet_list
			audio_array = np.concatenate(audio_packet_list)
			to_send = {'type':'audio-array','array':audio_array.tolist()}
			f = open("temp.bin","wb")
			f.write(audio_array)
			f.close()
			print browser_audio_sockets
			for socket in browser_audio_sockets:
				socket.write_message(json.dumps(to_send))
				print "Sent audio data"
			audio_packet_list = []
		elif self.request.headers["message-type"] == "audio-bin":
			print 'got audio'
			#f = open("temp.bin","wb")
			#f.write(body)
			#f.close()
			#print 'File written'
			#audio_array = np.fromfile("temp.bin", dtype=np.int16)
			#print "Audio array from file"
			#print audio_array
			global audio_packet_list
			print "Packets recieved: ", len(audio_packet_list)
			#print audio_packet_list
			audio_packet = np.frombuffer(body, dtype=np.int16)
			audio_packet_list.append(audio_packet)
			print "Good Audio from post"
			#print audio_array
			#barr = bytearray(body)
			#print "file written"
		elif self.request.headers["message-type"] == "test":
			print body
		else:
			print "No image sent"

def make_app():
	handlers = [(r"/camera_socket", cam_socket), (r"/audio_socket", aud_socket), (r"/source_audio_socket", source_audio_socket), (r"/post_image", post_image)]
	return tornado.web.Application(handlers)

if __name__ == "__main__":
	#global audio_packet_list
	enable_pretty_logging()
	app = make_app()
	app.listen(8000, address='127.0.0.1')
	tornado.ioloop.IOLoop.current().start()
