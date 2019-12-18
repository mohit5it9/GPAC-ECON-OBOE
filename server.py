'''
This is the server side code that serves
the Dash File and video segment chunks for
the Dash video file. Runs with python2
Not tested with python3
'''

import SimpleHTTPServer
import SocketServer

from econ_helper import *
from video_data import *

OBOE = False # Chanhe this to True if we need to run OBOE+ECON
ECON = True # Change this to False if you're running BOLA, BBA. But do not change this value for now


class MyRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        customUrl = self.path.split("_dash")
        if len(customUrl) > 1 and ECON == True:
            # get the next bitrate to serve as determined by ECON
            econ_bitrate = get_econ_bitrate(OBOE)
            print ("econ_bitrate is", econ_bitrate)
            self.path = "/output" + econ_bitrate + "_dash" + customUrl[1]

            # Writing to file to determine number of switches, representation
            global quality_to_bitrate, quality_to_rep
            f = open("bitrate_econ.txt", "a")
            f.write(str(quality_to_bitrate[econ_bitrate])+"\n")
            f.close()
            f = open("rep_econ.txt", "a")
            f.write(str(quality_to_rep[econ_bitrate])+"\n")
            f.close()
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

Handler = MyRequestHandler
PORT = 80

# replace IP with your machine IP
server = SocketServer.TCPServer(('130.245.145.208', PORT), Handler)
print ("Serving at port", PORT)
server.serve_forever()