"""
Copyright AdvanceQC LLC 2014,2015.  All rights reserved
"""

import re

from aqclib         import utils
from aqclib.dbUtils import dbConnection, dbQuote, dbFetchOne, dbFetchAll, dbExecute

from viewsCapture import ViewCapture, ajaxProcess


#############################################################################
# ViewCaptureLabour
#############################################################################
class ViewCaptureLabour(ViewCapture):

    @ajaxProcess
    def ajax_form(self, request, frmName, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None, bbox=None):
        fs, form = self.processInitForm(request, frmName)
        menuEntry = [ x for x in self.MENU_ITEMS if x['name'] == 'labour' ][0]
        form = { 'name':  menuEntry['name']
               , 'label': menuEntry['label']
               , 'desc':  'Labor capture for staff who accrue to only one task at a time.  This is the fastest way to clock-on or off a task.'
               , 'flds':  []
               }
        self.appendUser(request, fs, form)
        return self.processFini(request, fs, form, msgType=msgType, msg=msg, bbox=self.get_workOrderTaskInfo(fs))

    def createField_skill(self, value=None, msgType=ViewCapture.FLD_MSG_TYPE_NONE, msg=None):
        return self.lineEdit('skill', 'Skill', 8, value=value, msgType=msgType, msg=msg)

    def createField_task(self, value=None, msgType=ViewCapture.FLD_MSG_TYPE_NONE, msg=None):
        return self.lineEdit('task', 'Task', 10, value=value, msgType=msgType, msg=msg)


    def gotUser(self, request, fs, form, flds, fld):
        #see if users are to scan skills when making labor entries
        q = """select wo_skill_scan
                 from quantum"""
        row, fldNames = dbFetchOne(None, q)
        fs['wo_skill_scan'], = row

        if fs['wo_flag'] == "F" and fs['mo_flag'] == "F":
            fld['value'] = ""
            fld['msgType'] = self.FLD_MSG_TYPE_NOT_FOUND
            fld['msg'] = "{} has not been set to accrue labour".format(fs['employee_code'])
            return self.processFini(request, fs, form)

        self.fldsAppend(False, flds, self.createField_done())
        if fs['wo_skill_scan'] == 'T' or not fs['wok_auto_key']:
            self.fldsAppend(False, flds, self.createField_skill())
        else:
            self.fldsAppend(False, flds, self.createField_skill(value=fs['wok_auto_key'], msgType=self.FLD_MSG_TYPE_VALID, msg=fs['wokDesc']))
            self.fldsAppend(False, flds, self.createField_task())


    @ajaxProcess
    def ajax_fld_userId(self, request, frmName, fldName=None, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None):
        fs, form, flds, fldIdx, fld, user_id = self.processInitFld(request, frmName, fldName)

        self.generic_fld_userId(request, fs, form, flds, fld, user_id)
        if fs['sysur_auto_key']:
            self.gotUser(request, fs, form, flds, fld)
        return self.processFini(request, fs, form, bbox=self.get_workOrderTaskInfo(fs))


    @ajaxProcess
    def ajax_fld_skill(self, request, frmName, fldName=None, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None):
        fs, form, flds, fldIdx, fld, wok_auto_key = self.processInitFld(request, frmName, fldName)

        fs['wok_auto_key'] = wok_auto_key
        q = """ select description
                  from wo_skills
                 where wok_auto_key = :wok_auto_key """
        row, fldNames = dbFetchOne(None, q, fs)

        if not row:
            fld['value'] = ""
            fld['msgType'] = self.FLD_MSG_TYPE_NOT_FOUND
            fld['msg'] = "Skill not found"
            return self.processFini(request, fs, form)
        description, = row

        # confirm that this skill is one that the user currently possesses
        q = """ select 'true'
                  from wo_empl_skills WES
                 where sysur_auto_key = :sysur_auto_key
                   and sysdate between nvl(onset_date, sysdate -1)
                                   and nvl(expir_date, sysdate +1)
                   and wok_auto_key = :wok_auto_key
                union
                select 'true'
                  from sys_users
                 where sysur_auto_key = :sysur_auto_key
                   and wok_auto_key = :wok_auto_key """
        row, fldNames = dbFetchOne(None, q, fs)

        if not row:
            fld['value'] = ""
            fld['msgType'] = self.FLD_MSG_TYPE_NOT_FOUND
            fld['msg'] = "Skill not currently possessed"
            return self.processFini(request, fs, form)

        fld['value'] = wok_auto_key
        fld['msgType'] = self.FLD_MSG_TYPE_VALID
        fld['msg'] = description
        self.fldsAppend(False, flds, self.createField_task())
        return self.processFini(request, fs, form, bbox=self.get_workOrderTaskInfo(fs))


    @ajaxProcess
    def ajax_fld_task(self, request, frmName, fldName=None, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None):
        fs, form, flds, fldIdx, fld, task = self.processInitFld(request, frmName, fldName)

        matchObj = re.match('^(\d+)([sScC])$', task.strip().upper())
        if matchObj is None:
            fld['value'] = ""
            fld['msgType'] = self.FLD_MSG_TYPE_INVALID
            fld['msg'] = "Entered task has invalid format"
            return self.processFini(request, fs, form)

        wot_auto_key = matchObj.group(1);  fs['wot_auto_key'] = wot_auto_key
        barcodeType  = matchObj.group(2);  fs['barcodeType'] =  barcodeType

        # get the status, and description
        q = """ select WOT.woo_auto_key
                     , nvl(WOS.status_type, 'Pending')
                     , nvl(WOS.description, 'Pending')
                     , WOT.sequence
                     , nvl(nvl(WOT.squawk_desc, WOT.long_descr), WTM.description)
                  from wo_task        WOT
                     , wo_status      WOS
                     , wo_task_master WTM
                 where WOT.wos_auto_key = WOS.wos_auto_key (+)
                   and WOT.wtm_auto_key = WTM.wtm_auto_key  -- all tasks have a master
                   and WOT.wot_auto_key = :wot_auto_key """
        row, fldNames = dbFetchOne(None, q, fs)

        if not row:
            fld['value'] = ""
            fld['msgType'] = self.FLD_MSG_TYPE_NOT_FOUND
            fld['msg'] = "Task not found"
            return self.processFini(request, fs, form)
        fs['woo_auto_key'], status_type, status_desc, task_sequence, task_desc = row

        # can labor be posted to closed tasks;  are we using direct labor...
        q = """ select nvl(closed_labor_rec, 'F') closed_labor_rec
                     , nvl(direct_labor, 'F')     direct_labor
                  from wo_control """
        row, fldNames = dbFetchOne(None, q)

        if not row:
            fld['value'] = ""
            msgType = self.FORM_MSG_TYPE_CRITICAL
            msg = "WO-Control Table is inaccessible"
            return self.processFini(request, fs, form, msgType=msgType, msg=msg)
        closed_labor_rec, direct_labor = row

        # possible staus_types: Open Closed Delay Defer Cancel (Pending)
        # if closed_labor_rec is "T" then allow unconditionally
        # else only allow if status_type is not 'Closed' or 'Cancelled'
        if closed_labor_rec == 'F' and status_type in ('Closed', 'Cancelled'):
            fld['value'] = ""
            fld['msgType'] = self.FLD_MSG_TYPE_INVALID
            fld['msg'] = "Task status is: {}.".format(status_desc)
            return self.processFini(request, fs, form)

        if direct_labor == 'T':
            # insert entry into database
            q = """ declare
                        foo QC_UTL_PKG.CURSOR_TYPE;
                    begin
                        aqcCaptureQC.authUserSession(:user_id);
                        foo := QC_WO_PKG2.SPI_DIRECT_LABOR( P_SYSUR        => :sysur_auto_key
                                                          , P_WOT          => :wot_auto_key
                                                          , P_WOK          => :wok_auto_key
                                                          , P_BARCODE_TYPE => :barcodeType
                                                          , P_CLOSE_TASK   => 'F'
                                                          , P_MACHINE      => :loggedInUser
                                                          , P_PROGRAM      => :appName
                                                          );
                        commit;
                    end;
                """
        else:
            q = """ begin
                        aqcCaptureQC.authUserSession(:user_id);
                        insert into wo_barcode_labor (
                                   wbl_auto_key,          woo_orig,      woo_curr,      wot_orig,      wot_curr,      sysur_curr,      sysur_orig,      wok_orig,      wok_curr,     log_time_curr, log_time_orig, activity_flag_orig, activity_flag_curr, machine,       program     )
                        values ( g_wbl_auto_key.nextVal, :woo_auto_key, :woo_auto_key, :wot_auto_key, :wot_auto_key, :sysur_auto_key, :sysur_auto_key, :wok_auto_key, :wok_auto_key, sysdate,       sysdate,       :barcodeType,       :barcodeType,       :loggedInUser, :appName );
                        commit;
                    end;
                """
        rc = dbExecute(None, q, fs)

        # AvroTechnik customization
        # if this task is "In Prog-Initial" or "In-Prog. Final" then we need to ensure the WO status is at least as high
        q = """ declare
                    QUANTUM_ID constant number := 1952;
                    l_quantumId number;
                begin
                    select quantum_id into l_quantumID from quantum;
                    if l_quantumID != QUANTUM_ID then
                        return;
                    end if;
                    aqcCaptureQC.authUserSession(:user_id);
                    aqc_1952.advanceStatus(:wot_auto_key);
                    commit;
                end;
            """
        rc = dbExecute(None, q, fs)

        woti = self.get_workOrderTaskInfo(fs)
        msg = {'S': 'Signed onto task', 'C': 'Signed off of task'}[barcodeType]
        if request.session['conUser'].get('public', 0):
            return self.ajax_form(request, frmName
                                  , msgType=self.FORM_MSG_TYPE_TX_COMPLETE
                                  , msg=msg
                                  , bbox=woti
                                  )
        else:
            fld['value'] = ""
            fld['msgType'] = self.FLD_MSG_TYPE_VALID
            fld['msg'] = ""
            return self.processFini( request, fs, form
                                   , msgType=self.FORM_MSG_TYPE_TX_COMPLETE
                                   , msg=msg
                                   , bbox=woti
                                   )


    #--------------------------------------------------
    #- convenience routines
    #--------------------------------------------------
    # modelled after laborBatch but will only ever return a single workOrder and single task
    def get_workOrderTaskInfo(self, fs):
        if 'sysur_auto_key' not in fs:
            return None
        if 'wot_auto_key' in fs:
            wClause = """ and WOT.wot_auto_key = inProgress.wot_auto_key (+)
                          and WOT.wot_auto_key = :wot_auto_key """
        else:
            wClause = """ and WOT.wot_auto_key = inProgress.wot_auto_key """

        q = """
                with inProgressTasks as (  -- get wot_auto_keys for batch tasks into which user is logged
                         select WTL.wot_auto_key, 1 as clockedIn
                           from wo_task_labor WTL
                          where WTL.start_time is not null
                            and WTL.stop_time is null
                            and WTL.delete_date is null
                            and WTL.sysur_auto_key = :sysur_auto_key
                            and WTL.lbd_auto_key is  null     --ignore labor recs that are batch
                         )
                   , symptom as (
                         select distinct WSL.woo_auto_key as WSL_woo_auto_key
                              , first_value(DBMS_LOB.substr(WSL.notes, 512) ignore nulls) over
                                   (partition by WSL.woo_auto_key order by WSL.sequence, WSL.wsl_auto_key) as WSL_firstNote
                           from wo_symptom_list WSL
                         )
                select WOO.woo_auto_key     as "woo_auto_key"  --0
                     , WOO.si_number        as "si_number"     --1
                     , PNM.pn               as "partNumber"    --2
                     , PNM.description      as "partDesc"      --3
                     , WOT.wot_auto_key     as "wot_auto_key"  --4
                     , WOT.sequence         as "sequence"      --5
                     , WTM.description      as "masterDesc"    --6
                     --, nvl(nvl(WOT.squawk_desc, WOT.long_descr), null)    as "longDesc"  --7
                     , QC_WO_PKG2.get_taks_descr(WOT.wot_auto_key)        as "longDesc"  --7
                     , nvl(inProgress.clockedIn, 0)                                      as "clockedIn"            --8
                     , count(WOT.wot_auto_key)     over (partition by WOO.woo_auto_key)  as "countTasks"           --9
                     , count(inProgress.clockedIn) over (partition by WOO.woo_auto_key)  as "countTasksClockedIn"  --10
                     , nvl(symptom.WSL_firstNote, '')         as "symptom"         --11
                     , nvl(WOS_WOO.description,   'Pending')  as "woo_statusDesc"  --12
                     , nvl(WOS_WOT.description,   'Pending')  as "wot_statusDesc"  --13
                  from wo_operation     WOO
                     , parts_master     PNM
                     , wo_task          WOT
                     , wo_task_master   WTM
                     , wo_status        WOS_WOO
                     , wo_status        WOS_WOT
                     , symptom          symptom
                     , inProgressTasks  inProgress
                 where WOO.pnm_auto_key = PNM.pnm_auto_key
                   and WOO.woo_auto_key = WOT.woo_auto_key
                   and WOT.wtm_auto_key = WTM.wtm_auto_key  -- all tasks have a masters
                   and WOO.wos_auto_key = WOS_WOO.wos_auto_key (+)
                   and WOT.wos_auto_key = WOS_WOT.wos_auto_key (+)
                   and WOO.woo_auto_key = symptom.WSL_woo_auto_key (+)
                   and WOT.wot_auto_key = inProgress.wot_auto_key (+)
                   {wClause}
                   --and WOO.open_flag = 'T'
                 order by WOO.woo_auto_key, WOT.sequence
            """.format(wClause=wClause)
        rec, fldNames = dbFetchOne(None, q, fs, asDict=True)
        return rec

