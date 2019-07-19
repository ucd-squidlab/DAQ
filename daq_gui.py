# this script can only be run on Mac using pythonw

import wx
import serial
import struct

# class for housing everything related to Arduino communcations 
class ArduinoComms():
    magnent_bias_progress = 0

    def __init__(self, baud_rate, port, timeout):
        # create instance of serial class
        self.ser = serial.Serial()
        
        # setup and open serial port
        self.ser.baudrate = baud_rate
        # port to open serial comms on 
        self.ser.port = port
        # port timeout ( in seconds )
        # self.ser.timeout = timeout
        self.ser.open()

        # cleanup incoming and outgoing bits
        self.ser.flushInput()
        self.ser.flushOutput()

    def __del__(self):
        # close serial port when ArduinoComms is destroyed 
        self.ser.close()

    # bit map:
    #   function    dac_channel     adc_channel     DATA
    #       4           2               2            120

    # function for converting a floating point value to a value usable by the DAC
    def Float2Binary(self, f):
        return int((16384 * ((float(f)/5.0) + 2)))

    # function for converting a two's complement number from the ADC to a usable floating point value
    def Twos2Float(self, i):
        #r esolution for 16 bit mode operation, the ADC resolution can take 2 values, 16 or 24 bit
        ADCRES16 = 65535.0
        
        #full scale range, can take 4 different values
        FSR = 20.0

        return (FSR * (i - (ADCRES16/2.0)) / ADCRES16) 

    # sets a DAC channel to output a value ( passed in Volts )
    def SetDACChannel(self, dac_channel, channel_value):
        # function code: 0

        # write serial data, forcing MSB first order 
        self.ser.write(bytearray([0 << 4 | int(dac_channel) << 2]))
        # pack data into the size of a 16 bit integer 
        self.ser.write(struct.pack('>H', self.Float2Binary(channel_value)))
        # write 13 bytes of padding
        self.ser.write(13)

    def StartADCConversion(self, adc_channel):
        # function code: 1

        # write serial data, forcing MSB first order 
        self.ser.write(bytearray([1 << 4 | int(adc_channel)]))
        # write 15 bytes of padding
        self.ser.write(15)

    def ReadADC(self, adc_channel):
        # function code: 2

        # write serial data, forcing MSB first order
        self.ser.write(bytearray([2 << 4 | int(adc_channel)]))
        #write 15 bytes of padding
        self.ser.write(15)

        # arduino will send back 2 bytes of data for the requested ADC covnersion, convert and return
        buff = self.ser.read(2)
        return self.Twos2Float(buff[0] << 8 | buff[1])

    def BiasMagnent(self, startv, stopv, points, max_rate):
        # need start, stop, number of points, max rate 
        
        return

