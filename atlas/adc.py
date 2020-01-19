
import spidev

class ADC(object):
    def __init__(self):
        self.spi = spidev.SpiDev()
        self.spi.open(0,0)   
    def getValue(self, channel=0):
        self.spi.max_speed_hz = 1350000
        adc = self.spi.xfer2([1,(8+channel)<<4,0])
        output = ((adc[1]&3) << 8) + adc[2]
        return output

if __name__=="__main__":
    from time import sleep
    adc = ADC()
    while 1:
        print(adc.getValue())
        sleep(0.002)

