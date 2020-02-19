from microbit import *

DISTANCE_CM_PER_BIT = 0.21
DISTANCE_OFFSET = -2
TRIG_PIN = 0
ECHO_PIN = 0
display.off()

def pins(trigger, echo):
    global TRIG_PIN
    global ECHO_PIN
    TRIG_PIN = trigger
    ECHO_PIN = echo

def distancia():
    global TRIG_PIN
    global ECHO_PIN
    spi.init(baudrate=50000, bits=8, mode=0, miso=ECHO_PIN)
    TRIG_PIN.write_digital(True)
    TRIG_PIN.write_digital(False)
    x = spi.read(200)
    high_bits = 0
    for i in range(len(x)):
        if x[i] == 0 and high_bits > 0:
            break
        elif x[i] == 0xFF:
            high_bits += 8
        else:
            high_bits += bin(x[i]).count("1")
    x = None
    dist = high_bits * DISTANCE_CM_PER_BIT
    if dist >= 2:
        dist += DISTANCE_OFFSET
    return round(dist)
