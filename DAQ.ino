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

//in 16 bit mode, ADC has a conversion rate of 15437 Hz maxiumum
//size for each ADC channel convertion result buffer  
#define BUFFERSIZE 8196
//data buffer, MSB order
volatile uint8_t adc_data[4][BUFFERSIZE];
volatile bool buffer_full = false;

void setup() {
    Serial.begin(115200);

    dac.SetupAD5764(DAC_CS, DAC_LDAC, DAC_CLR);
    adc.SetupAD7734(ADC_CS, ADC_RDY, ADC_RST);

    dac.SetDataRegister(-5, DAC_A);
    adc.StartContinousConversion(ADC_A);

    attachInterrupt(digitalPinToInterrupt(ADC_RDY), Interrupt, FALLING);
}

void loop() {
    if (Serial.available() >= 16) {
        uint8_t data[16];
        Serial.readBytes(data, 16);

        uint8_t fnc = data[0] >> 4;

        switch (fnc) {
            case 0:
                //perform auto ramp up function
                Ramp(
                    data[0] >> 2 & 0x3, 
                    data[1] << 8 | data[2], 
                    data[3] << 8 | data[4], 
                    data[5] << 8 | data[6], 
                    data[7] << 24 | data[8] << 16 | data[9] << 8 | data[10]
                );

            break;

            case 1:
                //send data buffer to PC and mark as empty
                Serial.write((const uint8_t*)adc_data[ADC_A], BUFFERSIZE);
                buffer_full = false;
            break;

            default:
            break;
        }
    }

    if (buffer_full) {       
        buffer_full = false;
    }
}

void Interrupt() {
    //current indicies for each adc_data buffer
    static unsigned indices[4] = {0, 0, 0, 0};

    if (buffer_full)   
        return;

    //if adc_data buffer is full, dump it to the serial port, and reset the index
    if (indices[ADC_A] >= BUFFERSIZE) {
        indices[ADC_A] = 0; 
        buffer_full = true;
        return;
    }

    //currently using only 1 ADC channel (A)
    uint16_t data = adc.GetConversionData(ADC_A);
    adc_data[ADC_A][indices[ADC_A]++] = (uint8_t)(data >> 8);
    adc_data[ADC_A][indices[ADC_A]++] = (uint8_t)(data & 0x00FF);
}

/*
    Ramp function

    dac_channel: which channel the dac will output the ramp on

    vstart: starting voltage

    vstop: stopping voltage

    steps: how many steps will the ramp take to reach the final voltage

    duration: how long function take to complete (in microseconds)
*/

void Ramp(uint8_t dac_channel, uint16_t vstart, uint16_t vstop, uint16_t steps, uint32_t duration) {
    uint16_t dt = duration / (float)steps;
    int32_t dv = (vstop - vstart) / (float)steps;

    for (unsigned i = 0; i < steps; i++) {
        //set the start time of the timer
        unsigned long start = micros();
        //check if value will overflow, also add 10 microseconds to allow DAC output to settle 
        unsigned long stop = (start + dt + 10 < 0xFFFFFFFF) ? start + dt + 10 : dt - (0xFFFFFFFF - start) + 10;
        
        //increment DAC voltage up
        dac.SetDataRegister(vstart += dv, dac_channel);

        //wait until the correct number of microseconds has passed
        while (micros() < stop);
    }
}