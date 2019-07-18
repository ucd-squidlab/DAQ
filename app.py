import wx
#import serial
import struct

"""class ArduinoComms():
    ser = serial.Serial()
    
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
"""
#panel which has manual control inputs 
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

        # voltage input for DAC outputs
        num1 = wx.TextCtrl(self)
        num2 = wx.TextCtrl(self)
        num3 = wx.TextCtrl(self)
        num4 = wx.SpinCtrl(self)
        num5 = wx.TextCtrl(self)

        # DAC selectors
        self.combo1 = wx.Choice(self, choices = ["DAC A", "DAC B", "DAC C", "DAC D"])
        self.combo2 = wx.Choice(self, choices = ["DAC A", "DAC B", "DAC C", "DAC D"])

        # button to set DAC output 
        btn1 = wx.Button(self, label="Set")                
        btn2 = wx.Button(self, label="Set")

        #progress bar for magnent setting
        self.bar1 = wx.Gauge(self, style=wx.GA_HORIZONTAL)

        # layout sizers

        #s1 is the root sizer 
        s1 = wx.BoxSizer(wx.VERTICAL)
        s1.Add(text1, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        s1.Add(wx.StaticLine(self, style=wx.LI_HORIZONTAL), proportion=0, flag=wx.EXPAND)
        s1.Add(text2, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        
        #s2 SQUID bias settings  
        s2 = wx.FlexGridSizer(rows=2, cols=2, vgap=8, hgap=5)
        s2.AddMany([
            (wx.StaticText(self, label="DAC"), 0, wx.ALIGN_CENTER), (text5, 0, wx.ALIGN_CENTER),
            (self.combo1, 0), (num1, 0, wx.EXPAND),
        ])

        s1.Add(s2, flag=wx.ALIGN_CENTER | wx.ALL, border=4)
        s1.Add(btn1, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border = 5)
        s1.Add(wx.StaticLine(self, style=wx.LI_HORIZONTAL), proportion=0, flag=wx.EXPAND)

        #s3 mangnent bias settings 
        s1.Add(text3, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        s3 = wx.FlexGridSizer(rows=2, cols=5, vgap=8, hgap=5)
        s3.AddMany([
            (wx.StaticText(self, label="DAC"), 0, wx.ALIGN_CENTER), (text6, 0, wx.ALIGN_CENTER), (text7, 0, wx.ALIGN_CENTER), (text8, 0, wx.ALIGN_CENTER), (text9, 0, wx.ALIGN_CENTER),
            (self.combo2, 0), (num2, 0), (num3, 0), (num4, 0), (num5, 0)
        ])

        s1.Add(s3, flag=wx.ALIGN_CENTER | wx.ALL, border=4)
        s1.Add(btn2, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        s1.Add(self.bar1, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL)

        self.SetSizer(s1)

        #bind input events
        num1.Bind(wx.EVT_CHAR, self.OnTextInput)
        num2.Bind(wx.EVT_CHAR, self.OnTextInput)
        num3.Bind(wx.EVT_CHAR, self.OnTextInput)
        num5.Bind(wx.EVT_CHAR, self.OnTextInput)

    def OnBiasSQUID(self, event):
        return
    
    def OnBiasMagnent(self, event):
        return

    def OnTextInput(self, event):
        key_code = event.GetKeyCode()

        if ord('0') <= key_code <= ord('9'):
            event.Skip()
            return
        
        if key_code == ord('\t'):
            event.Skip()
            return

        if key_code == ord('.'):
            event.Skip()
            return
        
        if key_code == ord('\b') or key_code == ord('\n') or key_code == ord('\r'):
            event.Skip()
            return

        return   

    def UpdateProgressBar(self, value):
        self.bar1.SetValue(value)

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

        #set frame sizers
        s1 = wx.BoxSizer(wx.HORIZONTAL)
        s1.Add(p1, proportion=0, flag=wx.EXPAND | wx.ALL)
        s1.Add(p2, proportion=0, flag = wx.EXPAND | wx.ALL)
        self.SetSizer(s1)

        #bind the close event to OnExit
        self.Bind(wx.EVT_CLOSE, self.OnExit)

    #on exit event, closes the frame and cleans up
    def OnExit(self, event):
        self.Destroy()

if (__name__ == '__main__'):
    app = wx.App()
    main_frame = Frame(None, title='DAQ Controller')
    main_frame.Show(True)
    app.MainLoop()