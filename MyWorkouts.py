from PyQt5.QtGui import QStandardItemModel
from AddWorkout import AddWorkoutGUI
import sys, json
import numpy as np
import PyQt5
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import (QApplication, QGridLayout, QLabel, QMainWindow, QComboBox, QPushButton, QCheckBox, 
                            QFormLayout, QDockWidget, QTableView, QHeaderView, QGraphicsView, QWidget)
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from AddWorkout import AddWorkoutGUI


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

        self.setupToolsDockWidget()
        self.setupChart()
        # self.setupMenu()
        self.show()
    
    def setupChart(self):
        """
        
        """

        self.model = QStandardItemModel()
        self.model.setColumnCount(5)
        self.model.setHorizontalHeaderLabels(['Activity', 'Date', 'Distance', 'Time', 'Pace'])
        
        data = self.loadJSONFile()
        self.data_arr = np.array(data)
        
        self.dates = self.data_arr[:,1]
        # self.distances = data_arr[:,2]
        # self.timings = data_arr[:,3]
        # self.paces = data_arr[:,4]
        
        self.split_dates = []
        for d in self.dates:
            self.split_dates.append(d.split(' '))
        
        
        self.drawChart()
        
    def drawChart(self):
        """
        Draw chart based on selected year and month
        """
        current_month = self.year_cb.currentText()
        current_year = self.month_cb.currentText()
        
        # for date in self.split_dates:
        #     if date[1] == current_month and date[2] == current_year:
                
            
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
        
        
        # self.antialiasing_check_box = QCheckBox()
        # self.antialiasing_check_box.toggled.connect(self.toggleAntialiasing)
        year_label = QLabel("Year")
        self.year_cb = QComboBox()
        self.year_cb.addItem("2021")
        self.year_cb.addItem("2020")
        self.year_cb.setCurrentText("2021")
        self.year_cb.currentTextChanged.connect(self.changeYear)
        
        self.months = ["All","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        month_label = QLabel("Month")
        self.month_cb = QComboBox()
        self.month_cb.addItems(self.months[:QDate.currentDate().month()+1])
        self.month_cb.setCurrentIndex(len(self.months[:QDate.currentDate().month()+1])-1)
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
        
        data_table_view = QTableView()
        
        dock_form = QFormLayout()
        dock_form.setAlignment(Qt.AlignTop)
        dock_form.addRow(theme_label)
        dock_form.addRow(themes_cb)
        dock_form.addRow(animation_label)
        dock_form.addRow(self.animations_cb)
        dock_form.addRow(legend_label)
        dock_form.addRow(self.legend_cb)
        dock_form.addRow(reset_button)
        dock_form.spacing()
        dock_form.addRow(period_select_box)
        dock_form.addRow(data_table_view)
        dock_form.addRow(add_data_button)
        
        
        tools_container = QWidget()
        tools_container.setLayout(dock_form)
        tools_dock.setWidget(tools_container)
        
        self.addDockWidget(Qt.LeftDockWidgetArea, tools_dock)

    
    def changeYear(self):
        """
        When cb year is changed, edit month according to availabe current month of the year
        """
        self.month_cb.clear()
        
        if self.year_cb.currentText() == '2021':
            self.month_cb.addItems(self.months[:QDate.currentDate().month()+1])
            self.month_cb.setCurrentIndex(len(self.months[:QDate.currentDate().month()+1])-1)
        elif self.year_cb.currentText() == '2020':
            self.month_cb.addItems(self.months)
            
            
    
    def addData(self):
        """
        Add new workout when button is clicked
        """
        # self.hide()
        self.add_workout = AddWorkoutGUI()
        # add_workout.startUI()
        self.add_workout.show()
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())