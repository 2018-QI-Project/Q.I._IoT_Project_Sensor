import sqlite3
from neo import easyGpio
from neo_adc import ADC
from threading import Thread
from threading import Lock
from time import sleep, time
import datetime

# aqi calculation range
aqi_index = [[0, 51, 101, 151, 201, 301, 401],[50, 100, 150, 200, 300, 400, 500]]
o3_8 = [[0, 55, 71, 86, 106], [54, 70, 85, 105, 200]] # ppb
o3_1 = [[-1, -1, 125, 165, 205, 405, 505], [-1, -1, 164, 204, 404, 504, 604]] # ppb
pm25_24 = [[0, 12.1, 35.5, 55.5, 150.5, 250.5, 350.5],[12.0, 35.4, 55.4, 150.4, 250.4, 350.4, 500.4]] # ug/m3
co_8 = [[1, 4.5, 9.5, 12.5, 15.5, 30.5, 40.5],[4.4, 9.4, 12.4, 15.4, 30.4, 40.4, 50.4]] # ppm
so2_1 = [[0, 36, 76, 186, 186, 186, 186],[35, 75, 185, 304, 304, 304, 304]] # ppb
so2_24 = [[-1, -1, -1, -1, 305, 605, 805], [-1, -1, -1, -1, 604, 804, 1004]] # ppb
no2_1 = [[0, 54, 101, 361, 650, 1250, 1650],[53, 100, 360, 649, 1249, 1649, 2049]] # ppb

o3_temp = [.18, .18, .18, .18, .18, .18, .18, .18, 2.87]
so2_temp = [.85, .85, .85, .85, .85, 1.15, 1.45, 1.75, 1.95]
no2_temp = [1.18, 1.18, 1.18, 1.18, 1.18, 1.18, 1.18, 2., 2.7]
co_temp = [1.4, 1.03, .85, .62, .3, .03, -.25, -.48, -.8]

