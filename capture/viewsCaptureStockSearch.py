"""
Copyright AdvanceQC LLC 2014,2015.  All rights reserved
"""

import re

from django.core.urlresolvers import reverse

from aqclib.dbUtils import dbConnection, dbQuote, dbFetchOne, dbFetchAll, dbExecute

from viewUtils    import jsonRedirect
from viewsCapture import ViewCapture, ajaxProcess


#############################################################################
# ViewCaptureStockSearch
#############################################################################
class ViewCaptureStockSearch(ViewCapture):

    @ajaxProcess
    def ajax_form(self, request, frmName, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None, bbox=None):
        fs, form = self.processInitForm(request, frmName)
        menuEntry = [ x for x in self.MENU_ITEMS if x['name'] == 'stockSearch' ][0]
        form = { 'name':  menuEntry['name']
               , 'label': menuEntry['label']
               , 'desc':  'Find/Confirm part numbers, or stock and availability.'
               , 'flds':  [ self.createField_partOrStock() ]
               }
        return self.processFini(request, fs, form, msgType=msgType, msg=msg)

    def createField_partOrStock(self, value=None, msgType=ViewCapture.FLD_MSG_TYPE_NONE, msg=None):
        return self.lineEdit('partOrStock', 'Part/Stock', length=40, size=12, prompt="Part or Control", value=value, msgType=msgType, msg=msg)

    def createField_partList(self, listItems=[], value=None, msgType=ViewCapture.FLD_MSG_TYPE_NONE, msg=None):
        return self.listView('partList', 'Parts', listItems, value=value, msgType=msgType, msg=msg)

    @ajaxProcess
    def ajax_fld_partOrStock(self, request, frmName, fldName=None, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None):
        fs, form, flds, fldIdx, fld, data = self.processInitFld(request, frmName, fldName)

        # is it a control No/Id
        whereClause = None
        ctrlNo = None; ctrlId = None
        if re.match('[0-9]{12}$', data):
            ctrlNo = data[:6]
            ctrlId = data[6:]
        elif re.match('[0-9]{1,6}[,. ][0-9]{1,6}$', data):
            ctrlNo, ctrlId = re.split('[,. ]', data)

        if ctrlNo:
            q = """ select STM.pnm_auto_key
                      from stock STM
                     where STM.ctrl_number = :ctrlNo
                       and STM.ctrl_id = :ctrlId  """
            row, fldNames = dbFetchOne(None, q, dict(ctrlNo=ctrlNo, ctrlId=ctrlId))
            if row:
                fs['pnm_auto_key'], = row
                whereClause = "PNM.pnm_auto_key = :pnm_auto_key"

        if not whereClause:
            whereClause = "1=2 "
            if re.match('[0-9]+$', data):    # it's all numeric
                whereClause += " or PNM.pnm_auto_key = {0} ".format(data)
                whereClause += " or PNM.pn_stripped like '{1}{0}{1}' ".format(dbQuote(data), '%')
            elif re.search('[\w]', data):      # it has at least one alphanumeric character
                whereClause += " or upper(PNM.pn_stripped) like upper('{1}{0}{1}') ".format(re.sub('[\W_]+', '', data), '%')
                whereClause += " or upper(PNM.description) like upper('{1}{0}{1}') ".format(re.sub('[\W_]+', '', data), '%')

        q = """ with cq as (  select CQD.pnm_auto_key
                                   , CQD.unit_price
                                   , CQD.entry_date
                                from cq_detail    CQD
                                   , parts_master PNM
                               where CQD.pnm_auto_key = PNM.pnm_auto_key
                                 and ({whereClause})
                                 and CQD.cqd_auto_key = ( select max(cqd_auto_key)
                                                            from cq_detail
                                                           where pnm_auto_key = PNM.pnm_auto_key
                                                        )
                           ),
                     so as (  select SOD.pnm_auto_key
                                   , SOD.unit_price
                                   , SOD.entry_date
                                from so_detail    SOD
                                   , parts_master PNM
                               where SOD.pnm_auto_key = PNM.pnm_auto_key
                                 and ({whereClause})
                                 and SOD.sod_auto_key = ( select max(sod_auto_key)
                                                            from so_detail
                                                           where pnm_auto_key = PNM.pnm_auto_key
                                                        )
                           )
                select pnm_auto_key    as "pnm_auto_key"
                     , pn              as "pn"
                     , description     as "desc"
                     , qty_oh          as "qtyOH"
                     , qty_reserved    as "qtyRes"
                     , qty_available   as "qtyAvail"
                     , salePrice       as "salePrice"
                     , saleDate        as "saleDate"
                     , quotePrice      as "quotePrice"
                     , quoteDate       as "quoteDate"
                from ( select PNM.pnm_auto_key
                            , PNM.pn
                            , PNM.description
                            , to_char(PNM.qty_oh)        as qty_oh
                            , to_char(PNM.qty_reserved)  as qty_reserved
                            , to_char(PNM.qty_available) as qty_available
                            , nvl(to_char(SO.unit_price), '-') as salePrice,  nvl(to_char(SO.entry_date, 'yyyy-mm-dd'), '-') as saleDate
                            , nvl(to_char(CQ.unit_price), '-') as quotePrice, nvl(to_char(CQ.entry_date, 'yyyy-mm-dd'), '-') as quoteDate
                         from parts_master PNM
                            , so           SO
                            , cq           CQ
                        where 1=1
                          and PNM.pnm_auto_key = SO.pnm_auto_key (+)
                          and PNM.pnm_auto_key = CQ.pnm_auto_key (+)
                          and ({whereClause})
                        order by pn
                     )
                 where rownum < 100
            """.format(whereClause=whereClause)

        recs, fldNames = dbFetchAll(None, q, fs, asDict=True)
        if not recs:
            fld['value'] = data
            fld['msgType'] = self.FLD_MSG_TYPE_INVALID
            fld['msg'] = "No Part Found"
            return self.processFini(request, fs, form)

        fld['value'] = data
        fld['msgType'] = self.FLD_MSG_TYPE_VALID
        fld['msg'] = ""
        self.fldsAppend(False, flds, self.createField_done())
        self.fldsAppend(False, flds, self.createField_print())
        self.fldsAppend(False, flds, self.createField_partList(listItems=recs))
        return self.processFini(request, fs, form)


    @ajaxProcess
    def ajax_getStockList(self, request, frmName, fldName=None, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None):
        fs, form, flds, part = self.processInit(request, frmName)

        q = """ select STM.stm_auto_key                     as "stm_auto_key"
                     , STM.serial_number                    as "serialNumber"
                     , to_char(STM.exp_date, 'yyyy-mm-dd')  as "expDate"
                     , STM.receiver_number                  as "receiverNumber"
                     , STM.original_po_number               as "poNum"
                     , to_char(STM.qty_oh)                  as "qtyOH"
                     , to_char(STM.qty_reserved)            as "qtyRes"
                     , to_char(STM.qty_available)           as "qtyAvail"
                     , WHS.warehouse_code                   as "warehouseCode"
                     , LOC.location_code                    as "locationCode"
                     , nvl(PCC.condition_code, '-')         as "conditionCode"
                     , to_char(STM.unit_cost)               as "unitCost"
                     , to_char(STM.rec_date, 'yyyy-mm-dd')  as "recDate"
                     , STM.ctrl_number                      as "ctrlNo"
                     , STM.ctrl_id                          as "ctrlId"
                  from stock                 STM
                     , location              LOC
                     , warehouse             WHS
                     , part_condition_codes  PCC
                 where STM.whs_auto_key = WHS.whs_auto_key (+)
                   and STM.loc_auto_key = LOC.loc_auto_key (+)
                   and STM.pcc_auto_key = PCC.pcc_auto_key (+)
                   and STM.pnm_auto_key = :pnm_auto_key
                   and STM.historical_flag = 'F'
            """
        recs, fldNames = dbFetchAll(None, q, part, asDict=True)
        return self.processFini(request, fs, form, payload=recs)


    @ajaxProcess
    def ajax_fld_print(self, request, frmName, fldName=None, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None):
        fs, form, flds, fldIdx, fld, stmAutoKey = self.processInitFld(request, frmName, fldName)

        request.session['stock.stmAutoKey'] = stmAutoKey
        uri = reverse('capture:stockLabel', kwargs=dict(frmName='stockLabel')) + '.html'
        return jsonRedirect(dict(redirectTo=uri), 'Printing...')

