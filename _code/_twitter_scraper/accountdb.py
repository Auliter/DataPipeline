import asyncio
import sqlite3
from twscrape import API

db_path = "../../_data/_twitter/accounts.db"

# add accounts
async def add_account():
    api = API(db_path)  # default is `accounts.db`
    #add_account("user1", "password1", "email1", "emailpassword")
    #await api.pool.add_account("@tempforqf5214", "dB~Q^!c/na8v.6+", "mailforqf5214@yahoo.com", "Mkun4?Y.QanNig%") #XuZiyi
    #await api.pool.add_account("@CaiSenti62009", "istKySg6kc6p77:", "yuze_cai@yahoo.com", "/LMqTK2Z&yMi4hX") #Caiyuze
    #await api.pool.add_account("@yngwnd1267223", "e7C_BsHEu5iLceX", "dylanywd@myyahoo.com", "_HASz-Azs!6x26Z") #YangWendi
    #await api.pool.add_account("@yayoooooya", "ilikebbg5!", "hooyayooh@myyahoo.com", "ilikebbg5!") #MaYufei
    #await api.pool.add_account("@AnyaTaylor97390", "Cms123456", "anyatalorjoyhaha@gmail.com", "Cms123456") #YangYihang
    #await api.pool.add_account("@tianti49373", "cms123456", "chentiantian2222@gmail.com", "cms123456") #YangYihang

#delete accounts
async def remove_account():
    api = API(db_path)
    # delete_accounts(self, usernames: str | list[str])
    await api.pool.delete_accounts("user1")
    # await api.pool.delete_accounts(["user2", "user3"])

def check_accounts_db(db_file=db_path):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM accounts")
    accounts = cursor.fetchall()
    for account in accounts:
        print(account)
    conn.close()

if __name__ == "__main__":
    asyncio.run(add_account())
    #asyncio.run(remove_account())
    check_accounts_db()
