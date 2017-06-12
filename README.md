# Webcam Web Code

This repository contains the web code for the webcam project detailed fully in [this repository](https://github.com/nathanshelly/webcam). Please read the introduction there before investigating this code. This code is composed of two parts: a HTML/CSS/JS website that is quite portable, and the server framework that we used to host it.

# Website code

The website which displays the stream is quite simple, and intentionally somewhat minimalist. The javascript on the feed page attempts to open two websockets to the server, one for audio streaming and one for images. When successful, it updates the displayed image whenever it receives a message from the server, and schedules audio to play continuously, as it receives the audio.

# Server code

Once you've got NGINX serving static files as you'd expect (you should be able to view each page of the website, there just won't be any image or audio streaming on the stream page) you're ready to start streaming audio and images. If you're happy to use Python and the Tornado library you shouldn't need to make any changes. If you'd like a different back-end you'll need to replicate the functionality of the server.py file in your language of choice.