from tkinter import *
import tkinter as tk
from numpy import delete
import ttkbootstrap as tb
import datetime
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
from Store import Store as _Store
from AppData import AppData as _AppData


class AppUI:
    def __init__(self, appdata, store):
        #Übergabeparameter
        self._AppData = appdata
        self._Store = store
        
        #Window
        self.root = tb.Window(themename="superhero")
        self.root.columnconfigure(3, weight=1)
        self.root.rowconfigure(6, weight=1)
        
        #Kalender
        self.calendarstart = tb.DateEntry()
        self.calendarend = tb.DateEntry()
        
        #Liste
        self.combolistdata = self._Store.LstData
        self.combolistloc = self._Store.LstLoc
        
        #Combobox
        self.comboboxdata = tb.Combobox()
        self.comboboxloc = tb.Combobox()
        
        #Button
        self.buttonstart = tb.Button()
        
        self.buttonaverage = tb.Button()
        self.buttonmax = tb.Button()
        self.buttonmin = tb.Button()
        self.buttonhumidity = tb.Button()
       
        #Label
        self.labelerror = tb.Label()
        self.labeldata = tb.Label()
        
        #Linie
        self.labelline = tb.Label()
        
        self.canvasline = tb.Canvas()
        

        # Erstelle ein Frame für die Matplotlib-Grafik
        self.frame = tb.Frame(self.root)
        self.frame.grid(row=5,rowspan=3,column=0,columnspan=5, sticky="NSEW")
        # Erstelle eine Matplotlib-Figur
        self.fig = Figure(figsize=(4, 2), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel("Zeitraum")
        self.ax.set_ylabel("Temperatur")
        self.ax.legend()
        # Erstelle einen Canvas für die Matplotlib-Figur
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        
        return
    
    def Window_Initialize(self):
        # Erzeugung des Fensters
        self.root.title("Feinstaub")
        self.root.geometry('1000x700')
    
    def Window_Initialize_UI(self):
        self.Window_Initialize_Buttons(self)
    
        return
    
    def Window_Initialize_Buttons(self):
        
        #Kalender Startdatum
        self.calendarstart = tb.DateEntry(self.root, startdate=self._Store.LstDay[2])
        self.calendarstart.grid(row=0,column=0,padx=10,pady=20)
        
        #Kalender Endddatum
        self.calendarend = tb.DateEntry(self.root, startdate=self._Store.LstDay[1])
        self.calendarend.grid(row=0,column=1,padx=10,pady=20)

        # #Kombobox Datenauswahl
        # self.comboboxdata = tb.Combobox(self.root,values=self.combolistdata, state="readonly")
        # self.comboboxdata.grid(row=0,column=2,padx=10,pady=20)
        # self.comboboxdata.set(self.combolistdata[0])

        #Kombobox Locationauswahl
        self.comboboxloc = tb.Combobox(self.root,values=self.combolistloc, state="readonly")
        self.comboboxloc.grid(row=0,column=2,padx=10,pady=20)
        self.comboboxloc.set(self.combolistloc[0])

        #Start-Button
        self.buttonstart = tb.Button(self.root, command =lambda:self.ButtonStart_Clicked(self), text='Start', bootstyle="SUCCESS")
        self.buttonstart.grid(row=0,column=3,padx=10,pady=20)

        self.buttonaverage = tb.Button(self.root, command =lambda:self.ButtonAverage_Clicked(self), text='Durchschnitt', bootstyle="SUCCESS, outline")
        self.buttonmax = tb.Button(self.root, command =lambda:self.ButtonMax_Clicked(self), text='Maximum', bootstyle="SUCCESS, outline")
        self.buttonmin = tb.Button(self.root, command =lambda:self.ButtonMin_Clicked(self), text='Minimum', bootstyle="SUCCESS, outline")
        self.buttonhumidity = tb.Button(self.root, command =lambda:self.ButtonHumidity_Clicked(self), text='Luftfeuchtigkeit', bootstyle="SUCCESS, outline")
        
        #Error-Label
        self.labelerror = tb.Label(self.root)
        
        #Line-Canvas
        self.canvasline.create_line(0, 0, 50,0)
        
        #Data-Label
        self.labeldata = tb.Label(self.root)
        
    def Window_Activate(self):
        # Aktivierung des Fensters
        self.root.mainloop()
        

    def UI_DataToStore(self):
        self._Store._Constant.CurrentCalendarStart = datetime.datetime.strptime(self.calendarstart.entry.get(), '%d.%m.%Y')
        self._Store._Constant.CurrentCalendarEnd = datetime.datetime.strptime(self.calendarend.entry.get(), '%d.%m.%Y')
        self._Store._Constant.CurrentSensorGUI = self.comboboxloc.get()
        return
    
    def UI_CheckData(self):

        try:
            start_date = datetime.datetime.strptime(self.calendarstart.entry.get(), '%d.%m.%Y')
            end_date = datetime.datetime.strptime(self.calendarend.entry.get(), '%d.%m.%Y')
        except:
            return False
        
        if(start_date > end_date):
            return False
        elif(end_date > self._Store.LstDay[1]):
            return False
        
        return True
    
    def UI_StartGraphic(self):
        
        #Linie und Daten setzen
        # self.canvasline.grid(row=2, column=0,sticky="w")
        self.labeldata.config(text=f"{self.calendarstart.entry.get()} - {self.calendarend.entry.get()}, {self._Store._Constant.CurrentSensorGUI}")
        self.labeldata.grid(row=3, column=0,columnspan=2,sticky="w",padx=10)
        self.buttonaverage.grid(row=4, column=0)
        self.buttonmax.grid(row=4, column=1, pady=30)
        self.buttonmin.grid(row=4, column=2)
        self.buttonhumidity.grid(row=4, column=3)
        
        self.UI_StartPlot(self)
        
        return
    def UI_StartPlot(self):

        self.ax.plot(self._Store._Constant.AnalyseDataAverageTime, self._Store._Constant.AnalyseDataAverage, label="Durchschnitt")
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        return
    ########################################
    ## EVENTS
    ########################################
    def ButtonStart_Clicked(self):
        
        #aufräumen
        self.labelerror.grid_forget()
        # self.canvasline.grid_forget()
        
        #Falls Fehler, Textfeld anzeigen
        if(self.UI_CheckData(self) == False):
            self.labelerror.config(text="Fehler bei Datumeingabe")
            self.labelerror.grid(row=0,column=4,padx=10,pady=20)
            return
        
        #Daten in Store speichern 
        self.UI_DataToStore(self)
        
        #AppData aufrufen
        if _AppData.Database_CheckData(_AppData):
            self.UI_StartGraphic(self)
            return
        else:
            self.labelerror.configure(text="Eingabe nicht darstellbar")
            self.labelerror.grid(row=0,column=4,padx=10,pady=20)
        return
    
    def ButtonAverage_Clicked(self):
        return
    
    def ButtonMax_Clicked(self):
        return
    
    def ButtonMin_Clicked(self):
        return
    
    def ButtonHumidity_Clicked(self):
        return