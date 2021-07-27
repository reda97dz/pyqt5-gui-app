from PyQt5.QtGui import QStandardItem, QStandardItemModel
from numpy.core import einsumfunc
from AddWorkout import AddWorkoutGUI
import sys, json
import numpy as np
import PyQt5
from PyQt5.QtCore import QDate, QLine, Qt
from PyQt5.QtWidgets import (QAbstractItemView, QApplication, QGridLayout, QLabel, QMainWindow, QComboBox, QPushButton, QCheckBox, 
                            QFormLayout, QDockWidget, QTableView, QHeaderView, QGraphicsView, QWidget)
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from AddWorkout import AddWorkoutGUI
from qt_material import apply_stylesheet

import matplotlib
matplotlib.use('Qt5Agg') # Configure the backend to use Qt5
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure

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
        
        self.setMinimumSize(1200, 600)
        self.setWindowTitle("My Workouts")
       
        self.setupWidgets()
        self.setupChart()
        self.setupToolsDockWidget()
        
        # self.setupMenu()
        self.show()
    
    def setupWidgets(self):
        """Set up some default comboboxes
        """
        self.year_cb = QComboBox()
        self.current_year = QDate.currentDate().year()
        self.year_cb.addItem("2021")
        self.year_cb.addItem("2020")
        self.year_cb.setCurrentText("2021")
        self.year_cb.currentTextChanged.connect(self.changeYear)
        
        self.months = ["All","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        self.month_cb = QComboBox()
        self.current_month = QDate.currentDate().month()
        self.month_cb.addItems(self.months[:self.current_month+1])
        self.month_cb.setCurrentIndex(len(self.months[:self.current_month+1])-1)
        self.month_cb.currentTextChanged.connect(self.changeMonth)
        
        self.current_day = QDate.currentDate().day()
        
        self.labels = ['Activity', 'Date', 'Distance (km)', 'Timing', 'Pace (km/in)']
        self.model = QStandardItemModel()
        
        self.data = self.loadJSONFile()
    
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
        # self.filterData()
        
        self.filtered = []
        for i, date in enumerate(new_arr):
            values = []
            if str(date[1]) == str(selected_month)  and str(date[3]) == str(selected_year):
                values.append(date[2])
                values.append(self.data[i][2])
                values.append(self.data[i][3])
                values.append(self.data[i][4])
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
        
        canvas.axes.bar(x1[smask],distance_series[smask],width=0.9)
        
        # canvas.axes.plot(x1[smask], distance_series[smask], linestyle='-', marker='o')
        canvas.axes.set_xlim([1,num_days+1])
        canvas.axes.set_ylim([0,8])
        canvas.axes.set_xticks(x1)
        canvas.axes.set_yticks(np.arange(0,8))
        canvas.axes.grid(which='major', axis='y', linestyle='--')
        
        pace_series = np.empty(num_days+1) * np.nan
        pace_series[dates] = [value[-1] for value in self.filtered]
        smask = np.isfinite(pace_series)
        
        axes2 = canvas.axes.twinx()
        axes2.plot(x1[smask],pace_series[smask],linestyle='-', marker='o')
        axes2.set_ylim([10,4])
        
        # test = np.array([0,2,5,8,6,4,2,1,5,6])
        # x = np.arange(len(test))
        
        # canvas = CreateCanvas(self)
        # canvas.axes.plot(x, test)
        # self.addToolBar(NavigationToolbar2QT(canvas, self))
        self.setCentralWidget(canvas)
        
        
        self.setupTable()
    
    def filterDate(self):
        """Filter data according to selected month and year
        """
        
    
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
        add_data_button.clicked.connect(self.addData)
        
        self.data_table_view = QTableView()
        self.data_table_view.setModel(self.model)
        self.data_table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.data_table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.data_table_view.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        dock_form = QFormLayout()
        dock_form.setAlignment(Qt.AlignTop)
        # dock_form.addRow(theme_label)
        # dock_form.addRow(themes_cb)
        # dock_form.addRow(animation_label)
        # dock_form.addRow(self.animations_cb)
        # dock_form.addRow(legend_label)
        # dock_form.addRow(self.legend_cb)
        # dock_form.addRow(reset_button)
        dock_form.spacing()
        dock_form.addRow(period_select_box)
        dock_form.addRow(self.data_table_view)
        dock_form.addRow(add_data_button)
        
        
        
        tools_container = QWidget()
        tools_container.setLayout(dock_form)
        tools_dock.setWidget(tools_container)
        
        self.addDockWidget(Qt.LeftDockWidgetArea, tools_dock)

    
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
        
    def addData(self):
        """
        Add new workout when button is clicked
        """
        # self.hide()
        self.add_workout = AddWorkoutGUI(self)
        # add_workout.startUI()
        self.add_workout.show()
        
        # self.refresh()
    
    def refresh(self):
        """
        Refresh after add workout
        """
        self.data = self.loadJSONFile()
        self.setupChart()
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    # apply_stylesheet(app, theme='dark_amber.xml')
    sys.exit(app.exec_())