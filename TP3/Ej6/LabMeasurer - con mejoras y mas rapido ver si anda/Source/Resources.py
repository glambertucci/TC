import time
import numpy as np
import os
import matplotlib.pyplot as plt

###################################################################################
#MISC
###################################################################################
SET = 0
GET = 1
OOR_VAL = '9.9e+37' #out of range value
REST_TIME = 3
###################################################################################
#CHANNEL
###################################################################################
CHANNEL_1 = 1
CHANNEL_2 = 2
CHANNEL_3 = 3
CHANNEL_4 = 4
CHANNEL_MATH = 'MATH'
CHAN_DIV_SQUARES = 8
COUP_DC = 'DC'
COUP_AC = 'AC'
###################################################################################
# TIMEBASE
###################################################################################
MODE_MAIN = 'MAIN'
TIME_DIV_SQUARES = 10
REF_CENTER = 'CENTer'
###################################################################################
# TRIGGER
###################################################################################
TRIG_NORMAL = 'NORMAL'
TRIG_SLOPE_POSITIVE =  'POSitive'
TRIG_HFREJ_ON = 'ON'
TRIG_HFREJ_OFF = 'OFF'
TRIG_EXTERNAL = 'EXTernal'
###################################################################################
# ACQUIRE
###################################################################################
ACQUIRE_TYPE_NORMAL = 'NORMal'
ACQUIRE_TYPE_AVERAGE = 'AVERage'
ACQUIRE_TYPE_HIGH_RES = 'HRESolution'
###################################################################################
# WAVEFORM
###################################################################################
WAVEFORM_FORMAT_BYTE = 'BYTE'
WAVEFORM_FORMAT_WORD = 'WORD'
WAVEFORM_FORMAT_ASCII = 'ASCii'
WAVEFORM_UNSIGNED_ON = 'ON'
WAVEFORM_UNSIGNED_OFF = 'OFF'
WAVEFORM_POINTS_MODE_RAW = 'RAW'
###################################################################################
# STATISTICS
###################################################################################
STATS_MEAN = 'MEAN'
STATS_CURR = 'CURRent'


#:TIMebase:MODE must be set to MAIN to perform a :DIGitize command or to perform any
#:WAVeform subsystem query. A "Settings conflict" error message will be returned if these
#commands are executed when MODE is set to ROLL, XY, or WINDow (zoomed). Sending the
#*RST (reset) command will also set the time base mode to normal.

#When you change the oscilloscope configuration, the waveform buffers are cleared. Before
#doing a measurement, send the :DIGitize command to the oscilloscope to ensure new data
#has been collected.

class Oscilloscope:
    def __init__(self, resource):
        self.resource = resource
        self.chan1=1
        self.chan2=2
        self.reset()

