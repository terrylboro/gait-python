import time

import serial
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal
from serial.tools import list_ports

class ViconCommsSignals(QObject):
    # signals to communicate with main controller
    start_record = pyqtSignal()
    stop_record = pyqtSignal()



class ViconComms(QRunnable):
    """ this class controls the communcation with Vicon via the serial port """
    def __init__(self, port="COM6", baudrate=1000000):
        super(ViconComms, self).__init__()
        # setup serial object, port and baudrate chosen by user
        self.mSerial = serial.Serial()
        self.mSerial.port = port
        self.mSerial.baudrate = baudrate
        self.signals = ViconCommsSignals() # must do it this way as only QObject has signals
        # open the serial port
        print("Setting up serial port...")
        time.sleep(0.1)
        self.mSerial.open()
        self.mSerial.flushInput()
        time.sleep(0.5)
        print("Set up serial port!")

    def __del__(self):
        print("串口异常", "此串口不能被打开\nSerial port exception", "This serial port cannot be opened!")
        print("ViconComms object deleted")

    def set_port(self, port):
        """ set the COM port to use for serial communications """
        self.mSerial.port = port
        print("Vicon port is now on: ", port)

    # 串口检测 search for available COM ports
    def serial_port_check(self):
        # 检测所有存在的串口，将信息存储在字典中
        # Detect all existing serial ports and store the information in a dictionary
        """ detect serial ports and add them to dropdown box """
        # Com_Dict = {}
        port_list = list(list_ports.comports())
        return port_list
        # self.ComNoSelect.clear()
        # for port in port_list:
        #     Com_Dict["%s" % port[0]] = "%s" % port[1]
        #     self.ComNoSelect.addItem(port[0])
        # # 无串口判断
        # if len(self.Com_Dict) == 0:
        #     self.ComNoSelect.addItem("None Found")

    def run(self):
        """ polls the serial port and relays the result to the main thread, 0 = stop and 1 = go """
        prevVal = b'0'
        while True:
            # Wait until there is data waiting in the serial buffer
            if self.mSerial.in_waiting > 0:
                # return True if byte 0x01 (i.e. int 1) received else (assumed to be 0) False
                val_received = self.mSerial.read(1)
                if val_received == b'1':
                    self.signals.start_record.emit()
                    print("Vicon capture started!")
                if val_received == b'1':
                        print("Vicon capture started!")
                        self.signals.start_record.emit()
                elif val_received == b'0':
                        self.signals.stop_record.emit()
                else: print("received un recognised character: ", val_received)
                prevVal = val_received
                # print(val_received)
                # if val_received != prevVal:
                #     if val_received == 0x01:
                #         print("Recording triggered!")
                #         self.start_record.emit()
                #     elif val_received == 0x00:
                #         print("Recording ended!")
                #         self.stop_record.emit()

    def TrigerVicon_Start(self):
        self.CMD_Start = '61' #'AB'
        self.success_bytes = self.mSerial.write(bytes.fromhex(self.CMD_Start))
        # while (not (self.CMD_Return[0] == 0xAB)):
        #     self.success_bytes = self.mSerial.write(bytes.fromhex(self.CMD_Start))
        #     if (self.mSerial.inWaiting()):
        #         self.CMD_Return = self.mSerial.read(self.mSerial.inWaiting())
        print("VICON has started")

    def TrigerVicon_Stop(self):
        self.CMD_Stop = '62' #'CD'
        # self.success_bytes = self.mSerial.write(bytes.fromhex(self.CMD_Start))
        self.success_bytes = self.mSerial.write(bytes.fromhex(self.CMD_Stop))
        # while (not (self.CMD_Return[0] == 0xCD)):
        #     self.success_bytes = self.mSerial.write(bytes.fromhex(self.CMD_Stop))
        #     if (self.mSerial.inWaiting()):
        #         self.CMD_Return = self.mSerial.read(self.mSerial.inWaiting())
        print("VICON has stoped")
