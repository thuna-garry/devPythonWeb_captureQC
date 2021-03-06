'use strict';

describe('ngIdle', function() {
  // helpers
  beforeEach(function() {
    this.addMatchers({
      toEqualData: function(expected) {
        return angular.equals(this.actual, expected);
      }
    });
  });

  beforeEach(module('ngIdle.localStorage'));

  describe('LocalStorage service', function() {
    beforeEach(function() {
      angular.module('app', function() {});
    });

    var $window, LocalStorage;
    beforeEach(inject(function(_$window_, _LocalStorage_) {
      $window = _$window_;
      LocalStorage = _LocalStorage_;

      spyOn($window.localStorage, 'setItem').andCallThrough();
    }));

    it ('set() should set value', function() {
      LocalStorage.set('key', 1);
      expect($window.localStorage.setItem).toHaveBeenCalledWith('ngIdle.key', '1');
    });

    it ('get() should retrieve value as JSON', function() {
      spyOn($window.localStorage, 'getItem').andReturn('{"value": 1}');
      var actual = LocalStorage.get('key');
      expect(actual).toEqualData({value:1});
    });

    it ('get() should retrieve value as string', function() {
      spyOn($window.localStorage, 'getItem').andReturn('test');
      var actual = LocalStorage.get('key');
      expect(actual).toEqualData('test');
    });

    it ('get() should retrieve value as date', function() {
      var expected = new Date();
      var raw = JSON.stringify(expected);
      spyOn($window.localStorage, 'getItem').andReturn(raw);
      
      var actual = LocalStorage.get('key');
      expect(actual).toEqual(expected);
    });

    it ('remove() should remove key/value', function() {
      spyOn($window.localStorage, 'removeItem');
      LocalStorage.remove('key');
      expect($window.localStorage.removeItem).toHaveBeenCalledWith('ngIdle.key');
    });
  });
});
