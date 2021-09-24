import multiprocessing
multiprocessing.freeze_support()

import sys
import tkinter
from tkinter import Radiobutton, Text, messagebox
from tkinter.constants import BOTTOM, END
import snipeit_api
import systeminfo

systemInformation = systeminfo.sysInfo
createFlag = False
assetExists = snipeit_api.CheckIfExists(serial_number=systemInformation['Serial_Number'],hostname=systemInformation['Hostname'])
radio_selection = 'Desktops'

window = tkinter.Tk()
window.title("Snipe-IT Asset Logger")

def DisplaySysInfo(systemInformation, container):

    for entry in systemInformation:
        newLabel = tkinter.Label(master=container,text="{0}: {1}".format(entry,systemInformation[entry]))
        newLabel.pack(anchor=tkinter.W)

def Button_UpdateAsset(systemInformation,notes):
    asset_id = snipeit_api.GetAssetID(serial_number=systemInformation['Serial_Number'],hostname=systemInformation['Hostname'])

    if(asset_id != None):

        updateResult = snipeit_api.UpdateAsset(systemInformation,asset_id,notes=notes)

        if(updateResult is True):
            messagebox.showinfo('Success', 'Asset successfully updated')
        else:
            messagebox.showerror('Error', 'Asset was unable to be updated.')
    else:
        messagebox.showerror('Error', 'Asset was unable to be updated.')

def Button_CreateAsset(systemInformation,notes):

    if(createFlag is False):
        createResult = snipeit_api.CreateNewAsset(systemInformation,notes)

        if(createResult is True):
            messagebox.showinfo('Success', 'Asset successfully created')
        else:
            messagebox.showerror('Error', 'Asset was unable to be created.')

    choice_frame.destroy()
    tkinter.Button(master=window,text='Close',command=window.destroy,pady=10).pack()

def Button_CreateModel(model_name,device_type,modelframe):
    createResult = snipeit_api.CreateModel(systemInformation,model_name,device_type)
    modelframe.destroy()

    if(createResult is True):
        messagebox.showinfo('Success', 'Model successfully created')
    else:
        messagebox.showerror('Error', 'Model was unable to be created.')

    ShowChoiceFrame()

def ShowChoiceFrame():

    notes_entry = tkinter.Text(master=choice_frame,height=5,pady=5)
    tkinter.Label(master=choice_frame,text='Notes').pack(anchor=tkinter.W)
    notes_entry.pack(anchor=tkinter.CENTER)

    if(assetExists == True):
        tkinter.Label(master=choice_frame,text='An asset with this hostname or serial number already exists in Snipe-IT.',pady=10).pack(anchor=tkinter.W)
        tkinter.Label(master=choice_frame,text='Update Asset?').pack(anchor=tkinter.CENTER)
        tkinter.Button(master=choice_frame,text='Update',command=lambda:Button_UpdateAsset(systemInformation,notes_entry.get('1.0',END))).pack(anchor=tkinter.CENTER)
    else:
        tkinter.Label(master=choice_frame,text="This asset does not exist within Snipe-IT.",pady=10).pack(anchor=tkinter.W)
        tkinter.Label(master=choice_frame,text='Create Asset?').pack(anchor=tkinter.CENTER)
        tkinter.Button(master=choice_frame,text='Create',command=lambda:Button_CreateAsset(systemInformation,notes_entry.get('1.0',END))).pack(anchor=tkinter.CENTER)

systemInfo_frame = tkinter.Frame(padx=10,pady=10,borderwidth=2)

tkinter.Label(master=systemInfo_frame,text='System Specifications:',font=('Arial', 25)).pack(anchor=tkinter.W)

DisplaySysInfo(systemInformation, systemInfo_frame)

systemInfo_frame.pack(anchor=tkinter.W)

choice_frame = tkinter.Frame(padx=10,pady=10)

if(snipeit_api.CheckModelNumber(systemInformation['Model']) is False):
    model_frame = tkinter.Frame(padx=10,pady=10)
    input_frame = tkinter.Frame(master=model_frame,pady=5)
    #radio_frame = tkinter.Frame(master=model_frame,padx=10,pady=10)
    #tkinter.Label(master=radio_frame,text='Device Type:').pack(side=tkinter.TOP)
    #R1 = Radiobutton(radio_frame,text='Desktop',variable=radio_selection, value='Desktops')
    #R2 = Radiobutton(radio_frame,text='Laptop',variable=radio_selection, value='Laptops')
    #R1.pack(side=tkinter.LEFT)
    #R2.pack(side=tkinter.RIGHT)
    #radio_frame.pack(side=tkinter.TOP)
    tkinter.Label(master=input_frame,text='Please input the device model name (Not the model number):').pack(side=tkinter.LEFT)
    model_entry = tkinter.Entry(master=input_frame)
    model_entry.pack(side=tkinter.RIGHT)
    input_frame.pack()
    model_button = tkinter.Button(master=model_frame,text='Submit',command=lambda:Button_CreateModel(model_name=model_entry.get(),modelframe=model_frame,device_type='Desktops'))
    tkinter.Label(master=model_frame,text='Ex: Lenovo ThinkCentre M800 M/N: 10FY0015US -> ThinkCentre M800').pack(side=tkinter.TOP)
    model_button.pack(side=tkinter.BOTTOM)
    model_frame.pack()
else:
    ShowChoiceFrame()

choice_frame.pack()
window.update()
window.mainloop()