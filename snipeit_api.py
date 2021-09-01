from os import system
import requests

appkey = None #API KEY HERE
api_url = None #PUT API URL HERE

headers = {
    'Accept': 'application/json', 
    'Content-Type' : 'application/json', 
    'Authorization' : 'Bearer {0}'.format(appkey)
    }

class Error():

    #Error Types: 'API Error', 'Workflow Error', 'Does Not Exist'
    error_type = None
    error_message = None

    def __init__(self, type, message):
        self.error_type = type
        self.error_message = message


#Checks if the asset exists by querying Snipe IT for provided variables
def CheckIfExists(hostname=None, serial_number=None):

    assetExists = False

    if(type(QueryHostname(hostname)) is not Error or type(QuerySerialNumber(serial_number)) is not Error):
        assetExists = True
    
    return assetExists

def GetAssetID(hostname=None,serial_number=None):

    serialnumberQuery = QuerySerialNumber(serial_number)
    hostnameQuery = QueryHostname(hostname)

    if(type(serialnumberQuery) is not Error):
        return serialnumberQuery['id']
    elif(type(hostnameQuery) is not Error):
        return hostnameQuery['id']
    else:
        return None

    
#Grabs the appropriate information to update hardware information.
def GenerateAssetPayload(system_info):

    modelInformation = QueryModelNumber(system_info['Model'])

    if(type(modelInformation) is not Error):

        payload = {
            'model_id': modelInformation['id'],
            'status_id':1,
            'name':system_info['Hostname'],
            '_snipeit_cpu_5':system_info['Processor'],
            '_snipeit_hostname_4':system_info['Hostname'],
            '_snipeit_ram_6':system_info['Ram_Size'],
            '_snipeit_ram_type_12':system_info['Ram_Type'],
            '_snipeit_operating_system_3':system_info['Operating System'],
            'serial':system_info['Serial_Number']
        }

        return payload

    else:
        #Return error information back down
        return modelInformation

def CreateNewAsset(system_info):

    payload = GenerateAssetPayload(system_info)

    if(type(payload) is not Error):
        query = api_url+'/hardware'
        PostRequest(query=query,payload=payload)
        return True
    else:
        return payload

def UpdateAsset(system_info, asset_id):
    payload = GenerateAssetPayload(system_info)
    if(type(payload) is not Error and asset_id != None):
        query = api_url+'/hardware/{0}'.format(asset_id)
        PatchRequest(query,payload)
        return True
    else:
        return payload

def GetRequest(query, parameters=None):
    response = requests.request("GET", query, headers=headers,params=parameters)
    response_data = response.json()

    if(response.status_code == 404):
        return Error('API Error','404 Error')
    else:
        return response_data

def PostRequest(query, payload=None):
    response = requests.request("POST", query, headers=headers,json=payload)

def PatchRequest(query,payload=None):
    response = requests.request("PATCH", query,headers=headers, json=payload)

#Recursion method, seperates a desired nested dictionary
def QueryForDictionary(nested_dict,target_dictionary):

    if(target_dictionary in nested_dict):
        return nested_dict[target_dictionary]

    for key, value in nested_dict.items():

        if(type(value) is dict):
            funcResult = QueryForDictionary(value,target_dictionary)
            if(funcResult != None):
                return funcResult 

def QueryHostname(hostname):
    
    if(hostname!=None):
        query = api_url+'/hardware/'
        hostnameData = GetRequest(query=query,parameters={'search':hostname})
        
        #In the event of a 404 Error.
        if(type(hostnameData) == Error):
            return hostnameData

        elif(hostnameData['total'] != 0):

            #TODO Add Support for multiple results for querying the same hostname
            #Issue with this going forward: Multiple matches to host names. Duplicate entries? How to handle this?
            hostnameData = hostnameData['rows'][0]

            hostnameField = QueryForDictionary(hostnameData,'Hostname')

            if(hostnameField['value'] == hostname):
                    return hostnameData            
            else:
                return Error('DNE Error',"Asset with this hostname doesn't exist")       
        else:
            return Error('DNE Error', "Asset with this hostname doesn't exist")   
    else:
        return Error('Invalid Input Error',"No hostname provided")
        
def QuerySerialNumber(serial_number):
    
    if(serial_number!=None):
        query = api_url+'/hardware/byserial/{0}'.format(serial_number)
        serialData = GetRequest(query=query)

        
        if(type(serialData) is Error):
            return serialData

        elif(serialData['total'] != 0):
            serialData = serialData['rows'][0]
            return serialData
        
        else:
            return Error('DNE Error',"Asset with this model number doesn't")
    else:
        return Error('Invalid Input Error',"No model number provided")

def QueryModelNumber(model_number):

    if(model_number != None):
        query = api_url+'/models/'
        modelData = GetRequest(query=query,parameters={'search':model_number})
        
        #In the event of a 404 Error.
        if(type(modelData) is Error):
            return modelData

        elif(modelData['total'] != 0):

            modelData = modelData['rows'][0]
            
            #You have to verify this, sometimes other strings get caught in the search.
            if(modelData['model_number'] == model_number):
                return modelData
            else:
                return Error('DNE Error',"Model doesn't exist in the database.")
        
        else:
            #Return the error
            return Error('DNE Error', "Model doesn't exist in the database.")
    else:
        return Error('Invalid Input Error',"No model number provided")
