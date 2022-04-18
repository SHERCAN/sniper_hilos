from asyncio import sleep
from json import load
from time import sleep
from binance.client import Client
import ordenes
with open('json_data.json') as json_file:
    claves = load(json_file)
client = Client(claves['shercan']['key'],claves['shercan']['secret'])
def create_order_exe(datos,orderId,intro:str):
    while True:
        order=client.futures_get_order(orderId=orderId,symbol=datos['symbol'])
        print(intro,order['status'],order['orderId'])
        if order['status']=='FILLED' and intro=='create':
            datos['price']=order['avgPrice']
            ordenes.stop_loss(datos,datos['side'])
            ordenes.take_profit(datos,datos['side'])
            break            
        if (order['status']=='FILLED' and intro=='stop') or order['status']=='CANCELED':
            client.futures_cancel_all_open_orders(symbol=datos['symbol'])
            break
        if (order['status']=='FILLED' and intro=='take') or order['status']=='CANCELED':
            client.futures_cancel_all_open_orders(datos['symbol'])
            break
        sleep(2)