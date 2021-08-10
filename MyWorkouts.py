import os
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from matplotlib.cbook import file_requires_unicode
from numpy.core import einsumfunc
from AddWorkout import AddWorkoutGUI
import sys, json
import numpy as np
import PyQt5
from PyQt5.QtCore import QDate, QLine, QPoint, QTime, Qt
from PyQt5.QtWidgets import (QAbstractItemView, QAbstractSpinBox, QAction, QApplication, QBoxLayout, QDateEdit, QDesktopWidget, QDoubleSpinBox, QFileDialog, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QComboBox, QMessageBox, QPushButton, QCheckBox, 
                            QFormLayout, QDockWidget, QSpinBox, QTableView, QHeaderView, QGraphicsView, QTableWidget, QTextEdit, QTimeEdit, QVBoxLayout, QWidget)
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis

from qt_material import apply_stylesheet

import matplotlib
matplotlib.use('Qt5Agg') # Configure the backend to use Qt5
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
import seaborn as sns
from FrameLayout import FrameLayout

class CreateCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, nrow=1, ncol=1):
        # Create Matplotlib Figure object
        figure = Figure(figsize=(6, 5), dpi=100)
        # Reserve width and height space for subplots
        figure.subplots_adjust(wspace= 0.3, hspace=0.4)
        # Create the axes and set the number of rows/columns for the subplot(s)
        self.axes = figure.subplots(nrow, ncol)
        
        super(CreateCanvas, self).__init__(figure)
        
class MyWorkoutsView(QChartView):
    
    def __init__(self, chart):
        super().__init__(chart)
        self.chart = chart
        
        self.start_pos = None
    
    def wheelEvent(self, event):
        """Reimplement the scroll wheel on the mouse for zooming in and out on the chart."""
        zoom_factor = 1.0 # Simple way to control the total amount zoomed in or out
        scale_factor = 1.10 # How much to scale into or out of the chart

        if event.angleDelta().y() >= 120 and zoom_factor < 3.0:
            zoom_factor *= 1.25
            self.chart.zoom(scale_factor)
        elif event.angleDelta().y() <= -120 and zoom_factor > 0.5:
            zoom_factor *= 0.8
            self.chart.zoom(1 / scale_factor)
            
    def mousePressEvent(self, event):
        """If the mouse button is pressed, change the mouse cursor and 
        get the coordinates of the click."""
        if event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.start_pos = event.pos()

