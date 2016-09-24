#!/usr/bin/env python3

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import os
import time
from PIL import ImageTk, Image
from Coliform import *
from datetime import datetime

filepath = os.sep.join((os.path.expanduser('~'), 'Desktop'))
filename = 'TestJPEG.jpeg'
tf = 'PlotTextFile.txt'
if os.path.isfile(tf):
    os.remove(tf)

def heaterpoweron(*args):
    try:
        HeaterPowerStatus.set('Heater ON')
        heaterbutton.configure(text='Heater OFF')
        heaterbutton.configure(command=heaterpoweroff)
        Heater.startHeater(12,100)
        heaterbutton.after(1000,heaterinput)
    except ValueError:
        pass

def heaterinput(*args):
    try:
        if HeaterPowerStatus.get() != 'Heater OFF':
            value = float(temp.get())
            sensor = float(TemperatureNumber[1])
            Heater.HeaterPID(value,sensor)
        heaterbutton.after(1000,heaterinput)
    except ValueError:
        Heater.stopHeater()
        HeaterPowerStatus.set('Heater OFF')
        heaterbutton.configure(text='Heater ON')
        heaterbutton.configure(command=heaterpoweron)
        messagebox.showinfo(message='Please type number into Target Temperature box.')
        heaterbutton.after(1000,heaterinput)

def heaterpoweroff(*args):
    try:
        Heater.stopHeater()
        HeaterPowerStatus.set('Heater OFF')
        heaterbutton.configure(text='Heater ON')
        heaterbutton.configure(command=heaterpoweron)
    except ValueError:
        pass

def onewireon(*args):
    try:
        global ids
        global TemperatureNumber
        ids = OneWire.getOneWireID()
        TemperatureDegrees, TemperatureNumber = getTempList()
        templabel.config(text=TemperatureDegrees)
        MultiPlot.GeneratePlotDataFile(tf,TemperatureNumber,start_time)
        if ids == []:
            TempSensorPowerStatus.set('Temp. Sensor OFF')
            templabel.config(text='NULL')
        else:
            TempSensorPowerStatus.set('Temp. Sensor ON')
        templabel.after(1000,onewireon)
    except IndexError:
        pass

def popupplot(*args):
    try:
        MultiPlot.Plot(tf,len(ids))
    except KeyError:
        messagebox.showinfo(message='No temperature sensor connected.')


def savefile(*args):
    tempfilename = 'TemperatureData.csv'
    OneWire.SaveToCsv(tf,tempfilename,filepath,len(ids))
    messagebox.showinfo(message='File saved to directory.')

# def closebutton(*args):
#     f.close()
#     root.destroy()

def pumppoweron(*args):
    try:
        PumpPowerStatus.set("Pump ON")
        pumpbutton.configure(text='Pump OFF')
        pumpbutton.configure(command=pumppoweroff)
        Pump.startPump(11,pumpintensity.get())

    except ValueError:
        PumpPowerStatus.set("Pump OFF")
        pumpbutton.configure(text='Pump ON')
        pumpbutton.configure(command=pumppoweron)
        Pump.stopPump()
        messagebox.showinfo(message='Please type number from 0-100 into Pump text box.')

def pumppoweroff(*args):
    try:
        PumpPowerStatus.set("Pump OFF")
        pumpbutton.configure(text='Pump ON')
        pumpbutton.configure(command=pumppoweron)

    except ValueError:
        pass

def pumppowerchange(*args):
    try:
        Pump.setPumpIntensity(pumpintensity.get())
    except ValueError:
        messagebox.showinfo(message='Please type number from 0-100 into Pump text box.')

def directorychosen(*args):
    try:
        global filepath
        filepath = filedialog.askdirectory()
    except ValueError:
        pass

def picturetaken(*args):
    try:
        path = filepath
        global filename
        filename = datetime.strftime(datetime.now(),"%Y.%m.%d-%H:%M:%S")+'.jpeg'
        portid = ArduCAM.getSerialPort()
        ArduCAM.TakePicture(path, portid[0], filename)
        messagebox.showinfo(message='JPEG created on directory')
    except (UnboundLocalError, IndexError):
        messagebox.showinfo(message='Arduino not found, make sure it is connected to USB port')

