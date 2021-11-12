#!/usr/bin/env python
# coding: utf-8

#librerías
import requests
import os
import json
import pandas as pd
from datetime import datetime


# ## Llamar al api de twitter

# este token da la autorización para hacer las peticiones a la API de twitter
bearer_token = os.environ['BEARER_TOKEN']

# url y parámetros para api v2
search_url = 'https://api.twitter.com/2/tweets/search/recent'
#en query se puede poner un topic o aquello de lo que se quiera hacer la búsqueda
#la documentación de twitter también explica como seguir los tweets de un usuario concreto
query_params = {'query':"@repsol", 'max_results':100, 'tweet.fields':'created_at,text'}

#esta función "carga" el token para permitir la autorización
def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

# esta otra se conecta a la url que le hemos pedido con los parámetros indicados
def connect_to_endpoint(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

# finalmente, esta función nos devuelve un dataframe con las columnas de fecha y texto. Se pueden "parsear" más campos
# si fuera necesario, ya que para cada tweet hay bastante información 
def tweets_v2():
    json_response=connect_to_endpoint(search_url, query_params)
    cat=[]
    for x in json_response['data']:
        tweets = {}
        tweets['Fecha']  = x['created_at']
        tweets['Texto']  = x['text']
        cat.append(tweets)
    db = pd.DataFrame(cat)
    return db

# aquí asignamos la salida de la función anterior a una variable, para poder trabajar con el resultado
db = tweets_v2()

# con esto guardo en mi local el fichero, añadiendo al nombre el tiempo en el se guarda, 
# para asegurarme de que siempre tienen nombres distintos
from datetime import datetime
now = datetime.now()
current_time = now.strftime("%H_%M_%S")

ruta='salidas_api_twitter/'+str(current_time)+'.xlsx'

db.to_excel(ruta, encoding='latin1')


# ## Meanincloud

# aquí el proceso es similar que al de twitter, con un token de mi cuenta personal y la url final llamo al api de 
# meaningcloud para "pasarle" un texto y que me devuelva su valoración respecto a la reputación
def meaningcloud(texto):    
    token= os.environ['MEANINGCLOUD_TOKEN']
    endpoint='https://api.meaningcloud.com/reputation-2.0'
    texto=texto
    payload={
        'key': token,
        'txt': texto,
        'lang': 'auto',
    }
    response = requests.post(endpoint, data=payload)
    print('Status code:', response.status_code)
    return(response.json())

#también similar al caso de twitter, con esta función tomo el resultado de la función anterior y asigno el
#tipo de reputación y la polaridad
def tipe(texto):
    try:
        respon=meaningcloud(texto)
        for ent in respon['entity_list']:
            tipe = {}
            tipe['code']  = ent['category_list'][0]['code']
            tipe['polarity']  = ent['category_list'][0]['polarity']
        return tipe
    except:
        return {}        

#nutro el dataframe anterior pasando por meaningcloud todos los tweets, uno a uno, y escribiendo el resutlado en una 
# columna nueva. Tarda unos segundos por cada petición.
db['code']=db.apply(lambda row: tipe(row['Texto']), axis=1)


#guardamos los resultados para enviarlos a Maca y Lorenzo todos los días
import datetime
today = datetime.date.today()

ruta='salidas_api_twitter/polaridad/'+str(today)+'.xlsx'
db.to_excel(ruta, encoding='latin1')

# aquí damos varios pasos, primero tomar la columna de resultdos y convertirla en un dataframe aparte, con las columnas
# de tipo y polaridad
# db_2=db['code'].apply(pd.Series)
# 
# #nos quitamos los vacios
# db_2=db_2.dropna()
# 
# #convertimos la polaridad en una escala numérica para poder operar
# db_2=db_2.replace({'P+':5,'P':4,'NEU':3,'NONE':3,'N':2,'N+':1})
# 
# #agrupamos por tipo, en este caso creando una media simple, aunque se puede hacer un NPS como tal u otro índice
# nps=pd.DataFrame(db_2.groupby('code')['polarity'].apply(lambda x: x.mean())).reset_index()
