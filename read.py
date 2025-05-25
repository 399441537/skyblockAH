import sqlite3
con = sqlite3.connect('db.db')


"""con.execute('UPDATE DB SET NAME=REPLACE(NAME," (Year 72)","") WHERE NAME LIKE "%New Year Cake %"')
con.execute('DELETE FROM PRICE WHERE NAME = "New Year Cake (Year 72)"')
con.commit()"""

item = "wither cata"
for info in con.execute(f'SELECT * FROM db WHERE NAME LIKE "%{item}%" ORDER BY PRICE ASC'):
 print(info[0],info[1],info[2])

print(con.execute('SELECT COUNT(*) FROM DB').fetchone()[0])

