from AppData import AppData as _AppData
from Store import Store as _Store
from AppUI import AppUI as _AppUI

_Store.__init__(_Store)
_AppData.__init__(_AppData, _Store)

#Datenbank initialisieren
_AppData.Database_Initialize(_AppData)

#Daten aus Datenbank in Store speichern
_AppData.Database_DataToStore(_AppData)

#Window inititialisieren
_AppUI.__init__(_AppUI, _AppData, _Store)
_AppUI.Window_Initialize(_AppUI)

#Window-Benutzeroberfläche erzeugen
_AppUI.Window_Initialize_UI(_AppUI)

#Window aktivieren
_AppUI.Window_Activate(_AppUI)