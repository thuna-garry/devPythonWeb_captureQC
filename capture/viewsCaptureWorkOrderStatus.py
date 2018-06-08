"""
Copyright AdvanceQC LLC 2014,2015.  All rights reserved
"""

import re

from aqclib         import utils
from aqclib.dbUtils import dbConnection, dbQuote, dbFetchOne, dbFetchAll, dbExecute

from viewsCapture import ViewCapture, ajaxProcess


#############################################################################
# ViewCaptureWoStatus
#############################################################################
class ViewCaptureWorkOrderStatus(ViewCapture):

    @ajaxProcess
    def ajax_form(self, request, frmName, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None, bbox=None):
        fs, form = self.processInitForm(request, frmName)
        menuEntry = [ x for x in self.MENU_ITEMS if x['name'] == 'woStatus' ][0]
        form = { 'name':  menuEntry['name']
               , 'label': menuEntry['label']
               , 'desc':  'Change the status of Work Orders'
               , 'flds':  []
               }
        self.appendUser(request, fs, form)
        return self.processFini(request, fs, form, msgType=msgType, msg=msg)

    def createField_workOrderList(self, listItems=[], value=None, msgType=ViewCapture.FLD_MSG_TYPE_NONE, msg=None):
        return self.listView('workOrderList', 'Work Orders', listItems, value=value, msgType=msgType, msg=msg)


    def gotUser(self, request, fs, form, flds, fld):
        self.fldsAppend(True, flds, self.createField_done())
        self.fldsAppend(False, flds, self.createField_woot())
        listItems = self.get_workOrderList(fs, recentOnly=True)
        if listItems:
            self.fldsAppend(True, flds, self.createField_workOrderList(listItems=listItems, value=self.get_workOrderStatusList(fs)))


    @ajaxProcess
    def ajax_fld_woot(self, request, frmName, fldName=None, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None):
        fs, form, flds, fldIdx, fld, woot = self.processInitFld(request, frmName, fldName)

        woList = self.get_workOrderList(fs, wildCard=woot)
        wosList = self.get_workOrderStatusList(fs)

        fld['value'] = woot
        fld['msgType'] = self.FLD_MSG_TYPE_VALID
        fld['msg'] = "Found: {} work-orders".format(len(woList))
        if len(woList):
            self.fldsAppend(False, flds, self.createField_workOrderList(listItems=woList, value=wosList))
        return self.processFini(request, fs, form)


    @ajaxProcess
    def ajax_status(self, request, frmName, ):
        fs, form, flds, parms = self.processInit(request, frmName)

        woo_auto_key, wos_auto_key, si_number = parms
        q = """ begin
                    aqcCaptureQC.authUserSession(:user_id);
                    update wo_operation
                       set wos_auto_key = {wos_auto_key}
                     where woo_auto_key = {woo_auto_key};
                    commit;
                end;
            """.format( wos_auto_key = wos_auto_key
                      , woo_auto_key = woo_auto_key
                      )
        rc = dbExecute(None, q, fs)

        msg = "{} status changed".format(si_number)

        response = ['okay']
        return self.processFini(request, fs, form, payload=response, msgType=self.FORM_MSG_TYPE_TX_COMPLETE, msg=msg)


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
                   , symptom as (
                         select distinct WSL.woo_auto_key as WSL_woo_auto_key
                              , first_value(DBMS_LOB.substr(WSL.notes, 512) ignore nulls) over
                                   (partition by WSL.woo_auto_key order by WSL.sequence, WSL.wsl_auto_key) as WSL_firstNote
                           from wo_symptom_list WSL
                         )
                select distinct --needed as parts of where clause are optional
                       WOO.woo_auto_key                   as "woo_auto_key"
                     , WOO.si_number                      as "si_number"
                     , PNM.pn                             as "partNumber"
                     , PNM.description                    as "partDesc"
                     , nvl(symptom.WSL_firstNote, '')     as "symptom"
                     , nvl(WOS.wos_auto_key,  0)          as "wos_auto_key"
                     , nvl(WOS.description,   'Pending')  as "wos_statusDesc"
                  from wo_operation     WOO
                     , wo_task          WOT
                     , parts_master     PNM
                     , wo_status        WOS
                     , recentWorkOrder  recent
                     , symptom          symptom
                 where WOO.woo_auto_key = WOT.woo_auto_key
                   and WOO.pnm_auto_key = PNM.pnm_auto_key
                   and WOO.wos_auto_key = WOS.wos_auto_key (+)
                   and WOO.woo_auto_key = recent.woo_auto_key (+)
                   and WOO.woo_auto_key = symptom.WSL_woo_auto_key (+)
                   and WOO.open_flag = 'T'
                   {whereClause}
                 order by WOO.woo_auto_key
            """.format(whereClause=whereClause)
        recs, fldNames = dbFetchAll(None, q, fs, asDict=True)
        return recs


    def get_workOrderStatusList(self, fs):
        q = """ select wos_auto_key    as "wos_auto_key"
                     , description     as "description"
                  from wo_status
                 order by description
            """
        recs, fldNames = dbFetchAll(None, q, fs, asDict=True)
        return recs
