#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# GNU Radio version: 3.10.9.2

from gnuradio import blocks
import pmt
from gnuradio import blocks, gr
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import iio




class networkedSDR(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 2600000
        self.freq_c = freq_c = 1575420000

        ##################################################
        # Blocks
        ##################################################

        self.iio_fmcomms2_sink_0 = iio.fmcomms2_sink_fc32('ip:192.168.1.131', [True, True, False, False], 32768, False)
        self.iio_fmcomms2_sink_0.set_len_tag_key('')
        self.iio_fmcomms2_sink_0.set_bandwidth(20000000)
        self.iio_fmcomms2_sink_0.set_frequency(freq_c)
        self.iio_fmcomms2_sink_0.set_samplerate(samp_rate)
        if True:
            self.iio_fmcomms2_sink_0.set_attenuation(0, 30.0)
        if False:
            self.iio_fmcomms2_sink_0.set_attenuation(1, 10.0)
        self.iio_fmcomms2_sink_0.set_filter_params('Auto', '', 0, 0)
        self.blocks_probe_rate_0 = blocks.probe_rate(gr.sizeof_gr_complex*1, 500.0, 0.15, '')
        self.blocks_message_debug_0 = blocks.message_debug(False, gr.log_levels.info)
        self.blocks_interleaved_char_to_complex_0 = blocks.interleaved_char_to_complex(True,1.0)
        self.blocks_file_source_0_0 = blocks.file_source(gr.sizeof_char*2, 'E:\\Thesis\\GNSS-sdr-sim\\data\\OutputIQ.sigmf-data', False, 0, 0)
        self.blocks_file_source_0_0.set_begin_tag(pmt.PMT_NIL)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_probe_rate_0, 'rate'), (self.blocks_message_debug_0, 'print'))
        self.connect((self.blocks_file_source_0_0, 0), (self.blocks_interleaved_char_to_complex_0, 0))
        self.connect((self.blocks_interleaved_char_to_complex_0, 0), (self.blocks_probe_rate_0, 0))
        self.connect((self.blocks_interleaved_char_to_complex_0, 0), (self.iio_fmcomms2_sink_0, 0))


    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.iio_fmcomms2_sink_0.set_samplerate(self.samp_rate)

    def get_freq_c(self):
        return self.freq_c

    def set_freq_c(self, freq_c):
        self.freq_c = freq_c
        self.iio_fmcomms2_sink_0.set_frequency(self.freq_c)




def main(top_block_cls=networkedSDR, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    try:
        input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
