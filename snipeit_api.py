from os import name, system
import requests
from requests import api

appkey = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiNTQ5ZDU1OGIxOTE4MjdmMTgxOWEwNjFiNDJiMjgyZGVhNzIxYWM0Y2FjM2Y1Y2MyNWFlZTQ5YTAyZjhkNmEzNjE2MmRkZDVkMGQ4ZWZlNjMiLCJpYXQiOjE2MjkzODQzNzUuNTE4NjMyLCJuYmYiOjE2MjkzODQzNzUuNTE4NjM0LCJleHAiOjI4OTE2ODgzNzUuNDkwODYxLCJzdWIiOiIxIiwic2NvcGVzIjpbXX0.m-Ognw_S46c0JDtFqQUCK8Tu7D3ZTa8366FeJhrnw583xpoHTBMdieVdrlpZW9xdcHATLzKfksIJ-o6LmQBwoCuXd0D-jcGMJ540-ODuDhiIChGOi8C_VzJ2v_ONHBuvvlqeOpBOijHaIFS-fIu-HewpCC2AZd-ZPcynj9X8m7RRzfA6zMjUaiGdcEZctMAKOYtactMFzir0WM3YayZcTHt3AuMoZhZPMTBAKNiwO9WgeXuVul4eVkpk-x5gd1k9bGX7kN58_qpvTJZIG4mmp4pLdMvRtW40Z2xN8-fyXKvVj7gxu-uOU6b0aPHscnXEZNq95NsQBlNOVDXTnweM4nr0YBVYR2UVsdih_3iWF5e-g8vdXtWyFHGuQ3sYetzCIlcNhMwL1jRbOtm7mfaXEtv5fGTNilNgEei_Vi_FiFKIE4xFyOoJf-qsaqZa6Dkq0uHUw9zqYmX7AhF8DUPeTZ5iBKddFwLafFQlD4h3fM3Dg3XSYn7HpxFfH3W6aWC5zrJmOqlA8gaMM_xRQ2K-SGhD9G-cU1vVWZMTfIld7-GI0b6xxg48EC3AUaGY6dyE1Mt2HimnqwM8kmorCBw8mz75eo2VwR4CXSGyNDEsoII0mTB67twclePKcpKAkgHSjkrSfsGH_3spnRuyfQR17kkueuOHDib7VaKg-d9mjcE' #API KEY HERE
api_url = 'http://snipeit.kenmarkopt.com/api/v1' #PUT API URL HERE

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


def CheckModelNumber(model_name=None):

    if(model_name is not None):
        modelResult = QueryModelNumber(model_name)

        if(type(modelResult) is not Error):
            return True
        else:
            return False


#Checks if the asset exists by querying Snipe IT for provided variables
def CheckIfExists(hostname=None, serial_number=None):

    assetExists = False

    if(type(QuerySerialNumber(serial_number)) is not Error):
        assetExists = True
    #elif(type(QueryHostname(hostname)) is not Error):
        #assetExists = True
    
    return assetExists

def GetAssetID(hostname=None,serial_number=None):

    serialnumberQuery = QuerySerialNumber(serial_number)
    #hostnameQuery = QueryHostname(hostname)

    if(type(serialnumberQuery) is not Error):
        return serialnumberQuery['id']
    #elif(type(hostnameQuery) is not Error):
        #return hostnameQuery['id']
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
    payload['asset_tag'] = system_info['Serial_Number']

    print(payload)

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
    return response

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

def CreateModel(systemInfo,model_name,device_category):
    
    query = api_url+'/models'
    category = QueryForCategory('Desktops')
    manufacturer = QueryForManufacturer(systemInfo['Manufacturer'])
    fieldset = QueryForFieldset('Desktop')

    if(type(manufacturer) is Error):
        CreateManufacterer(systemInfo['Manufacturer'])
        manufacturer = QueryForManufacturer(systemInfo['Manufacturer'])

    if(type(query) is not Error):
        
        payload = {
            'name': model_name,
            'model_number': systemInfo['Model'],
            'category_id': category['id'],
            'manufacturer_id': manufacturer['id'],
            'fieldset_id': fieldset['id']
        }

        response = PostRequest(query,payload)

        return response

def QueryForCategory(device_type):
    query = api_url+'/categories'
    categoryList = GetRequest(query)
    for category in categoryList['rows']:
        if(category['name'] == device_type):
            return category

    return Error('DNE','DNE')

def QueryForFieldset(fieldset_name):
    query=api_url+'/fieldsets'
    fieldsetList = GetRequest(query=query)
    
    for fieldset in fieldsetList['rows']:
        if(fieldset['name'] == fieldset_name):
            return fieldset
    
    return Error('DNE','DNE')

def CreateManufacterer(manufacturer_name):
    query=api_url+'/manufacturers'
    PostRequest(query=query,payload={'name':manufacturer_name})

def QueryForManufacturer(manufacturer_name):
    query = api_url+'/manufacturers'
    manufacturerList = GetRequest(query=query)
    
    for manufacturer in manufacturerList['rows']:
        if(manufacturer['name'].lower() == manufacturer_name.lower()):
            return manufacturer
    
    return Error('DNE Error', "Don't exist")