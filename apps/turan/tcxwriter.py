#!/usr/bin/env python
# -*- coding: UTF-8
#

''' This file will need a list of objects.. FIXME elaborate
'''


class TCXWriter(object):

    xml = '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<TrainingCenterDatabase xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.garmin.com/xmlschemas/ActivityExtension/v2 http://www.garmin.com/xmlschemas/ActivityExtensionv2.xsd http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd">

  <Activities>
    <Activity Sport="Biking">
      <Id>2010-06-20T10:45:10Z</Id>
      <Lap StartTime="2010-06-20T10:45:10Z">
        <TotalTimeSeconds>292.7700000</TotalTimeSeconds>
        <DistanceMeters>1948.5429688</DistanceMeters>
        <MaximumSpeed>9.0850000</MaximumSpeed>
        <Calories>177</Calories>
        <AverageHeartRateBpm xsi:type="HeartRateInBeatsPerMinute_t">
          <Value>157</Value>
        </AverageHeartRateBpm>
        <MaximumHeartRateBpm xsi:type="HeartRateInBeatsPerMinute_t">
          <Value>207</Value>
        </MaximumHeartRateBpm>
        <Intensity>Active</Intensity>
        <Cadence>88</Cadence>
        <TriggerMethod>Manual</TriggerMethod>
      <Track>
'''
    xmlfooter = '''
      </Track>
      </Lap>
      <Creator xsi:type="Device_t">
        <Name>EDGE705</Name>
        <UnitId>3493151818</UnitId>
        <ProductID>625</ProductID>
        <Version>
          <VersionMajor>3</VersionMajor>
          <VersionMinor>10</VersionMinor>
          <BuildMajor>0</BuildMajor>
          <BuildMinor>0</BuildMinor>
        </Version>
      </Creator>
    </Activity>
  </Activities>

  <Author xsi:type="Application_t">
    <Name>Garmin Training Center(r)</Name>
    <Build>
      <Version>
        <VersionMajor>3</VersionMajor>
        <VersionMinor>5</VersionMinor>
        <BuildMajor>3</BuildMajor>
        <BuildMinor>0</BuildMinor>
      </Version>
      <Type>Release</Type>
      <Time>Feb  2 2010, 14:11:31</Time>
      <Builder>sqa</Builder>
    </Build>
    <LangID>EN</LangID>
    <PartNumber>006-A0119-00</PartNumber>
  </Author>

</TrainingCenterDatabase>
'''



    def __init__(self, objects):

        def point2xmlblock(time, lon, lat, alt, distance, hr, cadence):
            #xmlp = '<trkpt lat="%s" lon="%s">\n' %(lat, lon)
            #xmlp+= ' <ele>%.1f</ele>\n' %alt
            #xmlp+= ' <time>%s</time>\n' %time.strftime('%Y-%m-%dT%H:%M:%SZ')
            #xmlp+= '</trkpt>\n'
            posblock = ''
            if lat and lon:
                posblock = \
                '''
               <Position>
                 <LatitudeDegrees>%(lat)s</LatitudeDegrees>
                 <LongitudeDegrees>%(lon)s</LongitudeDegrees>
               </Position>''' %{'lat': lat, 'lon': lon}
            xmlp = '''
             <Trackpoint>
               <Time>%(time)s</Time>%(posblock)s
               <AltitudeMeters>%(alt)s</AltitudeMeters>
               <DistanceMeters>%(distance)s</DistanceMeters>
               <HeartRateBpm xsi:type="HeartRateInBeatsPerMinute_t">
                 <Value>%(hr)s</Value>
               </HeartRateBpm>
               <Cadence>%(cadence)s</Cadence>
             </Trackpoint>''' %{
                        'time': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                        'alt': alt,
                        'distance': distance,
                        'hr': hr,
                        'cadence': cadence,
                        'posblock': posblock,
              }


            if '':
                '''
               <Extensions>
                 <TPX xmlns="http://www.garmin.com/xmlschemas/ActivityExtension/v2">
                   <Watts>534</Watts>
                 </TPX>
               </Extensions>
             </Trackpoint>
'''
            return xmlp

        for o in objects:
            if not hasattr(o, 'distance'):
                o.distance = 0
            xmlblock = point2xmlblock(o.time, o.lon, o.lat, o.altitude, o.distance, o.hr, o.cadence)
            if xmlblock:
                self.xml += xmlblock
        self.xml += self.xmlfooter

#TODO
''' 
<Extensions>
<LX xmlns="http://www.garmin.com/xmlschemas/ActivityExtension/v2">
<AvgWatts>387</AvgWatts>
<MaxWatts>998</MaxWatts>
</LX>
</Extensions>
                  '''
