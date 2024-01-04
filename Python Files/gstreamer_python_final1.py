import gi
gi.require_version('Gst', '1.0')
gi.require_version('GLib', '2.0')
gi.require_version("GstRtspServer", "1.0")
from gi.repository import Gst, GLib

Gst.init(None)

RSTP_source_location = "rtsp://admin:Admin12345@192.168.23.199:554/cam/realmonitor?channel=1&subtype=0"

def on_message(bus, message):
    t = message.type
    if t == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        print("Error: %s" % err, debug)
    elif t == Gst.MessageType.EOS:
        print("End-Of-Stream reached")
        loop.quit()
    elif t == Gst.MessageType.STATE_CHANGED:
        if message.src.get_name() == "pipeline":
            old_state, new_state, pending_state = message.parse_state_changed()
            print("Pipeline state changed from %s to %s." %
                  (old_state.value_nick, new_state.value_nick))

pipeline = Gst.parse_launch('rtspsrc location={} ! rtph264depay ! h264parse ! avdec_h264 ! autovideosink'.format(RSTP_source_location))
pipeline.set_state(Gst.State.PLAYING)

bus = pipeline.get_bus()
bus.add_signal_watch()
bus.connect("message", on_message)

loop = GLib.MainLoop()
loop.run()