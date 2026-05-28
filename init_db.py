import sqlite3

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()


# Sample projects I will be changing later
cur.execute(
    "INSERT INTO projects (title, description, tech_stack, github_url) VALUES (?, ?, ?, ?)",
    (
        'Sentiment Analysis Tool',
        'Analysed 2024 US election tweets using VADER and BERT. Correlated results with polling data over a 13-week window.',
        'Python, BERT, VADER, Pandas, Matplotlib',
        'https://github.com/yourusername/sentiment-analysis'
    )
)

cur.execute(
    "INSERT INTO projects (title, description, tech_stack, github_url) VALUES (?, ?, ?, ?)",
    (
        'Distributed Messaging Server',
        'A multi-client Java socket server with SSL support. Implements login, upload, and download commands.',
        'Java, Sockets, SSL, Threading',
        'https://github.com/yourusername/distributed-messaging'
    )
)

cur.execute(
    "INSERT INTO projects (title, description, tech_stack, github_url) VALUES (?, ?, ?, ?)",
    (
        'Timetable Scheduling (Genetic Algorithm)',
        'Automated university timetabling using a genetic algorithm with constraint satisfaction for rooms, lecturers, and class groups.',
        'Python, NumPy, Genetic Algorithms',
        'https://github.com/yourusername/timetable-ga'
    )
)

connection.commit()
connection.close()

print("Database initialised successfully!")