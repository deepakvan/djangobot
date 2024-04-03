from django.http import HttpResponse
from django.shortcuts import render
from . import models

import datetime
import time
from time import sleep
from . import algobot_helper_functions as hf
from binance.um_futures import UMFutures
from binance.error import ClientError
import pandas as pd
import threading
import random



def bot():
    """ kuber """
    API_KEY = "haw4oFzdJxbVorYjh0EZnA5Yc4wmqo3gocN1lVYaa7pFwV9OZpnKrG7j7sAbkgdg"
    API_SECRET = "4S16wNfnsl0iiTloWNWcw8XOpFZQm36F6N9vkyPMdN4MmOMpqqiibu69PlAu30YC"
    client=UMFutures(key=API_KEY,secret=API_SECRET)
    coinpair_list= ['GALAUSDT']

    orders = 0
    symbol = ''

    threading.Thread(target=hf.remove_pending_orders, args=(client,)).start()
    while True:
        try:
            minutes = datetime.datetime.now().minute
            seconds = datetime.datetime.now().second
            if minutes % 15 <= 1 and seconds>=5: #minutes%15<=1
                # we need to get balance to check if the connection is good, or you have all the needed permissions
                balance = hf.get_balance_usdt(client)
                sleep(1)
                if balance == None:
                    print('Cant connect to API. Check IP, restrictions or wait some time')
                    models.BotLogs(description="----Cant connect to API. Check IP, restrictions or wait some time").save()
                if balance != None:
                    print("My balance is: ", balance, " USDT")
                    models.BotLogs(description="My balance is: "+ str(balance)+ " USDT").save()
                    # getting position list:
                    pos = hf.get_pos(client)
                    print(f'You have {len(pos)} opened positions:\n{pos}')
                    models.BotLogs(description=f'You have {len(pos)} opened positions:\n{pos}').save()
                    if len(pos)==0:
                        ord = hf.check_orders(client)
                        #print("working")
                        #print(ord)
                        # removing stop orders for closed positions
                        for elem in ord:
                            if not elem in pos:
                                hf.close_open_orders(client,elem)
                        random.shuffle(coinpair_list)
                        signal_list=[]
                        for coinpair in coinpair_list:
                            df=hf.fetch_historical_data(client,coinpair,'15m',10)
                            #print(coinpair)
                            signal_data=hf.get_signal(df)
                            #break
                            if signal_data!=None:
                                #print([coinpair,signal_data])
                                signal_list.append([coinpair,signal_data])
                        for sig in signal_list:
                            print(sig)
                            models.BotLogs(description=f'signal  {sig} ').save()
                        print("calling monitor")
                        models.BotLogs(description="calling monitor").save()
                        #hf.monitor_signal(client,signal_list,coinpair_list)
                        threading.Thread(target=hf.monitor_signal, args=(client,signal_list,coinpair_list)).start()

                #break # break while loop if needed
                time.sleep(3*60)
            elif minutes % 15 > 1:
                if (13 - (minutes % 15)) * 60 > 0:
                    print("sleeping for ", (13 - (minutes % 15)) * 60, " seconds (", 13 - (minutes % 15), ") minutes")
                    models.BotLogs(description=f'sleeping for  {(13 - (minutes % 15)) * 60} seconds:{13 - (minutes % 15)}').save()
                    time.sleep((13 - (minutes % 15)) * 60)
                    print("awaked at ",datetime.datetime.now())
                    models.BotLogs(
                        description=f'----awaked at {datetime.datetime.now()}').save()
            time.sleep(5)
        except:
            print("Error in code Main Code")
            models.BotLogs(description=f'Error in Main code').save()
            pass


# Create your views here.
def start_bot(request):
    if models.StaticData.objects.exists():
        # Your code to update the model value
        obj = models.StaticData.objects.get(static_id=1)  # Example: Retrieve the object you want to update
        print(obj.is_bot_running)
        if not obj.is_bot_running:
            obj.is_bot_running = True
            obj.save()
            print(obj.is_bot_running)
            threading.Thread(target=bot).start()
            models.BotLogs(description=f'bot has been started').save()
            return HttpResponse("Bot has been started!")
    models.BotLogs(description=f'bot already started').save()
    return HttpResponse("Bot already started!")


def index_page(request):

    return HttpResponse("Site is Alive!")


def update_model_on_startup(request):
    from .models import StaticData
    print("updaing model")
    models.BotLogs(description=f'Updating Model').save()
    # Check if there are any records in StaticData
    if not StaticData.objects.exists():
        # Create a new record with default values
        StaticData.objects.create(is_bot_running=False, volume=4, leverage=3, static_id=1)
    else:
        obj = StaticData.objects.get(static_id=1)  # Example: Retrieve the object you want to update
        obj.is_bot_running = False
        obj.save()
        print("model is saved bot running at ",obj.is_bot_running)

    return HttpResponse("Bot is_running set to False!")