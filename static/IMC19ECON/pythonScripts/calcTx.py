# Code for calculating throughput
import numpy as np
import math
import sys
import bayesian_changepoint_detection.online_changepoint_detection as oncd
from configmap_econ_oboe import *
from functools import partial

CD_INTERVAL = 5
def calcTxCubic(scwnd, rounds, used_cwnd, rtt, chunk_when_last_chd, prev_alpha, OBOE):
    c, beta = 0.4, 0.3
    wmax = int(scwnd / (1 - beta))
    k = (wmax * beta / c) ** (1/3)

    # Calculate the cwnd value for each round trip
    t, cwnds = 0, []
    for i in range(rounds):
        cwnd = int(c * (t - k) ** 3 + wmax)
        cwnds.append(cwnd)
        t += rtt

    # #pkts sent
    maxPktNum = sum(cwnds)

    # Calculate alpha and x
    if OBOE == False:
        pcwnd = used_cwnd
        idxW, cnt, alpha, pr = 0, 0, 0, 1
        cwnd = cwnds[idxW]
        if cwnd < len(pcwnd):
            _p = pcwnd[cwnd]
        else:
            _p = pcwnd[-1]

        for idxP in range(maxPktNum):
            # print(idxP)
            if idxP != 0:
                pr *= ((1 - _p) / _p)

            # See if need to update cwnd
            if cnt == cwnds[idxW]:
                cnt = 0
                idxW += 1
                cwnd = cwnds[idxW]
                if cwnd < len(pcwnd):
                    _p = pcwnd[cwnd]
                else:
                    _p = pcwnd[-1]

            cnt += 1
            pr *= _p
            alpha += (idxP + 1) * pr
    else:
        alpha, chunk_when_last_chd = getAlpha(used_cwnd, chunk_when_last_chd, prev_alpha)

    x, rem, idx = 0, alpha, -1
    while rem > 0:
        x += 1
        idx += 1
        rem -= cwnds[idx]

    n = alpha + cwnds[idx] - 1
    t = (x + 1) * rtt
    econ = n / t

    # print("cubic -- scwnd = " + str(scwnd) + "; Alpha = " + str(alpha) + "; X: " + str(x) + "; rtt:" + str(rtt))
    # res = [econ, t, cwnds[idx]]
    return econ, alpha, chunk_when_last_chd

def getAlpha(cwnd, chunk_when_last_chd, prev_alpha):
  ch_detected, ch_index = onlineCD(chunk_when_last_chd, CD_INTERVAL, cwnd)
  est_cwnd, est_std = getBWFeaturesWeightedPlayerVisible(cwnd, ch_index)

  print (ch_detected, ch_index, est_cwnd, est_std)

  if ch_detected:
      dict_name_backup = "configmap_econ_oboe_1"
      performance_t = (globals()[dict_name_backup])
      disc_min, disc_median, disc_max, disc_mean = getDynamicconfig_econ(performance_t, est_cwnd, est_std, 1)
      return disc_median, ch_index

  else:
    return prev_alpha, chunk_when_last_chd #Should this be CH_INDEX


def onlineCD(chunk_when_last_chd, interval, cwnd):
  chd_detected = False
  chd_index = chunk_when_last_chd
  trimThresh = 1000
  lenarray = len(cwnd)
  cwnd, cutoff = trimPlayerVisibleBW(cwnd, trimThresh)
  R, maxes = oncd.online_changepoint_detection(np.asanyarray(cwnd), partial(oncd.constant_hazard, 250), oncd.StudentT(0.1,0.01,1,0))
  interval = min(interval, len(cwnd))
  changeArray = R[interval,interval:-1]
  for i,v in reversed(list(enumerate(changeArray))): #reversed(list(enumerate(changeArray))): # enumerate(changeArray):
    if v > 0.01 and i + cutoff > chunk_when_last_chd and not (i == 0 and chunk_when_last_chd > -1):
      chd_index = i + cutoff
      chd_detected = True
      break
  return chd_detected, chd_index


def trimPlayerVisibleBW(cwnd, thresh):
  ret = []
  cutoff = 0
  lenarray = len(cwnd)
  if lenarray <= thresh:
    return cwnd, cutoff

  cutoff = lenarray - thresh
  ret = cwnd[cutoff:]
  return ret, cutoff


def getBWFeaturesWeightedPlayerVisible(cwnd, chunk_when_last_chd_ran):
  lookbackwindow = len(cwnd) - min(15, len(cwnd) - chunk_when_last_chd_ran)
  currentstateBWArray = cwnd[lookbackwindow:]
  return np.mean(currentstateBWArray), np.std(currentstateBWArray)


def getDynamicconfig_econ(pv_list_hyb, bw, std, step):
    bw_step = step
    std_step = step
    bw_cut =int(float(bw)/bw_step)*bw_step
    std_cut = int(float(std)/std_step)*std_step
    current_list_hyb = list()
    count = 0
    if True:
        if bw==-1 and std==-1:
            return 0.0, 0.0, 0.0, 0.0
        # if key not in performance vector
        if (bw_cut, std_cut) not in pv_list_hyb.keys():
            for i in range(1, 5):
                count += 1
                for bw_ in [bw_cut - (i - 1) * bw_step, bw_cut + (i-1) * bw_step]:
                    for std_ in range(std_cut - (i - 1) * std_step, std_cut + (i-1) * std_step + std_step, std_step):
                        if (bw_, std_) in pv_list_hyb.keys():
                            current_list_hyb = current_list_hyb + pv_list_hyb[(bw_, std_)]
                for std_ in [std_cut - (i - 1) * std_step, std_cut + (i-1) * std_step]:
                    for bw_ in range(bw_cut - (i - 2) * bw_step, bw_cut + (i-1) * bw_step, bw_step):
                        if (bw_, std_) in pv_list_hyb.keys():
                            current_list_hyb = current_list_hyb + pv_list_hyb[(bw_, std_)]
                if len(current_list_hyb)==0:
                    continue
                else:# len(abr_list)>0 and 'BB' not in abr_list:
                    break
        else:
            current_list_hyb = current_list_hyb + pv_list_hyb[(bw_cut, std_cut)]

    if len(current_list_hyb)==0:
        return 0.0, 0.0, 0.0, 0.0
    if max(current_list_hyb) ==-1.0:
        return 0.0, 0.0, 0.0, 0.0
    return min(current_list_hyb), np.percentile(current_list_hyb,50), max(current_list_hyb), np.mean(current_list_hyb)

if __name__ == '__main__':
    scwnd = float(sys.argv[1])
    rounds = int(sys.argv[2])
    cwnd = [int(x) for x in sys.argv[3].split(",")]
    rtt = float(sys.argv[4])
    chunk_when_last_chd = int(sys.argv[5])
    prev_alpha = float(sys.argv[6])
    OBOE = bool(sys.argv[7])
    econ, alpha, chunk_when_last_chd = calcTxCubic(scwnd, rounds, cwnd, rtt, chunk_when_last_chd, prev_alpha, OBOE)
    print (econ)
    print (alpha)
    print (chunk_when_last_chd)
