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
    print("RampUp dac_channel vstart vstop steps duration")
    print("RampDown dac_channel vstart vstop steps duration")

#bit map:
#   function    dac_channel     adc_channel     DATA
#       4           2               2            120

#function for converting a floating point value to a value usable by the DAC
def Float2Binary(f):
    return int((16384 * ((float(f)/5.0) + 2)))

#function for converting a two's complement number from the ADC to a usable floating point value
def Twos2Float(i):
    #resolution for 16 bit mode operation, the ADC resolution can take 2 values, 16 or 24 bit
    ADCRES16 = 65536.0
    
    #full scale range, can take 4 different values
    FSR = 20.0

    return (FSR * (i - (ADCRES16/2.0)) / ADCRES16) 

#instructs the Arduino to perform a ramp function
#   args: vstart, vstop, steps, duration 
def Ramp(args):
    #function id: 0
    global ser

    #check for correct number of args
    if len(args) != 6:
        print("Incorrect number of arguments (" + str(len(args)) + "). Expected 6.")
        return

    #   bit map (first byte excluded)
    #   vstart  vstop  steps  duration
    #     16      16    16      32


    #write data to serial, forcing MSB order  
    ser.write(bytearray([0 << 4 | int(args[1]) << 2]))
    ser.write(struct.pack('>H', Float2Binary(args[2])))
    ser.write(struct.pack('>H', Float2Binary(args[3])))
    ser.write(struct.pack('>H', int(args[4])))
    ser.write(struct.pack('>L', int(args[5])))
    
    #5 padding bytes to reach 16 bytes 
    ser.write(5)

    return

#instructs the Arduino to send its data buffer over serial com
#   args: null
def RequestData(args):
    #funciton id: 1
    global ser

    #write data to serial
    ser.write(bytearray([1 << 4]))
    #15 padding bytes to reach 16 bytes 
    ser.write(15)

    #read incoming data

    buffer = ser.read(4096)

    #the contents of the buffer are uint16_t separated into bytes in MSB
    #iterate over contents and convert to ints
    
    data = []

    for i in range(0, len(buffer), 2):
        data.append(Twos2Float(buffer[i] << 8 | buffer[i+1]))

    #dump data to text file 
    f = open("data.txt", "w")

    for i in data:
        f.write(str(i) + "\n")

    f.close()

    return

#input dictionary
input_dictionary = {
    "Help" : Help,
    "help" : Help,
    "Quit" : Quit,
    "quit" : Quit,
    "stop" : Quit,
    "q" : Quit,
    "Ramp" : Ramp,
    "ramp" : Ramp,
    "GetData" : RequestData,
    "getdata" : RequestData
}

def main():
    #setup and open serial port
    ser.baudrate = 115200
    ser.port = '/dev/tty.usbmodemfd141'
    ser.timeout = 1
    ser.open()

    while(should_close != True):
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