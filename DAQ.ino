#include <AD5764.h>
#include <AD7734.h>

#include "SPI.h"

AD5764 dac;
AD7734 adc;

//pins for adc and dac 
#define DAC_CS 4
#define DAC_LDAC 6
#define DAC_CLR 5

#define ADC_CS 52
#define ADC_RDY 48
#define ADC_RST 44

#define AUTORAMP_STEPS 100
#define AUTORAMP_DURATION 100000

volatile double autoramp_data[4][AUTORAMP_STEPS];

void setup() {
    Serial.begin(9600);

    dac.SetupAD5764(DAC_CS, DAC_LDAC, DAC_CLR);
    adc.SetupAD7734(ADC_CS, ADC_RDY, ADC_RST);

    dac.SetDataRegister(-5, DAC_A);
    adc.StartContinousConversion(ADC_A);

    attachInterrupt(digitalPinToInterrupt(ADC_RDY), Interrupt, FALLING);
}

void loop() {
    AutoRampUp(DAC_A, ADC_A, 0, 2, 100, 100000);
    //delay(100);
    //for (int i = 0; i < AUTORAMP_STEPS; i++)
    //    Serial.println(autoramp_data[0][i]);
}

void Interrupt() {
    static int i = 0;

    autoramp_data[0][i++] = adc.GetConversionData(ADC_A);
    i = i >= AUTORAMP_STEPS ? 0 : i;
}

/*
    AutoRamp functions

    AutoRampUp: performs a ramp function with a positive slope
    AutoRampDown: performs a ramp function with a negative slope
    AutoRampUpDown: performs a ramp function with positive slope, followed immediately by a ramp function with negative slope 

    Parameters:
    dac_channel: which channel the dac will output on

    adc_channel: which channel the adc will output on 

    vstart: defines the starting voltage of the ramp, for AutoRampUp, this will be the lower voltage, for AutoRampDown the higher voltage, 
    and for AutoRampUpDown, this will be the lower voltage

    vstop: defines the stopping voltage of the ramp functions

    steps: how many steps will the ramp take to reach the final voltage

    duration: how long will the function take to complete (in microseconds)

    Notes:
    These functions use software delays to time the function. Because of this, setting too many steps for a given time will result in 
    inaccurate function duration. Similarly, setting the duration too short will also result in inaccurate function duration. 
*/

void AutoRampUp(uint8_t dac_channel, uint8_t adc_channel, double vstart, double vstop, unsigned steps, double duration) {
    double dt = duration / steps;
    double dv = (vstop - vstart) / steps;

    for (unsigned i = 0; i < steps; i++) {
        //set the start time of the timer
        unsigned long start = micros();
        //check if value will overflow, also add 10 microseconds to allow DAC output to settle 
        unsigned long stop = (start + dt + 10 < 0xFFFFFFFF) ? start + dt + 10 : dt - (0xFFFFFFFF - start) + 10;
        
        //increment DAC voltage up
        dac.SetDataRegister(vstart + (dv * i), dac_channel);
        adc.StartSingleConversion(adc_channel);

        //while (digitalRead(ADC_RDY));
        
        // Serial.print("Voltage: ");
        // Serial.print(vstart + (dv * i), 5);
        // Serial.print("    ADC: ");
        // Serial.print(ADC2FLOAT(adc.GetConversionData(ADC_A)), 5);
        // Serial.print("\n");

        //wait until the correct number of microseconds has passed
        while (micros() < stop);
    }
}

void AutoRampDown(uint8_t dac_channel, uint8_t adc_channel, double vstart, double vstop, unsigned steps, double duration) {
    double dt = duration / steps;
    double dv = (vstart - vstop) / steps;

    for (unsigned i = 0; i < steps; i++) {
        //set the start time of the timer
        unsigned long start = micros();
        //check if value will overflow, also add 10 microseconds to allow DAC output to settle 
        unsigned long stop = (start + dt + 10 < 0xFFFFFFFF) ? start + dt + 10 : dt - (0xFFFFFFFF - start) + 10;
        
        //increment DAC voltage down
        dac.SetDataRegister(vstart - (dv * i), dac_channel);
        adc.StartSingleConversion(adc_channel);

        while (digitalRead(ADC_RDY));
        
        // Serial.print("Voltage: ");
        // Serial.print(vstart - (dv * i), 5);
        // Serial.print("    ADC: ");
        // Serial.print(ADC2FLOAT(adc.GetConversionData(ADC_A)), 5);
        // Serial.print("\n");

        //wait until the correct number of microseconds has passed
        while (micros() < stop);
    }
}

void AutoRampUpDown(uint8_t dac_channel, uint8_t adc_channel, double vstart, double vstop, unsigned steps, double duration) {
    AutoRampUp(dac_channel, adc_channel, vstart, vstop, steps/2, duration/2.0);
    AutoRampDown(dac_channel, adc_channel, vstop, vstart, steps/2, duration/2.0);
}