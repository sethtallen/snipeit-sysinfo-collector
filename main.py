import sys
import snipeit_api
from systeminfo import sysInfo

systemInformation = sysInfo

assetExists = snipeit_api.CheckIfExists(serial_number=systemInformation['Serial_Number'],hostname=systemInformation['Hostname'])

if(assetExists is False):
    print("Asset doesn't exist. Creating new one.")
    snipeit_api.CreateNewAsset(systemInformation)

else:

    asset_id = snipeit_api.GetAssetID(serial_number=systemInformation['Serial_Number'],hostname=systemInformation['Hostname'])

    if(asset_id != None):
        print('Updating Asset')
        snipeit_api.UpdateAsset(systemInformation,asset_id)

    else:
        print("Can't verify asset identity")