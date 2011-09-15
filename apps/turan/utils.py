#!/usr/bin/python

import numpy
import urllib, urllib2, simplejson

def calculate_xPower(attrlist):
    attrlist = exponential_moving_average(attrlist, 25)
    fourth = sum([pow(x, 4) for x in attrlist])
    if fourth:
        xpower = int(round(pow(fourth/len(attrlist), (0.25))))
        return xpower

def exponential_moving_average(s, n):
    """
    returns an n period exponential moving average for
    the time series s

    s is a list ordered from oldest (index 0) to most
    recent (index -1)
    n is an integer

    returns a numeric array of the exponential
    moving average
    """
    s= [s[0]]*((n)) + s
    s = numpy.array(s)
    ema = []
    j = 1

    #get n sma first and calculate the next n period ema
    sma = sum(s[:n]) / n
    multiplier = 2 / float(1 + n)
    ema.append(sma)

    #EMA(current) = ( (Price(current) - EMA(prev) ) x Multiplier) + EMA(prev)
    ema.append(( (s[n] - sma) * multiplier) + sma)

    #now calculate the rest of the values
    for i in s[n+1:]:
       tmp = ( (i - ema[j]) * multiplier) + ema[j]
       j = j + 1
       ema.append(tmp)

    return ema


def fetch_geonames_astergdem(lonlats):
    ''' Given a list of (lon, lat) tuples, fetch the altitudes from aster gdem geonames service '''

    apiurl = 'http://api.geonames.org/astergdem'
    lats = ''
    lngs = ''
    for pos in lonlats:
        lngs += '%s,' %pos[0]
        lats += '%s,' %pos[1]
    attrs = urllib.urlencode({
        'username': 'turan',
        'lats': lats,
        'lngs': lngs,
    })
    url = '%s?%s' %(apiurl, attrs)
    result = urllib2.urlopen(url).read()
    result = result.split()
    return result

