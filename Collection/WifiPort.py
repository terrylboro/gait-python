from PyQt5.QtCore import QThread, pyqtSignal
import time
import serial
import struct
import socket
import numpy as np
import datetime

class Thread_Serial(QThread):
    # 信号槽必须定义成类属性，而不能是实例属性，即:必须在__init__之前定义，而且前面不加self.
    # The signal slot must be defined as a class attribute, not an instance attribute,
    # that is, it must be defined before __init__, and self is not preceded.
    IMU_Data_Slot = pyqtSignal(list)
    UDP_Data_Slot = pyqtSignal(list) # for sending the data to unity
    connection_address = pyqtSignal(str)
    def __init__(self, queue_IMU):
        super(Thread_Serial, self).__init__()
        self.queue_IMU = queue_IMU
        self.NextPart = bytes()
        self.LastPart = bytes()
        self.Current = bytes()
        self.Last = bytes()
        self.HeadFound = False
        # self.FrameLength = 116
        # self.FrameLength = 156
        # self.FrameLength = 168
        self.FrameLength = 184
        self.DataSave_Init = True
        self.isStopped = False
        # 指定协议
        # specify protocol
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 让端口可以重复使用
        # Make the port reusable
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 绑定ip和端口
        # bind ip and port
        self.server.bind(('', 2233))
        # 监听 monitor the port
        self.server.listen(1)
        # 等待消息
        print("waiting to accept server")
        self.clientsocket, self.address = self.server.accept()
        print("addresses are: ", str(self.address))
        # self.connection_address.emit(self.address)
        self.AntiJitter_Counter = 0
        self.AntiInter_Counter = 0
        self.GyroX_Last = 0
        self.GyroY_Last = 0
        self.GyroZ_Last = 0

    def setIdentity(self, text):
        self.identity = text

    # 处理要做的业务逻辑
    # Handle the business logic to be done
    def run(self):
        while True:
            self.Serial_RxData = self.clientsocket.recv(self.FrameLength)
            # print(len(self.Serial_RxData))
            if len(self.Serial_RxData) == self.FrameLength:
                # 索引帧头
                # 如果找到，从帧头开始，将数据截成2段，帧头之前放LastPart，帧头+帧头之后放Current
                # 如果未找到，全部数据放LastPart
                # index frame header
                # If found, start from the frame header, cut the data into 2 segments, put LastPart before the frame header,
                # and put Current after the frame header + frame header
                # If not found, put all data in LastPart
                for self.index, self.checker in enumerate(self.Serial_RxData):
                    # print("self.checker is: ", self.checker)
                    # print("self.index is: ", self.index)
                    if self.checker == 0xAA and self.index < (len(self.Serial_RxData)-1):
                        # print("self.Serial_RxData[self.index+1] is: ", self.Serial_RxData[self.index+1])
                        if self.Serial_RxData[self.index+1] == 0xBB:
                            self.LastPart = self.Serial_RxData[0:self.index]
                            self.Current = self.Serial_RxData[self.index:len(self.Serial_RxData)]
                            self.HeadFound = True
                            break
                # 如果未找到帧头，数据全部放LastPart
                # If no frame header is found, all data will be placed in LastPart
                if not self.HeadFound:
                    # print("no head found")
                    self.LastPart = self.Serial_RxData
                    self.Current = bytes()

                # 将本次读取的LastPart和之前的Last部分拼接，检查长度够不够1帧，如果超过1帧长度，则提取帧
                # 如果提取到帧，帧后面还有数据，则判断本次接收数据是否包含帧头
                # 若未接收到帧头，说明帧提取后剩余的数据和当前接收的数据可能是同一帧数据，二者均需要保留，以供拼接
                # 若本次接收到帧头，提取帧后还剩余的数据为无效数据，丢弃
                # Splice the LastPart read this time with the previous Last part, check if the length is enough for 1 frame, if it exceeds 1 frame length, extract the frame
                # If the frame is extracted and there is data behind the frame, then judge whether the received data contains the frame header
                # If the frame header is not received, it means that the remaining data after frame extraction and the currently received data may be the same frame data, and both need to be reserved for splicing
                # If the frame header is received this time, the remaining data after extracting the frame is invalid and discarded
                self.Last = self.Last + self.LastPart
                # print("self.Last is: ", str(self.Last))
                # print("self.FrameLength is: ", str(self.FrameLength))
                if len(self.Last) >= self.FrameLength:
                    for self.index_last, self.checker_last in enumerate(self.Last):
                        # print("self.checker_last is: ", self.checker_last)
                        # print("self.index_last is: ", self.index_last)
                        # print("self.Last[self.index_last + 1] is: ", self.Last[self.index_last + 1])
                        if self.checker_last == 0xAA and self.index_last < (len(self.Last) - 1):
                            if self.Last[self.index_last + 1] == 0xBB and (len(self.Last) - self.index_last) >= self.FrameLength:
                                self.Last_next = self.Last[self.index_last + self.FrameLength:len(self.Last)]
                                self.Last = self.Last[self.index_last: self.index_last+self.FrameLength]
                                # print("extracting data...")
                                self.Data_Extract(self.Last)
                                self.Last = self.Last_next
                                break
                if self.HeadFound:
                    self.Last = bytes()
                # 如果接收到帧头，在处理完帧头之前的数据以后，检查帧头后面的数据有无完整帧，并确定有几帧
                # If the frame header is received, after processing the data before the frame header,
                # check whether the data after the frame header has a complete frame, and determine how many frames there are
                self.Len_Current = len(self.Current)
                # print(self.Len_Current)
                self.N_Frame = self.Len_Current // self.FrameLength
                # self.Len_NextPart = self.Len_Current % self.FrameLength
                for i in range(self.N_Frame):
                    self.Frame = self.Current[self.FrameLength*i:self.FrameLength*(i+1)]
                    # print("extracting data...")
                    self.Data_Extract(self.Frame)
                self.NextPart = self.Current[self.N_Frame*self.FrameLength:self.Len_Current]
                # 将本次帧提取之后，后面剩余的数据保留，以供下次接收数据后拼接
                # 注意，程序运行到这里，如果有提取到帧，则帧之前的无效数据已全部丢弃，如果没有提取到帧，则所有数据都会保留，供下次拼接
                # After this frame is extracted, the rest of the data will be kept for splicing after receiving data next time
                # Note that when the program runs here, if a frame is extracted, all invalid data before the frame has been discarded,
                # and if no frame is extracted, all data will be retained for the next splicing
                self.Last = self.Last + self.NextPart
                self.HeadFound = False
                # else:
                #     time.sleep(0.001)

    def Data_Extract(self, Frame_Data):
        # print(Frame_Data)
        self.FrameNumber = Frame_Data[2:6]
        self.FrameNumber = self.FrameNumber[0] << 24 | self.FrameNumber[1] << 16 | self.FrameNumber[2] << 8 | \
                           self.FrameNumber[3]
        if self.FrameNumber > 1882400000 or self.FrameNumber < 0:
            print(self.FrameNumber)

        # self.TimeStamp = Frame_Data[6:10]
        # self.TimeStamp = self.TimeStamp[0] << 24 | self.TimeStamp[1] << 16 | self.TimeStamp[2] << 8 | \
        #                    self.TimeStamp[3]

        self.AccelTimeStampA = Frame_Data[6:10]
        self.AccelTimeStampA = self.AccelTimeStampA[0] << 24 | self.AccelTimeStampA[1] << 16 | self.AccelTimeStampA[2] << 8 | \
                         self.AccelTimeStampA[3]
        self.AccelTimeStampB = Frame_Data[10:14]
        self.AccelTimeStampB = self.AccelTimeStampB[0] << 24 | self.AccelTimeStampB[1] << 16 | self.AccelTimeStampB[2] << 8 | \
                          self.AccelTimeStampB[3]
        self.MagTimeStampA = Frame_Data[14:18]
        self.MagTimeStampA = self.MagTimeStampA[0] << 24 | self.MagTimeStampA[1] << 16 | self.MagTimeStampA[2] << 8 | \
                          self.MagTimeStampA[3]
        self.MagTimeStampB = Frame_Data[18:22]
        self.MagTimeStampB = self.MagTimeStampB[0] << 24 | self.MagTimeStampB[1] << 16 | self.MagTimeStampB[2] << 8 | \
                          self.MagTimeStampB[3]
        # bottom timestamps
        self.AccelTimeStampC = Frame_Data[22:26]
        self.AccelTimeStampC = self.AccelTimeStampC[0] << 24 | self.AccelTimeStampC[1] << 16 | self.AccelTimeStampC[2] << 8 | \
                               self.AccelTimeStampC[3]
        self.AccelTimeStampD = Frame_Data[26:30]
        self.AccelTimeStampD = self.AccelTimeStampD[0] << 24 | self.AccelTimeStampD[1] << 16 | self.AccelTimeStampD[2] << 8 | \
                               self.AccelTimeStampD[3]
        self.MagTimeStampC = Frame_Data[30:34]
        self.MagTimeStampC = self.MagTimeStampC[0] << 24 | self.MagTimeStampC[1] << 16 | self.MagTimeStampC[2] << 8 | \
                             self.MagTimeStampC[3]
        self.MagTimeStampD = Frame_Data[34:38]
        self.MagTimeStampD = self.MagTimeStampD[0] << 24 | self.MagTimeStampD[1] << 16 | self.MagTimeStampD[2] << 8 | \
                             self.MagTimeStampD[3]

        # IMU data
        self.AccAX = Frame_Data[self.FrameLength - 146 : self.FrameLength - 142]
        self.AccAY = Frame_Data[self.FrameLength - 142 : self.FrameLength - 138]
        self.AccAZ = Frame_Data[self.FrameLength - 138 : self.FrameLength - 134]
        self.GyroAX = Frame_Data[self.FrameLength - 134 : self.FrameLength - 130]
        self.GyroAY = Frame_Data[self.FrameLength - 130 : self.FrameLength - 126]
        self.GyroAZ = Frame_Data[self.FrameLength - 126 : self.FrameLength - 122]
        self.MagAX = Frame_Data[self.FrameLength - 122 : self.FrameLength - 118]
        self.MagAY = Frame_Data[self.FrameLength - 118 : self.FrameLength - 114]
        self.MagAZ = Frame_Data[self.FrameLength - 114 : self.FrameLength - 110]

        self.AccBX = Frame_Data[self.FrameLength - 110 : self.FrameLength - 106]
        self.AccBY = Frame_Data[self.FrameLength - 106 : self.FrameLength - 102]
        self.AccBZ = Frame_Data[self.FrameLength - 102 : self.FrameLength - 98]
        self.GyroBX = Frame_Data[self.FrameLength - 98 : self.FrameLength - 94]
        self.GyroBY = Frame_Data[self.FrameLength - 94 : self.FrameLength - 90]
        self.GyroBZ = Frame_Data[self.FrameLength - 90 : self.FrameLength - 86]
        self.MagBX = Frame_Data[self.FrameLength - 86 : self.FrameLength - 82]
        self.MagBY = Frame_Data[self.FrameLength - 82 : self.FrameLength - 78]
        self.MagBZ = Frame_Data[self.FrameLength - 78 : self.FrameLength - 74]

        self.AccCX = Frame_Data[self.FrameLength - 74 : self.FrameLength - 70]
        self.AccCY = Frame_Data[self.FrameLength - 70 : self.FrameLength - 66]
        self.AccCZ = Frame_Data[self.FrameLength - 66 : self.FrameLength - 62]
        self.GyroCX = Frame_Data[self.FrameLength - 62 : self.FrameLength - 58]
        self.GyroCY = Frame_Data[self.FrameLength - 58 : self.FrameLength - 54]
        self.GyroCZ = Frame_Data[self.FrameLength - 54 : self.FrameLength - 50]
        self.MagCX = Frame_Data[self.FrameLength - 50 : self.FrameLength - 46]
        self.MagCY = Frame_Data[self.FrameLength - 46 : self.FrameLength - 42]
        self.MagCZ = Frame_Data[self.FrameLength - 42 : self.FrameLength - 38]

        self.AccDX = Frame_Data[self.FrameLength - 38 : self.FrameLength - 34]
        self.AccDY = Frame_Data[self.FrameLength - 34 : self.FrameLength - 30]
        self.AccDZ = Frame_Data[self.FrameLength - 30 : self.FrameLength - 26]
        self.GyroDX = Frame_Data[self.FrameLength - 26 : self.FrameLength - 22]
        self.GyroDY = Frame_Data[self.FrameLength - 22 : self.FrameLength - 18]
        self.GyroDZ = Frame_Data[self.FrameLength - 18 : self.FrameLength - 14]
        self.MagDX = Frame_Data[self.FrameLength - 14 : self.FrameLength - 10]
        self.MagDY = Frame_Data[self.FrameLength - 10 : self.FrameLength - 6]
        self.MagDZ = Frame_Data[self.FrameLength - 6 : self.FrameLength - 2]


        self.AccAX = struct.unpack('>f', bytearray(self.AccAX))[0]
        self.AccAY = struct.unpack('>f', bytearray(self.AccAY))[0]
        self.AccAZ = struct.unpack('>f', bytearray(self.AccAZ))[0]
        self.GyroAX = struct.unpack('>f', bytearray(self.GyroAX))[0]
        self.GyroAY = struct.unpack('>f', bytearray(self.GyroAY))[0]
        self.GyroAZ = struct.unpack('>f', bytearray(self.GyroAZ))[0]
        self.MagAX = struct.unpack('>f', bytearray(self.MagAX))[0]
        self.MagAY = struct.unpack('>f', bytearray(self.MagAY))[0]
        self.MagAZ = struct.unpack('>f', bytearray(self.MagAZ))[0]

        self.AccBX = struct.unpack('>f', bytearray(self.AccBX))[0]
        self.AccBY = struct.unpack('>f', bytearray(self.AccBY))[0]
        self.AccBZ = struct.unpack('>f', bytearray(self.AccBZ))[0]
        self.GyroBX = struct.unpack('>f', bytearray(self.GyroBX))[0]
        self.GyroBY = struct.unpack('>f', bytearray(self.GyroBY))[0]
        self.GyroBZ = struct.unpack('>f', bytearray(self.GyroBZ))[0]
        self.MagBX = struct.unpack('>f', bytearray(self.MagBX))[0]
        self.MagBY = struct.unpack('>f', bytearray(self.MagBY))[0]
        self.MagBZ = struct.unpack('>f', bytearray(self.MagBZ))[0]

        self.AccCX = struct.unpack('>f', bytearray(self.AccCX))[0]
        self.AccCY = struct.unpack('>f', bytearray(self.AccCY))[0]
        self.AccCZ = struct.unpack('>f', bytearray(self.AccCZ))[0]
        self.GyroCX = struct.unpack('>f', bytearray(self.GyroCX))[0]
        self.GyroCY = struct.unpack('>f', bytearray(self.GyroCY))[0]
        self.GyroCZ = struct.unpack('>f', bytearray(self.GyroCZ))[0]
        self.MagCX = struct.unpack('>f', bytearray(self.MagCX))[0]
        self.MagCY = struct.unpack('>f', bytearray(self.MagCY))[0]
        self.MagCZ = struct.unpack('>f', bytearray(self.MagCZ))[0]

        self.AccDX = struct.unpack('>f', bytearray(self.AccDX))[0]
        self.AccDY = struct.unpack('>f', bytearray(self.AccDY))[0]
        self.AccDZ = struct.unpack('>f', bytearray(self.AccDZ))[0]
        self.GyroDX = struct.unpack('>f', bytearray(self.GyroDX))[0]
        self.GyroDY = struct.unpack('>f', bytearray(self.GyroDY))[0]
        self.GyroDZ = struct.unpack('>f', bytearray(self.GyroDZ))[0]
        self.MagDX = struct.unpack('>f', bytearray(self.MagDX))[0]
        self.MagDY = struct.unpack('>f', bytearray(self.MagDY))[0]
        self.MagDZ = struct.unpack('>f', bytearray(self.MagDZ))[0]


        # self.IMU_Stamp = [self.FrameNumber, self.TimeStamp]
        self.IMU_Stamp = [self.FrameNumber, self.AccelTimeStampA, self.AccelTimeStampB, self.MagTimeStampA,
                          self.MagTimeStampB, self.AccelTimeStampC, self.AccelTimeStampD, self.MagTimeStampC,
                          self.MagTimeStampD]

        self.IMU_Data_A = [self.AccAX, self.AccAY, self.AccAZ, self.GyroAX, self.GyroAY, self.GyroAZ,
                         self.MagAX, self.MagAY, self.MagAZ]


        self.IMU_Data_B = [self.AccBX, self.AccBY, self.AccBZ,
                            self.GyroBX, self.GyroBY, self.GyroBZ,
                              self.MagBX, self.MagBY, self.MagBZ]


        self.IMU_Data_C = [self.AccCX, self.AccCY, self.AccCZ,
                              self.GyroCX, self.GyroCY, self.GyroCZ,
                              self.MagCX, self.MagCY, self.MagCZ]

        self.IMU_Data_D = [self.AccDX, self.AccDY, self.AccDZ,
                           self.GyroDX, self.GyroDY, self.GyroDZ,
                           self.MagDX, self.MagDY, self.MagDZ]

        self.IMU_Data = self.IMU_Stamp + self.IMU_Data_A + self.IMU_Data_B + self.IMU_Data_C + self.IMU_Data_D

        self.IMU_Data_Slot.emit(self.IMU_Data)
        self.UDP_Data_Slot.emit(self.IMU_Data)