#MISC
    def set_bode_meas(self, channel1, channel2):
        if(channel1 == 0):
            self.chan1 = CHANNEL_MATH
        elif(channel1 == 1):
            self.chan1 = CHANNEL_1
        elif (channel1 == 2):
            self.chan1 = CHANNEL_2
        elif (channel1 == 3):
            self.chan1 = CHANNEL_3
        elif (channel1 == 4):
            self.chan1 = CHANNEL_4
        if (channel2 == 0):
            self.chan2 = CHANNEL_MATH
        elif (channel2 == 1):
            self.chan2 = CHANNEL_1
        elif (channel2 == 2):
            self.chan2 = CHANNEL_2
        elif (channel2 == 3):
            self.chan2 = CHANNEL_3
        elif (channel2 == 4):
            self.chan2 = CHANNEL_4
        #self.clear_meas()
        self.set_ratio_meas(channel1, channel2)
        self.set_phase_meas(channel1, channel2)
        self.set_sleep_time_stats(REST_TIME)
        self.stat_set(STATS_MEAN)
    def set_sleep_time_stats(self, sleep):
        self.sleep = sleep
    def reset(self):
        self.resource.write('*RST')
    def autoscale(self):
        self.resource.write(':AUToscale')
    def measure_tran(self, channel1, channel2, filename):
        self.digitize_chan(channel1)
        self.waveform_source(channel1)
        self.waveform_format(WAVEFORM_FORMAT_ASCII)
        self.waveform_unsigned(WAVEFORM_UNSIGNED_OFF)
        self.waveform_points_mode(SET, WAVEFORM_POINTS_MODE_RAW)
        self.waveform_points(SET, 10000)
        preamble = self.waveform_preamble()
        preamble = preamble.split(',')
        time_increment = float(preamble[4])
        chan_increment = float(preamble[7])
        data1 = self.waveform_data()
        data1 = data1[10:]
        data1 = data1.split(',')
        len_data= (len(data1))
        data_float1=[]
        for i in range(len_data):
            data_float1.append(float(data1[i]))
        time_div = time_increment*len_data/TIME_DIV_SQUARES
        chan_div = chan_increment*32
        chan1_tran=[[time_div,chan_div]]
        for i in range(len_data):
            chan1_tran.append(data_float1[i])

        self.digitize_chan(channel2)
        self.waveform_source(channel2)
        self.waveform_format(WAVEFORM_FORMAT_ASCII)
        self.waveform_unsigned(WAVEFORM_UNSIGNED_OFF)
        self.waveform_points_mode(SET, WAVEFORM_POINTS_MODE_RAW)
        self.waveform_points(SET, 10000)
        preamble = self.waveform_preamble()
        preamble = preamble.split(',')
        time_increment = float(preamble[4])
        chan_increment = float(preamble[7])
        data2 = self.waveform_data()
        data2 = data2[10:]
        data2 = data2.split(',')
        len_data = (len(data2))
        data_float = []
        for i in range(len_data):
            data_float.append(float(data2[i]))
        time_div = time_increment * len_data / TIME_DIV_SQUARES
        chan_div = chan_increment * 32
        chan2_tran = [[time_div, chan_div]]
        for i in range(len_data):
            chan2_tran.append(data_float[i])

        if (os.path.exists("Mediciones/" + filename + ".csv")):
            file = open("Mediciones/" + filename + ".csv", "w+")
        else:
            for i in range(1, 100, 1):
                file = open("Mediciones/" + filename + "(" + str(i) + ")" + ".csv", 'w+')

        file.write("time\tV1\tV2\r\n")

        print(len_data)
        print(time_increment)
        time = np.arange(0, len_data*time_increment, time_increment)

        plt.plot(time, chan1_tran)
        plt.plot(time,chan2_tran)
        plt.show()

        for i in time:
            file.write(str(self.time[i]) + '\t')
            file.write(str(self.chan1_tran[i]) + '\t')
            file.write(str(self.chan2_tran[i]) + '\r\n')

        file.close()

#CHANNEL SET
    def chan_div(self, sog, channel, div = 1):       #CHANNEL DIVISION
        if(sog == SET):
            self.chan_rang(SET, channel, div*CHAN_DIV_SQUARES)
        elif(sog == GET):
            return float(self.chan_rang(GET, channel)) / CHAN_DIV_SQUARES

    def chan_rang(self, sog, channel, range = 8):    #CHANNEL RANGE
        if (sog == SET):
            self.resource.write(':CHANnel' + str(channel) + ':RANGe ' + str(range))
        elif (sog == GET):
            return self.resource.query(':CHANnel' + str(channel) + ':RANGe?')

    def chan_offs(self, sog, channel, offset = 0):   #CHANNEL OFFSET
        if (sog == SET):
            self.resource.write(':CHANnel' + str(channel) + ':OFFSet ' + str(offset))
        elif (sog == GET):
            return self.resource.query(':CHANnel' + str(channel) + ':OFFSet?')

    def chan_probe(self, sog, channel, probe = 1):   #CHANNEL PROBE ATENUATION
        if (sog == SET):
            self.resource.write(':CHANnel' + str(channel) + ':PROBe ' + str(probe))
        elif (sog == GET):
            return self.resource.query(':CHANnel' + str(channel) + ':PROBe?')

    def chan_coup(self, sog, channel, coupling = COUP_DC):    #CHANNEL COUPLING
        if (sog == SET):
            self.resource.write(':CHANnel' + str(channel) + ':COUPling ' + coupling)
        elif (sog == GET):
            return self.resource.query(':CHANnel' + str(channel) + ':COUPling?')

