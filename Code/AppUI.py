from tkinter import *
from tkinter import filedialog
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
import numpy as np


class AppUI:
    def __init__(self, appdata, store):
        #Übergabeparameter
        self._AppData = appdata
        self._Store = store
        
        #Window
        self.root = tb.Window(themename="superhero")
        
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
        self.buttonexport = tb.Button()
       
        #Label
        self.labelerror = tb.Label()
        self.labeldata = tb.Label()
        
        #Linie
        self.labelline = tb.Label()        
        self.canvasline = tb.Canvas()
        

        self.currentfig = None

        # Erstelle ein Frame für die Matplotlib-Grafik
        self.frameall = None
        # Erstelle eine Matplotlib-Figur
        self.figall =  None
        self.axall =  None
        # Erstelle einen Canvas für die Matplotlib-Figur
        self.canvasall = None

        # Erstelle ein Frame für die Matplotlib-Grafik
        self.frameaverage = None
        # Erstelle eine Matplotlib-Figur
        self.figaverage =  None
        self.axaverage =  None
        # Erstelle einen Canvas für die Matplotlib-Figur
        self.canvasaverage =  None
        
        # Erstelle ein Frame für die Matplotlib-Grafik
        self.framemax = None
        # Erstelle eine Matplotlib-Figur
        self.figmax =  None
        self.axmax =  None
        # Erstelle einen Canvas für die Matplotlib-Figur
        self.canvasmax =  None

        # Erstelle ein Frame für die Matplotlib-Grafik
        self.framemin = None
        # Erstelle eine Matplotlib-Figur
        self.figmin =  None
        self.axmin =  None
        # Erstelle einen Canvas für die Matplotlib-Figur
        self.canvasmin =  None
        
        return
    
    def Window_Initialize(self):
        # Erzeugung des Fensters
        self.root.title("Feinstaub")
        self.root.geometry('1060x700')
    
    def Window_Initialize_UI(self):
        self.Window_Initialize_Buttons(self)
    
        return
    
    def Window_Initialize_Buttons(self):
        
        #Kalender Startdatum
        self.calendarstart = tb.DateEntry(self.root, startdate=self._Store.LstDay[2])
        self.calendarstart.place(x=30,y=30)
        
        #Kalender Endddatum
        self.calendarend = tb.DateEntry(self.root, startdate=self._Store.LstDay[1])
        self.calendarend.place(x=275,y=30)

        #Kombobox Locationauswahl
        self.comboboxloc = tb.Combobox(self.root,values=self.combolistloc, state="readonly")
        self.comboboxloc.place(x=525,y=30)
        self.comboboxloc.set(self.combolistloc[0])

        #Start-Button
        self.buttonstart = tb.Button(self.root, command =lambda:self.ButtonStart_Clicked(self), text='Start', bootstyle="SUCCESS")
        self.buttonstart.place(x=750,y=30)

        self.buttonaverage = tb.Button(self.root, command =lambda:self.ButtonAverage_Clicked(self), text='Durchschnitt', bootstyle="SUCCESS, outline")
        self.buttonmax = tb.Button(self.root, command =lambda:self.ButtonMax_Clicked(self), text='Maximum', bootstyle="SUCCESS, outline")
        self.buttonmin = tb.Button(self.root, command =lambda:self.ButtonMin_Clicked(self), text='Minimum', bootstyle="SUCCESS, outline")
        self.buttonall = tb.Button(self.root, command =lambda:self.ButtonAll_Clicked(self), text='Gesamttemperatur', bootstyle="SUCCESS, outline")
        
        self.buttonexport = tb.Button(self.root, command =lambda:self.ButtonExport_Clicked(self), text='Exportieren', bootstyle="SUCCESS, outline")

        #Error-Label
        self.labelerror = tb.Label(self.root)
        
        #Line-Canvas
        self.canvasline.create_line(0, 0, 250,0)
        
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
        self.canvasline.place(x=30,y=85)
        self.labeldata.config(text=f"{self.calendarstart.entry.get()} - {self.calendarend.entry.get()}, {self._Store._Constant.CurrentSensorGUI}")
        self.labeldata.place(x=30,y=88)
        self.buttonall.place(x=100,y=150)
        self.buttonaverage.place(x=325,y=150)
        self.buttonmax.place(x=500,y=150)
        self.buttonmin.place(x=675,y=150)
        self.buttonexport.place(x=850,y=150)        


        self.UI_DeletePlot(self)
        self.UI_CreatePlot(self)
        self.UI_StartPlot(self)
        
        return
    def UI_DeletePlot(self):
        if not (self.frameall == None):
            self.canvasall.get_tk_widget().forget()
            self.canvasall.get_tk_widget().delete()
            self.figall.clf()
            
        self.frameall = None
        self.axall = None
        self.canvasall = None
        self.figall = None
        
        self.frameaverage = None
        self.axaverage = None
        self.canvasaverage = None
        self.figaverage = None
        
        self.framemax = None
        self.axmax = None
        self.canvasmax = None
        self.figmax = None
        
        self.framemin = None
        self.axmin = None
        self.canvasmin = None
        self.figmin = None

        return
    def UI_CreatePlot(self):
        # Erstelle ein Frame für die Matplotlib-Grafik
        self.frameall = tb.Frame(self.root)
        self.frameall.place(x=30,y=200)
        # Erstelle eine Matplotlib-Figur
        self.figall = Figure(figsize=(8,4), dpi=100)
        self.axall = self.figall.add_subplot(1,1,1)
        self.axall.set_xlabel("Zeitraum")
        self.axall.set_ylabel("Temperatur")
        self.axall.set_title(f"{self._Store._Constant.CurrentSensor}")
        # Erstelle einen Canvas für die Matplotlib-Figur
        self.canvasall = FigureCanvasTkAgg(self.figall, master=self.frameall)


        # Erstelle ein Frame für die Matplotlib-Grafik
        self.frameaverage = tb.Frame(self.root)
        self.frameaverage.place(x=30,y=200)
        # Erstelle eine Matplotlib-Figur
        self.figaverage = Figure(figsize=(8,4), dpi=100)
        self.axaverage = self.figaverage.add_subplot(1,1,1)
        self.axaverage.set_xlabel("Zeitraum")
        self.axaverage.set_ylabel("Temperatur")
        self.axaverage.set_title(f"{self._Store._Constant.CurrentSensor}")
        # Erstelle einen Canvas für die Matplotlib-Figur
        self.canvasaverage = FigureCanvasTkAgg(self.figaverage, master=self.frameaverage)
        
        
        # Erstelle ein Frame für die Matplotlib-Grafik
        self.framemax = tb.Frame(self.root)
        self.framemax.place(x=30,y=200)
        # Erstelle eine Matplotlib-Figur
        self.figmax = Figure(figsize=(8,4), dpi=100)
        self.axmax = self.figmax.add_subplot(1,1,1)
        self.axmax.set_xlabel("Zeitraum")
        self.axmax.set_ylabel("Temperatur")
        self.axmax.set_title(f"{self._Store._Constant.CurrentSensor}")
        # Erstelle einen Canvas für die Matplotlib-Figur
        self.canvasmax = FigureCanvasTkAgg(self.figmax, master=self.framemax)
        
        # Erstelle ein Frame für die Matplotlib-Grafik
        self.framemin = tb.Frame(self.root)
        self.framemin.place(x=30,y=200)
        # Erstelle eine Matplotlib-Figur
        self.figmin = Figure(figsize=(8,4), dpi=100)
        self.axmin = self.figmin.add_subplot(1,1,1)
        self.axmin.set_xlabel("Zeitraum")
        self.axmin.set_ylabel("Temperatur")
        self.axmin.set_title(f"{self._Store._Constant.CurrentSensor}")
        # Erstelle einen Canvas für die Matplotlib-Figur
        self.canvasmin = FigureCanvasTkAgg(self.figmin, master=self.framemin)
        
        return
    def UI_StartPlot(self):
        self.currentfig = self.figall
        self.buttonall.configure(state=DISABLED)
        self.buttonaverage.configure(state=NORMAL)
        self.buttonmax.configure(state=NORMAL)
        self.buttonmin.configure(state=NORMAL)

        self.axall.plot(self._Store._Constant.AnalyseDataAllTime, self._Store._Constant.AnalyseDataAll)
        self.canvasall.draw()
        self.canvasall.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        return
    ########################################
    ## EVENTS
    ########################################
    def ButtonStart_Clicked(self):
        
        #aufräumen
        self.labelerror.place_forget()
        
        #Falls Fehler, Textfeld anzeigen
        if(self.UI_CheckData(self) == False):
            self.labelerror.config(text="Fehler bei Datumeingabe")
            self.labelerror.place(x=800,y=30)
            return
        
        #Daten in Store speichern 
        self.UI_DataToStore(self)
        
        #AppData aufrufen
        if _AppData.Database_CheckData(_AppData):
            self.UI_StartGraphic(self)
            return
        else:
            self.labelerror.configure(text="Eingabe nicht darstellbar")
            self.labelerror.place(x=850,y=35)
        return
    
    def ButtonAverage_Clicked(self):
        self.currentfig = self.figaverage
        self.figall.set_visible(False)
        self.figaverage.set_visible(True)
        self.figmax.set_visible(False)
        self.figmin.set_visible(False)
        self.buttonall.configure(state=NORMAL)
        self.buttonaverage.configure(state=DISABLED)
        self.buttonmax.configure(state=NORMAL)
        self.buttonmin.configure(state=NORMAL)
        self.axaverage.plot(self._Store._Constant.AnalyseDataAverageTime, self._Store._Constant.AnalyseDataAverage)
        self.canvasaverage.draw()
        self.canvasaverage.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        return
    
    def ButtonMax_Clicked(self):
        self.currentfig = self.figmax
        self.figall.set_visible(False)
        self.figaverage.set_visible(False)
        self.figmax.set_visible(True)
        self.figmin.set_visible(False)
        self.buttonall.configure(state=NORMAL)
        self.buttonaverage.configure(state=NORMAL)
        self.buttonmax.configure(state=DISABLED)
        self.buttonmin.configure(state=NORMAL)
        self.axmax.plot(self._Store._Constant.AnalyseDataMaxTime, self._Store._Constant.AnalyseDataMax)
        self.canvasmax.draw()
        self.canvasmax.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        return
    
    def ButtonMin_Clicked(self):
        self.currentfig = self.figmin
        self.figall.set_visible(False)
        self.figaverage.set_visible(False)
        self.figmax.set_visible(False)
        self.figmin.set_visible(True)
        self.buttonall.configure(state=NORMAL)
        self.buttonaverage.configure(state=NORMAL)
        self.buttonmax.configure(state=NORMAL)
        self.buttonmin.configure(state=DISABLED)
        self.axmin.plot(self._Store._Constant.AnalyseDataMinTime, self._Store._Constant.AnalyseDataMin)
        self.canvasmin.draw()
        self.canvasmin.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        return
    
    def ButtonAll_Clicked(self):
        self.figall.set_visible(True)
        self.figaverage.set_visible(False)
        self.figmax.set_visible(False)
        self.figmin.set_visible(False)
        self.buttonall.configure(state=DISABLED)
        self.buttonaverage.configure(state=NORMAL)
        self.buttonmax.configure(state=NORMAL)
        self.buttonmin.configure(state=NORMAL)
        self.UI_StartPlot(self)
        return
    
    def ButtonExport_Clicked(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", 
                                                     filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), ("All files", "*.*")])
        if file_path:
            self.currentfig.savefig(file_path)
            tk.messagebox.showinfo("Save Plot", f"Plot saved as {file_path}")
        return