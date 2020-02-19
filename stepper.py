# Basada en la llibreria d'Elecfreaks: https://github.com/elecfreaks/pxt-robit/blob/master/robit.ts
# I amb la del gingemonster: https://github.com/gingemonster/PCA9685-Python-Microbit

from microbit import sleep, i2c
import math, ustruct

# Registers/etc:
PCA9685_ADDRESS    = 0x40
MODE1              = 0x00
MODE2              = 0x01
SUBADR1            = 0x02
SUBADR2            = 0x03
SUBADR3            = 0x04
PRESCALE           = 0xFE
LED0_ON_L          = 0x06
LED0_ON_H          = 0x07
LED0_OFF_L         = 0x08
LED0_OFF_H         = 0x09
ALL_LED_ON_L       = 0xFA
ALL_LED_ON_H       = 0xFB
ALL_LED_OFF_L      = 0xFC
ALL_LED_OFF_H      = 0xFD

# Bits:
RESTART            = 0x80
SLEEP              = 0x10
ALLCALL            = 0x01
INVRT              = 0x10
OUTDRV             = 0x04
RESET              = 0x00

# Variables:
on = 0
off = 0
freq_hz = 60

# Pins
STP_CHA_L = 2047
STP_CHA_H = 4095
STP_CHB_L = 1
STP_CHB_H = 2047
STP_CHC_L = 1023
STP_CHC_H = 3071
STP_CHD_L = 3071
STP_CHD_H = 1023


# Inicialització
i2c.write(PCA9685_ADDRESS, bytearray([MODE1, RESET]))   # Reset
# PWM a 0
i2c.write(PCA9685_ADDRESS, bytearray([ALL_LED_ON_L, on & 0xFF]))
i2c.write(PCA9685_ADDRESS, bytearray([ALL_LED_ON_H, on >> 8]))
i2c.write(PCA9685_ADDRESS, bytearray([ALL_LED_OFF_L, off & 0xFF]))
i2c.write(PCA9685_ADDRESS, bytearray([ALL_LED_OFF_H, off >> 8]))

i2c.write(PCA9685_ADDRESS, bytearray([MODE2, OUTDRV]))
i2c.write(PCA9685_ADDRESS, bytearray([MODE1, ALLCALL]))
sleep(5)  # wait for oscillator
i2c.write(PCA9685_ADDRESS, bytearray([MODE1]))  # write register we want to read from first
mode1 = i2c.read(PCA9685_ADDRESS, 1)
mode1 = ustruct.unpack('<H', mode1)[0]
mode1 = mode1 & ~SLEEP  # wake up (reset sleep)
i2c.write(PCA9685_ADDRESS, bytearray([MODE1, mode1]))
sleep(5)  # wait for oscillator


# Freqüència PWM in hertz
prescaleval = 25000000.0    # 25MHz
prescaleval /= 4096.0       # 12-bit
prescaleval /= float(freq_hz)
prescaleval -= 1.0
# print('Setting PWM frequency to {0} Hz'.format(freq_hz))
# print('Estimated pre-scale: {0}'.format(prescaleval))
prescale = int(math.floor(prescaleval + 0.5))
# print('Final pre-scale: {0}'.format(prescale))
i2c.write(PCA9685_ADDRESS, bytearray([MODE1]))  # write register we want to read from first
oldmode = i2c.read(PCA9685_ADDRESS, 1)
oldmode = ustruct.unpack('<H', oldmode)[0]
newmode = (oldmode & 0x7F) | 0x10    # sleep
i2c.write(PCA9685_ADDRESS, bytearray([MODE1, newmode]))  # go to sleep
i2c.write(PCA9685_ADDRESS, bytearray([PRESCALE, prescale]))
i2c.write(PCA9685_ADDRESS, bytearray([MODE1, oldmode]))
sleep(5)
i2c.write(PCA9685_ADDRESS, bytearray([MODE1, oldmode | 0x80]))

# Set pwm
def set_pwm(channel, on, off):
    """Sets a single PWM channel."""
    if on is None or off is None:
        i2c.write(PCA9685_ADDRESS, bytearray([LED0_ON_L+4*channel]))   # write register we want to read from first
        data = i2c.read(PCA9685_ADDRESS, 4)
        return ustruct.unpack('<HH', data)
    i2c.write(PCA9685_ADDRESS, bytearray([LED0_ON_L+4*channel, on & 0xFF]))
    i2c.write(PCA9685_ADDRESS, bytearray([LED0_ON_H+4*channel, on >> 8]))
    i2c.write(PCA9685_ADDRESS, bytearray([LED0_OFF_L+4*channel, off & 0xFF]))
    i2c.write(PCA9685_ADDRESS, bytearray([LED0_OFF_H+4*channel, off >> 8]))


def setStepper(index, direction):
    if index == 1:
        if direction:
            set_pwm(0, STP_CHA_L, STP_CHA_H)
            set_pwm(2, STP_CHB_L, STP_CHB_H)
            set_pwm(1, STP_CHC_L, STP_CHC_H)
            set_pwm(3, STP_CHD_L, STP_CHD_H)
        else:
            set_pwm(0, STP_CHA_L, STP_CHA_H)
            set_pwm(1, STP_CHB_L, STP_CHB_H)
            set_pwm(2, STP_CHC_L, STP_CHC_H)
            set_pwm(3, STP_CHD_L, STP_CHD_H)
    else:
        if direction:
            set_pwm(4, STP_CHA_L, STP_CHA_H)
            set_pwm(6, STP_CHB_L, STP_CHB_H)
            set_pwm(5, STP_CHC_L, STP_CHC_H)
            set_pwm(7, STP_CHD_L, STP_CHD_H)
        else:
            set_pwm(4, STP_CHA_L, STP_CHA_H)
            set_pwm(5, STP_CHB_L, STP_CHB_H)
            set_pwm(6, STP_CHC_L, STP_CHC_H)
            set_pwm(7, STP_CHD_L, STP_CHD_H)

def stepper(index, grau):
    if index < 1 or index > 2:
        print("No has seleccionat correctament el motor\n")
        print("Si us plau, indica quin motor stepper vols moure, 1 o 2\n")
        return

    setStepper(index, grau > 0)
    grau = abs(grau)
    sleep(8500 * grau / 360)
    stopMotors()

def stepperVoltes(index, voltes):
    graus = voltes * 360
    Stepper(index, graus)

def stopMotors():
    for i in range(1, 5, 1):
        set_pwm((i - 1) * 2, 0, 0)
        set_pwm((i - 1) * 2 + 1, 0, 0)
