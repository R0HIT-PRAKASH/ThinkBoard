from ssl import ALERT_DESCRIPTION_BAD_CERTIFICATE_HASH_VALUE
from flask import Flask
from flask import request
#import pandas as pd
import re
import os
import psycopg2
from flask_cors import CORS
from mlFuncs import get_summary, get_predictions

# Create a cursor.
user = "Rohit"
host = "free-tier14.aws-us-east-1.cockroachlabs.cloud"
cluster = "yeti-chimera-5034"
password = "gavDhGqwRAmRg1L6K493VA"


connection = psycopg2.connect(user=user,
                              host=host,
                              port=26257,
                              database=f'{cluster}.defaultdb',
                              password=password,
                              # sslmode='verify-full'
                              )

# Set to automatically commit each statement
connection.set_session(autocommit=True)

cursor = connection.cursor()

cursor.execute("""DROP DATABASE IF EXISTS Brainstorm;
                CREATE DATABASE Brainstorm; Use Brainstorm;""")
cursor.execute("""DROP TABLE IF EXISTS Brainstorm CASCADE;
                  CREATE TABLE Brainstorm (bID int, iID int, PRIMARY KEY (bID, iID));""")
cursor.execute("""DROP TABLE IF EXISTS Idea CASCADE;
                  CREATE TABLE Idea(iID serial PRIMARY KEY, summary varchar(500)
                , parent varchar(500), input varchar(1000));""")
cursor.execute("""DROP TABLE IF EXISTS ChildRelationship CASCADE;
                  CREATE TABLE ChildRelationship (pID int, cID int, type varchar(300), 
                  PRIMARY KEY (pID, cID));""")

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# summary, parent (summary), type, child summary, original input, parentID
#all_ideas = {str: [str, [(int, str)], str, int]}
all_ideas = {}
#newly_added_ideas = {str: [str, [(int, str)], str, int]}
COMMAND_CREATE = 'Create'
COMMAND_EXPAND = 'Expand'
COMMAND_SHRINK = 'Shrink'
COMMAND_ERROR = 'Error'
CHILD_BUBBLES = 0
PREDICTIONS = 1
IMAGES = 2
BID = 100


# password: gavDhGqwRAmRg1L6K493VA
# connection string: postgresql://Rohit:gavDhGqwRAmRg1L6K493VA@free-tier14.aws-us-east-1.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full&options=--cluster%3Dyeti-chimera-5034
###
# {
#     input: string,
#     parent: string,
# }
###

@app.route('/api/start', methods=['POST'])
def create_start_idea():
    start = request.json['start']
    cursor.execute(
        """Insert into Idea(summary, parent, input) values (%s, %s, %s) RETURNING iID;""", (start, 0, start))
    iID = cursor.fetchone()[0]
    cursor.execute("""Insert into Brainstorm values (%s, %s)""", (BID, iID))
    return ''


@app.route('/api/save', methods=['POST'])
def process_save_press(idea):
    summary = idea
    parent = all_ideas[idea][0]
    input = all_ideas[idea][2]
    child_type = all_ideas[idea][1][0]
    if parent == 0:
        cursor.execute("""INSERT INTO Idea(summary, parent, input) values (%s, %s, %s) RETURNING iID;
                            """, (summary, 0, input))
    else:
        cursor.execute("""INSERT INTO Idea(summary, parent, input) values (%s, %s, %s) RETURNING iID;
                            """, (summary, parent, input))
    iID = cursor.fetchone()[0]
    parent_id = all_ideas[idea][3]
    cursor.execute(
        """INSERT INTO ChildRelationship values (%s, %s, %s);""",
        (parent_id, iID, child_type))
    cursor.execute("""INSERT INTO Brainstorm values (%s, %s);""", (BID, iID))
    # cursor.execute("""SELECT * FROM Idea;""")
    # for item in cursor:
    #     print(item)
    # if summary != 'testing':
    #     process_load_press()
    # if idea == 'go':
    #     process_load_press()


@app.route('/api/load', methods=['GET'])
def process_load_press():
    bID = BID
    global all_ideas
    all_ideas = {}
    cursor.execute("""SELECT i.iID, i.summary, i.parent, i.input FROM Idea i JOIN Brainstorm b ON
    i.iID = b.iID WHERE b.bID = %s;""", (bID, ))
    for idea in cursor:
        if idea[1] not in all_ideas:
            all_ideas[idea[1]] = [idea[2], [], idea[3], -1]
    cursor.execute("""SELECT i.iID, i.summary, c.type, c.pID FROM Idea i JOIN ChildRelationship c
    ON i.iID = c.cID JOIN Brainstorm b on b.bID = i.iID WHERE b.bID = %s""", (bID, ))
    for idea in cursor:
        all_ideas[idea[3]][1] += (idea[2], idea[1])
    cursor.execute("""SELECT c.pID, c.cID, i.summary from ChildRelationship c JOIN Brainstorm b ON c.cID = b.iID
    JOIN Idea i ON c.cID = i.iID WHERE b.bID = %s""", (bID, ))
    for idea in cursor:
        all_ideas[idea[2]][3] = idea[0]
    print(f'all of them {all_ideas}')
    return all_ideas
    # SELECT i.iID, i.summary, JSON_ARRAY(SELECT JSON_ARRAY(c.type, a.summary) FROM ChildRelationship c
    #     LEFT JOIN Idea a
    #         ON a.iID = c.pID) AS children
    # FROM Idea i
    # LEFT JOIN Branstorm b
    #     i.iID = b.iID
    # WHERE b.bID = 2

    # cursor.execute("""SELECT i.iID, i.summary, i.parent, i.input, c.cID, c.type
    #  FROM Idea i JOIN ChildRelationship c ON i.iID = c.pID JOIN Brainstorm b ON b.iID =
    #  i.iID WHERE b.bID = %s;""", (bID,))
    # for idea in cursor:
    #     if idea[1] not in all_ideas:
    #         all_ideas[idea[1]] = {}


@app.route('/api/create', methods=['POST'])
def process_human_input():
    new_input = request.json['input']
    parent = request.json['parent']
    df = get_summary(new_input)
    summary = df.iloc[0][:-1]
    counter = 1
    while summary in all_ideas or not summary:
        summary = df.iloc[counter][:-1]
        counter += 1
    prediction = get_predictions(summary)  # string
    prediction = re.sub("[0-9]\. ", '', prediction)
    prediction = [i for i in prediction.split("\n") if i.strip()]
    all_ideas[summary] = [parent, [], new_input, -1]
    for i in prediction:
        all_ideas[summary][1].append((PREDICTIONS, i))
    # cursor.execute("""SELECT i.iID FROM Idea i WHERE
    #                  i.summary = %s; """, (parent, ))
    cursor.execute("""SELECT i.iID FROM Idea i JOIN Brainstorm b ON i.iID = b.iID
                      WHERE b.biD = %s""", (BID, ))
    #                 i.summary = %s; """, (summary, ))
    all_ideas[summary][3] = cursor.fetchone()[0]
    process_save_press(summary)
    return [summary, prediction]


###
# {
#     parent: string,
# }
###
@app.route('/api/expand', methods=['POST'])
def expand():
    parent = request.json['parent']
    parents_children = all_ideas[parent][1]
    grandchildren = {}  # {str: [(int, str)]}
    for child in parents_children:  # child is a tuple (type, child name)
        grandchildren[child[1]] = all_ideas[child[1]][1]
    return grandchildren


if __name__ == '__main__':
    app.run()
