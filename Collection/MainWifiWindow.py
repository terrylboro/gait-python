import sys
import time
from queue import Queue

from PyQt5.QtCore import QThreadPool
from PyQt5 import QtWidgets

# from PlotGraphs import Plot_Graphs
from ViconComms import ViconComms
# from WifiPort import Thread_Serial

#### Changes for testing the old, single timestamp code ######
# from WifiPortOneTimestamp import Thread_Serial
# from PlotGraphsOneTimestamp import Plot_Graphs
from WifiPortReduced import Thread_Serial
from PlotGraphsReduced import Plot_Graphs
############################################

from Collection.ControlWindow import Ui_MainWindow
# Visualisation
from Visualisation.Functions.plot_gait_data import plot_gait_data
from Visualisation.Functions.plot_imu_xyz import plot_imu_xyz
from Visualisation.Functions.plot_all_new_data import plot_all_new_data_timestamped
import pandas as pd
import numpy as np

import os


class MainWifiWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(MainWifiWindow, self).__init__()
        # IMU details
        self.queue_IMU = Queue(maxsize=0)
        # threading
        # setup thread pool
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
        # initialise wifi thread as None so graph only opens when there's connection
        self.wifi_thread = None
        self.isRunning = False  # Initialise to not running state
        # self.mSerial = serial.Serial()
        self.DataSaveEnabled = False
        self.UsingVicon = False  # Change this to true to incorporate Vicon
        self.IsMobileLab = False  # Set to true if using mobile lab (i.e. receiver rather than trigger)
        if self.UsingVicon:
            self.serial_worker = ViconComms(port="COM6", baudrate=1000000)  # setup vicon with selected port

        # variables for saving data
        self.filename = "Filename"  # set default value
        # self.filedir = str(sys.path[0])  # default path is current directory
        self.filedir = str(sys.path[1] + "\\Data")  # default path is current directory
        self.imudatafile = None  # this will be the variable storing the .txt file
        self.firstFrameFlag = True  # this is set to false once we start saving
        # self.colNames = open("C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Utils/timestampedColumnHeaders", "r").read()
        self.colNames = open("C:/Users/teri-/PycharmProjects/fourIMUReceiverPlotter/Utils/reducedColumnHeaders",
                             "r").read()

        # variables to process the incoming data frames
        self.prevFrameNum = None  # this will be populated  in DataSave

        # layout and windows
        self.graphwindow = None  # No external window yet.
        self.setupUi(self)
        # pre-fill boxes and labels
        if self.UsingVicon:
            self.serial_port_check()  # check COM ports used for Vicon trigger
        self.label_address.setText("Not Connected")
        self.prefill_entries()
        self.fill_activity_entry()
        # decide which buttons you can press at start
        # self.startRunButton.setEnabled(False)
        self.stopRunButton.setEnabled(False)
        self.openGraphButton.setEnabled(False)
        self.saveDataButton.setEnabled(False)
        self.viewLatestButton.setEnabled(False)

        # connect signals
        self.wifiButton.clicked.connect(self.evt_start_wifi)
        self.openGraphButton.clicked.connect(self.show_new_window)
        # self.startRunButton.clicked.connect(self.data_collect_enable)
        if not self.IsMobileLab:
            self.stopRunButton.clicked.connect(self.stop_session)
            self.saveDataButton.clicked.connect(self.data_save_enable)
        self.ComNoSelect.currentTextChanged.connect(self.on_vicon_dropdown_changed)
        self.viewLatestButton.clicked.connect(self.view_latest_data)
        # self.wifi_thread.IMU_Data_Slot.connect(self.graphwindow.Plot_IMUData)

    # Open the graph only if the WiFi is connected
    def show_new_window(self, checked):
        """ open the graphing window. Only works if WiFi connected """
        if self.graphwindow is None:
            if self.wifi_thread:
                self.graphwindow = Plot_Graphs()
                self.graphwindow.Plot_Init()
                self.graphwindow.show()
                self.data_collect_enable()  # start streaming on opening
            else:
                print("Need to connect to WiFi!")

        else:
            self.graphwindow.close()  # Close window.
            self.graphwindow = None  # Discard reference (so we can reinstantiate another graph later).

    # When WiFi button is pressed, connect to IMU device (client) with TCP server
    def evt_start_wifi(self):
        """ connect to IMU device (client) with TCP server """
        if not self.wifi_thread:
            self.wifi_thread = Thread_Serial(self.queue_IMU)
            # self.wifi_thread.start()
            self.label_address.setText(self.wifi_thread.address[0])
            self.openGraphButton.setEnabled(True)
        else:
            print("already connected to WiFi!")

    # 串口检测 search for available COM ports
    def serial_port_check(self):
        # 检测所有存在的串口，将信息存储在字典中
        # Detect all existing serial ports and store the information in a dictionary
        """ detect serial ports and add them to dropdown box """
        self.Com_Dict = {}
        port_list = self.serial_worker.serial_port_check()
        self.ComNoSelect.clear()
        for port in port_list:
            self.Com_Dict["%s" % port[0]] = "%s" % port[1]
            self.ComNoSelect.addItem(port[0])
        # 无串口判断
        if len(self.Com_Dict) == 0:
            self.ComNoSelect.addItem("None Found")

    def serial_port_open(self):
        """ open serial comms with Vicon """
        self.mSerial.port = self.ComNoSelect.currentText()  # 串口号
        self.mSerial.baudrate = 1000000  # 波特率
        try:
            time.sleep(0.1)
            self.mSerial.open()
            self.mSerial.flushInput()
            time.sleep(0.5)
        except:
            print("串口异常", "此串口不能被打开\nSerial port exception", "This serial port cannot be opened!")
            return None

    # pre-fill the boxes with the file path and default file name
    def prefill_entries(self):
        """ pre-fill the boxes with the file path and default file name """
        self.subjectLineEdit.setText("subjectName")
        self.trialNumLineEdit.setText("2")

    def fill_activity_entry(self):
        """ pre-fill the list of activities dropbox """
        activities = ["Static", "Walk", "WalkShake", "WalkNod", "WalkSlow", "Sit2Stand", "Stand2Sit", "TUG", "Reach", "PickUp"]
        self.activityComboBox.addItems(activities)
        self.activityComboBox.setCurrentText("Static")

    def vicon_start(self):
        """ triggers Vicon system to start via serial signal """
        cmdstart = 'AB'
        while not (self.CMD_Return[0] == 0xAB):
            success_bytes = self.mSerial.write(bytes.fromhex(cmdstart))
            if self.mSerial.inWaiting():
                self.CMD_Return = self.mSerial.read(self.mSerial.inWaiting())
        print("VICON has started")

    def vicon_stop(self):
        """ sends signal to stop Vicon """
        cmdstop = 'CD'
        while (not (self.CMD_Return[0] == 0xCD)):
            success_bytes = self.mSerial.write(bytes.fromhex(cmdstop))
            if self.mSerial.inWaiting():
                self.CMD_Return = self.mSerial.read(self.mSerial.inWaiting())
        print("VICON has stopped")

    # enable data collection by the IMU system
    def data_collect_enable(self):
        """ set run state on. Open serial comms. Run data streaming via TCP. This does not perform saving,
         for this use self.data_save_enable() and self.data_save() """
        if not self.wifi_thread:
            print("Must connect to WiFi first!")
        else:
            self.isRunning = True
            self.wifi_thread.isStopped = False
            # self.Data_Save_Enable()
            if self.UsingVicon:
                # serial_worker = ViconComms(self.ComNoSelect.currentText()) # setup vicon with selected port
                self.serial_worker.signals.start_record.connect(self.data_save_enable)
                self.serial_worker.signals.stop_record.connect(self.stop_session)
                self.threadpool.start(self.serial_worker)
                # if self.IsMobileLab:
                    # self.serial_worker.run()
                # self.serial_port_open()
            self.wifi_thread.IMU_Data_Slot.connect(self.plot_data)
            # self.wifi_thread.UDP_Data_Slot.connect(self.udpTest)
            self.wifi_thread.start()
            self.stopRunButton.setEnabled(True)
            self.saveDataButton.setEnabled(True)
            # self.startRunButton.setEnabled(False)

    # setup the data
    def data_save_enable(self):
        """ initialise setup for saving data. Triggers Vicon if self.UsingVicon is true """
        if not self.check_filepath():
            self.DataSaveEnabled = True
            self.saveDataButton.setEnabled(False)
            if self.UsingVicon:
                if not self.IsMobileLab:
                    print("Triggering vicon")
                    self.serial_worker.TrigerVicon_Start()
        else:
            print("Check the file-related entries are valid!")

    def check_filepath(self):
        """ Check and ensure that the filepath written to is valid """
        filename = self.subjectLineEdit.text().strip() + "-"\
                        + self.trialNumLineEdit.text().strip().zfill(2) + '.txt'
        subject_dir = str(self.filedir) + '/' + self.subjectLineEdit.text().strip() + '/'
        activity_dir = subject_dir + str(self.activityComboBox.currentText()) + '/'
        # Check that we're not going to overwrite a file
        self.latestFilePath = activity_dir + filename
        print("Saving to: ", self.latestFilePath)
        # if os.path.isfile(self.latestFilePath):
        #     # print("This file already exits! Check the details")
        #     print("Overwriting file!")
        #     return True
        # else:
        # first create a new dir if it didn't already exist
        if not os.path.isdir(subject_dir):
            try:
                os.mkdir(subject_dir)
            except OSError as error:
                print(error)
        if not os.path.isdir(activity_dir):
            try:
                os.mkdir(activity_dir)
            except OSError:
                print("Adding to existing folder")
        return False

    # saving the data
    def data_save(self, IMU_Data):
        # Vicon使用Triger方法同步，所以Python不再需要接收和保存Vicon的数据
        # Vicon uses the Trigger method to synchronize, so Python no longer needs to receive and save Vicon's data
        """ Writes the incoming data from the IMU device to a .txt file. With Vicon, the trigger method ensures it
        is already synchronised, so this data does not need to be saved here in Python """
        frametosave = IMU_Data
        # if this is the first frame, we need to open a new file and set the previous frame number
        if self.firstFrameFlag:
            self.imudatafile = open(self.latestFilePath, "w")
            self.prevFrameNum = frametosave[0]
            frametosave[0] = 1
            self.firstFrameFlag = False
            self.imudatafile.writelines([self.colNames, '', '\n'])
        # otherwise we can just find the difference between frame numbers
        else:
            incomingPrevFrameNum = frametosave[0]
            frametosave[0] = frametosave[0] - self.prevFrameNum
            self.prevFrameNum = incomingPrevFrameNum
        # in both cases, we write the incoming data to the file
        datatowrite = [round(x, 4) if i > 0 else x for i, x in enumerate(frametosave)]  # some kind of byte conversion?
        datatowrite = str(datatowrite)
        self.imudatafile.writelines([datatowrite[1:-1], '', '\n'])  # 序列转字符串时，会将[]也转成2个字符‘[’‘]’，存储时需要将字符‘[’‘]’去掉

    def stop_session(self):
        if not self.isRunning:
            print("Run not started yet!")
        else:
            if self.UsingVicon:
                print("Vicon capture ended!")
                if not self.IsMobileLab:
                    self.serial_worker.TrigerVicon_Stop()
            if self.DataSaveEnabled:
                self.imudatafile.close()
                self.DataSaveEnabled = False
            self.wifi_thread.isStopped = True
            # allow saving to a new file
            self.firstFrameFlag = True
            self.openGraphButton.setEnabled(True)
            # self.startRunButton.setEnabled(False)
            self.stopRunButton.setEnabled(True)
            self.saveDataButton.setEnabled(True)
            # Enable the last trial to be plotted
            self.viewLatestButton.setEnabled(True)
            # autoincrement the trial number
            self.trialNumLineEdit.setText(str(int(self.trialNumLineEdit.text()) + 1))
            print("Returned to default")

    def plot_data(self, imudata):
        """ send the data received from the IMU data slot to be plotted  """
        # only perform plotting when the window is open
        if self.graphwindow:
            self.graphwindow.Plot_IMUdata(imudata)
            if self.DataSaveEnabled:
                self.data_save(imudata)

    def on_vicon_dropdown_changed(self, value):
        """ update the serial port of the Vicon according to the dropdown box val """
        if self.UsingVicon:
            self.serial_worker.set_port(value)

    def view_latest_data(self):
        plot_all_new_data_timestamped(self.latestFilePath, self.subjectLineEdit.text())
