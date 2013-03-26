#!/usr/bin/env python
# Author: Adam Portier

import sys
from Tkinter import *

try:
    import netaddr
except ImportError:
    sys.exit("""Requres netaddr python module.
    Try easy_install netaddr or https://github.com/drkjam/netaddr""")

class SubnetCalculator(Frame):
    ''' Class to set up a Tkinter Subnet Calculator '''

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.grid()
        self.create_widgets()

    def create_widgets(self):
        ''' Sets up GUI widgets '''
        global broadcastValue, netmaskValue, hostmaskValue, sizeValue
        global statusValue, networkEntry, ipaddrText, gatewayValue

        #creating string widget variables
        self.broadcastValue = StringVar()
        self.netmaskValue = StringVar()
        self.hostmaskValue = StringVar()
        self.sizeValue = StringVar()
        self.gatewayValue = StringVar()
        self.statusValue = StringVar()

        #set up default text for widgets
        self.sizeValue.set("0 Usable Addresses")

        #setting up interactive widgets
        self.broadcastLabel = Label(self, text="Broadcast")
        self.broadcastValueText = Entry(self, state='readonly', width=15)
        self.broadcastValueText.config(textvariable=self.broadcastValue)
        self.netmaskLabel = Label(self, text="Netmask")
        self.netmaskValueText = Entry(self, state='readonly', width=15)
        self.netmaskValueText.config(textvariable=self.netmaskValue)
        self.hostmaskLabel = Label(self, text="Hostmask")
        self.hostmaskValueText = Entry(self, state='readonly', width=15)
        self.hostmaskValueText.config(textvariable=self.hostmaskValue)
        self.sizeLabel = Label(self, textvariable=self.sizeValue) 
        self.gatewayLabel = Label(self, text="Gateway")
        self.gatewayValueText = Entry(self, state='readonly', width=15)
        self.gatewayValueText.config(textvariable=self.gatewayValue)
        self.ipaddrScrollbar = Scrollbar(self)
        self.ipaddrText = Text(self, width=30, height=10,
            yscrollcommand=self.ipaddrScrollbar.set)
        self.ipaddrScrollbar.config(command=self.ipaddrText.yview)
        self.statusValueLabel = Label(self, textvariable=self.statusValue,
                relief=SUNKEN)
        self.networkEntry = Entry(self, width=15)
        self.calculateButton = Button(self, text="Calculate",
                width=15, command=self.calculate_subnet)

        #adding widgets to grid
        self.networkEntry.grid(row=0, column=0)
        self.calculateButton.grid(row=0, column=1)
        self.gatewayLabel.grid(row=1, column=0)
        self.gatewayValueText.grid(row=1, column=1)
        self.netmaskLabel.grid(row=2, column=0)
        self.netmaskValueText.grid(row=2, column=1)
        self.hostmaskLabel.grid(row=3, column=0)
        self.hostmaskValueText.grid(row=3, column=1)
        self.broadcastLabel.grid(row=4, column=0)
        self.broadcastValueText.grid(row=4, column=1)
        self.sizeLabel.grid(row=5, column=0, columnspan=2, sticky=W+E)
        self.ipaddrText.grid(row=6, column=0, columnspan=2, sticky=W+E)
        self.ipaddrScrollbar.grid(row=6, column=2, sticky=N+S)
        self.statusValueLabel.grid(row=7, column=0, columnspan=3, sticky=W+E)

    def calculate_subnet(self):
        ''' Takes in a CIDR notation subnet and calculates values '''

        try:
            ipnet = netaddr.IPNetwork(self.networkEntry.get())
            if ipnet.version == 4:
                self.broadcastValue.set(ipnet.broadcast)
                self.netmaskValue.set(ipnet.netmask)
                self.hostmaskValue.set(ipnet.hostmask)
                if ipnet.size > 4:
                    self.sizeValue.set(
                    "{} Usable Addresses".format(ipnet.size-3))
                else:
                    self.sizeValue.set("1 Usable Address")
                self.ipaddrText.delete(1.0, END)
                ipnetValues = [str(ipaddr) for ipaddr in list(ipnet)]
                if len(ipnetValues) > 2:
                    #discard first address(same as network)
                    ipnetValues.pop(0)
                    #discard last address(same as broadcast)
                    ipnetValues.pop()
                #set the gateway to the first value of the remaining list
                self.gatewayValue.set(ipnetValues.pop(0))
                #if there is nothing left in the list, re-add the last value
                if len(ipnetValues) == 0:
                    ipnetValues.append(self.gatewayValue.get())
                #add the remaining values to the list of usable addresses
                self.ipaddrText.insert(END, '\n'.join(ipnetValues))
                self.statusValue.set("Calculated")
            else:
                self.statusValue.set("IPv6 Networks Not Supported")
        except netaddr.AddrFormatError:
            self.statusValue.set("Invalid Network")

        
calc = SubnetCalculator()
calc.master.title("CIDR Subnet Calculator")
calc.master.resizable(0,0)
calc.mainloop()
