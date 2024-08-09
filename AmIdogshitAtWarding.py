# -*- coding: utf-8 -*-
'''
Hello ! :D

HOW TO === >   players.txt : .___________________________________________________.
                             |username#tag                                       |
                             |topMainCoolUserDepressed#EUW                       |
                             |HappySupport#WHY                                   |
                             |                                                   |
                             |                                                   |
                             |                                                   |
                             |                                                   |
                             |___________________________________________________|

Ce script a été fait par kouzouke (et chatgpt pour ce qu'il sait faire)
Le but de ce script est de vous permettre de comparer la taille de vos WARDS

Ce script créer un fichier csv contenant les résultats.
Aucuns appel à l'appel API de riot games ne sont conservé. (Prend de la place inutile qu'ils ont sur leurs serveurs)

Le script se limite automatiquement à 25 requête à la seconde et 90 pour deux minutes.
Le  but est d'avoir une marge pour ne pas dépasser les quotas autorisés.
Le programme attend à la fin pour compléter ses 2 minutes des requêtes. Laissez le finir pour être sur que la prochaine
exécution est sans dépassement de quotas, ou Terminez le CTRL-C, ce qui laissera un fichier temporaire, mais en cas de rééxecution
les quotas seront respecter à coup sur.

Ce script créer aussi un fichier temporaire, directement à sa location afin de savoir en cas
de lancement successif combien de requêtes ont été faites et ne pas dépasser les quotas.
Ce fichier est supprimer en utilisation normal automatiquement. Si vous le voyez, soit j'ai merdé, soit c'est vous :) 


       /\                                        |
      /!!\                                       |
     /!!!!\                                   __\|/__                            
     ------    AJOUTEZ bien VOTRE clé API et |ENLEVEZ| la avant de passer le fichier à quelqu'un :)
                                              -------

                          .
                            .
                        . ;.
                         .;
                          ;;.
                        ;.;;
                        ;;;;.
                        ;;;;;
                        ;;;;;
                        ;;;;;
                        ;;;;;
                        ;;;;;
                      ..;;;;;..
                       ':::::'
                         ':`

# -------------------------------------------------------------------------------------- '''
APIKEY = open('apikey.txt').read();                                                       '''
# --------------------------------------------------------------------------------------
                      
                           .
                         .:;:.
                       .:;;;;;:.
                         ;;;;;
                         ;;;;;
                         ;;;;;
                         ;;;;;
                         ;:;;;
                         : ;;;
                           ;:;
                         . :.;
                           . :
                         .   .
                      
                            .                                                           '''
import requests
import time
import os
import sys
# Pour les stats.
import csv
# pickle permet de générer/restaurer un dump de la mémoire.
import pickle
import traceback

#Request List size. Set the amount of request per two minute
RLSize = 90
#Request number. 
RN = 0
#Request time list.
RList = []
#Cached request url list, as a dict.
CRList = {}
#Number of seconds for the upper limit of call.
TIME_LONG_LIMIT = 120

DUMP_FILE_NAME = "unluckely_you_should_not_see_this_file"
PLAYER_FILENAME = "players.txt"
CSV_FILENAME = "AmIdogshit_stats.csv"
DEBUG_PRINT = False


def debug(*args):
       if(DEBUG_PRINT):
              print(*args)

# Generate dump for exception.
def oopsi():
       file = open(DUMP_FILE_NAME,"wb")
       pickle.dump(RList,file)
       file.close()
       traceback.print_exc()
       exit()

#Time Seconds, remove the millis.
def times():
       return int(time.time())

def sanitizeUrl(url):
       surl = url.replace("https://","").replace("http://","")
       path, *query = surl.split("?",1)
       subfolders = path.split("/")
       if query:
              query = query[0]
              params = query.split("&")
              surl_params = [param for param in params if not param.startswith("api_key")]
              if surl_params:
                     subfolders.append("&".join(surl_params))
       return subfolders
def isCached(url):
       global CRList
       path = os.path.join("cache",*sanitizeUrl(url))
       if CRList.get(path, None) == True:
              try:
                     with open(path, 'rb') as filecache:
                            CRList[path] = pickle.load(filecache)
              except (pickle.UnpicklingError, EOFError):
                     print(f"Cache failed on file {path}")
                     pass
              return path
       else:
              return False

