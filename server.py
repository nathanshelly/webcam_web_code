import tornado.ioloop, tornado.web, json,os, base64, numpy as np
from tornado.log import enable_pretty_logging
from tornado import websocket
from array import array
from datetime import datetime

cam_sockets = []
audio_packet_list = [] # list of numpy arrays of chunk size
browser_audio_sockets = []
writing_file_1 = True
image_base_64 = ""
packet_size = 200
num_packets_adaptive = 80*5

# initial buffer filled with representative data
adaptive_buffer = np.random.randn(num_packets_adaptive*packet_size)*3203.0 + 62473

class cam_socket(websocket.WebSocketHandler): 
	def check_origin(self, origin):
		return True

	def open(self):
		cam_sockets.append(self)
		print 'camera stream opened'

	def on_message(self, message):
		if message:
			print json.loads(message)

	def on_close(self):
		cam_sockets.remove(self)
		print 'camera stream closed'

class aud_socket(websocket.WebSocketHandler):
	def check_origin(self, origin):
		return True

	def open(self):
		browser_audio_sockets.append(self)
		print 'audio stream opened'

	def on_message(self, message):
		if message:
			message = json.loads(message)
			print message

	def on_close(self):
		browser_audio_sockets.remove(self)
		print 'audio stream closed'

class source_socket(websocket.WebSocketHandler):
	def check_origin(self, origin):
		return True

	def open(self):
		print 'audio socket to source opened'
		global audio_packet_list
		audio_packet_list = []

	def on_message(self, message):
		global audio_packet_list, writing_file_1, image_base_64, adaptive_buffer
		if message:
			if len(message) == 400: # it's an audio packet
				print "audio packet received"

				if len(audio_packet_list) == 25:
					print 'received audio termination request', datetime.now()

					audio_array = np.concatenate(audio_packet_list)
					audio_packet_list = []

					to_send = {'type': 'audio-array','array': audio_array.tolist()}
					for socket in browser_audio_sockets:
						socket.write_message(json.dumps(to_send))


				print "packets received: ", len(audio_packet_list)
				audio_packet_raw = np.frombuffer(message, dtype=np.uint16)
				adaptive_buffer = np.roll(adaptive_buffer, 200)
				adaptive_buffer[0:200] = audio_packet_raw

				adaptive_mean = np.mean(adaptive_buffer)
				adaptive_std = np.std(adaptive_buffer)

				audio_packet = (audio_packet_raw - adaptive_mean)/(10.0*adaptive_std)
				audio_packet = np.clip(audio_packet, -1, 1)
				audio_packet_list.append(audio_packet)

			else: 
				# it's an image packet - the audio ones are always exactly 200 long
				if message == "image done":
					print "Full image received"
					if writing_file_1:
						filename = "images/cam_feed1.jpg"
						writing_file_1 = False
						f = open("images/cam_feed2.jpg", "w")
						f.write("")
						f.close()
					else:
						filename = "images/cam_feed2.jpg"
						writing_file_1 = True
						f = open("images/cam_feed1.jpg", "w")
						f.write("")
						f.close()
					print "File size", os.stat(filename).st_size
					for websocket in cam_sockets:
						websocket.write_message(filename)
					
					image_base_64 = ""
				else:
					print "Image packet received"
					image_base_64 += base64.b64encode(message)
					if writing_file_1:
						filename = "images/cam_feed1.jpg"
					else:
						filename = "images/cam_feed2.jpg"
					f = open(filename,"ab")
					f.write(message)
					f.close()

	def on_close(self):
		print 'audio socket to source closed'

def make_app():
	handlers = [(r"/camera_socket", cam_socket), (r"/audio_socket", aud_socket), (r"/source_socket", source_socket)]
	return tornado.web.Application(handlers)

if __name__ == "__main__":
	enable_pretty_logging()
	app = make_app()
	app.listen(8000, address='127.0.0.1')
	tornado.ioloop.IOLoop.current().start()
