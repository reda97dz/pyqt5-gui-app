import sys, json
from PyQt5.QtCore import QDate, QPoint, QTime, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QAbstractSpinBox, QComboBox, QDateEdit, QDesktopWidget, QDoubleSpinBox, QFormLayout,
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, QSpinBox, QTextEdit, 
                            QTimeEdit, QVBoxLayout, QWidget, QApplication)
from AddWorkoutStylesheet import stylesheet



class AddWorkoutGUI(QWidget):
    def __init__(self):
        super().__init__()
        # self.parent = parent
        self.startUI()
        
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()
    
    def startUI(self):
        """
        Show components
        """
        self.setMinimumSize(400, 550)
        self.setWindowFlag(Qt.FramelessWindowHint)
        
        self.setupWindow()
        
        self.show()
        
    def setupWindow(self):
        """
        Set up widgets 
        """
        
        header_label = QLabel("Add Workout Details")
        header_label.setObjectName("header")
        header_label.setAlignment(Qt.AlignCenter)
        
        self.workout_name_entry = QLineEdit()
        
        self.date_entry = QDateEdit()
        self.date_entry.setDate(QDate.currentDate())
        self.date_entry.setFixedHeight(25)
        self.date_entry.setButtonSymbols(QAbstractSpinBox.NoButtons)
        
        self.time_entry = QTimeEdit()
        self.time_entry.setTime(QTime.currentTime())
        self.time_entry.setFixedHeight(25)
        self.time_entry.setButtonSymbols(QAbstractSpinBox.NoButtons)
        
        activities = ["Run", "Hike", "Walk"]
        self.activity_type = QComboBox()
        self.activity_type.addItems(activities)
        
        self.hours = QSpinBox()
        self.hours.setRange(0,24)
        self.hours.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.hours.valueChanged.connect(self.calculatePace)
        
        self.minutes = QSpinBox()
        self.minutes.setRange(0,59)
        self.minutes.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.minutes.valueChanged.connect(self.calculatePace)
        
        self.seconds = QSpinBox()
        self.seconds.setRange(0,59)
        self.seconds.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.seconds.valueChanged.connect(self.calculatePace)
        
        time_colon_label = QLabel(":")
        
        self.distance_entry = QDoubleSpinBox()
        self.distance_entry.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.distance_entry.setFixedWidth(190)
        self.distance_entry.setRange(0.1,150.0)
        self.distance_entry.valueChanged.connect(self.calculatePace)
        
        self.pace_minutes = QSpinBox()
        self.pace_minutes.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.pace_seconds = QSpinBox()
        self.pace_seconds.setButtonSymbols(QAbstractSpinBox.NoButtons)
        
        
        self.notes_entry = QTextEdit()
        
        date_time_h_box = QHBoxLayout()
        date_time_h_box.addWidget(self.date_entry)
        date_time_h_box.addWidget(self.time_entry)
        
        
        h_label = QLabel("hh")
        h_label.setObjectName("small_label")
        m_label = QLabel("mm")
        m_label.setObjectName("small_label")
        s_label = QLabel("ss")
        s_label.setObjectName("small_label")
        
        duration_h_box = QHBoxLayout()
        duration_h_box.addWidget(h_label)
        duration_h_box.addWidget(self.hours)
        # duration_h_box.addWidget(time_colon_label)
        duration_h_box.addWidget(m_label)
        duration_h_box.addWidget(self.minutes)
        # duration_h_box.addWidget(time_colon_label)
        duration_h_box.addWidget(s_label)
        duration_h_box.addWidget(self.seconds)
        duration_h_box.addStretch()
        
        pace_h_box = QHBoxLayout()
        pace_h_box.addWidget(self.pace_minutes)
        pace_h_box.addWidget(time_colon_label)
        pace_h_box.addWidget(self.pace_seconds)
        pace_h_box.addStretch()
        
        
        add_run_form = QFormLayout()
        add_run_form.setLabelAlignment(Qt.AlignTop)
        add_run_form.addRow(QLabel("Workout Name"))
        add_run_form.addRow(self.workout_name_entry)
        add_run_form.addRow(QLabel("Date and time"))
        add_run_form.addRow(date_time_h_box)
        add_run_form.addRow(QLabel("Activity"))    
        add_run_form.addRow(self.activity_type)
        add_run_form.addRow(QLabel("Duration"))
        add_run_form.addRow(duration_h_box)
        add_run_form.addRow(QLabel("Distanace (km)"))
        add_run_form.addRow(self.distance_entry)
        add_run_form.addRow(QLabel("Pace (min/km)"))
        add_run_form.addRow(pace_h_box)
        add_run_form.addRow(QLabel("Notes"))
        add_run_form.addRow(self.notes_entry)
        
        saveButton = QPushButton("Save")
        saveButton.setObjectName("save")
        saveButton.clicked.connect(self.saveWorkout)
        
        cancelButton = QPushButton("Cancel")
        cancelButton.setObjectName("cancel")
        cancelButton.clicked.connect(self.close)
        
        buttons_h_box = QHBoxLayout()
        buttons_h_box.addWidget(cancelButton)
        buttons_h_box.addWidget(saveButton) 
        
        
        main_v_box = QVBoxLayout()
        main_v_box.setAlignment(Qt.AlignTop)
        main_v_box.addWidget(header_label)
        main_v_box.addSpacing(10)
        main_v_box.addLayout(add_run_form)
        main_v_box.addLayout(buttons_h_box)
        self.setLayout(main_v_box)

    
    def calculatePace(self):
        """
        Calculate pace
        """
        distance = self.distance_entry.value()
        
        hours = self.hours.value()
        minutes = self.minutes.value()
        seconds = self.seconds.value()

        run_time = int(hours)*60 + int(minutes) + int(seconds)/60
        pace = run_time / distance
        
        self.pace_minutes.setValue(int(pace))
        self.pace_seconds.setValue((pace-int(pace))*60)
        
        
        
    def saveWorkout(self):
        """
        Nothing as of yet
        """
        workout_info = {}
        
        distance = self.distance_entry.value()
        
        hours = self.hours.value()
        minutes = self.minutes.value()
        seconds = self.seconds.value()
        
        run_time = int(hours)*60 + int(minutes) + int(seconds)/60
        pace = run_time / distance
        
        with open('Files/workouts.json', 'r+') as json_f:
            workout_data = json.load(json_f)
            workout_data['workoutList'].append(
                {
                    "activity": self.activity_type.currentText(),
                    "name": self.workout_name_entry.text(),
                    "date": self.date_entry.date().toString(),
                    "time": self.time_entry.time().toString(),
                    "duration": run_time,
                    "distance": distance,
                    "pace": pace,
                    "notes": self.notes_entry.toPlainText()
                }
            )
            
            workout_data.update(workout_info)
            json_f.seek(0)
            json.dump(workout_data, json_f, indent=2)
        
        self.close()
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(stylesheet)
    window = AddWorkoutGUI()

    sys.exit(app.exec_())