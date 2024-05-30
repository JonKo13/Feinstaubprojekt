import sqlite3
import csv
import gzip
from io import StringIO
from pickletools import read_float8
import shutil
import os
from urllib.request import urlretrieve
import requests
from datetime import datetime, timedelta
from Store import Store as _Store


class AppData:
    def __init__(self, store):
        #�bergabeparameter
        self._Store = store
        
        #Datenbank
        self.cursor = sqlite3.Cursor
        self.conn = sqlite3

    def Database_Initialize(self):
        # Verbindung zur Datenbank herstellen (falls die Datenbank nicht existiert, wird sie automatisch erstellt)
        self.conn = sqlite3.connect(self._Store._Constant.DbName)
        
        # Ein Cursor-Objekt erstellen, um SQL-Operationen durchzuf�hren
        self.cursor = self.conn.cursor()
        
        return

    def Database_DataToStore(self):
        # Abfrage 
        self.cursor.execute("SELECT Alias FROM tbl_SensorSt")
        self._Store.LstLoc = self.cursor.fetchall()

        return
    
    
    def Database_CheckData(self):
        
        #CurrentSensortbl zur�cksetzen
        self._Store._Constant.CurrentSensortbl = "tbl_"
        
        # SensorAlias in SensorID umwandeln
        self.cursor.execute(f"SELECT SensorID FROM tbl_SensorSt WHERE Alias='{self._Store._Constant.CurrentSensorGUI}'")
        temp_value = self.cursor.fetchone()
        
        for row in temp_value:
            self._Store._Constant.CurrentSensortbl = self._Store._Constant.CurrentSensortbl + row
            self._Store._Constant.CurrentSensor = row
            break

        # Tabelle erstellen (falls sie nicht existiert)
        self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS {self._Store._Constant.CurrentSensortbl}
                  ("sensor_id"	INTEGER,
	               "sensor_type"	TEXT,
	               "location"	INTEGER,
	               "lat"	NUMERIC,
	               "lon"	NUMERIC,
	               "timestamp"	INTEGER,
	               "temperature"	INTEGER,
	               "humidity"	NUMERIC)''')
        
        # Start- und Enddatum f�r Abfrage formatieren
        self._Store._Constant.CurrentCalendarStartQuery = self._Store._Constant.CurrentCalendarStart - timedelta(days=1)
        self._Store._Constant.CurrentCalendarEndQuery = self._Store._Constant.CurrentCalendarEnd + timedelta(days=1)
        
        #Abfrage auf Datenbank ausf�hren
        self.Check_Data(self)

        #Falls Daten nicht vorhanden, herunterladen
        if(self._Store._Constant.QueryTime == []):
            self.Download_Files(self)
            self.Check_Data(self)
            if not self.GetData_FromTbl(self):
                return False
        
        else:
            #Pr�fen, ob Datumswerte fehlen, falls ja, herunterladen
            self.Check_MissingDates(self)
            if not (self._Store._Constant.Missing_Dates == []):
                self.Download_Files_Missing(self, self._Store._Constant.Missing_Dates)
            
            self.GetData_FromTbl(self)
        
        return True
    

    def Check_Data(self):
        # Pr�fen, ob Daten schon vorhanden
        self.cursor.execute(f"SELECT timestamp FROM {self._Store._Constant.CurrentSensortbl} WHERE timestamp > '{self._Store._Constant.CurrentCalendarStartQuery}' AND timestamp < '{self._Store._Constant.CurrentCalendarEndQuery}' ")
        self._Store._Constant.QueryTime = self.cursor.fetchall()
        return
    
    def GetData_FromTbl(self):
        if(self._Store._Constant.QueryTime == []):
            return False
        
        self.cursor.execute(f"SELECT timestamp, temperature, humidity FROM {self._Store._Constant.CurrentSensortbl} WHERE timestamp > '{self._Store._Constant.CurrentCalendarStartQuery}' AND timestamp < '{self._Store._Constant.CurrentCalendarEndQuery}' ")
        data = self.cursor.fetchall()

        for entry in data:
            self._Store._Constant.AnalyseDataAverage.append(float(entry[1]))
            self._Store._Constant.AnalyseDataAverageTime.append(entry[0])
        
        return True

    def Check_MissingDates(self):
                
        # Konvertiere die Datumswerte in datetime-Objekte
        start_date = self._Store._Constant.CurrentCalendarStart
        end_date = self._Store._Constant.CurrentCalendarEnd

        # Berechne die Anzahl der Tage zwischen den beiden Daten
        delta = end_date - start_date

        # Erzeuge eine Liste von Datumswerten zwischen den beiden Daten
        date_list = [start_date + timedelta(days=i) for i in range(delta.days + 1)]

        # Ausgabe der Datumswerte
        for date in date_list:
            # Datum f�r Abfrage formatieren
            start = date - timedelta(days=1)
            end = date + timedelta(days=1)
            
            #Abfrage durchf�hren
            self.cursor.execute(f"SELECT timestamp FROM {self._Store._Constant.CurrentSensortbl} WHERE timestamp > '{start}' AND timestamp < '{end}'")
            date_db = self.cursor.fetchall()
            
            #Falls Datum nicht vorhanden, �bergeben
            if date_db == []:
                self._Store._Constant.Missing_Dates.append(date)
            date_db = []
                
        return
            
    def Download_Files(self):
        #Variablen
        current_date = self._Store._Constant.CurrentCalendarStart
        two_year_ago = datetime(datetime.now().year - 1,1,1)
        gztruefalse = False
        downloadfailed = False
    
        # Tabelle erstellen, falls sie nicht existiert
        self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS {self._Store._Constant.CurrentSensortbl}
                  ("sensor_id"	INTEGER,
	               "sensor_type"	TEXT,
	               "location"	INTEGER,
	               "lat"	NUMERIC,
	               "lon"	NUMERIC,
	               "timestamp"	INTEGER,
	               "temperature"	INTEGER,
	               "humidity"	NUMERIC)''')

        while current_date <= self._Store._Constant.CurrentCalendarEnd:

            date_str = current_date.strftime('%Y-%m-%d')
            endung = ""
            if current_date < two_year_ago:
                # F�r Dateien, die �lter als zwei Jahre sind
                year_month_day_str = current_date.strftime('%Y-%m-%d')
                year_str = current_date.strftime('%Y')
                endung = ".csv.gz"
                url = f"{self._Store._Constant.Base_URL}/{year_str}/{year_month_day_str}/{date_str}_{self._Store._Constant.CurrentSensor}{endung}"
                
                try:
                    r = requests.get(url)
                    if(r.status_code != 200):
                        endung = ".csv"
                        url = f"{self._Store._Constant.Base_URL}/{year_str}/{year_month_day_str}/{date_str}_{self._Store._Constant.CurrentSensor}{endung}"
                except requests.exceptions.ConnectionError:
                    continue
            else:
                endung = ".csv"
                # F�r Dateien innerhalb der letzten 2 Jahre
                url = f"{self._Store._Constant.Base_URL}/{date_str}/{date_str}_{self._Store._Constant.CurrentSensor}{endung}"
        
            response = requests.get(url)
            csv_data = response.text
            datei = f"{date_str}_{self._Store._Constant.CurrentSensor}{endung}"  

            if response.status_code == 200:
                os.makedirs(self._Store._Constant.Output_Dir, exist_ok=True)
                file_path = os.path.join(self._Store._Constant.Output_Dir, datei)
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                print(f"Downloaded: {file_path}")
                downloadfailed = False
            else:
                print(f"Failed to download: {url} - Status Code: {response.status_code}")
                current_date += timedelta(days=1)
                downloadfailed = True
                continue


            # Entpacken der Datei, falls sie eine .gz-Erweiterung hat
            if file_path.endswith('.gz'):
                with gzip.open(file_path, 'rb') as f_in:
                    with open(file_path[:-3], 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(file_path)  # Entfernen der .gz-Datei nach dem Entpacken
                file_path = file_path[:-3]
                print(f"Unzipped: {file_path[:-3]}")
                gztruefalse = True
        
            if gztruefalse:
                with open(file_path) as csvfile:
                    reader = csv.reader(csvfile, delimiter=';')
                    header = next(reader)  # �berspringen der Header-Zeile

                    for row in reader: 
                        self.cursor.execute(f'''INSERT INTO {self._Store._Constant.CurrentSensortbl}(sensor_id,sensor_type, location, lat, lon, timestamp, temperature, humidity) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', row)
                gztruefalse = False
                
            else:
                # CSV-Daten in die SQLite-Datenbank einf�gen
                reader = csv.reader(StringIO(csv_data), delimiter=';')
                header = next(reader)  # �berspringen der Header-Zeile

                for row in reader: 
                    self.cursor.execute(f'''INSERT INTO {self._Store._Constant.CurrentSensortbl}(sensor_id,sensor_type, location, lat, lon, timestamp, temperature, humidity) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', row)
            

            self.conn.commit()
            print(f"Inserted sensor_data from {file_path} into database")
            
            current_date += timedelta(days=1)
        
        #Falls Ordner Existiert, l�schen
        if not downloadfailed:
            shutil.rmtree(os.path.join(self._Store._Constant.Output_Dir))

        return
    
    def Download_Files_Missing(self, missing_dates):
        
        #Variablen
        two_year_ago = datetime(datetime.now().year - 1,1,1)
        gztruefalse = False
        downloadfailed = False
    
        # Tabelle erstellen, falls sie nicht existiert
        self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS {self._Store._Constant.CurrentSensortbl}
                  ("sensor_id"	INTEGER,
	               "sensor_type"	TEXT,
	               "location"	INTEGER,
	               "lat"	NUMERIC,
	               "lon"	NUMERIC,
	               "timestamp"	INTEGER,
	               "temperature"	INTEGER,
	               "humidity"	NUMERIC)''')

        for date in missing_dates:

            date_str = date.strftime('%Y-%m-%d')
            endung = ""
            if date < two_year_ago:
                # F�r Dateien, die �lter als zwei Jahre sind
                year_month_day_str = date.strftime('%Y-%m-%d')
                year_str = date.strftime('%Y')
                endung = ".csv.gz"
                url = f"{self._Store._Constant.Base_URL}/{year_str}/{year_month_day_str}/{date_str}_{self._Store._Constant.CurrentSensor}{endung}"
                
                try:
                    r = requests.get(url)
                    if(r.status_code != 200):
                        endung = ".csv"
                        url = f"{self._Store._Constant.Base_URL}/{year_str}/{year_month_day_str}/{date_str}_{self._Store._Constant.CurrentSensor}{endung}"
                except requests.exceptions.ConnectionError:
                    continue
            else:
                endung = ".csv"
                # F�r Dateien innerhalb der letzten 2 Jahre
                url = f"{self._Store._Constant.Base_URL}/{date_str}/{date_str}_{self._Store._Constant.CurrentSensor}{endung}"
        
            response = requests.get(url)
            csv_data = response.text
            datei = f"{date_str}_{self._Store._Constant.CurrentSensor}{endung}"  

            if response.status_code == 200:
                os.makedirs(self._Store._Constant.Output_Dir, exist_ok=True)
                file_path = os.path.join(self._Store._Constant.Output_Dir, datei)
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                print(f"Downloaded: {file_path}")
                downloadfailed = False
            else:
                print(f"Failed to download: {url} - Status Code: {response.status_code}")
                downloadfailed = True
                continue


            # Entpacken der Datei, falls sie eine .gz-Erweiterung hat
            if file_path.endswith('.gz'):
                with gzip.open(file_path, 'rb') as f_in:
                    with open(file_path[:-3], 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(file_path)  # Entfernen der .gz-Datei nach dem Entpacken
                file_path = file_path[:-3]
                print(f"Unzipped: {file_path[:-3]}")
                gztruefalse = True
        
            if gztruefalse:
                with open(file_path) as csvfile:
                    reader = csv.reader(csvfile, delimiter=';')
                    header = next(reader)  # �berspringen der Header-Zeile

                    for row in reader: 
                        self.cursor.execute(f'''INSERT INTO {self._Store._Constant.CurrentSensortbl}(sensor_id,sensor_type, location, lat, lon, timestamp, temperature, humidity) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', row)
                gztruefalse = False
                
            else:
                # CSV-Daten in die SQLite-Datenbank einf�gen
                reader = csv.reader(StringIO(csv_data), delimiter=';')
                header = next(reader)  # �berspringen der Header-Zeile

                for row in reader: 
                    self.cursor.execute(f'''INSERT INTO {self._Store._Constant.CurrentSensortbl}(sensor_id,sensor_type, location, lat, lon, timestamp, temperature, humidity) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', row)
            

            self.conn.commit()
            print(f"Inserted sensor_data from {file_path} into database")
                    
        #Falls Ordner Existiert, l�schen
        if not downloadfailed:
            shutil.rmtree(os.path.join(self._Store._Constant.Output_Dir))

        return