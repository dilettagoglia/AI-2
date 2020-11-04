# -*- coding: utf-8 -*-
"""
Created on Wed Nov  4 16:18:28 2020

@author: Diletta
"""

import getpass, sys, telnetlib
#HOST = "margot.di.unipi.it, 8421"
tn = telnetlib.Telnet('margot.di.unipi.it', '8421')

tn.write("NEW test28".encode('utf-8')) # pass bytes, not string
#print(tn.read_all().decode('ascii')) # la read_all blocca tutto 
tn.read_some()
#tn.read_until(b"OK", timeout=10) # using b in order to pass bytes avoiding 'encode'
# test JOIN charlie H - first player
