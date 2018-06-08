/* Copyright AdvanceQC LLC 2014,2015.  All rights reserved */

F_URI = "/capture/form/";

captureApp.controller('captureFormStockUndoCtrl', ['$scope', '$http', 'Idle', function ($scope, $http, Idle) {
          $scope.aqcUtils = aqcUtils;
          $scope.events = [];
          $scope.$on('IdleStart',   function()             { showPopupDialog('idleDetected');                           });
          $scope.$on('IdleWarn',    function(e, countdown) { $('#idleCountdown').html('Reset in ' + countdown + 's')    });
          $scope.$on('IdleTimeout', function()             { $('#idleCountdown').html('Reloading...'); $scope.reload(); });
          $scope.$on('IdleEnd',     function()             { hidePopupDialog('idleDetected');                           });
          $scope.$on('Keepalive',   function()             {});

          $scope.init = function(formName) {
                     $scope.hideDesc = false;
                     if (formName)
                         ajaxRequest(formName);
                 };
          $scope.reload = function(formName) {
                     formName = formName || $scope.form.name;
                     window.location.href = formName + ".html";
                 };
          $scope.gotFocus = function(fldIdx) {   //remove all fields after the currently focused field
                     if ($scope.form.flds[fldIdx].w2cm == 2)
                         $scope.form.flds[fldIdx].msg = "";
                     trimFlds(fldIdx);
                 };
          function trimFlds(fldIdx) {
              var length = $scope.form.flds.length;
              if ((!$scope.form.flds[fldIdx].group) ||
                  (length - 1 > fldIdx && $scope.form.flds[fldIdx].group != $scope.form.flds[fldIdx + 1].group )
                 )
                  $scope.form.flds.length = fldIdx + 1;
          }
          $scope.change = function(fldIdx) {
                     Idle.watch();
                     $scope.formMsg = "";
                     if ($scope.form.flds[fldIdx].w2cm == 1)
                         $scope.form.flds[fldIdx].msg = "";
                     $scope.form.flds[fldIdx].dirty = true;
                 };
          $scope.entryDone = function(fldIdx, forceDirty) {
                     if (fldIdx > $scope.form.flds.length -1)
                         return;  //field no longer exists
                     forceDirty = forceDirty || false;
                     if (!( $scope.form.flds[fldIdx].dirty || forceDirty))
                         return;   //field is unchanged
                     $scope.form.flds[fldIdx].dirty = false;
                     if ($scope.form.flds[fldIdx].w2cm == 3)
                         $scope.form.flds[fldIdx].msg = "";
                     ajaxRequest($scope.form.name, $scope.form.flds[fldIdx].name, {
                         'value': $scope.form.flds[fldIdx].value
                     });
                 };
          $scope.detailShow = function(fldName, proc, curItem) {
                     $scope.formMsg = "";
                     $scope.curItem = curItem;
                     $scope.curIdx = aqcUtils.getFldIdx($scope.form, fldName);
                     $http.post(F_URI + $scope.form.name + "/" + proc, curItem).success(good).error(bad);
                     function good(data, status, headers, config) {
                         if (data[0] == '!flds') {
                             $scope.form.flds.push.apply($scope.form.flds, data[3]);
                         } else {
                             $scope.curItemDetail = data[0];
                         }
                         $("body").pagecontainer("change", "#pageItemDetail", { /*role:'dialog',*/ transition: "slidedown" });
                         setTimeout(function () { $("#pageItemDetail").trigger('create');
                                                  $(".ui-listview").listview("refresh");
                                                } , 0);
                         postAjax();
                     }
                 };
          $scope.detEntryDone = function(fldIdx, forceDirty) {
                     if (fldIdx > $scope.form.flds.length -1)
                         return;  //field no longer exists
                     forceDirty = forceDirty || false;
                     if (!( $scope.form.flds[fldIdx].dirty || forceDirty))
                         return;   //field is unchanged
                     $scope.form.flds[fldIdx].dirty = false;
                     if ($scope.form.flds[fldIdx].w2cm == 3)
                         $scope.form.flds[fldIdx].msg = "";
                     $http.post(F_URI + $scope.form.name + "/fld_" +  $scope.form.flds[fldIdx].name, { 'stkTiItem': $scope.curItem
                                                                                                     , 'value':$scope.form.flds[fldIdx].value
                                                                                                     }).success(good).error(bad);
                     function good(data, status, headers, config) {
                         if (data[0] == '!flds') {
                             trimFlds($scope.curIdx);
                             $scope.form.flds.push.apply($scope.form.flds, data[3]);
                         } else {
                             $.mobile.back();
                             $scope.form = data[0]; $scope.formMsgType = data[1]; $scope.formMsg = data[2]; $scope.bbox = data[3];
                         }
                         postAjax();
                     }
                 };
          $scope.detailCancel = function() {
                     $.mobile.back();
                     trimFlds($scope.curIdx);
                 };

          function ajaxRequest(formName, fldName, postData) {
              if (typeof fldName  === 'undefined') {
                  $http.get(F_URI + formName).success(good).error(bad);
              } else {
                  $http.post(F_URI + $scope.form.name + "/fld_" + fldName, postData).success(good).error(bad);
              }
              function good(data, status, headers, config) {
                  $scope.form = data[0]; $scope.formMsgType = data[1]; $scope.formMsg = data[2]; $scope.bbox = data[3];
                  postAjax();
              }
          }

          function bad(data, status, headers, config) {
              data = parseErrorResponse(data);
              if ('redirectTo' in data)
                  window.location.replace(data['redirectTo']);
              else {
                  $scope.errDialog = data;
                  showErrDialog();
              }
          }

          function postAjax() {
              setTimeout(function () {
                  var lastId = "#" + $scope.form.name + "-" + $scope.form.flds[$scope.form.flds.length -1].name;
                  $(".ajaxLoaded").trigger('create');
                  $(lastId).focus();
              }, 0);
          }
}]);
