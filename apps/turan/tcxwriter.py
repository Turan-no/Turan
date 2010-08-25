#!/usr/bin/env python
# -*- coding: UTF-8
#

''' This file will need a list of objects.. FIXME elaborate
'''


class TCXWriter(object):

    xml = '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<TrainingCenterDatabase xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.garmin.com/xmlschemas/ActivityExtension/v2 http://www.garmin.com/xmlschemas/ActivityExtensionv2.xsd http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd">

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



    def __init__(self, objects, distance, avg_hr, max_hr, kcal, max_speed, duration, time, avg_cadence):

        time = time.strftime('%Y-%m-%dT%H:%M:%SZ')
        act_block = '''
  <Activities>
    <Activity Sport="Biking">
      <Id>%(time)s</Id>
      <Lap StartTime="%(time)s">
        <TotalTimeSeconds>%(duration)s</TotalTimeSeconds>
        <DistanceMeters>%(distance)s</DistanceMeters>
        <MaximumSpeed>%(max_speed)s</MaximumSpeed>
        <Calories>%(kcal)s</Calories>
        <AverageHeartRateBpm xsi:type="HeartRateInBeatsPerMinute_t">
          <Value>%(avg_hr)s</Value>
        </AverageHeartRateBpm>
        <MaximumHeartRateBpm xsi:type="HeartRateInBeatsPerMinute_t">
          <Value>%(max_hr)s</Value>
        </MaximumHeartRateBpm>
        <Intensity>Active</Intensity>
        <Cadence>%(avg_cadence)s</Cadence>
        <TriggerMethod>Manual</TriggerMethod>
      <Track>
      ''' %locals()
        self.xml += act_block

        def point2xmlblock(time, lon, lat, alt, distance, hr, cadence):
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
