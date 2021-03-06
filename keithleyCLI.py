#!/usr/bin/env python

""" Keithley_CLI.py: Command line interface
"""


#######################################
# Imports
#######################################

import sys
import cmd
import time
import datetime
from threading import Thread

#######################################
# Class CLI
#######################################

class CLI(cmd.Cmd,Thread):
    """Command Line Interface"""


    def __init__(self):
        cmd.Cmd.__init__(self)
        Thread.__init__(self)
        self.running = True
        #super(CLI,self).__init__()
        self.keithleys={}

        # Init logging file
        value = datetime.datetime.fromtimestamp(time.time())
        logfile_name = "keithleyLog_" + value.strftime('%Y_%m_%d_%H_%M') + ".txt"
        self.logfile = open(logfile_name, "w", 1)

    def run(self):
        self.cmdloop()

    def set_keithleys(self,keithleys):
        """ set a map of  keithley devices"""
        self.keithleys= keithleys
        print 'set keithleys'
        for name in keithleys:
            print name,keithleys[name].name

    def do_exit(self,line):
        """Quit CLI"""

        # Turn off the devices
        for k in self.keithleys.keys():
            self.keithleys[k].isKilled=True

        self.logfile.close()
        self.running = False

        return True

    def do_names(self,line):
        """Print connected Keithley devices"""

        print 'There are %d Keithleys connected:'%len(self.keithleys)
        k = 1
        for i in self.keithleys:
            print k, i
            k+=1

    #######################################
    # do_ON / do_OFF
    #######################################

    def setOutput(self,name,status):
        print 'Set Output %d: %s'%(status,name)
        if name.upper() == 'ALL':
            for k in self.keithleys:
                self.setOutput(k,status)
            return
        if self.keithleys.has_key(name):
            keithley = self.keithleys[name]
            keithley.wait_for_device()
            keithley.isBusy=True
            try:
                keithley.setOutput(status)
                keithley.lastUChange = time.time()
                keithley.powering_down = False
            except Exception as inst:
                print type(inst),inst
            keithley.isBusy=False
        else:
            print 'cannot find %s'%name

    def do_ON(self,line):
        """ Set output of device to ON.
        Usage: ON KeithleyName
        (ON ALL to turn on all devices)
        """
        self.setOutput(line,True)


    def do_OFF_FAST(self,line):
        """ Set output of device to OFF.
        Usage: OFF_FAST KeithleyName
        (OFF_FAST ALL to turn on all devices)
        """
        self.setOutput(line,False)


    def do_OFF(self,line):
        """ Set output of device to OFF.
        Usage: OFF KeithleyName
        (OFF ALL to turn off all devices)
        """

        try:
            name = line.split()[0]
            if name.upper() == 'ALL':
                for k in self.keithleys:
                    self.do_OFF(k)
            else:
                self.keithleys[name].power_down()

        except Exception as inst:
            print type(inst),inst


    #######################################
    # do_FILTER
    #######################################
    def setFilter(self,name,status):
        print 'Set Filter %d: %s'%(status,name)
        if name.upper() == 'ALL':
            for k in self.keithleys:
                self.setFilter(k,status)
            return
        if self.keithleys.has_key(name):
            keithley = self.keithleys[name]
            keithley.wait_for_device()
            keithley.isBusy=True
            try:
                keithley.setAverageFiltering(status)
            except Exception as inst:
                print type(inst),inst
            keithley.isBusy=False
        else:
            print 'cannot find %s'%name

    def do_FILTER(self,line):
        """ Set filter of device.
        FILTER KeithleyName status
        status should be 0/1
        ('FILTER ALL 0/1' sets all devices)"""
        try:
            name = line.split()[0]
            status = int(line.split()[1])
            print 'do_FILTER',line,name,status
            self.setFilter(name,status)
        except Exception as inst:
            print type(inst),inst


    #######################################
    # do_MANUAL
    #######################################

    def set_manual(self,name,status):
        """ (De-)Activates manual control mode.
        MANUAL KeithleyName status
        status should be 0/1
        ('MANUAL ALL 0/1' sets all devices)"""
        try:
            keithley = self.keithleys[name]
        except Exception as inst:
            print 'cannot find keithley with name "%s"'%name
        try:
            keithley.set_manual(status)
        except Exception as inst:
            print type(inst),inst

    def do_MANUAL(self,line):
        try:
            [name,status] = line.split()
            status = int(status)
        except:
            print 'Wrong input for MANUAL',line
            return
        if name.upper() == 'ALL':
            for k in self.keithleys:
                self.set_manual(k,status)
        else:
            try:
                keithley = self.keithleys[name]
                keithley.set_manual(status)
            except:
                print 'cannot find keithley with name "%s"'%name

    #######################################
    # do_BIAS
    #######################################

    def setBias(self, name, target_bias ):

        try:
            if self.keithleys.has_key(name):
                keithley = self.keithleys[name]

                if (   (target_bias < keithley.minBias)
                    or (target_bias > keithley.maxBias)):
                    print "This bias voltage", target_bias, "is not allowed! Boundaries are: ", keithley.minBias, keithley.maxBias
                    return

                keithley.set_target_bias(target_bias)

        except Exception as inst:
            print type(inst),inst


    def do_BIAS(self,line):
        """ Set target voltage of device.
        Usage:
        BIAS KeithleyName voltage"""

        try:
            name        = line.split()[0]
            target_bias = float(line.split()[1])
            self.setBias( name, target_bias )

        except Exception as inst:
            print type(inst),inst

    #######################################
    # do_COMMAND
    #######################################
    def do_COMMAND(self,line):
        """performs any command on device"""
        try:
            command = line.split(None,1)
            name = command [0]
            if self.keithleys.has_key(name):
                keithley = self.keithleys[name]
                keithley.wait_for_device()
                keithley.isBusy = True
                try:
                    print 'Write to "%s" "%s"'%(name,command[1])
                    keithley.write(command[1])
                except:
                    pass
                keithley.isBusy = False
            else:
                print 'cannot find %s'%name
        except Exception as inst:
            print type(inst),inst

    def do_read(self,line):
        """Call read for device"""
        try:
            name = line
            keithley = self.keithleys[name]
            keithley.wait_for_device()
            keithley.isBusy = True
            try:
                print keithley.read()
            except:
                pass
            keithley.isBusy = False
        except Exception as inst:
            print type(inst),inst
            print Exception


    #######################################
    # do_NEWLOG
    #######################################

    def do_NEWLOG(self,line):
        """ Closes the current logfile and opens a new one"""

        # Close old and open new logging file
        value = datetime.datetime.fromtimestamp(time.time())
        logfile_name = "keithleyLog_" + value.strftime('%Y_%m_%d_%H_%M') + ".txt"
        self.logfile.close()
        self.logfile = open(logfile_name, "w",1)




# End of Class CLI
