# UCD DAQ Project
Host repository for the DAQ project at CU Denver. 

The DAQ is a combination of an Arduino, DAC, and ADC. 

## Libraries
This project uses the AD5764 and AD7734 libraries which can be found at https://www.github.com/ucd-squidlab/AD5764Lib and https://www.github.com/ucd-squidlab/AD7734Lib.
To use these libraries, they must be cloned in the libraries directory located in the Arduino root folder. Then in the Arduino IDE, the library can be included by going to Sketch->Include Library->Contributed Librares->"Your Library". 

## Overview 
Included in the project is the DAQ.ino Arduino sketch, as well as two Python scripts.

The purpose of the Python scripts is to take user input and communicate with the Arduino via a serial interface, thus controlling the DAQ. This is done by sending commands over serial which are then decoded on the Arduino and the corresponding function is exectued. The Arduino serves the purpose of managing the DAC and ADC through SPI, and to perform rudementary functions like setting DAC outputs and starting and reading ADC conversions. Special functions like ramps, data processing, or experiments should be handled by the Python scripts.   

The bytestream used for communcation with the Arduino is 16 bytes wide. The top byte is a header containing the function code, DAC channel, and ADC channel. The remaining 15 bytes are used for data. All data sent to the Arduino should be send in MSB order. Shown in the table below is the data layout. 

|Bit 7-4|Bit 3-2|Bit 1-0|DB[14]-DB[0]|
|:---:|:---:|:---:|:---:|
|Funciton Code|DAC Ch.|ADC Ch.|DATA|

The following are the currently supported functions:
* Set DAC (code = 0)
* Start ADC Conversion (code = 1)
* Get ADC Data (code = 2)

Notes:
* It is important that an entire 16 byte data stream is sent to the Arduino. While the Arduino will not hang if it does not receive the expected number of bytes, its behaviour will be unpredictable. For this reason, padding bytes may need to be added to the bitsteam. 
* All data sent to the Arduino MUST be in MSB first order. 

### Arduino Code Structure
The Arduino code consists of 3 main functions/sections:
* setup
* loop
* ADCDataRdyISR

The "setup" function (and the lines above it) simply sets up the Arduino to work with its peripherals (the ADC and DAC). 

The "loop" function is exectued forever. Its purpose is to process incoming commands from serial, and route them to the corresponding function. This is done by stripping the function code from the byte string and using it as the argument for a switch-case statement. 

The "ADCDataRdyISR" is an interrupt service routine (ISR). It is triggered on the falling edge of the ADC ready pin (which transitions from high to low when ADC conversion data is ready). This function then fetches the ADC conversion data from all channels, and stores it in a buffer. This buffer can be requested per ADC channel via a serial command.  

The Arduino has two peripherals: 
* ADC (AD7734) (datasheet: https://www.analog.com/media/en/technical-documentation/data-sheets/AD7734.pdf)
* DAC (AD5764) (datasheet: https://www.analog.com/media/en/technical-documentation/data-sheets/AD5764.pdf)

The Arduino communicates with these peripherals using SPI (see code and data sheets for more information)

### Python Code

If the DAQ is not connected to the PC, or the wrong port is specified, the Python scripts will fail to start. 

daq_terminal.py is a command line script used for controlling the DAQ via a serial interface. daq_gui.py is a graphical version of this script, built using wxPython (docs: https://wxpython.org/Phoenix/docs/html/). 
Notes:
* daq_gui.py must be run using the command line argument "pythonw daq_gui.py" on Mac, arduinocom.py can be run using "python daq_terminal.py"
* The serial port for the Arduino may not be the same on all computers. On Mac, use the command line arugment "ls /dev/*" to find what port the Arduino is on, then change the port in the Python files.

#### daq_terminal
The "main" function of daq_terminal serves the purpose of setting up serial communcation, and taking user commands via the command line. Seen in the file is a dictionary of valid commands, which are then paired with the corresponding function. This function is then called with an arguments list, some of which will communicate with the Arduino over serial.  

#### daq_gui
This script begins towards the bottom with the "if (__name__ == '__main__')". Here, a wxPython application is created, the main window frame is created, the main window frame is shown, and the application main loop is entered. Just above this, an instance of the "ArduinoComms" class is created, which handles communciations with the Arduino specifically.

When the main frame is being created, it creates two panels inside of it, which house the controls for manual and automated opeations. These panels are added to a sizer, which is wxPython's method for handeling window layouts, and the sizer is then applied to the frame. Then the exit event is found, which allows the application to be closed. 

The panels are organized using classes. For example, all controls that exist in the manual controls panel, exist in the class "ManualPanel". Additionally, each instrument that requires its own communcations setup should have an associated class designed for communcating with that instruments (e.g. ArduinoComms). 

The panels follow a similar process in creation as the main frame. All GUI items, such as buttons and text fields, are created on the class initialization. GUI items are then added to sizers to organize their layouts on screen. The sizers are then applied to the panel, and the events such as button presses or text inputs are bound. 

Once all frames and panels are created, the user will then be ableto interact with the GUI. The Python application will perform serial communciation with the Arduino when necesary. 