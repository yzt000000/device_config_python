# -*- coding: utf-8 -*-
import os
import time
import pyvisa
import csv

class DMM34461(object):
    Measurement_List = [""]

    def __init__(self):
        #self.rm = pyvisa.ResourceManager()
        self.Terminals = "FRON"
        self.ReadBuff = []
        self.idn_list = []

    def _find_dmm_resource(self):
        
        try:
            self.rm = pyvisa.ResourceManager()
        except:
            self.rm = pyvisa.ResourceManager('@sim')
        resources = self.rm.list_resources()
        for resource in resources:
            try:
                inst = self.rm.open_resource(resource)
                idn = inst.query("*IDN?").strip()
                inst.close()
                if "34461A" in idn:  # Adjust this condition based on your DMM model
                    return resource
            except:
                continue
        raise ValueError("DMM device not found")

    def _open_device(self, resourceName=""):
        self.resource_str = self._find_dmm_resource()
        print(f"DMM resource: {self.resource_str}")
        if resourceName:
            self.resource_str = resourceName
        self.my_instrument = self.rm.open_resource(self.resource_str)
        self.my_instrument.read_termination = '\n'
        self.my_instrument.write_termination = '\n'
        self._show_instrument_message()

    def _show_instrument_message(self):
        self.idn_list = self.my_instrument.query("*IDN?").split(",")
        print("Manufacturing: {0}".format(self.idn_list[0]))
        print("Model: {0}".format(self.idn_list[1]))
        print("SN: {0}".format(self.idn_list[2]))
        print("Version: {0}".format(self.idn_list[3]))

    def _reset_dmm(self):
        self.my_instrument.write("*RST")  # 恢复出厂设置
        self.my_instrument.write("*CLS")
        ret = self.my_instrument.query("*TST?")
        if ret != "+0":
            print("self-test:{0}".format(ret))
        else:
            print("self-test:PASS")

        self._dmm_display_view('NUMeric')

    def _read_config(self):
        ret = self.my_instrument.query("CONFigure?")
        return ret

    def _set_config(self, Measurementype, Range="DEF", Resolution="DEF"):
        if Measurementype == "CAP":
            cmd = "CONF:CAP 100".format(Range, Resolution)
            self.my_instrument.write(cmd)
            ret = self.my_instrument.query("READ?")
            return ret

    def _config_current_parameter(self, Measurementype, Range="DEF", Resolution="DEF"):
        CMD = "CONFigure:CURRent:{0} {1},{2}".format(Measurementype, Range, Resolution)
        print("Config", CMD)
        self.my_instrument.write(CMD)

    def _measuremen_diode(self):
        CMD = "CONF:DIOD"
        self.my_instrument.write(CMD)

    def _measuremen_frequency_or_period(self, Measurementype, Range="DEF", Resolution="DEF"):
        Measurementypes = ["FREQuency", "PERiod", "FREQ", "PER"]
        if Measurementype in Measurementypes:
            if Measurementype == "FREQuency" or Measurementype == "FREQ":
                CMD = "CONFigure:FREQuency {0},{1}".format(Range, Resolution)
                self.my_instrument.write(CMD)
            elif Measurementype == "PERiod" or Measurementype == "PER":
                CMD = "CONFigure:PERiod {0},{1}".format(Range, Resolution)
                self.my_instrument.write(CMD)
        else:
            print("Measurementype not support")

    def _measuremen_resistance_or_fresistance(self, Measurementype, Range="DEF", Resolution="DEF"):
        Range = str.upper(Range)
        RangeNumber_Dic = {
            "100M": 100000000,
            "10M": 10000000,
            "1M": 1000000,
            "100K": 100000,
            "10K": 10000,
            "1K": 1000,
            "100": 0.1
        }
        Measurementypes = ["RESistance", "FRESistance", "RES", "FRES"]
        if Range in RangeNumber_Dic:
            Range = RangeNumber_Dic[Range]
        if Measurementype in Measurementypes:
            if Measurementype == "RESistance" or Measurementype == "RES":
                CMD = "CONFigure:RESistance {0},{1}".format(Range, Resolution)
                self.my_instrument.write(CMD)
            elif Measurementype == "FRESistance" or Measurementype == "FRES":
                CMD = "CONFigure:FRESistance {0},{1}".format(Range, Resolution)
                self.my_instrument.write(CMD)
        else:
            print("Measurementype not support")

    def _config_voltage_parameter(self, Measurementype, Range="DEF", Resolution="DEF"):
        CMD = "CONFigure:VOLTage:{0} {1},{2}".format(Measurementype, Range, Resolution)
        print("send cmd", CMD)
        self.my_instrument.write(CMD)

    def _check_terminals(self, Terminals):
        TerminalsTypes = ["FRON", "REAR"]
        Terminals = str.upper(Terminals)
        if Terminals in TerminalsTypes:
            ret = self.my_instrument.query("ROUTe:TERMinals?")
            if self.Terminals == ret:
                return True
            return False
        return False

    def _sample(self):
        self.my_instrument.write("SAMPle:COUNt 50")
        self.my_instrument.write("SAMPle:SOURce TIMer")

    def _read_buff(self):
        ret = self.my_instrument.query("READ?", 1000)
        print("result {0}".format(ret))

    def _finish(self):
        del self.ReadBuff[:]

    def _save_buff_to_csv(self, logpath):
        filename = logpath
        with open(filename, "w+") as csvfile:
            fieldnames = ['Manufacturing Information', 'Device Model', "Device SN", "Version"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            Device_Information = {
                'Manufacturing Information': self.idn_list[0],
                'Device Model': self.idn_list[1],
                'Device SN': self.idn_list[2],
                'Version': self.idn_list[3],
            }
            writer.writerow(Device_Information)
        with open(filename, "a+") as csvfile:
            fieldnames = ["ReadBuff"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for buff in self.ReadBuff:
                print(buff)
                writer.writerow({"ReadBuff": buff})

    def _dmm_display(self, displayStr):
        CMD = "DISPlay {0}".format("ON")
        self.my_instrument.write(CMD)
        CMD = "DISPlay:TEXT:DATA \"{0}\"".format(displayStr)
        self.my_instrument.write(CMD)

    def _dmm_display_clear(self):
        CMD = "DISPlay:TEXT:CLEar"
        self.my_instrument.write(CMD)

    def _dmm_display_view(self, ViewType):
        ViewTypes = ["NUMeric", "HISTogram", "TCHart", "METer"]
        if ViewType in ViewTypes:
            CMD = "DISPlay:VIEW {0}".format(ViewType)
            self.my_instrument.write(CMD)

    def _set_limit(self, Limit_Low, Limit_Upp):
        self._limit_clear()
        CMD = "CALCulate:LIM:LOW {0}".format(Limit_Low)
        self.my_instrument.write(CMD)
        CMD = "CALCulate:LIM:UPP {0}".format(Limit_Upp)
        self.my_instrument.write(CMD)

    def _limit_clear(self):
        CMD = "CALCulate:LIMit:CLEa"
        self.my_instrument.write(CMD)

    def _set_limit_on_off(self, SetLimitONOFF="OFF"):
        LinitStates = ["ON", "OFF", "0", "1"]
        if SetLimitONOFF in LinitStates:
            CMD = "CALCulate:LIM:STATe {0}".format(SetLimitONOFF)
            self.my_instrument.write(CMD)

    def _read_questionable(self):
        result = self.my_instrument.query("STATus:QUEStionable:CONDition?")
        return result

    def _set_trigger_source(self, Source):
        SourceTypes = ["IMMediate", "BUS", "EXTernal", "INTernal"]
        if Source in SourceTypes:
            self.my_instrument.write("TRIG:SOUR {0}".format(Source))
            self.my_instrument.write("TRIG:TRIG:DEL 2")

    def _set_sample_count(self, Count):
        Cmd = "SAMPle:COUNt {0}".format(Count)
        self.my_instrument.write(Cmd)

    def _voltage_measuremen(self, VoltageType, Count=50, Range="DEF", Resolution="DEF", LimitLow=0, LimitUpp=0):
        print("VoltageMeasuremen parameter error")
        Range = str.upper(Range)
        VoltageType = str.upper(VoltageType)
        RangeNumber_Dic = {"1000V": 1000, "100V": 100, "10V": 10, "1V": 1, "100MV": 0.1}
        Measurementypes = ["AC", "DC"]
        if (VoltageType in Measurementypes) and (Range in RangeNumber_Dic):
            self._config_voltage_parameter(VoltageType, Range, Resolution)
            self._set_trigger_source("BUS")
            self._set_sample_count(Count)
            self._limit_clear()
            if LimitLow != 0 and LimitUpp != 0:
                self._set_limit(LimitLow, LimitUpp)
                self._set_limit_on_off("ON")
            self.my_instrument.write("INIT")
            self.my_instrument.write("*TRG")
            self.ReadBuff = self.my_instrument.query("FETC?").split(",")
            self._save_buff_to_csv("Voltage.csv")
        else:
            print("VoltageMeasuremen parameter error")

    def _current_measuremen(self, CurrentType, Count=50, Range="DEF", Resolution="DEF"):
        print("CurrentMeasuremen", Range, Resolution)
        CurrentTypes = ["AC", "DC"]
        RangeNumber_Dic = {"3A": 3, "10A": 10}
        if (CurrentType in CurrentTypes) and (Range in RangeNumber_Dic):
            self._config_current_parameter(CurrentType, Range, Resolution)
            self._set_trigger_source("BUS")
            self._set_sample_count(Count)
            self._limit_clear()
            self._set_limit_on_off("OFF")
            self.my_instrument.write("INIT")
            self.my_instrument.write("*TRG")
            self.ReadBuff = self.my_instrument.query("FETC?", 5).split(",")
            self._save_buff_to_csv("Current.csv")
        else:
            print("CurrentMeasuremen parameter error")

    def connect_and_measure(self, resourceName=""):
        self._open_device(resourceName)
        self._reset_dmm()
        self._finish()
        if self._check_terminals("FRON"):
            self._current_measuremen("DC", Count=5, Range="10A", Resolution=0.00001)
            self._voltage_measuremen("DC", 200, "10V", 0.001, 4.5, 5.5)
            self._read_questionable()
            print("测量完成")
        else:
            print("请切换段子")

# if __name__ == '__main__':
#     dmm = DMM34461()
#     dmm.connect_and_measure()