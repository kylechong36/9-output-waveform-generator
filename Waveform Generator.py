# Code that will be used for the waveform generator that will be used at
# Kairospace. The code will have adjustable amplitude, DC offset, frequency and waveform.
# This will have a Raspberry pi3 controlling an AD9833BRMZ by SPI interface
# It will also feature external parameters (amplitude, DC offset) controlled by the Raspberry PI.
# *ControlRegister might only work if put at the end of the code testing required
# Code last edited June 22nd 2023

# libraries used for coding

# spidev enables coding SPI on the Raspberry PI 
import spidev

# RPI.GPIO enables coding the pin I/O for the Raspberry Pi
import RPi.GPIO as GPIO

import time

import math

# Enables SPI
spi = spidev.SpiDev()

# Open spi port 0, device 1 
spi.open(0, 1)

# Setting SPI speed
spi.max_speed_hz = 500000

# Setting SPI clock polarity and clock phase
spi.mode = 0

# Setting global variables
controlRegister = 0x0000

# Crystal Oscillator constant input
mclk = 24*10000000

# Control word write
cont = 0x2000

# Bit 13 to 0 to end the frequency calculation
end = 0xDFFF

# Frequency registers
freq0 = 0x4000
freq1 = 0x8000

# Defining the pins of the Raspberry Pi 3
GPIO.setmode(GPIO.BOARD)

DC1 = 16

DC2 = 18

AMP1 = 11

AMP2 = 13

AMP3 = 15

# Setting the pins I/O status
GPIO.setup(DC1, GPIO.OUT)
GPIO.setup(DC2, GPIO.OUT)
GPIO.setup(AMP1, GPIO.OUT)
GPIO.setup(AMP2, GPIO.OUT)
GPIO.setup(AMP3, GPIO.OUT)

print('Configuring Waveform Generator\n')


# Removing white spaces in strings
def remove(string):

    return string.replace(" ", "")

# Lowercasing inputs for validation
def lower(string):
    
    return string.lower()

# Case function for waveform
def wave_switch(wave):

    # Coding AD9883BRMZ to output square waveform
    if wave == 'squ':
        controlRegister &= 0xFFFD
        controlRegister |= 0x0020
        spi.xfer(controlRegister)
    
        # Coding AD9883BRMZ to output sin waveform
    elif wave == 'sin':
        controlRegister &= 0xFFDD
        spi.xfer(controlRegister)
    
        # Coding AD9883BRMZ to output tri waveform
    elif wave == 'tri':
        controlRegister &= 0xFFDF
        controlRegister |= 0x0002
        spi.xfer(controlRegister)
        
    print('selected waveform is ' + wave)

# Frequency is not 1 to 1 to input so we need to do some calculations
# Frequency calculation might need to be done first
def frequency_calc(freq):
    
    # To get desired frequency output we have to calculate the frequency register
    freq_reg = (freq *pow(2,28))/mclk
    hex_freq1 = int(freq_reg)
    
    # This seperates bytes to a high and low value to be written
    high,low = hex_freq1 >> 14, hex_freq1 & 0x0003FFF
    
    # These are the two 14 bit registers created
    high = hex(high)
    low = hex(low)
    
    # Converting them to strings
    high = str(high)
    low = str(low)
    
    # Removing the 0x to pad with 0s
    high = high.replace('0x', '')
    low = low.replace('0x','')
    
    # Padding program
    high = high.rjust(4, '0')
    low = low.rjust(4, '0')
    
    # Readding 0s
    high = high.rjust(5, 'x')
    high = high.rjust(6, '0')
    
    low = low.rjust(5, 'x')
    low = low.rjust(6, '0')
    
    # This sets the microcontroller to "write" mode
    controlRegister |= cont
    spi.xfer(controlRegister)
    
    # Sends the "high" code to be written in the frequency
    time.sleep(.01)
    spi.xfer(high)
    
    # Sends the "low" code to be changed in the frequency
    time.sleep(.01)
    spi.xfer(low)
    
    # Sets bit 13 back to 0 to end the frequency adjustment
    controlRegister &= end
    spi.xfer(controlRegister)

# Case function for amplitude
def amp_switch(amp):

    #Setting the amplitude of the waveform generator with inputted amplitude
        
    if amp == 0.0:
            
        GPIO.output(AMP1,GPIO.LOW)
        GPIO.output(AMP2,GPIO.LOW)
        GPIO.output(AMP3,GPIO.LOW)
            
    elif amp == 0.5:

        GPIO.output(AMP1,GPIO.LOW)
        GPIO.output(AMP2,GPIO.LOW)
        GPIO.output(AMP3,GPIO.HIGH)
            
    elif amp == 1.0:
            
        GPIO.output(AMP1,GPIO.LOW)
        GPIO.output(AMP2,GPIO.HIGH)
        GPIO.output(AMP3,GPIO.LOW)
            
    elif amp == 1.5:
            
        GPIO.output(AMP1,GPIO.LOW)
        GPIO.output(AMP2,GPIO.HIGH)
        GPIO.output(AMP3,GPIO.HIGH)
            
    elif amp == 2.0:
            
        GPIO.output(AMP1,GPIO.HIGH)
        GPIO.output(AMP2,GPIO.LOW)
        GPIO.output(AMP3,GPIO.LOW)
        
    elif amp == 2.5:
            
        GPIO.output(AMP1,GPIO.HIGH)
        GPIO.output(AMP2,GPIO.LOW)
        GPIO.output(AMP3,GPIO.HIGH)
            
    elif amp == 3.0:
            
        GPIO.output(AMP1,GPIO.HIGH)
        GPIO.output(AMP2,GPIO.HIGH)
        GPIO.output(AMP3,GPIO.LOW)
            
    elif amp == 3.5:
            
        GPIO.output(AMP1,GPIO.HIGH)
        GPIO.output(AMP2,GPIO.HIGH)
        GPIO.output(AMP3,GPIO.HIGH)
        
    print('Selected amplitude is ' + amp)

