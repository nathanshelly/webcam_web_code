// Variables
var ws; // websocket instance
var logs = [];
var logsLimit = 4;
var b = document.getElementById('btnWS');
var img = document.getElementById('pic');

// Initialize the WebSocket
function initWebSocket() {
    var ipName = window.location.hostname;
    if (ws) {
        ws.close(); // close the websocket if open.
        ws = undefined;
    }
    ws = new WebSocket('wss://' + ipName + '/ws');

    ws.onopen = function () { // when handshake is complete:
        log('WebSocket open to ' + ipName);
        //*** Change the text of the button to read "Stop Webcam" ***//
        b.innerHTML = "Stop Webcam";
        
        //*** Change the title attribute of the button to display "Click to stop webcam" ***//
        b.title = "Click to stop webcam";
        
        //*** Enable the button" ***//
        b.disabled = false;
        
        // Display the image!
        displayImage();
    };

    ws.onclose = function () { // when socket is closed:
        log('WebSocket connection to ' + ipName + ' has been closed!');
        //*** Change the text of the button to read "Start Webcam" ***//
        b.innerHTML = "Start Webcam";
        
        //*** Change the title attribute of the button to display "Click to start webcam" ***//
        b.title = "Click to start webcam";
        
        //*** Enable the button" ***//
        b.disabled = false;
        
        img.src = 'images/big_brother_placeholder.png';
        
        document.getElementById('timestamp').innerHTML = 'No current image';
    };

    ws.onmessage = function (event) { // when client receives a WebSocket message:
        //*** Display a new timestamp ***//
        document.getElementById('timestamp').innerHTML = Date();

				console.log(event);
        
        // Display the image!
        displayImage();
    };
	
	ws.onerror = function () { // when an error occurs
		ws.close();
		log('Websocket error');
        //*** Change the text of the button to read "Start Webcam" ***//
        b.innerHTML = "Start Webcam";
		
        //*** Change the title attribute of the button to display "Click to start webcam" ***//
		b.title = "Click to start webcam";
        
        //*** Enable the button" ***//
        b.disabled = false;
	};
}

function displayImage() {
    //*** Set the source of the image to the image on the WiFi chip ***//
	var d = new Date();	
	img.src = 'images/cam_feed.jpg' + '?dummy=' + d.getTime();
}

// Set up event listeners
//*** When the button is clicked, disable it, and depending on whether a Websocket is open or not, either run "initWebSocket()" or "ws.close()" ***//
b.onclick = function () {
    b.disabled = true;
    ws.readyState === ws.OPEN ? ws.close() : initWebSocket();    
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
    initWebSocket();
    adjust_image_width('#pic');
    img.style.width = '95%';
    img.style.height = 'auto';
}

// Open Websocket as soon as page loads
window.onload = init;
window.addEventListener('resize', adjust_image_width('#pic'));
