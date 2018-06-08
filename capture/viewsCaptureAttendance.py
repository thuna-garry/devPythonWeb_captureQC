"""
Copyright AdvanceQC LLC 2014,2015.  All rights reserved
"""
import json
import logging
import math

from aqclib         import utils
from aqclib.dbUtils import dbConnection, dbQuote, dbFetchOne, dbFetchAll, dbExecute

from viewsCapture import ViewCapture, ajaxProcess


#############################################################################
# ViewCaptureLabourBatch
#############################################################################
class ViewCaptureAttendance(ViewCapture):

    @ajaxProcess
    def ajax_form(self, request, frmName, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None, bbox=None):
        fs, form = self.processInitForm(request, frmName)
        menuEntry = [ x for x in self.MENU_ITEMS if x['name'] == 'timeClock' ][0]
        form = { 'name':  menuEntry['name']
               , 'label': menuEntry['label']
               , 'desc':  'Clock-in and out of work.'
               , 'flds':  []
               }
        self.appendUser(request, fs, form)
        return self.processFini(request, fs, form, msgType=msgType, msg=msg)

    def createField_clockEvents(self, listItems=[], value=None, msgType=ViewCapture.FLD_MSG_TYPE_NONE, msg=None):
        return self.listView('clockEvents', 'Clock Events', listItems, value=value, msgType=msgType, msg=msg)


    def gotUser(self, request, fs, form, flds, fld):
        if not fs['tah_auto_key']:
            fld['value'] = ""
            fld['msgType'] = self.FLD_MSG_TYPE_VALID
            fld['msg'] = "{} has no shift assigned".format(fs['employee_code'])
            return self.processFini(request, fs, form, msgType=self.FORM_MSG_TYPE_ERROR, msg="Account has no assigned shift")

        # get the clients time offset
        fs['clientTzOffset'] = request.META.get('HTTP_AQC_TZ_OFFSET')
        if (fs['clientTzOffset'] == None):
            fs['clientTzOffset'] = request.session['tzOffset']

        clockEventsList = self.get_clockEventsList(fs, fs['autoLunch'])
        self.fldsAppend(False, flds, self.createField_clockEvents(listItems=clockEventsList))


    def ajax_fld_clockEvents(self, request, frmName, fldName=None, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None):
        fs, form, flds, fldIdx, fld, tag = self.processInitFld(request, frmName, fldName)

        if   tag == 'SS': scanType = 'IN'
        elif tag == 'BO': scanType = 'OUT'
        elif tag == 'BI': scanType = 'IN'
        elif tag == 'SF': scanType = 'OUT'
        elif tag == 'XS': scanType = 'IN'
        elif tag == 'XF': scanType = 'OUT'
        machine = request.session['conUser'].get('userId', 0)

        q = """ begin
                    aqcCaptureQC.authUserSession(:user_id);
                    insert into ta_user_entry (
                         scan_type, sysur_auto_key,  tag,  machine,  program
                    ) values (
                        :scanType, :sysur_auto_key, :tag, :machine, :program
                    );
                    commit;
                end;
            """
        rc = dbExecute(None, q, dict(fs.items() + dict( scanType = scanType
                                                      , tag      = tag
                                                      , machine  = machine
                                                      , program  = utils.globalDict['appName']
                                                      ).items()
                                    ))

        return self.ajax_form( request, frmName
                             , msgType=self.FORM_MSG_TYPE_TX_COMPLETE
                             , msg={'IN': 'Clocked-In', 'OUT': 'Clocked-Out'}[scanType]
                             )



    #--------------------------------------------------
    #- convenience routines
    #--------------------------------------------------
    def get_clockEventsList(self, fs, autoLunch):

        tzOffset = 0
        if fs.get('clientTzOffset',0):
            tzOffset = -int( fs.get('clientTzOffset',0) )
        tzOffset = "{}{:0>2d}:{:0>2d}".format( {-1:'-', 1:'+'}[math.copysign(1, tzOffset)]
                                             , int(abs(tzOffset)/60)
                                             , abs(tzOffset) % 60
                                             )

        q = """ select *
                  from (select
                               -- "cast X as timestamp with timezone" yields the time with the local sessionTimeZone (ie server TZ) included
                               -- "at time zone" converts the stored (server) time to the timezone of the client
                               to_char( cast(TAU.scan_time as timestamp with time zone) at time zone '{tzOffset}'
                                      , 'yyyy-mm-dd hh24:mi:ss')                   as "scanTime"
                             , TAU.tag                                             as "tag"
                             , TAU.system                                          as "system"
                          from ta_user_entry   TAU
                             , ta_shift_header TAH
                             , sys_users       SYSUR
                         where SYSUR.sysur_auto_key = TAU.sysur_auto_key
                           and SYSUR.tah_auto_key   = TAH.tah_auto_key (+)
                           and SYSUR.sysur_auto_key = :sysur_auto_key
                           and TAU.scan_time > sysdate - 10
                         order by TAU.tau_auto_key desc
                       )
                  where rownum <= 20 """.format(tzOffset=tzOffset)
        rows, fldNames = dbFetchAll(None, q, fs)

        # filter out rows prior to most recent and relevant start
        displayRows = []
        foundStart = False
        for row in rows:  #remember sequence is currently in reverse event order
            scanTime, tag, system = row
            if tag in ['SF', 'XF'] and not foundStart:
                # displayRows = []
                break
            # if tag in ['SF', 'XF', 'BI'] and foundStart:
            #     break
            # elif tag in ['SS', 'XS', 'BO']:
            #     foundStart = True
            displayRows.append(row)

        # displayRows = [ dict(zip([col[0] for col in fldNames], row)) for row in displayRows[::-1] ]
        eventList = [ {'tag':'SS', 'label':'Start Shift',  'scanTime':'', 'focus':0, 'enabled':False},
                      {'tag':'BO', 'label':'Start Meal',   'scanTime':'', 'focus':0, 'enabled':False},
                      {'tag':'BI', 'label':'Finish Meal',  'scanTime':'', 'focus':0, 'enabled':False},
                      {'tag':'SF', 'label':'Finish Shift', 'scanTime':'', 'focus':0, 'enabled':False},
                      {'tag':'XS', 'label':'Start Extra',  'scanTime':'', 'focus':0, 'enabled':False},
                      {'tag':'XF', 'label':'Finish Extra', 'scanTime':'', 'focus':0, 'enabled':False} ]

        # set scan times
        if autoLunch == 'T':
            eventList[1]['scanTime'] = 'automatic'
            eventList[2]['scanTime'] = 'automatic'
        for row in displayRows[::-1]:
            scanTime, tag, system = row
            if   tag == 'SS': eventList[0]['scanTime'] = scanTime
            elif tag == 'BO': eventList[1]['scanTime'] = scanTime
            elif tag == 'BI': eventList[2]['scanTime'] = scanTime
            elif tag == 'SF': eventList[3]['scanTime'] = scanTime
            elif tag == 'XS': eventList[4]['scanTime'] = scanTime
            elif tag == 'XF': eventList[5]['scanTime'] = scanTime
            # lastTag = tag

        lastTag = 'SF'
        if len(rows):
            _foo1, lastTag, _foo2 = rows[0]
        if   lastTag == 'SS': self.enableClockEvents(eventList, [1,1,0,1,0,0])
        elif lastTag == 'BO': self.enableClockEvents(eventList, [0,1,1,1,0,0])
        elif lastTag == 'BI': self.enableClockEvents(eventList, [0,0,0,1,0,0])
        elif lastTag == 'SF': self.enableClockEvents(eventList, [1,0,0,0,1,0])
        elif lastTag == 'XS': self.enableClockEvents(eventList, [0,0,0,0,1,1])
        elif lastTag == 'XF': self.enableClockEvents(eventList, [1,0,0,0,1,0])

        # figure out item status based on lastRow
        if   lastTag in ['SF', 'XF']:
            eventList[0]['focus'] = 1
        elif lastTag == 'SS' and autoLunch == 'F':
            eventList[1]['focus'] = 1
        elif lastTag == 'BO':
            eventList[2]['focus'] = 1
        elif (lastTag == 'SS' and autoLunch == 'T') or ( lastTag == 'BI'):
            eventList[3]['focus'] = 1
        elif lastTag == 'XS':
            eventList[5]['focus'] = 1

        return eventList


    def enableClockEvents(self, eventList, enabledStates):
        for i in xrange(6):
            eventList[i]['enabled'] = [False, True][enabledStates[i]]


# understanding Oracle timezone stuff
# =========================================================
# select to_char(time_start, 'yyyy-mm-dd hh24:mi:ss')
#      , SESSIONTIMEZONE, DBTIMEZONE
#      , cast(time_start as timestamp with time zone)       --simply appends the SESSIONTIMEZONE to the data value
#      , to_char(cast(time_start as timestamp with time zone) at time zone '00:00', 'yyyy-mm-dd"T"hh24:mi:ssTZH:TZM')
#      , cast(time_start as timestamp with time zone) at time zone 'UTC'
#   from ta_log
#
# select SESSIONTIMEZONE from dual;
# select DBTIMEZONE from dual;


# select * from 
#     (select * from ta_user_entry order by 1 desc)
# where rownum <10

# select day_of_week, act_time_start, act_lunch_time_start, act_lunch_time_finish, act_time_finish
#  from 
#     (select * from ta_log order by 1 desc)
# where rownum <10