# Case function for switch
def off_switch(off):

    # Setting offset of the waveform generator with inputted offset
        
    if off == 0:
            
        GPIO.output(DC1,GPIO.LOW)
        GPIO.output(DC2,GPIO.LOW)
            
    elif off == 1:
            
        GPIO.output(DC1,GPIO.LOW)
        GPIO.output(DC2,GPIO.HIGH)
            
    elif off == 2:
            
        GPIO.output(DC1,GPIO.HIGH)
        GPIO.output(DC2,GPIO.LOW)
            
    elif off == 3:
            
        GPIO.output(DC1,GPIO.HIGH)
        GPIO.output(DC2,GPIO.HIGH)
        
    print('Selected offset is ' + off)

# Function to change waveform

def waveform_conf():
    # Prompting user for desired waveform
    print('Enter desired waveform')
    waveform = input('squ = Square, sin = Sine, tri = Triangle\n')
    lower(waveform)

    # input validation
    while (waveform != 'squ' or waveform!= 'sin' or waveform!= 'tri'):
        print('Error, Invalid input')
        waveform = input('squ = Square, sin = Sine, tri = Triangle\n')
    
    wave_switch(waveform)

# Function to change Frequency
def frequency_conf():
    
    # Prompting user for desired frequency
    print('Enter desired frequency')
    print ('Frequency range is between 0-10 mhZ\n')
    frequency = input('hz = 1, khz = 10^3, mhz = 10^6\n')
    lower(frequency)
    
    #Converting the Hz to its respective int value
    frequency = remove(frequency)

    # Checking length of frequency
    length = int(len(frequency))

    # This convers kHz to Hz
    if 'khz' in frequency:
    
        if length == 6:
            frequency = frequency[0] + frequency[1] + frequency[2]
        
        elif length == 5:
            frequency = frequency[0] + frequency[1]
        
        elif length == 4:
            frequency = frequency[0]
        
        value = int(frequency)
        frequency = value * 1000
    
    # This converts MHz to hz
    elif 'mhz' in frequency:
    
        if length == 6:
            frequency = frequency[0] + frequency[1] + frequency[2]
        
        elif length == 5:
            frequency = frequency[0] + frequency[1]
        
        elif length == 4:
            frequency = frequency[0]
        
        value = int(frequency)
        frequency = value * 1000000
        
    # This is just the Hz value
    else:
    
        if length == 5:
            frequency = frequency[0] + frequency[1] + frequency[2]
        
        elif length == 4:
            frequency = frequency[0] + frequency[1]
        
        elif length == 3:
            frequency = frequency[0]
        
        value = int(frequency)
        frequency = value
    
    # input validation
    while (0 > frequency or frequency > 10000000):
        print('Error, Invalid input')
        frequency = input('Frequency range is between 0-10 MHZ\n')
        frequency = int(frequency)
        frequency_conf()
    print('Selected frequency is ' + frequency)    
    frequency_calc(frequency)

# Function to change amplitude
def amplitude_conf():
    # Prompting user for desired amplitude
    print('Enter desired amplitude')
    
    amplitude = input('Amplitude range is between 0-3.5V\n')
    amplitude = float(amplitude)
    
    # input vaidation
    while (0 < amplitude or amplitude > 3.5):
        print('Error, Invalid input')
        amplitude = input('Amplitude range is between 0-3.5V\n')
        amplitude = float(amplitude)
        
    amp_switch(amplitude)

# Function to change offset
def offset_conf():
    # Prompting user for desired DC offset
    print('Enter desired Offset')
    offset = input('Offset range is between 0-3V\n')
    offset = float(offset)
    
    # input validatin
    while (0 < offset or offset > 3):
        print('Error, Invalid input')
        offset = input('Offset range is between 0-3V\n')
        offset = float(offset)
        
    off_switch(offset)

# Function to reset the waveform generator
def reset_conf():
    
    controlRegister &= 0xF1FF
    spi.xfer(controlRegister)
    
# Function to turn of the waveform generator
def end_conf():

    controlRegister |= 0x00C0
    spi.xfer(controlRegister)

# On startup calls the functions
waveform_conf()
frequency_conf()
amplitude_conf()
offset_conf()

#Prompting user if they would like to change any settings
i = 1

while i == 1:

    print('Would you like to change any settings?')
    print('1. Waveform')
    print('2. Frequency')
    print('3. Amplitude')
    print('4. Offset')
    print('5. Reset')
    status = input('6. End\n')
    
    status = int(status)
    
    # input validation
    while (0 > status or status > 6):
            
        print('Error, Invalid input')
        print('Would you like to change any settings?')
        print('1. Waveform')
        print('2. Frequency')
        print('3. Amplitude')
        print('4. Offset')
        print('5. Reset')
        status = input('6. End\n')
    
    # Based on which value is chosen it directs user back to the respective change
    if status == 1:
        waveform_conf()
        
    elif status == 2:
        frequency_conf()
        
    elif status == 3:
        amplitude_conf()
        
    elif status == 4:
        offset_conf()
        
    elif status == 5:
        reset_conf()
        
    elif status == 6:
        end_conf()
        i = i - 1
        print('Waveform Generator Shutting Down')