def loadCachedUrl():
       global CRList
       CRList = {}
       if not os.path.isdir("cache"):
              os.mkdir("cache")
       path = "cache"
       loadCachedUrl_recursive_folder(path)

def loadCachedUrl_recursive_folder(folder):
       for filename in os.listdir(folder):
              path = os.path.join(folder,filename)
              if os.path.isdir(path):
                     loadCachedUrl_recursive_folder(path)
              elif os.path.isfile(path):
                     CRList[path] = True
                     

def stockUrl(url,data):
       surl = sanitizeUrl(url)
       filename = surl[-1]
       sublink = "cache/"
       for folder in surl[:-1]:
              if not os.path.isdir(f"{sublink}{folder}"):
                     os.mkdir(f"{sublink}{folder}")
              sublink+=f"{folder}/"
       filecache = open(f"{sublink}{filename}",'wb')
       pickle.dump(data,filecache)
       filecache.close()

# Make API calls and control the flowrate.
def get(url):
       global RN, RList,RLSize, CRList
       surl = isCached(url)
       if surl:
              debug(f"is cached {surl}")
              return CRList[surl]
       time.sleep(1/25)
       # print(RList,RN)
       #Check to see if this position is not already filled by a call made less than a minute ago.
       #If so, wait for the difference to account for the minute. Then goes to execute.
       delta = times() - RList[RN]
       if(delta < TIME_LONG_LIMIT):
              print(f"Long limit of calls has been achieved, waiting for {TIME_LONG_LIMIT-delta}s to call again.")
              time.sleep(TIME_LONG_LIMIT-delta)
       try:
              #API call.
              response = requests.get(url)

              # Stock time + Incr.
              RList[RN] = times()
              RN = (RN+1)%RLSize
              #-
              if response.status_code == 200:
                     data = response.json()
                     CRList[url] = data
                     stockUrl(url,data)
                     return data
              else:
                     print(f"Failed to retrieve data: {response.status_code}.  Have you setup the API Key ? Valid Request user ?")
                     print(f"{url}")
                     oopsi()

       except Exception as e:
              print(e)
              oopsi()


def get_puuid(NAME,TAG):
       url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{NAME}/{TAG}?api_key={APIKEY}"
       data = get(url)
       return data.get('puuid')
def get_50_last_game(PUUID):
       url = f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{PUUID}/ids?type=ranked&start=0&count=50&api_key={APIKEY}"
       return get(url)

def get_vision_score(NAME,TAG):
       # return [[1,1]]*50
       try:
              puuid = get_puuid(NAME,TAG)
              games = get_50_last_game(puuid)
              table_score = []
              for GAMEID in games:
                     url = f"https://europe.api.riotgames.com/lol/match/v5/matches/{GAMEID}?api_key={APIKEY}"
                     data = get(url)
                     info = data.get('info',{})
                     gameDuration = int(info.get('gameDuration') / 60)
                     participants = info.get('participants',[])
                     found = False
                     for player in participants:
                            if player.get('puuid') == puuid:
                                   vision_score = player.get('visionScore')
                                   table_score += [[vision_score,vision_score/gameDuration,player.get('win')]]
                                   found = True
                     if not found:
                            print("Well... that's awkward.. This should never happen, the player is not in the game.. that we found with his infos lmao. Riot ?")
                            # Yes this is premade result to not break anything,
                            # as you can see, it's an impossible score. Zero divided by something giving 1 :) 
                            table_score +=[ [0,1]]
              return table_score
       except Exception as e:
              print(e)
              oopsi()

def calculate_averages(values, name):
       avg_values = sum(values) / len(values)
       top_20_values = sorted(values,reverse=True)[:20]
       avg_top_20_values = sum(top_20_values) / len(top_20_values)
       return {f"avg_{name}":avg_values,f"avg_top_20_{name}":avg_top_20_values}

def loadPlayers():
       players = []
       with open(PLAYER_FILENAME, "r") as file:
              for line in file:
                     line = line.strip()
                     if '#' in line:
                            user, tag = line.split('#',1)
                            players.append({"user":user,"tag":tag})
       return players


