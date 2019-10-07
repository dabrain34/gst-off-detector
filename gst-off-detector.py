#!/usr/bin/env python3

'''
Simple example to demonstrate dynamically adding and removing source elements
to a playing pipeline.
'''

import sys
import random
import openfoodfacts
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GLib', '2.0')
gi.require_version('GObject', '2.0')
from gi.repository import GLib, GObject, Gst
from optparse import OptionParser

class GstPlayer:
    def __init__(self, pipe, loop):
        self.pipe = pipe
        self.loop = loop

def check_off (symbol):
    product = openfoodfacts.products.get_product(symbol)
    print(product['status'])
    return product

def bus_call(bus, message, player):
    t = message.type
    if t == Gst.MessageType.EOS:
        sys.stdout.write("End-of-stream\n")
        player.loop.quit()
    elif t == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        sys.stderr.write("Error: %s: %s\n" % (err, debug))
        player.loop.quit()
    elif t == Gst.MessageType.ELEMENT:
        if message.get_structure().get_name() == "barcode":
          print (message.get_structure())
          print (message.get_structure().get_string("type"))
          print (message.get_structure().get_string("symbol"))
          #check_off("michelpatrick")
          check_off(message.get_structure().get_string("symbol"))

    return True

def main(args):
    GObject.threads_init()
    Gst.init(None)

    parser = OptionParser()
    parser.add_option("-c", "--custom_pipeline", dest="pipeline_str",
                  help="Use a custom pipeline")
    parser.add_option("-f", "--file", dest="file",
                  help="Use file instead of v4l2src")
    parser.add_option("-x", "--zxing",
                  action="store_true", dest="zxing", default=False,
                  help="use zxing instead of zbar")
    parser.add_option("-l", "--loop",
                  action="store_true", dest="loop", default=False,
                  help="playback loop on eos")

    (options, args) = parser.parse_args()
    
    source = "v4l2src ! video/x-raw,width=640,height=480"
    barcode_reader = "zbar"

    if options.pipeline_str:
      pipeline_str = options.pipeline_str

    if options.zxing:
        barcode_reader = "zxing"
    if options.file:
        source = "filesrc location=%s ! decodebin ! videoflip video-direction=auto" % options.file
    pipeline_str = source + " ! videoconvert ! " + barcode_reader + " ! xvimagesink"

    if options.pipeline_str:
        pipeline_str = options.pipeline_str

    print (pipeline_str)
    pipe =  bin = Gst.parse_launch(pipeline_str)

    loop = GObject.MainLoop()

    player = GstPlayer(pipe, loop)

    bus = pipe.get_bus()
    bus.add_signal_watch()
    bus.connect ("message", bus_call, player)

    # start play back and listen to events
    pipe.set_state(Gst.State.PLAYING)
    try:
        loop.run()
    except:
        pass

    # cleanup
    pipe.set_state(Gst.State.NULL)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
