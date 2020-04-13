
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
    def __get__(self, instance, owner):
        return list(map(lambda x: self.getValue(x), range(8)))

if __name__=="__main__":
    from time import sleep
    adc = ADC()
    bellmin = 488
    bellmax = 527
    while 1:
        bell = adc.getValue(1)
        changed = False
        if bell < bellmin: 
            bellmin = bell
            changed = True
        if bell > bellmax:
            bellmax = bell
            changed = True
        if changed:
            print("bellmin:{} bellmax:{}".format(bellmin, bellmax))
        out = "".join(["ch{}:{}\t".format(x, adc.getValue(x)) for x in range(8)])
        # print(out)
        sleep(0.002)

