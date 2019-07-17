//DAC library header
#include <AD5764.h>
//ADC library header
#include <AD7734.h>
//Arduino SPI library header
#include "SPI.h"

//instance of the AD5764 class ( DAC )
AD5764 dac;
//instance of the AD7734 class ( ADC )
AD7734 adc;

//pins for adc and dac 
//DAC chip select pin 
#define DAC_CS 4
//DAC LDAC pin
#define DAC_LDAC 6
//DAC clear pin
#define DAC_CLR 5

//ADC chips select pin
#define ADC_CS 52
//ADC data ready pin
#define ADC_RDY 48
//ADC reset pin 
#define ADC_RST 44

//buffer size for ADC converstions
#define BUFFERSIZE 2
//ADC conversion data buffer
volatile uint8_t adc_data[4][BUFFERSIZE];
//goes true when data buffer is ready to be sent via serial 
volatile bool buffer_rdy = false;

void setup() {    
    //begin serial communication with a BAUD rate of 115200
    Serial.begin(115200);

    //setup the DAC (see the AD5764 library for details)
    dac.SetupAD5764(DAC_CS, DAC_LDAC, DAC_CLR);
    //setup the ADC (see the AD7734 library for details)
    adc.SetupAD7734(ADC_CS, ADC_RDY, ADC_RST);

    //attach an interrupt to the ADC_RDY pin, with ADCDataRdyISR as the handler on falling edge
    attachInterrupt(digitalPinToInterrupt(ADC_RDY), ADCDataRdyISR, FALLING);
}

void loop() {
    //wait for a valid 16 byte data stream to become available
    if (Serial.available() >= 16) {
        //read 16 bytes of serial data into a data buffer
        uint8_t data[16];
        Serial.readBytes(data, 16);

        //get function code (upper 4 bits from first data byte)
        uint8_t fnc = data[0] >> 4;

        //branch based on function code 
        switch (fnc) {
            case 0:
                //change the voltage on the passed DAC channel to the passed voltage 
                dac.SetDataRegister((data[1] << 8) | data[2], (data[0] >> 2) & 0x3);
            break;

            case 1:
            {
                //begin ADC conversion on the passed channels 
                adc.StartSingleConversion(data[0] & 0x3);
            }
            break;

            default:
            break;
        }
    }

    if (buffer_rdy) {
        //send data to PC
        Serial.write((uint8_t*)adc_data[ADC_A], 2);
        buffer_rdy = false;
    }
}

void ADCDataRdyISR() {
    if (buffer_rdy)
        return;
    
    //only using ADC_A for now
    static unsigned i = 0; 

    uint16_t data = adc.GetConversionData(ADC_A);

    //store the conversion data 
    adc_data[ADC_A][i++] = data >> 8;
    adc_data[ADC_A][i++] = data >> 0xF;

    if (i >= BUFFERSIZE) {
        buffer_rdy = true;
        i = 0;
    }
}