import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QCalendarWidget, QPushButton, QTextEdit, QListWidget, QListWidgetItem, QDialog
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QDate, Qt, QLocale  
import os
import re

class TodoDialog(QDialog):
    def __init__(self, date):
        super().__init__()
        self.date = date
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Video List')
        self.setGeometry(400, 400, 800, 600)

        self.video_list = QListWidget(self)
        self.video_list.itemDoubleClicked.connect(self.playVideo)

        vbox = QVBoxLayout()
        vbox.addWidget(self.video_list)

        self.setLayout(vbox)

        self.populateVideoList()

    def populateVideoList(self):
        connection = sqlite3.connect("todo.db")
        cursor = connection.cursor()

        cursor.execute("CREATE TABLE IF NOT EXISTS videos (date TEXT, filename TEXT)")
        
        # Convert self.date to "yyyy-MM-dd" format
        date_str = self.date.toString("yyyy-MM-dd")

        cursor.execute("SELECT filename FROM videos WHERE date=?", (date_str,))
        videos = cursor.fetchall()
        for video in videos:
            print(video[0])
            filename = video[0]
            item = QListWidgetItem(filename)
            self.video_list.addItem(item)

        connection.close()
        
    def playVideo(self, item):
        filename = item.text()
        filepath = os.path.join(".", filename)
        os.system(filepath)  # 해당 동영상을 재생합니다.

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        QLocale.setDefault(QLocale(QLocale.English, QLocale.UnitedStates))
        
        self.cal = QCalendarWidget(self)
        self.cal.setFirstDayOfWeek(Qt.Sunday)  # 시작 요일을 일요일로 설정
        self.cal.setGridVisible(True)
        self.cal.clicked[QDate].connect(self.showDate) # 클릭하면은

        self.lbl = QLabel(self)
        date = self.cal.selectedDate()
        self.lbl.setText(date.toString())

        self.vbox = QVBoxLayout()   # 기본 간격
        self.vbox.addWidget(self.cal) # 달력
        self.vbox.addWidget(self.lbl) # 출력 라벨

        self.setLayout(self.vbox) # 간격 set

        self.setWindowTitle('Record (Made by TCK)')
        self.setGeometry(400, 400, 800, 600)
        self.show()
        connection = sqlite3.connect("todo.db")
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS videos (date TEXT, filename TEXT)")
        connection.close()
        
        # Add video files to the database
        self.addVideosToDatabase()

        # Color calendar dates based on the number of videos
        self.colorCalendarDates()

    def showDate(self, date):
        self.lbl.setText(date.toString()) # 날짜 좌측 하단에 출력하고
        self.openTodoDialog(date) 

    def openTodoDialog(self, date): # 바로 Todo 창 출력
        dialog = TodoDialog(date)
        dialog.exec_()

    def addVideosToDatabase(self):
        connection = sqlite3.connect("todo.db")
        cursor = connection.cursor()

        # duplicate 방지
        # Clear the existing videos table
        cursor.execute("DROP TABLE IF EXISTS videos")
        cursor.execute("CREATE TABLE videos (date TEXT, filename TEXT)")

        # Insert videos from the current folder
        video_files = set()
        for filename in os.listdir("."):
            if filename.endswith(".avi"):
                date_match = re.search(r"(\d{4}-\d{2}-\d{2})", filename)
                if date_match:
                    date = date_match.group(0)
                    video_files.add((date, filename))

        for date, filename in video_files:
            cursor.execute("INSERT INTO videos (date, filename) VALUES (?, ?)", (date, filename))

        connection.commit()
        connection.close()
            
    def colorCalendarDates(self):
        connection = sqlite3.connect("todo.db")
        cursor = connection.cursor()

        cursor.execute("CREATE TABLE IF NOT EXISTS videos (date TEXT, filename TEXT)")
        cursor.execute("SELECT date, COUNT(*) FROM videos GROUP BY date")
        video_counts = cursor.fetchall()

        for date, count in video_counts:
            date_obj = QDate.fromString(date, "yyyy-MM-dd")
            if count == 1:
                self.cal.setDateTextFormat(date_obj, self.createBackgroundFormat(QColor(144, 238, 144)))
            elif count == 2:
                self.cal.setDateTextFormat(date_obj, self.createBackgroundFormat(QColor(255, 223, 186)))
            elif count >= 3:
                self.cal.setDateTextFormat(date_obj, self.createBackgroundFormat(QColor(240, 128, 128)))

        connection.close()

    def createBackgroundFormat(self, color):
        background_format = self.cal.dateTextFormat(QDate.currentDate())
        background_format.setBackground(color)
        return background_format

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())