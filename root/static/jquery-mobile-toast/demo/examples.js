/* jshint devel: true */
"use strict";

$( document ).on( "pageinit", "#demoPage", function( event ) {

    $("#default").on("tap", function() {
        $.mobile.toast({
            message: "Live long and prosper!"
        });
    });

    $("#longer").on("tap", function() {
        $.mobile.toast({
            message: "Live long and prosper!",
            duration: "long"
        });
    });

    $("#top").on("tap", function() {
        $.mobile.toast({
            message: "Live long and prosper!",
            position: "top"
        });
    });

    $("#center").on("tap", function() {
        $.mobile.toast({
            message: "Live long and prosper!",
            position: "center"
        });
    });

    $("#bottom").on("tap", function() {
        $.mobile.toast({
            message: "Live long and prosper!",
            position: "bottom"
        });
    });

    $("#custom").on("tap", function() {
        $.mobile.toast({
            message: "Live long and prosper!",
            classOnOpen: "pomegranate"
        });
    });

    $("#custom-kitkat").on("tap", function() {
        $.mobile.toast({
            message: "Live long and prosper!",
            classOnOpen: "kitkat"
        });
    });

    $("#close-event").on("tap", function() {
        $.mobile.toast({
            message: "Live long and prosper!",
            afterclose: function(event, ui) {
                alert("Toast closed!");
            }
        });
    });

    $("#animate-css").on("tap", function() {
        $.mobile.toast({
            message: "Live long and prosper!",
            classOnOpen: "animated bounceInUp"
        });
    });

    $("#animate-css2").on("tap", function() {
        $.mobile.toast({
            message: "Live long and prosper!",
            classOnOpen: "animated slideInLeft",
            classOnClose: "slideOutRight"
        });
    });

});
