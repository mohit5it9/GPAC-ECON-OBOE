## GPAC-ECON-OBOE

# Requirements
- Linux Kernel 4.0
- Python2.7
- GPAC version 0.8.0

# Setup
How to setup Bayesian change point detection?

The code for this detector is on
github (https://github.com/hildensia/bayesian_changepoint_detection). We are including
here as well. To install the package do the following steps:

	$> cd bayesian_changepoint_detection-master
	$> python setup.py install 

How to run Server?

	$> python setup.py install
	$> sudo python server.py 

Make sure that port 80 is available and you run the server.py as sudo as it is hardcoded to port 80. You can use any other port also.

How to run Client?

GPAC Dash Player is used as client. https://github.com/gpac/gpac

Update gpac/src/media_tools/dash_client.c with the dash_client.c provided in our repository. This file implements dash_do_rate_adaptation_econ() which interacts with server to implement ECON or OBOE_ECON. In addition, we have also implemented dash_do_rate_adaptation_mpc() which implements Model Predictive Control(MPC) algorithm.

To run: 

	$> MP4Client http:// <serverip> : <port> /<video_file>.mpd
  

To run OBOE with ECON make sure that the variables are set to True in the init section of server.py

# Data

Create dash aligned representations of a video for different bitrates using ffmpeg and MP4Box.

Following are sample commands that can be used to segment a video into different representation such that it is dash aligned:

	$> ffmpeg -y -i inputfile -ac 2 -ab 128k -c:v libx264 -x264opts 'keyint=24:min-keyint=24:no-scenecut' -b:v 800k maxrate 800k bufsize 500k -vf "scale=-1:540" outputfile540
	$> MP4Box -dash 2000 -rap -frag-rap -profile Live -out output.mpd outputfile180.mp4 outputfile360.mp4 outputfile540.mp4 outputfile7200.mp4 outputfile1080.mp4
	

Sample DASH Video file can be downloaded at https://drive.google.com/file/d/14qwl9kGKYADPXL5vZJWoXFNRIBuFCZtR/view?usp=sharing. This video file must be stored in static/ directory. **UPDATE**: we have uploaded this file on github inside static folder, so no need to download from drive

# Config map generation in offline mode

You can create a config map by running the ECON algorith for various congestion window traces (also synthetic traces too). One such sample config map file is present in *static/IMC19ECON/pythonScripts/configmap_econ_oboe.py*

# References

[1] Yi Cao, Javad Nejati, Aruna Balasubramanian, Anshul Gandhi. ECON: Modeling the network to improve application performance. IMC ’19, October 21–23, 2019, Amsterdam, Netherlands.

[2] Zahaib Akhtar, Yun Seong Nam. Oboe: Auto-tuning Video ABR Algorithms to Network Conditions. SIGCOMM ’18, August 20–25, 2018, Budapest, Hungary.
