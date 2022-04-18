# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 14:46:33 2022

@author: Yesid Farfan
"""
from threading import Thread
#modules
import imaplib,requests
import email
from json import load, loads
from time import sleep
from binance.client import Client
from check_exe import create_order_exe
datos={'side':'','id':'','symbol':'','quantity':'',
'price':'','take_l':0.009,'take_s':0.017,'stop':0.03}
with open('json_data.json') as json_file:
    claves = load(json_file)
client = Client(claves['shercan']['key'],claves['shercan']['secret'])
datos['take_l']=claves['limits']['take_l']
datos['take_s']=claves['limits']['take_s']
datos['stop']=claves['limits']['stop']
#credentials
username =claves['account']['mail']
#generated app password
app_password= claves['account']['mail']
# https://www.systoolsgroup.com/imap/
gmail_host= 'imap.gmail.com'
#set connection
mail = imaplib.IMAP4_SSL(gmail_host)
#login
mail.login(username, app_password)
#select inbox
mail.select("INBOX")
#select specific mails

mail_nuevo=''
saldo=0
precio_anterior=0
porcentaje=0
posicion=''

def create_order(position:str,symbol:str):
    datos['symbol']=symbol.replace('PERP','')
    balance=client.futures_account_balance()
    balance=2.1#[x['balance'] for x in balance if x['asset']=='BUSD'][0]
    #print(balance)
    try:
        client.futures_cancel_all_open_orders(symbol=symbol)
    except:
        pass
    """ order=client.futures_create_order(
        symbol=datos['symbol'], 
        side=position, 
        type='MARKET', 
        quantity=str((balance*30)/float(
            client.futures_symbol_ticker(symbol=datos['symbol'])['price']))[0:5]
        ) """
    datos['side']=position
    datos['quantity']=0.001#order['origQty']
    datos['id']=5331681067#order['orderId']
    #print(datos)
    order_exe=Thread(target= create_order_exe, args=(datos['id'],'create',))
    order_exe.start()    
    #print(order)
def stop_loss(position:str):
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
    order_exe=Thread(target= create_order_exe, args=(stop['orderId'],'stop',))
    order_exe.start()    
def take_profit(position:str):
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
    order_exe=Thread(target=create_order_exe, args=(take['orderId'],'take',))
    order_exe.start()    
def create_order_exe(order_id,intro:str):
    while True:
        order=client.futures_get_order(orderId=order_id,symbol=datos['symbol'])
        print(intro,order['status'],order['orderId'])
        if order['status']=='FILLED' and intro=='create':
            datos['price']=order['avgPrice']
            stop_loss(datos['side'])
            take_profit(datos['side'])
            break            
        if (order['status']=='FILLED' and intro=='stop') or order['status']=='CANCELED':
            client.futures_cancel_all_open_orders(symbol=datos['symbol'])
            break
        if (order['status']=='FILLED' and intro=='take') or order['status']=='CANCELED':
            client.futures_cancel_all_open_orders(datos['symbol'])
            break
        sleep(2)
def inicio():
    empezar=True#--------------------------------
    mensaje=''
    mail_viejo=''
    nuevo=''
    while True:
        mail = imaplib.IMAP4_SSL(gmail_host)
        #login
        mail.login(username, app_password)
        #select inbox
        mail.select("INBOX")
        _, selected_mails = mail.search(None, '(FROM "noreply@tradingview.com")')
        _, data = mail.fetch(selected_mails[0].split()[-1] , '(RFC822)')
        _, bytes_data = data[0]
        #convert the byte data to message
        email_message = email.message_from_bytes(bytes_data)
        mail_nuevo=email_message["subject"]
        #print(mail_nuevo,mail_viejo)
        #{"order":"{{strategy.order.action}}","position":"{{plot_15}}","ticker":"{{ticker}}"}
        if mail_nuevo!=mail_viejo and empezar:
            print(mail_nuevo,type(mail_nuevo))
            try:
                nuevo=loads(mail_nuevo.replace('Alerta: ',''))
                print(nuevo, end="")
                if nuevo['position']=='1' and nuevo['order']=='buy':
                    print('long')
                    create_order('BUY',nuevo['ticker'])
                elif nuevo['position']=='-1' and nuevo['order']=='sell':
                    print('short')
                    create_order('SELL',nuevo['ticker'])
            except:
                pass
            if nuevo != 'null':
                mail_viejo=mail_nuevo
            if nuevo != 'null':
                requests.post('https://api.telegram.org/bot5243749301:AAHIDCwt13NLYpmJ7WVaJLs57G0Z_IyFTLE/sendMessage',data={'chat_id':'-548326689','text':mensaje}) #742390776
        if not empezar:
            mail_viejo=mail_nuevo
        mail.logout()
        empezar=True
        sleep(0.5)
if __name__ == "__main__":
    inicio()
