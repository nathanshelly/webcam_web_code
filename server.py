import tornado.ioloop, tornado.web, json,os, base64, numpy as np
from tornado.log import enable_pretty_logging
from tornado import websocket
from array import array
from datetime import datetime

cam_sockets = []
browser_audio_sockets = []
audio_packet_list = [] # list of numpy arrays of chunk size
camera_packet_list = []
#filename1 = "images/cam_feed1.jpg"
#filename2 = "images/cam_feed2.jpg"
writing_file_1 = True


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
		browser_audio_sockets.append(self)
		print 'audio stream opened'

	def on_message(self, message):
		if message:
			message = json.loads(message)
			print message

	def on_close(self):
		browser_audio_sockets.remove(self)
		print 'audio stream closed'

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
		else:
			print "No image sent"

class source_cam_socket(websocket.WebSocketHandler):
	f = open("images/cam_feed.jpg","wb")
	f.write("")
	f.close()

	#writing_file_1 = True

	def check_origin(self, origin):
		return True

	def open(self):
		print 'camera stream to source opened'
		#f = open("images/cam_feed.jpg","ab")

	def on_message(self, message):
                global writing_file_1
		if message:
                        #print "Image packet received of length ", len(message)
                        print "Image data packet received"
                        if writing_file_1:
				filename = "images/cam_feed1.jpg"
			else:
				filename = "images/cam_feed2.jpg"
			f = open(filename,"ab")
			f.write(message)
			f.close()
                        #print message.encode('hex')
                else:
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

	def on_close(self):
		print 'camera stream to source closed'

class source_audio_socket(websocket.WebSocketHandler):
	def check_origin(self, origin):
		return True

	def open(self):
		print 'audio socket to source opened'
		global audio_packet_list
		audio_packet_list = []

	def on_message(self, message):
		if message:
			global audio_packet_list

			if len(audio_packet_list) == 40:
				print "received termination request"
				print str(datetime.now())
				audio_array = np.concatenate(audio_packet_list)

				to_send = {'type': 'audio-array','array': audio_array.tolist()}
				for socket in browser_audio_sockets:
					socket.write_message(json.dumps(to_send))
					print "sent audio data"
				audio_packet_list = []
			print "packets recieved: ", len(audio_packet_list) 
			audio_packet = ((np.frombuffer(message, dtype=np.uint16)/2.0**15)-1.75)*4 - .62
			audio_packet_list.append(audio_packet)

	def on_close(self):
		print 'audio socket to source closed'

def make_app():
	handlers = [(r"/camera_socket", cam_socket), (r"/audio_socket", aud_socket), (r"/source_audio_socket", source_audio_socket), (r"/source_cam_socket", source_cam_socket), (r"/post_image", post_image)]
	return tornado.web.Application(handlers)

if __name__ == "__main__":
	enable_pretty_logging()
	app = make_app()
	app.listen(8000, address='127.0.0.1')
	tornado.ioloop.IOLoop.current().start()