def showimage(*args):
    try:
        global t1
        t1 = Toplevel(mainframe)
        currentimg = ImageTk.PhotoImage(Image.open(os.path.join(filepath, filename)))
        #currentimgs = Image.open(os.path.join(filepath, filename))
        imglabel = Label(t1, image=currentimg)
        imglabel.pack(side='bottom', fill='both',expand='yes')
        #currentimgs.show()
        currentimg.show()
    except FileNotFoundError:
        t1.destroy()
        messagebox.showinfo(message='File not found, make sure you selected the correct directory.')

#def quitwindow(*args):
#    try:
#        t1.destroy()
#    except ValueError:
#        pass

root = Tk()
root.title("Coliform Control GUI")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

temp = StringVar()
PumpPowerStatus = StringVar()
HeaterPowerStatus = StringVar()
TempSensorPowerStatus = StringVar()
pumpintensity = StringVar()

HeaterPowerStatus.set('Heater OFF')
PumpPowerStatus.set("Pump OFF")

masterpane = ttk.Panedwindow(mainframe, orient=VERTICAL)

toppane = ttk.Panedwindow(masterpane, orient=HORIZONTAL)

f2 = ttk.Labelframe(toppane, text='Temperature Sensor:', width=100, height=100)
f3 = ttk.Labelframe(toppane, text='Heater:', width=100, height=100)
toppane.add(f2)
toppane.add(f3)
masterpane.add(toppane)

templabel = ttk.Label(f2)
templabel.grid(column=1, row=2, sticky=(W))
ttk.Label(f2, text="Temperature:").grid(column=1, row=1, sticky=W)
ttk.Button(f2, text='Show Plot', command=popupplot).grid(column=2,row=1,sticky=E)
ttk.Button(f2, text='Save Data File', command=savefile).grid(column=2,row=2,sticky=(S,E))

temp_entry = ttk.Entry(f3, width=7, textvariable=temp)
temp_entry.grid(column=2, row=1, sticky=(W, E))
ttk.Label(f3, text="Target Temperature:").grid(column=1, row=1, sticky=W)
heaterbutton = ttk.Button(f3, text="Heater ON", command=heaterpoweron)
heaterbutton.grid(column=1, row=2, sticky=W)

bottompane = ttk.Panedwindow(masterpane, orient=HORIZONTAL)
f1 = ttk.Labelframe(bottompane, text='Status:', width=100, height=100)
f4 = ttk.Labelframe(bottompane, text='Pump:', width=100, height=100)
f5 = ttk.Labelframe(bottompane, text='Camera:', width=100, height=100)
bottompane.add(f4)
bottompane.add(f5)
bottompane.add(f1)
masterpane.add(bottompane)

pumpbutton = ttk.Button(f4, text="Power ON", command=pumppoweron)
pumpbutton.grid(column=1, row=1, sticky=W)
pumpchangebutton = ttk.Button(f4, text="Submit", command=pumppoweron)
pumpchangebutton.grid(column=1, row=3, sticky=(W, E))
pump_entry = ttk.Entry(f4, width=4, textvariable=pumpintensity)
pump_entry.grid(column=1, row=2, sticky=(W, E))

ttk.Button(f5, text="Take Picture", command=picturetaken).grid(column=1, row=1, sticky=(E,W))
ttk.Button(f5, text="Choose Directory",command=directorychosen).grid(column=1, row=2, sticky=E)
ttk.Button(f5, text="Show Last Image", command=showimage).grid(column=1, row=4, sticky=(E,W))

tempsensorstatus = ttk.Label(f1, textvariable=TempSensorPowerStatus).grid(column=1, row=1, sticky=(W, E))
pumpstatus = ttk.Label(f1, textvariable=PumpPowerStatus).grid(column=1, row=2, sticky=(W, E))
heaterstatus = ttk.Label(f1, textvariable=HeaterPowerStatus).grid(column=1, row=3, sticky=(W, E))

for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

temp_entry.focus()
start_time = time.time()
onewireon()
heaterinput()
root.mainloop()