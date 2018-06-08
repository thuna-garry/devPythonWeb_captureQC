 /* global $, describe, it, expect, beforeEach, afterEach, spyOn, jasmine */
describe("jquery.mobile.toast", function() {
    "use strict";

    describe("widget", function() {
        var toast, $toast;

        beforeEach(function() {
            toast = $.mobile.toast;
        });

        it("should be available on the jQuery object", function() {
            expect(toast).toBeDefined();
        });

        it("should be destroyed", function() {
            $toast = toast({ message: "Foo" });
            $toast.destroy();
            expect($toast.$p).toBeNull();
            expect($toast.$c).toBeNull();
            expect($toast.$toast).toBeNull();
            expect($toast.timer).toBeNull();
        });
    });

    describe("property", function() {
        describe("version", function() {
            var version = "0.0.7";
            it("should be defined", function() {
                expect($.mobile.toast.version).toBeDefined();
            });
            it("should have a value", function() {
                expect($.mobile.toast.version).toEqual(version);
            });
        });

        describe("option", function() {
            var defaults = {
                message:        "",
                duration:       2000,
                position:       80,
                classOnOpen:    "",
                classOnClose:   "",
                beforeposition: null,
                afterclose:     null,
                afteropen:      null
            };
            var options = {
                message:        "Foo",
                duration:       5000,
                position:       50,
                classOnOpen:    "fooOpen",
                classOnClose:   "animated bounceInUp",
                beforeposition: function() {},
                afterclose:     function() {},
                afteropen:      function() {}
            };
            var toast, $toast = null;
            var cb;

            beforeEach(function() {
                $.mobile.toast.prototype.options.message =        defaults.message;
                $.mobile.toast.prototype.options.duration =       defaults.duration;
                $.mobile.toast.prototype.options.position =       defaults.position;
                $.mobile.toast.prototype.options.classOnOpen =    defaults.classOnOpen;
                $.mobile.toast.prototype.options.classOnClose =   defaults.classOnClose;
                $.mobile.toast.prototype.options.beforeposition = defaults.beforeposition;
                $.mobile.toast.prototype.options.afterclose =     defaults.afterclose;
                $.mobile.toast.prototype.options.afteropen =      defaults.afteropen;

                toast = $.mobile.toast;
                cb = jasmine.createSpy("cb");
                jasmine.clock().install();
            });

            afterEach(function() {
                $toast = null;
                jasmine.clock().uninstall();
            });

            describe("classOnClose", function() {
                it("should be defined", function() {
                    expect(toast.prototype.options.classOnClose).toBeDefined();
                });
                it("should have a default value", function() {
                    expect(toast.prototype.options.classOnClose).toEqual(defaults.classOnClose);
                });
                it("should have a new default value", function() {
                    toast.prototype.options.classOnClose = options.classOnClose;
                    expect(toast.prototype.options.classOnClose).toEqual(options.classOnClose);
                });
                it("...", function() {
                    $toast = toast({ message: "foo", beforeClose: cb, classOnClose: options.classOnClose });
                    expect(cb).not.toHaveBeenCalled();
                    jasmine.clock().tick(2001);
                    expect(cb).toHaveBeenCalled();
                });
            });

            describe("classOnOpen", function() {
                it("should be defined", function() {
                    expect(toast.prototype.options.classOnOpen).toBeDefined();
                });
                it("should have a default value", function() {
                    expect(toast.prototype.options.classOnOpen).toEqual(defaults.classOnOpen);
                });
                it("should have a new default value", function() {
                    toast.prototype.options.classOnOpen = options.classOnOpen;
                    expect(toast.prototype.options.classOnOpen).toEqual(options.classOnOpen);
                });
            });

            describe("duration", function() {
                it("should be defined", function() {
                    expect(toast.prototype.options.duration).toBeDefined();
                });
                it("should have a default value", function() {
                    expect(toast.prototype.options.duration).toEqual(defaults.duration);
                });
                it("should have a new default value", function() {
                    toast.prototype.options.duration = options.duration;
                    expect(toast.prototype.options.duration).toEqual(options.duration);
                });
                it("should parse value", function() {
                    $toast = toast({ message: "foo", duration: "short" });
                    expect($toast.option("duration")).toEqual(2500);
                    $toast.option("duration", "long");
                    expect($toast.option("duration")).toEqual(3500);
                    $toast.option("duration", "foo");
                    expect($toast.option("duration")).toEqual(2000);
                    $toast.option("duration", 1000);
                    expect($toast.option("duration")).toEqual(1000);
                });
            });

            describe("message", function() {
                it("should be defined", function() {
                    expect(toast.prototype.options.message).toBeDefined();
                });
                it("should have a default value", function() {
                    expect(toast.prototype.options.message).toEqual(defaults.message);
                });
                it("should have a new default value", function() {
                    toast.prototype.options.message = options.message;
                    expect(toast.prototype.options.message).toEqual(options.message);
                });
                it("should parse value", function() {
                    $toast = toast({ message: "foo" });
                    expect($toast.option("message")).toEqual("foo");
                    $toast.option("message", "   foo    ");
                    expect($toast.option("message")).toEqual("foo");
                    $toast.option("message", "");
                    expect($toast.option("message")).toEqual("foo");
                });
            });

            describe("position", function() {
                it("should be defined", function() {
                    expect(toast.prototype.options.position).toBeDefined();
                });
                it("should have a default value", function() {
                    expect(toast.prototype.options.position).toEqual(defaults.position);
                });
                it("should have a new default value", function() {
                    toast.prototype.options.position = options.position;
                    expect(toast.prototype.options.position).toEqual(options.position);
                });
                it("should parse value", function() {
                    $toast = toast({ position: "top" });
                    expect($toast.option("position")).toEqual(20);
                    $toast.option("position", "center");
                    expect($toast.option("position")).toEqual(50);
                    $toast.option("position", "bottom");
                    expect($toast.option("position")).toEqual(80);
                    $toast.option("position", "foo");
                    expect($toast.option("position")).toEqual(80);
                    $toast.option("position", 60);
                    expect($toast.option("position")).toEqual(60);
                });
            });

            describe("afteropen", function() {
                it("should be called after toast opened", function() {
                    $toast = toast({ message: "foo", afteropen: cb });
                    expect(cb).toHaveBeenCalled();
                });
            });

            describe("beforeposition", function() {
                it("should be called before position", function() {
                    $toast = toast({ message: "foo", beforeposition: cb });
                    expect(cb).toHaveBeenCalled();
                });
            });

            describe("beforeClose", function() {
                it("should be called before toast closed", function() {
                    $toast = toast({ message: "foo", beforeClose: cb });
                    expect(cb).not.toHaveBeenCalled();
                    jasmine.clock().tick(2001);
                    expect(cb).toHaveBeenCalled();
                });
            });

            describe("afterclose", function() {
                it("should be called after toast closed", function() {
                    $toast = toast({ message: "foo", afterclose: cb });
                    expect(cb).not.toHaveBeenCalled();
                    jasmine.clock().tick(2001);
                    expect(cb).toHaveBeenCalled();
                });
            });
        });
    });
});