def VISION(players):
       for player in players:
              player_score = get_vision_score(player['user'],player['tag'])
              debug(f"{player['user']} has theses scores in visions : \n{player_score}")
              vs = calculate_averages([s[0] for s in player_score],'vision_score')
              vspg = calculate_averages([s[1] for s in player_score],'vision_score_per_minute')
              vsw = calculate_averages([s[0] for s in player_score if s[2]], 'vision_score_when_winning')
              vswpm = calculate_averages([s[1] for s in player_score if s[2]], 'vision_score_when_winning_per_minute')
              vsl = calculate_averages([s[0] for s in player_score if not s[2]], 'vision_score_when_losing')
              vslpm = calculate_averages([s[1] for s in player_score if not s[2]], 'vision_score_when_losing_per_minute')
              if not ('stat' in player):
                     player['stat'] = {}
              if not (isinstance(player['stat'],dict)):
                     player['stat'] = {}
              player['stat'] |= vs
              player['stat'] |= vspg
              player['stat'] |= vsw
              player['stat'] |= vswpm
              player['stat'] |= vsl
              player['stat'] |= vslpm
              debug(f"vision : {vs}, \n vision per minute : {vspg}")
       debug(players)

def write_csv(players):
       data_dict = {f"{item['user']}#{item['tag']}": item['stat'] for item in players}
       if(os.path.exists(CSV_FILENAME)):
              with open(CSV_FILENAME,mode='r',newline='') as file:
                     reader =csv.DictReader(file)
                     old_data = {row['player']: row for row in reader}
       else:
              old_data = {}
       for player, stats in data_dict.items():
              if player in old_data:
                     old_data[player].update(stats)
              else:
                     old_data[player] = {'player': player, **stats}
       all_fieldnames = set()
       for row in old_data.values():
              all_fieldnames.update(row.keys())
       with open(CSV_FILENAME,mode='w',newline='') as file:
              writer = csv.DictWriter(file, fieldnames=sorted(all_fieldnames))
              writer.writeheader()
              for row in old_data.values():
                     writer.writerow(row)
       print(f"All the stats have been written to {CSV_FILENAME}.")

def dicho_min(arr):
       left,right = 0,len(arr) -1
       while left < right:
              mid = (left + right) //2
              if(arr[mid] > arr[right]):
                     left = mid +1
              else:
                     right = mid
       return left

def main():
       global RN, RList, RLSize, CRList
       loadCachedUrl()
       try:
              #Check if the players file exist.
              if not (os.path.isfile(PLAYER_FILENAME)):
                     print(f"My brother in Christ, the script is not in your head. Create the {PLAYER_FILENAME} file and put line by line the user and tag you want to compare.")
                     exit()
              players = loadPlayers()
              if len(players) < 1:
                     print(f"You made the file, but you either can't write or you forgot something. see the example in the script file.")
                     exit()
              #Check if last was oopsi
              if(os.path.isfile(f"./{DUMP_FILE_NAME}")):
                     dump = open(f"{DUMP_FILE_NAME}",mode="rb")
                     RList = pickle.load(dump)
                     dump.close()
                     delta_size = RLSize - len(RList)
                     if(delta_size < 0):
                            RLSize += [0]*delta_size
                     elif(delta_size > 0):
                            RList = RList[:-delta_size]
                     now = times()
                     RN = RLSize-1
                     # Find where we should start the next request.
                     # Basically find the smaller value in the array 
                     RN = dicho_min(RList)
              else:
                     RList = [0]*RLSize

              VISION(players)
              write_csv(players)
              now = times()
              if(RList[RN-1]+TIME_LONG_LIMIT > now):
                     delay = (RList[RN-1]+TIME_LONG_LIMIT) - now
                     print(f"The script needs to sleep for {delay}s to complete the full circle of calls.")
                     time.sleep(delay)
              if(os.path.isfile(f"./{DUMP_FILE_NAME}")):
                     os.remove(f"./{DUMP_FILE_NAME}")
              print("Script ended ! :D") 
       except KeyboardInterrupt:
              print("Program interrupted!")
              oopsi()  
if __name__ == "__main__":
       if len(sys.argv) > 1:
              if(sys.argv[1] in ['DEBUG','debug','-d','-D']):
                     DEBUG_PRINT = True
       main()
       # print(sanitizeUrl("https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/blouch/TDP?api_key=RGAPI-a7190d70-2844-473d-acf6-cb32394ca5ae"))