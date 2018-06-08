/* Copyright AdvanceQC LLC 2014,2015.  All rights reserved */

var aqcUtils = aqcUtils || {};
aqcUtils.monthNamesShort = ['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
aqcUtils.monthNamesLong  = ['','January','February','March','April','May','June','July','August','September','October','November','December'];

aqcUtils.getYearLookupList = function(dateTuple) {
    var items = [];
    for	(i = 0; i < 25; i++) {
        var y = dateTuple.y - 3 + i;
        items[i] = {"seq": y, "code": "y"+y, "desc": y};
    }
    return items;
};

aqcUtils.getMonthLookupList = function(dateTuple) {
    var items = [];
    for	(i = 0; i < 12; i++) {
        items[i] = {"seq":(i+1), "code":"m"+(i+1), "desc":aqcUtils.monthNamesLong[i+1]};
    }
    return items;
};

aqcUtils.getDayLookupList = function(dateTuple) {
    var daysInMonth = new Date(dateTuple.y, dateTuple.m, 0).getDate();
    var items = [];
    for	(i = 0; i < daysInMonth; i++)
        items[i] = {"seq":(i+1), "code":"d"+(i+1), "desc":(i+1)};
    return items;
};

aqcUtils.getFldIdx = function(form, fldName) {
    if (form == undefined)
        return (-1);
    for (var i = form.flds.length - 1; i >= 0; i--) {
        if (form.flds[i]['name'] == fldName)
            return (i);
    }
    return (-1);
};

aqcUtils.getFldType = function(form, fldName) {
    if (form == undefined)
        return null;
    for (var i = form.flds.length - 1; i >= 0; i--) {
        if (form.flds[i]['name'] == fldName)
            return form.flds[i]['type'];
    }
    return (-1);
};

aqcUtils.getFldAttr = function(form, fldName, attr) {
    fldIdx = aqcUtils.getFldIdx(form, fldName);
    if (fldIdx < 0)
        return null;
    return form.flds[fldIdx][attr];
};

function parseErrorResponse(data) {
    var regex = /^\n$/m;
    if (regex.test(data) )
        return JSON.parse(data.split(regex)[1]);
    else
        return data;
}
