def conver_aqi(data_type, pollution) :
   if data_type == 'o3_8' :
      index = find_index(o3_8, pollution)

      if index == -1 :
         pass
      else :
         return  calculate_aqi(pollution, o3_8[0][index], o3_8[1][index], aqi_index[0][index], aqi_index[1][index])
   elif data_type == 'o3_1' :
      index = find_index(o3_1, pollution)

      if index == -1 :
         pass
      else :
         return  calculate_aqi(pollution, o3_1[0][index], o3_1[1][index], aqi_index[0][index], aqi_index[1][index])
   elif data_type == 'pm25_24' :
      index = find_index(pm25_24, pollution)

      if index == -1 :
         pass
      else :
         return calculate_aqi(pollution, pm25_24[0][index], pm25_24[1][index], aqi_index[0][index], aqi_index[1][index])
   elif data_type == 'co_8' :
      index = find_index(co_8, pollution)

      if index == -1 :
         pass
      else :
         return calculate_aqi(pollution, co_8[0][index], co_8[1][index], aqi_index[0][index], aqi_index[1][index])
   elif data_type == 'so2_1' :
      index = find_index(so2_1, pollution)

      if index == -1 :
         pass
      else :
         return calculate_aqi(pollution, so2_1[0][index], so2_1[1][index], aqi_index[0][index], aqi_index[1][index])
   elif data_type == 'no2_1' :
      index = find_index(no2_1, pollution)

      if index == -1 :
         pass
      else :
         return calculate_aqi(pollution, no2_1[0][index], no2_1[1][index], aqi_index[0][index], aqi_index[1][index])
   else :
      return -1

def calculate_aqi(c, low_c, high_c, low_i, high_i) :
   pollution = float(c)
   low_pollution_range = float(low_c)
   low_aqi_range = float(low_i)
   high_pollution_range = float(high_c)
   high_aqi_range = float(high_i)
   return int((((high_aqi_range - low_aqi_range) / (high_pollution_range - low_pollution_range)) * (pollution - low_pollution_range)) + low_aqi_range)

aqi_index = [[0, 51, 101, 151, 201, 301, 401],[50, 100, 150, 200, 300, 400, 500]]
o3_8 = [[0, 55, 71, 86, 106], [54, 70, 85, 105, 200]] # ppb
o3_1 = [[-1, -1, 125, 165, 205, 405, 505], [-1, -1, 164, 204, 404, 504, 604]] # ppb
pm25_24 = [[0, 12.1, 35.5, 55.5, 150.5, 250.5, 350.5],[12.0, 35.4, 55.4, 150.4, 250.4, 350.4, 500.4]] # ug/m3
co_8 = [[1, 4.5, 9.5, 12.5, 15.5, 30.5, 40.5],[4.4, 9.4, 12.4, 15.4, 30.4, 40.4, 50.4]] # ppm
so2_1 = [[0, 36, 76, 186, 305, 605, 805],[35, 75, 185, 304, 604, 804, 1004]] # ppb
no2_1 = [[0, 54, 101, 361, 650, 1250, 1650],[53, 100, 360, 649, 1249, 1649, 2049]] # ppb

def find_index(data_list, pollution) :
   index = -1

   for k, v in enumerate(data_list[0]) :
      if data_list[0][k] == -1 :
         continue;
      elif data_list[0][k] <= pollution <= data_list[1][k] :
         index = k
         break

   return index
