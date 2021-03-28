"""
Copyright AdvanceQC LLC 2014,2015.  All rights reserved
"""

import re

from aqclib         import utils
from aqclib.dbUtils import dbConnection, dbQuote, dbFetchOne, dbFetchAll, dbExecute

from viewsCapture import ViewCapture, ajaxProcess


#############################################################################
# ViewCaptureLabourBatch
#############################################################################
class ViewCaptureLabourBatch(ViewCapture):

    @ajaxProcess
    def ajax_form(self, request, frmName, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None, bbox=None):
        fs, form = self.processInitForm(request, frmName)
        menuEntry = [ x for x in self.MENU_ITEMS if x['name'] == 'labourBatch' ][0]
        form = { 'name':  menuEntry['name']
               , 'label': menuEntry['label']
               , 'desc':  'Clock-in and out of multiple tasks and have your time prorated across all concurrent tasks.'
               , 'flds':  []
               }
        self.appendUser(request, fs, form)
        return self.processFini(request, fs, form, msgType=msgType, msg=msg)

    def createField_woot(self, value=None, msgType=ViewCapture.FLD_MSG_TYPE_NONE, msg=None):
        return self.lineEdit('woot', 'Work Orders', 16, prompt="W/O, Task or Part", value=value, msgType=msgType, msg=msg)

    def createField_skill(self, value=None, msgType=ViewCapture.FLD_MSG_TYPE_NONE, msg=None):
        return self.lineEdit('skill', 'Skill', 10, value=value, msgType=msgType, msg=msg)

    def createField_workOrderList(self, listItems=[], value=None, msgType=ViewCapture.FLD_MSG_TYPE_NONE, msg=None):
        return self.listView('workOrderList', 'Work Orders', listItems, value=value, msgType=msgType, msg=msg)


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

        if fs['wo_skill_scan'] == 'T' or not fs['wok_auto_key']:
            self.fldsAppend(False, flds, self.createField_skill())
        else:
            self.fldsAppend(False, flds, self.createField_skill(value=fs['wok_auto_key'], msgType=self.FLD_MSG_TYPE_VALID, msg=fs['wokDesc']))
            self.fldsAppend(False, flds, self.createField_woot())
            self.fldsAppend(False, flds, self.createField_workOrderList(listItems=self.get_workOrderList(fs, recentOnly=True)))
        self.fldsAppend(False, form['flds'], self.createField_done())


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
        self.fldsAppend(False, flds, self.createField_woot())
        self.fldsAppend(False, flds, self.createField_workOrderList(listItems=self.get_workOrderList(fs, recentOnly=True)))
        return self.processFini(request, fs, form)


    @ajaxProcess
    def ajax_fld_woot(self, request, frmName, fldName=None, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None):
        fs, form, flds, fldIdx, fld, woot = self.processInitFld(request, frmName, fldName)

        workOrders = self.get_workOrderList(fs, wildCard=woot)

        fld['value'] = woot
        fld['msgType'] = self.FLD_MSG_TYPE_VALID
        fld['msg'] = "Found: {} work-orders".format(len(workOrders))
        if len(workOrders):
            self.fldsAppend(False, flds, self.createField_workOrderList(listItems=workOrders))
        return self.processFini(request, fs, form)


    @ajaxProcess
    def ajax_woClockedTasks(self, request, frmName, ):
        fs, form, flds, workOrder = self.processInit(request, frmName)

        # divide into onTaskWOTs and offTaskWOTs groups
        # print jsonDump(workOrder, 'workOrder')
        onTaskWOTs = []; offTaskWOTs = []
        for task in workOrder['tasks']:
            if task.get('clockedIn', 0):
                onTaskWOTs.append(task['wot_auto_key'])
            else:
                offTaskWOTs.append(task['wot_auto_key'])
        # get list of tasks from open batch
        #   query assumes that only one batch can be open for a given user
        openBatchKey = -1
        q = """ select LBH.lbh_auto_key, LBD.wot_auto_key
                  from labor_batch_header LBH
                     , labor_batch_detail LBD
                 where LBH.lbh_auto_key = LBD.lbh_auto_key
                   and LBH.sysur_auto_key = :sysur_auto_key
                   and LBH.start_time is not null
                   and LBH.stop_time is null
            """
        rows, foo = dbFetchAll(None, q, fs)
        openBatchWOTs = [ row[1] for row in rows ]

        if openBatchWOTs:  # okay there was an open batch lets see if we need to modify it
            openBatchKey = rows[0][0]
            tasksAdded =   [ t for t in onTaskWOTs  if t not in openBatchWOTs ]
            tasksRemoved = [ t for t in offTaskWOTs if t     in openBatchWOTs ]
        else:
            tasksAdded =   [ t for t in onTaskWOTs ]
            tasksRemoved = []

        changes = tasksAdded + tasksRemoved
        if not changes:
            response = ['okay']
            msgType = self.FORM_MSG_TYPE_TX_COMPLETE
            msg = "Batch unchanged"
            return self.processFini(request, fs, form, payload=response, msgType=msgType, msg=msg)

        q = """ declare
                    cur  QC_UTL_PKG.CURSOR_TYPE;
                    foo  QC_UTL_PKG.CURSOR_TYPE;
                    l_lbh           number := null;
                    l_start         date   := null;
                    l_start_svr     date   := null;
                    l_wot           number := null;
                    l_back_lbh      number := null;
                    l_back_date     date   := null;
                    l_back_date_svr date   := null;
                    type nt_type    is table of number;
                    autoKeyList     nt_type;
                begin
                    aqcCaptureQC.authUserSession(:user_id);
                    if {openBatchKey} > 0 then
                        select lbh_auto_key, svr_start_time, start_time
                          into l_lbh,        l_start_svr,    l_start
                          from labor_batch_header
                         where lbh_auto_key = {openBatchKey};
                        --
                        select min(wot_auto_key)
                          into l_wot
                          from labor_batch_detail
                         where lbh_auto_key = {openBatchKey};
                        --
                        -- unconditionally close the open batch
                        foo := QC_WO_PKG5.SPI_DIRECT_LABOR2( P_SYSUR        => {sysur_auto_key}
                                                           , P_WOT          => l_wot
                                                           , P_WOK          => {wok_auto_key}
                                                           , P_BARCODE_TYPE => 'C'
                                                           , P_CLOSE_TASK   => 'F'
                                                           , P_MACHINE      => '{loggedInUser}'
                                                           , P_PROGRAM      => 'CaptureQC'
                                                           , P_LBH          => l_lbh
                                                           , P_STOP_TIME_OVERRIDE => null
                                                           );
                        update labor_batch_header
                           set description = 'Closed  ( '
                                          || to_char(trunc( (svr_stop_time - svr_start_time) * 24 ), '09') || 'hr '
                                          || to_char(trunc( (       ((svr_stop_time - svr_start_time) * 24)
                                                             - trunc((svr_stop_time - svr_start_time) * 24)
                                                            ) * 60
                                                          ), '09'
                                                    ) || 'min duration)'
                         where lbh_auto_key = l_lbh;
                        --
                        -- if the openBatch was started within the 'graceTime'
                        --   mark deleted any WTL records that were part of this open batch
                        if (sysdate - l_start_svr) * 86400 <= {graceTime} then
                            for r in ( select wtl_auto_key
                                         from wo_task_labor
                                        where lbd_auto_key in (select lbd_auto_key
                                                                 from labor_batch_detail
                                                                where lbh_auto_key = l_lbh)) loop
                                QC_WO_PKG2.SPD_WTL(r.wtl_auto_key);
                            end loop;
                            --
                            l_back_lbh      := l_lbh;       --keep back reference for later access
                            l_back_date_svr := l_start_svr;
                            l_back_date     := l_start;
                        end if;
                        --
                    end if;
                    --
                    -- create a new batch, and prime it with LBDs from the openBatch
                    select g_lbh_auto_key.nextval into l_lbh from dual;
                    insert into labor_batch_header (
                            lbh_auto_key, sysur_auto_key,   description
                        ) values (
                            l_lbh,        {sysur_auto_key}, 'ACTIVE'
                        );
                    --
                    -- if there was an openBatch then prime the new batch with LBDs from the openBatch
                    if {openBatchKey} > 0 then
                        insert into labor_batch_detail (
                                     lbd_auto_key,           lbh_auto_key, wot_auto_key
                            ) select g_lbd_auto_key.nextval, l_lbh,        wot_auto_key
                                from labor_batch_detail
                               where lbh_auto_key = {openBatchKey};
                    end if;
                    --
                    -- we now have the new batch to manipulate: remove tasksRemoved
                    autoKeyList := nt_type({tasksRemoved});
                    for i in 1..autoKeyList.count loop
                        delete from labor_batch_detail
                         where lbh_auto_key = l_lbh
                           and wot_auto_key = autoKeyList(i);
                    end loop;
                    --
                    -- add tasksAdded
                    autoKeyList := nt_type({tasksAdded});
                    for i in 1..autoKeyList.count loop
                        insert into labor_batch_detail (
                                 lbd_auto_key,           lbh_auto_key, wot_auto_key
                            ) values (
                                 g_lbd_auto_key.nextval, l_lbh,        autoKeyList(i)
                            );
                        --
                        -- AvroTechnik customization
                        -- if this task is 'In Prog-Initial' or 'In-Prog. Final' then we need to ensure the WO status is at least as high
                        declare
                            QUANTUM_ID constant number := 1952;
                            l_quantumId number;
                        begin
                            select quantum_id into l_quantumID from quantum;
                            if l_quantumID = QUANTUM_ID then
                                aqc_1952.advanceStatus(autoKeyList(i));
                            end if;
                        end;
                    end loop;
                    --
                    -- see if the batch has any detail left by attempting to retrieve a WOT from the batch's detail
                    open cur for
                        select min(wot_auto_key)
                          from labor_batch_detail
                         where lbh_auto_key = l_lbh;
                    fetch cur into l_wot;
                    if cur{percentNotFound} then
                        l_wot := NULL;
                    end if;
                    close cur;
                    --
                    if l_wot is null then    -- batch is empty so get rid of it
                        delete from labor_batch_header
                         where lbh_auto_key = l_lbh;
                        --
                    else
                        -- start the batch
                        foo := QC_WO_PKG5.SPI_DIRECT_LABOR2( P_SYSUR        => {sysur_auto_key}
                                                           , P_WOT          => l_wot
                                                           , P_WOK          => {wok_auto_key}
                                                           , P_BARCODE_TYPE => 'S'
                                                           , P_CLOSE_TASK   => 'F'
                                                           , P_MACHINE      => '{loggedInUser}'
                                                           , P_PROGRAM      => 'CaptureQC'
                                                           , P_LBH          => l_lbh
                                                           , P_STOP_TIME_OVERRIDE => null
                                                           );
                        -- fix the start times by adjustment (time-zone agnostic)
                        if l_back_lbh is not null then
                            update labor_batch_header
                               set svr_start_time = l_back_date_svr + interval '1' second
                                 , start_time     = l_back_date     + interval '1' second
                                 , batch_id = (select regexp_substr(batch_id, '^[^-]+') || '-'
                                                      || to_char(nvl(to_number(substr(regexp_substr(batch_id, '-[0-9]+$'), 2)), 0) + 1)
                                                 from labor_batch_header
                                                where lbh_auto_key = l_back_lbh)
                             where lbh_auto_key = l_lbh;
                            --
                            update wo_task_labor
                               set svr_start_time = l_back_date_svr + interval '1' second
                                 , start_time     = l_back_date     + interval '1' second
                             where lbd_auto_key in (select lbd_auto_key
                                                      from labor_batch_detail
                                                     where lbh_auto_key = l_lbh);
                        end if;
                    end if;
                    --
                    -- as much as possible make a superseded batch become invisible
                    if l_back_lbh is not null then
                        if l_wot is not null then
                            update labor_batch_header
                               set description = 'Superseded by batch ' || (select batch_id
                                                                              from labor_batch_header
                                                                             where lbh_auto_key = l_lbh)
                             where lbh_auto_key = l_back_lbh;
                        else
                            update labor_batch_header
                               set description = 'Cancelled by {loggedInUser}'
                             where lbh_auto_key = l_back_lbh;
                        end if;
                    end if;
                    --
                    commit;
                end;
            """.format( openBatchKey = openBatchKey
                      , graceTime = request.session['defaultsProfile'].get('batchLaborGraceTime', 300)
                      , tasksAdded   = ",".join([str(x) for x in tasksAdded])
                      , tasksRemoved = ",".join([str(x) for x in tasksRemoved])
                      , loggedInUser = fs['loggedInUser']
                      , sysur_auto_key = fs['sysur_auto_key']
                      , wok_auto_key = fs['wok_auto_key']
                      , percentNotFound = '%NOTFOUND'
                      )
        rc = dbExecute(None, q, fs)

        newBatchKey = None
        newBatchId = None
        q = """ select lbh_auto_key, batch_id
                  from labor_batch_header
                 where sysur_auto_key = :sysur_auto_key
                   and start_time is not null
                   and stop_time is null """
        row, fldNames = dbFetchOne(None, q, fs)
        if row:
            newBatchKey, newBatchId = row

        if newBatchKey == openBatchKey:
            msg = "Batch {} updated".format(newBatchId)
        elif newBatchKey:
            msg = "Batch {} created".format(newBatchId)
        else:
            msg = "Batch {} closed".format(openBatchKey)

        response = ['okay']
        return self.processFini(request, fs, form, payload=response, msgType=self.FORM_MSG_TYPE_TX_COMPLETE, msg=msg)


    @ajaxProcess
    def ajax_restart(self, request, frmName, ):
        fs, form, flds, foo = self.processInit(request, frmName)

        # make sure we already have user's id and skill by checking that the woot field is being displayed
        if not self.getFldIndex(flds, 'woot'):
            msgType = self.FORM_MSG_TYPE_ERROR
            msg = "User and skill must first be provided"
            return self.processFini(request, fs, form, msgType=msgType, msg=msg)

        # see if user already has an open batch
        q = """ select lbh_auto_key, batch_id
                  from labor_batch_header
                 where sysur_auto_key = :sysur_auto_key
                   and start_time is not null
                   and stop_time is null """
        row, fldNames = dbFetchOne(None, q, fs)
        if row:
            newBatchKey, newBatchId = row
            msgType = self.FORM_MSG_TYPE_ERROR
            msg = "Batch {} is currently open".format(newBatchId)
            return self.processFini(request, fs, form, msgType=msgType, msg=msg)

        # get the lbh for the most recent batch
        q = """ select max(lbh_auto_key)
                  from labor_batch_detail
                 where lbd_auto_key in (select lbd_auto_key
                                          from wo_task_labor
                                         where sysur_auto_key = :sysur_auto_key
                                           and lbd_auto_key is not NULL
                                           and delete_date is Null
                                       )
            """
        row, fldNames = dbFetchOne(None, q, fs)
        if not row:
            msgType = self.FORM_MSG_TYPE_ERROR
            msg = "No previous batch found"
            return self.processFini(request, fs, form, msgType=msgType, msg=msg)
        lbh_auto_key = row[0]

        # create a copy of the batch and start it
        q = """ declare
                    cur  QC_UTL_PKG.CURSOR_TYPE;
                    foo  QC_UTL_PKG.CURSOR_TYPE;
                    l_lbh           number := null;
                    l_wot           number := null;
                    l_back_lbh      number := null;
                begin
                    aqcCaptureQC.authUserSession(:user_id);
                    -- find the most recent batch
                    open cur for
                        select max(lbh_auto_key)
                         from labor_batch_detail
                        where lbd_auto_key in (select lbd_auto_key
                                                 from wo_task_labor
                                                where sysur_auto_key = {sysur_auto_key}
                                                  and lbd_auto_key is not NULL
                                                  and delete_date is Null
                                              );
                    fetch cur into l_back_lbh;
                    if cur{percentNotFound} then
                        raise_application_error(-20999, 'User has no previous batch');
                    end if;
                    close cur;
                    --
                    -- create a new batch
                    select g_lbh_auto_key.nextval into l_lbh from dual;
                    insert into labor_batch_header (
                            lbh_auto_key, sysur_auto_key,   description
                        ) values (
                            l_lbh,        {sysur_auto_key}, 'ACTIVE'
                        );
                    --
                    -- prime from last batch
                    insert into labor_batch_detail (
                                 lbd_auto_key,           lbh_auto_key, wot_auto_key
                        ) select g_lbd_auto_key.nextval, l_lbh,        wot_auto_key
                            from labor_batch_detail
                           where lbh_auto_key = l_back_lbh;
                    --
                    -- see if the batch has any detail by attempting to retrieve a WOT from the batch's detail
                    open cur for
                        select min(wot_auto_key)
                          from labor_batch_detail
                         where lbh_auto_key = l_lbh;
                    fetch cur into l_wot;
                    if cur{percentNotFound} then l_wot := NULL; end if;
                    close cur;
                    --
                    if l_wot is null then
                        -- batch is empty so get rid of it
                        delete from labor_batch_header
                         where lbh_auto_key = l_lbh;
                        --
                    else
                        -- start the batch
                        foo := QC_WO_PKG5.SPI_DIRECT_LABOR2( P_SYSUR        => {sysur_auto_key}
                                                           , P_WOT          => l_wot
                                                           , P_WOK          => {wok_auto_key}
                                                           , P_BARCODE_TYPE => 'S'
                                                           , P_CLOSE_TASK   => 'F'
                                                           , P_MACHINE      => '{loggedInUser}'
                                                           , P_PROGRAM      => 'CaptureQC'
                                                           , P_LBH          => l_lbh
                                                           , P_STOP_TIME_OVERRIDE => null
                                                           );
                    end if;
                    --
                    commit;
                end;
            """.format( loggedInUser = fs['loggedInUser']
                      , sysur_auto_key = fs['sysur_auto_key']
                      , wok_auto_key = fs['wok_auto_key']
                      , percentNotFound = '%NOTFOUND'
                      )
        rc = dbExecute(None, q, fs)

        newBatchKey = None
        newBatchId = None
        q = """ select lbh_auto_key, batch_id
                  from labor_batch_header
                 where sysur_auto_key = :sysur_auto_key
                   and start_time is not null
                   and stop_time is null """
        row, fldNames = dbFetchOne(None, q, fs)
        if row:
            newBatchKey, newBatchId = row

        if newBatchKey:
            msg = "Batch {} created".format(newBatchId)
            idx = self.getFldIndex(flds, 'workOrderList')
            if idx:
                flds[idx]['listItems']=self.get_workOrderList(fs, recentOnly=True)
            else:
                self.fldsAppend(False, flds, self.createField_workOrderList(listItems=self.get_workOrderList(fs, recentOnly=True)))
        else:
            msg = "No batch created"

        response = ['okay']
        return self.processFini(request, fs, form, msgType=self.FORM_MSG_TYPE_TX_COMPLETE, msg=msg)


    @ajaxProcess
    def ajax_stopAllTasks(self, request, frmName, ):
        fs, form, flds, foo = self.processInit(request, frmName)

        # make sure we already have user's id and skill by checking that the woot field is being displayed
        if not self.getFldIndex(flds, 'woot'):
            msgType = self.FORM_MSG_TYPE_ERROR
            msg = "User and skill must first be provided"
            return self.processFini(request, fs, form, msgType=msgType, msg=msg)

        # check that user already has an open batch
        q = """ select lbh_auto_key, batch_id
                  from labor_batch_header
                 where sysur_auto_key = :sysur_auto_key
                   and start_time is not null
                   and stop_time is null """
        row, fldNames = dbFetchOne(None, q, fs)
        if not row:
            msgType = self.FORM_MSG_TYPE_ERROR
            msg = "No open batch"
            return self.processFini(request, fs, form, msgType=msgType, msg=msg)

        # close it
        curBatchKey, curBatchId = row
        q = """ declare
                    cur  QC_UTL_PKG.CURSOR_TYPE;
                    foo  QC_UTL_PKG.CURSOR_TYPE;
                    l_lbh            number := null;
                    l_wot            number := null;
                begin
                    aqcCaptureQC.authUserSession(:user_id);
                    -- find the open batch
                    open cur for
                        select LBH.lbh_auto_key, min(wot_auto_key)
                          from labor_batch_header LBH
                             , labor_batch_detail LBD
                         where LBH.lbh_auto_key = LBD.lbh_auto_key
                           and LBH.sysur_auto_key = {sysur_auto_key}
                           and LBH.start_time is not null
                           and LBH.stop_time is null
                         group by LBH.lbh_auto_key;
                    fetch cur into l_lbh, l_wot;
                    if cur{percentNotFound} then
                        raise_application_error(-20999, 'User has no open batch');
                    end if;
                    close cur;
                    --
                    -- stop the batch
                    foo := QC_WO_PKG5.SPI_DIRECT_LABOR2( P_SYSUR        => {sysur_auto_key}
                                                       , P_WOT          => l_wot
                                                       , P_WOK          => {wok_auto_key}
                                                       , P_BARCODE_TYPE => 'C'
                                                       , P_CLOSE_TASK   => 'F'
                                                       , P_MACHINE      => '{loggedInUser}'
                                                       , P_PROGRAM      => 'CaptureQC'
                                                       , P_LBH          => l_lbh
                                                       , P_STOP_TIME_OVERRIDE => null
                                                       );
                    update labor_batch_header
                       set description = 'Closed  ( '
                                      || to_char(trunc( (svr_stop_time - svr_start_time) * 24 ), '09') || 'hr '
                                      || to_char(trunc( (       ((svr_stop_time - svr_start_time) * 24)
                                                         - trunc((svr_stop_time - svr_start_time) * 24)
                                                        ) * 60
                                                      ), '09'
                                                ) || 'min duration)'
                     where lbh_auto_key = l_lbh;
                    --
                    commit;
                end;
            """.format( loggedInUser = fs['loggedInUser']
                      , sysur_auto_key = fs['sysur_auto_key']
                      , wok_auto_key = fs['wok_auto_key']
                      , percentNotFound = '%NOTFOUND'
                      )
        rc = dbExecute(None, q, fs)

        batchKey = None
        q = """ select max(lbh_auto_key)
                  from labor_batch_header
                 where sysur_auto_key = :sysur_auto_key
                   and start_time is not null
                   and stop_time is not null """
        row, fldNames = dbFetchOne(None, q, fs)
        if row:
            batchKey, = row

        if batchKey == curBatchKey:
            msg = "Batch {} closed".format(curBatchId)
            idx = self.getFldIndex(flds, 'workOrderList')
            if idx:
                flds[idx]['listItems']=self.get_workOrderList(fs, recentOnly=True)
            else:
                self.fldsAppend(False, flds, self.createField_workOrderList(listItems=self.get_workOrderList(fs, recentOnly=True)))
        else:
            msg = "Open batch not found"

        response = ['okay']
        return self.processFini(request, fs, form, msgType=self.FORM_MSG_TYPE_TX_COMPLETE, msg=msg)


    #--------------------------------------------------
    #- convenience routines
    #--------------------------------------------------
    def get_workOrderList(self, fs, recentOnly=False, wildCard=None):

        whereClause = ""
        if wildCard:  #match workOrders by scanned-task, workOrder, or partNumber
            whereClause = "and ( 1=2 "
            if re.match('[0-9]+[SCsc]$', wildCard):  # could be a task capture
                whereClause += " or WOT.wot_auto_key = {0} ".format(wildCard[:-1])
            elif re.match('[0-9]+$', wildCard):    # it's all numeric
                whereClause += " or WOO.woo_auto_key = {0} ".format(wildCard)
                whereClause += " or PNM.pnm_auto_key = {0} ".format(wildCard)
                whereClause += " or WOO.si_number like '{1}{0}{1}' ".format(dbQuote(wildCard), '%')
                whereClause += " or PNM.pn_stripped like '{1}{0}{1}' ".format(dbQuote(wildCard), '%')
            elif re.search('[\w]', wildCard):      # it has at least one alphanumeric character
                whereClause += " or upper(WOO.si_number)   like upper('{1}{0}{1}') ".format(re.sub('[\W_]+', '', wildCard), '%')
                whereClause += " or upper(PNM.pn_stripped) like upper('{1}{0}{1}') ".format(re.sub('[\W_]+', '', wildCard), '%')
                whereClause += " or upper(PNM.description) like upper('{1}{0}{1}') ".format(re.sub('[\W_]+', '', wildCard), '%')
            whereClause += ")"
        if recentOnly:
            whereClause += " and recent.woo_auto_key is not null"
        print "recentOnly", recentOnly
        q = """
                with recentTasks as (     -- all direct tasks for user within one day of most recent activity
                         select distinct wot_auto_key
                           from wo_task_labor
                          where (
                                     (    start_time is not null
                                      and stop_time is null
                                     )
                                 or
                                     start_time > ( select max(start_time)
                                                      from wo_task_labor
                                                     where sysur_auto_key = :sysur_auto_key
                                                       and delete_date is null
                                                  ) - 1
                                )
                            and delete_date is null
                         )
                   , recentIndirect as (  -- all indirect tasks for user within one day of most recent activity
                         select distinct wot_curr as wot_auto_key
                           from wo_barcode_labor
                          where log_time_curr > ( select max(log_time_curr)
                                                    from wo_barcode_labor
                                                   where sysur_curr = :sysur_auto_key
                                                ) - 1
                         )
                   , recentWorkOrder as ( -- workorders related to the recent direct and indirect tasks
                         select distinct woo_auto_key
                           from wo_task
                          where wot_auto_key in (select wot_auto_key from recentTasks)
                             or wot_auto_key in (select wot_auto_key from recentIndirect)
                         )
                   , inProgressTasks as (  -- get wot_auto_keys for batch tasks into which user is logged
                         select WTL.wot_auto_key, 1 as clockedIn
                           from wo_task_labor WTL
                          where WTL.start_time is not null
                            and WTL.stop_time is null
                            and WTL.delete_date is null
                            and WTL.sysur_auto_key = :sysur_auto_key
                            and WTL.lbd_auto_key is not null     --ignore labor recs that are single-task
                         )
                   , symptom as (
                         select distinct WSL.woo_auto_key as WSL_woo_auto_key
                              , first_value(DBMS_LOB.substr(WSL.notes, 512) ignore nulls) over
                                   (partition by WSL.woo_auto_key order by WSL.sequence, WSL.wsl_auto_key) as WSL_firstNote
                           from wo_symptom_list WSL
                         )
                select WOO.woo_auto_key     as woo_auto_key  --0
                     , WOO.si_number        as si_number     --1
                     , PNM.pn               as partNumber    --2
                     , PNM.description      as partDesc      --3
                     , WOT.wot_auto_key     as wot_auto_key  --4
                     , WOT.sequence         as sequence      --5
                     , WTM.description      as masterDesc    --6
                     --, nvl(nvl(WOT.squawk_desc, WOT.long_descr), null)    as longDesc  --7
                     , QC_WO_PKG2.get_taks_descr(WOT.wot_auto_key)        as longDesc    --7
                     , decode(nvl(recent.woo_auto_key, -1), -1, 0, 1)     as recent      --8
                     , nvl(inProgress.clockedIn, 0)                                      as taskClockedIn        --9
                     , count(WOT.wot_auto_key)     over (partition by WOO.woo_auto_key)  as countTasks           --10
                     , count(inProgress.clockedIn) over (partition by WOO.woo_auto_key)  as countTasksClockedIn  --11
                     , nvl(symptom.WSL_firstNote, '')         as symptom         --12
                     , nvl(WOS_WOO.description,   'Pending')  as woo_statusDesc  --13
                     , nvl(WOS_WOT.description,   'Pending')  as wot_statusDesc  --14
                  from wo_operation     WOO
                     , parts_master     PNM
                     , wo_task          WOT
                     , wo_task_master   WTM
                     , wo_status        WOS_WOO
                     , wo_status        WOS_WOT
                     , recentWorkOrder  recent
                     , inProgressTasks  inProgress
                     , symptom          symptom
                 where WOO.pnm_auto_key = PNM.pnm_auto_key (+)
                   and WOO.woo_auto_key = WOT.woo_auto_key
                   and WOT.wtm_auto_key = WTM.wtm_auto_key  -- all tasks have a masters
                   and WOO.wos_auto_key = WOS_WOO.wos_auto_key (+)
                   and WOT.wos_auto_key = WOS_WOT.wos_auto_key (+)
                   and WOO.woo_auto_key = recent.woo_auto_key (+)
                   and WOT.wot_auto_key = inProgress.wot_auto_key (+)
                   and WOO.woo_auto_key = symptom.WSL_woo_auto_key (+)
                   and WOO.open_flag = 'T'
                   {whereClause}
                 order by WOO.woo_auto_key, WOT.sequence
            """.format(whereClause=whereClause)
        rows, fldNames = dbFetchAll(None, q, fs)

        # post process to split workOrders and tasks
        recent = []; others = []
        cur = {'woo_auto_key': -1}
        tasks = []
        for row in rows:
            if row[0] != cur['woo_auto_key']:  #first time we see this work order
                tasks = []
                cur = { 'woo_auto_key':         row[0]
                      , 'si_number':            row[1]
                      , 'partNumber':           row[2]
                      , 'partDesc':             row[3]
                      , 'recent':               row[8]
                      , 'countTasks':           row[10]
                      , 'countTasksClockedIn':  row[11]
                      , 'symptom':              row[12]
                      , 'woo_statusDesc':       row[13]
                      , 'tasks':                tasks
                      }
                if row[8]:
                    recent.append(cur)
                else:
                    others.append(cur)
            else:
                tasks = cur['tasks']
            tasks.append({ 'wot_auto_key':    row[4]
                         , 'sequence':        row[5]
                         , 'masterDesc':      row[6]
                         , 'longDesc':        row[7]
                         , 'clockedIn':       row[9]
                         , 'wot_statusDesc':  row[14]
                         })
        return recent + others
