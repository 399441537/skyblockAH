import requests, os, time, clipboard, io, base64
from nbt import nbt
from threading import Thread
search = {
  "Scare Fragment":800000,
}


def read(page):
  auctions = requests.get(f'https://api.hypixel.net/skyblock/auctions?page={page}').json()['auctions']
  for auction in auctions:
    if auction['bin'] and any(item in auction['item_name'] and round(auction['starting_bid'] / nbt.NBTFile(fileobj = io.BytesIO(base64.b64decode(auction['item_bytes'])))[0][0]['Count'].value) <= search[item] for item in search):
      items.append([auction['item_name'], auction['starting_bid'], auction['uuid']])
update = 0

def list():
  print('\a')
  os.system("""osascript -e 'display notification "{} items" with title "AH"'""".format(len(items)))
  items.sort(key=lambda x:x[1])
  for item in items:
    print(f'{item[0]}, {item[1]:,}',end='')
    #name = requests.get(f'https://sessionserver.mojang.com/session/minecraft/profile/{item[2]}').json()['name']
    clipboard.copy(f'/viewauction {item[2]}')
    input()
  print('None')
    
while True:
  request = requests.get('https://api.hypixel.net/skyblock/auctions').json()
  if update < request['lastUpdated']:
    update = request['lastUpdated']
    pages = request['totalPages']
    items = []
    threads = []
    for page in range(pages):
      thread = Thread(target=read, args=(page,))
      threads.append(thread)
      thread.start()
    for thread in threads:
      thread.join()
    if items:
      list()
  time.sleep(1)