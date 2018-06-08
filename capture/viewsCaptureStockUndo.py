"""
Copyright AdvanceQC LLC 2014,2015.  All rights reserved
"""

import re

from aqclib         import utils
from aqclib.dbUtils import dbConnection, dbQuote, dbFetchOne, dbFetchAll, dbExecute

from viewsCapture import ViewCapture, ajaxProcess


#############################################################################
# ViewCaptureStockIssue
#############################################################################
class ViewCaptureStockUndo(ViewCapture):

    @ajaxProcess
    def ajax_form(self, request, frmName, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None, bbox=None):
        fs, form = self.processInitForm(request, frmName)
        menuEntry = [ x for x in self.MENU_ITEMS if x['name'] == 'stockUndo' ][0]
        form = { 'name':  menuEntry['name']
               , 'label': menuEntry['label']
               , 'desc':  'Return excess issued stock, or take back a stock turn-in.'
               , 'flds':  []
               }
        self.appendUser(request, fs, form)
        return self.processFini(request, fs, form, msgType=msgType, msg=msg)

    def createField_partOrStock(self, value=None, msgType=ViewCapture.FLD_MSG_TYPE_NONE, msg=None):
        return self.lineEdit('partOrStock', 'Part/Stock', length=40, size=12, prompt="Part or Control", value=value, msgType=msgType, msg=msg, group=1)

    def createField_stockTiList(self, listItems=[], value=None, msgType=ViewCapture.FLD_MSG_TYPE_NONE, msg=None):
        return self.listView('stockTiList', 'TurnIn/Issue', listItems, value=value, msgType=msgType, msg=msg, group=1)

    def createField_undoQty(self, value=None, msgType=ViewCapture.FLD_MSG_TYPE_NONE, msg=None):
        return self.lineEdit('undoQty', 'Undo', 8, prompt="Quantity", value=value, msgType=msgType, msg=msg, w2cm=self.W2CM_EDIT_DONE)


    def gotUser(self, request, fs, form, flds, fld):
        self.fldsAppend(False, flds, self.createField_done())
        self.fldsAppend(False, flds, self.createField_woot())

    def gotWot(self, request, fs, form, flds, fld):
        self.fldsAppend(False, flds, self.createField_partOrStock())
        self.fldsAppend(True,  flds, self.createField_stockTiList(listItems=self.get_stockTiList(fs)))


    @ajaxProcess
    def ajax_fld_partOrStock(self, request, frmName, fldName=None, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None):
        fs, form, flds, fldIdx, fld, data = self.processInitFld(request, frmName, fldName)

        fs['partOrStockFilter'] = data.strip()
        recs = self.get_stockTiList(fs)
        fld['value'] = data
        fld['msgType'] = self.FLD_MSG_TYPE_NONE
        fld['msg'] = ""
        self.fldsAppend(True, flds, self.createField_stockTiList(listItems=recs))
        return self.processFini(request, fs, form)


    def ajax_getUndoForm(self, request, frmName, fldName=None, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None):
        fs, form, flds, stiData = self.processInit(request, frmName)

        qtyFld = self.createField_undoQty(msgType=self.FLD_MSG_TYPE_NONE, msg="max: {}".format(stiData['tiQty']))
        return self.processFini(request, fs, form, payload="!flds", bbox=[qtyFld])


    def ajax_fld_undoQty(self, request, frmName, fldName=None, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None):
        fs, form, flds, data = self.processInit(request, frmName)

        undoQty = data['value']
        stkTiItem = data['stkTiItem']

        q = """ declare
                    cur  qc_utl_pkg.cursor_type;
                begin
                    aqcCaptureQC.authUserSession(:user_id);
                    cur := qc_ic_pkg2.spi_issue_reverse ( p_sti      => {sti_auto_key}
                                                        , p_qty      => {undoQty}
                                                        , p_commit   => 'N'
                                                        );
                    commit;
                end;
            """.format( sti_auto_key = stkTiItem['sti_auto_key']
                      , undoQty      = undoQty
                      )
        rc = dbExecute(None, q, fs)

        # refresh the stockTiList
        self.fldsAppend(True, flds, self.createField_stockTiList(listItems=self.get_stockTiList(fs)))

        return self.processFini(request, fs, form, msgType=self.FORM_MSG_TYPE_TX_COMPLETE, msg="Stock activity adjusted")


    #--------------------------------------------------
    #- convenience routines
    #--------------------------------------------------
    def get_stockTiList(self, fs):

        whereClause = ""
        if fs.get('wot_auto_key'):
            whereClause += " and (WOT.wot_auto_key = :wot_auto_key)"

        if fs.get('partOrStockFilter'):
            filter = fs.get('partOrStockFilter')
            whereClause += " and (1=2"

            # is it a control No/Id
            ctrlNo = None; ctrlId = None
            if re.match('[0-9]{12}$', filter):
                ctrlNo = filter[:6]
                ctrlId = filter[6:]
            elif re.match('[0-9]{1,6}[,. ][0-9]{1,6}$', filter):
                ctrlNo, ctrlId = re.split('[,. ]', filter)
            if ctrlNo:
                whereClause += " or (STM.ctrl_number = {} and STM.ctrl_id = {})".format(ctrlNo, ctrlId)

            if re.match('[0-9]+$', filter):    # it's all numeric
                whereClause += " or PNM.pnm_auto_key = {0} ".format(filter)
                whereClause += " or PNM.pn_stripped like '{1}{0}{1}' ".format(dbQuote(filter), '%')
            elif re.search('[\w]', filter):      # it has at least one alphanumeric character
                whereClause += " or upper(PNM.pn_stripped) like upper('{1}{0}{1}') ".format(re.sub('[\W_]+', '', filter), '%')
                whereClause += " or upper(PNM.description) like upper('{1}{0}{1}') ".format(re.sub('[\W_]+', '', filter), '%')

            whereClause += ")"

        # ref: QC_WP_PKG.SPS_WP_STOCK_ACTIVITY
        q = """ select stm_auto_key                as "stm_auto_key"
                     , sti_auto_key                as "sti_auto_key"
                     , to_char(tiQty)              as "tiQty"
                     , activity                    as "activity"
                     , stockLine                   as "stockLine"
                     , partNum                     as "partNum"
                     , partDesc                    as "partDesc"
                     , partCond                    as "partCond"
                     , condLevel                   as "condLevel"
                     , tiType                      as "tiType"
                     , taskSeq                     as "taskSeq"
                     , taskDesc                    as "taskDesc"
                     , taskCode                    as "taskCode"
                     , serialNum                   as "serialNum"
                  from (  select STI.stm_auto_key
                               , STI.sti_auto_key
                               , case
                                     when     STI.ti_type = 'T'
                                          and nvl(STM.qty_available,0) + nvl((select sum(qty_reserved)
                                                                                from stock_reservations
                                                                               where wob_auto_key = WOB.wob_auto_key),0)
                                           < nvl(STI.qty,0) - nvl(STI.qty_reverse,0)
                                     then
                                              nvl(STM.qty_available,0) + nvl((select sum(qty_reserved)
                                                                                from stock_reservations
                                                                               where wob_auto_key = WOB.wob_auto_key),0)
                                     else
                                         nvl(STI.qty,0) - nvl(STI.qty_reverse,0)
                                 end                                               as tiQty
                               , QC_WP_PKG.get_wob_activity(WOB.activity)          as activity
                               , STM.stock_line                                    as stockLine
                               , PNM.pn                                            as partNum
                               , PNM.description                                   as partDesc
                               , PCC.condition_code                                as partCond
                               , WOB.cond_level                                    as condLevel
                               , DECODE(STI.ti_type, 'I', 'Issue', 'T', 'Turn-In') as tiType
                               , WOT.sequence                                      as taskSeq
                               , QC_WO_PKG2.get_taks_descr(WOB.wot_auto_key)       as taskDesc
                               , WTM.description                                   as taskCode
                               , STM.serial_number                                 as serialNum
                            from wo_bom               WOB
                               , wo_task              WOT
                               , wo_task_master       WTM
                               , wo_status            WOS
                               , part_condition_codes PCC
                               , stock_ti             STI
                               , parts_master         PNM
                               , stock                STM
                         where 1=1
                           and WOB.wot_auto_key = WOT.wot_auto_key (+)
                           and WOT.wtm_auto_key = WTM.wtm_auto_key (+)
                           and WOT.wos_auto_key = WOS.wos_auto_key (+)
                           and WOB.pcc_auto_key = PCC.pcc_auto_key (+)
                           and WOB.wob_auto_key = STI.wob_auto_key
                           and STI.stm_auto_key = STM.stm_auto_key (+)
                           and STM.pnm_auto_key = PNM.pnm_auto_key (+)
                           --
                           and WOB.woo_auto_key  = :woo_auto_key
                           and (   (NVL(WOS.status_type,'Pending') not in ('Closed','Cancel','Defer'))
                                or (WOS.closed_allow_inv = 'T' and QC_SC_PKG.get_has_access(20441/*qsICFuncStockMaterClosed*/) = 'T'))
                           and STI.ti_type  <> 'R'
                           {whereClause}
                         order by partNum
                                , taskSeq
                                , tiType
                       )
                 where tiQty > 0
                   and rownum < 100
            """.format(whereClause=whereClause)
        recs, fldNames = dbFetchAll(None, q, fs, asDict=True)
        return recs
