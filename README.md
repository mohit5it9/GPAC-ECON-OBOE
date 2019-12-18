## GPAC-ECON-OBOE

# Requirements
- Linux Kernel 4.0
- Python2.7

# Setup
How to run Server?

sudo python server.py

Make sure that port 80 is available and you run the serve.py as sudo as it is hardcoded to port 80. You can use any other port also.

How to run Client?

GPAC Dash Player is used as client. https://github.com/gpac/gpac

To run: MP4Client http:// <serverip> : <port> /<video_file>.mpd
  

To run OBOE with ECON make sure that the variables are set to True in the init section of server.py

# Data

Create dash aligned representations of a video for different bitrates using ffmpeg and MP4Box.

Sample DASH Video file can be downloaded at https://drive.google.com/file/d/14qwl9kGKYADPXL5vZJWoXFNRIBuFCZtR/view?usp=sharing