#TIMEBASE SET
    def tim_mode(self, sog, mode):   #TIMEBASE MODE
        if (sog == SET):
            self.resource.write(':TIMebase:MODE ' + mode)
        elif (sog == GET):
            return self.resource.query(':TIMebase:MODE?')
    def tim_rang(self, sog, range):  #TIMEBASE RANGE
        if (sog == SET):
            self.resource.write(':TIMebase:RANGe ' + str(range))
        elif (sog == GET):
            return self.resource.query(':TIMebase:RANGe?')
    def tim_div(self, sog, div):     #TIMEBASE DIVISION
        if (sog == SET):
            self.tim_rang(SET, div*8)
        elif (sog == GET):
            return self.tim_rang(GET) / 8
    def tim_delay(self, sog, delay): #TIMEBASE DELAY
        if (sog == SET):
            self.resource.write(':TIMebase:DELay ' + str(delay))
        elif (sog == GET):
            return self.resource.write(':TIMebase:DELay?')
    def tim_ref(self, sog, position): #TIMEBASE POSITION
        if (sog == SET):
            self.resource.write( ':TIMebase:REFerence ' + position)
        elif (sog == GET):
            return self.resource.query(':TIMebase:REFerence?')

#TRIGGER SET
    def trig_sweep_mode(self, sog, mode):    #TRIGGER SWEEP MODE
        if(sog == SET):
            self.resource.write(':TRIGger:SWEep ' + mode)
        elif(sog == GET):
            return self.resource.query(':TRIGger:SWEep?')
    def trig_level(self, sog, lvl):          #TRIGGER LEVEL
        if(sog == SET):
            self.resource.write(':TRIGger:LEVel ' + str(lvl))
        elif(sog == GET):
            return self.resource.query(':TRIGger:LEVel?')
    def trig_slope(self, sog, slope):
        if(sog == SET):
            self.resource.write(':TRIGger:SLOPe ' + slope)
        elif(sog == GET):
            return self.resource.query(':TRIGger:SLOPe?')
    def trig_hfreject(self, sog, mode):
        if(sog==SET):
            self.resource.write(':TRIGger:HFReject ' + mode)
        elif(sog==GET):
            return self.resource.query(':TRIGger:HFReject?')
    def trig_source(self, sog, mode):
        if(sog==SET):
            self.resource.write(':TRIGger:SOURce ' + mode)
        elif(sog==GET):
            return self.resource.query(':TRIGger:SOURce?')

#AQUIRE
    def acq_type(self, sog, mode):
        if(sog==SET):
            self.resource.write(':ACQuire:TYPE ' + mode)
        elif(sog==GET):
            return self.resource.query(':ACQuire:TYPE?')
    def acq_average_count(self, sog, count):
        if(sog==SET):
            self.resource.write(':ACQuire:COUNt ' + str(count))
        if(sog==GET):
            return self.resource.query(':ACQuire:COUNt?')

#DIGITALIZATION
    def digitize_chan(self, channel):
        self.resource.write(':DIGitize CHANnel' + str(channel))
    def waveform_source(self, channel):
        self.resource.write(':WAVeform:SOURce CHANnel' + str(channel))
    def waveform_format(self, format):
        self.resource.write(':WAVeform:FORMat ' + format)
    def waveform_unsigned(self, mode):
        self.resource.write('WAVeform:UNSigned ' + mode)
    def waveform_points_mode(self, sog, mode):
        if(sog==SET):
            self.resource.write(':WAVeform:POINts:MODE ' + mode)
        elif(sog==GET):
            return self.resource.query(':WAVeform:POINts:MODE?')
    def waveform_points(self, sog, points):
        if (sog == SET):
            self.resource.write(':WAVeform:POINts ' + str(points))
        elif (sog == GET):
            return self.resource.query(':WAVeform:POINts?')
    def waveform_preamble(self):
        return self.resource.query(':WAVeform:PREamble?')
    def waveform_data(self):
        return self.resource.query(':WAVeform:DATA?')
