from nbt import nbt
from threading import Thread
import requests, os, time, clipboard, sqlite3, io, base64, re

blacklist_type = ['SWORD','BOW','DRILL','PICKAXE','GAUNTLET','NECKLACE','CLOAK','BELT','BRACELET','GLOVES','FISHING','HELMET','CHESTPLATE','LEGGINGS','BOOTS']
blacklist_name = ['Rune','Lvl','Potion','Attribute Shard','null','New Year Cake']
interval = 8 * 3600000 
price_min = 50000
price_max = 5000000
rate = 0.5
sample = 10
tolerance = 3
enable = False
  
def update_end(auctions):
  for auction in auctions:
    item = nbt.NBTFile(fileobj = io.BytesIO(base64.b64decode(auction['item_bytes'])))[0][0]
    name = item['tag']['display']['Name'].value
    if auction['bin'] \
    and not any(x in item['tag']['display']['Lore'][-1] for x in blacklist_type) \
    and (not any(x in name for x in blacklist_name) or \
        'God Potion' in name):
      name = re.sub('(Bizarre |Itchy |Ominous |Pleasant |Pretty |Strange |Vivid |Godly |Demonic |Forceful |Hurtful |Keen |Strong |Superior |Unpleasant |Zealous |Silky |Bloody |Shaded |Sweet )','',name)
      con.execute('INSERT INTO DB VALUES(?,?,?,?)',
                  (name, round(auction['price'] / item['Count'].value),
                   item['Count'].value, auction['timestamp']))
      if not con.execute(f'SELECT NAME FROM PRICE WHERE NAME = "{name}"').fetchone():
        con.execute(f'INSERT INTO PRICE VALUES ("{name}",0,0)')
  con.commit()
  
def update_price(time):
  con.execute('UPDATE PRICE SET PRICE = 0, COUNT = 0')
  con.execute(f'DELETE FROM DB WHERE {time} - TIME > 86400000')
  con.commit()
  con.execute('vacuum')
  for info in con.execute('SELECT NAME FROM PRICE'):
    auctions = con.execute(f'SELECT PRICE, COUNT FROM DB WHERE NAME = "{info[0]}" AND {time} - TIME < {interval}').fetchall()
    if auctions:
      total = 0
      count = 0
      for i in range(2):
        if i:
          auctions = con.execute(f'SELECT PRICE, COUNT FROM DB WHERE NAME = "{info[0]}" AND {time} - TIME < {interval} AND PRICE <= {round(total/count)*tolerance}').fetchall()
        total = count = 0
        for auction in auctions:
          total += auction[0] * auction[1]
          count += auction[1]
      con.execute(f'UPDATE PRICE SET PRICE = {round(total/count)}, COUNT = {count} WHERE NAME = "{info[0]}"')
  con.commit()
  
def update_auction(pages):
  threads = []
  for page in range(pages):
    thread = Thread(target=update_auction_page, args=(page,))
    threads.append(thread)
    thread.start()
  for thread in threads:
    thread.join()
  
def update_auction_page(page):
  con = sqlite3.connect('db.db')
  auctions = requests.get(f'https://api.hypixel.net/skyblock/auctions?page={page}').json()['auctions']
  for auction in auctions:
    if auction['bin'] and not any(x in auction['item_lore'] for x in blacklist_type) \
    and (not any(x in auction['item_name'] for x in blacklist_name) or 'God Potion' in auction['item_name']):
      item = nbt.NBTFile(fileobj = io.BytesIO(base64.b64decode(auction['item_bytes'])))[0][0]
      name = re.sub('(Bizarre |Itchy |Ominous |Pleasant |Pretty |Shiny |Strange |Vivid |Godly |Demonic |Forceful |Hurtful |Keen |Strong |Superior |Unpleasant |Zealous |Silky |Bloody |Shaded |Sweet )',
                    '',item['tag']['display']['Name'].value)
      info = con.execute(f'SELECT PRICE, COUNT FROM PRICE WHERE NAME = "{name}"').fetchone()
      if info and info[1] != 0:
        price = round(auction['starting_bid'] / item['Count'].value)
        if price_min <= price <= price_max and price <= info[0] * rate and info[1] >= sample:
          items.append([re.sub('§.','',name),price,info[0],info[1],auction['uuid']])
  con.close()
  
def read():
  while True:
    if items:
      print('\a')
      os.system("""osascript -e 'display notification "{} items" with title "AH"'""".format(len(items)))
      #items.sort(key=lambda x:x[1])
      os.system('clear')
      while items:
        print('{:<40}{:>20,}{:>20,}{:>10}'.format(items[0][0],items[0][1],items[0][2],items[0][3]),end='')
        input()
        clipboard.copy(f'/viewauction {items[0][4]}')
        del items[0]
      os.system('clear')
      print('None')
    time.sleep(1)
  
con = sqlite3.connect('db.db')
end_updatetime = requests.get('https://api.hypixel.net/skyblock/auctions_ended').json()['lastUpdated']
price_updatetime = 0
auction_updatetime = 0
if enable:
  items = []
  Thread(target=read).start()
  
while True:
  auction = requests.get('https://api.hypixel.net/skyblock/auctions').json()
  end = requests.get('https://api.hypixel.net/skyblock/auctions_ended').json()
  current_time = round(time.time()*1000)
  if end['lastUpdated'] > end_updatetime:
    end_updatetime = end['lastUpdated']
    update_end(end['auctions'])
  if enable and current_time - price_updatetime > 600000:
    price_updatetime = current_time
    st = time.time()
    update_price(current_time)
    print('price runtime',time.time()-st)
  if enable and auction_updatetime < auction['lastUpdated']:
    auction_updatetime = auction['lastUpdated']
    st = time.time()
    update_auction(auction['totalPages']) 
    print('au runtime',time.time()-st)
  time.sleep(5)