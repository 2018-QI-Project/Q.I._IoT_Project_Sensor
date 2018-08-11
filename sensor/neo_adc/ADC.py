class ADC:
    adc_files = (
	"/sys/bus/iio/devices/iio:device0/in_voltage0_raw", # A0 (ADC1)
	"/sys/bus/iio/devices/iio:device0/in_voltage1_raw", # A1 (ADC1)
	"/sys/bus/iio/devices/iio:device0/in_voltage2_raw", # A2 (ADC1)
	"/sys/bus/iio/devices/iio:device0/in_voltage3_raw", # A3 (ADC1)
	"/sys/bus/iio/devices/iio:device1/in_voltage0_raw", # A4 (ADC2)
	"/sys/bus/iio/devices/iio:device1/in_voltage1_raw"  # A5 (ADC2)
    )
    scale_files = (
	"/sys/bus/iio/devices/iio:device0/in_voltage_scale", # ADC1
	"/sys/bus/iio/devices/iio:device1/in_voltage_scale"  # ADC2
    )

    def __init__(self, pin):
	self.pin = int(pin)

    def get_raw(self):
	"Returns the raw, unscaled ADC value from 0 to 4095."

	try:
	    # obtain Location of the ADC file based on initialized pin
	    adc_file = ADC.adc_files[self.pin]

	    #open and read the ADC file, then we'll return the value
	    with open(adc_file) as adc:
	        adc_value = adc.read().replace("\n","")
	        return int(adc_value)
	except Exception as e:
            print "ERROR (get_raw): {0}".format(repr(e))
	    return -1

    def get_mvolts(self):
	"Returns the voltage (in mV) read by the ADC, from 0.0 to 3300.0"

	try:
	    adc_num = 1 if self.pin > 3 else 0
	    scale_file_path = ADC.scale_files[adc_num]

	    raw = self.get_raw()

	    scale = 0.
	    with open(scale_file_path) as scale_file:
		scale =float(scale_file.read().replace("\n",""))

	    return raw*scale
	except Exception as e:
	    print "ERROR (get_molts): {0}".format(repr(e))
	    return -1
