import sqlite3

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()



cur.execute(
    "INSERT INTO projects (title, description, tech_stack, github_url) VALUES (?, ?, ?, ?)",
    (
        'Final Year Project - Using sentiment analysis techniques to identify correlations in tweets relating to the 2024 US election',
        'Used two different sentiment analysis techniques one being an AI approach by using a transformer while the other appraoch used was the VADER lexicon approach. After comparing the two technqiues the transformer sentiment results were compared with election poll percentages from the 2024 US election to try find any corrlations during a 13 month period using techniques like time and lag analysis.',
        'Python, BERT, VADER, Pandas, Matplotlib, Scikit, Spyder',
        'https://github.com/brianpurcell16/FYPImplementation'
    )
)

cur.execute(
    "INSERT INTO projects (title, description, tech_stack, github_url) VALUES (?, ?, ?, ?)",
    (
        'Distributed Messaging Server',
        'A multi-client Java socket server with SSL support. Implements login, upload, and download commands.',
        'Java, Sockets, SSL, Threading',
        'https://github.com/brianpurcell16/Distributed_Computing_Project'
    )
)


connection.commit()
connection.close()

print("Database initialised successfully!")