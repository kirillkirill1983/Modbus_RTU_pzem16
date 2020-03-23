from PyQt5 import QtCore, QtWidgets
from modbus_rtu_design import Ui_MainWindow
import sys
import time
import csv
import serial
import modbus_tk
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu


class MyThread(QtCore.QThread):

    mysignal = QtCore.pyqtSignal(str)
    master = modbus_rtu.RtuMaster(serial.Serial(
        port="COM3", baudrate=9600, bytesize=8, parity='N', stopbits=1, xonxoff=0))

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.running = False   # Флаг выполнения
        self.count = 0

    def run(self):
        self.running = True
        while self.running:    # Проверяем значение флага
            self.master.set_timeout(2.0)
            self.master.set_verbose(True)
            self.measure = self.master.execute(
                1, cst.READ_INPUT_REGISTERS, 0, 10)
            self.a = str(self.measure[0] / 10)
            self.mysignal.emit("%s" % self.a)
            self.sleep(4)      # Имитируем процесс


class ThreaderTime(QtCore.QThread):
    timer = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.running = False

    def run(self):
        self.running = True
        while self.running:    # Проверяем значение флага
            self.time = QtCore.QTimer()
            a = time.strftime("%H:%M:%S")
            self.timer.emit(a)
            self.sleep(1)


class mywindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.threadtimer = ThreaderTime()
        self.threadtimer.timer.connect(
            self.on_timr, QtCore.Qt.QueuedConnection)
        #self.time = QtCore.QTimer()

        self.mythread = MyThread()     # Создаем экземпляр класса
        self.ui.pushButton.clicked.connect(self.on_start)
        self.ui.pushButton_2.clicked.connect(self.on_stop)
        self.mythread.mysignal.connect(self.on_change,
                                       QtCore.Qt.QueuedConnection)

    def on_start(self):
        if not self.mythread.isRunning():
            self.mythread.start()     # Запускаем поток
        if not self.threadtimer.isRunning():
            self.threadtimer.start()

    def on_stop(self):
        self.mythread.running = False  # Изменяем флаг выполнения

    def on_change(self, t):
        self.ui.label.setText(t)
        # Запись значение в файл есть проблема !! добовляет пустое поле
        volt = list(str(t))
        time_pole = list(time.strftime("%H:%M:%S"))
        data = [{"name":time_pole,"age":volt}]
        columns = ["name", "age"]
        #writer.writeheader()
        with open('mod_bus_int.csv', 'a',newline="") as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writerows(data)

    def on_timr(self, s):
        self.ui.label_2.setText(s)

    def closeEvent(self, event):       # Вызывается при закрытии окна
        self.hide()                    # Скрываем окно
        self.mythread.running = False  # Изменяем флаг выполнения
        self.mythread.wait(5000)       # Даем время, чтобы закончить
        event.accept()                 # Закрываем окно


app = QtWidgets.QApplication([])
application = mywindow()
application.setWindowTitle("modbus_rtu_design")
application.show()

sys.exit(app.exec())
