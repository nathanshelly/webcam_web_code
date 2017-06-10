// Variables
var cam_socket; // camera socket instance
var aud_socket; // audio socket instance
var logs = [];
var logsLimit = 4;
var b = document.getElementById('btnWS');
var img = document.getElementById('pic');
var start_time = 0;
var audio_context = new AudioContext();

// Initialize sockets
function initSockets() {
    var host_url = window.location.hostname;
    if (cam_socket)
        cam_socket.close(); // close the websocket if open.
    if (aud_socket)
        aud_socket.close(); // close the websocket if open.

    cam_socket = new WebSocket('wss://' + host_url + '/camera_socket');
    aud_socket = new WebSocket('wss://' + host_url + '/audio_socket');

    cam_socket.onopen = function () {
				logAndUpdateButton('Sockets open to ' + host_url, 'Stop webcam', 'Click to stop webcam', false);
    };

    cam_socket.onclose = function () {
				logAndUpdateButton('Sockets to ' + host_url + ' closed', 'Start webcam', 'Click to start webcam', false);
        img.src = 'images/white_on_black.png';
    };

    cam_socket.onmessage = function (message) {
				displayImage(message.data);
    };

	cam_socket.onerror = function () {
		cam_socket.close();
		logAndUpdateButton('Websocket error', 'Start webcam', 'Click to start webcam', false);
	};

	aud_socket.onopen = function () { 
		console.log('Audio socket open');
	};

	aud_socket.onclose = function () { 
		console.log('Audio socket closed');
	};

	aud_socket.onmessage = function (message) {
		if (message) {
			var data_json = JSON.parse(message.data);
			
			if(data_json['type'] == 'audio-array') {
			    var audio_array = data_json['array'];
			    let audio_buffer = audio_context.createBuffer(1, audio_array.length, 16000);
			    audio_buffer.getChannelData(0).set(audio_array);

			    let source = audio_context.createBufferSource();
			    source.buffer = audio_buffer;
			    source.start();
			    source.connect(audio_context.destination);
			    audio_array = [];
			}
			else
			    console.log('unknown message type');
		}
	};

	aud_socket.onerror = function () {
		aud_socket.close();
		console.log('Audio socket error');
	};
}

function logAndUpdateButton(new_log_msg, new_btn_txt, new_btn_title, btn_status) {
		log(new_log_msg);
		b.innerHTML = new_btn_txt;
		b.title = new_btn_title;
		b.disabled = btn_status;
}

function displayImage(filename) {
    //*** Set the source of the image to the image on the WiFi chip ***//
    img.src = filename + '?dummy=' + (new Date()).getTime();
}

// Set up event listeners
// When the button is clicked, disable it.
b.onclick = function () {
	b.disabled = true;
	if(cam_socket.readyState === cam_socket.OPEN 
		 && cam_socket.readyState === cam_socket.OPEN) {
		cam_socket.close();
		aud_socket.close();
	}
	else
		initSockets();
}

// Other functions
function log(txt) {
    logs.push({
        'content': txt,
        'type': 'log'
		});
    showLog(logs, 'log', logsLimit);
}

function showLog(logArray, logId, logLimit) {
    var logContent = '';
    var logLength = logArray.length;
    var iStart = logLength - logLimit - 1;
    if (iStart < 0)
        iStart = 0;
    for (var index = iStart; index < logLength; ++index) {
        logItem = logArray[index];
        logContent += '<span class="' + logItem.type + '">' + logItem.content + '</span><br/>\n'
    }
    document.getElementById(logId).innerHTML = logContent;
}

// Define initialization function
function init() {
    initSockets();
    adjust_image_width('#pic');
    img.style.width = '95%';
    img.style.height = 'auto';
}

// Open Websocket as soon as page loads
window.onload = init;
window.addEventListener('resize', adjust_image_width('#pic'));
