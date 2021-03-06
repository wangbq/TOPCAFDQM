#!/usr/bin/env python
# -*- coding: utf-8 -*-

from basf2 import *
from ROOT import TCanvas
import argparse
import os.path as path
import os

set_log_level(LogLevel.ERROR)

parser = argparse.ArgumentParser(description='Go through a data file, apply calibration, and write the waveforms to a root file.',
                                 usage='%(prog)s [options]')

parser.add_argument(
    '--inputRun',
    metavar='InputRun (i.e. file name = InputRun.dat)',
    required=True,
    help='the name for the input data files.')

parser.add_argument(
    '-t',
    '--topConfiguration',
    required=False,
    default=path.join(os.environ['BELLE2_LOCAL_DIR'], 'topcaf/data/TopConfigurations.root'),
    help="Path name of top configuration root file, e.g. ../data/TopConfigurations.root")

parser.add_argument(
    '--ped',
    metavar='PedestalFile (path/filename)',
    required=False,
    help='The pedestal file and path to be used for the analysis. If not specified, will use the conditions service.')

parser.add_argument('--output', metavar='Output File (path/filename)',
                    help='the output file name.  A default based on the input will be created if this argument is not supplied')

args = parser.parse_args()

main = create_path()
SRootReader = register_module('SeqRootInput')
SRootReader.param('inputFileName', args.inputRun)

itopconfig = register_module('TopConfiguration')
itopconfig.param('filename', args.topConfiguration)

itopeventconverter = register_module('iTopRawConverterSRoot')
itopeventconverter.param('forceTrigger0xF', True)

#histomanager = register_module("HistoManager")

if args.output:
    outputFile = args.output
else:
    outputFile = args.inputRun.replace('.sroot', '_writehits.root')
# print('Writing output root file to ' + outputFile)
#output = register_module('RootOutput')
#outputDict = {'outputFileName': outputFile,
#              'excludeBranchNames': ["EventWaveformPackets"]}
#output.param(outputDict)

pedmodule = register_module('Pedestal')
pedmodule.param('mode', 1)
if args.ped:
    pedmodule.param('inputFileName', args.ped)
    pedmodule.param('conditions', 0)
else:
    pedmodule.param('conditions', 1)

mergemodule = register_module('WaveMerging')

timemodule = register_module('WaveTimingFast')
timeDict = {'time2TDC': 1.0}
timemodule.param(timeDict)
timemodule.param('threshold', 50.)  # always
timemodule.param('threshold_n', -300.)  # must be -150 for "small calpulse"
# it shouldn't be anything else
# if it, is the code will crash -- on purpose

timecalibmodule = register_module('DoubleCalPulse')
timecalibmodule.param('calibrationTimeMin', 200)   # laser
timecalibmodule.param('calibrationWidthMax', 20)
timecalibmodule.param('calibrationWidthMin', 6)
timecalibmodule.param('calibrationADCThreshold', -300)  # must be -150 for "small calpulse"
timecalibmodule.param('calibrationADCThreshold_max', -800)

dqmmodule = register_module("TOPDataQualityOnline")

progress = register_module('Progress')

main.add_module(SRootReader)
#main.add_module(histomanager)
main.add_module(itopconfig)
main.add_module(itopeventconverter)
main.add_module(pedmodule)
main.add_module(mergemodule)
main.add_module(timemodule)
main.add_module(timecalibmodule)
main.add_module(dqmmodule)
main.add_module(progress)
#main.add_module(plotsmodule)
# main.add_module(output)
process(main)

print(statistics)
