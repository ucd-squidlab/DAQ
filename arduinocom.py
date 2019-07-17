import serial
import struct
import matplotlib
import matplotlib.pyplot as plt

should_close = False
ser = serial.Serial()

def Quit(args):
    global should_close
    should_close = True

def Help(args):
    print("\nAll commands are listed below:\n")
    print("setdac dac_channel voltage")
    print("adc adc_channel")

#bit map:
#   function    dac_channel     adc_channel     DATA
#       4           2               2            120

#function for converting a floating point value to a value usable by the DAC
def Float2Binary(f):
    return int((16384 * ((float(f)/5.0) + 2)))

#function for converting a two's complement number from the ADC to a usable floating point value
def Twos2Float(i):
    #resolution for 16 bit mode operation, the ADC resolution can take 2 values, 16 or 24 bit
    ADCRES16 = 65535.0
    
    #full scale range, can take 4 different values
    FSR = 20.0

    return (FSR * (i - (ADCRES16/2.0)) / ADCRES16) 

def SetDACChannel(args):
    #expected arguments: DAC channel(1), channel value(2)

    #function code: 0
    global ser

    if len(args) != 3: 
        print("Passed " + str(len(args)) + " arguments. Expected 3.")
        return



    #write serial data, forcing MSB first order 
    ser.write(bytearray([0 << 4 | int(args[1]) << 2]))
    ser.write(struct.pack('>H', Float2Binary(args[2])))
    #write 13 bytes of padding
    ser.write(13)

def StartADCConversion(args):
    #expected arguments: ADC channel(1)

    #function code: 1
    global ser

    if len(args) != 2:
        print("Passed " + str(len(args)) + " arguments. Expected 2.")
        return

    #write serial data, forcing MSB first order 
    ser.write(bytearray([1 << 4 | int(args[1])]))
    #write 15 bytes of padding
    ser.write(15)

def BiasMagnent():
    #need start, stop, number of points, max rate 
    
    return

#input dictionary
input_dictionary = {
    "Help" : Help,
    "help" : Help,
    "Quit" : Quit,
    "quit" : Quit,
    "stop" : Quit,
    "q"    : Quit,
    "setdac" : SetDACChannel,
    "adc" : StartADCConversion
}

def main():
    #setup and open serial port
    ser.baudrate = 115200
    ser.port = '/dev/tty.usbmodemfd141'
    ser.timeout = 1
    ser.open()

    while(should_close != True):
        if ser.in_waiting == 2:
            buff = ser.read(2)
            print(Twos2Float(buff[0] << 8 | buff[1]))
       
        #wait for user input 
        usr_input = input("\nWaiting for commands. Type \"Help\" for a list of commands.\n")

        #split user input using space delimiters
        split_inputs = usr_input.split()     

        #route user commands using dictionary
        try:
            input_dictionary[split_inputs[0]](split_inputs)
        except:
            print("Unknown command: " + "\"" + usr_input + "\"")

    #close serial port when program is finished 
    ser.close()

if __name__ == "__main__":
    main()