class SensorServer(Thread):
    def __init__(self, db_file="blue.db"):
        Thread.__init__(self)

        # assign GPIO pins that control mux selector pins
        # (if you're using a GPIO)
        self.mux = [
        	easyGpio(24),
        	easyGpio(25),
        	easyGpio(26),
        	easyGpio(27)
	]
    
        for sel in self.mux:
                sel.pinOUT()

        # initialize ADC library to read ADC value(s)
        self.A0 = ADC(0) # alphasense, PM 2.5
        self.A1 = ADC(1) # temperature sensor

        # json format output        
        self.sensor_output = {
            "date": 0.,
            "temp": 0.,
            "no2": 0.,
            "no2_1h_aqi": 0.,
            "o3": 0.,
            "o3_1h_aqi": 0.,
            "o3_8h_aqi": 0.,
            "co": 0.,
            "co_8h_aqi": 0.,
            "so2": 0.,
            "so2_1h_aqi": 0.,
            "so2_24h_aqi": 0.,
            "pm25": 0.,
            "pm25_aqi": 0.
        }

        self.sensor_output_lock = Lock()
        self.db_file = db_file

        try:
            self.db_conn = sqlite3.connect(self.db_file)
            self.db_cur = self.db_conn.cursor()
        except Exception as e:
            print "ERROR (sensor.py): {}".format(repr(e))
            self.__del__()

        self.db_cur.execute("select datetime('now')")

        # delete all data on the table
        '''self.db_cur.execute("DROP TABLE history")
        self.db_conn.commit()'''

        # execute query to create table using IF NOT EXISTS keywords
        self.db_cur.execute("CREATE TABLE IF NOT EXISTS history (time INT PRIMARY KEY NOT NULL, temp REAL, no2 REAL, o3 REAL, co REAL, so2 REAL, pm25 REAL)")
        self.db_conn.commit()

    def __del__(self):
        self.db_conn.close()
        # if you're using a mux, reset all selector pins to LOW
        self.set_mux_channel(0)

    def get_recent_sensor_output(self):
        return self.sensor_output.copy()

    def set_mux_channel(self, ch):
        # chang 4 selector pins depending on value of ch
        bits = "{0:04b}".format(ch)
        for i in range(0, 4):
                bit = int(bits[3-i])
                sel = self.mux[3-i]
                sel.on() if bit else sel.off()
	sleep(1)

    def run(self):
        while True:
                # aquire the lock
                self.sensor_output_lock.acquire()

                try:
			self.db_conn = sqlite3.connect(self.db_file)
			self.db_cur = self.db_conn.cursor()
	        except Exception as e:
        	        print "Error: (sensor.py) : {}".format(repr(e))
			self.__del__()

                # read from all sensors
                self.set_mux_channel(0)
                NO2_WE = self.A0.get_mvolts()

                self.set_mux_channel(1)
                NO2_AE = self.A0.get_mvolts()

                self.set_mux_channel(2)
                O3_WE = self.A0.get_mvolts()

                self.set_mux_channel(3)
                O3_AE = self.A0.get_mvolts()

                self.set_mux_channel(4)
                CO_WE = self.A0.get_mvolts()

                self.set_mux_channel(5)
                CO_AE = self.A0.get_mvolts()

                self.set_mux_channel(6)
                SO2_WE = self.A0.get_mvolts()

                self.set_mux_channel(7)
                SO2_AE = self.A0.get_mvolts()

                MT = self.A1.get_mvolts()

                self.set_mux_channel(8)
                PM = self.A0.get_mvolts()

                # get the current time
                current = int(time())
                print current

                # o3 8 hour average
                time1 = int(time()) - (8 * 60 * 60) + 25200
                time2 = int(time()) + 25200
                query = self.db_cur.execute("SELECT AVG(o3) FROM history WHERE time BETWEEN ? AND ?", (time1, time2))
                o3_8h = query.fetchone()[0]
                print "o3_8h : {}".format(self.convert_aqi('o3_8', o3_8h))

                # o3 1 hour average
                time1 = int(time()) - (1 * 60 * 60) + 25200
                query = self.db_cur.execute("SELECT AVG(o3) FROM history WHERE time BETWEEN ? AND ?", (time1, time2)) 
                o3_1h = query.fetchone()[0]
                print "o3_1h : {}".format(self.convert_aqi('o3_1', o3_1h))

                # pm25 24 hour average
                time1 = int(time()) - (24 * 60 * 60) + 25200
                query = self.db_cur.execute("SELECT AVG(pm25) FROM history WHERE time BETWEEN ? AND ?", (time1, time2))
                pm25 = query.fetchone()[0] 
                print "pm25 : {}".format(self.convert_aqi('pm25_24', pm25))

                # co 8 hour average 
                time1 = int(time()) - (8 * 60 * 60) + 25200
                query = self.db_cur.execute("SELECT AVG(co) FROM history WHERE time BETWEEN ? AND ?", (time1, time2))
                co_8h = query.fetchone()[0]
                print "co_8h : {}".format(self.convert_aqi('co_8', co_8h))
 
                # so2 1 hour average 
                time1 = int(time()) - (1 * 60 * 60) + 25200
                query = self.db_cur.execute("SELECT AVG(so2) FROM history WHERE time BETWEEN ? AND ?", (time1, time2))
                so2_1h = query.fetchone()[0]
                print "so2_1h : {}".format(self.convert_aqi('so2_1', so2_1h))

                # so2 24 hour average
                time1 = int(time()) - (24 * 60 * 60) + 25200
                query = self.db_cur.execute("SELECT AVG(so2) FROM history WHERE time BETWEEN ? AND ?", (time1, time2))
                so2_24h = query.fetchone()[0] 
                print "so2_24h : {}".format(self.convert_aqi('so2_24', so2_24h))

                # no2 1 hour average
                time1 = int(time()) - (1 * 60 * 60) + 25200
                query = self.db_cur.execute("SELECT AVG(no2) FROM history WHERE time BETWEEN ? AND ?", (time1, time2))
                no2_1h = query.fetchone()[0]
                print "no2_1h : {}".format(self.convert_aqi('no2_1', no2_1h))

                print "o3_8h avg : {}".format(o3_8h)
                print "o3_1h avg : {}".format(o3_1h)
                print "pm25 avg : {}".format(pm25)
                print "co_8h avg : {}".format(co_8h)
                print "so2_1h avg : {}".format(so2_1h)
                print "so2_24h avg : {}".format(so2_24h)
                print "no2_1h avg : {}".format(no2_1h)

                # calculate ppb or ug/m^3
                temp = ((MT * 0.004882814) - 0.5) * 5
                #temp = (((MT * 3.3) / 1024) - 0.5) * 100
                NO2 = ((NO2_WE - 287) - self.convert_temp('no2', temp) * (NO2_AE - 292)) /0.258
                O3 = ((O3_WE - 418) - self.convert_temp('o3', temp) * (O3_AE - 404)) / 0.393
                CO = ((CO_WE - 345) - self.convert_temp('co', temp) * (CO_AE - 315)) / 292
                SO2 = ((SO2_WE - 333) - self.convert_temp('so2', temp) * (SO2_AE - 274)) / 0.288
                mV = PM / 1000
                hppcf = (240. * (mV ** 6)) - (2491.3 * (mV ** 5)) + (944.87 * (mV ** 4)) - (14840 * (mV ** 3)) + (10684 * (mV ** 2)) + (2211.8 * mV) + 7.9623
                pm = 0.518 + 0.00274 * hppcf

                # if the measurement for aqi calculation is negative, replace it with zero
                if NO2 < 0:
                    NO2 = 0
                if O3 < 0:
                    O3 = 0
                if CO < 0:
                    CO = 0
                if SO2 < 0:
                    SO2 = 0
                if pm < 0:
                    pm = 0               
 
                # update the dictionary
		self.sensor_output["date"] = (current + 25200)
                self.sensor_output["temp"] = temp
                self.sensor_output["no2"] = NO2
                self.sensor_output["no2_1h_aqi"] = self.convert_aqi('no2_1', no2_1h)
                self.sensor_output["o3"] = O3
                self.sensor_output["o3_1h_aqi"] = self.convert_aqi('o3_1', o3_1h)
                self.sensor_output["o3_8h_aqi"] = self.convert_aqi('o3_8', o3_8h)
                self.sensor_output["so2"] = SO2
                self.sensor_output["so2_1h_aqi"] = self.convert_aqi('so2_1', so2_1h)
                self.sensor_output["so2_24h_aqi"] = self.convert_aqi('so2_24', so2_24h)
                self.sensor_output["co"] = CO
                self.sensor_output["co_8h_aqi"] = self.convert_aqi('co_8', co_8h)
		self.sensor_output["pm25"] = pm
                self.sensor_output["pm25_aqi"] = self.convert_aqi('pm25_24', pm25)

                print self.sensor_output                

                # insert new values into the database
                self.db_cur.execute("INSERT INTO history (time, temp, no2, o3, co, so2, pm25) VALUES (?, ?, ?, ?, ?, ?, ?)", (current + 25200, temp, NO2, O3, CO, SO2, pm)) 
                self.db_conn.commit()

                # get the measured value from the table and shows it in one line 
		'''for row in self.db_cur.execute("SELECT * FROM history"):
			pass'''
		
                # delete data stored for 24 hours
                '''yesterdate = int(time()) - (24 * 60 * 60)
                print yesterdate
		self.db_cur.execute("DELETE FROM history WHERE time <= ?", (str(yesterdate), ))
                self.db_conn.commit()'''

                # release the lock
                self.sensor_output_lock.release()

                sleep(1)

    def convert_temp(self, data_type, temp) :
        if data_type == 'o3' :
            for i in range(0, 8):
                if -30 + i * 10 <= temp < -20 + i * 10:
                    n = o3_temp[i]
                    break        
            return n
        elif data_type == 'so2' :
            for i in range(0, 8):
                if -30 + i * 10 <= temp < -20 + i * 10:
                    n = so2_temp[i]
                    break        
            return n
        elif data_type == 'no2' :
            for i in range(0, 8):
                if -30 + i * 10 <= temp < -20 + i * 10:
                    n = no2_temp[i]
                    break        
            return n
        elif data_type == 'co' :
            for i in range(0, 8):
                if -30 + i * 10 <= temp < -20 + i * 10:
                    n = co_temp[i]
                    break        
            return n

    # calculate aqi for each pollution
    def convert_aqi(self, data_type, pollution) :
        if data_type == 'no2_1' :
            index = self.find_index(no2_1, pollution)

            # if the range is exceeded, return 500
            if index == -1 :
                return 500
            else :
                return self.calculate_aqi(pollution, no2_1[0][index], no2_1[1][index], aqi_index[0][index], aqi_index[1][index])
        elif data_type == 'o3_1' :
            index = self.find_index(o3_1, pollution)

            if index == -1 :
		if pollution < o3_1[0][2] :
                    return -1
                else : 
                    return 500
            else :
                return  self.calculate_aqi(pollution, o3_1[0][index], o3_1[1][index], aqi_index[0][index], aqi_index[1][index])
        elif data_type == 'o3_8' :
            index = self.find_index(o3_8, pollution)

            if index == -1 :
                return 500  
            else :
                return  self.calculate_aqi(pollution, o3_8[0][index], o3_8[1][index], aqi_index[0][index], aqi_index[1][index])
        elif data_type == 'co_8' :
            index = self.find_index(co_8, pollution)

            if index == -1 :
                return 500
            else :
                return self.calculate_aqi(pollution, co_8[0][index], co_8[1][index], aqi_index[0][index], aqi_index[1][index])
        elif data_type == 'so2_1' :
            index = self.find_index(so2_1, pollution)

            if index == -1 :
                return 500
            else :
                return self.calculate_aqi(pollution, so2_1[0][index], so2_1[1][index], aqi_index[0][index], aqi_index[1][index])
        elif data_type == 'so2_24' :
            index = self.find_index(so2_24, pollution)

            if index == -1 :
                return 500
            else :
                return self.calculate_aqi(pollution, so2_24[0][index], so2_24[1][index], aqi_index[0][index], aqi_index[1][index])
        elif data_type == 'pm25_24' :
            index = self.find_index(pm25_24, pollution)

            if index == -1 :
                return 500
            else :
                return self.calculate_aqi(pollution, pm25_24[0][index], pm25_24[1][index], aqi_index[0][index], aqi_index[1][index])
        else :
            return -1

    # aqi formula
    def calculate_aqi(self, c, low_c, high_c, low_i, high_i) :
        pollution = float(c)
        low_pollution_range = float(low_c)
        low_aqi_range = float(low_i)
        high_pollution_range = float(high_c)
        high_aqi_range = float(high_i)

        return int((((high_aqi_range - low_aqi_range) / (high_pollution_range - low_pollution_range)) * (pollution - low_pollution_range)) + low_aqi_range)

    # find 'index' range
    def find_index(self, data_list, pollution) :
        index = -1

        for k, v in enumerate(data_list[0]) :
            if data_list[0][k] == -1 :
                continue
            elif data_list[0][k] <= pollution <= data_list[1][k] :
                index = k
                break

        return index

