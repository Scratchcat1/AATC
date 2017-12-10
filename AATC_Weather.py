import pyowm, AATC_Coordinate, math,time

def Get_OWM():
    owm = pyowm.OWM('5b943c4857a45d75ef7ee9b301666fa8')

class OWM_Control:
    def __init__(self):
        self._owm = pyowm.OWM('5b943c4857a45d75ef7ee9b301666fa8')
        
    def Get_Ajusted_Speed(self,CoordA,CoordB,Speed,At_Time = time.time()):
        try:
            
            forecast = self._owm.daily_forecast_at_coords(CoordA.Get_Y(),CoordA.Get_X())
            wind = forecast.get_weather_at(int(At_Time)).get_wind()
            
            bearing = AATC_Coordinate.GetBearing(CoordA,CoordB)
            wind_bearing = AATC_Coordinate.Reverse_Angle(wind["deg"])

            Vx = Speed*math.sin(AATC_Coordinate.toRadian(bearing))+ wind["speed"]*math.sin(AATC_Coordinate.toRadian(wind_bearing))
            Vy = Speed*math.cos(AATC_Coordinate.toRadian(bearing))+ wind["speed"]*math.cos(AATC_Coordinate.toRadian(wind_bearing))
            V = math.sqrt(Vx**2+Vy**2)
            if V < 0:  #To prevent estimating negative speeds
                V = 1
            return V
        except:
            return Speed
    
