import sys
import tkinter
from tkinter import messagebox
import snipeit_api
from systeminfo import sysInfo

systemInformation = sysInfo
createFlag = False
assetExists = snipeit_api.CheckIfExists(serial_number=systemInformation['Serial_Number'],hostname=systemInformation['Hostname'])

window = tkinter.Tk()

def DisplaySysInfo(systemInformation, container):

    for entry in systemInformation:
        newLabel = tkinter.Label(master=container,text="{0}: {1}".format(entry,systemInformation[entry]))
        newLabel.pack(anchor=tkinter.W)

def Button_UpdateAsset(systemInformation):
    asset_id = snipeit_api.GetAssetID(serial_number=systemInformation['Serial_Number'],hostname=systemInformation['Hostname'])

    if(asset_id != None):

        updateResult = snipeit_api.UpdateAsset(systemInformation,None)

        if(updateResult is True):
            messagebox.showinfo('Success', 'Asset successfully updated')
        else:
            messagebox.showerror('Error', 'Asset was unable to be updated.')
    else:
        messagebox.showerror('Error', 'Asset was unable to be updated.')

def Button_CreateAsset(systemInformation):

    if(createFlag is False):
        createResult = snipeit_api.CreateNewAsset(systemInformation)

        if(createResult is True):
            messagebox.showinfo('Success', 'Asset successfully created')
        else:
            messagebox.showerror('Error', 'Asset was unable to be created.')
    else:
        messagebox.showerror('Error', 'You already created this asset.')

def PopupMessage(title,text):
    popup = tkinter.Tk()
    popup.title(title)
    popupFrame = tkinter.Frame(padx=10,pady=10)
    tkinter.Label(master=popupFrame,text=text).pack()
    tkinter.Button(master=popupFrame,text='Close',command=popup.destroy).pack()
    popupFrame.pack()
    popup.mainloop()

systemInfo_frame = tkinter.Frame(padx=10,pady=10,borderwidth=2)

tkinter.Label(master=systemInfo_frame,text='System Specifications:',font=('Arial', 25)).pack(anchor=tkinter.W)

DisplaySysInfo(systemInformation, systemInfo_frame)

systemInfo_frame.pack(anchor=tkinter.W)

choice_frame = tkinter.Frame(padx=10,pady=10)

if(assetExists == True):
    tkinter.Label(master=choice_frame,text='An asset with this hostname or serial number already exists in Snipe-IT.').pack(anchor=tkinter.W)
    tkinter.Label(master=choice_frame,text='Update Asset?').pack(anchor=tkinter.CENTER)
    tkinter.Button(master=choice_frame,text='Update',command=lambda:Button_UpdateAsset(systemInformation)).pack(anchor=tkinter.CENTER)
else:
    tkinter.Label(master=choice_frame,text="This asset does not exist within Snipe-IT.").pack(anchor=tkinter.W)
    tkinter.Label(master=choice_frame,text='Create Asset?').pack(anchor=tkinter.CENTER)
    tkinter.Button(master=choice_frame,text='Create',command=lambda:Button_CreateAsset(systemInformation)).pack(anchor=tkinter.CENTER)

choice_frame.pack()

window.mainloop()