import signal
import time

def fn(*args, **kwargs):
    print args
    print kwargs
    print "hey SIGINT"
    import sys
    sys.exit()

signal.signal(signal.SIGINT, fn)
signal.signal(signal.SIGTERM, fn)
# signal.signal(signal.SIGSTOP, fn)
# signal.signal(signal.SIGKILL, fn)

while True:
    time.sleep(0.1)
    print ".", 


