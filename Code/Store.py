import datetime

class Store:
    def __init__(self):
        self._Constant = Constant()
        
        self.LstLoc = []
        self.LstData = [self._Constant.DataAverage, self._Constant.DataMax,self._Constant.DataMin]     
        self.LstDay = [self._Constant.DayZero, self._Constant.DayOne, self._Constant.DayTwo]

        return
    
class Constant:
    def __init__(self):
        
        #Database
        self.DbName = "Sensor_Data.db"
        self.Output_Dir = "Temp"

        #Url
        self.Base_URL = "https://archive.sensor.community"

        #Datenauswahl
        self.DataAverage = "Durchschnitt"
        self.DataMax = "Maximum"
        self.DataMin = "Minimum"
        
        # Tage
        self.DayZero = datetime.datetime.today() - datetime.timedelta(days=0)
        self.DayOne = datetime.datetime.today() - datetime.timedelta(days=1)
        self.DayTwo = datetime.datetime.today() - datetime.timedelta(days=2)

        #CurrentData
        #Daten aus der Kalender Box
        self.CurrentCalendarStart = datetime.datetime
        self.CurrentCalendarEnd = datetime.datetime
        #Für die Abfrage der Tabellen
        self.CurrentCalendarStartQuery = datetime.datetime
        self.CurrentCalendarEndQuery = datetime.datetime
        self.QueryTime = []        

        self.CurrentSensor = ""
        self.CurrentSensorGUI = ""
        self.CurrentSensortbl = "tbl_"
        
        #Fehlende Datumswerte
        self.Missing_Dates = []
        
        #Daten zur Auswertung
        self.AnalyseDataAverage = []
        self.AnalyseDataAverageTime = []
        
        self.AnalyseDataMax = []
        self.AnalyseDataMaxTime = []

        self.AnalyseDataMin = []
        self.AnalyseDataMinTime = []

        self.AnalyseDataHumidity = []
        self.AnalyseDataHumidityTime = []

        return