#MEASURE
    def clear_meas(self):
        self.resource.write(':MEASure:CLEar')
    def meas_source(self, sog, channel1 = 1, channel2 = 2):
        if(sog==SET):
            self.resource.write(':MEASure:SOURce ' + str(channel1) + ',' + str(channel2))
        elif(sog==GET):
            return self.resource.query(':MEASure:SOURce?')
    def is_clipping(self, channel):
        self.resource.write(':MEASure:SOURce CHANnel' + str(channel))
        vmax = float(self.resource.query(':MEASure:VMAX?'))
        vmin = float(self.resource.query(':MEASure:VMIN?'))
        if(vmax == float(OOR_VAL) or vmin == float(OOR_VAL)):
            return True
        else:
            return False
    def is_big_enough(self, channel):
        self.resource.write(':MEASure:SOURce CHANnel' + str(channel))
        vmax = float(self.resource.query(':MEASure:VMAX?'))
        vmin = float(self.resource.query(':MEASure:VMIN?'))
        chan_div = float(self.chan_div(GET, channel))
        if(abs((vmax-vmin)) > 4*chan_div):
            return True
        else:
            return False

    def get_freq(self, channel):
        if(channel == 0):
            return self.resource.query(':MEASure:FREQuency? ' + CHANNEL_MATH)
        elif(channel != 0):
            return self.resource.query(':MEASure:FREQuency? ' + str(channel))
        return self.resource.query(':MEASure:FREQuency? CHANnel' + str(channel))
    def get_phase(self, channel1=1, channel2=2):
        return self.resource.query(':MEASure:PHAse?')
    def get_ratio(self, channel1=1, channel2=2):
        return self.resource.query(':MEASure:VRATio?')
    def set_freq_meas(self, channel):
        if (channel != 0):
            self.resource.write(':MEASure:FREQuency CHANnel' + str(channel))
        elif(channel == 0):
            self.resource.write(':MEASure:FREQuency ' + CHANNEL_MATH)
    def set_phase_meas(self, channel1, channel2):
        if(channel1 == 0):
            self.resource.write(':MEASure:SOURce ' + CHANNEL_MATH + ',CHANnel' + str(channel2))
        elif(channel2 == 0):
            self.resource.write(':MEASure:SOURce CHANnel' + str(channel1) + ',' + CHANNEL_MATH)
        else:
            self.resource.write(':MEASure:SOURce CHANnel' + str(channel1) + ',CHANnel' + str(channel2))
        self.resource.write(':MEASure:PHAse')
    def set_ratio_meas(self, channel1, channel2):
        if (channel1 == 0):
            self.resource.write(':MEASure:SOURce ' + CHANNEL_MATH + ',CHANnel' + str(channel2))
        elif (channel2 == 0):
            self.resource.write(':MEASure:SOURce CHANnel' + str(channel1) + ',' + CHANNEL_MATH)
        else:
            self.resource.write(':MEASure:SOURce CHANnel' + str(channel1) + ',CHANnel' + str(channel2))
        self.resource.write(':MEASure:VRATio')
    def stats_reset(self, f, mintime):
        self.resource.write(':MEASure:STATistics:RESet')
        freqtime = 8*(1/(np.power(f, (1/6))))
        if(mintime > freqtime):
            time.sleep(mintime)
        else:
            time.sleep(freqtime)
    def stat_set(self, stat):
        self.resource.write(':MEASure:STATistics ' + stat)
    def measure_stats(self, f, mintime):
        self.stats_reset(f, mintime)
        return self.resource.query(':MEASure:RESults?')

##############################################################################################################################################################
class Generator:
    def __init__(self, resource):
        self.resource = resource
        self.reset()

    def reset(self):
        self.resource.write('*RST')
    def set_output(self, set):
        self.resource.write(':OUTPUT ' + str(set))
    def set_voltage(self, volt):
        self.resource.write('VOLT ' + str(volt))
    def set_frequency(self, frequency):
        self.resource.write(':FREQ ' + str(frequency))