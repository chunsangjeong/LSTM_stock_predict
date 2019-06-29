from pywinauto import application
from pywinauto import timings
import win32com.client
import json
import time
import os
import ctypes

g_objCodeMgr = win32com.client.Dispatch('CpUtil.CpCodeMgr')
g_objCpStatus = win32com.client.Dispatch('CpUtil.CpCybos')
g_objCpTrade = win32com.client.Dispatch('CpTrade.CpTdUtil')
g_objCpStockCode = win32com.client.Dispatch('CpUtil.CpStockCode')
g_objMarketEye = win32com.client.Dispatch("CpSysDib.MarketEye")

class Dasin():

    def __init__(self):

        self._init_pulse_check(True)

    def _init_pulse_check(self, practical=False):
        # run as admin
        if ctypes.windll.shell32.IsUserAnAdmin():
            print('Started as Admin')
        else:
            print('Should run as Admin')
            return False

        self.IsConnected = g_objCpStatus.Isconnect
        if self.IsConnected:
            print("Connected to Server")
        else:
            print("Connection failed")

            if practical:
                for i in range(1,4):
                    self._autoLogIn()
                    print("Trying to connect {} times".format(i))
                    time.sleep(10)

                    self.IsConnected = g_objCpStatus.Isconnect
                    if self.IsConnected:
                        print("Connected to Server")
                        break

            print("Failed to run")
            exit()

    def _open_configs(self, filename='config.json'):
        with open(filename) as json_file:
            configs = json.load(json_file)
            userId = configs["user"]["dasin"]["userId"]
            passWord = configs["user"]["dasin"]["passWord"]
            passCert = configs["user"]["dasin"]["passCert"]
            return userId, passWord, passCert
        # addd exception code here

    def _autoLogIn(self):
        print("Starting autologin")
        userId, passWord, passCert = self._open_configs()
        app = application.Application()
        command_string = 'C:\DAISHIN\STARTER//ncStarter.exe /prj:cp' + ' /id:' + userId + ' /pwd:' + passWord + ' /pwdcert:' + passCert + ' /autostart'
        print(command_string)
        app.start(command_string)

    def getStockName(self, number):
        stockCode = g_objCpStockCode.GetData(0, number)
        stockName = g_objCpStockCode.GetData(1, number)

        print("StockCode {} - {}".format(stockCode, stockName))
        return stockCode, stockName
    
    def getPER(self):
        tarketCodeList = g_objCodeMgr.GetGroupCodeList(5)

        for code in tarketCodeList:
            print(code, g_objCodeMgr.CodeToName(code))

        # Get PER
        g_objMarketEye.SetInputValue(0, 67)
        g_objMarketEye.SetInputValue(1, tarketCodeList)

        # BlockRequest
        g_objMarketEye.BlockRequest()

        # GetHeaderValue
        numStock = g_objMarketEye.GetHeaderValue(2)

        # GetData
        sumPer = 0
        for i in range(numStock):
            iPer = g_objMarketEye.GetDataValue(0, i)
            print("{}: {}".format(i,iPer))
            sumPer +=iPer

        print("Average PER: ", sumPer / numStock)


if __name__ == "__main__":
    inst = Dasin()
    inst.getStockName(11)
    inst.getPER()