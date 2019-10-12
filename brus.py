#!/usr/bin/python

'''
    Copyright 2019, Jeff Sharkey

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os
import sys
import re
import urllib2
import collections

def fetch(url):
    clean = re.sub(r"[^a-zA-Z0-9]", "_", url)
    if not os.path.exists(clean):
        with open(clean, "w") as f:
            response = urllib2.urlopen(url)
            f.write(response.read())
    with open(clean) as f:
        return f.read()

# Destinations from Brussels with both low airfares ($33)
# and fast transit (under 2 hours)
DEST = [
    "FCO", # Italy
    "FLR", # Italy
    "MXP", # Italy
    "TRN", # Italy
    "VCE", # Italy
    "BLQ", # Italy

    "BOD", # France
    "LYS", # France
    "MRS", # France
    "NCE", # France
    "TLS", # France

    "BSL", # Switzerland
    "GVA", # Switzerland

    "HAJ", # Germany
    "HAM", # Germany
    "TXL", # Germany

    "BCN", # Spain
    "BIO", # Spain
    
    "BUD", # Hungary
    
    "PRG", # Czech Republic
    
    "KRK", # Poland
    "WAW", # Poland
    "WMI", # Poland

    # Assuming they leave ECAA
    #"BHX", # United Kingdom
    #"BRS", # United Kingdom
    #"LHR", # United Kingdom
    #"MAN", # United Kingdom
]

# Min/max connection times
MIN_DWELL = 30
MAX_DWELL = 180

FLIGHTS = collections.defaultdict(lambda: list())

class Flight():
    def __init__(self, dep, arr, fr, to, no):
        self.dep = dep
        self.arr = arr
        self.fr = fr
        self.to = to
        self.no = no
        
    def __repr__(self):
        return ("%s %s-%s %s-%s" % (self.no, self.fr, self.to, self.dep, self.arr))

for dest in DEST:
    # print "Fetching %s..." % (dest)
    raw = fetch("https://www.brusselsairlines.com/en-be/practical-information/timetable/timetable-results.aspx?FromAirportCode=BRU&ToAirportCode=%s&DepartureDate=04/03/2020&ReturnDate=04/03/2020" % (dest))
    for dep, arr, fr, to, no in re.findall(r'aria-label="Departure at ([0-9:]+) Arrival at ([0-9:]+) Local time" class="timetable_detail_popup" href="/en-be/destinations/destinationdetail.aspx.From=([A-Z]+)&To=([A-Z]+)&FlightNumber=([A-Z0-9/]+)&Time=04/03/2020', raw):
        FLIGHTS[fr].append(Flight(dep, arr, fr, to, no))

# Negative in past, positive in future
def compare(a, b):
    a = int(a[0:2]) * 60 + int(a[3:5])
    b = int(b[0:2]) * 60 + int(b[3:5])
    return b - a

def interesting(sofar, where, when, seg):
    delta = compare(when, seg.dep)
    if len(sofar) == 0:
        return delta < MAX_DWELL
    else:
        return delta > MIN_DWELL and delta < MAX_DWELL

# We're willing to explore the next 3 flights after this time
def explore(sofar, where, when):
    options = [ seg for seg in FLIGHTS[where] if interesting(sofar, where, when, seg) ]
    # Dump route when nothing left and we're back at origin
    if len(options) == 0 and where == "BRU" and len(sofar) > 4:
        print sofar
    for o in options:
        explore(sofar + [o], o.to, o.arr)


explore([], "BRU", "06:00")

