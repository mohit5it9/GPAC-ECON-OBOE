import os
from IMC19ECON.pythonScripts import calcTx as tx
from  IMC19ECON.pythonScripts import findLoss as loss
from video_data import *

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

def get_econ_bitrate(OBOE):
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
    
    econTx = None
    bitrate = 0

    # if running OBOE+ECON
    if OBOE == True:
        # calculate throughput from ECON Paper
        global chunk_when_last_chd, alpha
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

        global chunk_when_last_chd, alpha
        econTx, alpha, chunk_when_last_chd = tx.calcTxCubic(scwnd, rounds, pcwnd, rtt, 0, 0, False)
        print ("econTx is", econTx*1500*0.25)
        bitrate = getCorrespondingBitrate(econTx*1500*2)
        return bitrate



# gets bitrate corresponding to ECON predicted throughput
def getCorrespondingBitrate(tx):
    bitrate = '180'
    for quality in sorted(quality_to_bitrate.keys(), reverse=True):
        size = quality_to_bitrate[quality]
        if tx >= size:
            bitrate = str(quality)
            break
    return bitrate


