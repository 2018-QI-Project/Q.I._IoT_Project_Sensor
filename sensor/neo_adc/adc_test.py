from neo_adc import ADC

# initialize the ADC class with pin A0
pin = 0
adc = ADC(pin)

raw = adc.get_raw()
mV = adc.get_mvolts()

print """Pin:	{0}
Raw:	{1}
mV:	{2}""".format(pin, raw, round(mV, 2))