class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.initializeUI()

    def initializeUI(self):
        
        self.setMinimumSize(1300, 650)
        self.setWindowTitle("My Workouts")
        self.createconnection()
        # self.setupWidgets()
        # self.setupChart()
        # self.setupToolsDockWidget()
        
        # self.setupMenu()
        self.setupTable1()
        self.show()
    
    def createconnection(self):
        self.database = QSqlDatabase.addDatabase("QSQLITE")
        self.database.setDatabaseName("databases/workout.sql")

        if not self.database.open():
            print("Unable to open data source file.")
            print("Connection failed: ", self.database.lastError().text())
            sys.exit(1) # Error code 1 - signifies error in opening file
    
        # Check if the tables we want to use exist in the database
        tables_needed = {'workouts'}
        tables_not_found = tables_needed - set(self.database.tables())
        if tables_not_found:
            QMessageBox.critical(None, 'Error',
                'The following tables are missing from the database: {}'.format(tables_not_found))
            sys.exit(1)
    
    def setupTable1(self):
        """
        
        """
        model = QSqlTableModel()
        model.setTable('workouts')
        model.setQuery(QSqlQuery("SELECT * FROM workouts"))

        table_view = QTableView()
        table_view.setModel(model)
        table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Populate the model with data
        model.select()

        # Main layout
        main_v_box = QVBoxLayout()
        main_v_box.addWidget(table_view)
        self.setCentralWidget(table_view)
    
    def setupMenu(self):
        """
        Menu
        """
        menu_bar = self.menuBar()
        menu_bar.setNativeMenuBar(False)

        add_workout_act = QAction('Add workouts from csv file', self)
        add_workout_act.triggered.connect(self.openCSVFile)
        # Create file menu and add actions
        file_menu = menu_bar.addMenu('File')
        file_menu.addAction(add_workout_act)
        # Create view menu and add actions
        view_menu = menu_bar.addMenu('View')
        view_menu.addAction(self.toggle_dock_tools_act)
        
    def setupWidgets(self):
        """Set up some default comboboxes
        """
        self.year_cb = QComboBox()
        self.current_year = QDate.currentDate().year()
        self.year_cb.addItem("2021")
        self.year_cb.addItem("2020")
        self.year_cb.setCurrentText("2021")
        self.year_cb.currentTextChanged.connect(self.changeYear)
        
        self.months = ["All","January","February","March","April","May","June","July","August","September","October","November","December"]
        self.month_cb = QComboBox()
        self.current_month = QDate.currentDate().month()
        self.month_cb.addItems(self.months[:self.current_month+1])
        self.month_cb.setCurrentIndex(len(self.months[:self.current_month+1])-1)
        self.month_cb.currentTextChanged.connect(self.changeMonth)
        
        self.current_day = QDate.currentDate().day()
        
        self.labels = ['Activity', 'Date', 'Timing', 'Distance (km)', 'Pace (km/in)']
        self.model = QStandardItemModel()
        
        self.data = self.loadJSONFile()

        self.do_not_call_changeMonth_function = False
    
    def setupChart(self):
        """
        
        """
        self.model.clear()
        self.model.setColumnCount(5)
        self.model.setHorizontalHeaderLabels(self.labels)
        
        activities, self.dates, durations, self.distances, paces = [], [], [], [], []
        for item in range(len(self.data)):
            activities.append(self.data[item][0])
            self.dates.append(self.data[item][1])
            durations.append(self.data[item][2])
            self.distances.append(self.data[item][3])
            paces.append(self.data[item][4])
        
        new_arr = []
        for i,d in enumerate(self.dates):
            t= d.split(' ')
            new_arr.append(t)
        
        selected_month = self.month_cb.currentText()
        selected_year = self.year_cb.currentText()
        
        self.filtered = []
        for i, date in enumerate(new_arr):
            values = []
            if str(date[1]) == str(selected_month)[:3]  and str(date[3]) == str(selected_year):
                values.append(date[2])
                values.append(self.data[i][2]) #timing
                values.append(self.data[i][3]) #disance
                values.append(self.data[i][4]) #pace
                self.filtered.append(values)
                values = []
        
        dates = []
        for value in self.filtered:
            dates.append(int(value[0]))
        
        if(self.current_year == int(selected_year) and self.current_month == self.months.index(selected_month)):
            num_days = QDate.currentDate().day()
        else:
            num_days = QDate(int(selected_year), self.months.index(selected_month), 1).daysInMonth()
        
        distance_series = np.empty(num_days+1) * np.nan
        distance_series[dates] = [value[2] for value in self.filtered]
        smask = np.isfinite(distance_series)
        
        canvas = CreateCanvas(self)
        x1 = np.arange(0,num_days+1)
        
        canvas.axes.bar(x1[smask],distance_series[smask],width=0.9, color='#152238', label='Distance (km)')
        canvas.axes.set_title(selected_month)
        canvas.axes.set_xlim([1,num_days+1])
        canvas.axes.set_ylim([0,8])
        canvas.axes.set_xticks(x1)
        canvas.axes.set_ylabel('Distance (km)')
        canvas.axes.set_xlabel('Days')
        canvas.axes.set_yticks(np.arange(0,8))
        canvas.axes.grid(which='major', axis='y', linestyle='--', alpha=0.2)

        
        pace_series = np.empty(num_days+1) * np.nan
        pace_series[dates] = [value[-1] for value in self.filtered]
        smask = np.isfinite(pace_series)
        
        axes2 = canvas.axes.twinx()
        axes2.plot(x1[smask],pace_series[smask], linestyle='--', marker='o', color='#F58735', label='Pace (min/km)')
        axes2.set_ylim([10,4])
        axes2.set_ylabel('Pace (min/km)')
        
        labels = [item.get_text() for item in axes2.get_yticklabels()]
        for i in range(len(labels)):
            labels[i] = '{}:00'.format(i+4)
            
        axes2.set_yticklabels(labels)
        
        canvas.figure.legend(loc="upper right", bbox_to_anchor=(1,1), bbox_transform=canvas.axes.transAxes)

        self.setCentralWidget(canvas)
        
        
        self.setupTable()
        
    
    def setupTable(self):
        """Update tableview
        """
        
        for value in range(len(self.filtered)):
            # line_series.append(self.distances[value])
            items = [QStandardItem(str(item)) for item in self.data[value]]
            self.model.insertRow(value, items)  
                   
    def loadJSONFile(self):
        """
        Load data from json
        """
        # data = {}
        with open('Files/workouts.json') as json_f:
            workout_data = json.load(json_f)
        
        row_values = []
        data_labels = []
        for workout in workout_data["workoutList"]:
            activity = workout["activity"]
            date = workout["date"]
            duration = workout["duration"]
            distance = workout["distance"]
            pace = workout["pace"]
            
            row_values.append(activity)
            row_values.append(date)
            row_values.append(duration)
            row_values.append(distance)
            row_values.append(pace)
            
            data_labels.append(row_values)
            row_values = []
        
        return data_labels
            
    def setupToolsDockWidget(self):
        """
        
        """
        tools_dock = QDockWidget()
        tools_dock.setWindowTitle("Tools")
        tools_dock.setMinimumWidth(400)
        tools_dock.setMaximumWidth(600)
        tools_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        theme_label = QLabel("Themes")
        themes_cb = QComboBox()
        themes_cb.addItems(["Light", "Cerulean Blue", "Dark"])
        # themes_cb.currentTextChanged.connect(self.changeChartTheme)
        
        animation_label = QLabel("Animations")
        self.animations_cb = QComboBox()
        self.animations_cb.addItem("No Animation", QChart.NoAnimation)
        self.animations_cb.addItem("Series Animation", QChart.SeriesAnimations)
        # self.animations_cb.currentIndexChanged.connect(self.changeAnimations)
        
        legend_label = QLabel("Legend position")
        self.legend_cb = QComboBox()
        self.legend_cb.addItem("No Legend")
        self.legend_cb.addItem("Align Left", Qt.AlignLeft)
        self.legend_cb.addItem("Align Top", Qt.AlignTop)
        self.legend_cb.addItem("Align Right", Qt.AlignRight)
        self.legend_cb.addItem("Align Bottom", Qt.AlignBottom)
        # self.legend_cb.currentTextChanged.connect(self.changeLegend)
        year_label = QLabel("Year")
        month_label = QLabel("Month")
        # self.antialiasing_check_box = QCheckBox()
        # self.antialiasing_check_box.toggled.connect(self.toggleAntialiasing)
        
        # self.month_cb.clear()
        # self.month_cb.currentTextChanged.connect(self.changeMonth)
        
        period_select_box = QGridLayout()
        period_select_box.addWidget(year_label, 0, 0)
        period_select_box.addWidget(month_label, 0, 1)
        period_select_box.addWidget(self.year_cb, 1, 0)
        period_select_box.addWidget(self.month_cb, 1, 1)
        
        reset_button = QPushButton("Reset Chart Axes")
        # reset_button.clicked.connect(self.resetChartZoom)
        
        add_data_button = QPushButton("Add new workout")
        add_data_button.clicked.connect(self.saveWorkout)
        
        self.data_table_view = QTableView()
        self.data_table_view.setModel(self.model)
        self.data_table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.data_table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.data_table_view.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        ## ADD WORKOUT FORM

        self.workout_name_entry = QLineEdit()
        
        self.date_entry = QDateEdit()
        self.date_entry.setDate(QDate.currentDate())
        self.date_entry.setFixedHeight(25)
        self.date_entry.setButtonSymbols(QAbstractSpinBox.NoButtons)
        
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
        
        # activity_v_box = QVBoxLayout()
        # activity_v_box.addWidget(QLabel("Activity"))
        # activity_v_box.addWidget(self.activity_type)
        
        # date_v_box = QVBoxLayout()
        # date_v_box.addWidget(QLabel("Date"))
        # date_v_box.addWidget(self.date_entry)
        
        # activity_date_h_box = QHBoxLayout()
        # activity_date_h_box.addLayout(activity_v_box)
        # activity_date_h_box.addLayout(date_v_box)
        
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
        
        # distance_v_box = QVBoxLayout()
        # distance_v_box.addWidget(QLabel("Distance (km)"))
        # distance_v_box.addWidget(self.distance_entry)
            
        
        # duration_v_box = QVBoxLayout()
        # duration_v_box.addWidget(QLabel("Duration"))
        # duration_v_box.addLayout(duration_h_box)
        
        # duration_distance_h_box = QHBoxLayout()
        # duration_distance_h_box.addLayout(duration_v_box)
        # duration_distance_h_box.addLayout(distance_v_box)
                
        pace_h_box = QHBoxLayout()
        pace_h_box.addWidget(self.pace_minutes)
        pace_h_box.addWidget(time_colon_label)
        pace_h_box.addWidget(self.pace_seconds)
        pace_h_box.addStretch()
        
        
        workout_details_grid = QGridLayout()
        # workout_details_grid.addLayout(activity_date_h_box,0,0,2,2)
        workout_details_grid.addWidget(QLabel("Activity"),0,0)
        workout_details_grid.addWidget(QLabel("Date"),0,1)
        workout_details_grid.addWidget(self.activity_type,1,0)
        workout_details_grid.addWidget(self.date_entry,1,1)
        workout_details_grid.addWidget(QLabel("Duration"),2,0)
        workout_details_grid.addWidget(QLabel("Distace (km)"),2,1)
        workout_details_grid.addLayout(duration_h_box,3,0)
        workout_details_grid.addWidget(self.distance_entry,3,1)
        
        
        add_run_form = QFormLayout()
        add_run_form.setLabelAlignment(Qt.AlignTop)
        add_run_form.addRow(QLabel("Workout Name"))
        add_run_form.addRow(self.workout_name_entry)
        add_run_form.addRow(workout_details_grid)
        add_run_form.addRow(QLabel("Pace (min/km)"))
        add_run_form.addRow(pace_h_box)
        
        save_workout_button = QPushButton("Save")
        save_workout_button.setObjectName("save")
        save_workout_button.clicked.connect(self.saveWorkout)
        
        add_workout = QVBoxLayout()
        add_workout.setAlignment(Qt.AlignTop)
        add_workout.addLayout(add_run_form)
        add_workout.addWidget(save_workout_button)
        
        add_workout_c = FrameLayout(title="Add New Workout")
        add_workout_c.addLayout(add_workout)
        
        
        ## FORM
        
        dock_form = QFormLayout()
        dock_form.setAlignment(Qt.AlignTop)
        dock_form.spacing()
        dock_form.addRow(period_select_box)
        dock_form.addRow(self.data_table_view)
        dock_form.addRow(add_workout_c)
        
        
        
        tools_container = QWidget()
        tools_container.setLayout(dock_form)
        tools_dock.setWidget(tools_container)
        
        self.addDockWidget(Qt.LeftDockWidgetArea, tools_dock)
        self.toggle_dock_tools_act = tools_dock.toggleViewAction()

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
        Get entry values, open json file and save data
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
                    "time": "",
                    "duration": run_time,
                    "distance": distance,
                    "pace": pace,
                    "notes": ""
                }
            )
            
            workout_data.update(workout_info)
            json_f.seek(0)
            json.dump(workout_data, json_f, indent=2)
        
        self.workout_name_entry.clear()
        self.minutes.setValue(0)
        self.seconds.setValue(0)
        self.distance_entry.setValue(0.1)
        self.pace_minutes.setValue(0)
        self.pace_seconds.setValue(0)
        self.refresh()
    
    def changeYear(self):
        """
        When cb year is changed, edit month according to availabe current month of the year
        """
        self.do_not_call_changeMonth_function = True
        self.month_cb.clear()
        if self.year_cb.currentText() == '2021':
            self.month_cb.addItems(self.months[:QDate.currentDate().month()+1])
            self.month_cb.setCurrentIndex(len(self.months[:QDate.currentDate().month()+1])-1)
        else:
            self.month_cb.addItems(self.months)
            self.do_not_call_changeMonth_function = False
            self.month_cb.setCurrentIndex(1)
        
        
        # self.setupChart()
    
    def changeMonth(self):
        """
        update table view when month is changed
        """
        if self.do_not_call_changeMonth_function is not None and self.do_not_call_changeMonth_function:
            print("skipping update")
            self.do_not_call_changeMonth_function = False
        else:
            self.setupChart()
    
    def refresh(self):
        """
        Refresh after add workout
        """
        self.data = self.loadJSONFile()
        self.setupChart()
    
    def openCSVFile(self):
        """
        Add list of workouts from CSV file
        """
        self.csv_file, _ = QFileDialog.getOpenFileName(self, "Open File",
                            os.getenv('Home'), "CSV (*.csv)")

        
        if self.csv_file:
            print('File loaded')
        else:
            QMessageBox.information(self, "Error",
                                    "No file loaded", QMessageBox.Ok)
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    # apply_stylesheet(app, theme='dark_purple.xml')
    sys.exit(app.exec_())