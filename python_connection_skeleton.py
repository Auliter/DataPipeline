import mysql.connector as cnt

cnx = cnt.connect(user='testUser',password='123456',host='47.250.52.110',database='ModelFeatures')
mycursor = cnx.cursor()
sql = "SELECT TOP 2 * FROM Sentiment"

mycursor.execute("SELECT * FROM Sentiment LIMIT 2")
results = mycursor.fetchall()
for result in results:
    print(result)

mycursor.execute("SELECT * FROM stockPrice LIMIT 2")
results = mycursor.fetchall()
for result in results:
    print(result)

mycursor.execute("SELECT * FROM TwSentiment LIMIT 2")
results = mycursor.fetchall()
for result in results:
    print(result)
