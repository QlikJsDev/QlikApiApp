import streamlit as st
import requests
from cProfile import run
from pickle import TRUE
import websocket
import ssl
import sqlite3
import os
from pathlib import Path
import datetime
import time
import json
import pandas as pd
import math


server_name ="wss://sensedev.agilos.com/apis/app/"
header_name='api_usr'
header_user_name='agilos\\mge'

finalResponse=''

# Titre de l'application
st.title("Lead Time App")

# Champ de saisie pour le nombre
nombre = st.number_input("Requested Quantity :", min_value=0, step=1)

# Liste déroulante pour choisir une option
options = ["991.8310.52", "991.1542.01", "991.2368.34"]
choix = st.selectbox("Item Number :", options)

def first_connect(server_name,header_name,header_user_name):
    #################################################################################################################################
    # First connection to api and get cookie header
    header_user = {header_name: header_user_name}

    # Path to the file/directory
    path = r"Cookie_headers.txt"
    
    ti_c = os.path.getctime(path)
    ti_m = os.path.getmtime(path)

    modification_time=datetime.datetime.fromtimestamp(ti_m)
    current_time=datetime.datetime.now()

    if modification_time>current_time-datetime.timedelta(minutes = 5):
        with open('Cookie_headers.txt') as f:
            lines = f.readlines()
        
        cookie_header=lines[0]
    
    else:
        ws = websocket.create_connection(server_name, sslopt={"cert_reqs": ssl.CERT_NONE},header=header_user)
        cookie_header=ws.headers['set-cookie']

        ws.close()

        with open('Cookie_headers.txt', 'w') as f:
            f.write(cookie_header)

    print('Connection')
    return cookie_header

    #################################################################################################################################

###################################################################################
# Open document
###################################################################################
def open_doc(server_name,header_name,header_user_name,doc_id,cookie_header):
    ###################################################################################
    #print('Open Doc '+str(doc_id)+' : ') #FOR EACH DOC
    ###################################################################################

    header_user = {header_name: header_user_name}

    # Path to the file/directory
    path = r"Cookie_headers.txt"
    
    ti_c = os.path.getctime(path)
    ti_m = os.path.getmtime(path)

    modification_time=datetime.datetime.fromtimestamp(ti_m)
    current_time=datetime.datetime.now()

    if modification_time>current_time-datetime.timedelta(minutes = 5):
        with open('Cookie_headers.txt') as f:
            lines = f.readlines()
        
        cookie_header_stored=lines[0]

        ws = websocket.create_connection(server_name, sslopt={"cert_reqs": ssl.CERT_NONE},header={header_name: header_user_name,'Cookie': 'X-Qlik-Session-api='+cookie_header_stored.split('X-Qlik-Session-api=')[1].split(';')[0]})

    
    else:
        ws = websocket.create_connection(server_name, sslopt={"cert_reqs": ssl.CERT_NONE},header=header_user)
        cookie_header=ws.headers['set-cookie']
        ws.close()

        with open('Cookie_headers.txt', 'w') as f:
            f.write(cookie_header)

        ws = websocket.create_connection(server_name, sslopt={"cert_reqs": ssl.CERT_NONE},header={header_name: header_user_name,'Cookie': 'X-Qlik-Session-api='+cookie_header.split('X-Qlik-Session-api=')[1].split(';')[0]})
    
    ws.send(json.dumps({
        "method": "OpenDoc",
        "handle": -1,
        "params": [
            doc_id
        ],
        # "params": [{
        #     'qDocName':doc_id,
        #     'qNoData': True
        # }  
        # ],
        "headers":{
            'Cookie': 'X-Qlik-Session-api='+cookie_header.split('X-Qlik-Session-api=')[1].split(';')[0]
        },
        "outKey": -1,
        "id": 2
    }))


    result = ws.recv()
    vDocOpen = json.loads(result)
    result = ws.recv()
    vDocOpen = json.loads(result)

    # Time sleep shoul be dependant of app size
    time.sleep(1)

    return ws


###################################################################################
# Close document
###################################################################################
def close_doc(ws):
    ws.close()




###################################################################"
# get Hypercube Data
# ##################################################################

def get_hypercube_data(server_name,header_name,header_user_name,doc_id,obj_id,cookie_header):

    ws=open_doc(server_name,header_name,header_user_name,doc_id,cookie_header)

    ######################################
    ## Change variable value
    #######################################
    ws.send(json.dumps({
                "handle": 1,
                "method": "GetVariableById",
                "params": {
                    "qId": "23471c3d-4499-4933-a71f-fc77fff6b519"
                }
            }
            ))
    result = ws.recv()
    vAppReloaded = json.loads(result)
    print(vAppReloaded)

    ws.send(json.dumps({
                "handle": 2,
                "method": "SetNumValue",
                "params": {
                    "qVal": nombre
                },
                "outKey": -1,
                "id": 5
            }
            ))

    result = ws.recv()
    vAppReloaded = json.loads(result)
    print(vAppReloaded)

    #############################################
    ws.send(json.dumps({
            "handle": 1,
            "method": "GetObject",
            "params": {
                "qId": obj_id #"njXEN"
            },
            "outKey": -1,
            "id": 5
        }))
   

    time.sleep(1)
    print('HEY')
    result = ws.recv()
    vAppReloaded = json.loads(result)
    print(vAppReloaded)
    result = ws.recv()
    vAppReloaded = json.loads(result)
    print(vAppReloaded)

    ws.send(json.dumps({
            "handle": 3,
            "method": "GetHyperCubeData",
            "params": {
                "qPath": "/qHyperCubeDef",
                "qPages": [ # limited to 10000 cells (Lines*Columns)
                    {
                        "qLeft": 0,
                        "qTop": 0,
                        "qWidth": 1, #number of Columns
                        "qHeight": 1 # number of lines
                    }
                ]
            },
            "outKey": -1,
            "id": 13
        }))


    result = ws.recv()
    vAppReloaded = json.loads(result)
    print(vAppReloaded)
    finalResponse=vAppReloaded
    st.success(f"Réponse API : {vAppReloaded}")

    ws.close()
##########################################################################################################



# Bouton pour envoyer la requête
if st.button("Envoyer la requête"):
    cookie_header=first_connect(server_name,header_name,header_user_name)

    get_hypercube_data(server_name,header_name,header_user_name,'baaebc6d-7e88-4394-8fea-49a28c3bc258','ZNeYhA',cookie_header)

    