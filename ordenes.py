from multiprocessing import Process
from binance.client import Client
from json import load
import check_exe
with open('json_data.json') as json_file:
    claves = load(json_file)
client = Client(claves['shercan']['key'],claves['shercan']['secret'])
def stop_loss(datos,position:str):
    #print(position)
    if position=='BUY':
        pos='SELL'
        stop=round(float(datos['price'])*(1.002-datos['stop']),1)
        price=round(float(datos['price'])*(1-datos['stop']),1)
    elif position=='SELL':
        pos='BUY'
        stop=round(float(datos['price'])*(0.998+datos['stop']),1)
        price=round(float(datos['price'])*(1+datos['stop']),1)
    #print(stop,price,pos,datos)
    stop=client.futures_create_order(
        symbol=datos['symbol'], 
        side=pos, 
        type='STOP',
        quantity=datos['quantity'],
        price=price,
        stopPrice=stop,
        reduceOnly=True
        )
    #print(stop)
    order_exe=Process(target= check_exe.create_order_exe, args=(datos,stop['orderId'],'stop',))
    order_exe.start()    
def take_profit(datos,position:str):
    if position=='BUY':
        pos='SELL'
        stop=round(float(datos['price'])*(0.998+datos['take_l']),1)
        price=round(float(datos['price'])*(1+datos['take_l']),1)
    elif position=='SELL':
        pos='BUY'
        stop=round(float(datos['price'])*(1.002-datos['take_s']),1)
        price=round(float(datos['price'])*(1-datos['take_s']),1)
    take=client.futures_create_order(
        symbol=datos['symbol'],
        side=pos,
        type='TAKE_PROFIT',
        quantity=datos['quantity'],
        price=price,
        stopPrice=stop,
        reduceOnly=True
        )
    #print(take)
    order_exe=Process(target= check_exe.create_order_exe, args=(datos,take['orderId'],'take',))
    order_exe.start()    