import sys, os
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtSql import QSqlDatabase, QSqlQuery

class CreateDatabaseObject():
    
    database = QSqlDatabase.addDatabase('QSQLITE')
    database.setDatabaseName('databases/workout.sql')

    if not database.open():
        print('Connection failed', database.lastError().text())
        sys.exit(1)
    
    query = QSqlQuery()  

    query.exec_("DROP TABLE IF EXISTS workouts")
    
    query.exec_(
    """
    CREATE TABLE workouts (
        workout_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
        activity VARCHAR (25) NOT NULL,
        name VARCHAR (25),
        date DATE NOT NULL,
        time TIME,
        duration FLOAT NOT NULL,
        distance FLOAT NOT NULL,
        pace FLOAT NOT NULL,
        notes VARCHAR (300)
    )
    """
    )
    
class InsertDataIntoTable():
    workouts = [
        ["Run", "Run", '2021-07-05', '12:59:15', 21.3, 4.09],
        ["Run", "Run", '2021-07-09', '13:01:20', 24.75, 4.91],
        ["Run", "Run", '2021-07-11', '13:02:14', 20.51, 3.82],
        ["Run", "Run", '2021-07-15', '12:59:15', 20.08, 5.37],
        ["Run", "Run", '2021-07-18', '12:59:15', 25.35, 4.86]
    ]
    
    query = QSqlQuery()
    
    query.prepare("INSERT INTO workouts (activity, name, date, time, duration, distance, pace, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)")
    
    for i in range(len(workouts)):
        
        activity = workouts[i][0]
        name = workouts[i][1]
        date = workouts[i][2]
        time = workouts[i][3]
        duration = workouts[i][4]
        distance = workouts[i][5]
        pace = duration/distance
        
        query.addBindValue(activity)
        query.addBindValue(name)
        query.addBindValue(date)
        query.addBindValue(time)
        query.addBindValue(duration)
        query.addBindValue(distance)
        query.addBindValue(pace)
        
        query.exec_()
    
    print("[INFO] Database successfully created.")
    sys.exit(0)
    
if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    CreateDatabaseObject()
    InsertDataIntoTable()
    sys.exit(app.exec_())