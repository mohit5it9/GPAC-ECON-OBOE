'''
This is the server side code that serves
the Dash File and video segment chunks for
the Dash video file. Runs with python2
Not tested with python3
'''

import SimpleHTTPServer
import SocketServer
import os
import IMC19ECON.pythonScripts.calcTx as tx
import IMC19ECON.pythonScripts.findLoss as loss

# initialization section
cwnd_arr = list() # contains historical cwnd values
prev_snd_nxt = 0

# ECON constants
rounds = 100
alpha = 0.0

last_ts = None
prev_cwnd = None

# segment number when change detection algo was last run for OBOE = True
chunk_when_last_chd = -1

packet_size = 1
scwnd = None
OBOE = False # Chanhe this to True if we need to run OBOE+ECON
ECON = True # Change this to False if you're running BOLA, BBA. But do not change this value for now

# dictionary for bitrate value to representation number
quality_to_rep = {
    "180": 0, "360": 1, "540": 2, "720": 3, "1080": 4
}

# dict for bitrate value to equivalent size
quality_to_bitrate = {
    "1080": 1589541.0, "720": 1515802.0, "360": 512520.0, "540": 864894.0, "180": 222078.0
}

# gets bitrate corresponding to ECON predicted throughput
def getCorrespondingBitrate(tx):
    # tx /= 8
    bitrate = '180'
    if tx >= 1589541.0:
        bitrate = '1080'
    elif tx >= 1515802.0:
        bitrate = '720'
    elif tx >= 864894.0:
        bitrate = '540'
    elif tx >= 512520.0:
        bitrate = '360'
    elif tx >= 222078.0:
        bitrate = '180'
    return bitrate

def get_econ_bitrate():
    # runs shell command to get the previous 10 congestion window values.
    # This runs only on ubuntu machines where kernel level <= 4.16
    stream = os.popen("grep 'src=130.245.145.208:80' /sys/kernel/debug/tracing/trace | tail -n 10")
    terminal_output = stream.read()
    terminal_output = terminal_output.split('\n')
    # process the tcpprobe output
    for line in terminal_output:
        # parse the CWND and RTT values from tcpprobe output
        trace = [x.strip() for x in line.split()]
        if len(trace) <= 0:
            continue
        ts = trace[3]
        cwnd = trace[11].split("=")[1]
        snd_nxt = int(trace[9].split("=")[1], 16)
        rtt = float(int(trace[14].split("=")[1])/1000000.0)

        prev_snd_nxt = snd_nxt
        global last_ts, scwnd, cwnd_arr, prev_cwnd
        if ts != last_ts:
            if scwnd == None:
                scwnd = float(cwnd)
            elif (cwnd < prev_cwnd):
                scwnd = float(cwnd)
            cwnd_arr.append(int(cwnd))
            prev_cwnd = cwnd
        last_ts = ts
    global OBOE, chunk_when_last_chd, alpha
    econTx = None
    bitrate = 0

    # if running OBOE+ECON
    if OBOE == True:
        # calculate throughput from ECON Paper
        econTx, alpha, chunk_when_last_chd = tx.calcTxCubic(scwnd, rounds, cwnd_arr, rtt, chunk_when_last_chd, alpha, True)
        bitrate = getCorrespondingBitrate(econTx*1500*2)
        return bitrate

    else:
        # TODO: Only added for TCP Cubic variant.
        pcwnd, sIdx, eIdx = loss.findLossCubic(cwnd_arr)
        if not len(pcwnd) or all(pcwnd) == 0.0:
            econTx = float(cwnd_arr[-1]*1500*2/(rtt))
            bitrate = getCorrespondingBitrate(econTx)
            return bitrate

        econTx, alpha, chunk_when_last_chd = tx.calcTxCubic(scwnd, rounds, pcwnd, rtt, 0, 0, False)
        print ("econTx is", econTx*1500*0.25)
        bitrate = getCorrespondingBitrate(econTx*1500*2)
        return bitrate

class MyRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        customUrl = self.path.split("_dash")
        if len(customUrl) > 1 and ECON == True:
            # get the next bitrate to serve as determined by ECON
            econ_bitrate = get_econ_bitrate()
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