# panel which has manual control inputs 
class ManualPanel(wx.Panel):
    def __init__(self, *args, **kw):
        #call initializer on base class 
        super(ManualPanel, self).__init__(*args, **kw)

        # GUI fields

        #static texts
        text1 = wx.StaticText(self, label="Manual Controls")
        text2 = wx.StaticText(self, label="SQUID Bias")
        text3 = wx.StaticText(self, label="Magnent Bias")
        text5 = wx.StaticText(self, label="Voltage (V)")
        text6 = wx.StaticText(self, label="Start Voltage (V)")
        text7 = wx.StaticText(self, label="Stop Voltage (V)")
        text8 = wx.StaticText(self, label="Steps")
        text9 = wx.StaticText(self, label="Max Rate (V/s)")

        # static text for ADC readings
        self.adc_0 = wx.StaticText(self, label="-")
        self.adc_1 = wx.StaticText(self, label="-")
        self.adc_2 = wx.StaticText(self, label="-")
        self.adc_3 = wx.StaticText(self, label="-")

        # voltage inputs
        self.num1 = wx.TextCtrl(self)
        self.num2 = wx.TextCtrl(self)
        self.num3 = wx.TextCtrl(self)
        self.num5 = wx.TextCtrl(self)
        
        #steps input for magnent bias 
        self.num4 = wx.SpinCtrl(self)

        # DAC selectors
        self.combo1 = wx.Choice(self, choices = ["DAC A", "DAC B", "DAC C", "DAC D"])
        self.combo2 = wx.Choice(self, choices = ["DAC A", "DAC B", "DAC C", "DAC D"])
        
        # buttons to apply DAC outputs 
        self.btn1 = wx.Button(self, label="Set")                
        self.btn2 = wx.Button(self, label="Set")
        self.btn3 = wx.Button(self, label="Read ADCs")

        # layout sizers

        # sizer 1 (s1) is the root sizer which will be applied to the panel  
        # a box sizer organizes GUI elements as boxes 
        s1 = wx.BoxSizer(wx.VERTICAL)
        # just adding some flavor text as a header 
        s1.Add(text1, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        s1.Add(wx.StaticLine(self, style=wx.LI_HORIZONTAL), proportion=0, flag=wx.EXPAND)
        s1.Add(text2, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        
        # s2 SQUID bias settings sizer

        # a FlexGridSizer is just a type of sizer that organizes items in a grid         
        s2 = wx.FlexGridSizer(rows=2, cols=2, vgap=8, hgap=5)
        s2.AddMany([
            (wx.StaticText(self, label="DAC"), 0, wx.ALIGN_CENTER), (text5, 0, wx.ALIGN_CENTER),
            (self.combo1, 0), (self.num1, 0, wx.EXPAND),
        ])

        # add sizer 2 (s2) to s1
        s1.Add(s2, flag=wx.ALIGN_CENTER | wx.ALL, border=4)
        # add button 1 to s1
        s1.Add(self.btn1, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        # add a pretty horizontal line for effect
        s1.Add(wx.StaticLine(self, style=wx.LI_HORIZONTAL), proportion=0, flag=wx.EXPAND)

        # s3 magnent bias settings sizer
        s1.Add(text3, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        s3 = wx.FlexGridSizer(rows=2, cols=5, vgap=8, hgap=5)
        # add GUI elements in a grid
        s3.AddMany([
            (wx.StaticText(self, label="DAC"), 0, wx.ALIGN_CENTER), (text6, 0, wx.ALIGN_CENTER), (text7, 0, wx.ALIGN_CENTER), (text9, 0, wx.ALIGN_CENTER), (text8, 0, wx.ALIGN_CENTER),
            (self.combo2, 0), (self.num2, 0), (self.num3, 0), (self.num5, 0), (self.num4, 0)
        ])

        # add sizer 3 to s1
        s1.Add(s3, flag=wx.ALIGN_CENTER | wx.ALL, border=4)
        # add button 2 to s1
        s1.Add(self.btn2, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        # once again, add a horizontal line for pretty factor
        s1.Add(wx.StaticLine(self, style=wx.LI_HORIZONTAL), proportion=0, flag=wx.EXPAND)

        # s4 ADC readings sizer
        s4 = wx.FlexGridSizer(rows=5, cols=2, vgap=8, hgap=5)
        # add text labels in a grid 
        s4.AddMany([
            (wx.StaticText(self, label="ADC"), 0, wx.ALIGN_CENTER), (wx.StaticText(self, label="Value (V)"), 0, wx.ALIGN_CENTER),
            (wx.StaticText(self, label="A"), 0, wx.ALIGN_CENTER), (self.adc_0, 0, wx.ALIGN_LEFT | wx.ALL),
            (wx.StaticText(self, label="B"), 0, wx.ALIGN_CENTER), (self.adc_1, 0, wx.ALIGN_LEFT | wx.ALL),
            (wx.StaticText(self, label="C"), 0, wx.ALIGN_CENTER), (self.adc_2, 0, wx.ALIGN_LEFT | wx.ALL),
            (wx.StaticText(self, label="D"), 0, wx.ALIGN_CENTER), (self.adc_3, 0, wx.ALIGN_LEFT | wx.ALL)
        ])

        # add s4 to s1
        s1.Add(s4, flag=wx.ALIGN_CENTER | wx.ALL, border=4)
        # add button 3 to s1 
        s1.Add(self.btn3, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        # apply sizer to panel 
        self.SetSizer(s1)

        # bind input events
        self.num1.Bind(wx.EVT_CHAR, self.OnTextInput)
        self.num2.Bind(wx.EVT_CHAR, self.OnTextInput)
        self.num3.Bind(wx.EVT_CHAR, self.OnTextInput)
        self.num5.Bind(wx.EVT_CHAR, self.OnTextInput)
        
        self.btn1.Bind(wx.EVT_BUTTON, self.OnBiasSQUID)
        self.btn2.Bind(wx.EVT_BUTTON, self.OnBiasMagnent)
        self.btn3.Bind(wx.EVT_BUTTON, self.OnReadADCs)

    # event handles when button 3 (btn3) is pressed 
    def OnReadADCs(self, event):
        global arduino

        # disable the button while read happens
        self.btn3.Disable()

        # read all 4 ADCs
        # while the ADC do take time to convert their data, the Serial communciation is slow enough that this is not a problem
        arduino.StartADCConversion(0)
        arduino.StartADCConversion(1)
        arduino.StartADCConversion(2)
        arduino.StartADCConversion(3)
        
        # read ADC data
        self.adc_0.SetLabel(str(arduino.ReadADC(0)))
        self.adc_1.SetLabel(str(arduino.ReadADC(1)))
        self.adc_2.SetLabel(str(arduino.ReadADC(2)))
        self.adc_3.SetLabel(str(arduino.ReadADC(3)))
        
        # read is finished, re-enable button
        self.btn3.Enable()

    # event hanels event when button 1 (btn1) is pressed 
    def OnBiasSQUID(self, event):
        # get field values from GUI ( fields located in sizer 2 ) and set the DAC output
        global arduino

        # GetSelection returns the index of the selection, which in this case works find
        # get the value from the num1 field, and parse it into a float
        arduino.SetDACChannel(self.combo1.GetSelection(), float(self.num1.GetLineText(0)))

        return
    
    # event for handeling when button 2 is pressed
    def OnBiasMagnent(self, event):
        # if pressed, disable button and place a progress bar in its place
        self.btn2.Disable()
        
        # will probably need to use threading to allow for program remaining responsive while this operation occurs 

        self.btn2.Enable()
        
        return

    def OnTextInput(self, event):
        # this controls the text entry fields, allowing only numeric values to be passed
        # get keycode from key event 
        key_code = event.GetKeyCode()

        # check the following keycodes, if they are allowed, skip the event, otherwise return
        # by skipping the event, we are allowing the input to be passed through and input into the box
        # we do this so we can filter out all non numeric symbols 
         
        if ord('0') <= key_code <= ord('9'):
            event.Skip()
            return
        
        if key_code == ord('\t') or key_code == ord('\b') or key_code == ord('\n') or key_code == ord('\r'):
            event.Skip()
            return

        if key_code == ord('.') or key_code == ord('-'):
            event.Skip()
            return

        return   

# panel which houses automated control inputs 
class AutomatedPanel(wx.Panel):
    def __init__(self, *args, **kw):
        super(AutomatedPanel, self).__init__(*args, **kw)

        # GUI fields

        # static texts
        text1 = wx.StaticText(self, label="Automatic Controls")

        # s1 is the root sizer 
        s1 = wx.BoxSizer(wx.VERTICAL)
        s1.Add(text1, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=10)        
        s1.Add(wx.StaticLine(self, style=wx.LI_HORIZONTAL), proportion=0, flag=wx.EXPAND)

        self.SetSizer(s1)

class Frame(wx.Frame):
    def __init__(self, *args, **kw):
        #call the initializer for the base class
        super(Frame, self).__init__(*args, **kw)

        # add panels for GUI items here
        p1 = ManualPanel(self)
        p2 = AutomatedPanel(self)

        # set frame sizers
        s1 = wx.BoxSizer(wx.HORIZONTAL)
        s1.Add(p1, proportion=0, flag=wx.EXPAND | wx.ALL)
        s1.Add(p2, proportion=0, flag = wx.EXPAND | wx.ALL)
        self.SetSizer(s1)

        # bind the close event to OnExit, close event is pressing the close button on the window frame 
        self.Bind(wx.EVT_CLOSE, self.OnExit)

    # on close event, closes the frame and cleans up
    def OnExit(self, event):
        self.Destroy()

# create an instance of ArduinoComms to handle input with the Arduino specifically 
arduino = ArduinoComms(115200, '/dev/tty.usbmodemfd141', 1)

if (__name__ == '__main__'):
    # create a wxPython applicatoin
    app = wx.App()
    # create wxPython main frame 
    main_frame = Frame(None, title='DAQ Controller', size=(800,600))
    # show the frame 
    main_frame.Show(True)

    #start a thread to handle serial communication for the Arduino


    #enter App main loop
    app.MainLoop()