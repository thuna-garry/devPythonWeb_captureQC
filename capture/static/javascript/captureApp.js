/* Copyright AdvanceQC LLC 2014,2015.  All rights reserved */

var captureApp = angular.module('captureApp', [ 'ngLoadingSpinner', 'ngIdle' ])
        //.factory('redirectInterceptor', function($q) {
        //    return {
        //        'request': function(response) {
        //            if (typeof response.data === 'string') {
        //                if (response.data.indexOf instanceof Function &&
        //                    response.data.indexOf('<html id="ng-app" ng-app="loginApp">') != -1) {
        //                        $location.path("/logout");
        //                    window.location = url + "logout"; // just in case
        //                }
        //            }
        //            return response;
        //        }
        //    };
        //})
        .config(['$httpProvider', /*'IdleProvider', 'KeepaliveProvider',*/ function($httpProvider/*, IdleProvider, KeepaliveProvider*/) {
            $httpProvider.defaults.headers.common['X-CSRFToken'] = getCookie('csrftoken');
            $httpProvider.defaults.headers.common['AQC_TZ_OFFSET'] = new Date().getTimezoneOffset();
            //$httpProvider.interceptors.push('redirectInterceptor');
            //IdleProvider.idle(5); // in seconds
            //IdleProvider.timeout(5); // in seconds
            //KeepaliveProvider.interval(2); // in seconds
        }])
        .run( function(){
            //stuff to do when app starts
        })
        .directive('aqcKeyedAdvance', function () {
            return function (scope, element, attrs) {
                element.bind("keydown keypress", function (event) {
                    if(event.which === 13 || event.which === 9) {
                        scope.$apply(function (){
                             scope.$eval(attrs.aqcKeyedAdvance);
                        });
                        event.preventDefault();
                    }
                });
            };
         })
        .directive('aqcSelectOnFocus', function () {
            return {
                restrict: 'A',
                link: function (scope, element) {
                    element.on('focus', function () {
                            this.select();
                    });
                }
            };
         })
        .directive('aqcTapHold', function () {
            return {
                restrict: 'A',
                link: function (scope, element, attrs) {
                    element.bind('taphold', function (event) {
                        scope.$apply(function (){
                             scope.$eval(attrs.aqcTapHold);
                        });
                        event.preventDefault();
                    });
                }
            };
         })
        .directive('aqcIdle', ['Idle', function(Idle) {
            return {
                restrict: 'EA',
                scope: {
                    aqcIdle:    '@',
                    aqcTimeout: '@'
                },
                link: function(scope, element, attrs) {
                    Idle.setIdle(parseInt(scope.aqcIdle));
                    Idle.setTimeout(parseInt(scope.aqcTimeout));
                }
            };
         }])
        .directive('aqcClock', ['dateFilter', '$timeout', function(dateFilter, $timeout){
            return {
                restrict: 'E',
                scope: {
                    format: '@'
                },
                link: function(scope, element, attrs){
                    var updateTime = function(){
                        var now = Date.now();
                        element.html(dateFilter(now, scope.format));
                        $timeout(updateTime, now % 1000);
                    };
                    updateTime();
                }
            };
        }])
        .filter('unsafe', ['$sce', function($sce) {
            return function(val) {
                return $sce.trustAsHtml(val);
            };
        }])
    ;
