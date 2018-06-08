/* Copyright AdvanceQC LLC 2014,2015.  All rights reserved */

function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length == 2) return parts.pop().split(";").shift();
}

function defaultFor(arg, val) {
    return typeof arg !== 'undefined' ? arg : val;
}

function showErrDialog() {
    showPopupDialog("dialogError");
}
function showPopupDialog(domId) {
    $("#" + domId).css('width', '85vw');
    $("#" + domId).css('display', '');
    $("#" + domId).trigger('create');
    $("#" + domId).popup();
    $("#" + domId).popup('open', {positionTo: "window", transition: "pop"});
}
function hidePopupDialog(domId) {
    $("#" + domId).popup('close');
    $("#" + domId).css('display', 'none');
}

function cssTransform(elem, txfm) {
    elem.css('transform',         txfm);
    elem.css('-webkit-transform', txfm);
    elem.css('-moz-transform',    txfm);
    elem.css('-o-transform',      txfm);
    elem.css('-ms-transform',     txfm);
}

function cssScale(elem, scale) {
    var txfm = 'scale(' + scale + ')';
    cssTransform(elem, txfm);
}