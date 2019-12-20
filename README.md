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

	$> sudo python server.py 

Make sure that port 80 is available and you run the serve.py as sudo as it is hardcoded to port 80. You can use any other port also.

How to run Client?

GPAC Dash Player is used as client. https://github.com/gpac/gpac

Update gpac/src/media_tools/dash_client.c with the dash_client.c provided in our repository. This file implements dash_do_rate_adaptation_econ() which interacts with server to implement ECON or OBOE_ECON. In addition, we have also implemented dash_do_rate_adaptation_mpc() which implements Model Predictive Control(MPC) algorithm.

To run: 

	$> MP4Client http:// <serverip> : <port> /<video_file>.mpd
  

To run OBOE with ECON make sure that the variables are set to True in the init section of server.py

# Data

Create dash aligned representations of a video for different bitrates using ffmpeg and MP4Box.

Sample DASH Video file can be downloaded at https://drive.google.com/file/d/14qwl9kGKYADPXL5vZJWoXFNRIBuFCZtR/view?usp=sharing

# References

[1] Yi Cao, Javad Nejati, Aruna Balasubramanian, Anshul Gandhi. ECON: Modeling the network to improve application performance. IMC ’19, October 21–23, 2019, Amsterdam, Netherlands.

[2] Zahaib Akhtar, Yun Seong Nam. Oboe: Auto-tuning Video ABR Algorithms to Network Conditions. SIGCOMM ’18, August 20–25, 2018, Budapest, Hungary.
