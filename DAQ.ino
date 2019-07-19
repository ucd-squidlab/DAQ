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

    //if Serial.available() % 16 != 0 after a communication is completed, then the Arduino will not process
    //the bitstream properly, the fastest way to fix this is a restart, the input stream can also be flushed with data
    //until Serial.available() % 16 == 0.
    
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
                //begin ADC conversion on the passed channels 
                adc.StartSingleConversion(data[0] & 0x3);
            break;

            case 2:
                //write back the requested ADC conversion data 
                Serial.write((uint8_t*)(adc_data[data[0] & 0x3]), 2);
            default:
            break;
        }
    }
}

//when data is ready, the ADC_RDY pin goes low, triggering this interrupt
void ADCDataRdyISR() {    
    //disable interrupts on ADC_RDY to prevent thrashing 
    detachInterrupt(digitalPinToInterrupt(ADC_RDY));

    //temporary value to store returned ADC data
    uint16_t data = 0;

    for (int i = 0; i < 4; i++) {
        //get ADC data
        data = adc.GetConversionData(i);
            
        //store the conversion data 
        //move upper half of word to lower byte
        adc_data[i][0] = data >> 8;
        //remove upper half of word
        adc_data[i][1] = data & 0xFF;
    }

    //re-enable interrupts
    attachInterrupt(digitalPinToInterrupt(ADC_RDY), ADCDataRdyISR, FALLING);
}