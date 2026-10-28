// Seite „Heimnetz“ – gebaut mit esbuild aus custom_components/heimnetz/frontend/src (nicht von Hand ändern)
var __create = Object.create;
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __getProtoOf = Object.getPrototypeOf;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __commonJS = (cb, mod) => function __require() {
  try {
    return mod || (0, cb[__getOwnPropNames(cb)[0]])((mod = { exports: {} }).exports, mod), mod.exports;
  } catch (e6) {
    throw mod = 0, e6;
  }
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toESM = (mod, isNodeMode, target) => (target = mod != null ? __create(__getProtoOf(mod)) : {}, __copyProps(
  // If the importer is in node compatibility mode or this is not an ESM
  // file that has been converted to a CommonJS file using a Babel-
  // compatible transform (i.e. "__esModule" has not been set), then set
  // "default" to the CommonJS "module.exports" for node compatibility.
  isNodeMode || !mod || !mod.__esModule ? __defProp(target, "default", { value: mod, enumerable: true }) : target,
  mod
));

// node_modules/leaflet/dist/leaflet.js
var require_leaflet = __commonJS({
  "node_modules/leaflet/dist/leaflet.js"(exports, module) {
    /* @preserve
     * Leaflet 1.9.4, a JS library for interactive maps. https://leafletjs.com
     * (c) 2010-2023 Vladimir Agafonkin, (c) 2010-2011 CloudMade
     */
    !(function(t7, e6) {
      "object" == typeof exports && "undefined" != typeof module ? e6(exports) : "function" == typeof define && define.amd ? define(["exports"], e6) : e6((t7 = "undefined" != typeof globalThis ? globalThis : t7 || self).leaflet = {});
    })(exports, function(t7) {
      "use strict";
      function l4(t8) {
        for (var e7, i7, n5 = 1, o8 = arguments.length; n5 < o8; n5++) for (e7 in i7 = arguments[n5]) t8[e7] = i7[e7];
        return t8;
      }
      var R2 = Object.create || function(t8) {
        return N2.prototype = t8, new N2();
      };
      function N2() {
      }
      function a3(t8, e7) {
        var i7, n5 = Array.prototype.slice;
        return t8.bind ? t8.bind.apply(t8, n5.call(arguments, 1)) : (i7 = n5.call(arguments, 2), function() {
          return t8.apply(e7, i7.length ? i7.concat(n5.call(arguments)) : arguments);
        });
      }
      var D2 = 0;
      function h3(t8) {
        return "_leaflet_id" in t8 || (t8._leaflet_id = ++D2), t8._leaflet_id;
      }
      function j2(t8, e7, i7) {
        var n5, o8, s5 = function() {
          n5 = false, o8 && (r6.apply(i7, o8), o8 = false);
        }, r6 = function() {
          n5 ? o8 = arguments : (t8.apply(i7, arguments), setTimeout(s5, e7), n5 = true);
        };
        return r6;
      }
      function H4(t8, e7, i7) {
        var n5 = e7[1], e7 = e7[0], o8 = n5 - e7;
        return t8 === n5 && i7 ? t8 : ((t8 - e7) % o8 + o8) % o8 + e7;
      }
      function u3() {
        return false;
      }
      function i6(t8, e7) {
        return false === e7 ? t8 : (e7 = Math.pow(10, void 0 === e7 ? 6 : e7), Math.round(t8 * e7) / e7);
      }
      function W3(t8) {
        return t8.trim ? t8.trim() : t8.replace(/^\s+|\s+$/g, "");
      }
      function F(t8) {
        return W3(t8).split(/\s+/);
      }
      function c4(t8, e7) {
        for (var i7 in Object.prototype.hasOwnProperty.call(t8, "options") || (t8.options = t8.options ? R2(t8.options) : {}), e7) t8.options[i7] = e7[i7];
        return t8.options;
      }
      function U(t8, e7, i7) {
        var n5, o8 = [];
        for (n5 in t8) o8.push(encodeURIComponent(i7 ? n5.toUpperCase() : n5) + "=" + encodeURIComponent(t8[n5]));
        return (e7 && -1 !== e7.indexOf("?") ? "&" : "?") + o8.join("&");
      }
      var V2 = /\{ *([\w_ -]+) *\}/g;
      function q(t8, i7) {
        return t8.replace(V2, function(t9, e7) {
          e7 = i7[e7];
          if (void 0 === e7) throw new Error("No value provided for variable " + t9);
          return e7 = "function" == typeof e7 ? e7(i7) : e7;
        });
      }
      var d3 = Array.isArray || function(t8) {
        return "[object Array]" === Object.prototype.toString.call(t8);
      };
      function G(t8, e7) {
        for (var i7 = 0; i7 < t8.length; i7++) if (t8[i7] === e7) return i7;
        return -1;
      }
      var K = "data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=";
      function Y(t8) {
        return window["webkit" + t8] || window["moz" + t8] || window["ms" + t8];
      }
      var X = 0;
      function J(t8) {
        var e7 = +/* @__PURE__ */ new Date(), i7 = Math.max(0, 16 - (e7 - X));
        return X = e7 + i7, window.setTimeout(t8, i7);
      }
      var $2 = window.requestAnimationFrame || Y("RequestAnimationFrame") || J, Q = window.cancelAnimationFrame || Y("CancelAnimationFrame") || Y("CancelRequestAnimationFrame") || function(t8) {
        window.clearTimeout(t8);
      };
      function x2(t8, e7, i7) {
        if (!i7 || $2 !== J) return $2.call(window, a3(t8, e7));
        t8.call(e7);
      }
      function r5(t8) {
        t8 && Q.call(window, t8);
      }
      var tt = { __proto__: null, extend: l4, create: R2, bind: a3, get lastId() {
        return D2;
      }, stamp: h3, throttle: j2, wrapNum: H4, falseFn: u3, formatNum: i6, trim: W3, splitWords: F, setOptions: c4, getParamString: U, template: q, isArray: d3, indexOf: G, emptyImageUrl: K, requestFn: $2, cancelFn: Q, requestAnimFrame: x2, cancelAnimFrame: r5 };
      function et() {
      }
      et.extend = function(t8) {
        function e7() {
          c4(this), this.initialize && this.initialize.apply(this, arguments), this.callInitHooks();
        }
        var i7, n5 = e7.__super__ = this.prototype, o8 = R2(n5);
        for (i7 in (o8.constructor = e7).prototype = o8, this) Object.prototype.hasOwnProperty.call(this, i7) && "prototype" !== i7 && "__super__" !== i7 && (e7[i7] = this[i7]);
        if (t8.statics && l4(e7, t8.statics), t8.includes) {
          var s5 = t8.includes;
          if ("undefined" != typeof L && L && L.Mixin) {
            s5 = d3(s5) ? s5 : [s5];
            for (var r6 = 0; r6 < s5.length; r6++) s5[r6] === L.Mixin.Events && console.warn("Deprecated include of L.Mixin.Events: this property will be removed in future releases, please inherit from L.Evented instead.", new Error().stack);
          }
          l4.apply(null, [o8].concat(t8.includes));
        }
        return l4(o8, t8), delete o8.statics, delete o8.includes, o8.options && (o8.options = n5.options ? R2(n5.options) : {}, l4(o8.options, t8.options)), o8._initHooks = [], o8.callInitHooks = function() {
          if (!this._initHooksCalled) {
            n5.callInitHooks && n5.callInitHooks.call(this), this._initHooksCalled = true;
            for (var t9 = 0, e8 = o8._initHooks.length; t9 < e8; t9++) o8._initHooks[t9].call(this);
          }
        }, e7;
      }, et.include = function(t8) {
        var e7 = this.prototype.options;
        return l4(this.prototype, t8), t8.options && (this.prototype.options = e7, this.mergeOptions(t8.options)), this;
      }, et.mergeOptions = function(t8) {
        return l4(this.prototype.options, t8), this;
      }, et.addInitHook = function(t8) {
        var e7 = Array.prototype.slice.call(arguments, 1), i7 = "function" == typeof t8 ? t8 : function() {
          this[t8].apply(this, e7);
        };
        return this.prototype._initHooks = this.prototype._initHooks || [], this.prototype._initHooks.push(i7), this;
      };
      var e6 = { on: function(t8, e7, i7) {
        if ("object" == typeof t8) for (var n5 in t8) this._on(n5, t8[n5], e7);
        else for (var o8 = 0, s5 = (t8 = F(t8)).length; o8 < s5; o8++) this._on(t8[o8], e7, i7);
        return this;
      }, off: function(t8, e7, i7) {
        if (arguments.length) if ("object" == typeof t8) for (var n5 in t8) this._off(n5, t8[n5], e7);
        else {
          t8 = F(t8);
          for (var o8 = 1 === arguments.length, s5 = 0, r6 = t8.length; s5 < r6; s5++) o8 ? this._off(t8[s5]) : this._off(t8[s5], e7, i7);
        }
        else delete this._events;
        return this;
      }, _on: function(t8, e7, i7, n5) {
        "function" != typeof e7 ? console.warn("wrong listener type: " + typeof e7) : false === this._listens(t8, e7, i7) && (e7 = { fn: e7, ctx: i7 = i7 === this ? void 0 : i7 }, n5 && (e7.once = true), this._events = this._events || {}, this._events[t8] = this._events[t8] || [], this._events[t8].push(e7));
      }, _off: function(t8, e7, i7) {
        var n5, o8, s5;
        if (this._events && (n5 = this._events[t8])) if (1 === arguments.length) {
          if (this._firingCount) for (o8 = 0, s5 = n5.length; o8 < s5; o8++) n5[o8].fn = u3;
          delete this._events[t8];
        } else "function" != typeof e7 ? console.warn("wrong listener type: " + typeof e7) : false !== (e7 = this._listens(t8, e7, i7)) && (i7 = n5[e7], this._firingCount && (i7.fn = u3, this._events[t8] = n5 = n5.slice()), n5.splice(e7, 1));
      }, fire: function(t8, e7, i7) {
        if (this.listens(t8, i7)) {
          var n5 = l4({}, e7, { type: t8, target: this, sourceTarget: e7 && e7.sourceTarget || this });
          if (this._events) {
            var o8 = this._events[t8];
            if (o8) {
              this._firingCount = this._firingCount + 1 || 1;
              for (var s5 = 0, r6 = o8.length; s5 < r6; s5++) {
                var a4 = o8[s5], h4 = a4.fn;
                a4.once && this.off(t8, h4, a4.ctx), h4.call(a4.ctx || this, n5);
              }
              this._firingCount--;
            }
          }
          i7 && this._propagateEvent(n5);
        }
        return this;
      }, listens: function(t8, e7, i7, n5) {
        "string" != typeof t8 && console.warn('"string" type argument expected');
        var o8 = e7, s5 = ("function" != typeof e7 && (n5 = !!e7, i7 = o8 = void 0), this._events && this._events[t8]);
        if (s5 && s5.length && false !== this._listens(t8, o8, i7)) return true;
        if (n5) {
          for (var r6 in this._eventParents) if (this._eventParents[r6].listens(t8, e7, i7, n5)) return true;
        }
        return false;
      }, _listens: function(t8, e7, i7) {
        if (this._events) {
          var n5 = this._events[t8] || [];
          if (!e7) return !!n5.length;
          i7 === this && (i7 = void 0);
          for (var o8 = 0, s5 = n5.length; o8 < s5; o8++) if (n5[o8].fn === e7 && n5[o8].ctx === i7) return o8;
        }
        return false;
      }, once: function(t8, e7, i7) {
        if ("object" == typeof t8) for (var n5 in t8) this._on(n5, t8[n5], e7, true);
        else for (var o8 = 0, s5 = (t8 = F(t8)).length; o8 < s5; o8++) this._on(t8[o8], e7, i7, true);
        return this;
      }, addEventParent: function(t8) {
        return this._eventParents = this._eventParents || {}, this._eventParents[h3(t8)] = t8, this;
      }, removeEventParent: function(t8) {
        return this._eventParents && delete this._eventParents[h3(t8)], this;
      }, _propagateEvent: function(t8) {
        for (var e7 in this._eventParents) this._eventParents[e7].fire(t8.type, l4({ layer: t8.target, propagatedFrom: t8.target }, t8), true);
      } }, it = (e6.addEventListener = e6.on, e6.removeEventListener = e6.clearAllEventListeners = e6.off, e6.addOneTimeEventListener = e6.once, e6.fireEvent = e6.fire, e6.hasEventListeners = e6.listens, et.extend(e6));
      function p4(t8, e7, i7) {
        this.x = i7 ? Math.round(t8) : t8, this.y = i7 ? Math.round(e7) : e7;
      }
      var nt = Math.trunc || function(t8) {
        return 0 < t8 ? Math.floor(t8) : Math.ceil(t8);
      };
      function m3(t8, e7, i7) {
        return t8 instanceof p4 ? t8 : d3(t8) ? new p4(t8[0], t8[1]) : null == t8 ? t8 : "object" == typeof t8 && "x" in t8 && "y" in t8 ? new p4(t8.x, t8.y) : new p4(t8, e7, i7);
      }
      function f3(t8, e7) {
        if (t8) for (var i7 = e7 ? [t8, e7] : t8, n5 = 0, o8 = i7.length; n5 < o8; n5++) this.extend(i7[n5]);
      }
      function _2(t8, e7) {
        return !t8 || t8 instanceof f3 ? t8 : new f3(t8, e7);
      }
      function s4(t8, e7) {
        if (t8) for (var i7 = e7 ? [t8, e7] : t8, n5 = 0, o8 = i7.length; n5 < o8; n5++) this.extend(i7[n5]);
      }
      function g2(t8, e7) {
        return t8 instanceof s4 ? t8 : new s4(t8, e7);
      }
      function v2(t8, e7, i7) {
        if (isNaN(t8) || isNaN(e7)) throw new Error("Invalid LatLng object: (" + t8 + ", " + e7 + ")");
        this.lat = +t8, this.lng = +e7, void 0 !== i7 && (this.alt = +i7);
      }
      function w2(t8, e7, i7) {
        return t8 instanceof v2 ? t8 : d3(t8) && "object" != typeof t8[0] ? 3 === t8.length ? new v2(t8[0], t8[1], t8[2]) : 2 === t8.length ? new v2(t8[0], t8[1]) : null : null == t8 ? t8 : "object" == typeof t8 && "lat" in t8 ? new v2(t8.lat, "lng" in t8 ? t8.lng : t8.lon, t8.alt) : void 0 === e7 ? null : new v2(t8, e7, i7);
      }
      p4.prototype = { clone: function() {
        return new p4(this.x, this.y);
      }, add: function(t8) {
        return this.clone()._add(m3(t8));
      }, _add: function(t8) {
        return this.x += t8.x, this.y += t8.y, this;
      }, subtract: function(t8) {
        return this.clone()._subtract(m3(t8));
      }, _subtract: function(t8) {
        return this.x -= t8.x, this.y -= t8.y, this;
      }, divideBy: function(t8) {
        return this.clone()._divideBy(t8);
      }, _divideBy: function(t8) {
        return this.x /= t8, this.y /= t8, this;
      }, multiplyBy: function(t8) {
        return this.clone()._multiplyBy(t8);
      }, _multiplyBy: function(t8) {
        return this.x *= t8, this.y *= t8, this;
      }, scaleBy: function(t8) {
        return new p4(this.x * t8.x, this.y * t8.y);
      }, unscaleBy: function(t8) {
        return new p4(this.x / t8.x, this.y / t8.y);
      }, round: function() {
        return this.clone()._round();
      }, _round: function() {
        return this.x = Math.round(this.x), this.y = Math.round(this.y), this;
      }, floor: function() {
        return this.clone()._floor();
      }, _floor: function() {
        return this.x = Math.floor(this.x), this.y = Math.floor(this.y), this;
      }, ceil: function() {
        return this.clone()._ceil();
      }, _ceil: function() {
        return this.x = Math.ceil(this.x), this.y = Math.ceil(this.y), this;
      }, trunc: function() {
        return this.clone()._trunc();
      }, _trunc: function() {
        return this.x = nt(this.x), this.y = nt(this.y), this;
      }, distanceTo: function(t8) {
        var e7 = (t8 = m3(t8)).x - this.x, t8 = t8.y - this.y;
        return Math.sqrt(e7 * e7 + t8 * t8);
      }, equals: function(t8) {
        return (t8 = m3(t8)).x === this.x && t8.y === this.y;
      }, contains: function(t8) {
        return t8 = m3(t8), Math.abs(t8.x) <= Math.abs(this.x) && Math.abs(t8.y) <= Math.abs(this.y);
      }, toString: function() {
        return "Point(" + i6(this.x) + ", " + i6(this.y) + ")";
      } }, f3.prototype = { extend: function(t8) {
        var e7, i7;
        if (t8) {
          if (t8 instanceof p4 || "number" == typeof t8[0] || "x" in t8) e7 = i7 = m3(t8);
          else if (e7 = (t8 = _2(t8)).min, i7 = t8.max, !e7 || !i7) return this;
          this.min || this.max ? (this.min.x = Math.min(e7.x, this.min.x), this.max.x = Math.max(i7.x, this.max.x), this.min.y = Math.min(e7.y, this.min.y), this.max.y = Math.max(i7.y, this.max.y)) : (this.min = e7.clone(), this.max = i7.clone());
        }
        return this;
      }, getCenter: function(t8) {
        return m3((this.min.x + this.max.x) / 2, (this.min.y + this.max.y) / 2, t8);
      }, getBottomLeft: function() {
        return m3(this.min.x, this.max.y);
      }, getTopRight: function() {
        return m3(this.max.x, this.min.y);
      }, getTopLeft: function() {
        return this.min;
      }, getBottomRight: function() {
        return this.max;
      }, getSize: function() {
        return this.max.subtract(this.min);
      }, contains: function(t8) {
        var e7, i7;
        return (t8 = ("number" == typeof t8[0] || t8 instanceof p4 ? m3 : _2)(t8)) instanceof f3 ? (e7 = t8.min, i7 = t8.max) : e7 = i7 = t8, e7.x >= this.min.x && i7.x <= this.max.x && e7.y >= this.min.y && i7.y <= this.max.y;
      }, intersects: function(t8) {
        t8 = _2(t8);
        var e7 = this.min, i7 = this.max, n5 = t8.min, t8 = t8.max, o8 = t8.x >= e7.x && n5.x <= i7.x, t8 = t8.y >= e7.y && n5.y <= i7.y;
        return o8 && t8;
      }, overlaps: function(t8) {
        t8 = _2(t8);
        var e7 = this.min, i7 = this.max, n5 = t8.min, t8 = t8.max, o8 = t8.x > e7.x && n5.x < i7.x, t8 = t8.y > e7.y && n5.y < i7.y;
        return o8 && t8;
      }, isValid: function() {
        return !(!this.min || !this.max);
      }, pad: function(t8) {
        var e7 = this.min, i7 = this.max, n5 = Math.abs(e7.x - i7.x) * t8, t8 = Math.abs(e7.y - i7.y) * t8;
        return _2(m3(e7.x - n5, e7.y - t8), m3(i7.x + n5, i7.y + t8));
      }, equals: function(t8) {
        return !!t8 && (t8 = _2(t8), this.min.equals(t8.getTopLeft()) && this.max.equals(t8.getBottomRight()));
      } }, s4.prototype = { extend: function(t8) {
        var e7, i7, n5 = this._southWest, o8 = this._northEast;
        if (t8 instanceof v2) i7 = e7 = t8;
        else {
          if (!(t8 instanceof s4)) return t8 ? this.extend(w2(t8) || g2(t8)) : this;
          if (e7 = t8._southWest, i7 = t8._northEast, !e7 || !i7) return this;
        }
        return n5 || o8 ? (n5.lat = Math.min(e7.lat, n5.lat), n5.lng = Math.min(e7.lng, n5.lng), o8.lat = Math.max(i7.lat, o8.lat), o8.lng = Math.max(i7.lng, o8.lng)) : (this._southWest = new v2(e7.lat, e7.lng), this._northEast = new v2(i7.lat, i7.lng)), this;
      }, pad: function(t8) {
        var e7 = this._southWest, i7 = this._northEast, n5 = Math.abs(e7.lat - i7.lat) * t8, t8 = Math.abs(e7.lng - i7.lng) * t8;
        return new s4(new v2(e7.lat - n5, e7.lng - t8), new v2(i7.lat + n5, i7.lng + t8));
      }, getCenter: function() {
        return new v2((this._southWest.lat + this._northEast.lat) / 2, (this._southWest.lng + this._northEast.lng) / 2);
      }, getSouthWest: function() {
        return this._southWest;
      }, getNorthEast: function() {
        return this._northEast;
      }, getNorthWest: function() {
        return new v2(this.getNorth(), this.getWest());
      }, getSouthEast: function() {
        return new v2(this.getSouth(), this.getEast());
      }, getWest: function() {
        return this._southWest.lng;
      }, getSouth: function() {
        return this._southWest.lat;
      }, getEast: function() {
        return this._northEast.lng;
      }, getNorth: function() {
        return this._northEast.lat;
      }, contains: function(t8) {
        t8 = ("number" == typeof t8[0] || t8 instanceof v2 || "lat" in t8 ? w2 : g2)(t8);
        var e7, i7, n5 = this._southWest, o8 = this._northEast;
        return t8 instanceof s4 ? (e7 = t8.getSouthWest(), i7 = t8.getNorthEast()) : e7 = i7 = t8, e7.lat >= n5.lat && i7.lat <= o8.lat && e7.lng >= n5.lng && i7.lng <= o8.lng;
      }, intersects: function(t8) {
        t8 = g2(t8);
        var e7 = this._southWest, i7 = this._northEast, n5 = t8.getSouthWest(), t8 = t8.getNorthEast(), o8 = t8.lat >= e7.lat && n5.lat <= i7.lat, t8 = t8.lng >= e7.lng && n5.lng <= i7.lng;
        return o8 && t8;
      }, overlaps: function(t8) {
        t8 = g2(t8);
        var e7 = this._southWest, i7 = this._northEast, n5 = t8.getSouthWest(), t8 = t8.getNorthEast(), o8 = t8.lat > e7.lat && n5.lat < i7.lat, t8 = t8.lng > e7.lng && n5.lng < i7.lng;
        return o8 && t8;
      }, toBBoxString: function() {
        return [this.getWest(), this.getSouth(), this.getEast(), this.getNorth()].join(",");
      }, equals: function(t8, e7) {
        return !!t8 && (t8 = g2(t8), this._southWest.equals(t8.getSouthWest(), e7) && this._northEast.equals(t8.getNorthEast(), e7));
      }, isValid: function() {
        return !(!this._southWest || !this._northEast);
      } };
      var ot = { latLngToPoint: function(t8, e7) {
        t8 = this.projection.project(t8), e7 = this.scale(e7);
        return this.transformation._transform(t8, e7);
      }, pointToLatLng: function(t8, e7) {
        e7 = this.scale(e7), t8 = this.transformation.untransform(t8, e7);
        return this.projection.unproject(t8);
      }, project: function(t8) {
        return this.projection.project(t8);
      }, unproject: function(t8) {
        return this.projection.unproject(t8);
      }, scale: function(t8) {
        return 256 * Math.pow(2, t8);
      }, zoom: function(t8) {
        return Math.log(t8 / 256) / Math.LN2;
      }, getProjectedBounds: function(t8) {
        var e7;
        return this.infinite ? null : (e7 = this.projection.bounds, t8 = this.scale(t8), new f3(this.transformation.transform(e7.min, t8), this.transformation.transform(e7.max, t8)));
      }, infinite: !(v2.prototype = { equals: function(t8, e7) {
        return !!t8 && (t8 = w2(t8), Math.max(Math.abs(this.lat - t8.lat), Math.abs(this.lng - t8.lng)) <= (void 0 === e7 ? 1e-9 : e7));
      }, toString: function(t8) {
        return "LatLng(" + i6(this.lat, t8) + ", " + i6(this.lng, t8) + ")";
      }, distanceTo: function(t8) {
        return st.distance(this, w2(t8));
      }, wrap: function() {
        return st.wrapLatLng(this);
      }, toBounds: function(t8) {
        var t8 = 180 * t8 / 40075017, e7 = t8 / Math.cos(Math.PI / 180 * this.lat);
        return g2([this.lat - t8, this.lng - e7], [this.lat + t8, this.lng + e7]);
      }, clone: function() {
        return new v2(this.lat, this.lng, this.alt);
      } }), wrapLatLng: function(t8) {
        var e7 = this.wrapLng ? H4(t8.lng, this.wrapLng, true) : t8.lng;
        return new v2(this.wrapLat ? H4(t8.lat, this.wrapLat, true) : t8.lat, e7, t8.alt);
      }, wrapLatLngBounds: function(t8) {
        var e7 = t8.getCenter(), i7 = this.wrapLatLng(e7), n5 = e7.lat - i7.lat, e7 = e7.lng - i7.lng;
        return 0 == n5 && 0 == e7 ? t8 : (i7 = t8.getSouthWest(), t8 = t8.getNorthEast(), new s4(new v2(i7.lat - n5, i7.lng - e7), new v2(t8.lat - n5, t8.lng - e7)));
      } }, st = l4({}, ot, { wrapLng: [-180, 180], R: 6371e3, distance: function(t8, e7) {
        var i7 = Math.PI / 180, n5 = t8.lat * i7, o8 = e7.lat * i7, s5 = Math.sin((e7.lat - t8.lat) * i7 / 2), e7 = Math.sin((e7.lng - t8.lng) * i7 / 2), t8 = s5 * s5 + Math.cos(n5) * Math.cos(o8) * e7 * e7, i7 = 2 * Math.atan2(Math.sqrt(t8), Math.sqrt(1 - t8));
        return this.R * i7;
      } }), rt = 6378137, rt = { R: rt, MAX_LATITUDE: 85.0511287798, project: function(t8) {
        var e7 = Math.PI / 180, i7 = this.MAX_LATITUDE, i7 = Math.max(Math.min(i7, t8.lat), -i7), i7 = Math.sin(i7 * e7);
        return new p4(this.R * t8.lng * e7, this.R * Math.log((1 + i7) / (1 - i7)) / 2);
      }, unproject: function(t8) {
        var e7 = 180 / Math.PI;
        return new v2((2 * Math.atan(Math.exp(t8.y / this.R)) - Math.PI / 2) * e7, t8.x * e7 / this.R);
      }, bounds: new f3([-(rt = rt * Math.PI), -rt], [rt, rt]) };
      function at(t8, e7, i7, n5) {
        d3(t8) ? (this._a = t8[0], this._b = t8[1], this._c = t8[2], this._d = t8[3]) : (this._a = t8, this._b = e7, this._c = i7, this._d = n5);
      }
      function ht(t8, e7, i7, n5) {
        return new at(t8, e7, i7, n5);
      }
      at.prototype = { transform: function(t8, e7) {
        return this._transform(t8.clone(), e7);
      }, _transform: function(t8, e7) {
        return t8.x = (e7 = e7 || 1) * (this._a * t8.x + this._b), t8.y = e7 * (this._c * t8.y + this._d), t8;
      }, untransform: function(t8, e7) {
        return new p4((t8.x / (e7 = e7 || 1) - this._b) / this._a, (t8.y / e7 - this._d) / this._c);
      } };
      var lt = l4({}, st, { code: "EPSG:3857", projection: rt, transformation: ht(lt = 0.5 / (Math.PI * rt.R), 0.5, -lt, 0.5) }), ut = l4({}, lt, { code: "EPSG:900913" });
      function ct(t8) {
        return document.createElementNS("http://www.w3.org/2000/svg", t8);
      }
      function dt(t8, e7) {
        for (var i7, n5, o8, s5, r6 = "", a4 = 0, h4 = t8.length; a4 < h4; a4++) {
          for (i7 = 0, n5 = (o8 = t8[a4]).length; i7 < n5; i7++) r6 += (i7 ? "L" : "M") + (s5 = o8[i7]).x + " " + s5.y;
          r6 += e7 ? b3.svg ? "z" : "x" : "";
        }
        return r6 || "M0 0";
      }
      var _t = document.documentElement.style, pt = "ActiveXObject" in window, mt = pt && !document.addEventListener, n4 = "msLaunchUri" in navigator && !("documentMode" in document), ft = y4("webkit"), gt = y4("android"), vt = y4("android 2") || y4("android 3"), yt = parseInt(/WebKit\/([0-9]+)|$/.exec(navigator.userAgent)[1], 10), yt = gt && y4("Google") && yt < 537 && !("AudioNode" in window), xt = !!window.opera, wt = !n4 && y4("chrome"), bt = y4("gecko") && !ft && !xt && !pt, Pt = !wt && y4("safari"), Lt = y4("phantom"), o7 = "OTransition" in _t, Tt = 0 === navigator.platform.indexOf("Win"), Mt = pt && "transition" in _t, zt = "WebKitCSSMatrix" in window && "m11" in new window.WebKitCSSMatrix() && !vt, _t = "MozPerspective" in _t, Ct = !window.L_DISABLE_3D && (Mt || zt || _t) && !o7 && !Lt, Zt = "undefined" != typeof orientation || y4("mobile"), St = Zt && ft, Et = Zt && zt, kt = !window.PointerEvent && window.MSPointerEvent, Ot = !(!window.PointerEvent && !kt), At = "ontouchstart" in window || !!window.TouchEvent, Bt = !window.L_NO_TOUCH && (At || Ot), It = Zt && xt, Rt = Zt && bt, Nt = 1 < (window.devicePixelRatio || window.screen.deviceXDPI / window.screen.logicalXDPI), Dt = (function() {
        var t8 = false;
        try {
          var e7 = Object.defineProperty({}, "passive", { get: function() {
            t8 = true;
          } });
          window.addEventListener("testPassiveEventSupport", u3, e7), window.removeEventListener("testPassiveEventSupport", u3, e7);
        } catch (t9) {
        }
        return t8;
      })(), jt = !!document.createElement("canvas").getContext, Ht = !(!document.createElementNS || !ct("svg").createSVGRect), Wt = !!Ht && ((Wt = document.createElement("div")).innerHTML = "<svg/>", "http://www.w3.org/2000/svg" === (Wt.firstChild && Wt.firstChild.namespaceURI));
      function y4(t8) {
        return 0 <= navigator.userAgent.toLowerCase().indexOf(t8);
      }
      var b3 = { ie: pt, ielt9: mt, edge: n4, webkit: ft, android: gt, android23: vt, androidStock: yt, opera: xt, chrome: wt, gecko: bt, safari: Pt, phantom: Lt, opera12: o7, win: Tt, ie3d: Mt, webkit3d: zt, gecko3d: _t, any3d: Ct, mobile: Zt, mobileWebkit: St, mobileWebkit3d: Et, msPointer: kt, pointer: Ot, touch: Bt, touchNative: At, mobileOpera: It, mobileGecko: Rt, retina: Nt, passiveEvents: Dt, canvas: jt, svg: Ht, vml: !Ht && (function() {
        try {
          var t8 = document.createElement("div"), e7 = (t8.innerHTML = '<v:shape adj="1"/>', t8.firstChild);
          return e7.style.behavior = "url(#default#VML)", e7 && "object" == typeof e7.adj;
        } catch (t9) {
          return false;
        }
      })(), inlineSvg: Wt, mac: 0 === navigator.platform.indexOf("Mac"), linux: 0 === navigator.platform.indexOf("Linux") }, Ft = b3.msPointer ? "MSPointerDown" : "pointerdown", Ut = b3.msPointer ? "MSPointerMove" : "pointermove", Vt = b3.msPointer ? "MSPointerUp" : "pointerup", qt = b3.msPointer ? "MSPointerCancel" : "pointercancel", Gt = { touchstart: Ft, touchmove: Ut, touchend: Vt, touchcancel: qt }, Kt = { touchstart: function(t8, e7) {
        e7.MSPOINTER_TYPE_TOUCH && e7.pointerType === e7.MSPOINTER_TYPE_TOUCH && O(e7);
        ee(t8, e7);
      }, touchmove: ee, touchend: ee, touchcancel: ee }, Yt = {}, Xt = false;
      function Jt(t8, e7, i7) {
        return "touchstart" !== e7 || Xt || (document.addEventListener(Ft, $t, true), document.addEventListener(Ut, Qt, true), document.addEventListener(Vt, te, true), document.addEventListener(qt, te, true), Xt = true), Kt[e7] ? (i7 = Kt[e7].bind(this, i7), t8.addEventListener(Gt[e7], i7, false), i7) : (console.warn("wrong event specified:", e7), u3);
      }
      function $t(t8) {
        Yt[t8.pointerId] = t8;
      }
      function Qt(t8) {
        Yt[t8.pointerId] && (Yt[t8.pointerId] = t8);
      }
      function te(t8) {
        delete Yt[t8.pointerId];
      }
      function ee(t8, e7) {
        if (e7.pointerType !== (e7.MSPOINTER_TYPE_MOUSE || "mouse")) {
          for (var i7 in e7.touches = [], Yt) e7.touches.push(Yt[i7]);
          e7.changedTouches = [e7], t8(e7);
        }
      }
      var ie = 200;
      function ne(t8, i7) {
        t8.addEventListener("dblclick", i7);
        var n5, o8 = 0;
        function e7(t9) {
          var e8;
          1 !== t9.detail ? n5 = t9.detail : "mouse" === t9.pointerType || t9.sourceCapabilities && !t9.sourceCapabilities.firesTouchEvents || ((e8 = Ne(t9)).some(function(t10) {
            return t10 instanceof HTMLLabelElement && t10.attributes.for;
          }) && !e8.some(function(t10) {
            return t10 instanceof HTMLInputElement || t10 instanceof HTMLSelectElement;
          }) || ((e8 = Date.now()) - o8 <= ie ? 2 === ++n5 && i7((function(t10) {
            var e9, i8, n6 = {};
            for (i8 in t10) e9 = t10[i8], n6[i8] = e9 && e9.bind ? e9.bind(t10) : e9;
            return (t10 = n6).type = "dblclick", n6.detail = 2, n6.isTrusted = false, n6._simulated = true, n6;
          })(t9)) : n5 = 1, o8 = e8));
        }
        return t8.addEventListener("click", e7), { dblclick: i7, simDblclick: e7 };
      }
      var oe, se, re, ae, he, le, ue = we(["transform", "webkitTransform", "OTransform", "MozTransform", "msTransform"]), ce = we(["webkitTransition", "transition", "OTransition", "MozTransition", "msTransition"]), de = "webkitTransition" === ce || "OTransition" === ce ? ce + "End" : "transitionend";
      function _e(t8) {
        return "string" == typeof t8 ? document.getElementById(t8) : t8;
      }
      function pe(t8, e7) {
        var i7 = t8.style[e7] || t8.currentStyle && t8.currentStyle[e7];
        return "auto" === (i7 = i7 && "auto" !== i7 || !document.defaultView ? i7 : (t8 = document.defaultView.getComputedStyle(t8, null)) ? t8[e7] : null) ? null : i7;
      }
      function P2(t8, e7, i7) {
        t8 = document.createElement(t8);
        return t8.className = e7 || "", i7 && i7.appendChild(t8), t8;
      }
      function T2(t8) {
        var e7 = t8.parentNode;
        e7 && e7.removeChild(t8);
      }
      function me(t8) {
        for (; t8.firstChild; ) t8.removeChild(t8.firstChild);
      }
      function fe(t8) {
        var e7 = t8.parentNode;
        e7 && e7.lastChild !== t8 && e7.appendChild(t8);
      }
      function ge(t8) {
        var e7 = t8.parentNode;
        e7 && e7.firstChild !== t8 && e7.insertBefore(t8, e7.firstChild);
      }
      function ve(t8, e7) {
        return void 0 !== t8.classList ? t8.classList.contains(e7) : 0 < (t8 = xe(t8)).length && new RegExp("(^|\\s)" + e7 + "(\\s|$)").test(t8);
      }
      function M2(t8, e7) {
        var i7;
        if (void 0 !== t8.classList) for (var n5 = F(e7), o8 = 0, s5 = n5.length; o8 < s5; o8++) t8.classList.add(n5[o8]);
        else ve(t8, e7) || ye(t8, ((i7 = xe(t8)) ? i7 + " " : "") + e7);
      }
      function z2(t8, e7) {
        void 0 !== t8.classList ? t8.classList.remove(e7) : ye(t8, W3((" " + xe(t8) + " ").replace(" " + e7 + " ", " ")));
      }
      function ye(t8, e7) {
        void 0 === t8.className.baseVal ? t8.className = e7 : t8.className.baseVal = e7;
      }
      function xe(t8) {
        return void 0 === (t8 = t8.correspondingElement ? t8.correspondingElement : t8).className.baseVal ? t8.className : t8.className.baseVal;
      }
      function C2(t8, e7) {
        if ("opacity" in t8.style) t8.style.opacity = e7;
        else if ("filter" in t8.style) {
          var i7 = false, n5 = "DXImageTransform.Microsoft.Alpha";
          try {
            i7 = t8.filters.item(n5);
          } catch (t9) {
            if (1 === e7) return;
          }
          e7 = Math.round(100 * e7), i7 ? (i7.Enabled = 100 !== e7, i7.Opacity = e7) : t8.style.filter += " progid:" + n5 + "(opacity=" + e7 + ")";
        }
      }
      function we(t8) {
        for (var e7 = document.documentElement.style, i7 = 0; i7 < t8.length; i7++) if (t8[i7] in e7) return t8[i7];
        return false;
      }
      function be(t8, e7, i7) {
        e7 = e7 || new p4(0, 0);
        t8.style[ue] = (b3.ie3d ? "translate(" + e7.x + "px," + e7.y + "px)" : "translate3d(" + e7.x + "px," + e7.y + "px,0)") + (i7 ? " scale(" + i7 + ")" : "");
      }
      function Z2(t8, e7) {
        t8._leaflet_pos = e7, b3.any3d ? be(t8, e7) : (t8.style.left = e7.x + "px", t8.style.top = e7.y + "px");
      }
      function Pe(t8) {
        return t8._leaflet_pos || new p4(0, 0);
      }
      function Le() {
        S3(window, "dragstart", O);
      }
      function Te() {
        k2(window, "dragstart", O);
      }
      function Me(t8) {
        for (; -1 === t8.tabIndex; ) t8 = t8.parentNode;
        t8.style && (ze(), le = (he = t8).style.outlineStyle, t8.style.outlineStyle = "none", S3(window, "keydown", ze));
      }
      function ze() {
        he && (he.style.outlineStyle = le, le = he = void 0, k2(window, "keydown", ze));
      }
      function Ce(t8) {
        for (; !((t8 = t8.parentNode).offsetWidth && t8.offsetHeight || t8 === document.body); ) ;
        return t8;
      }
      function Ze(t8) {
        var e7 = t8.getBoundingClientRect();
        return { x: e7.width / t8.offsetWidth || 1, y: e7.height / t8.offsetHeight || 1, boundingClientRect: e7 };
      }
      ae = "onselectstart" in document ? (re = function() {
        S3(window, "selectstart", O);
      }, function() {
        k2(window, "selectstart", O);
      }) : (se = we(["userSelect", "WebkitUserSelect", "OUserSelect", "MozUserSelect", "msUserSelect"]), re = function() {
        var t8;
        se && (t8 = document.documentElement.style, oe = t8[se], t8[se] = "none");
      }, function() {
        se && (document.documentElement.style[se] = oe, oe = void 0);
      });
      pt = { __proto__: null, TRANSFORM: ue, TRANSITION: ce, TRANSITION_END: de, get: _e, getStyle: pe, create: P2, remove: T2, empty: me, toFront: fe, toBack: ge, hasClass: ve, addClass: M2, removeClass: z2, setClass: ye, getClass: xe, setOpacity: C2, testProp: we, setTransform: be, setPosition: Z2, getPosition: Pe, get disableTextSelection() {
        return re;
      }, get enableTextSelection() {
        return ae;
      }, disableImageDrag: Le, enableImageDrag: Te, preventOutline: Me, restoreOutline: ze, getSizedParentNode: Ce, getScale: Ze };
      function S3(t8, e7, i7, n5) {
        if (e7 && "object" == typeof e7) for (var o8 in e7) ke(t8, o8, e7[o8], i7);
        else for (var s5 = 0, r6 = (e7 = F(e7)).length; s5 < r6; s5++) ke(t8, e7[s5], i7, n5);
        return this;
      }
      var E2 = "_leaflet_events";
      function k2(t8, e7, i7, n5) {
        if (1 === arguments.length) Se(t8), delete t8[E2];
        else if (e7 && "object" == typeof e7) for (var o8 in e7) Oe(t8, o8, e7[o8], i7);
        else if (e7 = F(e7), 2 === arguments.length) Se(t8, function(t9) {
          return -1 !== G(e7, t9);
        });
        else for (var s5 = 0, r6 = e7.length; s5 < r6; s5++) Oe(t8, e7[s5], i7, n5);
        return this;
      }
      function Se(t8, e7) {
        for (var i7 in t8[E2]) {
          var n5 = i7.split(/\d/)[0];
          e7 && !e7(n5) || Oe(t8, n5, null, null, i7);
        }
      }
      var Ee = { mouseenter: "mouseover", mouseleave: "mouseout", wheel: !("onwheel" in window) && "mousewheel" };
      function ke(e7, t8, i7, n5) {
        var o8, s5, r6 = t8 + h3(i7) + (n5 ? "_" + h3(n5) : "");
        e7[E2] && e7[E2][r6] || (s5 = o8 = function(t9) {
          return i7.call(n5 || e7, t9 || window.event);
        }, !b3.touchNative && b3.pointer && 0 === t8.indexOf("touch") ? o8 = Jt(e7, t8, o8) : b3.touch && "dblclick" === t8 ? o8 = ne(e7, o8) : "addEventListener" in e7 ? "touchstart" === t8 || "touchmove" === t8 || "wheel" === t8 || "mousewheel" === t8 ? e7.addEventListener(Ee[t8] || t8, o8, !!b3.passiveEvents && { passive: false }) : "mouseenter" === t8 || "mouseleave" === t8 ? e7.addEventListener(Ee[t8], o8 = function(t9) {
          t9 = t9 || window.event, We(e7, t9) && s5(t9);
        }, false) : e7.addEventListener(t8, s5, false) : e7.attachEvent("on" + t8, o8), e7[E2] = e7[E2] || {}, e7[E2][r6] = o8);
      }
      function Oe(t8, e7, i7, n5, o8) {
        o8 = o8 || e7 + h3(i7) + (n5 ? "_" + h3(n5) : "");
        var s5, r6, i7 = t8[E2] && t8[E2][o8];
        i7 && (!b3.touchNative && b3.pointer && 0 === e7.indexOf("touch") ? (n5 = t8, r6 = i7, Gt[s5 = e7] ? n5.removeEventListener(Gt[s5], r6, false) : console.warn("wrong event specified:", s5)) : b3.touch && "dblclick" === e7 ? (n5 = i7, (r6 = t8).removeEventListener("dblclick", n5.dblclick), r6.removeEventListener("click", n5.simDblclick)) : "removeEventListener" in t8 ? t8.removeEventListener(Ee[e7] || e7, i7, false) : t8.detachEvent("on" + e7, i7), t8[E2][o8] = null);
      }
      function Ae(t8) {
        return t8.stopPropagation ? t8.stopPropagation() : t8.originalEvent ? t8.originalEvent._stopped = true : t8.cancelBubble = true, this;
      }
      function Be(t8) {
        return ke(t8, "wheel", Ae), this;
      }
      function Ie(t8) {
        return S3(t8, "mousedown touchstart dblclick contextmenu", Ae), t8._leaflet_disable_click = true, this;
      }
      function O(t8) {
        return t8.preventDefault ? t8.preventDefault() : t8.returnValue = false, this;
      }
      function Re(t8) {
        return O(t8), Ae(t8), this;
      }
      function Ne(t8) {
        if (t8.composedPath) return t8.composedPath();
        for (var e7 = [], i7 = t8.target; i7; ) e7.push(i7), i7 = i7.parentNode;
        return e7;
      }
      function De(t8, e7) {
        var i7, n5;
        return e7 ? (n5 = (i7 = Ze(e7)).boundingClientRect, new p4((t8.clientX - n5.left) / i7.x - e7.clientLeft, (t8.clientY - n5.top) / i7.y - e7.clientTop)) : new p4(t8.clientX, t8.clientY);
      }
      var je = b3.linux && b3.chrome ? window.devicePixelRatio : b3.mac ? 3 * window.devicePixelRatio : 0 < window.devicePixelRatio ? 2 * window.devicePixelRatio : 1;
      function He(t8) {
        return b3.edge ? t8.wheelDeltaY / 2 : t8.deltaY && 0 === t8.deltaMode ? -t8.deltaY / je : t8.deltaY && 1 === t8.deltaMode ? 20 * -t8.deltaY : t8.deltaY && 2 === t8.deltaMode ? 60 * -t8.deltaY : t8.deltaX || t8.deltaZ ? 0 : t8.wheelDelta ? (t8.wheelDeltaY || t8.wheelDelta) / 2 : t8.detail && Math.abs(t8.detail) < 32765 ? 20 * -t8.detail : t8.detail ? t8.detail / -32765 * 60 : 0;
      }
      function We(t8, e7) {
        var i7 = e7.relatedTarget;
        if (!i7) return true;
        try {
          for (; i7 && i7 !== t8; ) i7 = i7.parentNode;
        } catch (t9) {
          return false;
        }
        return i7 !== t8;
      }
      var mt = { __proto__: null, on: S3, off: k2, stopPropagation: Ae, disableScrollPropagation: Be, disableClickPropagation: Ie, preventDefault: O, stop: Re, getPropagationPath: Ne, getMousePosition: De, getWheelDelta: He, isExternalTarget: We, addListener: S3, removeListener: k2 }, Fe = it.extend({ run: function(t8, e7, i7, n5) {
        this.stop(), this._el = t8, this._inProgress = true, this._duration = i7 || 0.25, this._easeOutPower = 1 / Math.max(n5 || 0.5, 0.2), this._startPos = Pe(t8), this._offset = e7.subtract(this._startPos), this._startTime = +/* @__PURE__ */ new Date(), this.fire("start"), this._animate();
      }, stop: function() {
        this._inProgress && (this._step(true), this._complete());
      }, _animate: function() {
        this._animId = x2(this._animate, this), this._step();
      }, _step: function(t8) {
        var e7 = +/* @__PURE__ */ new Date() - this._startTime, i7 = 1e3 * this._duration;
        e7 < i7 ? this._runFrame(this._easeOut(e7 / i7), t8) : (this._runFrame(1), this._complete());
      }, _runFrame: function(t8, e7) {
        t8 = this._startPos.add(this._offset.multiplyBy(t8));
        e7 && t8._round(), Z2(this._el, t8), this.fire("step");
      }, _complete: function() {
        r5(this._animId), this._inProgress = false, this.fire("end");
      }, _easeOut: function(t8) {
        return 1 - Math.pow(1 - t8, this._easeOutPower);
      } }), A2 = it.extend({ options: { crs: lt, center: void 0, zoom: void 0, minZoom: void 0, maxZoom: void 0, layers: [], maxBounds: void 0, renderer: void 0, zoomAnimation: true, zoomAnimationThreshold: 4, fadeAnimation: true, markerZoomAnimation: true, transform3DLimit: 8388608, zoomSnap: 1, zoomDelta: 1, trackResize: true }, initialize: function(t8, e7) {
        e7 = c4(this, e7), this._handlers = [], this._layers = {}, this._zoomBoundLayers = {}, this._sizeChanged = true, this._initContainer(t8), this._initLayout(), this._onResize = a3(this._onResize, this), this._initEvents(), e7.maxBounds && this.setMaxBounds(e7.maxBounds), void 0 !== e7.zoom && (this._zoom = this._limitZoom(e7.zoom)), e7.center && void 0 !== e7.zoom && this.setView(w2(e7.center), e7.zoom, { reset: true }), this.callInitHooks(), this._zoomAnimated = ce && b3.any3d && !b3.mobileOpera && this.options.zoomAnimation, this._zoomAnimated && (this._createAnimProxy(), S3(this._proxy, de, this._catchTransitionEnd, this)), this._addLayers(this.options.layers);
      }, setView: function(t8, e7, i7) {
        if ((e7 = void 0 === e7 ? this._zoom : this._limitZoom(e7), t8 = this._limitCenter(w2(t8), e7, this.options.maxBounds), i7 = i7 || {}, this._stop(), this._loaded && !i7.reset && true !== i7) && (void 0 !== i7.animate && (i7.zoom = l4({ animate: i7.animate }, i7.zoom), i7.pan = l4({ animate: i7.animate, duration: i7.duration }, i7.pan)), this._zoom !== e7 ? this._tryAnimatedZoom && this._tryAnimatedZoom(t8, e7, i7.zoom) : this._tryAnimatedPan(t8, i7.pan))) return clearTimeout(this._sizeTimer), this;
        return this._resetView(t8, e7, i7.pan && i7.pan.noMoveStart), this;
      }, setZoom: function(t8, e7) {
        return this._loaded ? this.setView(this.getCenter(), t8, { zoom: e7 }) : (this._zoom = t8, this);
      }, zoomIn: function(t8, e7) {
        return t8 = t8 || (b3.any3d ? this.options.zoomDelta : 1), this.setZoom(this._zoom + t8, e7);
      }, zoomOut: function(t8, e7) {
        return t8 = t8 || (b3.any3d ? this.options.zoomDelta : 1), this.setZoom(this._zoom - t8, e7);
      }, setZoomAround: function(t8, e7, i7) {
        var n5 = this.getZoomScale(e7), o8 = this.getSize().divideBy(2), t8 = (t8 instanceof p4 ? t8 : this.latLngToContainerPoint(t8)).subtract(o8).multiplyBy(1 - 1 / n5), n5 = this.containerPointToLatLng(o8.add(t8));
        return this.setView(n5, e7, { zoom: i7 });
      }, _getBoundsCenterZoom: function(t8, e7) {
        e7 = e7 || {}, t8 = t8.getBounds ? t8.getBounds() : g2(t8);
        var i7 = m3(e7.paddingTopLeft || e7.padding || [0, 0]), n5 = m3(e7.paddingBottomRight || e7.padding || [0, 0]), o8 = this.getBoundsZoom(t8, false, i7.add(n5));
        return (o8 = "number" == typeof e7.maxZoom ? Math.min(e7.maxZoom, o8) : o8) === 1 / 0 ? { center: t8.getCenter(), zoom: o8 } : (e7 = n5.subtract(i7).divideBy(2), n5 = this.project(t8.getSouthWest(), o8), i7 = this.project(t8.getNorthEast(), o8), { center: this.unproject(n5.add(i7).divideBy(2).add(e7), o8), zoom: o8 });
      }, fitBounds: function(t8, e7) {
        if ((t8 = g2(t8)).isValid()) return t8 = this._getBoundsCenterZoom(t8, e7), this.setView(t8.center, t8.zoom, e7);
        throw new Error("Bounds are not valid.");
      }, fitWorld: function(t8) {
        return this.fitBounds([[-90, -180], [90, 180]], t8);
      }, panTo: function(t8, e7) {
        return this.setView(t8, this._zoom, { pan: e7 });
      }, panBy: function(t8, e7) {
        var i7;
        return e7 = e7 || {}, (t8 = m3(t8).round()).x || t8.y ? (true === e7.animate || this.getSize().contains(t8) ? (this._panAnim || (this._panAnim = new Fe(), this._panAnim.on({ step: this._onPanTransitionStep, end: this._onPanTransitionEnd }, this)), e7.noMoveStart || this.fire("movestart"), false !== e7.animate ? (M2(this._mapPane, "leaflet-pan-anim"), i7 = this._getMapPanePos().subtract(t8).round(), this._panAnim.run(this._mapPane, i7, e7.duration || 0.25, e7.easeLinearity)) : (this._rawPanBy(t8), this.fire("move").fire("moveend"))) : this._resetView(this.unproject(this.project(this.getCenter()).add(t8)), this.getZoom()), this) : this.fire("moveend");
      }, flyTo: function(n5, o8, t8) {
        if (false === (t8 = t8 || {}).animate || !b3.any3d) return this.setView(n5, o8, t8);
        this._stop();
        var s5 = this.project(this.getCenter()), r6 = this.project(n5), e7 = this.getSize(), a4 = this._zoom, h4 = (n5 = w2(n5), o8 = void 0 === o8 ? a4 : o8, Math.max(e7.x, e7.y)), i7 = h4 * this.getZoomScale(a4, o8), l5 = r6.distanceTo(s5) || 1, u4 = 1.42, c5 = u4 * u4;
        function d4(t9) {
          t9 = (i7 * i7 - h4 * h4 + (t9 ? -1 : 1) * c5 * c5 * l5 * l5) / (2 * (t9 ? i7 : h4) * c5 * l5), t9 = Math.sqrt(t9 * t9 + 1) - t9;
          return t9 < 1e-9 ? -18 : Math.log(t9);
        }
        function _3(t9) {
          return (Math.exp(t9) - Math.exp(-t9)) / 2;
        }
        function p5(t9) {
          return (Math.exp(t9) + Math.exp(-t9)) / 2;
        }
        var m4 = d4(0);
        function f4(t9) {
          return h4 * (p5(m4) * (_3(t9 = m4 + u4 * t9) / p5(t9)) - _3(m4)) / c5;
        }
        var g3 = Date.now(), v3 = (d4(1) - m4) / u4, y5 = t8.duration ? 1e3 * t8.duration : 1e3 * v3 * 0.8;
        return this._moveStart(true, t8.noMoveStart), function t9() {
          var e8 = (Date.now() - g3) / y5, i8 = (1 - Math.pow(1 - e8, 1.5)) * v3;
          e8 <= 1 ? (this._flyToFrame = x2(t9, this), this._move(this.unproject(s5.add(r6.subtract(s5).multiplyBy(f4(i8) / l5)), a4), this.getScaleZoom(h4 / (e8 = i8, h4 * (p5(m4) / p5(m4 + u4 * e8))), a4), { flyTo: true })) : this._move(n5, o8)._moveEnd(true);
        }.call(this), this;
      }, flyToBounds: function(t8, e7) {
        t8 = this._getBoundsCenterZoom(t8, e7);
        return this.flyTo(t8.center, t8.zoom, e7);
      }, setMaxBounds: function(t8) {
        return t8 = g2(t8), this.listens("moveend", this._panInsideMaxBounds) && this.off("moveend", this._panInsideMaxBounds), t8.isValid() ? (this.options.maxBounds = t8, this._loaded && this._panInsideMaxBounds(), this.on("moveend", this._panInsideMaxBounds)) : (this.options.maxBounds = null, this);
      }, setMinZoom: function(t8) {
        var e7 = this.options.minZoom;
        return this.options.minZoom = t8, this._loaded && e7 !== t8 && (this.fire("zoomlevelschange"), this.getZoom() < this.options.minZoom) ? this.setZoom(t8) : this;
      }, setMaxZoom: function(t8) {
        var e7 = this.options.maxZoom;
        return this.options.maxZoom = t8, this._loaded && e7 !== t8 && (this.fire("zoomlevelschange"), this.getZoom() > this.options.maxZoom) ? this.setZoom(t8) : this;
      }, panInsideBounds: function(t8, e7) {
        this._enforcingBounds = true;
        var i7 = this.getCenter(), t8 = this._limitCenter(i7, this._zoom, g2(t8));
        return i7.equals(t8) || this.panTo(t8, e7), this._enforcingBounds = false, this;
      }, panInside: function(t8, e7) {
        var i7 = m3((e7 = e7 || {}).paddingTopLeft || e7.padding || [0, 0]), n5 = m3(e7.paddingBottomRight || e7.padding || [0, 0]), o8 = this.project(this.getCenter()), t8 = this.project(t8), s5 = this.getPixelBounds(), i7 = _2([s5.min.add(i7), s5.max.subtract(n5)]), s5 = i7.getSize();
        return i7.contains(t8) || (this._enforcingBounds = true, n5 = t8.subtract(i7.getCenter()), i7 = i7.extend(t8).getSize().subtract(s5), o8.x += n5.x < 0 ? -i7.x : i7.x, o8.y += n5.y < 0 ? -i7.y : i7.y, this.panTo(this.unproject(o8), e7), this._enforcingBounds = false), this;
      }, invalidateSize: function(t8) {
        if (!this._loaded) return this;
        t8 = l4({ animate: false, pan: true }, true === t8 ? { animate: true } : t8);
        var e7 = this.getSize(), i7 = (this._sizeChanged = true, this._lastCenter = null, this.getSize()), n5 = e7.divideBy(2).round(), o8 = i7.divideBy(2).round(), n5 = n5.subtract(o8);
        return n5.x || n5.y ? (t8.animate && t8.pan ? this.panBy(n5) : (t8.pan && this._rawPanBy(n5), this.fire("move"), t8.debounceMoveend ? (clearTimeout(this._sizeTimer), this._sizeTimer = setTimeout(a3(this.fire, this, "moveend"), 200)) : this.fire("moveend")), this.fire("resize", { oldSize: e7, newSize: i7 })) : this;
      }, stop: function() {
        return this.setZoom(this._limitZoom(this._zoom)), this.options.zoomSnap || this.fire("viewreset"), this._stop();
      }, locate: function(t8) {
        var e7, i7;
        return t8 = this._locateOptions = l4({ timeout: 1e4, watch: false }, t8), "geolocation" in navigator ? (e7 = a3(this._handleGeolocationResponse, this), i7 = a3(this._handleGeolocationError, this), t8.watch ? this._locationWatchId = navigator.geolocation.watchPosition(e7, i7, t8) : navigator.geolocation.getCurrentPosition(e7, i7, t8)) : this._handleGeolocationError({ code: 0, message: "Geolocation not supported." }), this;
      }, stopLocate: function() {
        return navigator.geolocation && navigator.geolocation.clearWatch && navigator.geolocation.clearWatch(this._locationWatchId), this._locateOptions && (this._locateOptions.setView = false), this;
      }, _handleGeolocationError: function(t8) {
        var e7;
        this._container._leaflet_id && (e7 = t8.code, t8 = t8.message || (1 === e7 ? "permission denied" : 2 === e7 ? "position unavailable" : "timeout"), this._locateOptions.setView && !this._loaded && this.fitWorld(), this.fire("locationerror", { code: e7, message: "Geolocation error: " + t8 + "." }));
      }, _handleGeolocationResponse: function(t8) {
        if (this._container._leaflet_id) {
          var e7, i7, n5 = new v2(t8.coords.latitude, t8.coords.longitude), o8 = n5.toBounds(2 * t8.coords.accuracy), s5 = this._locateOptions, r6 = (s5.setView && (e7 = this.getBoundsZoom(o8), this.setView(n5, s5.maxZoom ? Math.min(e7, s5.maxZoom) : e7)), { latlng: n5, bounds: o8, timestamp: t8.timestamp });
          for (i7 in t8.coords) "number" == typeof t8.coords[i7] && (r6[i7] = t8.coords[i7]);
          this.fire("locationfound", r6);
        }
      }, addHandler: function(t8, e7) {
        return e7 && (e7 = this[t8] = new e7(this), this._handlers.push(e7), this.options[t8] && e7.enable()), this;
      }, remove: function() {
        if (this._initEvents(true), this.options.maxBounds && this.off("moveend", this._panInsideMaxBounds), this._containerId !== this._container._leaflet_id) throw new Error("Map container is being reused by another instance");
        try {
          delete this._container._leaflet_id, delete this._containerId;
        } catch (t9) {
          this._container._leaflet_id = void 0, this._containerId = void 0;
        }
        for (var t8 in void 0 !== this._locationWatchId && this.stopLocate(), this._stop(), T2(this._mapPane), this._clearControlPos && this._clearControlPos(), this._resizeRequest && (r5(this._resizeRequest), this._resizeRequest = null), this._clearHandlers(), this._loaded && this.fire("unload"), this._layers) this._layers[t8].remove();
        for (t8 in this._panes) T2(this._panes[t8]);
        return this._layers = [], this._panes = [], delete this._mapPane, delete this._renderer, this;
      }, createPane: function(t8, e7) {
        e7 = P2("div", "leaflet-pane" + (t8 ? " leaflet-" + t8.replace("Pane", "") + "-pane" : ""), e7 || this._mapPane);
        return t8 && (this._panes[t8] = e7), e7;
      }, getCenter: function() {
        return this._checkIfLoaded(), this._lastCenter && !this._moved() ? this._lastCenter.clone() : this.layerPointToLatLng(this._getCenterLayerPoint());
      }, getZoom: function() {
        return this._zoom;
      }, getBounds: function() {
        var t8 = this.getPixelBounds();
        return new s4(this.unproject(t8.getBottomLeft()), this.unproject(t8.getTopRight()));
      }, getMinZoom: function() {
        return void 0 === this.options.minZoom ? this._layersMinZoom || 0 : this.options.minZoom;
      }, getMaxZoom: function() {
        return void 0 === this.options.maxZoom ? void 0 === this._layersMaxZoom ? 1 / 0 : this._layersMaxZoom : this.options.maxZoom;
      }, getBoundsZoom: function(t8, e7, i7) {
        t8 = g2(t8), i7 = m3(i7 || [0, 0]);
        var n5 = this.getZoom() || 0, o8 = this.getMinZoom(), s5 = this.getMaxZoom(), r6 = t8.getNorthWest(), t8 = t8.getSouthEast(), i7 = this.getSize().subtract(i7), t8 = _2(this.project(t8, n5), this.project(r6, n5)).getSize(), r6 = b3.any3d ? this.options.zoomSnap : 1, a4 = i7.x / t8.x, i7 = i7.y / t8.y, t8 = e7 ? Math.max(a4, i7) : Math.min(a4, i7), n5 = this.getScaleZoom(t8, n5);
        return r6 && (n5 = Math.round(n5 / (r6 / 100)) * (r6 / 100), n5 = e7 ? Math.ceil(n5 / r6) * r6 : Math.floor(n5 / r6) * r6), Math.max(o8, Math.min(s5, n5));
      }, getSize: function() {
        return this._size && !this._sizeChanged || (this._size = new p4(this._container.clientWidth || 0, this._container.clientHeight || 0), this._sizeChanged = false), this._size.clone();
      }, getPixelBounds: function(t8, e7) {
        t8 = this._getTopLeftPoint(t8, e7);
        return new f3(t8, t8.add(this.getSize()));
      }, getPixelOrigin: function() {
        return this._checkIfLoaded(), this._pixelOrigin;
      }, getPixelWorldBounds: function(t8) {
        return this.options.crs.getProjectedBounds(void 0 === t8 ? this.getZoom() : t8);
      }, getPane: function(t8) {
        return "string" == typeof t8 ? this._panes[t8] : t8;
      }, getPanes: function() {
        return this._panes;
      }, getContainer: function() {
        return this._container;
      }, getZoomScale: function(t8, e7) {
        var i7 = this.options.crs;
        return e7 = void 0 === e7 ? this._zoom : e7, i7.scale(t8) / i7.scale(e7);
      }, getScaleZoom: function(t8, e7) {
        var i7 = this.options.crs, t8 = (e7 = void 0 === e7 ? this._zoom : e7, i7.zoom(t8 * i7.scale(e7)));
        return isNaN(t8) ? 1 / 0 : t8;
      }, project: function(t8, e7) {
        return e7 = void 0 === e7 ? this._zoom : e7, this.options.crs.latLngToPoint(w2(t8), e7);
      }, unproject: function(t8, e7) {
        return e7 = void 0 === e7 ? this._zoom : e7, this.options.crs.pointToLatLng(m3(t8), e7);
      }, layerPointToLatLng: function(t8) {
        t8 = m3(t8).add(this.getPixelOrigin());
        return this.unproject(t8);
      }, latLngToLayerPoint: function(t8) {
        return this.project(w2(t8))._round()._subtract(this.getPixelOrigin());
      }, wrapLatLng: function(t8) {
        return this.options.crs.wrapLatLng(w2(t8));
      }, wrapLatLngBounds: function(t8) {
        return this.options.crs.wrapLatLngBounds(g2(t8));
      }, distance: function(t8, e7) {
        return this.options.crs.distance(w2(t8), w2(e7));
      }, containerPointToLayerPoint: function(t8) {
        return m3(t8).subtract(this._getMapPanePos());
      }, layerPointToContainerPoint: function(t8) {
        return m3(t8).add(this._getMapPanePos());
      }, containerPointToLatLng: function(t8) {
        t8 = this.containerPointToLayerPoint(m3(t8));
        return this.layerPointToLatLng(t8);
      }, latLngToContainerPoint: function(t8) {
        return this.layerPointToContainerPoint(this.latLngToLayerPoint(w2(t8)));
      }, mouseEventToContainerPoint: function(t8) {
        return De(t8, this._container);
      }, mouseEventToLayerPoint: function(t8) {
        return this.containerPointToLayerPoint(this.mouseEventToContainerPoint(t8));
      }, mouseEventToLatLng: function(t8) {
        return this.layerPointToLatLng(this.mouseEventToLayerPoint(t8));
      }, _initContainer: function(t8) {
        t8 = this._container = _e(t8);
        if (!t8) throw new Error("Map container not found.");
        if (t8._leaflet_id) throw new Error("Map container is already initialized.");
        S3(t8, "scroll", this._onScroll, this), this._containerId = h3(t8);
      }, _initLayout: function() {
        var t8 = this._container, e7 = (this._fadeAnimated = this.options.fadeAnimation && b3.any3d, M2(t8, "leaflet-container" + (b3.touch ? " leaflet-touch" : "") + (b3.retina ? " leaflet-retina" : "") + (b3.ielt9 ? " leaflet-oldie" : "") + (b3.safari ? " leaflet-safari" : "") + (this._fadeAnimated ? " leaflet-fade-anim" : "")), pe(t8, "position"));
        "absolute" !== e7 && "relative" !== e7 && "fixed" !== e7 && "sticky" !== e7 && (t8.style.position = "relative"), this._initPanes(), this._initControlPos && this._initControlPos();
      }, _initPanes: function() {
        var t8 = this._panes = {};
        this._paneRenderers = {}, this._mapPane = this.createPane("mapPane", this._container), Z2(this._mapPane, new p4(0, 0)), this.createPane("tilePane"), this.createPane("overlayPane"), this.createPane("shadowPane"), this.createPane("markerPane"), this.createPane("tooltipPane"), this.createPane("popupPane"), this.options.markerZoomAnimation || (M2(t8.markerPane, "leaflet-zoom-hide"), M2(t8.shadowPane, "leaflet-zoom-hide"));
      }, _resetView: function(t8, e7, i7) {
        Z2(this._mapPane, new p4(0, 0));
        var n5 = !this._loaded, o8 = (this._loaded = true, e7 = this._limitZoom(e7), this.fire("viewprereset"), this._zoom !== e7);
        this._moveStart(o8, i7)._move(t8, e7)._moveEnd(o8), this.fire("viewreset"), n5 && this.fire("load");
      }, _moveStart: function(t8, e7) {
        return t8 && this.fire("zoomstart"), e7 || this.fire("movestart"), this;
      }, _move: function(t8, e7, i7, n5) {
        void 0 === e7 && (e7 = this._zoom);
        var o8 = this._zoom !== e7;
        return this._zoom = e7, this._lastCenter = t8, this._pixelOrigin = this._getNewPixelOrigin(t8), n5 ? i7 && i7.pinch && this.fire("zoom", i7) : ((o8 || i7 && i7.pinch) && this.fire("zoom", i7), this.fire("move", i7)), this;
      }, _moveEnd: function(t8) {
        return t8 && this.fire("zoomend"), this.fire("moveend");
      }, _stop: function() {
        return r5(this._flyToFrame), this._panAnim && this._panAnim.stop(), this;
      }, _rawPanBy: function(t8) {
        Z2(this._mapPane, this._getMapPanePos().subtract(t8));
      }, _getZoomSpan: function() {
        return this.getMaxZoom() - this.getMinZoom();
      }, _panInsideMaxBounds: function() {
        this._enforcingBounds || this.panInsideBounds(this.options.maxBounds);
      }, _checkIfLoaded: function() {
        if (!this._loaded) throw new Error("Set map center and zoom first.");
      }, _initEvents: function(t8) {
        this._targets = {};
        var e7 = t8 ? k2 : S3;
        e7((this._targets[h3(this._container)] = this)._container, "click dblclick mousedown mouseup mouseover mouseout mousemove contextmenu keypress keydown keyup", this._handleDOMEvent, this), this.options.trackResize && e7(window, "resize", this._onResize, this), b3.any3d && this.options.transform3DLimit && (t8 ? this.off : this.on).call(this, "moveend", this._onMoveEnd);
      }, _onResize: function() {
        r5(this._resizeRequest), this._resizeRequest = x2(function() {
          this.invalidateSize({ debounceMoveend: true });
        }, this);
      }, _onScroll: function() {
        this._container.scrollTop = 0, this._container.scrollLeft = 0;
      }, _onMoveEnd: function() {
        var t8 = this._getMapPanePos();
        Math.max(Math.abs(t8.x), Math.abs(t8.y)) >= this.options.transform3DLimit && this._resetView(this.getCenter(), this.getZoom());
      }, _findEventTargets: function(t8, e7) {
        for (var i7, n5 = [], o8 = "mouseout" === e7 || "mouseover" === e7, s5 = t8.target || t8.srcElement, r6 = false; s5; ) {
          if ((i7 = this._targets[h3(s5)]) && ("click" === e7 || "preclick" === e7) && this._draggableMoved(i7)) {
            r6 = true;
            break;
          }
          if (i7 && i7.listens(e7, true)) {
            if (o8 && !We(s5, t8)) break;
            if (n5.push(i7), o8) break;
          }
          if (s5 === this._container) break;
          s5 = s5.parentNode;
        }
        return n5 = n5.length || r6 || o8 || !this.listens(e7, true) ? n5 : [this];
      }, _isClickDisabled: function(t8) {
        for (; t8 && t8 !== this._container; ) {
          if (t8._leaflet_disable_click) return true;
          t8 = t8.parentNode;
        }
      }, _handleDOMEvent: function(t8) {
        var e7, i7 = t8.target || t8.srcElement;
        !this._loaded || i7._leaflet_disable_events || "click" === t8.type && this._isClickDisabled(i7) || ("mousedown" === (e7 = t8.type) && Me(i7), this._fireDOMEvent(t8, e7));
      }, _mouseEvents: ["click", "dblclick", "mouseover", "mouseout", "contextmenu"], _fireDOMEvent: function(t8, e7, i7) {
        "click" === t8.type && ((a4 = l4({}, t8)).type = "preclick", this._fireDOMEvent(a4, a4.type, i7));
        var n5 = this._findEventTargets(t8, e7);
        if (i7) {
          for (var o8 = [], s5 = 0; s5 < i7.length; s5++) i7[s5].listens(e7, true) && o8.push(i7[s5]);
          n5 = o8.concat(n5);
        }
        if (n5.length) {
          "contextmenu" === e7 && O(t8);
          var r6, a4 = n5[0], h4 = { originalEvent: t8 };
          for ("keypress" !== t8.type && "keydown" !== t8.type && "keyup" !== t8.type && (r6 = a4.getLatLng && (!a4._radius || a4._radius <= 10), h4.containerPoint = r6 ? this.latLngToContainerPoint(a4.getLatLng()) : this.mouseEventToContainerPoint(t8), h4.layerPoint = this.containerPointToLayerPoint(h4.containerPoint), h4.latlng = r6 ? a4.getLatLng() : this.layerPointToLatLng(h4.layerPoint)), s5 = 0; s5 < n5.length; s5++) if (n5[s5].fire(e7, h4, true), h4.originalEvent._stopped || false === n5[s5].options.bubblingMouseEvents && -1 !== G(this._mouseEvents, e7)) return;
        }
      }, _draggableMoved: function(t8) {
        return (t8 = t8.dragging && t8.dragging.enabled() ? t8 : this).dragging && t8.dragging.moved() || this.boxZoom && this.boxZoom.moved();
      }, _clearHandlers: function() {
        for (var t8 = 0, e7 = this._handlers.length; t8 < e7; t8++) this._handlers[t8].disable();
      }, whenReady: function(t8, e7) {
        return this._loaded ? t8.call(e7 || this, { target: this }) : this.on("load", t8, e7), this;
      }, _getMapPanePos: function() {
        return Pe(this._mapPane) || new p4(0, 0);
      }, _moved: function() {
        var t8 = this._getMapPanePos();
        return t8 && !t8.equals([0, 0]);
      }, _getTopLeftPoint: function(t8, e7) {
        return (t8 && void 0 !== e7 ? this._getNewPixelOrigin(t8, e7) : this.getPixelOrigin()).subtract(this._getMapPanePos());
      }, _getNewPixelOrigin: function(t8, e7) {
        var i7 = this.getSize()._divideBy(2);
        return this.project(t8, e7)._subtract(i7)._add(this._getMapPanePos())._round();
      }, _latLngToNewLayerPoint: function(t8, e7, i7) {
        i7 = this._getNewPixelOrigin(i7, e7);
        return this.project(t8, e7)._subtract(i7);
      }, _latLngBoundsToNewLayerBounds: function(t8, e7, i7) {
        i7 = this._getNewPixelOrigin(i7, e7);
        return _2([this.project(t8.getSouthWest(), e7)._subtract(i7), this.project(t8.getNorthWest(), e7)._subtract(i7), this.project(t8.getSouthEast(), e7)._subtract(i7), this.project(t8.getNorthEast(), e7)._subtract(i7)]);
      }, _getCenterLayerPoint: function() {
        return this.containerPointToLayerPoint(this.getSize()._divideBy(2));
      }, _getCenterOffset: function(t8) {
        return this.latLngToLayerPoint(t8).subtract(this._getCenterLayerPoint());
      }, _limitCenter: function(t8, e7, i7) {
        var n5, o8;
        return !i7 || (n5 = this.project(t8, e7), o8 = this.getSize().divideBy(2), o8 = new f3(n5.subtract(o8), n5.add(o8)), o8 = this._getBoundsOffset(o8, i7, e7), Math.abs(o8.x) <= 1 && Math.abs(o8.y) <= 1) ? t8 : this.unproject(n5.add(o8), e7);
      }, _limitOffset: function(t8, e7) {
        var i7;
        return e7 ? (i7 = new f3((i7 = this.getPixelBounds()).min.add(t8), i7.max.add(t8)), t8.add(this._getBoundsOffset(i7, e7))) : t8;
      }, _getBoundsOffset: function(t8, e7, i7) {
        e7 = _2(this.project(e7.getNorthEast(), i7), this.project(e7.getSouthWest(), i7)), i7 = e7.min.subtract(t8.min), e7 = e7.max.subtract(t8.max);
        return new p4(this._rebound(i7.x, -e7.x), this._rebound(i7.y, -e7.y));
      }, _rebound: function(t8, e7) {
        return 0 < t8 + e7 ? Math.round(t8 - e7) / 2 : Math.max(0, Math.ceil(t8)) - Math.max(0, Math.floor(e7));
      }, _limitZoom: function(t8) {
        var e7 = this.getMinZoom(), i7 = this.getMaxZoom(), n5 = b3.any3d ? this.options.zoomSnap : 1;
        return n5 && (t8 = Math.round(t8 / n5) * n5), Math.max(e7, Math.min(i7, t8));
      }, _onPanTransitionStep: function() {
        this.fire("move");
      }, _onPanTransitionEnd: function() {
        z2(this._mapPane, "leaflet-pan-anim"), this.fire("moveend");
      }, _tryAnimatedPan: function(t8, e7) {
        t8 = this._getCenterOffset(t8)._trunc();
        return !(true !== (e7 && e7.animate) && !this.getSize().contains(t8)) && (this.panBy(t8, e7), true);
      }, _createAnimProxy: function() {
        var t8 = this._proxy = P2("div", "leaflet-proxy leaflet-zoom-animated");
        this._panes.mapPane.appendChild(t8), this.on("zoomanim", function(t9) {
          var e7 = ue, i7 = this._proxy.style[e7];
          be(this._proxy, this.project(t9.center, t9.zoom), this.getZoomScale(t9.zoom, 1)), i7 === this._proxy.style[e7] && this._animatingZoom && this._onZoomTransitionEnd();
        }, this), this.on("load moveend", this._animMoveEnd, this), this._on("unload", this._destroyAnimProxy, this);
      }, _destroyAnimProxy: function() {
        T2(this._proxy), this.off("load moveend", this._animMoveEnd, this), delete this._proxy;
      }, _animMoveEnd: function() {
        var t8 = this.getCenter(), e7 = this.getZoom();
        be(this._proxy, this.project(t8, e7), this.getZoomScale(e7, 1));
      }, _catchTransitionEnd: function(t8) {
        this._animatingZoom && 0 <= t8.propertyName.indexOf("transform") && this._onZoomTransitionEnd();
      }, _nothingToAnimate: function() {
        return !this._container.getElementsByClassName("leaflet-zoom-animated").length;
      }, _tryAnimatedZoom: function(t8, e7, i7) {
        if (!this._animatingZoom) {
          if (i7 = i7 || {}, !this._zoomAnimated || false === i7.animate || this._nothingToAnimate() || Math.abs(e7 - this._zoom) > this.options.zoomAnimationThreshold) return false;
          var n5 = this.getZoomScale(e7), n5 = this._getCenterOffset(t8)._divideBy(1 - 1 / n5);
          if (true !== i7.animate && !this.getSize().contains(n5)) return false;
          x2(function() {
            this._moveStart(true, i7.noMoveStart || false)._animateZoom(t8, e7, true);
          }, this);
        }
        return true;
      }, _animateZoom: function(t8, e7, i7, n5) {
        this._mapPane && (i7 && (this._animatingZoom = true, this._animateToCenter = t8, this._animateToZoom = e7, M2(this._mapPane, "leaflet-zoom-anim")), this.fire("zoomanim", { center: t8, zoom: e7, noUpdate: n5 }), this._tempFireZoomEvent || (this._tempFireZoomEvent = this._zoom !== this._animateToZoom), this._move(this._animateToCenter, this._animateToZoom, void 0, true), setTimeout(a3(this._onZoomTransitionEnd, this), 250));
      }, _onZoomTransitionEnd: function() {
        this._animatingZoom && (this._mapPane && z2(this._mapPane, "leaflet-zoom-anim"), this._animatingZoom = false, this._move(this._animateToCenter, this._animateToZoom, void 0, true), this._tempFireZoomEvent && this.fire("zoom"), delete this._tempFireZoomEvent, this.fire("move"), this._moveEnd(true));
      } });
      function Ue(t8) {
        return new B2(t8);
      }
      var B2 = et.extend({ options: { position: "topright" }, initialize: function(t8) {
        c4(this, t8);
      }, getPosition: function() {
        return this.options.position;
      }, setPosition: function(t8) {
        var e7 = this._map;
        return e7 && e7.removeControl(this), this.options.position = t8, e7 && e7.addControl(this), this;
      }, getContainer: function() {
        return this._container;
      }, addTo: function(t8) {
        this.remove(), this._map = t8;
        var e7 = this._container = this.onAdd(t8), i7 = this.getPosition(), t8 = t8._controlCorners[i7];
        return M2(e7, "leaflet-control"), -1 !== i7.indexOf("bottom") ? t8.insertBefore(e7, t8.firstChild) : t8.appendChild(e7), this._map.on("unload", this.remove, this), this;
      }, remove: function() {
        return this._map && (T2(this._container), this.onRemove && this.onRemove(this._map), this._map.off("unload", this.remove, this), this._map = null), this;
      }, _refocusOnMap: function(t8) {
        this._map && t8 && 0 < t8.screenX && 0 < t8.screenY && this._map.getContainer().focus();
      } }), Ve = (A2.include({ addControl: function(t8) {
        return t8.addTo(this), this;
      }, removeControl: function(t8) {
        return t8.remove(), this;
      }, _initControlPos: function() {
        var i7 = this._controlCorners = {}, n5 = "leaflet-", o8 = this._controlContainer = P2("div", n5 + "control-container", this._container);
        function t8(t9, e7) {
          i7[t9 + e7] = P2("div", n5 + t9 + " " + n5 + e7, o8);
        }
        t8("top", "left"), t8("top", "right"), t8("bottom", "left"), t8("bottom", "right");
      }, _clearControlPos: function() {
        for (var t8 in this._controlCorners) T2(this._controlCorners[t8]);
        T2(this._controlContainer), delete this._controlCorners, delete this._controlContainer;
      } }), B2.extend({ options: { collapsed: true, position: "topright", autoZIndex: true, hideSingleBase: false, sortLayers: false, sortFunction: function(t8, e7, i7, n5) {
        return i7 < n5 ? -1 : n5 < i7 ? 1 : 0;
      } }, initialize: function(t8, e7, i7) {
        for (var n5 in c4(this, i7), this._layerControlInputs = [], this._layers = [], this._lastZIndex = 0, this._handlingClick = false, this._preventClick = false, t8) this._addLayer(t8[n5], n5);
        for (n5 in e7) this._addLayer(e7[n5], n5, true);
      }, onAdd: function(t8) {
        this._initLayout(), this._update(), (this._map = t8).on("zoomend", this._checkDisabledLayers, this);
        for (var e7 = 0; e7 < this._layers.length; e7++) this._layers[e7].layer.on("add remove", this._onLayerChange, this);
        return this._container;
      }, addTo: function(t8) {
        return B2.prototype.addTo.call(this, t8), this._expandIfNotCollapsed();
      }, onRemove: function() {
        this._map.off("zoomend", this._checkDisabledLayers, this);
        for (var t8 = 0; t8 < this._layers.length; t8++) this._layers[t8].layer.off("add remove", this._onLayerChange, this);
      }, addBaseLayer: function(t8, e7) {
        return this._addLayer(t8, e7), this._map ? this._update() : this;
      }, addOverlay: function(t8, e7) {
        return this._addLayer(t8, e7, true), this._map ? this._update() : this;
      }, removeLayer: function(t8) {
        t8.off("add remove", this._onLayerChange, this);
        t8 = this._getLayer(h3(t8));
        return t8 && this._layers.splice(this._layers.indexOf(t8), 1), this._map ? this._update() : this;
      }, expand: function() {
        M2(this._container, "leaflet-control-layers-expanded"), this._section.style.height = null;
        var t8 = this._map.getSize().y - (this._container.offsetTop + 50);
        return t8 < this._section.clientHeight ? (M2(this._section, "leaflet-control-layers-scrollbar"), this._section.style.height = t8 + "px") : z2(this._section, "leaflet-control-layers-scrollbar"), this._checkDisabledLayers(), this;
      }, collapse: function() {
        return z2(this._container, "leaflet-control-layers-expanded"), this;
      }, _initLayout: function() {
        var t8 = "leaflet-control-layers", e7 = this._container = P2("div", t8), i7 = this.options.collapsed, n5 = (e7.setAttribute("aria-haspopup", true), Ie(e7), Be(e7), this._section = P2("section", t8 + "-list")), o8 = (i7 && (this._map.on("click", this.collapse, this), S3(e7, { mouseenter: this._expandSafely, mouseleave: this.collapse }, this)), this._layersLink = P2("a", t8 + "-toggle", e7));
        o8.href = "#", o8.title = "Layers", o8.setAttribute("role", "button"), S3(o8, { keydown: function(t9) {
          13 === t9.keyCode && this._expandSafely();
        }, click: function(t9) {
          O(t9), this._expandSafely();
        } }, this), i7 || this.expand(), this._baseLayersList = P2("div", t8 + "-base", n5), this._separator = P2("div", t8 + "-separator", n5), this._overlaysList = P2("div", t8 + "-overlays", n5), e7.appendChild(n5);
      }, _getLayer: function(t8) {
        for (var e7 = 0; e7 < this._layers.length; e7++) if (this._layers[e7] && h3(this._layers[e7].layer) === t8) return this._layers[e7];
      }, _addLayer: function(t8, e7, i7) {
        this._map && t8.on("add remove", this._onLayerChange, this), this._layers.push({ layer: t8, name: e7, overlay: i7 }), this.options.sortLayers && this._layers.sort(a3(function(t9, e8) {
          return this.options.sortFunction(t9.layer, e8.layer, t9.name, e8.name);
        }, this)), this.options.autoZIndex && t8.setZIndex && (this._lastZIndex++, t8.setZIndex(this._lastZIndex)), this._expandIfNotCollapsed();
      }, _update: function() {
        if (this._container) {
          me(this._baseLayersList), me(this._overlaysList), this._layerControlInputs = [];
          for (var t8, e7, i7, n5 = 0, o8 = 0; o8 < this._layers.length; o8++) i7 = this._layers[o8], this._addItem(i7), e7 = e7 || i7.overlay, t8 = t8 || !i7.overlay, n5 += i7.overlay ? 0 : 1;
          this.options.hideSingleBase && (this._baseLayersList.style.display = (t8 = t8 && 1 < n5) ? "" : "none"), this._separator.style.display = e7 && t8 ? "" : "none";
        }
        return this;
      }, _onLayerChange: function(t8) {
        this._handlingClick || this._update();
        var e7 = this._getLayer(h3(t8.target)), t8 = e7.overlay ? "add" === t8.type ? "overlayadd" : "overlayremove" : "add" === t8.type ? "baselayerchange" : null;
        t8 && this._map.fire(t8, e7);
      }, _createRadioElement: function(t8, e7) {
        t8 = '<input type="radio" class="leaflet-control-layers-selector" name="' + t8 + '"' + (e7 ? ' checked="checked"' : "") + "/>", e7 = document.createElement("div");
        return e7.innerHTML = t8, e7.firstChild;
      }, _addItem: function(t8) {
        var e7, i7 = document.createElement("label"), n5 = this._map.hasLayer(t8.layer), n5 = (t8.overlay ? ((e7 = document.createElement("input")).type = "checkbox", e7.className = "leaflet-control-layers-selector", e7.defaultChecked = n5) : e7 = this._createRadioElement("leaflet-base-layers_" + h3(this), n5), this._layerControlInputs.push(e7), e7.layerId = h3(t8.layer), S3(e7, "click", this._onInputClick, this), document.createElement("span")), o8 = (n5.innerHTML = " " + t8.name, document.createElement("span"));
        return i7.appendChild(o8), o8.appendChild(e7), o8.appendChild(n5), (t8.overlay ? this._overlaysList : this._baseLayersList).appendChild(i7), this._checkDisabledLayers(), i7;
      }, _onInputClick: function() {
        if (!this._preventClick) {
          var t8, e7, i7 = this._layerControlInputs, n5 = [], o8 = [];
          this._handlingClick = true;
          for (var s5 = i7.length - 1; 0 <= s5; s5--) t8 = i7[s5], e7 = this._getLayer(t8.layerId).layer, t8.checked ? n5.push(e7) : t8.checked || o8.push(e7);
          for (s5 = 0; s5 < o8.length; s5++) this._map.hasLayer(o8[s5]) && this._map.removeLayer(o8[s5]);
          for (s5 = 0; s5 < n5.length; s5++) this._map.hasLayer(n5[s5]) || this._map.addLayer(n5[s5]);
          this._handlingClick = false, this._refocusOnMap();
        }
      }, _checkDisabledLayers: function() {
        for (var t8, e7, i7 = this._layerControlInputs, n5 = this._map.getZoom(), o8 = i7.length - 1; 0 <= o8; o8--) t8 = i7[o8], e7 = this._getLayer(t8.layerId).layer, t8.disabled = void 0 !== e7.options.minZoom && n5 < e7.options.minZoom || void 0 !== e7.options.maxZoom && n5 > e7.options.maxZoom;
      }, _expandIfNotCollapsed: function() {
        return this._map && !this.options.collapsed && this.expand(), this;
      }, _expandSafely: function() {
        var t8 = this._section, e7 = (this._preventClick = true, S3(t8, "click", O), this.expand(), this);
        setTimeout(function() {
          k2(t8, "click", O), e7._preventClick = false;
        });
      } })), qe = B2.extend({ options: { position: "topleft", zoomInText: '<span aria-hidden="true">+</span>', zoomInTitle: "Zoom in", zoomOutText: '<span aria-hidden="true">&#x2212;</span>', zoomOutTitle: "Zoom out" }, onAdd: function(t8) {
        var e7 = "leaflet-control-zoom", i7 = P2("div", e7 + " leaflet-bar"), n5 = this.options;
        return this._zoomInButton = this._createButton(n5.zoomInText, n5.zoomInTitle, e7 + "-in", i7, this._zoomIn), this._zoomOutButton = this._createButton(n5.zoomOutText, n5.zoomOutTitle, e7 + "-out", i7, this._zoomOut), this._updateDisabled(), t8.on("zoomend zoomlevelschange", this._updateDisabled, this), i7;
      }, onRemove: function(t8) {
        t8.off("zoomend zoomlevelschange", this._updateDisabled, this);
      }, disable: function() {
        return this._disabled = true, this._updateDisabled(), this;
      }, enable: function() {
        return this._disabled = false, this._updateDisabled(), this;
      }, _zoomIn: function(t8) {
        !this._disabled && this._map._zoom < this._map.getMaxZoom() && this._map.zoomIn(this._map.options.zoomDelta * (t8.shiftKey ? 3 : 1));
      }, _zoomOut: function(t8) {
        !this._disabled && this._map._zoom > this._map.getMinZoom() && this._map.zoomOut(this._map.options.zoomDelta * (t8.shiftKey ? 3 : 1));
      }, _createButton: function(t8, e7, i7, n5, o8) {
        i7 = P2("a", i7, n5);
        return i7.innerHTML = t8, i7.href = "#", i7.title = e7, i7.setAttribute("role", "button"), i7.setAttribute("aria-label", e7), Ie(i7), S3(i7, "click", Re), S3(i7, "click", o8, this), S3(i7, "click", this._refocusOnMap, this), i7;
      }, _updateDisabled: function() {
        var t8 = this._map, e7 = "leaflet-disabled";
        z2(this._zoomInButton, e7), z2(this._zoomOutButton, e7), this._zoomInButton.setAttribute("aria-disabled", "false"), this._zoomOutButton.setAttribute("aria-disabled", "false"), !this._disabled && t8._zoom !== t8.getMinZoom() || (M2(this._zoomOutButton, e7), this._zoomOutButton.setAttribute("aria-disabled", "true")), !this._disabled && t8._zoom !== t8.getMaxZoom() || (M2(this._zoomInButton, e7), this._zoomInButton.setAttribute("aria-disabled", "true"));
      } }), Ge = (A2.mergeOptions({ zoomControl: true }), A2.addInitHook(function() {
        this.options.zoomControl && (this.zoomControl = new qe(), this.addControl(this.zoomControl));
      }), B2.extend({ options: { position: "bottomleft", maxWidth: 100, metric: true, imperial: true }, onAdd: function(t8) {
        var e7 = "leaflet-control-scale", i7 = P2("div", e7), n5 = this.options;
        return this._addScales(n5, e7 + "-line", i7), t8.on(n5.updateWhenIdle ? "moveend" : "move", this._update, this), t8.whenReady(this._update, this), i7;
      }, onRemove: function(t8) {
        t8.off(this.options.updateWhenIdle ? "moveend" : "move", this._update, this);
      }, _addScales: function(t8, e7, i7) {
        t8.metric && (this._mScale = P2("div", e7, i7)), t8.imperial && (this._iScale = P2("div", e7, i7));
      }, _update: function() {
        var t8 = this._map, e7 = t8.getSize().y / 2, t8 = t8.distance(t8.containerPointToLatLng([0, e7]), t8.containerPointToLatLng([this.options.maxWidth, e7]));
        this._updateScales(t8);
      }, _updateScales: function(t8) {
        this.options.metric && t8 && this._updateMetric(t8), this.options.imperial && t8 && this._updateImperial(t8);
      }, _updateMetric: function(t8) {
        var e7 = this._getRoundNum(t8);
        this._updateScale(this._mScale, e7 < 1e3 ? e7 + " m" : e7 / 1e3 + " km", e7 / t8);
      }, _updateImperial: function(t8) {
        var e7, i7, t8 = 3.2808399 * t8;
        5280 < t8 ? (i7 = this._getRoundNum(e7 = t8 / 5280), this._updateScale(this._iScale, i7 + " mi", i7 / e7)) : (i7 = this._getRoundNum(t8), this._updateScale(this._iScale, i7 + " ft", i7 / t8));
      }, _updateScale: function(t8, e7, i7) {
        t8.style.width = Math.round(this.options.maxWidth * i7) + "px", t8.innerHTML = e7;
      }, _getRoundNum: function(t8) {
        var e7 = Math.pow(10, (Math.floor(t8) + "").length - 1), t8 = t8 / e7;
        return e7 * (t8 = 10 <= t8 ? 10 : 5 <= t8 ? 5 : 3 <= t8 ? 3 : 2 <= t8 ? 2 : 1);
      } })), Ke = B2.extend({ options: { position: "bottomright", prefix: '<a href="https://leafletjs.com" title="A JavaScript library for interactive maps">' + (b3.inlineSvg ? '<svg aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="12" height="8" viewBox="0 0 12 8" class="leaflet-attribution-flag"><path fill="#4C7BE1" d="M0 0h12v4H0z"/><path fill="#FFD500" d="M0 4h12v3H0z"/><path fill="#E0BC00" d="M0 7h12v1H0z"/></svg> ' : "") + "Leaflet</a>" }, initialize: function(t8) {
        c4(this, t8), this._attributions = {};
      }, onAdd: function(t8) {
        for (var e7 in (t8.attributionControl = this)._container = P2("div", "leaflet-control-attribution"), Ie(this._container), t8._layers) t8._layers[e7].getAttribution && this.addAttribution(t8._layers[e7].getAttribution());
        return this._update(), t8.on("layeradd", this._addAttribution, this), this._container;
      }, onRemove: function(t8) {
        t8.off("layeradd", this._addAttribution, this);
      }, _addAttribution: function(t8) {
        t8.layer.getAttribution && (this.addAttribution(t8.layer.getAttribution()), t8.layer.once("remove", function() {
          this.removeAttribution(t8.layer.getAttribution());
        }, this));
      }, setPrefix: function(t8) {
        return this.options.prefix = t8, this._update(), this;
      }, addAttribution: function(t8) {
        return t8 && (this._attributions[t8] || (this._attributions[t8] = 0), this._attributions[t8]++, this._update()), this;
      }, removeAttribution: function(t8) {
        return t8 && this._attributions[t8] && (this._attributions[t8]--, this._update()), this;
      }, _update: function() {
        if (this._map) {
          var t8, e7 = [];
          for (t8 in this._attributions) this._attributions[t8] && e7.push(t8);
          var i7 = [];
          this.options.prefix && i7.push(this.options.prefix), e7.length && i7.push(e7.join(", ")), this._container.innerHTML = i7.join(' <span aria-hidden="true">|</span> ');
        }
      } }), n4 = (A2.mergeOptions({ attributionControl: true }), A2.addInitHook(function() {
        this.options.attributionControl && new Ke().addTo(this);
      }), B2.Layers = Ve, B2.Zoom = qe, B2.Scale = Ge, B2.Attribution = Ke, Ue.layers = function(t8, e7, i7) {
        return new Ve(t8, e7, i7);
      }, Ue.zoom = function(t8) {
        return new qe(t8);
      }, Ue.scale = function(t8) {
        return new Ge(t8);
      }, Ue.attribution = function(t8) {
        return new Ke(t8);
      }, et.extend({ initialize: function(t8) {
        this._map = t8;
      }, enable: function() {
        return this._enabled || (this._enabled = true, this.addHooks()), this;
      }, disable: function() {
        return this._enabled && (this._enabled = false, this.removeHooks()), this;
      }, enabled: function() {
        return !!this._enabled;
      } })), ft = (n4.addTo = function(t8, e7) {
        return t8.addHandler(e7, this), this;
      }, { Events: e6 }), Ye = b3.touch ? "touchstart mousedown" : "mousedown", Xe = it.extend({ options: { clickTolerance: 3 }, initialize: function(t8, e7, i7, n5) {
        c4(this, n5), this._element = t8, this._dragStartTarget = e7 || t8, this._preventOutline = i7;
      }, enable: function() {
        this._enabled || (S3(this._dragStartTarget, Ye, this._onDown, this), this._enabled = true);
      }, disable: function() {
        this._enabled && (Xe._dragging === this && this.finishDrag(true), k2(this._dragStartTarget, Ye, this._onDown, this), this._enabled = false, this._moved = false);
      }, _onDown: function(t8) {
        var e7, i7;
        this._enabled && (this._moved = false, ve(this._element, "leaflet-zoom-anim") || (t8.touches && 1 !== t8.touches.length ? Xe._dragging === this && this.finishDrag() : Xe._dragging || t8.shiftKey || 1 !== t8.which && 1 !== t8.button && !t8.touches || ((Xe._dragging = this)._preventOutline && Me(this._element), Le(), re(), this._moving || (this.fire("down"), i7 = t8.touches ? t8.touches[0] : t8, e7 = Ce(this._element), this._startPoint = new p4(i7.clientX, i7.clientY), this._startPos = Pe(this._element), this._parentScale = Ze(e7), i7 = "mousedown" === t8.type, S3(document, i7 ? "mousemove" : "touchmove", this._onMove, this), S3(document, i7 ? "mouseup" : "touchend touchcancel", this._onUp, this)))));
      }, _onMove: function(t8) {
        var e7;
        this._enabled && (t8.touches && 1 < t8.touches.length ? this._moved = true : !(e7 = new p4((e7 = t8.touches && 1 === t8.touches.length ? t8.touches[0] : t8).clientX, e7.clientY)._subtract(this._startPoint)).x && !e7.y || Math.abs(e7.x) + Math.abs(e7.y) < this.options.clickTolerance || (e7.x /= this._parentScale.x, e7.y /= this._parentScale.y, O(t8), this._moved || (this.fire("dragstart"), this._moved = true, M2(document.body, "leaflet-dragging"), this._lastTarget = t8.target || t8.srcElement, window.SVGElementInstance && this._lastTarget instanceof window.SVGElementInstance && (this._lastTarget = this._lastTarget.correspondingUseElement), M2(this._lastTarget, "leaflet-drag-target")), this._newPos = this._startPos.add(e7), this._moving = true, this._lastEvent = t8, this._updatePosition()));
      }, _updatePosition: function() {
        var t8 = { originalEvent: this._lastEvent };
        this.fire("predrag", t8), Z2(this._element, this._newPos), this.fire("drag", t8);
      }, _onUp: function() {
        this._enabled && this.finishDrag();
      }, finishDrag: function(t8) {
        z2(document.body, "leaflet-dragging"), this._lastTarget && (z2(this._lastTarget, "leaflet-drag-target"), this._lastTarget = null), k2(document, "mousemove touchmove", this._onMove, this), k2(document, "mouseup touchend touchcancel", this._onUp, this), Te(), ae();
        var e7 = this._moved && this._moving;
        this._moving = false, Xe._dragging = false, e7 && this.fire("dragend", { noInertia: t8, distance: this._newPos.distanceTo(this._startPos) });
      } });
      function Je(t8, e7, i7) {
        for (var n5, o8, s5, r6, a4, h4, l5, u4 = [1, 4, 2, 8], c5 = 0, d4 = t8.length; c5 < d4; c5++) t8[c5]._code = si(t8[c5], e7);
        for (s5 = 0; s5 < 4; s5++) {
          for (h4 = u4[s5], n5 = [], c5 = 0, o8 = (d4 = t8.length) - 1; c5 < d4; o8 = c5++) r6 = t8[c5], a4 = t8[o8], r6._code & h4 ? a4._code & h4 || ((l5 = oi(a4, r6, h4, e7, i7))._code = si(l5, e7), n5.push(l5)) : (a4._code & h4 && ((l5 = oi(a4, r6, h4, e7, i7))._code = si(l5, e7), n5.push(l5)), n5.push(r6));
          t8 = n5;
        }
        return t8;
      }
      function $e(t8, e7) {
        var i7, n5, o8, s5, r6, a4, h4;
        if (!t8 || 0 === t8.length) throw new Error("latlngs not passed");
        I2(t8) || (console.warn("latlngs are not flat! Only the first ring will be used"), t8 = t8[0]);
        for (var l5 = w2([0, 0]), u4 = g2(t8), c5 = (u4.getNorthWest().distanceTo(u4.getSouthWest()) * u4.getNorthEast().distanceTo(u4.getNorthWest()) < 1700 && (l5 = Qe(t8)), t8.length), d4 = [], _3 = 0; _3 < c5; _3++) {
          var p5 = w2(t8[_3]);
          d4.push(e7.project(w2([p5.lat - l5.lat, p5.lng - l5.lng])));
        }
        for (_3 = r6 = a4 = h4 = 0, i7 = c5 - 1; _3 < c5; i7 = _3++) n5 = d4[_3], o8 = d4[i7], s5 = n5.y * o8.x - o8.y * n5.x, a4 += (n5.x + o8.x) * s5, h4 += (n5.y + o8.y) * s5, r6 += 3 * s5;
        u4 = 0 === r6 ? d4[0] : [a4 / r6, h4 / r6], u4 = e7.unproject(m3(u4));
        return w2([u4.lat + l5.lat, u4.lng + l5.lng]);
      }
      function Qe(t8) {
        for (var e7 = 0, i7 = 0, n5 = 0, o8 = 0; o8 < t8.length; o8++) {
          var s5 = w2(t8[o8]);
          e7 += s5.lat, i7 += s5.lng, n5++;
        }
        return w2([e7 / n5, i7 / n5]);
      }
      var ti, gt = { __proto__: null, clipPolygon: Je, polygonCenter: $e, centroid: Qe };
      function ei(t8, e7) {
        if (e7 && t8.length) {
          var i7 = t8 = (function(t9, e8) {
            for (var i8 = [t9[0]], n6 = 1, o9 = 0, s6 = t9.length; n6 < s6; n6++) (function(t10, e9) {
              var i9 = e9.x - t10.x, e9 = e9.y - t10.y;
              return i9 * i9 + e9 * e9;
            })(t9[n6], t9[o9]) > e8 && (i8.push(t9[n6]), o9 = n6);
            o9 < s6 - 1 && i8.push(t9[s6 - 1]);
            return i8;
          })(t8, e7 = e7 * e7), n5 = i7.length, o8 = new (typeof Uint8Array != "undefined" ? Uint8Array : Array)(n5);
          o8[0] = o8[n5 - 1] = 1, (function t9(e8, i8, n6, o9, s6) {
            var r7, a4, h4, l5 = 0;
            for (a4 = o9 + 1; a4 <= s6 - 1; a4++) h4 = ri(e8[a4], e8[o9], e8[s6], true), l5 < h4 && (r7 = a4, l5 = h4);
            n6 < l5 && (i8[r7] = 1, t9(e8, i8, n6, o9, r7), t9(e8, i8, n6, r7, s6));
          })(i7, o8, e7, 0, n5 - 1);
          var s5, r6 = [];
          for (s5 = 0; s5 < n5; s5++) o8[s5] && r6.push(i7[s5]);
          return r6;
        }
        return t8.slice();
      }
      function ii(t8, e7, i7) {
        return Math.sqrt(ri(t8, e7, i7, true));
      }
      function ni(t8, e7, i7, n5, o8) {
        var s5, r6, a4, h4 = n5 ? ti : si(t8, i7), l5 = si(e7, i7);
        for (ti = l5; ; ) {
          if (!(h4 | l5)) return [t8, e7];
          if (h4 & l5) return false;
          a4 = si(r6 = oi(t8, e7, s5 = h4 || l5, i7, o8), i7), s5 === h4 ? (t8 = r6, h4 = a4) : (e7 = r6, l5 = a4);
        }
      }
      function oi(t8, e7, i7, n5, o8) {
        var s5, r6, a4 = e7.x - t8.x, e7 = e7.y - t8.y, h4 = n5.min, n5 = n5.max;
        return 8 & i7 ? (s5 = t8.x + a4 * (n5.y - t8.y) / e7, r6 = n5.y) : 4 & i7 ? (s5 = t8.x + a4 * (h4.y - t8.y) / e7, r6 = h4.y) : 2 & i7 ? (s5 = n5.x, r6 = t8.y + e7 * (n5.x - t8.x) / a4) : 1 & i7 && (s5 = h4.x, r6 = t8.y + e7 * (h4.x - t8.x) / a4), new p4(s5, r6, o8);
      }
      function si(t8, e7) {
        var i7 = 0;
        return t8.x < e7.min.x ? i7 |= 1 : t8.x > e7.max.x && (i7 |= 2), t8.y < e7.min.y ? i7 |= 4 : t8.y > e7.max.y && (i7 |= 8), i7;
      }
      function ri(t8, e7, i7, n5) {
        var o8 = e7.x, e7 = e7.y, s5 = i7.x - o8, r6 = i7.y - e7, a4 = s5 * s5 + r6 * r6;
        return 0 < a4 && (1 < (a4 = ((t8.x - o8) * s5 + (t8.y - e7) * r6) / a4) ? (o8 = i7.x, e7 = i7.y) : 0 < a4 && (o8 += s5 * a4, e7 += r6 * a4)), s5 = t8.x - o8, r6 = t8.y - e7, n5 ? s5 * s5 + r6 * r6 : new p4(o8, e7);
      }
      function I2(t8) {
        return !d3(t8[0]) || "object" != typeof t8[0][0] && void 0 !== t8[0][0];
      }
      function ai(t8) {
        return console.warn("Deprecated use of _flat, please use L.LineUtil.isFlat instead."), I2(t8);
      }
      function hi(t8, e7) {
        var i7, n5, o8, s5, r6, a4;
        if (!t8 || 0 === t8.length) throw new Error("latlngs not passed");
        I2(t8) || (console.warn("latlngs are not flat! Only the first ring will be used"), t8 = t8[0]);
        for (var h4 = w2([0, 0]), l5 = g2(t8), u4 = (l5.getNorthWest().distanceTo(l5.getSouthWest()) * l5.getNorthEast().distanceTo(l5.getNorthWest()) < 1700 && (h4 = Qe(t8)), t8.length), c5 = [], d4 = 0; d4 < u4; d4++) {
          var _3 = w2(t8[d4]);
          c5.push(e7.project(w2([_3.lat - h4.lat, _3.lng - h4.lng])));
        }
        for (i7 = d4 = 0; d4 < u4 - 1; d4++) i7 += c5[d4].distanceTo(c5[d4 + 1]) / 2;
        if (0 === i7) a4 = c5[0];
        else for (n5 = d4 = 0; d4 < u4 - 1; d4++) if (o8 = c5[d4], s5 = c5[d4 + 1], i7 < (n5 += r6 = o8.distanceTo(s5))) {
          a4 = [s5.x - (r6 = (n5 - i7) / r6) * (s5.x - o8.x), s5.y - r6 * (s5.y - o8.y)];
          break;
        }
        l5 = e7.unproject(m3(a4));
        return w2([l5.lat + h4.lat, l5.lng + h4.lng]);
      }
      var vt = { __proto__: null, simplify: ei, pointToSegmentDistance: ii, closestPointOnSegment: function(t8, e7, i7) {
        return ri(t8, e7, i7);
      }, clipSegment: ni, _getEdgeIntersection: oi, _getBitCode: si, _sqClosestPointOnSegment: ri, isFlat: I2, _flat: ai, polylineCenter: hi }, yt = { project: function(t8) {
        return new p4(t8.lng, t8.lat);
      }, unproject: function(t8) {
        return new v2(t8.y, t8.x);
      }, bounds: new f3([-180, -90], [180, 90]) }, xt = { R: 6378137, R_MINOR: 6356752314245179e-9, bounds: new f3([-2003750834279e-5, -1549657073972e-5], [2003750834279e-5, 1876465623138e-5]), project: function(t8) {
        var e7 = Math.PI / 180, i7 = this.R, n5 = t8.lat * e7, o8 = this.R_MINOR / i7, o8 = Math.sqrt(1 - o8 * o8), s5 = o8 * Math.sin(n5), s5 = Math.tan(Math.PI / 4 - n5 / 2) / Math.pow((1 - s5) / (1 + s5), o8 / 2), n5 = -i7 * Math.log(Math.max(s5, 1e-10));
        return new p4(t8.lng * e7 * i7, n5);
      }, unproject: function(t8) {
        for (var e7, i7 = 180 / Math.PI, n5 = this.R, o8 = this.R_MINOR / n5, s5 = Math.sqrt(1 - o8 * o8), r6 = Math.exp(-t8.y / n5), a4 = Math.PI / 2 - 2 * Math.atan(r6), h4 = 0, l5 = 0.1; h4 < 15 && 1e-7 < Math.abs(l5); h4++) e7 = s5 * Math.sin(a4), e7 = Math.pow((1 - e7) / (1 + e7), s5 / 2), a4 += l5 = Math.PI / 2 - 2 * Math.atan(r6 * e7) - a4;
        return new v2(a4 * i7, t8.x * i7 / n5);
      } }, wt = { __proto__: null, LonLat: yt, Mercator: xt, SphericalMercator: rt }, Pt = l4({}, st, { code: "EPSG:3395", projection: xt, transformation: ht(bt = 0.5 / (Math.PI * xt.R), 0.5, -bt, 0.5) }), li = l4({}, st, { code: "EPSG:4326", projection: yt, transformation: ht(1 / 180, 1, -1 / 180, 0.5) }), Lt = l4({}, ot, { projection: yt, transformation: ht(1, 0, -1, 0), scale: function(t8) {
        return Math.pow(2, t8);
      }, zoom: function(t8) {
        return Math.log(t8) / Math.LN2;
      }, distance: function(t8, e7) {
        var i7 = e7.lng - t8.lng, e7 = e7.lat - t8.lat;
        return Math.sqrt(i7 * i7 + e7 * e7);
      }, infinite: true }), o7 = (ot.Earth = st, ot.EPSG3395 = Pt, ot.EPSG3857 = lt, ot.EPSG900913 = ut, ot.EPSG4326 = li, ot.Simple = Lt, it.extend({ options: { pane: "overlayPane", attribution: null, bubblingMouseEvents: true }, addTo: function(t8) {
        return t8.addLayer(this), this;
      }, remove: function() {
        return this.removeFrom(this._map || this._mapToAdd);
      }, removeFrom: function(t8) {
        return t8 && t8.removeLayer(this), this;
      }, getPane: function(t8) {
        return this._map.getPane(t8 ? this.options[t8] || t8 : this.options.pane);
      }, addInteractiveTarget: function(t8) {
        return this._map._targets[h3(t8)] = this;
      }, removeInteractiveTarget: function(t8) {
        return delete this._map._targets[h3(t8)], this;
      }, getAttribution: function() {
        return this.options.attribution;
      }, _layerAdd: function(t8) {
        var e7, i7 = t8.target;
        i7.hasLayer(this) && (this._map = i7, this._zoomAnimated = i7._zoomAnimated, this.getEvents && (e7 = this.getEvents(), i7.on(e7, this), this.once("remove", function() {
          i7.off(e7, this);
        }, this)), this.onAdd(i7), this.fire("add"), i7.fire("layeradd", { layer: this }));
      } })), ui = (A2.include({ addLayer: function(t8) {
        var e7;
        if (t8._layerAdd) return e7 = h3(t8), this._layers[e7] || ((this._layers[e7] = t8)._mapToAdd = this, t8.beforeAdd && t8.beforeAdd(this), this.whenReady(t8._layerAdd, t8)), this;
        throw new Error("The provided object is not a Layer.");
      }, removeLayer: function(t8) {
        var e7 = h3(t8);
        return this._layers[e7] && (this._loaded && t8.onRemove(this), delete this._layers[e7], this._loaded && (this.fire("layerremove", { layer: t8 }), t8.fire("remove")), t8._map = t8._mapToAdd = null), this;
      }, hasLayer: function(t8) {
        return h3(t8) in this._layers;
      }, eachLayer: function(t8, e7) {
        for (var i7 in this._layers) t8.call(e7, this._layers[i7]);
        return this;
      }, _addLayers: function(t8) {
        for (var e7 = 0, i7 = (t8 = t8 ? d3(t8) ? t8 : [t8] : []).length; e7 < i7; e7++) this.addLayer(t8[e7]);
      }, _addZoomLimit: function(t8) {
        isNaN(t8.options.maxZoom) && isNaN(t8.options.minZoom) || (this._zoomBoundLayers[h3(t8)] = t8, this._updateZoomLevels());
      }, _removeZoomLimit: function(t8) {
        t8 = h3(t8);
        this._zoomBoundLayers[t8] && (delete this._zoomBoundLayers[t8], this._updateZoomLevels());
      }, _updateZoomLevels: function() {
        var t8, e7 = 1 / 0, i7 = -1 / 0, n5 = this._getZoomSpan();
        for (t8 in this._zoomBoundLayers) var o8 = this._zoomBoundLayers[t8].options, e7 = void 0 === o8.minZoom ? e7 : Math.min(e7, o8.minZoom), i7 = void 0 === o8.maxZoom ? i7 : Math.max(i7, o8.maxZoom);
        this._layersMaxZoom = i7 === -1 / 0 ? void 0 : i7, this._layersMinZoom = e7 === 1 / 0 ? void 0 : e7, n5 !== this._getZoomSpan() && this.fire("zoomlevelschange"), void 0 === this.options.maxZoom && this._layersMaxZoom && this.getZoom() > this._layersMaxZoom && this.setZoom(this._layersMaxZoom), void 0 === this.options.minZoom && this._layersMinZoom && this.getZoom() < this._layersMinZoom && this.setZoom(this._layersMinZoom);
      } }), o7.extend({ initialize: function(t8, e7) {
        var i7, n5;
        if (c4(this, e7), this._layers = {}, t8) for (i7 = 0, n5 = t8.length; i7 < n5; i7++) this.addLayer(t8[i7]);
      }, addLayer: function(t8) {
        var e7 = this.getLayerId(t8);
        return this._layers[e7] = t8, this._map && this._map.addLayer(t8), this;
      }, removeLayer: function(t8) {
        t8 = t8 in this._layers ? t8 : this.getLayerId(t8);
        return this._map && this._layers[t8] && this._map.removeLayer(this._layers[t8]), delete this._layers[t8], this;
      }, hasLayer: function(t8) {
        return ("number" == typeof t8 ? t8 : this.getLayerId(t8)) in this._layers;
      }, clearLayers: function() {
        return this.eachLayer(this.removeLayer, this);
      }, invoke: function(t8) {
        var e7, i7, n5 = Array.prototype.slice.call(arguments, 1);
        for (e7 in this._layers) (i7 = this._layers[e7])[t8] && i7[t8].apply(i7, n5);
        return this;
      }, onAdd: function(t8) {
        this.eachLayer(t8.addLayer, t8);
      }, onRemove: function(t8) {
        this.eachLayer(t8.removeLayer, t8);
      }, eachLayer: function(t8, e7) {
        for (var i7 in this._layers) t8.call(e7, this._layers[i7]);
        return this;
      }, getLayer: function(t8) {
        return this._layers[t8];
      }, getLayers: function() {
        var t8 = [];
        return this.eachLayer(t8.push, t8), t8;
      }, setZIndex: function(t8) {
        return this.invoke("setZIndex", t8);
      }, getLayerId: h3 })), ci = ui.extend({ addLayer: function(t8) {
        return this.hasLayer(t8) ? this : (t8.addEventParent(this), ui.prototype.addLayer.call(this, t8), this.fire("layeradd", { layer: t8 }));
      }, removeLayer: function(t8) {
        return this.hasLayer(t8) ? ((t8 = t8 in this._layers ? this._layers[t8] : t8).removeEventParent(this), ui.prototype.removeLayer.call(this, t8), this.fire("layerremove", { layer: t8 })) : this;
      }, setStyle: function(t8) {
        return this.invoke("setStyle", t8);
      }, bringToFront: function() {
        return this.invoke("bringToFront");
      }, bringToBack: function() {
        return this.invoke("bringToBack");
      }, getBounds: function() {
        var t8, e7 = new s4();
        for (t8 in this._layers) {
          var i7 = this._layers[t8];
          e7.extend(i7.getBounds ? i7.getBounds() : i7.getLatLng());
        }
        return e7;
      } }), di = et.extend({ options: { popupAnchor: [0, 0], tooltipAnchor: [0, 0], crossOrigin: false }, initialize: function(t8) {
        c4(this, t8);
      }, createIcon: function(t8) {
        return this._createIcon("icon", t8);
      }, createShadow: function(t8) {
        return this._createIcon("shadow", t8);
      }, _createIcon: function(t8, e7) {
        var i7 = this._getIconUrl(t8);
        if (i7) return i7 = this._createImg(i7, e7 && "IMG" === e7.tagName ? e7 : null), this._setIconStyles(i7, t8), !this.options.crossOrigin && "" !== this.options.crossOrigin || (i7.crossOrigin = true === this.options.crossOrigin ? "" : this.options.crossOrigin), i7;
        if ("icon" === t8) throw new Error("iconUrl not set in Icon options (see the docs).");
        return null;
      }, _setIconStyles: function(t8, e7) {
        var i7 = this.options, n5 = i7[e7 + "Size"], n5 = m3(n5 = "number" == typeof n5 ? [n5, n5] : n5), o8 = m3("shadow" === e7 && i7.shadowAnchor || i7.iconAnchor || n5 && n5.divideBy(2, true));
        t8.className = "leaflet-marker-" + e7 + " " + (i7.className || ""), o8 && (t8.style.marginLeft = -o8.x + "px", t8.style.marginTop = -o8.y + "px"), n5 && (t8.style.width = n5.x + "px", t8.style.height = n5.y + "px");
      }, _createImg: function(t8, e7) {
        return (e7 = e7 || document.createElement("img")).src = t8, e7;
      }, _getIconUrl: function(t8) {
        return b3.retina && this.options[t8 + "RetinaUrl"] || this.options[t8 + "Url"];
      } });
      var _i = di.extend({ options: { iconUrl: "marker-icon.png", iconRetinaUrl: "marker-icon-2x.png", shadowUrl: "marker-shadow.png", iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], tooltipAnchor: [16, -28], shadowSize: [41, 41] }, _getIconUrl: function(t8) {
        return "string" != typeof _i.imagePath && (_i.imagePath = this._detectIconPath()), (this.options.imagePath || _i.imagePath) + di.prototype._getIconUrl.call(this, t8);
      }, _stripUrl: function(t8) {
        function e7(t9, e8, i7) {
          return (e8 = e8.exec(t9)) && e8[i7];
        }
        return (t8 = e7(t8, /^url\((['"])?(.+)\1\)$/, 2)) && e7(t8, /^(.*)marker-icon\.png$/, 1);
      }, _detectIconPath: function() {
        var t8 = P2("div", "leaflet-default-icon-path", document.body), e7 = pe(t8, "background-image") || pe(t8, "backgroundImage");
        return document.body.removeChild(t8), (e7 = this._stripUrl(e7)) ? e7 : (t8 = document.querySelector('link[href$="leaflet.css"]')) ? t8.href.substring(0, t8.href.length - "leaflet.css".length - 1) : "";
      } }), pi = n4.extend({ initialize: function(t8) {
        this._marker = t8;
      }, addHooks: function() {
        var t8 = this._marker._icon;
        this._draggable || (this._draggable = new Xe(t8, t8, true)), this._draggable.on({ dragstart: this._onDragStart, predrag: this._onPreDrag, drag: this._onDrag, dragend: this._onDragEnd }, this).enable(), M2(t8, "leaflet-marker-draggable");
      }, removeHooks: function() {
        this._draggable.off({ dragstart: this._onDragStart, predrag: this._onPreDrag, drag: this._onDrag, dragend: this._onDragEnd }, this).disable(), this._marker._icon && z2(this._marker._icon, "leaflet-marker-draggable");
      }, moved: function() {
        return this._draggable && this._draggable._moved;
      }, _adjustPan: function(t8) {
        var e7 = this._marker, i7 = e7._map, n5 = this._marker.options.autoPanSpeed, o8 = this._marker.options.autoPanPadding, s5 = Pe(e7._icon), r6 = i7.getPixelBounds(), a4 = i7.getPixelOrigin(), a4 = _2(r6.min._subtract(a4).add(o8), r6.max._subtract(a4).subtract(o8));
        a4.contains(s5) || (o8 = m3((Math.max(a4.max.x, s5.x) - a4.max.x) / (r6.max.x - a4.max.x) - (Math.min(a4.min.x, s5.x) - a4.min.x) / (r6.min.x - a4.min.x), (Math.max(a4.max.y, s5.y) - a4.max.y) / (r6.max.y - a4.max.y) - (Math.min(a4.min.y, s5.y) - a4.min.y) / (r6.min.y - a4.min.y)).multiplyBy(n5), i7.panBy(o8, { animate: false }), this._draggable._newPos._add(o8), this._draggable._startPos._add(o8), Z2(e7._icon, this._draggable._newPos), this._onDrag(t8), this._panRequest = x2(this._adjustPan.bind(this, t8)));
      }, _onDragStart: function() {
        this._oldLatLng = this._marker.getLatLng(), this._marker.closePopup && this._marker.closePopup(), this._marker.fire("movestart").fire("dragstart");
      }, _onPreDrag: function(t8) {
        this._marker.options.autoPan && (r5(this._panRequest), this._panRequest = x2(this._adjustPan.bind(this, t8)));
      }, _onDrag: function(t8) {
        var e7 = this._marker, i7 = e7._shadow, n5 = Pe(e7._icon), o8 = e7._map.layerPointToLatLng(n5);
        i7 && Z2(i7, n5), e7._latlng = o8, t8.latlng = o8, t8.oldLatLng = this._oldLatLng, e7.fire("move", t8).fire("drag", t8);
      }, _onDragEnd: function(t8) {
        r5(this._panRequest), delete this._oldLatLng, this._marker.fire("moveend").fire("dragend", t8);
      } }), mi = o7.extend({ options: { icon: new _i(), interactive: true, keyboard: true, title: "", alt: "Marker", zIndexOffset: 0, opacity: 1, riseOnHover: false, riseOffset: 250, pane: "markerPane", shadowPane: "shadowPane", bubblingMouseEvents: false, autoPanOnFocus: true, draggable: false, autoPan: false, autoPanPadding: [50, 50], autoPanSpeed: 10 }, initialize: function(t8, e7) {
        c4(this, e7), this._latlng = w2(t8);
      }, onAdd: function(t8) {
        this._zoomAnimated = this._zoomAnimated && t8.options.markerZoomAnimation, this._zoomAnimated && t8.on("zoomanim", this._animateZoom, this), this._initIcon(), this.update();
      }, onRemove: function(t8) {
        this.dragging && this.dragging.enabled() && (this.options.draggable = true, this.dragging.removeHooks()), delete this.dragging, this._zoomAnimated && t8.off("zoomanim", this._animateZoom, this), this._removeIcon(), this._removeShadow();
      }, getEvents: function() {
        return { zoom: this.update, viewreset: this.update };
      }, getLatLng: function() {
        return this._latlng;
      }, setLatLng: function(t8) {
        var e7 = this._latlng;
        return this._latlng = w2(t8), this.update(), this.fire("move", { oldLatLng: e7, latlng: this._latlng });
      }, setZIndexOffset: function(t8) {
        return this.options.zIndexOffset = t8, this.update();
      }, getIcon: function() {
        return this.options.icon;
      }, setIcon: function(t8) {
        return this.options.icon = t8, this._map && (this._initIcon(), this.update()), this._popup && this.bindPopup(this._popup, this._popup.options), this;
      }, getElement: function() {
        return this._icon;
      }, update: function() {
        var t8;
        return this._icon && this._map && (t8 = this._map.latLngToLayerPoint(this._latlng).round(), this._setPos(t8)), this;
      }, _initIcon: function() {
        var t8 = this.options, e7 = "leaflet-zoom-" + (this._zoomAnimated ? "animated" : "hide"), i7 = t8.icon.createIcon(this._icon), n5 = false, i7 = (i7 !== this._icon && (this._icon && this._removeIcon(), n5 = true, t8.title && (i7.title = t8.title), "IMG" === i7.tagName && (i7.alt = t8.alt || "")), M2(i7, e7), t8.keyboard && (i7.tabIndex = "0", i7.setAttribute("role", "button")), this._icon = i7, t8.riseOnHover && this.on({ mouseover: this._bringToFront, mouseout: this._resetZIndex }), this.options.autoPanOnFocus && S3(i7, "focus", this._panOnFocus, this), t8.icon.createShadow(this._shadow)), o8 = false;
        i7 !== this._shadow && (this._removeShadow(), o8 = true), i7 && (M2(i7, e7), i7.alt = ""), this._shadow = i7, t8.opacity < 1 && this._updateOpacity(), n5 && this.getPane().appendChild(this._icon), this._initInteraction(), i7 && o8 && this.getPane(t8.shadowPane).appendChild(this._shadow);
      }, _removeIcon: function() {
        this.options.riseOnHover && this.off({ mouseover: this._bringToFront, mouseout: this._resetZIndex }), this.options.autoPanOnFocus && k2(this._icon, "focus", this._panOnFocus, this), T2(this._icon), this.removeInteractiveTarget(this._icon), this._icon = null;
      }, _removeShadow: function() {
        this._shadow && T2(this._shadow), this._shadow = null;
      }, _setPos: function(t8) {
        this._icon && Z2(this._icon, t8), this._shadow && Z2(this._shadow, t8), this._zIndex = t8.y + this.options.zIndexOffset, this._resetZIndex();
      }, _updateZIndex: function(t8) {
        this._icon && (this._icon.style.zIndex = this._zIndex + t8);
      }, _animateZoom: function(t8) {
        t8 = this._map._latLngToNewLayerPoint(this._latlng, t8.zoom, t8.center).round();
        this._setPos(t8);
      }, _initInteraction: function() {
        var t8;
        this.options.interactive && (M2(this._icon, "leaflet-interactive"), this.addInteractiveTarget(this._icon), pi && (t8 = this.options.draggable, this.dragging && (t8 = this.dragging.enabled(), this.dragging.disable()), this.dragging = new pi(this), t8 && this.dragging.enable()));
      }, setOpacity: function(t8) {
        return this.options.opacity = t8, this._map && this._updateOpacity(), this;
      }, _updateOpacity: function() {
        var t8 = this.options.opacity;
        this._icon && C2(this._icon, t8), this._shadow && C2(this._shadow, t8);
      }, _bringToFront: function() {
        this._updateZIndex(this.options.riseOffset);
      }, _resetZIndex: function() {
        this._updateZIndex(0);
      }, _panOnFocus: function() {
        var t8, e7, i7 = this._map;
        i7 && (t8 = (e7 = this.options.icon.options).iconSize ? m3(e7.iconSize) : m3(0, 0), e7 = e7.iconAnchor ? m3(e7.iconAnchor) : m3(0, 0), i7.panInside(this._latlng, { paddingTopLeft: e7, paddingBottomRight: t8.subtract(e7) }));
      }, _getPopupAnchor: function() {
        return this.options.icon.options.popupAnchor;
      }, _getTooltipAnchor: function() {
        return this.options.icon.options.tooltipAnchor;
      } });
      var fi = o7.extend({ options: { stroke: true, color: "#3388ff", weight: 3, opacity: 1, lineCap: "round", lineJoin: "round", dashArray: null, dashOffset: null, fill: false, fillColor: null, fillOpacity: 0.2, fillRule: "evenodd", interactive: true, bubblingMouseEvents: true }, beforeAdd: function(t8) {
        this._renderer = t8.getRenderer(this);
      }, onAdd: function() {
        this._renderer._initPath(this), this._reset(), this._renderer._addPath(this);
      }, onRemove: function() {
        this._renderer._removePath(this);
      }, redraw: function() {
        return this._map && this._renderer._updatePath(this), this;
      }, setStyle: function(t8) {
        return c4(this, t8), this._renderer && (this._renderer._updateStyle(this), this.options.stroke && t8 && Object.prototype.hasOwnProperty.call(t8, "weight") && this._updateBounds()), this;
      }, bringToFront: function() {
        return this._renderer && this._renderer._bringToFront(this), this;
      }, bringToBack: function() {
        return this._renderer && this._renderer._bringToBack(this), this;
      }, getElement: function() {
        return this._path;
      }, _reset: function() {
        this._project(), this._update();
      }, _clickTolerance: function() {
        return (this.options.stroke ? this.options.weight / 2 : 0) + (this._renderer.options.tolerance || 0);
      } }), gi = fi.extend({ options: { fill: true, radius: 10 }, initialize: function(t8, e7) {
        c4(this, e7), this._latlng = w2(t8), this._radius = this.options.radius;
      }, setLatLng: function(t8) {
        var e7 = this._latlng;
        return this._latlng = w2(t8), this.redraw(), this.fire("move", { oldLatLng: e7, latlng: this._latlng });
      }, getLatLng: function() {
        return this._latlng;
      }, setRadius: function(t8) {
        return this.options.radius = this._radius = t8, this.redraw();
      }, getRadius: function() {
        return this._radius;
      }, setStyle: function(t8) {
        var e7 = t8 && t8.radius || this._radius;
        return fi.prototype.setStyle.call(this, t8), this.setRadius(e7), this;
      }, _project: function() {
        this._point = this._map.latLngToLayerPoint(this._latlng), this._updateBounds();
      }, _updateBounds: function() {
        var t8 = this._radius, e7 = this._radiusY || t8, i7 = this._clickTolerance(), t8 = [t8 + i7, e7 + i7];
        this._pxBounds = new f3(this._point.subtract(t8), this._point.add(t8));
      }, _update: function() {
        this._map && this._updatePath();
      }, _updatePath: function() {
        this._renderer._updateCircle(this);
      }, _empty: function() {
        return this._radius && !this._renderer._bounds.intersects(this._pxBounds);
      }, _containsPoint: function(t8) {
        return t8.distanceTo(this._point) <= this._radius + this._clickTolerance();
      } });
      var vi = gi.extend({ initialize: function(t8, e7, i7) {
        if (c4(this, e7 = "number" == typeof e7 ? l4({}, i7, { radius: e7 }) : e7), this._latlng = w2(t8), isNaN(this.options.radius)) throw new Error("Circle radius cannot be NaN");
        this._mRadius = this.options.radius;
      }, setRadius: function(t8) {
        return this._mRadius = t8, this.redraw();
      }, getRadius: function() {
        return this._mRadius;
      }, getBounds: function() {
        var t8 = [this._radius, this._radiusY || this._radius];
        return new s4(this._map.layerPointToLatLng(this._point.subtract(t8)), this._map.layerPointToLatLng(this._point.add(t8)));
      }, setStyle: fi.prototype.setStyle, _project: function() {
        var t8, e7, i7, n5, o8, s5 = this._latlng.lng, r6 = this._latlng.lat, a4 = this._map, h4 = a4.options.crs;
        h4.distance === st.distance ? (n5 = Math.PI / 180, o8 = this._mRadius / st.R / n5, t8 = a4.project([r6 + o8, s5]), e7 = a4.project([r6 - o8, s5]), e7 = t8.add(e7).divideBy(2), i7 = a4.unproject(e7).lat, n5 = Math.acos((Math.cos(o8 * n5) - Math.sin(r6 * n5) * Math.sin(i7 * n5)) / (Math.cos(r6 * n5) * Math.cos(i7 * n5))) / n5, !isNaN(n5) && 0 !== n5 || (n5 = o8 / Math.cos(Math.PI / 180 * r6)), this._point = e7.subtract(a4.getPixelOrigin()), this._radius = isNaN(n5) ? 0 : e7.x - a4.project([i7, s5 - n5]).x, this._radiusY = e7.y - t8.y) : (o8 = h4.unproject(h4.project(this._latlng).subtract([this._mRadius, 0])), this._point = a4.latLngToLayerPoint(this._latlng), this._radius = this._point.x - a4.latLngToLayerPoint(o8).x), this._updateBounds();
      } });
      var yi = fi.extend({ options: { smoothFactor: 1, noClip: false }, initialize: function(t8, e7) {
        c4(this, e7), this._setLatLngs(t8);
      }, getLatLngs: function() {
        return this._latlngs;
      }, setLatLngs: function(t8) {
        return this._setLatLngs(t8), this.redraw();
      }, isEmpty: function() {
        return !this._latlngs.length;
      }, closestLayerPoint: function(t8) {
        for (var e7 = 1 / 0, i7 = null, n5 = ri, o8 = 0, s5 = this._parts.length; o8 < s5; o8++) for (var r6 = this._parts[o8], a4 = 1, h4 = r6.length; a4 < h4; a4++) {
          var l5, u4, c5 = n5(t8, l5 = r6[a4 - 1], u4 = r6[a4], true);
          c5 < e7 && (e7 = c5, i7 = n5(t8, l5, u4));
        }
        return i7 && (i7.distance = Math.sqrt(e7)), i7;
      }, getCenter: function() {
        if (this._map) return hi(this._defaultShape(), this._map.options.crs);
        throw new Error("Must add layer to map before using getCenter()");
      }, getBounds: function() {
        return this._bounds;
      }, addLatLng: function(t8, e7) {
        return e7 = e7 || this._defaultShape(), t8 = w2(t8), e7.push(t8), this._bounds.extend(t8), this.redraw();
      }, _setLatLngs: function(t8) {
        this._bounds = new s4(), this._latlngs = this._convertLatLngs(t8);
      }, _defaultShape: function() {
        return I2(this._latlngs) ? this._latlngs : this._latlngs[0];
      }, _convertLatLngs: function(t8) {
        for (var e7 = [], i7 = I2(t8), n5 = 0, o8 = t8.length; n5 < o8; n5++) i7 ? (e7[n5] = w2(t8[n5]), this._bounds.extend(e7[n5])) : e7[n5] = this._convertLatLngs(t8[n5]);
        return e7;
      }, _project: function() {
        var t8 = new f3();
        this._rings = [], this._projectLatlngs(this._latlngs, this._rings, t8), this._bounds.isValid() && t8.isValid() && (this._rawPxBounds = t8, this._updateBounds());
      }, _updateBounds: function() {
        var t8 = this._clickTolerance(), t8 = new p4(t8, t8);
        this._rawPxBounds && (this._pxBounds = new f3([this._rawPxBounds.min.subtract(t8), this._rawPxBounds.max.add(t8)]));
      }, _projectLatlngs: function(t8, e7, i7) {
        var n5, o8, s5 = t8[0] instanceof v2, r6 = t8.length;
        if (s5) {
          for (o8 = [], n5 = 0; n5 < r6; n5++) o8[n5] = this._map.latLngToLayerPoint(t8[n5]), i7.extend(o8[n5]);
          e7.push(o8);
        } else for (n5 = 0; n5 < r6; n5++) this._projectLatlngs(t8[n5], e7, i7);
      }, _clipPoints: function() {
        var t8 = this._renderer._bounds;
        if (this._parts = [], this._pxBounds && this._pxBounds.intersects(t8)) if (this.options.noClip) this._parts = this._rings;
        else for (var e7, i7, n5, o8, s5 = this._parts, r6 = 0, a4 = 0, h4 = this._rings.length; r6 < h4; r6++) for (e7 = 0, i7 = (o8 = this._rings[r6]).length; e7 < i7 - 1; e7++) (n5 = ni(o8[e7], o8[e7 + 1], t8, e7, true)) && (s5[a4] = s5[a4] || [], s5[a4].push(n5[0]), n5[1] === o8[e7 + 1] && e7 !== i7 - 2 || (s5[a4].push(n5[1]), a4++));
      }, _simplifyPoints: function() {
        for (var t8 = this._parts, e7 = this.options.smoothFactor, i7 = 0, n5 = t8.length; i7 < n5; i7++) t8[i7] = ei(t8[i7], e7);
      }, _update: function() {
        this._map && (this._clipPoints(), this._simplifyPoints(), this._updatePath());
      }, _updatePath: function() {
        this._renderer._updatePoly(this);
      }, _containsPoint: function(t8, e7) {
        var i7, n5, o8, s5, r6, a4, h4 = this._clickTolerance();
        if (this._pxBounds && this._pxBounds.contains(t8)) {
          for (i7 = 0, s5 = this._parts.length; i7 < s5; i7++) for (n5 = 0, o8 = (r6 = (a4 = this._parts[i7]).length) - 1; n5 < r6; o8 = n5++) if ((e7 || 0 !== n5) && ii(t8, a4[o8], a4[n5]) <= h4) return true;
        }
        return false;
      } });
      yi._flat = ai;
      var xi = yi.extend({ options: { fill: true }, isEmpty: function() {
        return !this._latlngs.length || !this._latlngs[0].length;
      }, getCenter: function() {
        if (this._map) return $e(this._defaultShape(), this._map.options.crs);
        throw new Error("Must add layer to map before using getCenter()");
      }, _convertLatLngs: function(t8) {
        var t8 = yi.prototype._convertLatLngs.call(this, t8), e7 = t8.length;
        return 2 <= e7 && t8[0] instanceof v2 && t8[0].equals(t8[e7 - 1]) && t8.pop(), t8;
      }, _setLatLngs: function(t8) {
        yi.prototype._setLatLngs.call(this, t8), I2(this._latlngs) && (this._latlngs = [this._latlngs]);
      }, _defaultShape: function() {
        return (I2(this._latlngs[0]) ? this._latlngs : this._latlngs[0])[0];
      }, _clipPoints: function() {
        var t8 = this._renderer._bounds, e7 = this.options.weight, e7 = new p4(e7, e7), t8 = new f3(t8.min.subtract(e7), t8.max.add(e7));
        if (this._parts = [], this._pxBounds && this._pxBounds.intersects(t8)) if (this.options.noClip) this._parts = this._rings;
        else for (var i7, n5 = 0, o8 = this._rings.length; n5 < o8; n5++) (i7 = Je(this._rings[n5], t8, true)).length && this._parts.push(i7);
      }, _updatePath: function() {
        this._renderer._updatePoly(this, true);
      }, _containsPoint: function(t8) {
        var e7, i7, n5, o8, s5, r6, a4, h4, l5 = false;
        if (!this._pxBounds || !this._pxBounds.contains(t8)) return false;
        for (o8 = 0, a4 = this._parts.length; o8 < a4; o8++) for (s5 = 0, r6 = (h4 = (e7 = this._parts[o8]).length) - 1; s5 < h4; r6 = s5++) i7 = e7[s5], n5 = e7[r6], i7.y > t8.y != n5.y > t8.y && t8.x < (n5.x - i7.x) * (t8.y - i7.y) / (n5.y - i7.y) + i7.x && (l5 = !l5);
        return l5 || yi.prototype._containsPoint.call(this, t8, true);
      } });
      var wi = ci.extend({ initialize: function(t8, e7) {
        c4(this, e7), this._layers = {}, t8 && this.addData(t8);
      }, addData: function(t8) {
        var e7, i7, n5, o8 = d3(t8) ? t8 : t8.features;
        if (o8) {
          for (e7 = 0, i7 = o8.length; e7 < i7; e7++) ((n5 = o8[e7]).geometries || n5.geometry || n5.features || n5.coordinates) && this.addData(n5);
          return this;
        }
        var s5, r6 = this.options;
        return (!r6.filter || r6.filter(t8)) && (s5 = bi(t8, r6)) ? (s5.feature = Zi(t8), s5.defaultOptions = s5.options, this.resetStyle(s5), r6.onEachFeature && r6.onEachFeature(t8, s5), this.addLayer(s5)) : this;
      }, resetStyle: function(t8) {
        return void 0 === t8 ? this.eachLayer(this.resetStyle, this) : (t8.options = l4({}, t8.defaultOptions), this._setLayerStyle(t8, this.options.style), this);
      }, setStyle: function(e7) {
        return this.eachLayer(function(t8) {
          this._setLayerStyle(t8, e7);
        }, this);
      }, _setLayerStyle: function(t8, e7) {
        t8.setStyle && ("function" == typeof e7 && (e7 = e7(t8.feature)), t8.setStyle(e7));
      } });
      function bi(t8, e7) {
        var i7, n5, o8, s5, r6 = "Feature" === t8.type ? t8.geometry : t8, a4 = r6 ? r6.coordinates : null, h4 = [], l5 = e7 && e7.pointToLayer, u4 = e7 && e7.coordsToLatLng || Li;
        if (!a4 && !r6) return null;
        switch (r6.type) {
          case "Point":
            return Pi(l5, t8, i7 = u4(a4), e7);
          case "MultiPoint":
            for (o8 = 0, s5 = a4.length; o8 < s5; o8++) i7 = u4(a4[o8]), h4.push(Pi(l5, t8, i7, e7));
            return new ci(h4);
          case "LineString":
          case "MultiLineString":
            return n5 = Ti(a4, "LineString" === r6.type ? 0 : 1, u4), new yi(n5, e7);
          case "Polygon":
          case "MultiPolygon":
            return n5 = Ti(a4, "Polygon" === r6.type ? 1 : 2, u4), new xi(n5, e7);
          case "GeometryCollection":
            for (o8 = 0, s5 = r6.geometries.length; o8 < s5; o8++) {
              var c5 = bi({ geometry: r6.geometries[o8], type: "Feature", properties: t8.properties }, e7);
              c5 && h4.push(c5);
            }
            return new ci(h4);
          case "FeatureCollection":
            for (o8 = 0, s5 = r6.features.length; o8 < s5; o8++) {
              var d4 = bi(r6.features[o8], e7);
              d4 && h4.push(d4);
            }
            return new ci(h4);
          default:
            throw new Error("Invalid GeoJSON object.");
        }
      }
      function Pi(t8, e7, i7, n5) {
        return t8 ? t8(e7, i7) : new mi(i7, n5 && n5.markersInheritOptions && n5);
      }
      function Li(t8) {
        return new v2(t8[1], t8[0], t8[2]);
      }
      function Ti(t8, e7, i7) {
        for (var n5, o8 = [], s5 = 0, r6 = t8.length; s5 < r6; s5++) n5 = e7 ? Ti(t8[s5], e7 - 1, i7) : (i7 || Li)(t8[s5]), o8.push(n5);
        return o8;
      }
      function Mi(t8, e7) {
        return void 0 !== (t8 = w2(t8)).alt ? [i6(t8.lng, e7), i6(t8.lat, e7), i6(t8.alt, e7)] : [i6(t8.lng, e7), i6(t8.lat, e7)];
      }
      function zi(t8, e7, i7, n5) {
        for (var o8 = [], s5 = 0, r6 = t8.length; s5 < r6; s5++) o8.push(e7 ? zi(t8[s5], I2(t8[s5]) ? 0 : e7 - 1, i7, n5) : Mi(t8[s5], n5));
        return !e7 && i7 && 0 < o8.length && o8.push(o8[0].slice()), o8;
      }
      function Ci(t8, e7) {
        return t8.feature ? l4({}, t8.feature, { geometry: e7 }) : Zi(e7);
      }
      function Zi(t8) {
        return "Feature" === t8.type || "FeatureCollection" === t8.type ? t8 : { type: "Feature", properties: {}, geometry: t8 };
      }
      Tt = { toGeoJSON: function(t8) {
        return Ci(this, { type: "Point", coordinates: Mi(this.getLatLng(), t8) });
      } };
      function Si(t8, e7) {
        return new wi(t8, e7);
      }
      mi.include(Tt), vi.include(Tt), gi.include(Tt), yi.include({ toGeoJSON: function(t8) {
        var e7 = !I2(this._latlngs);
        return Ci(this, { type: (e7 ? "Multi" : "") + "LineString", coordinates: zi(this._latlngs, e7 ? 1 : 0, false, t8) });
      } }), xi.include({ toGeoJSON: function(t8) {
        var e7 = !I2(this._latlngs), i7 = e7 && !I2(this._latlngs[0]), t8 = zi(this._latlngs, i7 ? 2 : e7 ? 1 : 0, true, t8);
        return Ci(this, { type: (i7 ? "Multi" : "") + "Polygon", coordinates: t8 = e7 ? t8 : [t8] });
      } }), ui.include({ toMultiPoint: function(e7) {
        var i7 = [];
        return this.eachLayer(function(t8) {
          i7.push(t8.toGeoJSON(e7).geometry.coordinates);
        }), Ci(this, { type: "MultiPoint", coordinates: i7 });
      }, toGeoJSON: function(e7) {
        var i7, n5, t8 = this.feature && this.feature.geometry && this.feature.geometry.type;
        return "MultiPoint" === t8 ? this.toMultiPoint(e7) : (i7 = "GeometryCollection" === t8, n5 = [], this.eachLayer(function(t9) {
          t9.toGeoJSON && (t9 = t9.toGeoJSON(e7), i7 ? n5.push(t9.geometry) : "FeatureCollection" === (t9 = Zi(t9)).type ? n5.push.apply(n5, t9.features) : n5.push(t9));
        }), i7 ? Ci(this, { geometries: n5, type: "GeometryCollection" }) : { type: "FeatureCollection", features: n5 });
      } });
      var Mt = Si, Ei = o7.extend({ options: { opacity: 1, alt: "", interactive: false, crossOrigin: false, errorOverlayUrl: "", zIndex: 1, className: "" }, initialize: function(t8, e7, i7) {
        this._url = t8, this._bounds = g2(e7), c4(this, i7);
      }, onAdd: function() {
        this._image || (this._initImage(), this.options.opacity < 1 && this._updateOpacity()), this.options.interactive && (M2(this._image, "leaflet-interactive"), this.addInteractiveTarget(this._image)), this.getPane().appendChild(this._image), this._reset();
      }, onRemove: function() {
        T2(this._image), this.options.interactive && this.removeInteractiveTarget(this._image);
      }, setOpacity: function(t8) {
        return this.options.opacity = t8, this._image && this._updateOpacity(), this;
      }, setStyle: function(t8) {
        return t8.opacity && this.setOpacity(t8.opacity), this;
      }, bringToFront: function() {
        return this._map && fe(this._image), this;
      }, bringToBack: function() {
        return this._map && ge(this._image), this;
      }, setUrl: function(t8) {
        return this._url = t8, this._image && (this._image.src = t8), this;
      }, setBounds: function(t8) {
        return this._bounds = g2(t8), this._map && this._reset(), this;
      }, getEvents: function() {
        var t8 = { zoom: this._reset, viewreset: this._reset };
        return this._zoomAnimated && (t8.zoomanim = this._animateZoom), t8;
      }, setZIndex: function(t8) {
        return this.options.zIndex = t8, this._updateZIndex(), this;
      }, getBounds: function() {
        return this._bounds;
      }, getElement: function() {
        return this._image;
      }, _initImage: function() {
        var t8 = "IMG" === this._url.tagName, e7 = this._image = t8 ? this._url : P2("img");
        M2(e7, "leaflet-image-layer"), this._zoomAnimated && M2(e7, "leaflet-zoom-animated"), this.options.className && M2(e7, this.options.className), e7.onselectstart = u3, e7.onmousemove = u3, e7.onload = a3(this.fire, this, "load"), e7.onerror = a3(this._overlayOnError, this, "error"), !this.options.crossOrigin && "" !== this.options.crossOrigin || (e7.crossOrigin = true === this.options.crossOrigin ? "" : this.options.crossOrigin), this.options.zIndex && this._updateZIndex(), t8 ? this._url = e7.src : (e7.src = this._url, e7.alt = this.options.alt);
      }, _animateZoom: function(t8) {
        var e7 = this._map.getZoomScale(t8.zoom), t8 = this._map._latLngBoundsToNewLayerBounds(this._bounds, t8.zoom, t8.center).min;
        be(this._image, t8, e7);
      }, _reset: function() {
        var t8 = this._image, e7 = new f3(this._map.latLngToLayerPoint(this._bounds.getNorthWest()), this._map.latLngToLayerPoint(this._bounds.getSouthEast())), i7 = e7.getSize();
        Z2(t8, e7.min), t8.style.width = i7.x + "px", t8.style.height = i7.y + "px";
      }, _updateOpacity: function() {
        C2(this._image, this.options.opacity);
      }, _updateZIndex: function() {
        this._image && void 0 !== this.options.zIndex && null !== this.options.zIndex && (this._image.style.zIndex = this.options.zIndex);
      }, _overlayOnError: function() {
        this.fire("error");
        var t8 = this.options.errorOverlayUrl;
        t8 && this._url !== t8 && (this._url = t8, this._image.src = t8);
      }, getCenter: function() {
        return this._bounds.getCenter();
      } }), ki = Ei.extend({ options: { autoplay: true, loop: true, keepAspectRatio: true, muted: false, playsInline: true }, _initImage: function() {
        var t8 = "VIDEO" === this._url.tagName, e7 = this._image = t8 ? this._url : P2("video");
        if (M2(e7, "leaflet-image-layer"), this._zoomAnimated && M2(e7, "leaflet-zoom-animated"), this.options.className && M2(e7, this.options.className), e7.onselectstart = u3, e7.onmousemove = u3, e7.onloadeddata = a3(this.fire, this, "load"), t8) {
          for (var i7 = e7.getElementsByTagName("source"), n5 = [], o8 = 0; o8 < i7.length; o8++) n5.push(i7[o8].src);
          this._url = 0 < i7.length ? n5 : [e7.src];
        } else {
          d3(this._url) || (this._url = [this._url]), !this.options.keepAspectRatio && Object.prototype.hasOwnProperty.call(e7.style, "objectFit") && (e7.style.objectFit = "fill"), e7.autoplay = !!this.options.autoplay, e7.loop = !!this.options.loop, e7.muted = !!this.options.muted, e7.playsInline = !!this.options.playsInline;
          for (var s5 = 0; s5 < this._url.length; s5++) {
            var r6 = P2("source");
            r6.src = this._url[s5], e7.appendChild(r6);
          }
        }
      } });
      var Oi = Ei.extend({ _initImage: function() {
        var t8 = this._image = this._url;
        M2(t8, "leaflet-image-layer"), this._zoomAnimated && M2(t8, "leaflet-zoom-animated"), this.options.className && M2(t8, this.options.className), t8.onselectstart = u3, t8.onmousemove = u3;
      } });
      var Ai = o7.extend({ options: { interactive: false, offset: [0, 0], className: "", pane: void 0, content: "" }, initialize: function(t8, e7) {
        t8 && (t8 instanceof v2 || d3(t8)) ? (this._latlng = w2(t8), c4(this, e7)) : (c4(this, t8), this._source = e7), this.options.content && (this._content = this.options.content);
      }, openOn: function(t8) {
        return (t8 = arguments.length ? t8 : this._source._map).hasLayer(this) || t8.addLayer(this), this;
      }, close: function() {
        return this._map && this._map.removeLayer(this), this;
      }, toggle: function(t8) {
        return this._map ? this.close() : (arguments.length ? this._source = t8 : t8 = this._source, this._prepareOpen(), this.openOn(t8._map)), this;
      }, onAdd: function(t8) {
        this._zoomAnimated = t8._zoomAnimated, this._container || this._initLayout(), t8._fadeAnimated && C2(this._container, 0), clearTimeout(this._removeTimeout), this.getPane().appendChild(this._container), this.update(), t8._fadeAnimated && C2(this._container, 1), this.bringToFront(), this.options.interactive && (M2(this._container, "leaflet-interactive"), this.addInteractiveTarget(this._container));
      }, onRemove: function(t8) {
        t8._fadeAnimated ? (C2(this._container, 0), this._removeTimeout = setTimeout(a3(T2, void 0, this._container), 200)) : T2(this._container), this.options.interactive && (z2(this._container, "leaflet-interactive"), this.removeInteractiveTarget(this._container));
      }, getLatLng: function() {
        return this._latlng;
      }, setLatLng: function(t8) {
        return this._latlng = w2(t8), this._map && (this._updatePosition(), this._adjustPan()), this;
      }, getContent: function() {
        return this._content;
      }, setContent: function(t8) {
        return this._content = t8, this.update(), this;
      }, getElement: function() {
        return this._container;
      }, update: function() {
        this._map && (this._container.style.visibility = "hidden", this._updateContent(), this._updateLayout(), this._updatePosition(), this._container.style.visibility = "", this._adjustPan());
      }, getEvents: function() {
        var t8 = { zoom: this._updatePosition, viewreset: this._updatePosition };
        return this._zoomAnimated && (t8.zoomanim = this._animateZoom), t8;
      }, isOpen: function() {
        return !!this._map && this._map.hasLayer(this);
      }, bringToFront: function() {
        return this._map && fe(this._container), this;
      }, bringToBack: function() {
        return this._map && ge(this._container), this;
      }, _prepareOpen: function(t8) {
        if (!(i7 = this._source)._map) return false;
        if (i7 instanceof ci) {
          var e7, i7 = null, n5 = this._source._layers;
          for (e7 in n5) if (n5[e7]._map) {
            i7 = n5[e7];
            break;
          }
          if (!i7) return false;
          this._source = i7;
        }
        if (!t8) if (i7.getCenter) t8 = i7.getCenter();
        else if (i7.getLatLng) t8 = i7.getLatLng();
        else {
          if (!i7.getBounds) throw new Error("Unable to get source layer LatLng.");
          t8 = i7.getBounds().getCenter();
        }
        return this.setLatLng(t8), this._map && this.update(), true;
      }, _updateContent: function() {
        if (this._content) {
          var t8 = this._contentNode, e7 = "function" == typeof this._content ? this._content(this._source || this) : this._content;
          if ("string" == typeof e7) t8.innerHTML = e7;
          else {
            for (; t8.hasChildNodes(); ) t8.removeChild(t8.firstChild);
            t8.appendChild(e7);
          }
          this.fire("contentupdate");
        }
      }, _updatePosition: function() {
        var t8, e7, i7;
        this._map && (e7 = this._map.latLngToLayerPoint(this._latlng), t8 = m3(this.options.offset), i7 = this._getAnchor(), this._zoomAnimated ? Z2(this._container, e7.add(i7)) : t8 = t8.add(e7).add(i7), e7 = this._containerBottom = -t8.y, i7 = this._containerLeft = -Math.round(this._containerWidth / 2) + t8.x, this._container.style.bottom = e7 + "px", this._container.style.left = i7 + "px");
      }, _getAnchor: function() {
        return [0, 0];
      } }), Bi = (A2.include({ _initOverlay: function(t8, e7, i7, n5) {
        var o8 = e7;
        return o8 instanceof t8 || (o8 = new t8(n5).setContent(e7)), i7 && o8.setLatLng(i7), o8;
      } }), o7.include({ _initOverlay: function(t8, e7, i7, n5) {
        var o8 = i7;
        return o8 instanceof t8 ? (c4(o8, n5), o8._source = this) : (o8 = e7 && !n5 ? e7 : new t8(n5, this)).setContent(i7), o8;
      } }), Ai.extend({ options: { pane: "popupPane", offset: [0, 7], maxWidth: 300, minWidth: 50, maxHeight: null, autoPan: true, autoPanPaddingTopLeft: null, autoPanPaddingBottomRight: null, autoPanPadding: [5, 5], keepInView: false, closeButton: true, autoClose: true, closeOnEscapeKey: true, className: "" }, openOn: function(t8) {
        return !(t8 = arguments.length ? t8 : this._source._map).hasLayer(this) && t8._popup && t8._popup.options.autoClose && t8.removeLayer(t8._popup), t8._popup = this, Ai.prototype.openOn.call(this, t8);
      }, onAdd: function(t8) {
        Ai.prototype.onAdd.call(this, t8), t8.fire("popupopen", { popup: this }), this._source && (this._source.fire("popupopen", { popup: this }, true), this._source instanceof fi || this._source.on("preclick", Ae));
      }, onRemove: function(t8) {
        Ai.prototype.onRemove.call(this, t8), t8.fire("popupclose", { popup: this }), this._source && (this._source.fire("popupclose", { popup: this }, true), this._source instanceof fi || this._source.off("preclick", Ae));
      }, getEvents: function() {
        var t8 = Ai.prototype.getEvents.call(this);
        return (void 0 !== this.options.closeOnClick ? this.options.closeOnClick : this._map.options.closePopupOnClick) && (t8.preclick = this.close), this.options.keepInView && (t8.moveend = this._adjustPan), t8;
      }, _initLayout: function() {
        var t8 = "leaflet-popup", e7 = this._container = P2("div", t8 + " " + (this.options.className || "") + " leaflet-zoom-animated"), i7 = this._wrapper = P2("div", t8 + "-content-wrapper", e7);
        this._contentNode = P2("div", t8 + "-content", i7), Ie(e7), Be(this._contentNode), S3(e7, "contextmenu", Ae), this._tipContainer = P2("div", t8 + "-tip-container", e7), this._tip = P2("div", t8 + "-tip", this._tipContainer), this.options.closeButton && ((i7 = this._closeButton = P2("a", t8 + "-close-button", e7)).setAttribute("role", "button"), i7.setAttribute("aria-label", "Close popup"), i7.href = "#close", i7.innerHTML = '<span aria-hidden="true">&#215;</span>', S3(i7, "click", function(t9) {
          O(t9), this.close();
        }, this));
      }, _updateLayout: function() {
        var t8 = this._contentNode, e7 = t8.style, i7 = (e7.width = "", e7.whiteSpace = "nowrap", t8.offsetWidth), i7 = Math.min(i7, this.options.maxWidth), i7 = (i7 = Math.max(i7, this.options.minWidth), e7.width = i7 + 1 + "px", e7.whiteSpace = "", e7.height = "", t8.offsetHeight), n5 = this.options.maxHeight, o8 = "leaflet-popup-scrolled";
        (n5 && n5 < i7 ? (e7.height = n5 + "px", M2) : z2)(t8, o8), this._containerWidth = this._container.offsetWidth;
      }, _animateZoom: function(t8) {
        var t8 = this._map._latLngToNewLayerPoint(this._latlng, t8.zoom, t8.center), e7 = this._getAnchor();
        Z2(this._container, t8.add(e7));
      }, _adjustPan: function() {
        var t8, e7, i7, n5, o8, s5, r6, a4;
        this.options.autoPan && (this._map._panAnim && this._map._panAnim.stop(), this._autopanning ? this._autopanning = false : (t8 = this._map, e7 = parseInt(pe(this._container, "marginBottom"), 10) || 0, e7 = this._container.offsetHeight + e7, a4 = this._containerWidth, (i7 = new p4(this._containerLeft, -e7 - this._containerBottom))._add(Pe(this._container)), i7 = t8.layerPointToContainerPoint(i7), o8 = m3(this.options.autoPanPadding), n5 = m3(this.options.autoPanPaddingTopLeft || o8), o8 = m3(this.options.autoPanPaddingBottomRight || o8), s5 = t8.getSize(), r6 = 0, i7.x + a4 + o8.x > s5.x && (r6 = i7.x + a4 - s5.x + o8.x), i7.x - r6 - n5.x < (a4 = 0) && (r6 = i7.x - n5.x), i7.y + e7 + o8.y > s5.y && (a4 = i7.y + e7 - s5.y + o8.y), i7.y - a4 - n5.y < 0 && (a4 = i7.y - n5.y), (r6 || a4) && (this.options.keepInView && (this._autopanning = true), t8.fire("autopanstart").panBy([r6, a4]))));
      }, _getAnchor: function() {
        return m3(this._source && this._source._getPopupAnchor ? this._source._getPopupAnchor() : [0, 0]);
      } })), Ii = (A2.mergeOptions({ closePopupOnClick: true }), A2.include({ openPopup: function(t8, e7, i7) {
        return this._initOverlay(Bi, t8, e7, i7).openOn(this), this;
      }, closePopup: function(t8) {
        return (t8 = arguments.length ? t8 : this._popup) && t8.close(), this;
      } }), o7.include({ bindPopup: function(t8, e7) {
        return this._popup = this._initOverlay(Bi, this._popup, t8, e7), this._popupHandlersAdded || (this.on({ click: this._openPopup, keypress: this._onKeyPress, remove: this.closePopup, move: this._movePopup }), this._popupHandlersAdded = true), this;
      }, unbindPopup: function() {
        return this._popup && (this.off({ click: this._openPopup, keypress: this._onKeyPress, remove: this.closePopup, move: this._movePopup }), this._popupHandlersAdded = false, this._popup = null), this;
      }, openPopup: function(t8) {
        return this._popup && (this instanceof ci || (this._popup._source = this), this._popup._prepareOpen(t8 || this._latlng) && this._popup.openOn(this._map)), this;
      }, closePopup: function() {
        return this._popup && this._popup.close(), this;
      }, togglePopup: function() {
        return this._popup && this._popup.toggle(this), this;
      }, isPopupOpen: function() {
        return !!this._popup && this._popup.isOpen();
      }, setPopupContent: function(t8) {
        return this._popup && this._popup.setContent(t8), this;
      }, getPopup: function() {
        return this._popup;
      }, _openPopup: function(t8) {
        var e7;
        this._popup && this._map && (Re(t8), e7 = t8.layer || t8.target, this._popup._source !== e7 || e7 instanceof fi ? (this._popup._source = e7, this.openPopup(t8.latlng)) : this._map.hasLayer(this._popup) ? this.closePopup() : this.openPopup(t8.latlng));
      }, _movePopup: function(t8) {
        this._popup.setLatLng(t8.latlng);
      }, _onKeyPress: function(t8) {
        13 === t8.originalEvent.keyCode && this._openPopup(t8);
      } }), Ai.extend({ options: { pane: "tooltipPane", offset: [0, 0], direction: "auto", permanent: false, sticky: false, opacity: 0.9 }, onAdd: function(t8) {
        Ai.prototype.onAdd.call(this, t8), this.setOpacity(this.options.opacity), t8.fire("tooltipopen", { tooltip: this }), this._source && (this.addEventParent(this._source), this._source.fire("tooltipopen", { tooltip: this }, true));
      }, onRemove: function(t8) {
        Ai.prototype.onRemove.call(this, t8), t8.fire("tooltipclose", { tooltip: this }), this._source && (this.removeEventParent(this._source), this._source.fire("tooltipclose", { tooltip: this }, true));
      }, getEvents: function() {
        var t8 = Ai.prototype.getEvents.call(this);
        return this.options.permanent || (t8.preclick = this.close), t8;
      }, _initLayout: function() {
        var t8 = "leaflet-tooltip " + (this.options.className || "") + " leaflet-zoom-" + (this._zoomAnimated ? "animated" : "hide");
        this._contentNode = this._container = P2("div", t8), this._container.setAttribute("role", "tooltip"), this._container.setAttribute("id", "leaflet-tooltip-" + h3(this));
      }, _updateLayout: function() {
      }, _adjustPan: function() {
      }, _setPosition: function(t8) {
        var e7, i7 = this._map, n5 = this._container, o8 = i7.latLngToContainerPoint(i7.getCenter()), i7 = i7.layerPointToContainerPoint(t8), s5 = this.options.direction, r6 = n5.offsetWidth, a4 = n5.offsetHeight, h4 = m3(this.options.offset), l5 = this._getAnchor(), i7 = "top" === s5 ? (e7 = r6 / 2, a4) : "bottom" === s5 ? (e7 = r6 / 2, 0) : (e7 = "center" === s5 ? r6 / 2 : "right" === s5 ? 0 : "left" === s5 ? r6 : i7.x < o8.x ? (s5 = "right", 0) : (s5 = "left", r6 + 2 * (h4.x + l5.x)), a4 / 2);
        t8 = t8.subtract(m3(e7, i7, true)).add(h4).add(l5), z2(n5, "leaflet-tooltip-right"), z2(n5, "leaflet-tooltip-left"), z2(n5, "leaflet-tooltip-top"), z2(n5, "leaflet-tooltip-bottom"), M2(n5, "leaflet-tooltip-" + s5), Z2(n5, t8);
      }, _updatePosition: function() {
        var t8 = this._map.latLngToLayerPoint(this._latlng);
        this._setPosition(t8);
      }, setOpacity: function(t8) {
        this.options.opacity = t8, this._container && C2(this._container, t8);
      }, _animateZoom: function(t8) {
        t8 = this._map._latLngToNewLayerPoint(this._latlng, t8.zoom, t8.center);
        this._setPosition(t8);
      }, _getAnchor: function() {
        return m3(this._source && this._source._getTooltipAnchor && !this.options.sticky ? this._source._getTooltipAnchor() : [0, 0]);
      } })), Ri = (A2.include({ openTooltip: function(t8, e7, i7) {
        return this._initOverlay(Ii, t8, e7, i7).openOn(this), this;
      }, closeTooltip: function(t8) {
        return t8.close(), this;
      } }), o7.include({ bindTooltip: function(t8, e7) {
        return this._tooltip && this.isTooltipOpen() && this.unbindTooltip(), this._tooltip = this._initOverlay(Ii, this._tooltip, t8, e7), this._initTooltipInteractions(), this._tooltip.options.permanent && this._map && this._map.hasLayer(this) && this.openTooltip(), this;
      }, unbindTooltip: function() {
        return this._tooltip && (this._initTooltipInteractions(true), this.closeTooltip(), this._tooltip = null), this;
      }, _initTooltipInteractions: function(t8) {
        var e7, i7;
        !t8 && this._tooltipHandlersAdded || (e7 = t8 ? "off" : "on", i7 = { remove: this.closeTooltip, move: this._moveTooltip }, this._tooltip.options.permanent ? i7.add = this._openTooltip : (i7.mouseover = this._openTooltip, i7.mouseout = this.closeTooltip, i7.click = this._openTooltip, this._map ? this._addFocusListeners() : i7.add = this._addFocusListeners), this._tooltip.options.sticky && (i7.mousemove = this._moveTooltip), this[e7](i7), this._tooltipHandlersAdded = !t8);
      }, openTooltip: function(t8) {
        return this._tooltip && (this instanceof ci || (this._tooltip._source = this), this._tooltip._prepareOpen(t8) && (this._tooltip.openOn(this._map), this.getElement ? this._setAriaDescribedByOnLayer(this) : this.eachLayer && this.eachLayer(this._setAriaDescribedByOnLayer, this))), this;
      }, closeTooltip: function() {
        if (this._tooltip) return this._tooltip.close();
      }, toggleTooltip: function() {
        return this._tooltip && this._tooltip.toggle(this), this;
      }, isTooltipOpen: function() {
        return this._tooltip.isOpen();
      }, setTooltipContent: function(t8) {
        return this._tooltip && this._tooltip.setContent(t8), this;
      }, getTooltip: function() {
        return this._tooltip;
      }, _addFocusListeners: function() {
        this.getElement ? this._addFocusListenersOnLayer(this) : this.eachLayer && this.eachLayer(this._addFocusListenersOnLayer, this);
      }, _addFocusListenersOnLayer: function(t8) {
        var e7 = "function" == typeof t8.getElement && t8.getElement();
        e7 && (S3(e7, "focus", function() {
          this._tooltip._source = t8, this.openTooltip();
        }, this), S3(e7, "blur", this.closeTooltip, this));
      }, _setAriaDescribedByOnLayer: function(t8) {
        t8 = "function" == typeof t8.getElement && t8.getElement();
        t8 && t8.setAttribute("aria-describedby", this._tooltip._container.id);
      }, _openTooltip: function(t8) {
        var e7;
        this._tooltip && this._map && (this._map.dragging && this._map.dragging.moving() && !this._openOnceFlag ? (this._openOnceFlag = true, (e7 = this)._map.once("moveend", function() {
          e7._openOnceFlag = false, e7._openTooltip(t8);
        })) : (this._tooltip._source = t8.layer || t8.target, this.openTooltip(this._tooltip.options.sticky ? t8.latlng : void 0)));
      }, _moveTooltip: function(t8) {
        var e7 = t8.latlng;
        this._tooltip.options.sticky && t8.originalEvent && (t8 = this._map.mouseEventToContainerPoint(t8.originalEvent), t8 = this._map.containerPointToLayerPoint(t8), e7 = this._map.layerPointToLatLng(t8)), this._tooltip.setLatLng(e7);
      } }), di.extend({ options: { iconSize: [12, 12], html: false, bgPos: null, className: "leaflet-div-icon" }, createIcon: function(t8) {
        var t8 = t8 && "DIV" === t8.tagName ? t8 : document.createElement("div"), e7 = this.options;
        return e7.html instanceof Element ? (me(t8), t8.appendChild(e7.html)) : t8.innerHTML = false !== e7.html ? e7.html : "", e7.bgPos && (e7 = m3(e7.bgPos), t8.style.backgroundPosition = -e7.x + "px " + -e7.y + "px"), this._setIconStyles(t8, "icon"), t8;
      }, createShadow: function() {
        return null;
      } }));
      di.Default = _i;
      var Ni = o7.extend({ options: { tileSize: 256, opacity: 1, updateWhenIdle: b3.mobile, updateWhenZooming: true, updateInterval: 200, zIndex: 1, bounds: null, minZoom: 0, maxZoom: void 0, maxNativeZoom: void 0, minNativeZoom: void 0, noWrap: false, pane: "tilePane", className: "", keepBuffer: 2 }, initialize: function(t8) {
        c4(this, t8);
      }, onAdd: function() {
        this._initContainer(), this._levels = {}, this._tiles = {}, this._resetView();
      }, beforeAdd: function(t8) {
        t8._addZoomLimit(this);
      }, onRemove: function(t8) {
        this._removeAllTiles(), T2(this._container), t8._removeZoomLimit(this), this._container = null, this._tileZoom = void 0;
      }, bringToFront: function() {
        return this._map && (fe(this._container), this._setAutoZIndex(Math.max)), this;
      }, bringToBack: function() {
        return this._map && (ge(this._container), this._setAutoZIndex(Math.min)), this;
      }, getContainer: function() {
        return this._container;
      }, setOpacity: function(t8) {
        return this.options.opacity = t8, this._updateOpacity(), this;
      }, setZIndex: function(t8) {
        return this.options.zIndex = t8, this._updateZIndex(), this;
      }, isLoading: function() {
        return this._loading;
      }, redraw: function() {
        var t8;
        return this._map && (this._removeAllTiles(), (t8 = this._clampZoom(this._map.getZoom())) !== this._tileZoom && (this._tileZoom = t8, this._updateLevels()), this._update()), this;
      }, getEvents: function() {
        var t8 = { viewprereset: this._invalidateAll, viewreset: this._resetView, zoom: this._resetView, moveend: this._onMoveEnd };
        return this.options.updateWhenIdle || (this._onMove || (this._onMove = j2(this._onMoveEnd, this.options.updateInterval, this)), t8.move = this._onMove), this._zoomAnimated && (t8.zoomanim = this._animateZoom), t8;
      }, createTile: function() {
        return document.createElement("div");
      }, getTileSize: function() {
        var t8 = this.options.tileSize;
        return t8 instanceof p4 ? t8 : new p4(t8, t8);
      }, _updateZIndex: function() {
        this._container && void 0 !== this.options.zIndex && null !== this.options.zIndex && (this._container.style.zIndex = this.options.zIndex);
      }, _setAutoZIndex: function(t8) {
        for (var e7, i7 = this.getPane().children, n5 = -t8(-1 / 0, 1 / 0), o8 = 0, s5 = i7.length; o8 < s5; o8++) e7 = i7[o8].style.zIndex, i7[o8] !== this._container && e7 && (n5 = t8(n5, +e7));
        isFinite(n5) && (this.options.zIndex = n5 + t8(-1, 1), this._updateZIndex());
      }, _updateOpacity: function() {
        if (this._map && !b3.ielt9) {
          C2(this._container, this.options.opacity);
          var t8, e7 = +/* @__PURE__ */ new Date(), i7 = false, n5 = false;
          for (t8 in this._tiles) {
            var o8, s5 = this._tiles[t8];
            s5.current && s5.loaded && (o8 = Math.min(1, (e7 - s5.loaded) / 200), C2(s5.el, o8), o8 < 1 ? i7 = true : (s5.active ? n5 = true : this._onOpaqueTile(s5), s5.active = true));
          }
          n5 && !this._noPrune && this._pruneTiles(), i7 && (r5(this._fadeFrame), this._fadeFrame = x2(this._updateOpacity, this));
        }
      }, _onOpaqueTile: u3, _initContainer: function() {
        this._container || (this._container = P2("div", "leaflet-layer " + (this.options.className || "")), this._updateZIndex(), this.options.opacity < 1 && this._updateOpacity(), this.getPane().appendChild(this._container));
      }, _updateLevels: function() {
        var t8 = this._tileZoom, e7 = this.options.maxZoom;
        if (void 0 !== t8) {
          for (var i7 in this._levels) i7 = Number(i7), this._levels[i7].el.children.length || i7 === t8 ? (this._levels[i7].el.style.zIndex = e7 - Math.abs(t8 - i7), this._onUpdateLevel(i7)) : (T2(this._levels[i7].el), this._removeTilesAtZoom(i7), this._onRemoveLevel(i7), delete this._levels[i7]);
          var n5 = this._levels[t8], o8 = this._map;
          return n5 || ((n5 = this._levels[t8] = {}).el = P2("div", "leaflet-tile-container leaflet-zoom-animated", this._container), n5.el.style.zIndex = e7, n5.origin = o8.project(o8.unproject(o8.getPixelOrigin()), t8).round(), n5.zoom = t8, this._setZoomTransform(n5, o8.getCenter(), o8.getZoom()), u3(n5.el.offsetWidth), this._onCreateLevel(n5)), this._level = n5;
        }
      }, _onUpdateLevel: u3, _onRemoveLevel: u3, _onCreateLevel: u3, _pruneTiles: function() {
        if (this._map) {
          var t8, e7, i7, n5 = this._map.getZoom();
          if (n5 > this.options.maxZoom || n5 < this.options.minZoom) this._removeAllTiles();
          else {
            for (t8 in this._tiles) (i7 = this._tiles[t8]).retain = i7.current;
            for (t8 in this._tiles) (i7 = this._tiles[t8]).current && !i7.active && (e7 = i7.coords, this._retainParent(e7.x, e7.y, e7.z, e7.z - 5) || this._retainChildren(e7.x, e7.y, e7.z, e7.z + 2));
            for (t8 in this._tiles) this._tiles[t8].retain || this._removeTile(t8);
          }
        }
      }, _removeTilesAtZoom: function(t8) {
        for (var e7 in this._tiles) this._tiles[e7].coords.z === t8 && this._removeTile(e7);
      }, _removeAllTiles: function() {
        for (var t8 in this._tiles) this._removeTile(t8);
      }, _invalidateAll: function() {
        for (var t8 in this._levels) T2(this._levels[t8].el), this._onRemoveLevel(Number(t8)), delete this._levels[t8];
        this._removeAllTiles(), this._tileZoom = void 0;
      }, _retainParent: function(t8, e7, i7, n5) {
        var t8 = Math.floor(t8 / 2), e7 = Math.floor(e7 / 2), i7 = i7 - 1, o8 = new p4(+t8, +e7), o8 = (o8.z = i7, this._tileCoordsToKey(o8)), o8 = this._tiles[o8];
        return o8 && o8.active ? o8.retain = true : (o8 && o8.loaded && (o8.retain = true), n5 < i7 && this._retainParent(t8, e7, i7, n5));
      }, _retainChildren: function(t8, e7, i7, n5) {
        for (var o8 = 2 * t8; o8 < 2 * t8 + 2; o8++) for (var s5 = 2 * e7; s5 < 2 * e7 + 2; s5++) {
          var r6 = new p4(o8, s5), r6 = (r6.z = i7 + 1, this._tileCoordsToKey(r6)), r6 = this._tiles[r6];
          r6 && r6.active ? r6.retain = true : (r6 && r6.loaded && (r6.retain = true), i7 + 1 < n5 && this._retainChildren(o8, s5, i7 + 1, n5));
        }
      }, _resetView: function(t8) {
        t8 = t8 && (t8.pinch || t8.flyTo);
        this._setView(this._map.getCenter(), this._map.getZoom(), t8, t8);
      }, _animateZoom: function(t8) {
        this._setView(t8.center, t8.zoom, true, t8.noUpdate);
      }, _clampZoom: function(t8) {
        var e7 = this.options;
        return void 0 !== e7.minNativeZoom && t8 < e7.minNativeZoom ? e7.minNativeZoom : void 0 !== e7.maxNativeZoom && e7.maxNativeZoom < t8 ? e7.maxNativeZoom : t8;
      }, _setView: function(t8, e7, i7, n5) {
        var o8 = Math.round(e7), o8 = void 0 !== this.options.maxZoom && o8 > this.options.maxZoom || void 0 !== this.options.minZoom && o8 < this.options.minZoom ? void 0 : this._clampZoom(o8), s5 = this.options.updateWhenZooming && o8 !== this._tileZoom;
        n5 && !s5 || (this._tileZoom = o8, this._abortLoading && this._abortLoading(), this._updateLevels(), this._resetGrid(), void 0 !== o8 && this._update(t8), i7 || this._pruneTiles(), this._noPrune = !!i7), this._setZoomTransforms(t8, e7);
      }, _setZoomTransforms: function(t8, e7) {
        for (var i7 in this._levels) this._setZoomTransform(this._levels[i7], t8, e7);
      }, _setZoomTransform: function(t8, e7, i7) {
        var n5 = this._map.getZoomScale(i7, t8.zoom), e7 = t8.origin.multiplyBy(n5).subtract(this._map._getNewPixelOrigin(e7, i7)).round();
        b3.any3d ? be(t8.el, e7, n5) : Z2(t8.el, e7);
      }, _resetGrid: function() {
        var t8 = this._map, e7 = t8.options.crs, i7 = this._tileSize = this.getTileSize(), n5 = this._tileZoom, o8 = this._map.getPixelWorldBounds(this._tileZoom);
        o8 && (this._globalTileRange = this._pxBoundsToTileRange(o8)), this._wrapX = e7.wrapLng && !this.options.noWrap && [Math.floor(t8.project([0, e7.wrapLng[0]], n5).x / i7.x), Math.ceil(t8.project([0, e7.wrapLng[1]], n5).x / i7.y)], this._wrapY = e7.wrapLat && !this.options.noWrap && [Math.floor(t8.project([e7.wrapLat[0], 0], n5).y / i7.x), Math.ceil(t8.project([e7.wrapLat[1], 0], n5).y / i7.y)];
      }, _onMoveEnd: function() {
        this._map && !this._map._animatingZoom && this._update();
      }, _getTiledPixelBounds: function(t8) {
        var e7 = this._map, i7 = e7._animatingZoom ? Math.max(e7._animateToZoom, e7.getZoom()) : e7.getZoom(), i7 = e7.getZoomScale(i7, this._tileZoom), t8 = e7.project(t8, this._tileZoom).floor(), e7 = e7.getSize().divideBy(2 * i7);
        return new f3(t8.subtract(e7), t8.add(e7));
      }, _update: function(t8) {
        var e7 = this._map;
        if (e7) {
          var i7 = this._clampZoom(e7.getZoom());
          if (void 0 === t8 && (t8 = e7.getCenter()), void 0 !== this._tileZoom) {
            var n5, e7 = this._getTiledPixelBounds(t8), o8 = this._pxBoundsToTileRange(e7), s5 = o8.getCenter(), r6 = [], e7 = this.options.keepBuffer, a4 = new f3(o8.getBottomLeft().subtract([e7, -e7]), o8.getTopRight().add([e7, -e7]));
            if (!(isFinite(o8.min.x) && isFinite(o8.min.y) && isFinite(o8.max.x) && isFinite(o8.max.y))) throw new Error("Attempted to load an infinite number of tiles");
            for (n5 in this._tiles) {
              var h4 = this._tiles[n5].coords;
              h4.z === this._tileZoom && a4.contains(new p4(h4.x, h4.y)) || (this._tiles[n5].current = false);
            }
            if (1 < Math.abs(i7 - this._tileZoom)) this._setView(t8, i7);
            else {
              for (var l5 = o8.min.y; l5 <= o8.max.y; l5++) for (var u4 = o8.min.x; u4 <= o8.max.x; u4++) {
                var c5, d4 = new p4(u4, l5);
                d4.z = this._tileZoom, this._isValidTile(d4) && ((c5 = this._tiles[this._tileCoordsToKey(d4)]) ? c5.current = true : r6.push(d4));
              }
              if (r6.sort(function(t9, e8) {
                return t9.distanceTo(s5) - e8.distanceTo(s5);
              }), 0 !== r6.length) {
                this._loading || (this._loading = true, this.fire("loading"));
                for (var _3 = document.createDocumentFragment(), u4 = 0; u4 < r6.length; u4++) this._addTile(r6[u4], _3);
                this._level.el.appendChild(_3);
              }
            }
          }
        }
      }, _isValidTile: function(t8) {
        var e7 = this._map.options.crs;
        if (!e7.infinite) {
          var i7 = this._globalTileRange;
          if (!e7.wrapLng && (t8.x < i7.min.x || t8.x > i7.max.x) || !e7.wrapLat && (t8.y < i7.min.y || t8.y > i7.max.y)) return false;
        }
        return !this.options.bounds || (e7 = this._tileCoordsToBounds(t8), g2(this.options.bounds).overlaps(e7));
      }, _keyToBounds: function(t8) {
        return this._tileCoordsToBounds(this._keyToTileCoords(t8));
      }, _tileCoordsToNwSe: function(t8) {
        var e7 = this._map, i7 = this.getTileSize(), n5 = t8.scaleBy(i7), i7 = n5.add(i7);
        return [e7.unproject(n5, t8.z), e7.unproject(i7, t8.z)];
      }, _tileCoordsToBounds: function(t8) {
        t8 = this._tileCoordsToNwSe(t8), t8 = new s4(t8[0], t8[1]);
        return t8 = this.options.noWrap ? t8 : this._map.wrapLatLngBounds(t8);
      }, _tileCoordsToKey: function(t8) {
        return t8.x + ":" + t8.y + ":" + t8.z;
      }, _keyToTileCoords: function(t8) {
        var t8 = t8.split(":"), e7 = new p4(+t8[0], +t8[1]);
        return e7.z = +t8[2], e7;
      }, _removeTile: function(t8) {
        var e7 = this._tiles[t8];
        e7 && (T2(e7.el), delete this._tiles[t8], this.fire("tileunload", { tile: e7.el, coords: this._keyToTileCoords(t8) }));
      }, _initTile: function(t8) {
        M2(t8, "leaflet-tile");
        var e7 = this.getTileSize();
        t8.style.width = e7.x + "px", t8.style.height = e7.y + "px", t8.onselectstart = u3, t8.onmousemove = u3, b3.ielt9 && this.options.opacity < 1 && C2(t8, this.options.opacity);
      }, _addTile: function(t8, e7) {
        var i7 = this._getTilePos(t8), n5 = this._tileCoordsToKey(t8), o8 = this.createTile(this._wrapCoords(t8), a3(this._tileReady, this, t8));
        this._initTile(o8), this.createTile.length < 2 && x2(a3(this._tileReady, this, t8, null, o8)), Z2(o8, i7), this._tiles[n5] = { el: o8, coords: t8, current: true }, e7.appendChild(o8), this.fire("tileloadstart", { tile: o8, coords: t8 });
      }, _tileReady: function(t8, e7, i7) {
        e7 && this.fire("tileerror", { error: e7, tile: i7, coords: t8 });
        var n5 = this._tileCoordsToKey(t8);
        (i7 = this._tiles[n5]) && (i7.loaded = +/* @__PURE__ */ new Date(), this._map._fadeAnimated ? (C2(i7.el, 0), r5(this._fadeFrame), this._fadeFrame = x2(this._updateOpacity, this)) : (i7.active = true, this._pruneTiles()), e7 || (M2(i7.el, "leaflet-tile-loaded"), this.fire("tileload", { tile: i7.el, coords: t8 })), this._noTilesToLoad() && (this._loading = false, this.fire("load"), b3.ielt9 || !this._map._fadeAnimated ? x2(this._pruneTiles, this) : setTimeout(a3(this._pruneTiles, this), 250)));
      }, _getTilePos: function(t8) {
        return t8.scaleBy(this.getTileSize()).subtract(this._level.origin);
      }, _wrapCoords: function(t8) {
        var e7 = new p4(this._wrapX ? H4(t8.x, this._wrapX) : t8.x, this._wrapY ? H4(t8.y, this._wrapY) : t8.y);
        return e7.z = t8.z, e7;
      }, _pxBoundsToTileRange: function(t8) {
        var e7 = this.getTileSize();
        return new f3(t8.min.unscaleBy(e7).floor(), t8.max.unscaleBy(e7).ceil().subtract([1, 1]));
      }, _noTilesToLoad: function() {
        for (var t8 in this._tiles) if (!this._tiles[t8].loaded) return false;
        return true;
      } });
      var Di = Ni.extend({ options: { minZoom: 0, maxZoom: 18, subdomains: "abc", errorTileUrl: "", zoomOffset: 0, tms: false, zoomReverse: false, detectRetina: false, crossOrigin: false, referrerPolicy: false }, initialize: function(t8, e7) {
        this._url = t8, (e7 = c4(this, e7)).detectRetina && b3.retina && 0 < e7.maxZoom ? (e7.tileSize = Math.floor(e7.tileSize / 2), e7.zoomReverse ? (e7.zoomOffset--, e7.minZoom = Math.min(e7.maxZoom, e7.minZoom + 1)) : (e7.zoomOffset++, e7.maxZoom = Math.max(e7.minZoom, e7.maxZoom - 1)), e7.minZoom = Math.max(0, e7.minZoom)) : e7.zoomReverse ? e7.minZoom = Math.min(e7.maxZoom, e7.minZoom) : e7.maxZoom = Math.max(e7.minZoom, e7.maxZoom), "string" == typeof e7.subdomains && (e7.subdomains = e7.subdomains.split("")), this.on("tileunload", this._onTileRemove);
      }, setUrl: function(t8, e7) {
        return this._url === t8 && void 0 === e7 && (e7 = true), this._url = t8, e7 || this.redraw(), this;
      }, createTile: function(t8, e7) {
        var i7 = document.createElement("img");
        return S3(i7, "load", a3(this._tileOnLoad, this, e7, i7)), S3(i7, "error", a3(this._tileOnError, this, e7, i7)), !this.options.crossOrigin && "" !== this.options.crossOrigin || (i7.crossOrigin = true === this.options.crossOrigin ? "" : this.options.crossOrigin), "string" == typeof this.options.referrerPolicy && (i7.referrerPolicy = this.options.referrerPolicy), i7.alt = "", i7.src = this.getTileUrl(t8), i7;
      }, getTileUrl: function(t8) {
        var e7 = { r: b3.retina ? "@2x" : "", s: this._getSubdomain(t8), x: t8.x, y: t8.y, z: this._getZoomForUrl() };
        return this._map && !this._map.options.crs.infinite && (t8 = this._globalTileRange.max.y - t8.y, this.options.tms && (e7.y = t8), e7["-y"] = t8), q(this._url, l4(e7, this.options));
      }, _tileOnLoad: function(t8, e7) {
        b3.ielt9 ? setTimeout(a3(t8, this, null, e7), 0) : t8(null, e7);
      }, _tileOnError: function(t8, e7, i7) {
        var n5 = this.options.errorTileUrl;
        n5 && e7.getAttribute("src") !== n5 && (e7.src = n5), t8(i7, e7);
      }, _onTileRemove: function(t8) {
        t8.tile.onload = null;
      }, _getZoomForUrl: function() {
        var t8 = this._tileZoom, e7 = this.options.maxZoom;
        return (t8 = this.options.zoomReverse ? e7 - t8 : t8) + this.options.zoomOffset;
      }, _getSubdomain: function(t8) {
        t8 = Math.abs(t8.x + t8.y) % this.options.subdomains.length;
        return this.options.subdomains[t8];
      }, _abortLoading: function() {
        var t8, e7, i7;
        for (t8 in this._tiles) this._tiles[t8].coords.z !== this._tileZoom && ((i7 = this._tiles[t8].el).onload = u3, i7.onerror = u3, i7.complete || (i7.src = K, e7 = this._tiles[t8].coords, T2(i7), delete this._tiles[t8], this.fire("tileabort", { tile: i7, coords: e7 })));
      }, _removeTile: function(t8) {
        var e7 = this._tiles[t8];
        if (e7) return e7.el.setAttribute("src", K), Ni.prototype._removeTile.call(this, t8);
      }, _tileReady: function(t8, e7, i7) {
        if (this._map && (!i7 || i7.getAttribute("src") !== K)) return Ni.prototype._tileReady.call(this, t8, e7, i7);
      } });
      function ji(t8, e7) {
        return new Di(t8, e7);
      }
      var Hi = Di.extend({ defaultWmsParams: { service: "WMS", request: "GetMap", layers: "", styles: "", format: "image/jpeg", transparent: false, version: "1.1.1" }, options: { crs: null, uppercase: false }, initialize: function(t8, e7) {
        this._url = t8;
        var i7, n5 = l4({}, this.defaultWmsParams);
        for (i7 in e7) i7 in this.options || (n5[i7] = e7[i7]);
        var t8 = (e7 = c4(this, e7)).detectRetina && b3.retina ? 2 : 1, o8 = this.getTileSize();
        n5.width = o8.x * t8, n5.height = o8.y * t8, this.wmsParams = n5;
      }, onAdd: function(t8) {
        this._crs = this.options.crs || t8.options.crs, this._wmsVersion = parseFloat(this.wmsParams.version);
        var e7 = 1.3 <= this._wmsVersion ? "crs" : "srs";
        this.wmsParams[e7] = this._crs.code, Di.prototype.onAdd.call(this, t8);
      }, getTileUrl: function(t8) {
        var e7 = this._tileCoordsToNwSe(t8), i7 = this._crs, i7 = _2(i7.project(e7[0]), i7.project(e7[1])), e7 = i7.min, i7 = i7.max, e7 = (1.3 <= this._wmsVersion && this._crs === li ? [e7.y, e7.x, i7.y, i7.x] : [e7.x, e7.y, i7.x, i7.y]).join(","), i7 = Di.prototype.getTileUrl.call(this, t8);
        return i7 + U(this.wmsParams, i7, this.options.uppercase) + (this.options.uppercase ? "&BBOX=" : "&bbox=") + e7;
      }, setParams: function(t8, e7) {
        return l4(this.wmsParams, t8), e7 || this.redraw(), this;
      } });
      Di.WMS = Hi, ji.wms = function(t8, e7) {
        return new Hi(t8, e7);
      };
      var Wi = o7.extend({ options: { padding: 0.1 }, initialize: function(t8) {
        c4(this, t8), h3(this), this._layers = this._layers || {};
      }, onAdd: function() {
        this._container || (this._initContainer(), M2(this._container, "leaflet-zoom-animated")), this.getPane().appendChild(this._container), this._update(), this.on("update", this._updatePaths, this);
      }, onRemove: function() {
        this.off("update", this._updatePaths, this), this._destroyContainer();
      }, getEvents: function() {
        var t8 = { viewreset: this._reset, zoom: this._onZoom, moveend: this._update, zoomend: this._onZoomEnd };
        return this._zoomAnimated && (t8.zoomanim = this._onAnimZoom), t8;
      }, _onAnimZoom: function(t8) {
        this._updateTransform(t8.center, t8.zoom);
      }, _onZoom: function() {
        this._updateTransform(this._map.getCenter(), this._map.getZoom());
      }, _updateTransform: function(t8, e7) {
        var i7 = this._map.getZoomScale(e7, this._zoom), n5 = this._map.getSize().multiplyBy(0.5 + this.options.padding), o8 = this._map.project(this._center, e7), n5 = n5.multiplyBy(-i7).add(o8).subtract(this._map._getNewPixelOrigin(t8, e7));
        b3.any3d ? be(this._container, n5, i7) : Z2(this._container, n5);
      }, _reset: function() {
        for (var t8 in this._update(), this._updateTransform(this._center, this._zoom), this._layers) this._layers[t8]._reset();
      }, _onZoomEnd: function() {
        for (var t8 in this._layers) this._layers[t8]._project();
      }, _updatePaths: function() {
        for (var t8 in this._layers) this._layers[t8]._update();
      }, _update: function() {
        var t8 = this.options.padding, e7 = this._map.getSize(), i7 = this._map.containerPointToLayerPoint(e7.multiplyBy(-t8)).round();
        this._bounds = new f3(i7, i7.add(e7.multiplyBy(1 + 2 * t8)).round()), this._center = this._map.getCenter(), this._zoom = this._map.getZoom();
      } }), Fi = Wi.extend({ options: { tolerance: 0 }, getEvents: function() {
        var t8 = Wi.prototype.getEvents.call(this);
        return t8.viewprereset = this._onViewPreReset, t8;
      }, _onViewPreReset: function() {
        this._postponeUpdatePaths = true;
      }, onAdd: function() {
        Wi.prototype.onAdd.call(this), this._draw();
      }, _initContainer: function() {
        var t8 = this._container = document.createElement("canvas");
        S3(t8, "mousemove", this._onMouseMove, this), S3(t8, "click dblclick mousedown mouseup contextmenu", this._onClick, this), S3(t8, "mouseout", this._handleMouseOut, this), t8._leaflet_disable_events = true, this._ctx = t8.getContext("2d");
      }, _destroyContainer: function() {
        r5(this._redrawRequest), delete this._ctx, T2(this._container), k2(this._container), delete this._container;
      }, _updatePaths: function() {
        if (!this._postponeUpdatePaths) {
          for (var t8 in this._redrawBounds = null, this._layers) this._layers[t8]._update();
          this._redraw();
        }
      }, _update: function() {
        var t8, e7, i7, n5;
        this._map._animatingZoom && this._bounds || (Wi.prototype._update.call(this), t8 = this._bounds, e7 = this._container, i7 = t8.getSize(), n5 = b3.retina ? 2 : 1, Z2(e7, t8.min), e7.width = n5 * i7.x, e7.height = n5 * i7.y, e7.style.width = i7.x + "px", e7.style.height = i7.y + "px", b3.retina && this._ctx.scale(2, 2), this._ctx.translate(-t8.min.x, -t8.min.y), this.fire("update"));
      }, _reset: function() {
        Wi.prototype._reset.call(this), this._postponeUpdatePaths && (this._postponeUpdatePaths = false, this._updatePaths());
      }, _initPath: function(t8) {
        this._updateDashArray(t8);
        t8 = (this._layers[h3(t8)] = t8)._order = { layer: t8, prev: this._drawLast, next: null };
        this._drawLast && (this._drawLast.next = t8), this._drawLast = t8, this._drawFirst = this._drawFirst || this._drawLast;
      }, _addPath: function(t8) {
        this._requestRedraw(t8);
      }, _removePath: function(t8) {
        var e7 = t8._order, i7 = e7.next, e7 = e7.prev;
        i7 ? i7.prev = e7 : this._drawLast = e7, e7 ? e7.next = i7 : this._drawFirst = i7, delete t8._order, delete this._layers[h3(t8)], this._requestRedraw(t8);
      }, _updatePath: function(t8) {
        this._extendRedrawBounds(t8), t8._project(), t8._update(), this._requestRedraw(t8);
      }, _updateStyle: function(t8) {
        this._updateDashArray(t8), this._requestRedraw(t8);
      }, _updateDashArray: function(t8) {
        if ("string" == typeof t8.options.dashArray) {
          for (var e7, i7 = t8.options.dashArray.split(/[, ]+/), n5 = [], o8 = 0; o8 < i7.length; o8++) {
            if (e7 = Number(i7[o8]), isNaN(e7)) return;
            n5.push(e7);
          }
          t8.options._dashArray = n5;
        } else t8.options._dashArray = t8.options.dashArray;
      }, _requestRedraw: function(t8) {
        this._map && (this._extendRedrawBounds(t8), this._redrawRequest = this._redrawRequest || x2(this._redraw, this));
      }, _extendRedrawBounds: function(t8) {
        var e7;
        t8._pxBounds && (e7 = (t8.options.weight || 0) + 1, this._redrawBounds = this._redrawBounds || new f3(), this._redrawBounds.extend(t8._pxBounds.min.subtract([e7, e7])), this._redrawBounds.extend(t8._pxBounds.max.add([e7, e7])));
      }, _redraw: function() {
        this._redrawRequest = null, this._redrawBounds && (this._redrawBounds.min._floor(), this._redrawBounds.max._ceil()), this._clear(), this._draw(), this._redrawBounds = null;
      }, _clear: function() {
        var t8, e7 = this._redrawBounds;
        e7 ? (t8 = e7.getSize(), this._ctx.clearRect(e7.min.x, e7.min.y, t8.x, t8.y)) : (this._ctx.save(), this._ctx.setTransform(1, 0, 0, 1, 0, 0), this._ctx.clearRect(0, 0, this._container.width, this._container.height), this._ctx.restore());
      }, _draw: function() {
        var t8, e7, i7 = this._redrawBounds;
        this._ctx.save(), i7 && (e7 = i7.getSize(), this._ctx.beginPath(), this._ctx.rect(i7.min.x, i7.min.y, e7.x, e7.y), this._ctx.clip()), this._drawing = true;
        for (var n5 = this._drawFirst; n5; n5 = n5.next) t8 = n5.layer, (!i7 || t8._pxBounds && t8._pxBounds.intersects(i7)) && t8._updatePath();
        this._drawing = false, this._ctx.restore();
      }, _updatePoly: function(t8, e7) {
        if (this._drawing) {
          var i7, n5, o8, s5, r6 = t8._parts, a4 = r6.length, h4 = this._ctx;
          if (a4) {
            for (h4.beginPath(), i7 = 0; i7 < a4; i7++) {
              for (n5 = 0, o8 = r6[i7].length; n5 < o8; n5++) s5 = r6[i7][n5], h4[n5 ? "lineTo" : "moveTo"](s5.x, s5.y);
              e7 && h4.closePath();
            }
            this._fillStroke(h4, t8);
          }
        }
      }, _updateCircle: function(t8) {
        var e7, i7, n5, o8;
        this._drawing && !t8._empty() && (e7 = t8._point, i7 = this._ctx, n5 = Math.max(Math.round(t8._radius), 1), 1 != (o8 = (Math.max(Math.round(t8._radiusY), 1) || n5) / n5) && (i7.save(), i7.scale(1, o8)), i7.beginPath(), i7.arc(e7.x, e7.y / o8, n5, 0, 2 * Math.PI, false), 1 != o8 && i7.restore(), this._fillStroke(i7, t8));
      }, _fillStroke: function(t8, e7) {
        var i7 = e7.options;
        i7.fill && (t8.globalAlpha = i7.fillOpacity, t8.fillStyle = i7.fillColor || i7.color, t8.fill(i7.fillRule || "evenodd")), i7.stroke && 0 !== i7.weight && (t8.setLineDash && t8.setLineDash(e7.options && e7.options._dashArray || []), t8.globalAlpha = i7.opacity, t8.lineWidth = i7.weight, t8.strokeStyle = i7.color, t8.lineCap = i7.lineCap, t8.lineJoin = i7.lineJoin, t8.stroke());
      }, _onClick: function(t8) {
        for (var e7, i7, n5 = this._map.mouseEventToLayerPoint(t8), o8 = this._drawFirst; o8; o8 = o8.next) (e7 = o8.layer).options.interactive && e7._containsPoint(n5) && (("click" === t8.type || "preclick" === t8.type) && this._map._draggableMoved(e7) || (i7 = e7));
        this._fireEvent(!!i7 && [i7], t8);
      }, _onMouseMove: function(t8) {
        var e7;
        !this._map || this._map.dragging.moving() || this._map._animatingZoom || (e7 = this._map.mouseEventToLayerPoint(t8), this._handleMouseHover(t8, e7));
      }, _handleMouseOut: function(t8) {
        var e7 = this._hoveredLayer;
        e7 && (z2(this._container, "leaflet-interactive"), this._fireEvent([e7], t8, "mouseout"), this._hoveredLayer = null, this._mouseHoverThrottled = false);
      }, _handleMouseHover: function(t8, e7) {
        if (!this._mouseHoverThrottled) {
          for (var i7, n5, o8 = this._drawFirst; o8; o8 = o8.next) (i7 = o8.layer).options.interactive && i7._containsPoint(e7) && (n5 = i7);
          n5 !== this._hoveredLayer && (this._handleMouseOut(t8), n5 && (M2(this._container, "leaflet-interactive"), this._fireEvent([n5], t8, "mouseover"), this._hoveredLayer = n5)), this._fireEvent(!!this._hoveredLayer && [this._hoveredLayer], t8), this._mouseHoverThrottled = true, setTimeout(a3(function() {
            this._mouseHoverThrottled = false;
          }, this), 32);
        }
      }, _fireEvent: function(t8, e7, i7) {
        this._map._fireDOMEvent(e7, i7 || e7.type, t8);
      }, _bringToFront: function(t8) {
        var e7, i7, n5 = t8._order;
        n5 && (e7 = n5.next, i7 = n5.prev, e7 && ((e7.prev = i7) ? i7.next = e7 : e7 && (this._drawFirst = e7), n5.prev = this._drawLast, (this._drawLast.next = n5).next = null, this._drawLast = n5, this._requestRedraw(t8)));
      }, _bringToBack: function(t8) {
        var e7, i7, n5 = t8._order;
        n5 && (e7 = n5.next, (i7 = n5.prev) && ((i7.next = e7) ? e7.prev = i7 : i7 && (this._drawLast = i7), n5.prev = null, n5.next = this._drawFirst, this._drawFirst.prev = n5, this._drawFirst = n5, this._requestRedraw(t8)));
      } });
      function Ui(t8) {
        return b3.canvas ? new Fi(t8) : null;
      }
      var Vi = (function() {
        try {
          return document.namespaces.add("lvml", "urn:schemas-microsoft-com:vml"), function(t8) {
            return document.createElement("<lvml:" + t8 + ' class="lvml">');
          };
        } catch (t8) {
        }
        return function(t8) {
          return document.createElement("<" + t8 + ' xmlns="urn:schemas-microsoft.com:vml" class="lvml">');
        };
      })(), zt = { _initContainer: function() {
        this._container = P2("div", "leaflet-vml-container");
      }, _update: function() {
        this._map._animatingZoom || (Wi.prototype._update.call(this), this.fire("update"));
      }, _initPath: function(t8) {
        var e7 = t8._container = Vi("shape");
        M2(e7, "leaflet-vml-shape " + (this.options.className || "")), e7.coordsize = "1 1", t8._path = Vi("path"), e7.appendChild(t8._path), this._updateStyle(t8), this._layers[h3(t8)] = t8;
      }, _addPath: function(t8) {
        var e7 = t8._container;
        this._container.appendChild(e7), t8.options.interactive && t8.addInteractiveTarget(e7);
      }, _removePath: function(t8) {
        var e7 = t8._container;
        T2(e7), t8.removeInteractiveTarget(e7), delete this._layers[h3(t8)];
      }, _updateStyle: function(t8) {
        var e7 = t8._stroke, i7 = t8._fill, n5 = t8.options, o8 = t8._container;
        o8.stroked = !!n5.stroke, o8.filled = !!n5.fill, n5.stroke ? (e7 = e7 || (t8._stroke = Vi("stroke")), o8.appendChild(e7), e7.weight = n5.weight + "px", e7.color = n5.color, e7.opacity = n5.opacity, n5.dashArray ? e7.dashStyle = d3(n5.dashArray) ? n5.dashArray.join(" ") : n5.dashArray.replace(/( *, *)/g, " ") : e7.dashStyle = "", e7.endcap = n5.lineCap.replace("butt", "flat"), e7.joinstyle = n5.lineJoin) : e7 && (o8.removeChild(e7), t8._stroke = null), n5.fill ? (i7 = i7 || (t8._fill = Vi("fill")), o8.appendChild(i7), i7.color = n5.fillColor || n5.color, i7.opacity = n5.fillOpacity) : i7 && (o8.removeChild(i7), t8._fill = null);
      }, _updateCircle: function(t8) {
        var e7 = t8._point.round(), i7 = Math.round(t8._radius), n5 = Math.round(t8._radiusY || i7);
        this._setPath(t8, t8._empty() ? "M0 0" : "AL " + e7.x + "," + e7.y + " " + i7 + "," + n5 + " 0,23592600");
      }, _setPath: function(t8, e7) {
        t8._path.v = e7;
      }, _bringToFront: function(t8) {
        fe(t8._container);
      }, _bringToBack: function(t8) {
        ge(t8._container);
      } }, qi = b3.vml ? Vi : ct, Gi = Wi.extend({ _initContainer: function() {
        this._container = qi("svg"), this._container.setAttribute("pointer-events", "none"), this._rootGroup = qi("g"), this._container.appendChild(this._rootGroup);
      }, _destroyContainer: function() {
        T2(this._container), k2(this._container), delete this._container, delete this._rootGroup, delete this._svgSize;
      }, _update: function() {
        var t8, e7, i7;
        this._map._animatingZoom && this._bounds || (Wi.prototype._update.call(this), e7 = (t8 = this._bounds).getSize(), i7 = this._container, this._svgSize && this._svgSize.equals(e7) || (this._svgSize = e7, i7.setAttribute("width", e7.x), i7.setAttribute("height", e7.y)), Z2(i7, t8.min), i7.setAttribute("viewBox", [t8.min.x, t8.min.y, e7.x, e7.y].join(" ")), this.fire("update"));
      }, _initPath: function(t8) {
        var e7 = t8._path = qi("path");
        t8.options.className && M2(e7, t8.options.className), t8.options.interactive && M2(e7, "leaflet-interactive"), this._updateStyle(t8), this._layers[h3(t8)] = t8;
      }, _addPath: function(t8) {
        this._rootGroup || this._initContainer(), this._rootGroup.appendChild(t8._path), t8.addInteractiveTarget(t8._path);
      }, _removePath: function(t8) {
        T2(t8._path), t8.removeInteractiveTarget(t8._path), delete this._layers[h3(t8)];
      }, _updatePath: function(t8) {
        t8._project(), t8._update();
      }, _updateStyle: function(t8) {
        var e7 = t8._path, t8 = t8.options;
        e7 && (t8.stroke ? (e7.setAttribute("stroke", t8.color), e7.setAttribute("stroke-opacity", t8.opacity), e7.setAttribute("stroke-width", t8.weight), e7.setAttribute("stroke-linecap", t8.lineCap), e7.setAttribute("stroke-linejoin", t8.lineJoin), t8.dashArray ? e7.setAttribute("stroke-dasharray", t8.dashArray) : e7.removeAttribute("stroke-dasharray"), t8.dashOffset ? e7.setAttribute("stroke-dashoffset", t8.dashOffset) : e7.removeAttribute("stroke-dashoffset")) : e7.setAttribute("stroke", "none"), t8.fill ? (e7.setAttribute("fill", t8.fillColor || t8.color), e7.setAttribute("fill-opacity", t8.fillOpacity), e7.setAttribute("fill-rule", t8.fillRule || "evenodd")) : e7.setAttribute("fill", "none"));
      }, _updatePoly: function(t8, e7) {
        this._setPath(t8, dt(t8._parts, e7));
      }, _updateCircle: function(t8) {
        var e7 = t8._point, i7 = Math.max(Math.round(t8._radius), 1), n5 = "a" + i7 + "," + (Math.max(Math.round(t8._radiusY), 1) || i7) + " 0 1,0 ", e7 = t8._empty() ? "M0 0" : "M" + (e7.x - i7) + "," + e7.y + n5 + 2 * i7 + ",0 " + n5 + 2 * -i7 + ",0 ";
        this._setPath(t8, e7);
      }, _setPath: function(t8, e7) {
        t8._path.setAttribute("d", e7);
      }, _bringToFront: function(t8) {
        fe(t8._path);
      }, _bringToBack: function(t8) {
        ge(t8._path);
      } });
      function Ki(t8) {
        return b3.svg || b3.vml ? new Gi(t8) : null;
      }
      b3.vml && Gi.include(zt), A2.include({ getRenderer: function(t8) {
        t8 = (t8 = t8.options.renderer || this._getPaneRenderer(t8.options.pane) || this.options.renderer || this._renderer) || (this._renderer = this._createRenderer());
        return this.hasLayer(t8) || this.addLayer(t8), t8;
      }, _getPaneRenderer: function(t8) {
        var e7;
        return "overlayPane" !== t8 && void 0 !== t8 && (void 0 === (e7 = this._paneRenderers[t8]) && (e7 = this._createRenderer({ pane: t8 }), this._paneRenderers[t8] = e7), e7);
      }, _createRenderer: function(t8) {
        return this.options.preferCanvas && Ui(t8) || Ki(t8);
      } });
      var Yi = xi.extend({ initialize: function(t8, e7) {
        xi.prototype.initialize.call(this, this._boundsToLatLngs(t8), e7);
      }, setBounds: function(t8) {
        return this.setLatLngs(this._boundsToLatLngs(t8));
      }, _boundsToLatLngs: function(t8) {
        return [(t8 = g2(t8)).getSouthWest(), t8.getNorthWest(), t8.getNorthEast(), t8.getSouthEast()];
      } });
      Gi.create = qi, Gi.pointsToPath = dt, wi.geometryToLayer = bi, wi.coordsToLatLng = Li, wi.coordsToLatLngs = Ti, wi.latLngToCoords = Mi, wi.latLngsToCoords = zi, wi.getFeature = Ci, wi.asFeature = Zi, A2.mergeOptions({ boxZoom: true });
      var _t = n4.extend({ initialize: function(t8) {
        this._map = t8, this._container = t8._container, this._pane = t8._panes.overlayPane, this._resetStateTimeout = 0, t8.on("unload", this._destroy, this);
      }, addHooks: function() {
        S3(this._container, "mousedown", this._onMouseDown, this);
      }, removeHooks: function() {
        k2(this._container, "mousedown", this._onMouseDown, this);
      }, moved: function() {
        return this._moved;
      }, _destroy: function() {
        T2(this._pane), delete this._pane;
      }, _resetState: function() {
        this._resetStateTimeout = 0, this._moved = false;
      }, _clearDeferredResetState: function() {
        0 !== this._resetStateTimeout && (clearTimeout(this._resetStateTimeout), this._resetStateTimeout = 0);
      }, _onMouseDown: function(t8) {
        if (!t8.shiftKey || 1 !== t8.which && 1 !== t8.button) return false;
        this._clearDeferredResetState(), this._resetState(), re(), Le(), this._startPoint = this._map.mouseEventToContainerPoint(t8), S3(document, { contextmenu: Re, mousemove: this._onMouseMove, mouseup: this._onMouseUp, keydown: this._onKeyDown }, this);
      }, _onMouseMove: function(t8) {
        this._moved || (this._moved = true, this._box = P2("div", "leaflet-zoom-box", this._container), M2(this._container, "leaflet-crosshair"), this._map.fire("boxzoomstart")), this._point = this._map.mouseEventToContainerPoint(t8);
        var t8 = new f3(this._point, this._startPoint), e7 = t8.getSize();
        Z2(this._box, t8.min), this._box.style.width = e7.x + "px", this._box.style.height = e7.y + "px";
      }, _finish: function() {
        this._moved && (T2(this._box), z2(this._container, "leaflet-crosshair")), ae(), Te(), k2(document, { contextmenu: Re, mousemove: this._onMouseMove, mouseup: this._onMouseUp, keydown: this._onKeyDown }, this);
      }, _onMouseUp: function(t8) {
        1 !== t8.which && 1 !== t8.button || (this._finish(), this._moved && (this._clearDeferredResetState(), this._resetStateTimeout = setTimeout(a3(this._resetState, this), 0), t8 = new s4(this._map.containerPointToLatLng(this._startPoint), this._map.containerPointToLatLng(this._point)), this._map.fitBounds(t8).fire("boxzoomend", { boxZoomBounds: t8 })));
      }, _onKeyDown: function(t8) {
        27 === t8.keyCode && (this._finish(), this._clearDeferredResetState(), this._resetState());
      } }), Ct = (A2.addInitHook("addHandler", "boxZoom", _t), A2.mergeOptions({ doubleClickZoom: true }), n4.extend({ addHooks: function() {
        this._map.on("dblclick", this._onDoubleClick, this);
      }, removeHooks: function() {
        this._map.off("dblclick", this._onDoubleClick, this);
      }, _onDoubleClick: function(t8) {
        var e7 = this._map, i7 = e7.getZoom(), n5 = e7.options.zoomDelta, i7 = t8.originalEvent.shiftKey ? i7 - n5 : i7 + n5;
        "center" === e7.options.doubleClickZoom ? e7.setZoom(i7) : e7.setZoomAround(t8.containerPoint, i7);
      } })), Zt = (A2.addInitHook("addHandler", "doubleClickZoom", Ct), A2.mergeOptions({ dragging: true, inertia: true, inertiaDeceleration: 3400, inertiaMaxSpeed: 1 / 0, easeLinearity: 0.2, worldCopyJump: false, maxBoundsViscosity: 0 }), n4.extend({ addHooks: function() {
        var t8;
        this._draggable || (t8 = this._map, this._draggable = new Xe(t8._mapPane, t8._container), this._draggable.on({ dragstart: this._onDragStart, drag: this._onDrag, dragend: this._onDragEnd }, this), this._draggable.on("predrag", this._onPreDragLimit, this), t8.options.worldCopyJump && (this._draggable.on("predrag", this._onPreDragWrap, this), t8.on("zoomend", this._onZoomEnd, this), t8.whenReady(this._onZoomEnd, this))), M2(this._map._container, "leaflet-grab leaflet-touch-drag"), this._draggable.enable(), this._positions = [], this._times = [];
      }, removeHooks: function() {
        z2(this._map._container, "leaflet-grab"), z2(this._map._container, "leaflet-touch-drag"), this._draggable.disable();
      }, moved: function() {
        return this._draggable && this._draggable._moved;
      }, moving: function() {
        return this._draggable && this._draggable._moving;
      }, _onDragStart: function() {
        var t8, e7 = this._map;
        e7._stop(), this._map.options.maxBounds && this._map.options.maxBoundsViscosity ? (t8 = g2(this._map.options.maxBounds), this._offsetLimit = _2(this._map.latLngToContainerPoint(t8.getNorthWest()).multiplyBy(-1), this._map.latLngToContainerPoint(t8.getSouthEast()).multiplyBy(-1).add(this._map.getSize())), this._viscosity = Math.min(1, Math.max(0, this._map.options.maxBoundsViscosity))) : this._offsetLimit = null, e7.fire("movestart").fire("dragstart"), e7.options.inertia && (this._positions = [], this._times = []);
      }, _onDrag: function(t8) {
        var e7, i7;
        this._map.options.inertia && (e7 = this._lastTime = +/* @__PURE__ */ new Date(), i7 = this._lastPos = this._draggable._absPos || this._draggable._newPos, this._positions.push(i7), this._times.push(e7), this._prunePositions(e7)), this._map.fire("move", t8).fire("drag", t8);
      }, _prunePositions: function(t8) {
        for (; 1 < this._positions.length && 50 < t8 - this._times[0]; ) this._positions.shift(), this._times.shift();
      }, _onZoomEnd: function() {
        var t8 = this._map.getSize().divideBy(2), e7 = this._map.latLngToLayerPoint([0, 0]);
        this._initialWorldOffset = e7.subtract(t8).x, this._worldWidth = this._map.getPixelWorldBounds().getSize().x;
      }, _viscousLimit: function(t8, e7) {
        return t8 - (t8 - e7) * this._viscosity;
      }, _onPreDragLimit: function() {
        var t8, e7;
        this._viscosity && this._offsetLimit && (t8 = this._draggable._newPos.subtract(this._draggable._startPos), e7 = this._offsetLimit, t8.x < e7.min.x && (t8.x = this._viscousLimit(t8.x, e7.min.x)), t8.y < e7.min.y && (t8.y = this._viscousLimit(t8.y, e7.min.y)), t8.x > e7.max.x && (t8.x = this._viscousLimit(t8.x, e7.max.x)), t8.y > e7.max.y && (t8.y = this._viscousLimit(t8.y, e7.max.y)), this._draggable._newPos = this._draggable._startPos.add(t8));
      }, _onPreDragWrap: function() {
        var t8 = this._worldWidth, e7 = Math.round(t8 / 2), i7 = this._initialWorldOffset, n5 = this._draggable._newPos.x, o8 = (n5 - e7 + i7) % t8 + e7 - i7, n5 = (n5 + e7 + i7) % t8 - e7 - i7, t8 = Math.abs(o8 + i7) < Math.abs(n5 + i7) ? o8 : n5;
        this._draggable._absPos = this._draggable._newPos.clone(), this._draggable._newPos.x = t8;
      }, _onDragEnd: function(t8) {
        var e7, i7, n5, o8, s5 = this._map, r6 = s5.options, a4 = !r6.inertia || t8.noInertia || this._times.length < 2;
        s5.fire("dragend", t8), !a4 && (this._prunePositions(+/* @__PURE__ */ new Date()), t8 = this._lastPos.subtract(this._positions[0]), a4 = (this._lastTime - this._times[0]) / 1e3, e7 = r6.easeLinearity, a4 = (t8 = t8.multiplyBy(e7 / a4)).distanceTo([0, 0]), i7 = Math.min(r6.inertiaMaxSpeed, a4), t8 = t8.multiplyBy(i7 / a4), n5 = i7 / (r6.inertiaDeceleration * e7), (o8 = t8.multiplyBy(-n5 / 2).round()).x || o8.y) ? (o8 = s5._limitOffset(o8, s5.options.maxBounds), x2(function() {
          s5.panBy(o8, { duration: n5, easeLinearity: e7, noMoveStart: true, animate: true });
        })) : s5.fire("moveend");
      } })), St = (A2.addInitHook("addHandler", "dragging", Zt), A2.mergeOptions({ keyboard: true, keyboardPanDelta: 80 }), n4.extend({ keyCodes: { left: [37], right: [39], down: [40], up: [38], zoomIn: [187, 107, 61, 171], zoomOut: [189, 109, 54, 173] }, initialize: function(t8) {
        this._map = t8, this._setPanDelta(t8.options.keyboardPanDelta), this._setZoomDelta(t8.options.zoomDelta);
      }, addHooks: function() {
        var t8 = this._map._container;
        t8.tabIndex <= 0 && (t8.tabIndex = "0"), S3(t8, { focus: this._onFocus, blur: this._onBlur, mousedown: this._onMouseDown }, this), this._map.on({ focus: this._addHooks, blur: this._removeHooks }, this);
      }, removeHooks: function() {
        this._removeHooks(), k2(this._map._container, { focus: this._onFocus, blur: this._onBlur, mousedown: this._onMouseDown }, this), this._map.off({ focus: this._addHooks, blur: this._removeHooks }, this);
      }, _onMouseDown: function() {
        var t8, e7, i7;
        this._focused || (i7 = document.body, t8 = document.documentElement, e7 = i7.scrollTop || t8.scrollTop, i7 = i7.scrollLeft || t8.scrollLeft, this._map._container.focus(), window.scrollTo(i7, e7));
      }, _onFocus: function() {
        this._focused = true, this._map.fire("focus");
      }, _onBlur: function() {
        this._focused = false, this._map.fire("blur");
      }, _setPanDelta: function(t8) {
        for (var e7 = this._panKeys = {}, i7 = this.keyCodes, n5 = 0, o8 = i7.left.length; n5 < o8; n5++) e7[i7.left[n5]] = [-1 * t8, 0];
        for (n5 = 0, o8 = i7.right.length; n5 < o8; n5++) e7[i7.right[n5]] = [t8, 0];
        for (n5 = 0, o8 = i7.down.length; n5 < o8; n5++) e7[i7.down[n5]] = [0, t8];
        for (n5 = 0, o8 = i7.up.length; n5 < o8; n5++) e7[i7.up[n5]] = [0, -1 * t8];
      }, _setZoomDelta: function(t8) {
        for (var e7 = this._zoomKeys = {}, i7 = this.keyCodes, n5 = 0, o8 = i7.zoomIn.length; n5 < o8; n5++) e7[i7.zoomIn[n5]] = t8;
        for (n5 = 0, o8 = i7.zoomOut.length; n5 < o8; n5++) e7[i7.zoomOut[n5]] = -t8;
      }, _addHooks: function() {
        S3(document, "keydown", this._onKeyDown, this);
      }, _removeHooks: function() {
        k2(document, "keydown", this._onKeyDown, this);
      }, _onKeyDown: function(t8) {
        if (!(t8.altKey || t8.ctrlKey || t8.metaKey)) {
          var e7, i7, n5 = t8.keyCode, o8 = this._map;
          if (n5 in this._panKeys) o8._panAnim && o8._panAnim._inProgress || (i7 = this._panKeys[n5], t8.shiftKey && (i7 = m3(i7).multiplyBy(3)), o8.options.maxBounds && (i7 = o8._limitOffset(m3(i7), o8.options.maxBounds)), o8.options.worldCopyJump ? (e7 = o8.wrapLatLng(o8.unproject(o8.project(o8.getCenter()).add(i7))), o8.panTo(e7)) : o8.panBy(i7));
          else if (n5 in this._zoomKeys) o8.setZoom(o8.getZoom() + (t8.shiftKey ? 3 : 1) * this._zoomKeys[n5]);
          else {
            if (27 !== n5 || !o8._popup || !o8._popup.options.closeOnEscapeKey) return;
            o8.closePopup();
          }
          Re(t8);
        }
      } })), Et = (A2.addInitHook("addHandler", "keyboard", St), A2.mergeOptions({ scrollWheelZoom: true, wheelDebounceTime: 40, wheelPxPerZoomLevel: 60 }), n4.extend({ addHooks: function() {
        S3(this._map._container, "wheel", this._onWheelScroll, this), this._delta = 0;
      }, removeHooks: function() {
        k2(this._map._container, "wheel", this._onWheelScroll, this);
      }, _onWheelScroll: function(t8) {
        var e7 = He(t8), i7 = this._map.options.wheelDebounceTime, e7 = (this._delta += e7, this._lastMousePos = this._map.mouseEventToContainerPoint(t8), this._startTime || (this._startTime = +/* @__PURE__ */ new Date()), Math.max(i7 - (+/* @__PURE__ */ new Date() - this._startTime), 0));
        clearTimeout(this._timer), this._timer = setTimeout(a3(this._performZoom, this), e7), Re(t8);
      }, _performZoom: function() {
        var t8 = this._map, e7 = t8.getZoom(), i7 = this._map.options.zoomSnap || 0, n5 = (t8._stop(), this._delta / (4 * this._map.options.wheelPxPerZoomLevel)), n5 = 4 * Math.log(2 / (1 + Math.exp(-Math.abs(n5)))) / Math.LN2, i7 = i7 ? Math.ceil(n5 / i7) * i7 : n5, n5 = t8._limitZoom(e7 + (0 < this._delta ? i7 : -i7)) - e7;
        this._delta = 0, this._startTime = null, n5 && ("center" === t8.options.scrollWheelZoom ? t8.setZoom(e7 + n5) : t8.setZoomAround(this._lastMousePos, e7 + n5));
      } })), kt = (A2.addInitHook("addHandler", "scrollWheelZoom", Et), A2.mergeOptions({ tapHold: b3.touchNative && b3.safari && b3.mobile, tapTolerance: 15 }), n4.extend({ addHooks: function() {
        S3(this._map._container, "touchstart", this._onDown, this);
      }, removeHooks: function() {
        k2(this._map._container, "touchstart", this._onDown, this);
      }, _onDown: function(t8) {
        var e7;
        clearTimeout(this._holdTimeout), 1 === t8.touches.length && (e7 = t8.touches[0], this._startPos = this._newPos = new p4(e7.clientX, e7.clientY), this._holdTimeout = setTimeout(a3(function() {
          this._cancel(), this._isTapValid() && (S3(document, "touchend", O), S3(document, "touchend touchcancel", this._cancelClickPrevent), this._simulateEvent("contextmenu", e7));
        }, this), 600), S3(document, "touchend touchcancel contextmenu", this._cancel, this), S3(document, "touchmove", this._onMove, this));
      }, _cancelClickPrevent: function t8() {
        k2(document, "touchend", O), k2(document, "touchend touchcancel", t8);
      }, _cancel: function() {
        clearTimeout(this._holdTimeout), k2(document, "touchend touchcancel contextmenu", this._cancel, this), k2(document, "touchmove", this._onMove, this);
      }, _onMove: function(t8) {
        t8 = t8.touches[0];
        this._newPos = new p4(t8.clientX, t8.clientY);
      }, _isTapValid: function() {
        return this._newPos.distanceTo(this._startPos) <= this._map.options.tapTolerance;
      }, _simulateEvent: function(t8, e7) {
        t8 = new MouseEvent(t8, { bubbles: true, cancelable: true, view: window, screenX: e7.screenX, screenY: e7.screenY, clientX: e7.clientX, clientY: e7.clientY });
        t8._simulated = true, e7.target.dispatchEvent(t8);
      } })), Ot = (A2.addInitHook("addHandler", "tapHold", kt), A2.mergeOptions({ touchZoom: b3.touch, bounceAtZoomLimits: true }), n4.extend({ addHooks: function() {
        M2(this._map._container, "leaflet-touch-zoom"), S3(this._map._container, "touchstart", this._onTouchStart, this);
      }, removeHooks: function() {
        z2(this._map._container, "leaflet-touch-zoom"), k2(this._map._container, "touchstart", this._onTouchStart, this);
      }, _onTouchStart: function(t8) {
        var e7, i7, n5 = this._map;
        !t8.touches || 2 !== t8.touches.length || n5._animatingZoom || this._zooming || (e7 = n5.mouseEventToContainerPoint(t8.touches[0]), i7 = n5.mouseEventToContainerPoint(t8.touches[1]), this._centerPoint = n5.getSize()._divideBy(2), this._startLatLng = n5.containerPointToLatLng(this._centerPoint), "center" !== n5.options.touchZoom && (this._pinchStartLatLng = n5.containerPointToLatLng(e7.add(i7)._divideBy(2))), this._startDist = e7.distanceTo(i7), this._startZoom = n5.getZoom(), this._moved = false, this._zooming = true, n5._stop(), S3(document, "touchmove", this._onTouchMove, this), S3(document, "touchend touchcancel", this._onTouchEnd, this), O(t8));
      }, _onTouchMove: function(t8) {
        if (t8.touches && 2 === t8.touches.length && this._zooming) {
          var e7 = this._map, i7 = e7.mouseEventToContainerPoint(t8.touches[0]), n5 = e7.mouseEventToContainerPoint(t8.touches[1]), o8 = i7.distanceTo(n5) / this._startDist;
          if (this._zoom = e7.getScaleZoom(o8, this._startZoom), !e7.options.bounceAtZoomLimits && (this._zoom < e7.getMinZoom() && o8 < 1 || this._zoom > e7.getMaxZoom() && 1 < o8) && (this._zoom = e7._limitZoom(this._zoom)), "center" === e7.options.touchZoom) {
            if (this._center = this._startLatLng, 1 == o8) return;
          } else {
            i7 = i7._add(n5)._divideBy(2)._subtract(this._centerPoint);
            if (1 == o8 && 0 === i7.x && 0 === i7.y) return;
            this._center = e7.unproject(e7.project(this._pinchStartLatLng, this._zoom).subtract(i7), this._zoom);
          }
          this._moved || (e7._moveStart(true, false), this._moved = true), r5(this._animRequest);
          n5 = a3(e7._move, e7, this._center, this._zoom, { pinch: true, round: false }, void 0);
          this._animRequest = x2(n5, this, true), O(t8);
        }
      }, _onTouchEnd: function() {
        this._moved && this._zooming ? (this._zooming = false, r5(this._animRequest), k2(document, "touchmove", this._onTouchMove, this), k2(document, "touchend touchcancel", this._onTouchEnd, this), this._map.options.zoomAnimation ? this._map._animateZoom(this._center, this._map._limitZoom(this._zoom), true, this._map.options.zoomSnap) : this._map._resetView(this._center, this._map._limitZoom(this._zoom))) : this._zooming = false;
      } })), Xi = (A2.addInitHook("addHandler", "touchZoom", Ot), A2.BoxZoom = _t, A2.DoubleClickZoom = Ct, A2.Drag = Zt, A2.Keyboard = St, A2.ScrollWheelZoom = Et, A2.TapHold = kt, A2.TouchZoom = Ot, t7.Bounds = f3, t7.Browser = b3, t7.CRS = ot, t7.Canvas = Fi, t7.Circle = vi, t7.CircleMarker = gi, t7.Class = et, t7.Control = B2, t7.DivIcon = Ri, t7.DivOverlay = Ai, t7.DomEvent = mt, t7.DomUtil = pt, t7.Draggable = Xe, t7.Evented = it, t7.FeatureGroup = ci, t7.GeoJSON = wi, t7.GridLayer = Ni, t7.Handler = n4, t7.Icon = di, t7.ImageOverlay = Ei, t7.LatLng = v2, t7.LatLngBounds = s4, t7.Layer = o7, t7.LayerGroup = ui, t7.LineUtil = vt, t7.Map = A2, t7.Marker = mi, t7.Mixin = ft, t7.Path = fi, t7.Point = p4, t7.PolyUtil = gt, t7.Polygon = xi, t7.Polyline = yi, t7.Popup = Bi, t7.PosAnimation = Fe, t7.Projection = wt, t7.Rectangle = Yi, t7.Renderer = Wi, t7.SVG = Gi, t7.SVGOverlay = Oi, t7.TileLayer = Di, t7.Tooltip = Ii, t7.Transformation = at, t7.Util = tt, t7.VideoOverlay = ki, t7.bind = a3, t7.bounds = _2, t7.canvas = Ui, t7.circle = function(t8, e7, i7) {
        return new vi(t8, e7, i7);
      }, t7.circleMarker = function(t8, e7) {
        return new gi(t8, e7);
      }, t7.control = Ue, t7.divIcon = function(t8) {
        return new Ri(t8);
      }, t7.extend = l4, t7.featureGroup = function(t8, e7) {
        return new ci(t8, e7);
      }, t7.geoJSON = Si, t7.geoJson = Mt, t7.gridLayer = function(t8) {
        return new Ni(t8);
      }, t7.icon = function(t8) {
        return new di(t8);
      }, t7.imageOverlay = function(t8, e7, i7) {
        return new Ei(t8, e7, i7);
      }, t7.latLng = w2, t7.latLngBounds = g2, t7.layerGroup = function(t8, e7) {
        return new ui(t8, e7);
      }, t7.map = function(t8, e7) {
        return new A2(t8, e7);
      }, t7.marker = function(t8, e7) {
        return new mi(t8, e7);
      }, t7.point = m3, t7.polygon = function(t8, e7) {
        return new xi(t8, e7);
      }, t7.polyline = function(t8, e7) {
        return new yi(t8, e7);
      }, t7.popup = function(t8, e7) {
        return new Bi(t8, e7);
      }, t7.rectangle = function(t8, e7) {
        return new Yi(t8, e7);
      }, t7.setOptions = c4, t7.stamp = h3, t7.svg = Ki, t7.svgOverlay = function(t8, e7, i7) {
        return new Oi(t8, e7, i7);
      }, t7.tileLayer = ji, t7.tooltip = function(t8, e7) {
        return new Ii(t8, e7);
      }, t7.transformation = ht, t7.version = "1.9.4", t7.videoOverlay = function(t8, e7, i7) {
        return new ki(t8, e7, i7);
      }, window.L);
      t7.noConflict = function() {
        return window.L = Xi, this;
      }, window.L = t7;
    });
  }
});

// node_modules/@lit/reactive-element/css-tag.js
/**
 * @license
 * Copyright 2019 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
var t = globalThis;
var e = t.ShadowRoot && (void 0 === t.ShadyCSS || t.ShadyCSS.nativeShadow) && "adoptedStyleSheets" in Document.prototype && "replace" in CSSStyleSheet.prototype;
var s = /* @__PURE__ */ Symbol();
var o = /* @__PURE__ */ new WeakMap();
var n = class {
  constructor(t7, e6, o7) {
    if (this._$cssResult$ = true, o7 !== s) throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");
    this.cssText = t7, this.t = e6;
  }
  get styleSheet() {
    let t7 = this.o;
    const s4 = this.t;
    if (e && void 0 === t7) {
      const e6 = void 0 !== s4 && 1 === s4.length;
      e6 && (t7 = o.get(s4)), void 0 === t7 && ((this.o = t7 = new CSSStyleSheet()).replaceSync(this.cssText), e6 && o.set(s4, t7));
    }
    return t7;
  }
  toString() {
    return this.cssText;
  }
};
var r = (t7) => new n("string" == typeof t7 ? t7 : t7 + "", void 0, s);
var i = (t7, ...e6) => {
  const o7 = 1 === t7.length ? t7[0] : e6.reduce((e7, s4, o8) => e7 + ((t8) => {
    if (true === t8._$cssResult$) return t8.cssText;
    if ("number" == typeof t8) return t8;
    throw Error("Value passed to 'css' function must be a 'css' function result: " + t8 + ". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.");
  })(s4) + t7[o8 + 1], t7[0]);
  return new n(o7, t7, s);
};
var S = (s4, o7) => {
  if (e) s4.adoptedStyleSheets = o7.map((t7) => t7 instanceof CSSStyleSheet ? t7 : t7.styleSheet);
  else for (const e6 of o7) {
    const o8 = document.createElement("style"), n4 = t.litNonce;
    void 0 !== n4 && o8.setAttribute("nonce", n4), o8.textContent = e6.cssText, s4.appendChild(o8);
  }
};
var c = e ? (t7) => t7 : (t7) => t7 instanceof CSSStyleSheet ? ((t8) => {
  let e6 = "";
  for (const s4 of t8.cssRules) e6 += s4.cssText;
  return r(e6);
})(t7) : t7;

// node_modules/@lit/reactive-element/reactive-element.js
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
var { is: i2, defineProperty: e2, getOwnPropertyDescriptor: h, getOwnPropertyNames: r2, getOwnPropertySymbols: o2, getPrototypeOf: n2 } = Object;
var a = globalThis;
var c2 = a.trustedTypes;
var l = c2 ? c2.emptyScript : "";
var p = a.reactiveElementPolyfillSupport;
var d = (t7, s4) => t7;
var u = { toAttribute(t7, s4) {
  switch (s4) {
    case Boolean:
      t7 = t7 ? l : null;
      break;
    case Object:
    case Array:
      t7 = null == t7 ? t7 : JSON.stringify(t7);
  }
  return t7;
}, fromAttribute(t7, s4) {
  let i6 = t7;
  switch (s4) {
    case Boolean:
      i6 = null !== t7;
      break;
    case Number:
      i6 = null === t7 ? null : Number(t7);
      break;
    case Object:
    case Array:
      try {
        i6 = JSON.parse(t7);
      } catch (t8) {
        i6 = null;
      }
  }
  return i6;
} };
var f = (t7, s4) => !i2(t7, s4);
var b = { attribute: true, type: String, converter: u, reflect: false, useDefault: false, hasChanged: f };
Symbol.metadata ??= /* @__PURE__ */ Symbol("metadata"), a.litPropertyMetadata ??= /* @__PURE__ */ new WeakMap();
var y = class extends HTMLElement {
  static addInitializer(t7) {
    this._$Ei(), (this.l ??= []).push(t7);
  }
  static get observedAttributes() {
    return this.finalize(), this._$Eh && [...this._$Eh.keys()];
  }
  static createProperty(t7, s4 = b) {
    if (s4.state && (s4.attribute = false), this._$Ei(), this.prototype.hasOwnProperty(t7) && ((s4 = Object.create(s4)).wrapped = true), this.elementProperties.set(t7, s4), !s4.noAccessor) {
      const i6 = /* @__PURE__ */ Symbol(), h3 = this.getPropertyDescriptor(t7, i6, s4);
      void 0 !== h3 && e2(this.prototype, t7, h3);
    }
  }
  static getPropertyDescriptor(t7, s4, i6) {
    const { get: e6, set: r5 } = h(this.prototype, t7) ?? { get() {
      return this[s4];
    }, set(t8) {
      this[s4] = t8;
    } };
    return { get: e6, set(s5) {
      const h3 = e6?.call(this);
      r5?.call(this, s5), this.requestUpdate(t7, h3, i6);
    }, configurable: true, enumerable: true };
  }
  static getPropertyOptions(t7) {
    return this.elementProperties.get(t7) ?? b;
  }
  static _$Ei() {
    if (this.hasOwnProperty(d("elementProperties"))) return;
    const t7 = n2(this);
    t7.finalize(), void 0 !== t7.l && (this.l = [...t7.l]), this.elementProperties = new Map(t7.elementProperties);
  }
  static finalize() {
    if (this.hasOwnProperty(d("finalized"))) return;
    if (this.finalized = true, this._$Ei(), this.hasOwnProperty(d("properties"))) {
      const t8 = this.properties, s4 = [...r2(t8), ...o2(t8)];
      for (const i6 of s4) this.createProperty(i6, t8[i6]);
    }
    const t7 = this[Symbol.metadata];
    if (null !== t7) {
      const s4 = litPropertyMetadata.get(t7);
      if (void 0 !== s4) for (const [t8, i6] of s4) this.elementProperties.set(t8, i6);
    }
    this._$Eh = /* @__PURE__ */ new Map();
    for (const [t8, s4] of this.elementProperties) {
      const i6 = this._$Eu(t8, s4);
      void 0 !== i6 && this._$Eh.set(i6, t8);
    }
    this.elementStyles = this.finalizeStyles(this.styles);
  }
  static finalizeStyles(s4) {
    const i6 = [];
    if (Array.isArray(s4)) {
      const e6 = new Set(s4.flat(1 / 0).reverse());
      for (const s5 of e6) i6.unshift(c(s5));
    } else void 0 !== s4 && i6.push(c(s4));
    return i6;
  }
  static _$Eu(t7, s4) {
    const i6 = s4.attribute;
    return false === i6 ? void 0 : "string" == typeof i6 ? i6 : "string" == typeof t7 ? t7.toLowerCase() : void 0;
  }
  constructor() {
    super(), this._$Ep = void 0, this.isUpdatePending = false, this.hasUpdated = false, this._$Em = null, this._$Ev();
  }
  _$Ev() {
    this._$ES = new Promise((t7) => this.enableUpdating = t7), this._$AL = /* @__PURE__ */ new Map(), this._$E_(), this.requestUpdate(), this.constructor.l?.forEach((t7) => t7(this));
  }
  addController(t7) {
    (this._$EO ??= /* @__PURE__ */ new Set()).add(t7), void 0 !== this.renderRoot && this.isConnected && t7.hostConnected?.();
  }
  removeController(t7) {
    this._$EO?.delete(t7);
  }
  _$E_() {
    const t7 = /* @__PURE__ */ new Map(), s4 = this.constructor.elementProperties;
    for (const i6 of s4.keys()) this.hasOwnProperty(i6) && (t7.set(i6, this[i6]), delete this[i6]);
    t7.size > 0 && (this._$Ep = t7);
  }
  createRenderRoot() {
    const t7 = this.shadowRoot ?? this.attachShadow(this.constructor.shadowRootOptions);
    return S(t7, this.constructor.elementStyles), t7;
  }
  connectedCallback() {
    this.renderRoot ??= this.createRenderRoot(), this.enableUpdating(true), this._$EO?.forEach((t7) => t7.hostConnected?.());
  }
  enableUpdating(t7) {
  }
  disconnectedCallback() {
    this._$EO?.forEach((t7) => t7.hostDisconnected?.());
  }
  attributeChangedCallback(t7, s4, i6) {
    this._$AK(t7, i6);
  }
  _$ET(t7, s4) {
    const i6 = this.constructor.elementProperties.get(t7), e6 = this.constructor._$Eu(t7, i6);
    if (void 0 !== e6 && true === i6.reflect) {
      const h3 = (void 0 !== i6.converter?.toAttribute ? i6.converter : u).toAttribute(s4, i6.type);
      this._$Em = t7, null == h3 ? this.removeAttribute(e6) : this.setAttribute(e6, h3), this._$Em = null;
    }
  }
  _$AK(t7, s4) {
    const i6 = this.constructor, e6 = i6._$Eh.get(t7);
    if (void 0 !== e6 && this._$Em !== e6) {
      const t8 = i6.getPropertyOptions(e6), h3 = "function" == typeof t8.converter ? { fromAttribute: t8.converter } : void 0 !== t8.converter?.fromAttribute ? t8.converter : u;
      this._$Em = e6;
      const r5 = h3.fromAttribute(s4, t8.type);
      this[e6] = r5 ?? this._$Ej?.get(e6) ?? r5, this._$Em = null;
    }
  }
  requestUpdate(t7, s4, i6, e6 = false, h3) {
    if (void 0 !== t7) {
      const r5 = this.constructor;
      if (false === e6 && (h3 = this[t7]), i6 ??= r5.getPropertyOptions(t7), !((i6.hasChanged ?? f)(h3, s4) || i6.useDefault && i6.reflect && h3 === this._$Ej?.get(t7) && !this.hasAttribute(r5._$Eu(t7, i6)))) return;
      this.C(t7, s4, i6);
    }
    false === this.isUpdatePending && (this._$ES = this._$EP());
  }
  C(t7, s4, { useDefault: i6, reflect: e6, wrapped: h3 }, r5) {
    i6 && !(this._$Ej ??= /* @__PURE__ */ new Map()).has(t7) && (this._$Ej.set(t7, r5 ?? s4 ?? this[t7]), true !== h3 || void 0 !== r5) || (this._$AL.has(t7) || (this.hasUpdated || i6 || (s4 = void 0), this._$AL.set(t7, s4)), true === e6 && this._$Em !== t7 && (this._$Eq ??= /* @__PURE__ */ new Set()).add(t7));
  }
  async _$EP() {
    this.isUpdatePending = true;
    try {
      await this._$ES;
    } catch (t8) {
      Promise.reject(t8);
    }
    const t7 = this.scheduleUpdate();
    return null != t7 && await t7, !this.isUpdatePending;
  }
  scheduleUpdate() {
    return this.performUpdate();
  }
  performUpdate() {
    if (!this.isUpdatePending) return;
    if (!this.hasUpdated) {
      if (this.renderRoot ??= this.createRenderRoot(), this._$Ep) {
        for (const [t9, s5] of this._$Ep) this[t9] = s5;
        this._$Ep = void 0;
      }
      const t8 = this.constructor.elementProperties;
      if (t8.size > 0) for (const [s5, i6] of t8) {
        const { wrapped: t9 } = i6, e6 = this[s5];
        true !== t9 || this._$AL.has(s5) || void 0 === e6 || this.C(s5, void 0, i6, e6);
      }
    }
    let t7 = false;
    const s4 = this._$AL;
    try {
      t7 = this.shouldUpdate(s4), t7 ? (this.willUpdate(s4), this._$EO?.forEach((t8) => t8.hostUpdate?.()), this.update(s4)) : this._$EM();
    } catch (s5) {
      throw t7 = false, this._$EM(), s5;
    }
    t7 && this._$AE(s4);
  }
  willUpdate(t7) {
  }
  _$AE(t7) {
    this._$EO?.forEach((t8) => t8.hostUpdated?.()), this.hasUpdated || (this.hasUpdated = true, this.firstUpdated(t7)), this.updated(t7);
  }
  _$EM() {
    this._$AL = /* @__PURE__ */ new Map(), this.isUpdatePending = false;
  }
  get updateComplete() {
    return this.getUpdateComplete();
  }
  getUpdateComplete() {
    return this._$ES;
  }
  shouldUpdate(t7) {
    return true;
  }
  update(t7) {
    this._$Eq &&= this._$Eq.forEach((t8) => this._$ET(t8, this[t8])), this._$EM();
  }
  updated(t7) {
  }
  firstUpdated(t7) {
  }
};
y.elementStyles = [], y.shadowRootOptions = { mode: "open" }, y[d("elementProperties")] = /* @__PURE__ */ new Map(), y[d("finalized")] = /* @__PURE__ */ new Map(), p?.({ ReactiveElement: y }), (a.reactiveElementVersions ??= []).push("2.1.2");

// node_modules/lit-html/lit-html.js
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
var t2 = globalThis;
var i3 = (t7) => t7;
var s2 = t2.trustedTypes;
var e3 = s2 ? s2.createPolicy("lit-html", { createHTML: (t7) => t7 }) : void 0;
var h2 = "$lit$";
var o3 = `lit$${Math.random().toFixed(9).slice(2)}$`;
var n3 = "?" + o3;
var r3 = `<${n3}>`;
var l2 = document;
var c3 = () => l2.createComment("");
var a2 = (t7) => null === t7 || "object" != typeof t7 && "function" != typeof t7;
var u2 = Array.isArray;
var d2 = (t7) => u2(t7) || "function" == typeof t7?.[Symbol.iterator];
var f2 = "[ 	\n\f\r]";
var v = /<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g;
var _ = /-->/g;
var m = />/g;
var p2 = RegExp(`>|${f2}(?:([^\\s"'>=/]+)(${f2}*=${f2}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`, "g");
var g = /'/g;
var $ = /"/g;
var y2 = /^(?:script|style|textarea|title)$/i;
var x = (t7) => (i6, ...s4) => ({ _$litType$: t7, strings: i6, values: s4 });
var b2 = x(1);
var w = x(2);
var T = x(3);
var E = /* @__PURE__ */ Symbol.for("lit-noChange");
var A = /* @__PURE__ */ Symbol.for("lit-nothing");
var C = /* @__PURE__ */ new WeakMap();
var P = l2.createTreeWalker(l2, 129);
function V(t7, i6) {
  if (!u2(t7) || !t7.hasOwnProperty("raw")) throw Error("invalid template strings array");
  return void 0 !== e3 ? e3.createHTML(i6) : i6;
}
var N = (t7, i6) => {
  const s4 = t7.length - 1, e6 = [];
  let n4, l4 = 2 === i6 ? "<svg>" : 3 === i6 ? "<math>" : "", c4 = v;
  for (let i7 = 0; i7 < s4; i7++) {
    const s5 = t7[i7];
    let a3, u3, d3 = -1, f3 = 0;
    for (; f3 < s5.length && (c4.lastIndex = f3, u3 = c4.exec(s5), null !== u3); ) f3 = c4.lastIndex, c4 === v ? "!--" === u3[1] ? c4 = _ : void 0 !== u3[1] ? c4 = m : void 0 !== u3[2] ? (y2.test(u3[2]) && (n4 = RegExp("</" + u3[2], "g")), c4 = p2) : void 0 !== u3[3] && (c4 = p2) : c4 === p2 ? ">" === u3[0] ? (c4 = n4 ?? v, d3 = -1) : void 0 === u3[1] ? d3 = -2 : (d3 = c4.lastIndex - u3[2].length, a3 = u3[1], c4 = void 0 === u3[3] ? p2 : '"' === u3[3] ? $ : g) : c4 === $ || c4 === g ? c4 = p2 : c4 === _ || c4 === m ? c4 = v : (c4 = p2, n4 = void 0);
    const x2 = c4 === p2 && t7[i7 + 1].startsWith("/>") ? " " : "";
    l4 += c4 === v ? s5 + r3 : d3 >= 0 ? (e6.push(a3), s5.slice(0, d3) + h2 + s5.slice(d3) + o3 + x2) : s5 + o3 + (-2 === d3 ? i7 : x2);
  }
  return [V(t7, l4 + (t7[s4] || "<?>") + (2 === i6 ? "</svg>" : 3 === i6 ? "</math>" : "")), e6];
};
var S2 = class _S {
  constructor({ strings: t7, _$litType$: i6 }, e6) {
    let r5;
    this.parts = [];
    let l4 = 0, a3 = 0;
    const u3 = t7.length - 1, d3 = this.parts, [f3, v2] = N(t7, i6);
    if (this.el = _S.createElement(f3, e6), P.currentNode = this.el.content, 2 === i6 || 3 === i6) {
      const t8 = this.el.content.firstChild;
      t8.replaceWith(...t8.childNodes);
    }
    for (; null !== (r5 = P.nextNode()) && d3.length < u3; ) {
      if (1 === r5.nodeType) {
        if (r5.hasAttributes()) for (const t8 of r5.getAttributeNames()) if (t8.endsWith(h2)) {
          const i7 = v2[a3++], s4 = r5.getAttribute(t8).split(o3), e7 = /([.?@])?(.*)/.exec(i7);
          d3.push({ type: 1, index: l4, name: e7[2], strings: s4, ctor: "." === e7[1] ? I : "?" === e7[1] ? L2 : "@" === e7[1] ? z : H }), r5.removeAttribute(t8);
        } else t8.startsWith(o3) && (d3.push({ type: 6, index: l4 }), r5.removeAttribute(t8));
        if (y2.test(r5.tagName)) {
          const t8 = r5.textContent.split(o3), i7 = t8.length - 1;
          if (i7 > 0) {
            r5.textContent = s2 ? s2.emptyScript : "";
            for (let s4 = 0; s4 < i7; s4++) r5.append(t8[s4], c3()), P.nextNode(), d3.push({ type: 2, index: ++l4 });
            r5.append(t8[i7], c3());
          }
        }
      } else if (8 === r5.nodeType) if (r5.data === n3) d3.push({ type: 2, index: l4 });
      else {
        let t8 = -1;
        for (; -1 !== (t8 = r5.data.indexOf(o3, t8 + 1)); ) d3.push({ type: 7, index: l4 }), t8 += o3.length - 1;
      }
      l4++;
    }
  }
  static createElement(t7, i6) {
    const s4 = l2.createElement("template");
    return s4.innerHTML = t7, s4;
  }
};
function M(t7, i6, s4 = t7, e6) {
  if (i6 === E) return i6;
  let h3 = void 0 !== e6 ? s4._$Co?.[e6] : s4._$Cl;
  const o7 = a2(i6) ? void 0 : i6._$litDirective$;
  return h3?.constructor !== o7 && (h3?._$AO?.(false), void 0 === o7 ? h3 = void 0 : (h3 = new o7(t7), h3._$AT(t7, s4, e6)), void 0 !== e6 ? (s4._$Co ??= [])[e6] = h3 : s4._$Cl = h3), void 0 !== h3 && (i6 = M(t7, h3._$AS(t7, i6.values), h3, e6)), i6;
}
var R = class {
  constructor(t7, i6) {
    this._$AV = [], this._$AN = void 0, this._$AD = t7, this._$AM = i6;
  }
  get parentNode() {
    return this._$AM.parentNode;
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  u(t7) {
    const { el: { content: i6 }, parts: s4 } = this._$AD, e6 = (t7?.creationScope ?? l2).importNode(i6, true);
    P.currentNode = e6;
    let h3 = P.nextNode(), o7 = 0, n4 = 0, r5 = s4[0];
    for (; void 0 !== r5; ) {
      if (o7 === r5.index) {
        let i7;
        2 === r5.type ? i7 = new k(h3, h3.nextSibling, this, t7) : 1 === r5.type ? i7 = new r5.ctor(h3, r5.name, r5.strings, this, t7) : 6 === r5.type && (i7 = new Z(h3, this, t7)), this._$AV.push(i7), r5 = s4[++n4];
      }
      o7 !== r5?.index && (h3 = P.nextNode(), o7++);
    }
    return P.currentNode = l2, e6;
  }
  p(t7) {
    let i6 = 0;
    for (const s4 of this._$AV) void 0 !== s4 && (void 0 !== s4.strings ? (s4._$AI(t7, s4, i6), i6 += s4.strings.length - 2) : s4._$AI(t7[i6])), i6++;
  }
};
var k = class _k {
  get _$AU() {
    return this._$AM?._$AU ?? this._$Cv;
  }
  constructor(t7, i6, s4, e6) {
    this.type = 2, this._$AH = A, this._$AN = void 0, this._$AA = t7, this._$AB = i6, this._$AM = s4, this.options = e6, this._$Cv = e6?.isConnected ?? true;
  }
  get parentNode() {
    let t7 = this._$AA.parentNode;
    const i6 = this._$AM;
    return void 0 !== i6 && 11 === t7?.nodeType && (t7 = i6.parentNode), t7;
  }
  get startNode() {
    return this._$AA;
  }
  get endNode() {
    return this._$AB;
  }
  _$AI(t7, i6 = this) {
    t7 = M(this, t7, i6), a2(t7) ? t7 === A || null == t7 || "" === t7 ? (this._$AH !== A && this._$AR(), this._$AH = A) : t7 !== this._$AH && t7 !== E && this._(t7) : void 0 !== t7._$litType$ ? this.$(t7) : void 0 !== t7.nodeType ? this.T(t7) : d2(t7) ? this.k(t7) : this._(t7);
  }
  O(t7) {
    return this._$AA.parentNode.insertBefore(t7, this._$AB);
  }
  T(t7) {
    this._$AH !== t7 && (this._$AR(), this._$AH = this.O(t7));
  }
  _(t7) {
    this._$AH !== A && a2(this._$AH) ? this._$AA.nextSibling.data = t7 : this.T(l2.createTextNode(t7)), this._$AH = t7;
  }
  $(t7) {
    const { values: i6, _$litType$: s4 } = t7, e6 = "number" == typeof s4 ? this._$AC(t7) : (void 0 === s4.el && (s4.el = S2.createElement(V(s4.h, s4.h[0]), this.options)), s4);
    if (this._$AH?._$AD === e6) this._$AH.p(i6);
    else {
      const t8 = new R(e6, this), s5 = t8.u(this.options);
      t8.p(i6), this.T(s5), this._$AH = t8;
    }
  }
  _$AC(t7) {
    let i6 = C.get(t7.strings);
    return void 0 === i6 && C.set(t7.strings, i6 = new S2(t7)), i6;
  }
  k(t7) {
    u2(this._$AH) || (this._$AH = [], this._$AR());
    const i6 = this._$AH;
    let s4, e6 = 0;
    for (const h3 of t7) e6 === i6.length ? i6.push(s4 = new _k(this.O(c3()), this.O(c3()), this, this.options)) : s4 = i6[e6], s4._$AI(h3), e6++;
    e6 < i6.length && (this._$AR(s4 && s4._$AB.nextSibling, e6), i6.length = e6);
  }
  _$AR(t7 = this._$AA.nextSibling, s4) {
    for (this._$AP?.(false, true, s4); t7 !== this._$AB; ) {
      const s5 = i3(t7).nextSibling;
      i3(t7).remove(), t7 = s5;
    }
  }
  setConnected(t7) {
    void 0 === this._$AM && (this._$Cv = t7, this._$AP?.(t7));
  }
};
var H = class {
  get tagName() {
    return this.element.tagName;
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  constructor(t7, i6, s4, e6, h3) {
    this.type = 1, this._$AH = A, this._$AN = void 0, this.element = t7, this.name = i6, this._$AM = e6, this.options = h3, s4.length > 2 || "" !== s4[0] || "" !== s4[1] ? (this._$AH = Array(s4.length - 1).fill(new String()), this.strings = s4) : this._$AH = A;
  }
  _$AI(t7, i6 = this, s4, e6) {
    const h3 = this.strings;
    let o7 = false;
    if (void 0 === h3) t7 = M(this, t7, i6, 0), o7 = !a2(t7) || t7 !== this._$AH && t7 !== E, o7 && (this._$AH = t7);
    else {
      const e7 = t7;
      let n4, r5;
      for (t7 = h3[0], n4 = 0; n4 < h3.length - 1; n4++) r5 = M(this, e7[s4 + n4], i6, n4), r5 === E && (r5 = this._$AH[n4]), o7 ||= !a2(r5) || r5 !== this._$AH[n4], r5 === A ? t7 = A : t7 !== A && (t7 += (r5 ?? "") + h3[n4 + 1]), this._$AH[n4] = r5;
    }
    o7 && !e6 && this.j(t7);
  }
  j(t7) {
    t7 === A ? this.element.removeAttribute(this.name) : this.element.setAttribute(this.name, t7 ?? "");
  }
};
var I = class extends H {
  constructor() {
    super(...arguments), this.type = 3;
  }
  j(t7) {
    this.element[this.name] = t7 === A ? void 0 : t7;
  }
};
var L2 = class extends H {
  constructor() {
    super(...arguments), this.type = 4;
  }
  j(t7) {
    this.element.toggleAttribute(this.name, !!t7 && t7 !== A);
  }
};
var z = class extends H {
  constructor(t7, i6, s4, e6, h3) {
    super(t7, i6, s4, e6, h3), this.type = 5;
  }
  _$AI(t7, i6 = this) {
    if ((t7 = M(this, t7, i6, 0) ?? A) === E) return;
    const s4 = this._$AH, e6 = t7 === A && s4 !== A || t7.capture !== s4.capture || t7.once !== s4.once || t7.passive !== s4.passive, h3 = t7 !== A && (s4 === A || e6);
    e6 && this.element.removeEventListener(this.name, this, s4), h3 && this.element.addEventListener(this.name, this, t7), this._$AH = t7;
  }
  handleEvent(t7) {
    "function" == typeof this._$AH ? this._$AH.call(this.options?.host ?? this.element, t7) : this._$AH.handleEvent(t7);
  }
};
var Z = class {
  constructor(t7, i6, s4) {
    this.element = t7, this.type = 6, this._$AN = void 0, this._$AM = i6, this.options = s4;
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  _$AI(t7) {
    M(this, t7);
  }
};
var j = { M: h2, P: o3, A: n3, C: 1, L: N, R, D: d2, V: M, I: k, H, N: L2, U: z, B: I, F: Z };
var B = t2.litHtmlPolyfillSupport;
B?.(S2, k), (t2.litHtmlVersions ??= []).push("3.3.3");
var D = (t7, i6, s4) => {
  const e6 = s4?.renderBefore ?? i6;
  let h3 = e6._$litPart$;
  if (void 0 === h3) {
    const t8 = s4?.renderBefore ?? null;
    e6._$litPart$ = h3 = new k(i6.insertBefore(c3(), t8), t8, void 0, s4 ?? {});
  }
  return h3._$AI(t7), h3;
};

// node_modules/lit-element/lit-element.js
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
var s3 = globalThis;
var i4 = class extends y {
  constructor() {
    super(...arguments), this.renderOptions = { host: this }, this._$Do = void 0;
  }
  createRenderRoot() {
    const t7 = super.createRenderRoot();
    return this.renderOptions.renderBefore ??= t7.firstChild, t7;
  }
  update(t7) {
    const r5 = this.render();
    this.hasUpdated || (this.renderOptions.isConnected = this.isConnected), super.update(t7), this._$Do = D(r5, this.renderRoot, this.renderOptions);
  }
  connectedCallback() {
    super.connectedCallback(), this._$Do?.setConnected(true);
  }
  disconnectedCallback() {
    super.disconnectedCallback(), this._$Do?.setConnected(false);
  }
  render() {
    return E;
  }
};
i4._$litElement$ = true, i4["finalized"] = true, s3.litElementHydrateSupport?.({ LitElement: i4 });
var o4 = s3.litElementPolyfillSupport;
o4?.({ LitElement: i4 });
(s3.litElementVersions ??= []).push("4.2.2");

// node_modules/lit-html/is-server.js
/**
 * @license
 * Copyright 2022 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */

// src/stil.js
var GLAS = `
:host { display: block; height: 100%; }
.menue-knopf { position: absolute; top: 10px; left: 14px; z-index: 6; width: 36px; height: 36px; border-radius: 50% !important; display: grid; place-items: center; font-size: 17px; color: var(--ink2); }
.fehler-band { padding: 10px 16px; border-color: var(--rot); color: var(--ink); font-size: 13px; }
.laden { opacity: .6; transition: opacity .2s; }
.leer { padding: 18px 0; text-align: center; color: var(--ink2); font-size: 13px; }
.knopf { padding: 7px 14px; border-radius: 12px; background: rgba(127,127,127,.2); font-size: 13px; }
.knopf.haupt { background: color-mix(in srgb, var(--blau) 30%, transparent); color: var(--ink); font-weight: 600; }
.knopf[disabled] { opacity: .45; cursor: not-allowed; }
.fein { color: var(--rot); font-size: 12px; }
/* ── ab hier: Glas-Stil wie ha-baustelle (frontend/src/alt.js, GLAS_CSS) ── */
.wurzel { position: relative; height: 100vh; height: 100dvh; font-family: -apple-system, "SF Pro Text", system-ui, "Segoe UI", Roboto, sans-serif; background: #0b0b0b; color: #fff; font-size: 14px; }
.wurzel.hell { background: #d9dee5; color: #111; }
.ui { position: absolute; inset: 0; }
.app { --s1: #3987e5; --s2: #d95926; --s3: #199e70; --s4: #c98500; --s5: #d55181; --s6: #008300;
  --ink: #fff; --ink2: rgba(255,255,255,.66); --gridc: rgba(255,255,255,.14); --axisc: rgba(255,255,255,.55); --amber: #ff9f0a; --rot: #ff6961; --blau: #64a8ff;
  --panel: rgba(255,255,255,.05); --panel-rand: rgba(255,255,255,.2); --sheet: rgba(28,32,44,.82);
  position: relative; height: 100%; overflow: hidden; color: var(--ink); container-type: inline-size; }
.hell .app { --s1: #2a78d6; --s2: #eb6834; --s3: #1baf7a; --s4: #eda100; --s5: #e87ba4; --s6: #008300;
  --ink: #111; --ink2: rgba(0,0,0,.6); --gridc: rgba(0,0,0,.1); --axisc: rgba(0,0,0,.5); --amber: #d97800; --rot: #d7372b; --blau: #0a64d6;
  --panel: rgba(255,255,255,.2); --panel-rand: rgba(255,255,255,.65); --sheet: rgba(250,250,252,.86); }
:where(.app button) { font: inherit; color: inherit; background: none; border: 0; padding: 0; cursor: pointer; text-align: inherit; }
.app input, .app select { font: inherit; color: var(--ink); background: rgba(127,127,127,.16); border: 1px solid var(--panel-rand); border-radius: 10px; padding: 7px 10px; }
.app select option { color: #111; }
.glas-bg { position: absolute; inset: 0; overflow: hidden; background: linear-gradient(165deg, var(--g1) 0%, var(--g2) 50%, var(--g3) 100%); }
.glas-bg[data-phase=morgen] { --g1: #2e2748; --g2: #4a3150; --g3: #6b4040; --f1: #ff8a5c; --f2: #6a7bd6; --f3: #d07ab8; }
.glas-bg[data-phase=tag]    { --g1: #1c3552; --g2: #1f4a70; --g3: #2a5575; --f1: #ffc766; --f2: #3aa0ff; --f3: #7fd0ff; }
.glas-bg[data-phase=abend]  { --g1: #2a1a36; --g2: #45203d; --g3: #5a2a2c; --f1: #ff7a2e; --f2: #d0457a; --f3: #7a4bd0; }
.glas-bg[data-phase=nacht]  { --g1: #070d1c; --g2: #0c1528; --g3: #131a33; --f1: #2c3e8a; --f2: #1b4a7a; --f3: #4b3a8a; }
.hell .glas-bg[data-phase=morgen] { --g1: #ffd9c7; --g2: #f5e0f0; --g3: #cfdcff; --f1: #ff9a6a; --f2: #9fb4ff; --f3: #f0a0c8; }
.hell .glas-bg[data-phase=tag]    { --g1: #cfe6ff; --g2: #e3f1ff; --g3: #fff3d6; --f1: #ffd060; --f2: #6ab8ff; --f3: #a8e0ff; }
.hell .glas-bg[data-phase=abend]  { --g1: #ffd2b0; --g2: #f7c6d8; --g3: #d9ccff; --f1: #ff8a3a; --f2: #ff6f9a; --f3: #a58aff; }
.hell .glas-bg[data-phase=nacht]  { --g1: #b9c4e0; --g2: #c9cde6; --g3: #d8d0ec; --f1: #6d80c8; --f2: #7fa3dc; --f3: #9a88d2; }
.glas-bg > i { position: absolute; border-radius: 50%; filter: blur(40px) saturate(1); opacity: .7; animation: schweben 14s ease-in-out infinite; }
.glas-bg .k1 { width: 260px; height: 260px; background: var(--f1); top: -60px; left: -60px; }
.glas-bg .k2 { width: 240px; height: 240px; background: var(--f2); top: 300px; right: -80px; animation-delay: -5s; }
.glas-bg .k3 { width: 200px; height: 200px; background: var(--f3); bottom: -40px; left: 40px; animation-delay: -9s; }
.glas-bg[data-phase=nacht] > i { opacity: .45; }
.scroll { position: absolute; inset: 0; overflow-y: auto; }
.seite { padding: 56px 14px 120px; display: flex; flex-direction: column; gap: 12px; max-width: 1100px; margin: 0 auto; animation: seite .28s cubic-bezier(.2,.7,.2,1) backwards; }
.glas-panel { background: var(--panel); border: 1px solid var(--panel-rand); backdrop-filter: blur(12px) saturate(1.4); -webkit-backdrop-filter: blur(12px) saturate(1.4);
  border-radius: 24px; box-shadow: 0 8px 32px rgba(0,0,0,.22), inset 0 1px 0 rgba(255,255,255,.22); }
.glas-kopf { display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 16px 18px; flex-wrap: wrap; }
.glas-klein { font-size: 11px; letter-spacing: 1.2px; color: var(--ink2); text-transform: uppercase; }
.glas-kw { font-size: 38px; font-weight: 300; letter-spacing: -.5px; display: flex; align-items: baseline; gap: 4px; white-space: nowrap; line-height: 1; }
.glas-kw small, .glas-wert small { font-size: .5em; opacity: .7; }
.chip { display: inline-flex; align-items: center; gap: 5px; font-size: 13px; padding: 6px 12px; border-radius: 18px !important; transition: transform .15s; }
.chip:active { transform: scale(.96); } .chip.rot { color: var(--rot); } .chip.amber { color: var(--amber); }
.glas-raster { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.glas-k { padding: 12px; display: flex; flex-direction: column; gap: 3px; animation: rein .5s ease-out backwards;  /* FE-0003: kein Dauer-Schweben mehr, nur Einblenden */ transition: transform .2s cubic-bezier(.2,.7,.2,1), box-shadow .2s; }
.glas-k:hover { box-shadow: 0 14px 40px rgba(0,0,0,.3), inset 0 1px 0 rgba(255,255,255,.3); } .glas-k:active { transform: scale(.97); }
.glas-wert { font-size: 26px; font-weight: 300; } .glas-kwk { font-size: 12px; color: var(--ink2); }
.glas-nav { position: absolute; left: 14px; right: 14px; bottom: 22px; display: flex; justify-content: space-around; padding: 6px; z-index: 5; }
.glas-nav button { flex: 1; text-align: center; padding: 8px 2px; border-radius: 16px; font-size: 13px; color: var(--ink2); transition: background .2s, color .2s; }
.glas-nav button.on { color: var(--ink); font-weight: 700; background: rgba(255,255,255,.16); }
.hell .glas-nav button.on { background: rgba(255,255,255,.7); }
.glas-nav.sechs button { font-size: 12px; padding-left: 1px; padding-right: 1px; }
.block { padding: 14px 16px; display: flex; flex-direction: column; gap: 8px; }
.block-kopf { display: flex; justify-content: space-between; align-items: baseline; gap: 10px; flex-wrap: wrap; }
.block-kopf h3 { margin: 0; font-size: 16px; font-weight: 600; }
.leise { color: var(--ink2); font-size: 12px; } .rot-t { color: var(--rot); } .blau { color: var(--blau); } .ok { color: #30d158; }
.zeile { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 10px 16px; width: 100%; box-sizing: border-box; min-height: 44px; }
.block .zeile { padding: 8px 0; }
.block .zeile + .zeile { border-top: 1px solid var(--gridc); }
/* AN-0006: Gruppenüberschriften deutlich (Variante B): fett, Farbstrich links, Trennlinie */
.gruppe { display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 700; letter-spacing: .2px; color: var(--ink); padding: 18px 0 6px; border-bottom: 1px solid var(--gridc); margin-bottom: 2px; }
.gruppe::before { content: ''; width: 4px; height: 16px; border-radius: 2px; background: var(--blau); flex: none; }
.gruppe .gr-ic { font-size: 15px; }
.g-ic { width: 32px; height: 32px; border-radius: 10px; display: grid; place-items: center; background: rgba(142,142,147,.22); flex: none; }
.seg { display: flex; padding: 3px; border-radius: 14px; background: rgba(120,120,128,.2); gap: 2px; }
.seg button { flex: 1; text-align: center; padding: 7px 6px; border-radius: 11px; font-size: 13px; color: var(--ink2); transition: background .2s, color .2s; white-space: nowrap; }
.seg button.on { background: rgba(255,255,255,.2); color: var(--ink); font-weight: 600; box-shadow: 0 2px 8px rgba(0,0,0,.15); }
.hell .seg button.on { background: #fff; }
.seg.klein button { padding: 5px 10px; font-size: 12px; flex: none; }
.badge { font-size: 11px; padding: 2px 8px; border-radius: 10px; background: rgba(142,142,147,.25); color: var(--ink2); white-space: nowrap; }
.badge.gruen { background: rgba(48,209,88,.22); color: #30d158; }
.badge.rot-b { background: rgba(255,69,58,.2); color: var(--rot); }
.badge.amber-b { background: color-mix(in srgb, var(--amber) 22%, transparent); color: var(--amber); }
.badge.blau-b { background: color-mix(in srgb, var(--blau) 22%, transparent); color: var(--blau); }
.schleier { position: absolute; inset: 0; background: rgba(0,0,0,.35); opacity: 0; pointer-events: none; transition: opacity .25s; z-index: 20; }
.schleier.an { opacity: 1; pointer-events: auto; }
.sheet { position: absolute; left: 8px; right: 8px; bottom: 8px; max-height: 82%; overflow-y: auto; z-index: 21; padding: 8px 18px 18px; background: var(--sheet);
  transform: translateY(110%); transition: transform .32s cubic-bezier(.2,.8,.2,1); border-radius: 28px; display: flex; flex-direction: column; gap: 10px; }
.sheet.an { transform: none; } .sheet > * { flex-shrink: 0; }
.sheet h3 { margin: 4px 0 0; font-size: 20px; }
.griff { width: 40px; height: 5px; border-radius: 3px; background: var(--ink2); opacity: .5; margin: 0 auto 4px; }
.sheet .zeile { padding: 8px 0; } .sheet .zeile + .zeile { border-top: 1px solid var(--gridc); }
.zu { position: absolute; top: 14px; right: 16px; font-size: 18px; color: var(--ink2); }
@keyframes schweben { 50% { transform: translate(30px, 40px) scale(1.15); } }
@keyframes seite { from { opacity: 0; transform: translateY(10px); } }
@keyframes rein { from { opacity: 0; transform: translateY(8px); } }
@media (prefers-reduced-motion: reduce) { .glas-k, .glas-bg > i, .seite, .strecke .fluss { animation: none !important; } }
@container (min-width: 700px) {
  .seite { padding: 84px 28px 40px; }
  .glas-nav { top: 16px; bottom: auto; left: 50%; right: auto; transform: translateX(-50%); width: 620px; }
  .glas-raster { grid-template-columns: repeat(auto-fill, minmax(170px, 1fr)); }
  .sheet { left: 50%; right: auto; width: 520px; bottom: auto; top: 50%; transform: translate(-50%, -40%) scale(.96); opacity: 0; pointer-events: none;
    transition: transform .25s cubic-bezier(.2,.8,.2,1), opacity .2s; }
  .sheet.an { transform: translate(-50%, -50%); opacity: 1; pointer-events: auto; }
  .griff { display: none; }
  .raster2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; align-items: start; }
}

/* ── eigene Bausteine der Heimnetz-Seite, nur mit den Variablen oben ── */
.raster2 > * + * { margin-top: 0; } .raster2 > * { min-width: 0; } .raster2 { display: grid; gap: 12px; }
.punkt { width: 9px; height: 9px; border-radius: 50%; flex: none; display: inline-block; background: #30d158; }
.punkt.amber { background: var(--amber); } .punkt.rot { background: var(--rot); } .punkt.grau { background: var(--ink2); opacity: .5; }
.kopf-titel { display: flex; align-items: center; gap: 10px; } .kopf-titel .punkt { width: 14px; height: 14px; box-shadow: 0 0 12px currentColor; }
.chips { display: flex; gap: 8px; flex-wrap: wrap; }
.befund { display: flex; gap: 10px; align-items: flex-start; padding: 10px 0; } .befund + .befund { border-top: 1px solid var(--gridc); }
.befund .punkt { margin-top: 5px; } .befund b { display: block; margin-bottom: 2px; } .befund p { margin: 0; color: var(--ink2); font-size: 13px; line-height: 1.45; }
.ereig { display: grid; grid-template-columns: 12px 92px 1fr; gap: 10px; align-items: baseline; padding: 7px 0; font-size: 13px; }
.ereig + .ereig { border-top: 1px solid var(--gridc); } .ereig .punkt { align-self: center; } .ereig time { color: var(--ink2); font-variant-numeric: tabular-nums; }
.leiste { display: flex; flex-wrap: wrap; gap: 8px 12px; align-items: center; }
.leiste .seg { flex: none; }
.wr { display: grid; grid-template-columns: 26px repeat(24, minmax(0, 1fr)); gap: 2px; font-size: 10px; color: var(--ink2); }
.wr i { aspect-ratio: 1.3; border-radius: 3px; display: block; cursor: default; }
.wr i.ohne { background: rgba(127,127,127,.12); }
.sig { display: inline-block; width: 70px; height: 8px; border-radius: 4px; background: rgba(127,127,127,.18); overflow: hidden; vertical-align: middle; }
.sig i { display: block; height: 100%; border-radius: 4px; }
.t tr.klick { cursor: pointer; }
.wr span { text-align: center; } .wr span.tag { text-align: left; align-self: center; }
/* WU-0004: Wochentag antippbar, Median-Zahl in der Kachel nur auf breitem Schirm, Tagesverlauf */
.wr button.tag { text-align: left; align-self: center; color: var(--blau); font-size: inherit; }
.wr button.tag.on { color: var(--ink); font-weight: 700; }
.wr i b { display: none; }
@container (min-width: 760px) { .wr i b { display: grid; place-items: center; height: 100%; font-size: 9.5px; font-weight: 600; font-style: normal; color: rgba(0,0,0,.72); font-variant-numeric: tabular-nums; } }
.tv { display: flex; flex-direction: column; gap: 8px; }
.tv svg { width: 100%; height: auto; display: block; touch-action: manipulation; }
/* Textfarbe statt Akzentblau: der Glas-Hintergrund ist oft selbst blau (WU-0004, Herbert 23.10.2026) */
.tv .band { fill: var(--ink); opacity: .26; } .tv .med { fill: none; stroke: var(--ink); stroke-width: 2.6; stroke-linejoin: round; }
.tv .med.luecke { stroke-width: 1.4; stroke-dasharray: 3 4; opacity: .55; } .tv .pkt { fill: var(--ink); }
.tv .glatt { fill: none; stroke: var(--amber); stroke-width: 2.6; stroke-linejoin: round; stroke-linecap: round; }
.tv .tarif { stroke: var(--ink2); stroke-dasharray: 4 4; stroke-width: 1; }
.tv .gitter { stroke: var(--gridc); stroke-width: 1; } .tv text { fill: var(--ink2); font-size: 11px; }
.tv .wahl { fill: rgba(127,127,127,.16); } .tv rect.h { fill: transparent; cursor: pointer; }
.tv .info { font-size: 13px; min-height: 20px; } .tv .info b { font-weight: 600; }
/* AN-0005: Popup zur Stundenkachel */
.wr i.kachel { cursor: pointer; } .wr i.wahl { outline: 2px solid var(--ink); outline-offset: 1px; }
.kpop { position: absolute; z-index: 15; width: 400px; max-width: calc(100% - 16px); box-sizing: border-box; padding: 10px 12px 8px;
  background: var(--sheet); border-radius: 16px; font-size: 12px; pointer-events: none; left: 8px; top: 8px; }
.kpop.fest { pointer-events: auto; }
.kpop .kp-kopf { display: flex; justify-content: space-between; align-items: baseline; gap: 8px; } .kpop .kp-kopf b { font-size: 13px; }
.kpop .kp-werte { color: var(--ink2); margin: 3px 0 6px; line-height: 1.4; } .kpop .kp-werte b { color: var(--ink); font-weight: 600; }
.kpop table.t { font-size: 12px; } .kpop .t td { padding: 4px 6px 4px 0; } .kpop .t th { padding: 2px 6px 4px 0; }
.kpop .kp-liste { max-height: 220px; overflow-y: auto; } .kpop .zu-k { font-size: 14px; padding: 0 2px; color: var(--ink2); }
.legende i.l-med { background: var(--ink); height: 3px; } .legende i.l-glatt { background: var(--amber); height: 3px; } .legende i.l-band { background: var(--ink); opacity: .3; }
.legende i.l-luecke { background: none; border-top: 1px dashed var(--ink); height: 0; } .legende i.l-tarif { background: none; border-top: 1px dashed var(--ink2); height: 0; }
.skala { display: flex; align-items: center; gap: 6px; font-size: 11px; color: var(--ink2); }
.skala i { width: 120px; height: 8px; border-radius: 4px; background: linear-gradient(90deg, var(--rot), var(--amber), var(--s3)); }
table.t { width: 100%; border-collapse: collapse; font-size: 13px; } .t th { text-align: left; font-weight: 500; color: var(--ink2); font-size: 11px; padding: 6px 8px 6px 0; }
.t td { padding: 7px 8px 7px 0; border-top: 1px solid var(--gridc); font-variant-numeric: tabular-nums; white-space: nowrap; } .t td.r, .t th.r { text-align: right; }
.t tr.belastet td { color: var(--ink2); }
.tab-scroll { overflow-x: auto; }
.streifen { display: flex; height: 14px; border-radius: 5px; overflow: hidden; background: rgba(127,127,127,.12); flex: 1; min-width: 120px; }
.streifen i { display: block; height: 100%; } .streifen i.an { background: var(--s3); } .streifen i.aus { background: transparent; } .streifen i.luecke { background: repeating-linear-gradient(45deg, transparent 0 3px, var(--gridc) 3px 6px); }
.geraet { display: grid; grid-template-columns: 32px minmax(0, 1.2fr) minmax(120px, 2fr) auto; gap: 12px; align-items: center; padding: 9px 0; cursor: pointer; }
.geraet + .geraet { border-top: 1px solid var(--gridc); } .geraet .n { display: flex; flex-direction: column; min-width: 0; } .geraet .n b { font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.achse { display: flex; justify-content: space-between; font-size: 10px; color: var(--ink2); }
.pegel { display: flex; flex-direction: column; gap: 4px; } .pegel-bahn { position: relative; height: 10px; border-radius: 5px; background: linear-gradient(90deg, var(--rot) 0 30%, var(--amber) 30% 55%, var(--s3) 55%); opacity: .85; }
.pegel-bahn b { position: absolute; top: -4px; width: 4px; height: 18px; border-radius: 2px; background: var(--ink); box-shadow: 0 0 0 2px rgba(0,0,0,.35); transform: translateX(-2px); }
.mw { display: flex; justify-content: space-between; align-items: baseline; gap: 8px; } .mw .glas-wert { font-size: 22px; }
svg.dia { width: 100%; height: auto; display: block; overflow: visible; } .dia text { fill: var(--axisc); font-size: 10px; } .dia .gitter { stroke: var(--gridc); }
.legende { display: flex; gap: 14px; flex-wrap: wrap; font-size: 12px; color: var(--ink2); } .legende i { display: inline-block; width: 10px; height: 10px; border-radius: 3px; margin-right: 5px; vertical-align: -1px; }
.neu { font-size: 10px; font-weight: 700; letter-spacing: .5px; padding: 1px 6px; border-radius: 6px; background: color-mix(in srgb, var(--blau) 25%, transparent); color: var(--blau); vertical-align: 2px; margin-left: 6px; }
.strecke { width: 100%; height: auto; display: block; }
.strecke .m-t { font-size: 12px; fill: var(--ink2); } .strecke .m-w { font-size: 15px; fill: var(--ink); font-weight: 600; }
.strecke .fluss { animation: fluss 1.6s linear infinite; } @keyframes fluss { to { stroke-dashoffset: -24; } }
.zellen { display: flex; flex-direction: column; }
.zelle { display: grid; grid-template-columns: 40px minmax(0, 1fr) auto auto; gap: 10px; align-items: center; padding: 8px 0; }
.zelle + .zelle { border-top: 1px solid var(--gridc); } .zelle .badge { text-align: center; }
.z-name { display: flex; flex-direction: column; min-width: 0; } .z-name b { font-weight: 600; font-size: 14px; }
.z-name .leise { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.z-wert { white-space: nowrap; min-width: 64px; display: flex; flex-direction: column; align-items: flex-end; font-variant-numeric: tabular-nums; } .z-wert small { opacity: .7; }
.stufen { display: inline-flex; align-items: flex-end; gap: 3px; height: 20px; } .stufen i { width: 5px; border-radius: 2px; background: rgba(127,127,127,.25); }
.klapp summary { list-style: none; cursor: pointer; display: flex; align-items: center; gap: 10px; }
.klapp summary::-webkit-details-marker { display: none; }
.klapp[open] > .hinweis { margin-top: 8px; }
.befund-k { padding: 12px 16px; } .befund-k b { flex: 1; font-weight: 600; font-size: 14px; line-height: 1.35; }
.befund-k .mehr { color: var(--ink2); font-size: 16px; } .befund-k[open] .mehr { color: var(--ink); }
.legende i.ring { border: 1px dashed var(--ink2); background: none; }
.legende i.osm-l { background: #8e8e93; border-radius: 0; clip-path: polygon(50% 0, 100% 100%, 0 100%); }
.legende i.punkt-l { border-radius: 50%; } .legende i.genau-l { border: 1px dashed var(--ink2); background: none; border-radius: 50%; }
.hinweis { font-size: 12px; color: var(--ink2); line-height: 1.45; margin: 0; }
.aus-box .glas-wert, .aus-box .glas-kw { color: var(--ink2); }
.suche { flex: 1 1 160px; min-width: 0; }
/* Geräte kompakt nach Verbindung (AN-0001, Mockup netzwerk.html · Geräte kompakt, Variante D) */
.geraet.gk { grid-template-columns: 22px minmax(0, 1fr) 84px 10px; gap: 8px; padding: 5px 0; font-size: 13px; }
.gk .n { min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: block; } .gk .n small { color: var(--ink2); margin-left: 6px; font-size: 11px; }
.gk .streifen { height: 8px; min-width: 0; } .punkt.blau { background: var(--blau); }
.ggr summary { display: flex; justify-content: space-between; padding: 8px 0 4px; font-size: 12px; letter-spacing: .8px; text-transform: uppercase; color: var(--ink2); cursor: pointer; list-style: none; }
.ggr summary::-webkit-details-marker { display: none; }
.gk-achse { display: grid; grid-template-columns: minmax(0, 1fr) 84px 10px; gap: 8px; } .gk-achse .achse { font-size: 10px; }
select.ga-wahl { font: inherit; font-size: 13px; color: var(--ink); background: rgba(120,120,128,.18); border: 1px solid var(--panel-rand); border-radius: 10px; padding: 5px 8px; }
.ga-zeile { padding: 6px 0 !important; }
/* Einstellungen mit Reitern (AN-0002, Mockup netzwerk.html · Einstellungen gruppiert, Variante B) */
.e-reiter { margin: 4px 0 8px; } .e-reiter.seg button { font-size: 12px; padding: 7px 4px; }
.ek { border: 1px solid var(--gridc); border-radius: 18px; background: rgba(127,127,127,.06); overflow: hidden; }
.ek-inhalt { padding: 4px 14px 12px; display: flex; flex-direction: column; }
.ez { display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 9px 0; min-height: 40px; font-size: 14px; }
.ez + .ez { border-top: 1px solid var(--gridc); } .ez > span:first-child small { display: block; color: var(--ink2); font-size: 11px; }
.ein { display: inline-flex; align-items: center; gap: 6px; background: rgba(127,127,127,.16); border: 1px solid var(--gridc); border-radius: 10px; padding: 5px 10px; font-size: 14px; }
.ein input { width: 64px; border: 0; background: none; color: var(--ink); font: inherit; text-align: right; padding: 0; }
.ein input[type=time], .ein input[type=date] { width: auto; text-align: left; color-scheme: dark; } .hell .ein input { color-scheme: light; }
.ein small { color: var(--ink2); } .sw[disabled] { opacity: .5; cursor: not-allowed; }
/* WU-0007: Einrichtung – was eingerichtet ist und was fehlt (Mockup netzwerk.html · Einrichtung) */
.amber-t { color: var(--amber); }
.e-punkt { display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: var(--amber); margin-left: 4px; vertical-align: 2px; }
.e-punkt.rot { background: var(--rot); }
.vs-stufe { font-size: 11px; letter-spacing: .8px; text-transform: uppercase; color: var(--ink2); padding: 10px 0 2px; display: flex; justify-content: space-between; }
.vs { display: grid; grid-template-columns: 22px minmax(0, 1fr) auto; gap: 10px; align-items: center; padding: 9px 0; min-height: 40px; font-size: 14px; }
.vs + .vs { border-top: 1px solid var(--gridc); }
.vs-st { width: 22px; height: 22px; border-radius: 50%; display: grid; place-items: center; font-size: 12px; font-weight: 700; }
.vs-st.ok { background: color-mix(in srgb, #30d158 22%, transparent); color: #30d158; }
.vs-st.fehlt { background: color-mix(in srgb, var(--amber) 22%, transparent); color: var(--amber); }
.vs-st.muss { background: color-mix(in srgb, var(--rot) 22%, transparent); color: var(--rot); }
.vs-st.aus { background: rgba(127,127,127,.18); color: var(--ink2); }
.vs > span:nth-child(2) { min-width: 0; } .vs small { display: block; color: var(--ink2); font-size: 11px; }
.vs-r { display: flex; gap: 6px; flex-wrap: wrap; justify-content: flex-end; align-items: center; font-size: 13px; }
.vs-r .leise { font-size: 12px; }
.vs-r button { font-size: 13px; padding: 5px 10px; border-radius: 12px; background: rgba(120,120,128,.2); white-space: nowrap; }
.vs-r button.blau { background: color-mix(in srgb, var(--blau) 22%, transparent); }
.vs-kopf { border-radius: 12px; padding: 8px 12px; font-size: 13px; line-height: 1.4; background: rgba(127,127,127,.1); margin: 6px 0 2px; }
@container (max-width: 520px) { .vs { grid-template-columns: 22px minmax(0, 1fr); } .vs-r { grid-column: 2; justify-content: flex-start; } }
/* WU-0008: Diagnose – Rohdaten eines vorgeschalteten Modems (Mockup netzwerk.html · Diagnose). Reiterleiste am Handy schiebbar. */
@container (max-width: 520px) { .e-reiter { overflow-x: auto; scrollbar-width: none; } .e-reiter.seg button { flex: none; padding: 7px 8px; } }
.dg-feld { display: flex; flex-direction: column; gap: 4px; font-size: 13px; color: var(--ink2); padding: 6px 0; }
.dg-feld input { font: inherit; font-size: 14px; color: var(--ink); background: rgba(120,120,128,.14); border: 1px solid var(--gridc); border-radius: 12px; padding: 8px 10px; }
.dg-ab { display: grid; grid-template-columns: 18px minmax(0, 1fr) auto; gap: 8px; align-items: center; padding: 6px 0; font-size: 13px; }
.dg-ab + .dg-ab { border-top: 1px solid var(--gridc); } .dg-ab code { font-size: 12px; color: var(--ink2); }
.dg-roh { font: 11.5px/1.45 ui-monospace, SFMono-Regular, Menlo, monospace; white-space: pre-wrap; word-break: break-all; border: 1px solid var(--gridc); border-radius: 12px; padding: 10px 12px; max-height: 260px; overflow: auto; color: var(--ink); margin: 6px 0; }
.dg-roh i { font-style: normal; color: var(--amber); }
.dg-knoepfe { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 4px; } .dg-knoepfe button { flex: 1 1 140px; padding: 10px; border-radius: 14px; font-size: 14px; font-weight: 600; background: rgba(120,120,128,.2); }
.dg-knoepfe button.amber { background: var(--amber); color: #1c1c1e; } .dg-knoepfe button[disabled] { opacity: .5; cursor: not-allowed; }
/* AN-0007: Messung löschen – Knopf unten im Fenster einer Messung, Rückfrage an derselben Stelle (Mockup netzwerk.html) */
.mg-loeschen { margin-top: 14px; width: 100%; padding: 11px; border-radius: 14px; font-size: 14px; color: var(--rot); background: color-mix(in srgb, var(--rot) 12%, transparent); }
.mg-frage { margin-top: 14px; border-radius: 14px; padding: 12px; background: color-mix(in srgb, var(--rot) 12%, transparent); font-size: 13px; line-height: 1.45; }
.mg-frage .dg-knoepfe button.rot { background: var(--rot); color: #fff; }
/* WU-0010: eigene Arten (Symbol + Name) und Warnungen */
.art-form { gap: 8px; } .art-form .art-ic { width: 46px; flex: none; text-align: center; padding: 7px 4px; } .art-form .art-name { flex: 1; min-width: 0; }
.art-form .knopf { flex: none; padding: 7px 12px; } .art-k { display: flex; gap: 10px; flex: none; } .art-k button, .ez > button.leise { font-size: 13px; padding: 4px 2px; }
select.w-ziel { max-width: 58%; } .ga-warnen .seg { flex: none; }
@container (max-width: 520px) { .ga-warnen { flex-wrap: wrap; } .ga-warnen .seg { width: 100%; } }
/* WU-0009: Internet – Herkunft des Zugangs, ⚙ › Zugang (Mockup netzwerk.html · Internet und Zugang) */
.iq { display: grid; grid-template-columns: 34px minmax(0, 1fr) auto; gap: 10px; align-items: center; padding: 10px 14px; }
.iq-ic { width: 34px; height: 34px; border-radius: 10px; display: grid; place-items: center; background: rgba(127,127,127,.18); font-size: 17px; }
.iq b { display: block; font-size: 15px; } .iq small { display: block; color: var(--ink2); font-size: 12px; }
.iq-r { display: flex; flex-direction: column; align-items: flex-end; gap: 4px; }
.iq-r button { background: none; padding: 2px 0; font-size: 12px; }
.amber-k .glas-wert { color: var(--amber); }
.iz-w { font-size: 13px; color: var(--ink); text-align: right; }
.zg { display: grid; grid-template-columns: 22px minmax(0, 1fr); gap: 10px; align-items: center; padding: 9px 0; font-size: 14px; cursor: pointer; width: 100%; text-align: left; background: none; color: var(--ink); border-radius: 0; }
.zg + .zg { border-top: 1px solid var(--gridc); } .zg small { display: block; color: var(--ink2); font-size: 11px; }
.zg[disabled] { cursor: default; }
.zg-r { width: 18px; height: 18px; border-radius: 50%; border: 2px solid var(--ink2); box-sizing: border-box; } .zg-r.on { border-color: var(--blau); background: radial-gradient(var(--blau) 45%, transparent 50%); }
@container (max-width: 520px) { .iq { grid-template-columns: 34px minmax(0, 1fr); } .iq-r { grid-column: 2; flex-direction: row; align-items: center; } }
/* Melden (Tickets wie im Baustrommanager; Mockup netzwerk.html · Melden, 13.10.2026) */
.melden-knopf { position: absolute; right: 16px; bottom: 96px; z-index: 6; width: 40px; height: 40px; border-radius: 50% !important; display: grid; place-items: center; color: var(--ink2); opacity: .85; }
.melden-knopf:hover { opacity: 1; color: var(--ink); }
.melden-knopf.im-sheet { position: absolute; top: 10px; right: 48px; bottom: auto; width: 30px; height: 30px; z-index: 2; background: rgba(120,120,128,.18); }
.feld { display: flex; flex-direction: column; gap: 6px; font-size: 13px; color: var(--ink2); }
.feld textarea { font: inherit; font-size: 14px; color: var(--ink); background: rgba(120,120,128,.14); border: 1px solid var(--panel-rand); border-radius: 14px; padding: 10px 12px; resize: vertical; }
.ml-kontext { font-size: 12px; display: flex; flex-direction: column; gap: 2px; }
/* WU-0006: öffentlich auf GitHub melden (Mockup githubMelden) */
.leise.mitte { text-align: center; }
.gh-vorschau { font: 12px/1.45 ui-monospace, SFMono-Regular, Menlo, monospace; white-space: pre-wrap; overflow-wrap: anywhere; border: 1px solid var(--panel-rand); border-radius: 12px; padding: 10px 12px; max-height: 240px; overflow: auto; color: var(--ink); }
.gh-warn { border-radius: 12px; padding: 8px 12px; font-size: 12px; line-height: 1.45; background: color-mix(in srgb, var(--amber) 16%, transparent); color: var(--ink); }
.gh-warn b { color: var(--amber); }
.mb-box { border: 1px dashed var(--panel-rand); border-radius: 16px; padding: 10px 12px; display: flex; flex-direction: column; gap: 8px; }
.mb-kopf { display: flex; justify-content: space-between; align-items: baseline; } .mb-knoepfe { display: flex; gap: 8px; flex-wrap: wrap; }
.mb-knoepfe button, .mb-knoepfe label { font-size: 13px; padding: 6px 12px; border-radius: 14px; background: rgba(120,120,128,.2); cursor: pointer; }
.mb-knoepfe input[type=file] { display: none; }
.mb-bilder, .ml-bilder { display: flex; gap: 8px; flex-wrap: wrap; }
.mb-bild { position: relative; width: 96px; display: flex; flex-direction: column; gap: 2px; } .mb-bild img { width: 96px; height: 62px; object-fit: cover; border-radius: 10px; }
.mb-bild .x { position: absolute; top: 3px; right: 3px; width: 22px; height: 22px; border-radius: 50%; background: rgba(0,0,0,.55); color: #fff; font-size: 12px; }
.mb-bild small { font-size: 10px; color: var(--ink2); }
.ml-bilder img, .ml-bilder i { width: 80px; height: 62px; object-fit: cover; border-radius: 10px; cursor: zoom-in; display: block; background: rgba(120,120,128,.2); }
.mb-gross { width: 100%; height: auto; border-radius: 12px; }
.sw { width: 46px; height: 28px; border-radius: 14px; background: rgba(120,120,128,.3); position: relative; flex: none; } .sw i { position: absolute; top: 3px; left: 3px; width: 22px; height: 22px; border-radius: 50%; background: #fff; transition: left .2s; }
.sw.on { background: #30d158; } .sw.on i { left: 21px; }
.knopf.breit { width: 100%; padding: 12px; border-radius: 16px; font-size: 15px; font-weight: 600; } .knopf.amber { background: var(--amber); color: #1c1c1e; }
.knopf.leise-k { background: none; color: var(--ink2); font-weight: 500; }
.ml { padding: 10px 0; display: flex; flex-direction: column; gap: 6px; } .ml + .ml { border-top: 1px solid var(--gridc); } .ml.erledigt { opacity: .7; }
.ml-kopf { display: flex; justify-content: space-between; gap: 8px; flex-wrap: wrap; align-items: baseline; } .ml-text { font-size: 14px; line-height: 1.4; white-space: pre-wrap; }
.ml-notiz { font-size: 12px; color: var(--ink2); border-left: 2px solid var(--blau); padding-left: 8px; } .ml-k { display: flex; gap: 8px; flex-wrap: wrap; }
.toast { position: absolute; left: 50%; bottom: 100px; transform: translate(-50%, 20px); opacity: 0; z-index: 30; padding: 10px 16px; border-radius: 16px; font-size: 13px; transition: opacity .2s, transform .2s; pointer-events: none; max-width: 90%; text-align: center; }
.toast.an { opacity: 1; transform: translate(-50%, 0); }
@container (min-width: 700px) { .melden-knopf { bottom: 24px; right: 24px; } .toast { bottom: 40px; } }
@container (max-width: 520px) {
  .geraet { grid-template-columns: 32px minmax(0, 1fr) auto; } .geraet .streifen { grid-column: 2 / 4; }
  .geraet.gk { grid-template-columns: 22px minmax(0, 1fr) 70px 10px; } .geraet.gk .streifen { grid-column: auto; } .gk-achse { grid-template-columns: minmax(0, 1fr) 70px 10px; }
  .ereig { grid-template-columns: 12px 70px 1fr; }
  .wr { grid-template-columns: 22px repeat(24, minmax(0, 1fr)); gap: 1px; font-size: 9px; }
}
`;
var stil = i`${r(GLAS)}`;

// src/sprache.js
var aktiv = "en";
function waehle(hass) {
  const l4 = String(hass && (hass.locale && hass.locale.language || hass.language) || "").toLowerCase();
  aktiv = l4 === "de" || l4.startsWith("de-") || l4.startsWith("de_") ? "de" : "en";
  return aktiv;
}
var sprache = () => aktiv;
function t3(text, werte) {
  const vorlage = aktiv === "de" ? text : EN[text] ?? text;
  return werte ? vorlage.replace(/\{(\w+)\}/g, (ganz, k2) => k2 in werte ? String(werte[k2]) : ganz) : vorlage;
}
var merke = (text) => text;
var tl = (liste) => liste.map(([k2, text]) => [k2, t3(text)]);
var EN = {
  // Rahmen der Seite
  "Übersicht": "Overview",
  "Speedtest": "Speedtest",
  // Name des Dienstes (Ookla), bleibt
  "Geräte": "Devices",
  "Verbrauch": "Usage",
  "Protokoll": "Log",
  "Alles in Ordnung": "All good",
  "Hinweise": "Notices",
  "Störung": "Outage",
  "FRITZ!Box nicht erreichbar": "FRITZ!Box not reachable",
  "{n} Störung": "{n} outage",
  "{n} Störungen": "{n} outages",
  "{n} Hinweis": "{n} notice",
  "{n} Hinweise": "{n} notices",
  "Die Box antwortet nicht · Home Assistant versucht es jede Minute": "The box is not responding · Home Assistant retries every minute",
  "Internet erreichbar": "Internet reachable",
  "kein Internet": "no internet",
  "Stand {zeit}": "as of {zeit}",
  "Einstellungen": "Settings",
  "Menü": "Menu",
  "Daten nicht abrufbar: {fehler}": "Data not available: {fehler}",
  "lädt …": "loading …",
  "Art nicht gespeichert: {fehler}": "Type not saved: {fehler}",
  // Zeiten (format.js)
  "Heute {uhr}": "Today {uhr}",
  "Gestern {uhr}": "Yesterday {uhr}",
  "gerade eben": "just now",
  "vor {n} min": "{n} min ago",
  "vor {n} h": "{n} h ago",
  "vor {n} Tagen": "{n} days ago",
  "heute": "today",
  "gestern": "yesterday",
  "jetzt": "now",
  "{n} Tag": "{n} day",
  "{n} Tage": "{n} days",
  "{von}–{bis} Uhr": "{von}–{bis} h",
  "{n} Uhr": "{n} h",
  // Übersicht
  "verbunden": "connected",
  "getrennt": "disconnected",
  "Geräte online": "Devices online",
  "nicht verfügbar": "not available",
  "{n} neu": "{n} new",
  "{n} wackelt": "{n} flaky",
  "alles ruhig": "all quiet",
  "Empfang": "Signal",
  "noch keine Messung": "no measurement yet",
  "Heute": "Today",
  "Speedtests {gb}": "speed tests {gb}",
  "keine Zählerdaten": "no counter data",
  "Befunde": "Findings",
  "offen": "open",
  "{n} offen": "{n} open",
  "Im Moment nichts Auffälliges.": "Nothing unusual right now.",
  "Abfrage unvollständig: {fehler}": "Query incomplete: {fehler}",
  "Prüfungen": "Checks",
  "jede Minute": "every minute",
  "Wichtige Ereignisse": "Important events",
  "ganzes Journal ›": "full journal ›",
  "Noch keine.": "None yet.",
  // Speedtest
  "7 Tage": "7 days",
  "4 Wochen": "4 weeks",
  "12 Wochen": "12 weeks",
  "weggelassen": "left out",
  "¼ gezählt": "counted ¼",
  "voll gezählt": "counted fully",
  "{n} % vom Tarif": "{n} % of plan",
  "Tagesverlauf {tag}": "Daily profile {tag}",
  "Median {wert} ({n} Messungen)": "median {wert} ({n} measurements)",
  "keine Messung": "no measurement",
  "Download zuletzt": "Last download",
  "Upload zuletzt": "Last upload",
  "Ping zuletzt": "Last ping",
  "Typisch (Median)": "Typical (median)",
  "{n} Messungen gezählt": "{n} measurements counted",
  "Messungen": "Measurements",
  "{n} belastet · {fehl} Fehlmessungen": "{n} under load · {fehl} failed",
  "Volumen Speedtests": "Speed test volume",
  "diesen Monat (geschätzt)": "this month (estimated)",
  "Wann ist das Internet schnell?": "When is the internet fast?",
  "Median je Wochentag und Stunde": "median per weekday and hour",
  "alle Server": "all servers",
  "keine Messungen im Zeitraum": "no measurements in this period",
  "langsam": "slow",
  "schnell": "fast",
  "typisch": "typical",
  "grau = keine Messung · Zahl = Median der Stunde · Tipp auf einen Tag zeigt den Verlauf · belastete Messungen {wie} (⚙) · {n} ohne Grundlast": "grey = no measurement · number = median of the hour · tap a day for its profile · measurements under load {wie} (⚙) · {n} without base load",
  "Im gewählten Zeitraum keine Messungen.": "No measurements in the selected period.",
  "Auffällig:": "Notable:",
  "Letzte Messungen": "Recent measurements",
  "mit Grundlast": "with base load",
  "Zeit": "Time",
  "Netz": "Network",
  "Zelle": "Cell",
  "Grundlast": "Base load",
  "Serie": "Series",
  "zählt nicht": "not counted",
  "zählt ¼": "counts ¼",
  "belastet": "under load",
  "Mbit/s. Grundlast = Verkehr über die Box in den Minuten vor der Messung; belastet = über {n} Mbit/s. Netz, Zelle (Ankerzelle), Signal (RSRP der Ankerzelle) und Box (Modell · Firmware) zum Zeitpunkt der Messung – ältere Messungen aus Verlauf und Journal nachgetragen, ohne Box („–“). Tippen auf eine Zeile zeigt alle Werte der Messung.": "Mbit/s. Base load = traffic through the box in the minutes before the measurement; under load = above {n} Mbit/s. Network, cell (anchor cell), signal (RSRP of the anchor cell) and box (model · firmware) at the time of the measurement – older measurements filled in from history and journal, without box (“–”). Tap a row to see all values of the measurement.",
  "Noch keine eigenen Messungen. Gemessen wird von der Ookla-Integration.": "No measurements yet. Measuring is done by the Ookla integration.",
  "Ookla-Integration fehlt": "Ookla integration missing",
  "misst gerade …": "measuring …",
  "automatisch aus": "automatic off",
  "verschoben wegen Verkehr – neuer Versuch {uhr}": "postponed due to traffic – next try {uhr}",
  "alle {n} h · nächste {zeit}": "every {n} h · next {zeit}",
  "Ookla misst zusätzlich nach eigenem Takt": "Ookla also measures on its own schedule",
  "In den Ookla-Einstellungen „manuell“ einschalten, damit nur dieser Plan misst.": "Turn on “manual” in the Ookla settings so that only this plan measures.",
  "Messplan": "Schedule",
  "misst …": "measuring …",
  "Jetzt messen": "Measure now",
  "Serie {lauf} von {n} …": "Series {lauf} of {n} …",
  "{n}× messen": "Measure {n}×",
  "Misst {n}× hintereinander – der nächste Durchlauf startet, sobald das Ergebnis des vorigen da ist.": "Measures {n}× in a row – the next run starts as soon as the result of the previous one is in.",
  "Spanne {min}–{max}": "range {min}–{max}",
  "kein Wert": "no value",
  "{n} von {geplant} Durchläufe": "{n} of {geplant} runs",
  "{n} Durchläufe": "{n} runs",
  "Letzte Serie": "Last series",
  "Durchlauf": "Run",
  "Median statt Mittelwert: ein Ausreißer verzieht ihn nicht. Die einzelnen Messungen zählen in Wochenraster und Auswertung normal mit (markiert als „Serie“). Für verschiedene Server in Ookla weitere Tests anlegen – die Serie wechselt dann reihum.": "Median instead of mean: a single outlier does not skew it. The individual measurements count normally in the weekly grid and the evaluation (marked as “Series”). For different servers, add more tests in Ookla – the series then takes turns.",
  "„Jetzt messen“": "“Measure now”",
  "Ookla (eigener Takt oder von Hand)": "Ookla (own schedule or manual)",
  "Werktag": "working day",
  "Wochenende": "weekend",
  "Feiertag": "public holiday",
  "klar": "clear",
  "bewölkt": "cloudy",
  "außergewöhnlich": "exceptional",
  "Nebel": "fog",
  "Hagel": "hail",
  "Gewitter": "thunderstorm",
  "Gewitter mit Regen": "thunderstorm with rain",
  "teils bewölkt": "partly cloudy",
  "Starkregen": "heavy rain",
  "Regen": "rain",
  "Schnee": "snow",
  "Schneeregen": "sleet",
  "sonnig": "sunny",
  "windig": "windy",
  "windig, bewölkt": "windy, cloudy",
  "Messung {zeit}": "Measurement {zeit}",
  "ohne Momentaufnahme (älter als der Verlauf von Home Assistant)": "without snapshot (older than the Home Assistant history)",
  "nachgetragen aus Verlauf und Journal – Box, Heimnetz und Teile des Mobilfunks nicht bekannt": "filled in from history and journal – box, home network and parts of the mobile data unknown",
  "Momentaufnahme im Moment der Messung": "snapshot at the moment of the measurement",
  "Messung löschen": "Delete measurement",
  "Messung {zeit} löschen?": "Delete measurement {zeit}?",
  "Sie verschwindet aus Raster, Tagesverlauf, Auswertung und dieser Liste. Der Verlauf der Ookla-Entitäten in Home Assistant bleibt. Das lässt sich nicht rückgängig machen.": "It disappears from the grid, daily profile, analysis and this list. The history of the Ookla entities in Home Assistant stays. This cannot be undone.",
  "löscht …": "deleting …",
  "Löschen dürfen nur Admins.": "Only admins may delete.",
  "Messung {zeit} gelöscht": "Measurement {zeit} deleted",
  "Messung": "Measurement",
  "Jitter (gesamt · ↓ · ↑)": "Jitter (total · ↓ · ↑)",
  "Note {note}": "grade {note}",
  "Server · Anbieter": "Server · provider",
  "Ergebnis bei Ookla": "Result at Ookla",
  "öffnen ›": "open ›",
  "Auslöser": "Trigger",
  "Durchlauf {lauf} von {n}": "run {lauf} of {n}",
  "Mobilfunk": "Mobile",
  "WLAN": "Wi-Fi",
  "📶 WLAN": "📶 Wi-Fi",
  "Ankerzelle · Sendeanlage": "Anchor cell · site",
  "Anlage {anlage}": "site {anlage}",
  "RSRP · RSRQ Anker": "RSRP · RSRQ anchor",
  "aus": "off",
  "aktiv": "active",
  "Entfernung laut Box": "Distance according to the box",
  "Nachbarzellen": "Neighbour cells",
  "Netz · Gebiet": "Network · area",
  "Verbunden seit": "Connected for",
  "Geschätzter Mast": "Estimated mast",
  "Modell · Firmware": "Model · firmware",
  "Läuft seit": "Running for",
  "Eingeschaltete Bänder": "Enabled bands",
  "Geräte online · davon WLAN": "Devices online · of which Wi-Fi",
  "Umgebung": "Environment",
  "Wetter": "Weather",
  "{n} % Feuchte": "{n} % humidity",
  "{n} % Wolken": "{n} % clouds",
  "Tag": "Day",
  "Nicht verfügbar über die Schnittstelle der Box: genutztes Band, SINR, Bandbreite, MIMO, Carrier Aggregation.": "Not available through the box interface: band in use, SINR, bandwidth, MIMO, carrier aggregation.",
  "Schließen": "Close",
  "Nicht abrufbar: {fehler}": "Not available: {fehler}",
  "niedrigste {min} · höchste {max}": "lowest {min} · highest {max}",
  "{n} gezählt": "{n} counted",
  "{n} belastet": "{n} under load",
  "Wann": "When",
  "… und {n} ältere": "… and {n} older",
  "alle Montage": "all Mondays",
  "alle Dienstage": "all Tuesdays",
  "alle Mittwoche": "all Wednesdays",
  "alle Donnerstage": "all Thursdays",
  "alle Freitage": "all Fridays",
  "alle Samstage": "all Saturdays",
  "alle Sonntage": "all Sundays",
  "oder Datum …": "or date …",
  "{n} Messung": "{n} measurement",
  "{n} Messungen": "{n} measurements",
  "Verlauf schließen": "Close profile",
  "Tagesverlauf": "Daily profile",
  "Tipp auf einen Wochentag (auch links im Raster) oder wähle ein Datum: Median je Stunde, dazu die niedrigste und höchste Messung.": "Tap a weekday (also on the left of the grid) or pick a date: median per hour, plus the lowest and highest measurement.",
  "Verlauf nicht geladen.": "Profile not loaded.",
  "An diesem Tag keine gezählte Messung.": "No counted measurement on this day.",
  "geglättet {wert}": "smoothed {wert}",
  "Beste Stunde {stunde} ({wert})": "Best hour {stunde} ({wert})",
  "schwächste {stunde} ({wert})": "weakest {stunde} ({wert})",
  "Tipp auf eine Stunde zeigt die Werte": "tap an hour to see its values",
  "Tarif {wert}": "plan {wert}",
  "Tarif": "Plan",
  "Median je Stunde": "median per hour",
  "Mittelwert geglättet (3 h)": "mean smoothed (3 h)",
  "niedrigste bis höchste Messung": "lowest to highest measurement",
  "Stunden ohne Messung überbrückt": "hours without measurement bridged",
  "Ein einzelner Tag hat meist nur wenige Messungen (Messplan) – Stunden ohne Messung bleiben leer, bei einer Messung gibt es kein Band.": "A single day usually has only a few measurements (schedule) – hours without measurement stay empty, a single measurement has no band.",
  // Einstellungen
  "weglassen": "leave out",
  "voll": "full",
  "verschieben": "postpone",
  "messen": "measure",
  "⏱️ Messplan": "⏱️ Schedule",
  "💬 Meldungen": "💬 Reports",
  // Einrichtung (WU-0007)
  "🧩 Einrichtung": "🧩 Setup",
  "Muss": "Must",
  "Soll – empfohlen": "Should – recommended",
  "Kann – optional": "Can – optional",
  "{ok} von {von}": "{ok} of {von}",
  "Was eingerichtet ist, sehen nur Admins.": "Only admins can see what is set up.",
  "{n} Voraussetzung fehlt": "{n} requirement missing",
  "{n} Voraussetzungen fehlen": "{n} requirements missing",
  "was dann fehlt, steht in der Zeile. Fehlen FRITZ!Box Tools oder Recorder, auch unter Einstellungen › System › Reparaturen.": "the row says what is then missing. If FRITZ!Box Tools or the recorder are missing, also see Settings › System › Repairs.",
  "{n} empfohlen": "{n} recommended",
  "Heimnetz läuft, mit diesem Teil zeigt es mehr.": "Heimnetz runs; with this part it shows more.",
  "Heimnetz läuft, mit diesen Teilen zeigt es mehr.": "Heimnetz runs; with these parts it shows more.",
  "Alles Nötige ist eingerichtet.": "Everything needed is set up.",
  "Heimnetz installiert nichts selbst: die Knöpfe öffnen Home Assistant oder HACS an der richtigen Stelle. Nach einem Download aus HACS Home Assistant neu starten, dann einrichten. Geprüft wird beim Öffnen dieses Reiters.": "Heimnetz installs nothing itself: the buttons open Home Assistant or HACS at the right place. After a download from HACS, restart Home Assistant, then set it up. Checked whenever this tab is opened.",
  "Einrichtung nicht abrufbar: {fehler}": "Setup status not available: {fehler}",
  // Diagnose: vorgeschaltetes Modem (WU-0008)
  "🔬 Diagnose": "🔬 Diagnostics",
  "Diese Abfrage können nur Admins starten.": "Only admins can run this query.",
  "Adresse des Modems": "Modem address",
  "Kennwort der Weboberfläche (optional)": "Web interface password (optional)",
  "wie beim Anmelden im Browser": "as when logging in via the browser",
  "⏳ fragt ab …": "⏳ querying …",
  "▶ Abfragen": "▶ Query",
  "Nur Adressen im eigenen Heimnetz (z. B. 192.168.x.x). Heimnetz liest nur und ändert am Modem nichts.": "Only addresses inside your home network (e.g. 192.168.x.x). Heimnetz only reads and changes nothing on the modem.",
  "Ergebnis": "Result",
  "{ok} von {gesamt} Abfragen · {werte} Werte · {geschwaerzt} geschwärzt": "{ok} of {gesamt} queries · {werte} values · {geschwaerzt} redacted",
  "Geschwärzt:": "Redacted:",
  "IMEI, IMSI, ICCID, Rufnummer, Seriennummer, MAC- und öffentliche IP-Adressen, WLAN-Namen und -Kennwörter. Die Zellkennung bleibt drin – daraus lässt sich ungefähr bestimmen, wo das Modem steht.": "IMEI, IMSI, ICCID, phone number, serial number, MAC and public IP addresses, Wi-Fi names and passwords. The cell ID stays – it can roughly reveal where the modem is located.",
  "⬇ Als Datei speichern": "⬇ Save as file",
  "⬇ Trotzdem als Datei speichern": "⬇ Save as file anyway",
  "⧉ Kopieren": "⧉ Copy",
  "Datei an den Entwickler schicken – per Mail oder als Anhang an ein GitHub-Issue. Heimnetz sendet selbst nichts.": "Send the file to the developer – by email or attached to a GitHub issue. Heimnetz sends nothing itself.",
  "Abfrage nicht möglich: {fehler}": "Query not possible: {fehler}",
  "Gespeichert: {name}": "Saved: {name}",
  "Kopiert – {n} Werte": "Copied – {n} values",
  "gelten für die ganze Seite": "apply to the whole page",
  "nur Admins ändern": "only admins can change",
  "Tarif Download": "Plan download",
  "Tarif Upload": "Plan upload",
  "Auswerten ab": "Evaluate from",
  "ältere Messungen zählen nicht": "older measurements do not count",
  "Speichern": "Save",
  "Belastete Messungen": "Measurements under load",
  "über {n} Mbit/s Verkehr vor der Messung": "above {n} Mbit/s of traffic before the measurement",
  "Die Auswahl „belastete Messungen“ gilt für das Wochenraster auf diesem Gerät.": "The choice “measurements under load” applies to the weekly grid on this device.",
  "verschoben – neuer Versuch {uhr}": "postponed – next try {uhr}",
  "Gemessen wird von der Ookla-Integration; dieser Plan sagt ihr, wann.": "Measuring is done by the Ookla integration; this schedule tells it when.",
  "Ohne sie kann der Plan nicht messen.": "Without it the schedule cannot measure.",
  "Jede Messung kostet Datenvolumen – bei schnellen Anschlüssen einige hundert MB. Bei Mobilfunk mit Datenlimit lieber selten messen.": "Every test uses data – a few hundred MB on fast connections. On mobile plans with a data cap, test rarely.",
  "Jede Messung kostet etwa {mb} MB Datenvolumen; mit diesem Plan {n} Messungen am Tag, rund {tag} MB am Tag und {monat} GB im Monat. Bei Mobilfunk mit Datenlimit lieber selten messen.": "Every test uses about {mb} MB of data; with this schedule {n} tests a day, around {tag} MB a day and {monat} GB a month. On mobile plans with a data cap, test rarely.",
  "Jede Messung kostet etwa {mb} MB Datenvolumen.": "Every test uses about {mb} MB of data.",
  "Ookla Speedtest ist nicht eingerichtet": "Ookla Speedtest is not set up",
  "Heimnetz läuft auch ohne – nur Messungen gibt es dann keine. Für Speedtests die HACS-Integration „Ookla Speedtest“ installieren und einrichten; den Rest erledigt dieser Plan.": "Heimnetz works without it – there are just no measurements. For speed tests install and set up the HACS integration “Ookla Speedtest”; this schedule does the rest.",
  "Ookla Speedtest auf GitHub ↗": "Ookla Speedtest on GitHub ↗",
  "In den Ookla-Einstellungen ist „manuell“ aus – dann misst Ookla neben diesem Plan. Für einen einzigen Plan dort „manuell“ einschalten.": "“Manual” is off in the Ookla settings – then Ookla measures in addition to this schedule. For a single schedule, turn on “manual” there.",
  "Automatisch messen": "Measure automatically",
  "Wie oft": "How often",
  "alle {n} h": "every {n} h",
  "Nur zwischen": "Only between",
  "Bei Verkehr im Heimnetz": "With traffic in the home network",
  "über {n} Mbit/s": "above {n} Mbit/s",
  "trotzdem messen": "measure anyway",
  "Serie „{n}× messen“": "Series “measure {n}×”",
  "Durchläufe hintereinander, Ergebnis als Median": "runs in a row, result as median",
  "Server der Serie": "Servers of the series",
  "alle Ookla-Tests reihum": "all Ookla tests in turn",
  "Verkehr gerade": "Current traffic",
  "ruhig": "quiet",
  "Nächste Messung": "Next measurement",
  "Server und „manuell“": "Servers and “manual”",
  "in Ookla eingestellt": "set in Ookla",
  "Wird verschoben, versucht es der Plan alle 5 Minuten neu, höchstens 30 Minuten lang; danach misst er trotzdem und die Messung gilt als belastet.": "When postponed, the schedule retries every 5 minutes for at most 30 minutes; then it measures anyway and the measurement counts as under load.",
  "Schwacher Empfang unter": "Weak signal below",
  "so meldet die Box den Empfang je Gerät": "as the box reports the signal per device",
  "Kanal, Gast-WLAN und Bänder stellst du in der FRITZ!Box ein – die Seite ändert dort nichts.": "Channel, guest Wi-Fi and bands are set in the FRITZ!Box – this page changes nothing there.",
  // Geräte
  "Alle": "All",
  "Auffällig": "Notable",
  "neu": "new",
  "wackelt": "flaky",
  "nach Verbindung": "by connection",
  "nach Art": "by type",
  "Geräte im Heimnetz": "Devices in the home network",
  "{n} von {gesamt} online · letzte 24 h": "{n} of {gesamt} online · last 24 h",
  "Suchen (Name oder IP)": "Search (name or IP)",
  "Die FRITZ!Box antwortet nicht – die Liste zeigt den letzten bekannten Stand.": "The FRITZ!Box is not responding – the list shows the last known state.",
  "Kein Gerät passt.": "No device matches.",
  "Punkt: grün online, grau offline, amber wackelt, blau neu. Streifen: grün = im Heimnetz, schraffiert = keine Aufzeichnung. Das WLAN-Band kennt die Box nur bei verbundenen Geräten. „🔐 VPN (WireGuard)“ sind Geräte, die sich von unterwegs über VPN mit deiner Box verbinden. Tippen öffnet den Verlauf.": "Dot: green online, grey offline, amber flaky, blue new. Stripe: green = in the home network, hatched = no record. The box only knows the Wi-Fi band of connected devices. “🔐 VPN (WireGuard)” are devices that connect to your box via VPN while away. Tap to open the history.",
  "{n} von {gesamt} online": "{n} of {gesamt} online",
  "Adresse {quelle}": "address {quelle}",
  "Zufalls-Adresse": "random address",
  "zuerst gesehen {tag}": "first seen {tag}",
  "Art": "Type",
  "automatisch": "automatic",
  "online 7 Tage": "online 7 days",
  "Abbrüche": "Drops",
  "Letzte 7 Tage": "Last 7 days",
  "Ereignisse": "Events",
  "Keine Ereignisse in den letzten 7 Tagen.": "No events in the last 7 days.",
  // Funk · WLAN
  "Die Box meldet gerade keine WLAN-Werte.": "The box currently reports no Wi-Fi values.",
  "Kanal {k}": "Channel {k}",
  "fest": "fixed",
  "{n} Gerät": "{n} device",
  "{n} Geräte": "{n} devices",
  "abgeschaltet": "switched off",
  "Gast-WLAN": "Guest Wi-Fi",
  "an": "on",
  "nur lesen": "read only",
  "Geräte im WLAN": "Devices on Wi-Fi",
  "{n} verbunden · schwächstes zuerst": "{n} connected · weakest first",
  "Gerät": "Device",
  "schwach": "weak",
  "Gast": "Guest",
  "Kein Gerät im WLAN.": "No device on Wi-Fi.",
  "Empfang und Geschwindigkeit meldet die FRITZ!Box je Gerät; schwach = unter {n} % (⚙). Tippen öffnet den Verlauf des Geräts.": "The FRITZ!Box reports signal and speed per device; weak = below {n} % (⚙). Tap to open the history of the device.",
  "Kanalwechsel": "Channel changes",
  "letzte 7 Tage · die Box wählt selbst": "last 7 days · the box chooses itself",
  "Kein Wechsel in den letzten 7 Tagen.": "No change in the last 7 days.",
  // Funk · Mobilfunk
  "Die Box meldet gerade keine Mobilfunkwerte.": "The box currently reports no mobile values.",
  "Verbindung zur Basisstation": "Connection to the base station",
  "Was zeigt die Liste?": "What does the list show?",
  "Die Box hält gleichzeitig mehrere Zellen: die Ankerzelle trägt die Verbindung, die übrigen bündeln dazu.": "The box holds several cells at once: the anchor cell carries the connection, the others are aggregated.",
  "Balken = Signalstärke (RSRP), daneben die Signalqualität (RSRQ).": "Bars = signal strength (RSRP), next to it the signal quality (RSRQ).",
  "Neueinwahl {zeit}": "reconnect {zeit}",
  "ohne Neueinwahl (7 Tage)": "no reconnect (7 days)",
  "Neueinwahlen, letzte 7 Tage": "reconnects, last 7 days",
  "Bänder": "Bands",
  "Verlauf Signalstärke": "Signal strength history",
  "4G-Anker": "4G anchor",
  "schwach (unter {n} dBm)": "weak (below {n} dBm)",
  "Steigt die Linie nach dem Umstellen der Box um etwa 10 dBm, war der Standort die Bremse.": "If the line rises by about 10 dBm after moving the box, the location was holding it back.",
  "Noch kein Verlauf aufgezeichnet.": "No history recorded yet.",
  "{art}-Zelle": "{art} cell",
  "Zelle {kennung}": "cell {kennung}",
  "Signal {wort} · {n} dBm": "signal {wort} · {n} dBm",
  "Basisstation": "Base station",
  "BeaconDB kennt diese Zellen nicht. Mit einem Schlüssel von opencellid.org (Einstellungen → Geräte & Dienste → Heimnetz → Konfigurieren) fragt die Integration zusätzlich OpenCellID.": "BeaconDB does not know these cells. With a key from opencellid.org (Settings → Devices & services → Heimnetz → Configure) the integration also asks OpenCellID.",
  "Weder OpenCellID noch BeaconDB kennen diese Zellen – die Karte zeigt nur die Entfernung laut Box.": "Neither OpenCellID nor BeaconDB know these cells – the map only shows the distance according to the box.",
  "Der Dienst für den Standort der Zellen war nicht erreichbar; neuer Versuch in einer Stunde.": "The service for the cell locations was not reachable; next try in one hour.",
  "OpenCellID lehnt den Schlüssel ab – unter Geräte & Dienste → Heimnetz → Konfigurieren prüfen.": "OpenCellID rejects the key – check under Devices & services → Heimnetz → Configure.",
  "Die Box nennt für keine Zelle eine vollständige Kennung – die Karte zeigt nur die Entfernung.": "The box gives no complete ID for any cell – the map only shows the distance.",
  "Wo steht der Mast?": "Where is the mast?",
  "geschätzt · {n} von {gesamt} Zellen gefunden": "estimated · {n} of {gesamt} cells found",
  "Wohnung": "Home",
  "Mast {name} (geschätzt)": "Mast {name} (estimated)",
  "4G + 5G (vermutlich)": "4G + 5G (probably)",
  "Ankerzelle": "Anchor cell",
  "weitere Zellen": "other cells",
  "Genauigkeit": "Accuracy",
  "Funkmast laut OpenStreetMap": "Radio mast according to OpenStreetMap",
  "(orange umrandet: passt am besten)": "(orange outline: best match)",
  "{ring} laut Box": "{ring} according to the box",
  "Woher kommt das?": "Where does this come from?",
  "Die Box meldet nur die Entfernung (Ring), nicht die Richtung. Jede Zelle mit voller Kennung schlägt die Integration bei BeaconDB (ohne Schlüssel) und – mit eigenem Schlüssel – bei OpenCellID nach und merkt sich das Ergebnis; es zählt der genauere Fund. Hinaus geht nur die Kennung der Zelle, nie dein Standort. Beide Dienste kennen nicht den Mast selbst, sondern die Orte, an denen Nutzer die Zelle empfangen haben – daher der Kreis für die Genauigkeit. Zellen derselben Sendeanlage (Kennung vor dem Bindestrich) hängen am selben Mast; sein Standort ist das Mittel ihrer Punkte, genauere zählen mehr. Zellen, von denen die Box nur die PCI nennt, lassen sich nicht nachschlagen – auch 5G nicht: Die Box nennt für 5G nur diese Nummer. Bei 5G-NSA hängt die 5G-Zelle aber meist am selben Mast wie die LTE-Ankerzelle, deshalb steht dort „4G + 5G (vermutlich)“, solange 5G mitläuft. Die Namen der Zellen erscheinen beim Hineinzoomen. Zoomen mit ＋/−, Mausrad oder zwei Fingern, ziehen zum Verschieben, ⌖ zeigt wieder alles. Die Kartenkacheln lädt dein Browser von basemap.at (Server der Stadt Wien) oder OpenStreetMap; der Anbieter sieht dabei den Kartenausschnitt, nicht mehr. Die gewählte Grundlage merkt sich dein Browser. „📡 Masten (OSM)“ zeigt Funkmasten, die in OpenStreetMap eingetragen sind – echte Bauwerke, aber meist ohne Betreiber. Orange umrandet ist der Mast, der am nächsten am geschätzten Mast der Zellen steht (höchstens 1,5 km daneben); ist der nicht bekannt, der Mast, dessen Entfernung am besten zur Entfernung laut Box passt – die schwankt je Zelle aber stark. Ein Hinweis, kein Beweis. Zellen einer Sendeanlage, die einmal gefunden wurden, zählen einen Monat lang mit – auch wenn die Box gerade an einem Sektor hängt, den keine Datenbank kennt. Antippen eines Masts zeigt Entfernung und Richtung und – mit OpenCellID-Schlüssel – Anbieter und Technik der Zellen, die OpenCellID in höchstens 500 m Abstand kennt (aus dem Datenabzug für ganz Österreich, einmal im Monat geladen und hier ausgewertet). ⛶ öffnet die Karte über die ganze Seite. Die Integration fragt dafür einmal im Monat einen großen Ausschnitt auf festem Raster bei OpenStreetMap ab; daraus lässt sich deine Wohnung nur auf etwa 22 × 15 km eingrenzen.": "The box only reports the distance (ring), not the direction. The integration looks up every cell with a full ID at BeaconDB (no key needed) and – with your own key – at OpenCellID and remembers the result; the more accurate find counts. Only the cell ID leaves your network, never your location. Neither service knows the mast itself, only the places where users received the cell – hence the circle for the accuracy. Cells of the same site (ID before the hyphen) hang on the same mast; its location is the mean of their points, more accurate ones weigh more. Cells for which the box only gives the PCI cannot be looked up – 5G neither: the box only gives this number for 5G. With 5G NSA, however, the 5G cell usually hangs on the same mast as the LTE anchor cell, which is why it says “4G + 5G (probably)” while 5G is active. The cell names appear when zooming in. Zoom with ＋/−, mouse wheel or two fingers, drag to move, ⌖ shows everything again. Your browser loads the map tiles from basemap.at (servers of the City of Vienna) or OpenStreetMap; the provider only sees the map section. Your browser remembers the chosen base map. “📡 Masts (OSM)” shows radio masts entered in OpenStreetMap – real structures, but usually without operator. Outlined in orange is the mast closest to the estimated mast of the cells (at most 1.5 km away); if that is unknown, the mast whose distance best matches the distance according to the box – which varies a lot per cell, though. A hint, not proof. Cells of a site that were found once keep counting for a month – even while the box is on a sector no database knows. Tapping a mast shows distance and direction and – with an OpenCellID key – providers and technology of the cells OpenCellID knows within 500 m (from the data dump for all of Austria, downloaded once a month and evaluated here). ⛶ opens the map across the whole page. For this, the integration queries a large section on a fixed grid from OpenStreetMap once a month; it only narrows down your home to about 22 × 15 km.",
  // Karte
  "Grundkarte": "Base map",
  "-Mitwirkende": " contributors",
  "Automatisch": "Automatic",
  "basemap.at grau": "basemap.at grey",
  "Masten": "Masts",
  "Vollbild schließen": "Close full screen",
  "Vollbild": "Full screen",
  "Karte: Wohnung, Zellen und geschätzter Mast": "Map: home, cells and estimated mast",
  "Näher": "Zoom in",
  "Weiter weg": "Zoom out",
  "Alles zeigen": "Show all",
  "Funkmasten aus OpenStreetMap ein/aus": "Radio masts from OpenStreetMap on/off",
  "Masten (OSM)": "Masts (OSM)",
  "Kartengrundlage": "Base map",
  "Funkmast": "Radio mast",
  "am nächsten am geschätzten Mast": "closest to the estimated mast",
  "passt zur Entfernung laut Box": "matches the distance according to the box",
  "{entfernung} {richtung} von der Wohnung": "{entfernung} {richtung} of home",
  "laut OpenCellID: {n} Zelle in höchstens 500 m – geschätzt, nicht amtlich": "according to OpenCellID: {n} cell within 500 m – estimated, not official",
  "laut OpenCellID: {n} Zellen in höchstens 500 m – geschätzt, nicht amtlich": "according to OpenCellID: {n} cells within 500 m – estimated, not official",
  "Anbieter und Technik unbekannt – OpenCellID kennt hier keine Zellen (oder es ist kein Schlüssel eingetragen). Im Senderkataster nachsehen.": "Provider and technology unknown – OpenCellID knows no cells here (or no key is set). Check the official transmitter register.",
  "Funkmast – antippen für Infos": "Radio mast – tap for details",
  "passt": "match",
  "Mast {name}": "Mast {name}",
  // Verbrauch
  "Keine Zähler von FRITZ!Box Tools gefunden („GB empfangen/gesendet“).": "No counters from FRITZ!Box Tools found (“GB received/sent”).",
  "davon Speedtests {gb} GB": "of which speed tests {gb} GB",
  "Diese Woche": "This week",
  "seit Montag": "since Monday",
  "Dieser Monat": "This month",
  "seit dem 1.": "since the 1st",
  "Ø je Tag": "Ø per day",
  "letzte {n} Tage": "last {n} days",
  "Davon Speedtests": "Of which speed tests",
  "geschätzt": "estimated",
  "Datenverbrauch der ganzen Box": "Data usage of the whole box",
  "davon Speedtests": "of which speed tests",
  "GB je Tag": "GB per day",
  "Die FRITZ!Box zählt nur gesamt, nicht je Gerät.": "The FRITZ!Box only counts the total, not per device.",
  // Protokoll
  "Journal": "Journal",
  "ohne Zeit": "without time",
  "Journal – was hat sich geändert?": "Journal – what has changed?",
  "Protokoll der FRITZ!Box": "FRITZ!Box log",
  "aus den Prüfungen dieser Seite": "from the checks of this page",
  "Ereignisse der Box": "events of the box",
  "Suchen (Enter)": "Search (Enter)",
  "nur Warnungen": "warnings only",
  "Keine Einträge.": "No entries.",
  // Melden
  "Fehler": "Bug",
  "Wunsch": "Wish",
  "Anregung": "Suggestion",
  "Was ist passiert, was hättest du erwartet?": "What happened, what did you expect?",
  "Was wünschst du dir?": "What would you like?",
  "Deine Idee": "Your idea",
  "Fehler, Wunsch oder Anregung melden": "Report a bug, wish or suggestion",
  "Melden": "Report",
  "Kein Bild gewählt": "No image selected",
  "Bild gewählt": "Image selected",
  "Bild eingefügt": "Image pasted",
  "Bild aufgenommen": "Image captured",
  "{n} von {gesamt}": "{n} of {gesamt}",
  "Bild wählen": "Choose image",
  "Fenster aufnehmen": "Capture window",
  "oder einen Screenshot mit": "or paste a screenshot with",
  "Strg+V": "Ctrl+V",
  "einfügen (z. B. nach Win+Shift+S)": "(e.g. after Win+Shift+S)",
  "Screenshot mit den Handy-Tasten machen, dann „Bild wählen“ – der neueste steht in der Galerie vorne": "Take a screenshot with the phone buttons, then “Choose image” – the newest is first in the gallery",
  "wird auf höchstens {n} px verkleinert": "scaled down to at most {n} px",
  "Bild {n}": "Image {n}",
  "Bild entfernen": "Remove image",
  "Fehler, Wunsch oder Anregung – wird ein lokales Ticket; öffentlich über GitHub erreicht es den Entwickler.": "Bug, wish or suggestion – becomes a local ticket; sent publicly via GitHub, it reaches the developer.",
  "kurz beschreiben": "describe briefly",
  "Reiter": "Tab",
  "Stand der Seite mitschicken": "Send page state",
  "Reiter, Filter und offener Dialog – hilft beim Nachstellen, ohne Zugangsdaten": "tab, filters and open dialog – helps to reproduce, without credentials",
  "sendet …": "sending …",
  "Senden": "Send",
  "Abbrechen": "Cancel",
  "wieder öffnen": "reopen",
  "Löschen": "Delete",
  "Meldungen": "Reports",
  "Jede Meldung ist ein Ticket: FE Fehler, WU Wunsch, AN Anregung": "Every report is a ticket: FE bug, WU wish, AN suggestion",
  "erledigt": "done",
  "alle": "all",
  "Keine Meldungen": "No reports",
  "Als Markdown kopieren": "Copy as Markdown",
  "Die Tickets bleiben lokal in Home Assistant und liegen lesbar unter heimnetz/meldungen.md. Ist eines erledigt, wird es geschlossen; passt es nicht, hier wieder öffnen.": "Tickets stay local in Home Assistant and can be read in heimnetz/meldungen.md. Once one is done it gets closed; if that does not fit, reopen it here.",
  "Schließen und löschen dürfen nur Admins.": "Only admins may close and delete.",
  "Tickets aus dem Melden-Knopf": "Tickets from the report button",
  "Fehler, Wünsche, Anregungen – lokal gespeichert": "bugs, wishes, suggestions – stored locally",
  "{n} offen · {erledigt} erledigt": "{n} open · {erledigt} done",
  "Dialog „{art}“": "dialog “{art}”",
  "Handy": "Phone",
  "Bitte kurz beschreiben": "Please describe briefly",
  "Nicht gesendet: {fehler}": "Not sent: {fehler}",
  "Danke – gemeldet als {ticket}": "Thanks – reported as {ticket}",
  " mit {n} Bild": " with {n} image",
  " mit {n} Bildern": " with {n} images",
  " · {n} Bild kam nicht an": " · {n} image did not arrive",
  " · {n} Bilder kamen nicht an": " · {n} images did not arrive",
  "Höchstens {n} Bilder": "At most {n} images",
  "Kein Bild ({typ}) – bitte ein Bild wählen": "Not an image ({typ}) – please choose an image",
  "Bild wird geladen …": "Loading image …",
  "Bild nicht lesbar": "Image not readable",
  "Bild nicht übernommen: {fehler}": "Image not added: {fehler}",
  "Bild nicht lesbar – bitte ein anderes wählen": "Image not readable – please choose another",
  "Aufnahme abgebrochen": "Capture cancelled",
  "Meldungen nicht abrufbar: {fehler}": "Reports not available: {fehler}",
  "Nicht geändert: {fehler}": "Not changed: {fehler}",
  "{ticket} gelöscht": "{ticket} deleted",
  "Nicht gelöscht: {fehler}": "Not deleted: {fehler}",
  "{n} Meldungen als Markdown kopiert": "{n} reports copied as Markdown",
  // Öffentlich auf GitHub melden (WU-0006)
  "Senden + öffentlich auf GitHub": "Send + report publicly on GitHub",
  "GitHub: für den Entwickler sichtbar, auch wenn er dein Heimnetz nicht kennt – mit deinem eigenen GitHub-Konto": "GitHub: visible to the developer, even without knowing your home network – with your own GitHub account",
  "Öffentlich auf GitHub melden": "Report publicly on GitHub",
  "Das Issue ist für alle sichtbar. Du siehst hier genau, was mitgeht; auf GitHub kannst du es vor dem Absenden noch ändern.": "The issue is visible to everyone. You see exactly what is included; on GitHub you can still change it before submitting.",
  "Der Text ist für den Link zu lang und wurde gekürzt – ganz steht er im lokalen Ticket.": "The text is too long for the link and was shortened – the full text is in the local ticket.",
  "Zell- und Signaldaten mitsenden": "Include cell and signal data",
  "Im Moment keine Zelldaten von der Box": "No cell data from the box right now",
  "Zellkennung, Signal, Entfernung zum Mast – hilft bei Fehlern im Mobilfunk-Reiter": "Cell ID, signal, distance to the mast – helps with problems in the mobile tab",
  "Achtung:": "Caution:",
  "Aus Zellkennung und Entfernung lässt sich ungefähr bestimmen, wo du wohnst. Nur mitsenden, wenn es für den Fehler nötig ist.": "Cell ID and distance reveal roughly where you live. Only include them if the problem needs them.",
  "Nie dabei: Gerätenamen, Hardware-Adressen, IP-Adressen, Standort von Home Assistant, Kennwörter.": "Never included: device names, hardware addresses, IP addresses, location of Home Assistant, passwords.",
  "Dein Bild kann GitHub nicht über den Link übernehmen – nach dem Öffnen ins Issue ziehen.": "GitHub cannot take your image over the link – drag it into the issue once it is open.",
  "Deine {n} Bilder kann GitHub nicht über den Link übernehmen – nach dem Öffnen ins Issue ziehen.": "GitHub cannot take your {n} images over the link – drag them into the issue once it is open.",
  "Speichern und weiter zu GitHub": "Save and continue to GitHub",
  "Zurück": "Back",
  "Vorschau nicht abrufbar: {fehler}": "Preview not available: {fehler}",
  "Gemeldet als {ticket} – GitHub öffnet sich in einem neuen Fenster": "Reported as {ticket} – GitHub opens in a new window",
  "Gemeldet als {ticket} – im Issue auf GitHub steht {vorher}, bitte dort ändern": "Reported as {ticket} – the GitHub issue says {vorher}, please change it there",
  // Internet und Zugang (WU-0009)
  "Internet": "Internet",
  "🌐 Zugang": "🌐 Access",
  "Automatisch (empfohlen)": "Automatic (recommended)",
  "Mobilfunk über die FRITZ!Box": "Mobile via the FRITZ!Box",
  "eingebautes Modem oder Stick": "built-in modem or stick",
  "Mobilfunk über ein vorgeschaltetes Modem": "Mobile via an upstream modem",
  "ZTE, Huawei, TP-Link … (Beta)": "ZTE, Huawei, TP-Link … (beta)",
  "DSL über die FRITZ!Box": "DSL via the FRITZ!Box",
  "ADSL, VDSL, Supervectoring": "ADSL, VDSL, supervectoring",
  "Glasfaser": "Fibre",
  "Kabel": "Cable",
  "über die FRITZ!Box": "via the FRITZ!Box",
  "keiner": "none",
  "Den Zugang legen nur Admins fest.": "Only admins set the access.",
  "Vorschlag: {text}": "Suggestion: {text}",
  "Internet kommt über": "Internet comes via",
  "jetzt: {text}": "now: {text}",
  "Vorgeschaltetes Gerät": "Upstream device",
  "Adresse": "Address",
  "vorgeschlagen: {liste} – nur Adressen im eigenen Heimnetz": "suggested: {liste} – only addresses in your own home network",
  "Kennwort der Weboberfläche": "Password of the web interface",
  "hinterlegt – zum Ändern neu eingeben": "stored – enter again to change",
  "wird in Home Assistant gespeichert (wie bei anderen Integrationen), nie angezeigt": "stored in Home Assistant (like other integrations), never shown",
  "Kennwort entfernen": "Remove password",
  "Ersatzzugang bei Ausfall": "Backup access on failure",
  "Ersatz": "Backup",
  "z. B. Mobilfunk-Stick an der FRITZ!Box, wenn DSL ausfällt": "e.g. a mobile stick on the FRITZ!Box when DSL fails",
  "↻ Erneut suchen": "↻ Search again",
  "🔬 Rohdaten abfragen ›": "🔬 Query raw data ›",
  "automatisch erkannt": "detected automatically",
  "festgelegt": "set manually",
  "Ersatz: {text}": "Backup: {text}",
  "Die FRITZ!Box meldet etwas anderes: {vorschlag}": "The FRITZ!Box reports something else: {vorschlag}",
  "ändern ›": "change ›",
  "📶 Ersatz": "📶 Backup",
  "Die Box meldet noch nicht, woher das Internet kommt – sie wird alle 10 Minuten gefragt.": "The box does not report yet where the internet comes from – it is asked every 10 minutes.",
  "Vorgeschaltet": "Upstream",
  "Die Box meldet gerade keine DSL-Werte.": "The box currently reports no DSL values.",
  "möglich {n}": "attainable {n}",
  "Tarif {n}": "plan {n}",
  "laut Box": "according to the box",
  "Synchron Download": "Sync download",
  "Synchron Upload": "Sync upload",
  "Störabstand ↓ / ↑": "Noise margin ↓ / ↑",
  "Marge, gut ab {n} dB": "margin, good from {n} dB",
  "Dämpfung ↓ / ↑": "Attenuation ↓ / ↑",
  "Leitung": "Line",
  "laut FRITZ!Box": "according to the FRITZ!Box",
  "Status": "Status",
  "Verfahren": "Mode",
  "Vectoring: {text}": "Vectoring: {text}",
  "letzte Neusynchronisierung {zeit}": "last resync {zeit}",
  "seit dem Start von Heimnetz keine Neusynchronisierung gesehen": "no resync seen since Heimnetz started",
  "Fehler je Stunde": "Errors per hour",
  "CRC = nicht korrigierbar, FEC = korrigiert": "CRC = uncorrectable, FEC = corrected",
  "Neusynchronisierungen": "Resyncs",
  "{n} in 7 Tagen": "{n} in 7 days",
  "Gegenstelle (DSLAM)": "Remote end (DSLAM)",
  "Verlauf 7 Tage": "History 7 days",
  "Synchron-Download und Störabstand": "sync download and noise margin",
  "Synchron-Download (Mbit/s)": "sync download (Mbit/s)",
  "Störabstand Download (dB)": "noise margin download (dB)",
  "Die Box meldet gerade keine Glasfaser-Werte.": "The box currently reports no fibre values.",
  "gut {von} … {bis}": "good {von} … {bis}",
  "Bereich meldet die Box nicht": "range not reported by the box",
  "Empfangene Lichtleistung": "Received optical power",
  "Gesendete Lichtleistung": "Transmitted optical power",
  "Verbindung": "Connection",
  "Glasfaser-Anschluss": "Fibre connection",
  "{n} Neusynchronisierungen laut Box": "{n} resyncs according to the box",
  "fehlerhaft empfangene Pakete": "packets received with errors",
  "Temperatur Modul": "Module temperature",
  "Anschluss-Kennung": "Connection ID",
  "⟨nur in der Box⟩": "⟨only in the box⟩",
  "Seriennummer und Kennung zeigt die Seite nicht": "the page does not show serial number and ID",
  "Lichtleistung": "optical power",
  "empfangene Lichtleistung (dBm)": "received optical power (dBm)",
  "Kabelanschluss getrennt": "Cable connection down",
  "Kabelanschluss verbunden": "Cable connection up",
  "Kanäle, Pegel und Fehler des Kabelmodems gibt die Schnittstelle der FRITZ!Box (TR-064) nicht heraus – nur die Geschwindigkeit der Verbindung.": "The FRITZ!Box interface (TR-064) does not provide channels, levels and errors of the cable modem – only the connection speed.",
  "Empfangskanäle": "Downstream channels",
  "Empfangspegel": "Downstream level",
  "Signal/Rausch (MER)": "Signal/noise (MER)",
  "Kanäle": "Channels",
  "Sendepegel": "Upstream level",
  "Fehler korrigiert / nicht korrigierbar": "Errors corrected / uncorrectable",
  "Kanalliste": "Channel list",
  "Ersatzzugang Mobilfunk": "Mobile backup access",
  "bereit · nicht aktiv": "ready · not active",
  "zuletzt aktiv {zeit}": "last active {zeit}",
  "Signal gerade {n} dBm": "signal now {n} dBm",
  "Umschaltungen": "Switchovers",
  "letzte 30 Tage": "last 30 days",
  "Über Ersatz": "Via backup",
  "Datenmenge": "Data volume",
  "über Ersatz: meldet die Box nicht getrennt": "via backup: not reported separately by the box",
  "Neusynchronisierung": "Resync",
  "Zugang nicht abrufbar: {fehler}": "Access not available: {fehler}",
  "Gesucht: FRITZ!Box neu gefragt": "Searched: FRITZ!Box asked again",
  "Eben erst gesucht – in einer halben Minute wieder": "Just searched – again in half a minute",
  "wird nur für diese Abfrage verwendet und nicht gespeichert – leer: das unter 🌐 Zugang für diese Adresse hinterlegte": "used only for this query and not stored – empty: the one stored under 🌐 Access for this address",
  // Vorgeschaltetes Gerät (WU-0009 Stufe 2)
  "Glasfaser über die FRITZ!Box": "Fibre via the FRITZ!Box",
  "eingebautes Glasfaser-Modem (z. B. FRITZ!Box 5590 Fiber)": "built-in fibre modem (e.g. FRITZ!Box 5590 Fiber)",
  "Glasfaser über ein eigenes Modem": "Fibre via an own modem",
  "ONT von Nokia, Huawei, Zyxel … – nur erkennen (Beta)": "ONT from Nokia, Huawei, Zyxel … – detection only (beta)",
  "Gesucht wird nur an der gespeicherten Adresse, am Vorschlag der FRITZ!Box und an den üblichen Modem-Adressen ({liste}) – kein Absuchen des Heimnetzes. Heimnetz liest nur.": "Only the stored address, the address suggested by the FRITZ!Box and the common modem addresses ({liste}) are asked – no scanning of the home network. Heimnetz only reads.",
  "über die Integration in Home Assistant": "via the Home Assistant integration",
  "zuletzt gelesen {zeit}": "last read {zeit}",
  "Erkannt": "Detected",
  "noch nicht gesucht": "not searched yet",
  "Hier fragt Heimnetz ein Gerät vor der FRITZ!Box (5G/LTE-Modem, Glasfaser-Modem) ab: erkennt Hersteller und Schnittstelle und zeigt alle Rohdaten, geschwärzt – damit der Entwickler weitere Geräte unterstützen kann.": "Here Heimnetz queries a device in front of the FRITZ!Box (5G/LTE modem, fibre modem): it detects maker and interface and shows all raw data, redacted – so the developer can support more devices.",
  "Heimnetz liest dieses Gerät laufend": "Heimnetz reads this device continuously",
  "nur erkennen – Werte noch nicht unterstützt": "detection only – values not supported yet",
  "Mit einem eigenen Glasfaser-Modem (ONT) vor der FRITZ!Box: unter ⚙ › 🌐 Zugang „Glasfaser über eigenes Modem“ wählen. Heimnetz erkennt das ONT; seine Werte liest es noch nicht.": "With an own fibre modem (ONT) in front of the FRITZ!Box: choose “Fibre via an own modem” under ⚙ › 🌐 Access. Heimnetz detects the ONT; it does not read its values yet.",
  "Werte vom vorgeschalteten Modem (Beta)": "Values from the upstream modem (beta)",
  "Die FRITZ!Box hängt hinter dem {geraet} und kennt das Funknetz nicht. Die Werte kommen aus dessen Integration in Home Assistant. Was sie nicht liefert, steht als „–“.": "The FRITZ!Box sits behind the {geraet} and does not know the mobile network. The values come from its Home Assistant integration. Whatever it does not provide shows as “–”.",
  "Modem": "modem",
  "Die FRITZ!Box hängt hinter dem {geraet} und kennt das Funknetz nicht. Heimnetz liest Zelle und Signal direkt am Gerät (Anmeldung mit dem in ⚙ › 🌐 Zugang hinterlegten Kennwort). Was es nicht liefert, steht als „–“.": "The FRITZ!Box sits behind the {geraet} and does not know the mobile network. Heimnetz reads cell and signal directly from the device (login with the password stored under ⚙ › 🌐 Access). Whatever it does not provide shows as “–”.",
  "Zuletzt gelesen {zeit}.": "Last read {zeit}.",
  "🌐 Zugang ›": "🌐 Access ›",
  "Band {band}": "band {band}",
  "Verbindung von {geraet} zur Basisstation": "Connection of {geraet} to the base station",
  "Werte von": "Values from",
  "vorgeschaltetes Modem": "upstream modem",
  "Band · SINR": "Band · SINR",
  "Funkwerte vom vorgeschalteten Modem – was es nicht liefert, fehlt.": "Radio values from the upstream modem – whatever it does not provide is missing.",
  "Gesucht: FRITZ!Box und vorgeschaltetes Gerät neu gefragt": "Searched: FRITZ!Box and upstream device asked again",
  // Eigene Arten und Warnungen (WU-0010)
  "🏷️ Arten": "🏷️ Types",
  "🔔 Warnungen": "🔔 Alerts",
  "wie Gruppe": "as group",
  "immer": "always",
  "nie": "never",
  "＋ eigene Art …": "＋ custom type …",
  "Name der Art, z. B. Baustelle": "Name of the type, e.g. building site",
  "Anlegen": "Create",
  "Eigene Arten erscheinen unter Geräte › nach Art und in ⚙ › Warnungen; umbenennen und löschen unter ⚙ › 🏷️ Arten.": "Custom types show up under Devices › by type and in ⚙ › Alerts; rename and delete them under ⚙ › 🏷️ Types.",
  "eigene Einstellung": "own setting",
  "wie Gruppe (an)": "as group (on)",
  "wie Gruppe (aus)": "as group (off)",
  "🔔 Bei offline warnen": "🔔 Alert when offline",
  "Symbol": "Symbol",
  "Eigene Arten legen nur Admins an.": "Only admins create custom types.",
  "eigene · {anzahl}": "custom · {anzahl}",
  "✎ ändern": "✎ edit",
  "löschen": "delete",
  "„{text}“ löschen?": "Delete “{text}”?",
  "Name, z. B. Werkstatt": "Name, e.g. workshop",
  "＋ Neue Art": "＋ New type",
  "Eigene Arten": "Custom types",
  "noch keine": "none yet",
  "Zuordnen im Fenster eines Geräts (Reiter Geräte → Gerät antippen → Art). Eigene Arten gelten wie die festen: unter Geräte › nach Art und in ⚙ › 🔔 Warnungen.": "Assign them in the window of a device (Devices tab → tap a device → Type). Custom types work like the built-in ones: under Devices › by type and in ⚙ › 🔔 Alerts.",
  "Feste Arten": "Built-in types",
  "fest · {anzahl}": "built-in · {anzahl}",
  "Warnungen stellen nur Admins ein.": "Only admins set up alerts.",
  "Nachricht an": "Message to",
  "notify-Dienst von Home Assistant": "notify service of Home Assistant",
  "Dienst fehlt": "Service missing",
  "Den gewählten notify-Dienst gibt es gerade nicht – Warnungen kommen nur als Ereignis und ins Journal.": "The chosen notify service does not exist right now – alerts only arrive as an event and in the journal.",
  "Offline melden nach": "Report offline after",
  "so lange muss ein Gerät weg sein": "how long a device has to be gone",
  "🔔 Testnachricht senden": "🔔 Send test message",
  "Überwachen nach Art": "Watch by type",
  "{n} von {gesamt} Geräten": "{n} of {gesamt} devices",
  "Einzeln abweichend": "Individual exceptions",
  "wird immer gemeldet – abweichend von der Gruppe": "always reported – differs from its group",
  "wird nie gemeldet – abweichend von der Gruppe": "never reported – differs from its group",
  "zurücksetzen": "reset",
  "keine": "none",
  "Einzelne Geräte stellst du im Fenster des Geräts um (Reiter Geräte → Gerät antippen).": "Change single devices in the window of the device (Devices tab → tap a device).",
  "Außerdem melden": "Also report",
  "Wieder online": "Back online",
  "mit Dauer, nur wenn vorher gemeldet": "with duration, only if reported before",
  "Neues unbekanntes Gerät": "New unknown device",
  "sobald sich ein noch nie gesehenes Gerät verbindet": "as soon as a never-seen device connects",
  "Internet oder FRITZ!Box weg": "Internet or FRITZ!Box down",
  "kommt an, sobald es wieder geht – mit Dauer des Ausfalls": "arrives as soon as it works again – with the duration of the outage",
  "Beispiel": "Example",
  "Nachrichten an die Companion App laufen über den Push-Dienst von Google bzw. Apple – der Gerätename verlässt dabei das Heimnetz. Für jede Meldung gibt es zusätzlich das Ereignis „heimnetz_warnung“ für eigene Automationen.": "Messages to the companion app go through the push service of Google or Apple – the device name leaves the home network. Every alert also fires the event “heimnetz_warnung” for your own automations.",
  "{n} Gerät bekommt wieder die automatisch erkannte Art; Warnungen für diese Art fallen weg.": "{n} device gets its automatically detected type back; alerts for this type are dropped.",
  "{n} Geräte bekommen wieder die automatisch erkannte Art; Warnungen für diese Art fallen weg.": "{n} devices get their automatically detected type back; alerts for this type are dropped.",
  "Arten nicht abrufbar: {fehler}": "Types not available: {fehler}",
  "Art angelegt": "Type created",
  "Art nicht angelegt: {fehler}": "Type not created: {fehler}",
  "Art gelöscht": "Type deleted",
  "Warnungen nicht abrufbar: {fehler}": "Alerts not available: {fehler}",
  "Nicht gespeichert: {fehler}": "Not saved: {fehler}",
  "Testnachricht an {ziel} geschickt": "Test message sent to {ziel}",
  "Keine Nachricht eingestellt – nur das Ereignis „heimnetz_warnung“ ausgelöst": "No message set up – only the event “heimnetz_warnung” was fired"
};

// src/format.js
var TAGE = { de: ["So", "Mo", "Di", "Mi", "Do", "Fr", "Sa"], en: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"] };
var MONATE = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
var zwei = (n4) => String(n4).padStart(2, "0");
function wochentage(abMontag = false) {
  const l4 = TAGE[sprache()] || TAGE.en;
  return abMontag ? [...l4.slice(1), l4[0]] : l4;
}
function datum(d3, mitTag = true) {
  const tagName = mitTag ? `${wochentage()[d3.getDay()]} ` : "";
  return sprache() === "de" ? `${tagName}${zwei(d3.getDate())}.${zwei(d3.getMonth() + 1)}.` : `${tagName}${d3.getDate()} ${MONATE[d3.getMonth()]}`;
}
function zahl(v2, stellen = 0) {
  if (v2 == null || Number.isNaN(v2)) return "–";
  return Number(v2).toLocaleString(sprache(), { minimumFractionDigits: stellen, maximumFractionDigits: stellen });
}
function zeit(s4, jetzt = Date.now()) {
  if (s4 == null) return "–";
  const d3 = new Date(s4 * 1e3), h3 = new Date(jetzt);
  const uhr2 = `${zwei(d3.getHours())}:${zwei(d3.getMinutes())}`;
  const tagBeginn = (x2) => new Date(x2.getFullYear(), x2.getMonth(), x2.getDate()).getTime();
  const abstand = Math.round((tagBeginn(h3) - tagBeginn(d3)) / 864e5);
  if (abstand === 0) return t3("Heute {uhr}", { uhr: uhr2 });
  if (abstand === 1) return t3("Gestern {uhr}", { uhr: uhr2 });
  return `${datum(d3)} ${uhr2}`;
}
function uhr(s4) {
  if (s4 == null) return "–";
  const d3 = new Date(s4 * 1e3);
  return `${zwei(d3.getHours())}:${zwei(d3.getMinutes())}`;
}
function tag(s4, jetzt = Date.now()) {
  return zeit(s4, jetzt).replace(/ \d\d:\d\d$/, "");
}
function vor(s4, jetzt = Date.now()) {
  if (s4 == null) return "";
  const x2 = Math.max(0, jetzt / 1e3 - s4);
  if (x2 < 90) return t3("gerade eben");
  if (x2 < 5400) return t3("vor {n} min", { n: Math.round(x2 / 60) });
  if (x2 < 172800) return t3("vor {n} h", { n: Math.round(x2 / 3600) });
  return t3("vor {n} Tagen", { n: Math.round(x2 / 86400) });
}
function farbe(lage) {
  if (lage == null) return "rgba(127,127,127,.12)";
  const x2 = Math.max(0, Math.min(1, lage));
  return x2 < 0.5 ? `color-mix(in srgb, var(--amber) ${Math.round(x2 * 200)}%, var(--rot))` : `color-mix(in srgb, var(--s3) ${Math.round((x2 - 0.5) * 200)}%, var(--amber))`;
}
function punkt(stufe) {
  return { kritisch: "rot", warnung: "amber", info: "grau", ok: "" }[stufe] ?? "grau";
}
function phase(sonne) {
  const a3 = sonne && sonne.attributes;
  if (!a3 || a3.elevation == null) return "tag";
  if (a3.elevation < -6) return "nacht";
  if (a3.elevation < 6) return a3.rising ? "morgen" : "abend";
  return "tag";
}

// src/ansichten/teile.js
function seg(liste, wert2, wahl, klein = true) {
  return b2`<div class="seg ${klein ? "klein" : ""}">
    ${liste.map(([k2, t7]) => b2`<button class=${k2 === wert2 ? "on" : ""} @click=${() => wahl(k2)}>${t7}</button>`)}
  </div>`;
}
function kachel(titel, wert2, unter, klick) {
  return b2`<button class="glas-k glas-panel" @click=${klick || (() => {
  })}>
    <span class="glas-klein">${titel}</span><span class="glas-wert">${wert2}</span><span class="glas-kwk">${unter}</span>
  </button>`;
}
function streifen(felder) {
  const breite = 100 / Math.max(1, felder.length);
  return b2`<span class="streifen">${felder.map((f3) => b2`<i class=${f3} style="width:${breite}%"></i>`)}</span>`;
}

// src/ansichten/uebersicht.js
function uebersicht(p4, u3) {
  const aus = !u3.box_erreichbar;
  const g2 = u3.geraete || {};
  const e6 = u3.empfang;
  const s4 = u3.speedtest;
  const h3 = u3.verbrauch_heute;
  const kacheln = [
    kachel(
      "Internet",
      b2`<span class=${u3.internet.ok ? "ok" : "rot-t"}>${u3.internet.ok ? t3("verbunden") : t3("getrennt")}</span>`,
      u3.internet.technik || "",
      () => p4.geh("protokoll")
    ),
    kachel(
      t3("Geräte online"),
      aus ? "–" : b2`${g2.online}<small> / ${g2.bekannt}</small>`,
      aus ? t3("nicht verfügbar") : [g2.neu ? t3("{n} neu", { n: g2.neu }) : "", g2.wackelt ? t3("{n} wackelt", { n: g2.wackelt }) : ""].filter(Boolean).join(" · ") || t3("alles ruhig"),
      () => p4.geh("geraete")
    ),
    kachel(
      t3("Empfang"),
      e6 ? b2`${e6.rsrp_anker ?? "–"}<small> dBm</small>` : "–",
      e6 ? `${e6.wort ?? ""}${e6.rsrp_5g != null ? ` · 5G ${e6.rsrp_5g} dBm` : ""}` : t3("nicht verfügbar"),
      () => {
        p4.setze("internet", { sicht: "haupt" }, false);
        p4.geh("internet");
      }
    ),
    kachel(
      "Speedtest",
      s4 && s4.down != null ? b2`${zahl(s4.down)}<small> Mbit/s</small>` : "–",
      s4 ? `↑ ${zahl(s4.up)} · ${zahl(s4.ping)} ms · ${vor(s4.t)}` : t3("noch keine Messung"),
      () => p4.geh("speedtest")
    ),
    kachel(
      t3("Heute"),
      h3 ? b2`${zahl(h3.down + h3.up, 1)}<small> GB</small>` : "–",
      h3 ? `↓ ${zahl(h3.down, 1)} · ↑ ${zahl(h3.up, 1)} · ${t3("Speedtests {gb}", { gb: zahl(h3.speedtest, 1) })}` : t3("keine Zählerdaten"),
      () => p4.geh("verbrauch")
    ),
    kachel(t3("Befunde"), b2`${(u3.befunde || []).length}`, t3("offen"), () => {
    })
  ];
  return b2`
    <div class="glas-raster">${kacheln}</div>
    <div class="raster2">
      <div class="glas-panel block">
        <div class="block-kopf"><h3>${t3("Befunde")}</h3><span class="leise">${t3("{n} offen", { n: (u3.befunde || []).length })}</span></div>
        ${(u3.befunde || []).length ? u3.befunde.map((b3) => b2`<div class="befund"><span class="punkt ${punkt(b3.stufe)}"></span><div><b>${b3.titel}</b><p>${b3.text}</p></div></div>`) : b2`<div class="leer">${t3("Im Moment nichts Auffälliges.")}</div>`}
        ${(u3.fehler || []).length ? b2`<p class="fein">${t3("Abfrage unvollständig: {fehler}", { fehler: u3.fehler.join(" · ") })}</p>` : A}
      </div>
      <div class="glas-panel block">
        <div class="block-kopf"><h3>${t3("Prüfungen")}</h3><span class="leise">${t3("jede Minute")}</span></div>
        ${u3.pruefungen.map((x2) => b2`<div class="zeile">
          <span style="display:flex;gap:10px;align-items:center"><span class="punkt ${x2.ok === true ? "" : x2.ok === false ? "rot" : "grau"}"></span>${x2.name}</span>
          <span class="leise" style="text-align:right">${x2.wert}</span></div>`)}
      </div>
    </div>
    <div class="glas-panel block">
      <div class="block-kopf"><h3>${t3("Wichtige Ereignisse")}</h3><button class="leise blau" @click=${() => p4.geh("protokoll")}>${t3("ganzes Journal ›")}</button></div>
      ${(u3.wichtig || []).length ? u3.wichtig.map((z2) => b2`<div class="ereig"><span class="punkt ${punkt(z2.stufe)}"></span><time>${zeit(z2.t)}</time><span>${z2.text}</span></div>`) : b2`<div class="leer">${t3("Noch keine.")}</div>`}
    </div>`;
}

// src/ansichten/speedtest.js
var GROESSEN = [["down", "↓ Download"], ["up", "↑ Upload"], ["ping", "Ping"]];
var ZEITRAEUME = [[7, merke("7 Tage")], [28, merke("4 Wochen")], [84, merke("12 Wochen")]];
var BELASTET = { aus: merke("weggelassen"), halb: merke("¼ gezählt"), mit: merke("voll gezählt") };
var prozent = (a3) => a3 == null ? "" : t3("{n} % vom Tarif", { n: zahl(a3 * 100) });
var zeitraum = (tage) => t3(ZEITRAEUME.find(([x2]) => x2 === tage)?.[1] ?? "");
var stunden = (h3) => t3("{von}–{bis} Uhr", { von: h3, bis: h3 + 1 });
function speedtest(p4, d3) {
  const o7 = p4._opt.speedtest;
  const l4 = d3.letzte;
  const la = d3.letzte_anteil || {};
  const tagWahl = o7.datum ? null : o7.tag;
  const TAGE2 = wochentage(true);
  const raster = d3.raster.map((reihe, wd) => b2`<button class="tag ${tagWahl === wd ? "on" : ""}" title=${t3("Tagesverlauf {tag}", { tag: TAGE2[wd] })}
    @click=${() => p4.setze("speedtest", { tag: wd, datum: null, stunde: null })}>${TAGE2[wd]}</button>${reihe.map((z2, h3) => z2.anzahl ? b2`<i class="kachel ${p4._kachel && p4._kachel.fest && p4._kachel.tag === wd && p4._kachel.stunde === h3 ? "wahl" : ""}" data-k="${wd}-${h3}"
      style="background:${farbe(z2.lage)}" aria-label=${`${TAGE2[wd]} ${stunden(h3)}: ${t3("Median {wert} ({n} Messungen)", { wert: `${zahl(z2.median, 1)} ${d3.einheit}`, n: z2.anzahl })}`}
      @mouseenter=${() => p4.kachelZeigen(wd, h3, false)} @mouseleave=${() => p4.kachelWeg(false)}
      @click=${() => p4.kachelZeigen(wd, h3, true)}><b>${zahl(z2.median)}</b></i>` : b2`<i class="ohne" title=${`${TAGE2[wd]} ${stunden(h3)}: ${t3("keine Messung")}`}></i>`)}`);
  return b2`
    <div class="glas-raster">
      ${kachel(t3("Download zuletzt"), l4 ? b2`${zahl(l4.down)}<small> Mbit/s</small>` : "–", l4 ? `${prozent(la.down)} · ${zeit(l4.t)}` : t3("noch keine Messung"))}
      ${kachel(t3("Upload zuletzt"), l4 ? b2`${zahl(l4.up)}<small> Mbit/s</small>` : "–", prozent(la.up))}
      ${kachel(t3("Ping zuletzt"), l4 ? b2`${zahl(l4.ping)}<small> ms</small>` : "–", l4 && l4.server ? `Server ${l4.server}` : "")}
      ${kachel(t3("Typisch (Median)"), d3.median != null ? b2`${zahl(d3.median, 1)}<small> ${d3.einheit}</small>` : "–", d3.anteil != null ? prozent(d3.anteil) : t3("{n} Messungen gezählt", { n: d3.anzahl }))}
      ${kachel(t3("Messungen"), b2`${d3.gesamt}`, t3("{n} belastet · {fehl} Fehlmessungen", { n: d3.belastet, fehl: d3.fehl }))}
      ${kachel(t3("Volumen Speedtests"), b2`${zahl(d3.volumen_monat_mb / 1e3, 1)}<small> GB</small>`, t3("diesen Monat (geschätzt)"))}
    </div>
    <div class="glas-panel block">
      <div class="block-kopf"><h3>${t3("Wann ist das Internet schnell?")}</h3><span class="leise">${t3("Median je Wochentag und Stunde")}</span></div>
      <div class="leiste">
        ${seg(tl(ZEITRAEUME), o7.tage, (v2) => p4.setze("speedtest", { tage: v2, datum: null, stunde: null }))}
        ${seg(GROESSEN, o7.groesse, (v2) => p4.setze("speedtest", { groesse: v2, stunde: null }))}
        <select style="font-size:12px;padding:5px 8px" @change=${(e6) => p4.setze("speedtest", { server: e6.target.value, stunde: null })}>
          <option value="" ?selected=${!o7.server}>${t3("alle Server")}</option>
          ${d3.server.map((s4) => b2`<option value=${s4.name} ?selected=${o7.server === s4.name}>${s4.name} (${s4.anzahl})</option>`)}
          ${o7.server && !d3.server.some((s4) => s4.name === o7.server) ? b2`<option value=${o7.server} selected>${o7.server} (${t3("keine Messungen im Zeitraum")})</option>` : A}
        </select>
      </div>
      ${d3.gesamt ? b2`<div class="wr"><span></span>${Array.from({ length: 24 }, (_2, h3) => b2`<span>${h3 % 3 ? "" : h3}</span>`)}${raster}</div>
        <div class="leiste" style="justify-content:space-between"><div class="skala">${d3.groesse === "ping" ? t3("langsam") : "0 %"}<i></i>${d3.groesse === "ping" ? t3("schnell") : d3.tarif ? t3("{n} % vom Tarif", { n: 100 }) : t3("typisch")}</div>
        <span class="leise">${t3("grau = keine Messung · Zahl = Median der Stunde · Tipp auf einen Tag zeigt den Verlauf · belastete Messungen {wie} (⚙) · {n} ohne Grundlast", { wie: t3(BELASTET[o7.grundlast]), n: d3.ungeprueft })}</span></div>` : b2`<div class="leer">${t3("Im gewählten Zeitraum keine Messungen.")}</div>`}
      ${d3.gesamt ? tagesverlauf(p4, d3) : A}
      ${d3.auffaellig ? b2`<p class="hinweis"><b>${t3("Auffällig:")}</b> ${d3.auffaellig}</p>` : A}
    </div>
    ${planStatus(p4, p4._daten.einstellungen)}
    ${serieKarte(p4._daten.einstellungen)}
    <div class="glas-panel block"><div class="block-kopf"><h3>${t3("Letzte Messungen")}</h3><span class="leise">${t3("mit Grundlast")}</span></div>
        ${d3.messungen.length ? b2`<div class="tab-scroll"><table class="t">
          <tr><th>${t3("Zeit")}</th><th>Server</th><th class="r">↓</th><th class="r">↑</th><th class="r">Ping</th><th>${t3("Netz")}</th><th>${t3("Zelle")}</th><th class="r">Signal</th><th>Box</th><th class="r">${t3("Grundlast")}</th><th></th></tr>
          ${d3.messungen.map((m3) => {
    const k2 = m3.kontext || {};
    return b2`<tr class="klick ${m3.gewicht ? "" : "belastet"}" @click=${() => p4.messungOeffnen(m3)}>
            <td>${zeit(m3.t)}</td><td>${m3.server ?? "–"}</td><td class="r">${zahl(m3.down)}</td><td class="r">${zahl(m3.up)}</td>
            <td class="r">${zahl(m3.ping)}</td><td>${k2.netz ? b2`<span class="badge ${k2.netz.startsWith("5G") ? "blau-b" : ""}">${k2.netz}</span>` : "–"}</td>
            <td>${k2.zelle ? kurzZelle(k2.zelle) : "–"}</td><td class="r">${k2.rsrp != null ? `${zahl(k2.rsrp)} dBm` : "–"}</td>
            <td>${k2.box_modell ? boxKurz(k2) : b2`<span class="leise">–</span>`}</td><td class="r">${zahl(m3.last, 1)}</td>
            <td>${m3.serie ? b2`<span class="badge blau-b">${t3("Serie")}</span> ` : A}${m3.belastet ? b2`<span class="badge amber-b">${m3.gewicht === 0 ? t3("zählt nicht") : m3.gewicht < 1 ? t3("zählt ¼") : t3("belastet")}</span>` : A}</td></tr>`;
  })}
        </table></div><p class="hinweis">${t3("Mbit/s. Grundlast = Verkehr über die Box in den Minuten vor der Messung; belastet = über {n} Mbit/s. Netz, Zelle (Ankerzelle), Signal (RSRP der Ankerzelle) und Box (Modell · Firmware) zum Zeitpunkt der Messung – ältere Messungen aus Verlauf und Journal nachgetragen, ohne Box („–“). Tippen auf eine Zeile zeigt alle Werte der Messung.", { n: zahl(d3.schwelle, 1) })}</p>` : b2`<div class="leer">${t3("Noch keine eigenen Messungen. Gemessen wird von der Ookla-Integration.")}</div>`}
    </div>`;
}
var OOKLA_LINK = "https://github.com/soulripper13/hass-speedtest-ookla";
function planStatus(p4, e6) {
  if (!e6 || !e6.messplan) return A;
  const m3 = e6.messplan, z2 = e6.plan, o7 = e6.ookla, admin = p4.istAdmin;
  const stand = !o7.vorhanden ? t3("Ookla-Integration fehlt") : z2.misst ? t3("misst gerade …") : !m3.an ? t3("automatisch aus") : z2.wartet ? t3("verschoben wegen Verkehr – neuer Versuch {uhr}", { uhr: uhr(z2.neuer_versuch) }) : t3("alle {n} h · nächste {zeit}", { n: m3.takt_h, zeit: z2.naechste ? zeit(z2.naechste) : "–" });
  return b2`<div class="glas-panel block">
    ${!o7.vorhanden ? b2`<div class="befund ohne-ookla"><span class="punkt grau"></span><div><b>${t3("Ookla Speedtest ist nicht eingerichtet")}</b>
      <p>${t3("Heimnetz läuft auch ohne – nur Messungen gibt es dann keine. Für Speedtests die HACS-Integration „Ookla Speedtest“ installieren und einrichten; den Rest erledigt dieser Plan.")}
      <a class="blau" href=${OOKLA_LINK} target="_blank" rel="noopener noreferrer">${t3("Ookla Speedtest auf GitHub ↗")}</a></p></div></div>` : A}
    ${o7.misst_selbst ? b2`<div class="befund"><span class="punkt amber"></span><div><b>${t3("Ookla misst zusätzlich nach eigenem Takt")}</b><p>${t3("In den Ookla-Einstellungen „manuell“ einschalten, damit nur dieser Plan misst.")}</p></div></div>` : A}
    <div class="zeile" style="padding:2px 0"><span style="display:flex;gap:10px;align-items:center"><span class="punkt ${m3.an && o7.vorhanden ? "" : "grau"}"></span>
      <span><b style="font-weight:600">${t3("Messplan")}</b> <span class="leise">${stand}</span></span></span>
      ${admin ? b2`<span class="chips"><button class="chip glas-panel" style="font-weight:600" ?disabled=${z2.misst || !!e6.serie || !o7.vorhanden} @click=${() => p4.jetztMessen()}>${z2.misst && !e6.serie ? `⏳ ${t3("misst …")}` : `▶ ${t3("Jetzt messen")}`}</button>
        <button class="chip glas-panel serie-knopf" style="font-weight:600" ?disabled=${!!e6.serie || z2.misst || !o7.vorhanden} @click=${() => p4.serieStarten()}>${e6.serie ? `⏳ ${t3("Serie {lauf} von {n} …", { lauf: e6.serie.lauf, n: e6.serie.n })}` : `▶ ${t3("{n}× messen", { n: m3.serie })}`}</button></span>` : A}</div>
    ${e6.serie ? b2`<p class="hinweis">${t3("Misst {n}× hintereinander – der nächste Durchlauf startet, sobald das Ergebnis des vorigen da ist.", { n: e6.serie.n })}</p>` : A}
    ${p4._hinweisPlan ? b2`<p class="fein">${p4._hinweisPlan}</p>` : A}
  </div>`;
}
function serieKarte(e6) {
  const s4 = e6 && e6.letzte_serie;
  if (!s4 || !s4.laeufe || !s4.laeufe.length) return A;
  const k2 = (titel, w2, einheit, zusatz) => b2`<div class="glas-k glas-panel"><span class="glas-klein">${titel} (Median)</span>
    <span class="glas-wert">${w2 ? zahl(w2.median) : "–"}<small> ${einheit}</small></span>
    <span class="glas-kwk">${w2 ? t3("Spanne {min}–{max}", { min: zahl(w2.min), max: zahl(w2.max) }) : t3("kein Wert")}${zusatz || ""}</span></div>`;
  const laeufe = s4.laeufe.length < s4.geplant ? t3("{n} von {geplant} Durchläufe", { n: s4.laeufe.length, geplant: s4.geplant }) : t3("{n} Durchläufe", { n: s4.laeufe.length });
  return b2`<div class="glas-panel block">
    <div class="block-kopf"><h3>${t3("Letzte Serie")}</h3><span class="leise">${zeit(s4.t)} · ${laeufe} · ${s4.server.join(", ") || "–"}</span></div>
    <div class="glas-raster" style="grid-template-columns:repeat(3,1fr)">
      ${k2("Download", s4.down, "Mbit/s", s4.anteil != null ? ` · ${t3("{n} % vom Tarif", { n: s4.anteil })}` : "")}${k2("Upload", s4.up, "Mbit/s")}${k2("Ping", s4.ping, "ms")}</div>
    <div class="tab-scroll"><table class="t" style="margin-top:8px"><tr><th>${t3("Durchlauf")}</th><th>Server</th><th class="r">↓</th><th class="r">↑</th><th class="r">Ping</th></tr>
      ${s4.laeufe.map((x2, i6) => b2`<tr><td>${i6 + 1} · ${zeit(x2.t)}</td><td>${x2.server ?? "–"}</td><td class="r">${zahl(x2.down)}</td><td class="r">${zahl(x2.up)}</td><td class="r">${zahl(x2.ping)}</td></tr>`)}</table></div>
    <p class="hinweis">${t3("Median statt Mittelwert: ein Ausreißer verzieht ihn nicht. Die einzelnen Messungen zählen in Wochenraster und Auswertung normal mit (markiert als „Serie“). Für verschiedene Server in Ookla weitere Tests anlegen – die Serie wechselt dann reihum.")}</p></div>`;
}
var kurzZelle = (z2) => z2.includes("-") ? `…-${z2.split("-").pop()}` : z2;
function boxKurz(k2) {
  const modell = k2.box_modell.replace(/^FRITZ!Box\s*/, "");
  const teile = (k2.box_firmware || "").split(".");
  const fw = teile.length >= 3 ? `${Number(teile[1])}.${teile[2]}` : k2.box_firmware || "";
  return fw ? `${modell} · ${fw}` : modell;
}
var AUSLOESER = { messplan: merke("Messplan"), jetzt: merke("„Jetzt messen“"), serie: merke("Serie"), ookla: merke("Ookla (eigener Takt oder von Hand)") };
var TAGESART = { werktag: merke("Werktag"), wochenende: merke("Wochenende"), feiertag: merke("Feiertag") };
var WETTER = {
  "clear-night": merke("klar"),
  cloudy: merke("bewölkt"),
  exceptional: merke("außergewöhnlich"),
  fog: merke("Nebel"),
  hail: merke("Hagel"),
  lightning: merke("Gewitter"),
  "lightning-rainy": merke("Gewitter mit Regen"),
  partlycloudy: merke("teils bewölkt"),
  pouring: merke("Starkregen"),
  rainy: merke("Regen"),
  snowy: merke("Schnee"),
  "snowy-rainy": merke("Schneeregen"),
  sunny: merke("sonnig"),
  windy: merke("windig"),
  "windy-variant": merke("windig, bewölkt")
};
function dauer(s4) {
  if (s4 == null) return null;
  const tg = Math.floor(s4 / 86400), h3 = Math.floor(s4 % 86400 / 3600), m3 = Math.floor(s4 % 3600 / 60);
  return tg ? `${t3(tg === 1 ? "{n} Tag" : "{n} Tage", { n: tg })} ${h3} h` : h3 ? `${h3} h ${m3} min` : `${m3} min`;
}
function messungBlatt(p4) {
  const m3 = p4._blatt.m, k2 = m3.kontext || {}, nach = k2.quelle === "nachgetragen", leer = !k2.quelle;
  const z2 = (titel, wert2) => b2`<div class="zeile"><span class="leise">${titel}</span><span style="text-align:right">${wert2 ?? b2`<span class="leise">–</span>`}</span></div>`;
  const mit = (...w2) => w2.some((x2) => x2 == null) ? null : w2.join(" · ");
  const dbm = (v2, e6 = "dBm") => v2 == null ? null : `${zahl(v2)} ${e6}`;
  return b2`<div class="griff"></div><button class="zu" @click=${() => p4.zu()}>✕</button>
    <h3>${t3("Messung {zeit}", { zeit: zeit(m3.t) })}</h3>
    <div class="leise">${leer ? t3("ohne Momentaufnahme (älter als der Verlauf von Home Assistant)") : nach ? t3("nachgetragen aus Verlauf und Journal – Box, Heimnetz und Teile des Mobilfunks nicht bekannt") : t3("Momentaufnahme im Moment der Messung")}</div>
    <div class="gruppe"><span class="gr-ic">📈</span>${t3("Messung")}</div>
    ${z2("Download · Upload · Ping", `${zahl(m3.down)} · ${zahl(m3.up)} Mbit/s · ${zahl(m3.ping)} ms`)}
    ${z2(t3("Jitter (gesamt · ↓ · ↑)"), k2.jitter != null ? `${[k2.jitter, k2.jitter_down, k2.jitter_up].map((x2) => x2 == null ? "–" : zahl(x2, 1)).join(" · ")} ms` : null)}
    ${z2("Bufferbloat", k2.bufferbloat ? t3("Note {note}", { note: k2.bufferbloat }) : null)}
    ${z2(t3("Server · Anbieter"), [m3.server, k2.anbieter].filter(Boolean).join(" · ") || null)}
    ${z2(t3("Ergebnis bei Ookla"), k2.ergebnis_url && /^https:\/\//.test(k2.ergebnis_url) ? b2`<a class="blau" href=${k2.ergebnis_url} target="_blank" rel="noopener noreferrer">${t3("öffnen ›")}</a>` : null)}
    ${z2(t3("Auslöser"), k2.ausloeser ? `${AUSLOESER[k2.ausloeser] ? t3(AUSLOESER[k2.ausloeser]) : k2.ausloeser}${k2.serie_n ? `, ${t3("Durchlauf {lauf} von {n}", { lauf: k2.serie_lauf, n: k2.serie_n })}` : ""}` : null)}
    ${z2(t3("Grundlast"), m3.last != null ? `${zahl(m3.last, 1)} Mbit/s${m3.belastet ? ` · ${t3("belastet")}` : ""}` : null)}
    <div class="gruppe"><span class="gr-ic">📶</span>${t3("Mobilfunk")}</div>
    ${k2.mobil_quelle === "modem" ? z2(t3("Werte von"), k2.modem_modell || t3("vorgeschaltetes Modem")) : A}
    ${z2(t3("Netz"), k2.netz ? b2`<span class="badge ${k2.netz.startsWith("5G") ? "blau-b" : ""}">${k2.netz}</span>` : null)}
    ${z2(t3("Ankerzelle · Sendeanlage"), k2.zelle ? [k2.zelle, k2.anlage && t3("Anlage {anlage}", { anlage: k2.anlage })].filter(Boolean).join(" · ") : null)}
    ${z2(t3("RSRP · RSRQ Anker"), k2.rsrp != null ? [dbm(k2.rsrp), dbm(k2.rsrq, "dB")].filter(Boolean).join(" · ") : null)}
    ${z2("5G", k2.nr_aktiv === false ? t3("aus") : k2.nr_aktiv ? [t3("aktiv"), k2.nr_pci != null && `PCI ${k2.nr_pci}`, dbm(k2.nr_rsrp), dbm(k2.nr_rsrq, "dB")].filter(Boolean).join(" · ") : null)}
    ${k2.band || k2.sinr != null || k2.nr_band || k2.nr_sinr != null ? z2(t3("Band · SINR"), [k2.band, k2.sinr != null && `${zahl(k2.sinr, 1)} dB`, k2.nr_band, k2.nr_sinr != null && `5G ${zahl(k2.nr_sinr, 1)} dB`].filter(Boolean).join(" · ")) : A}
    ${z2(t3("Entfernung laut Box"), k2.entfernung_m ? `${zahl(k2.entfernung_m / 1e3, 1)} km` : null)}
    ${z2(t3("Nachbarzellen"), k2.nachbarzellen)}
    ${z2(t3("Netz · Gebiet"), mit(k2.plmn, k2.tac && `TAC ${k2.tac}`))}
    ${z2(t3("Verbunden seit"), dauer(k2.verbunden_s))}
    ${z2(t3("Geschätzter Mast"), k2.mast_m ? `${zahl(k2.mast_m / 1e3, 1)} km ${k2.mast_richtung || ""}`.trim() : null)}
    <div class="gruppe"><span class="gr-ic">📦</span>Box</div>
    ${z2(t3("Modell · Firmware"), k2.box_modell ? [k2.box_modell, k2.box_firmware].filter(Boolean).join(" · ") : null)}
    ${z2(t3("Läuft seit"), dauer(k2.box_laufzeit_s))}
    ${z2(t3("Eingeschaltete Bänder"), k2.baender)}
    <div class="gruppe"><span class="gr-ic">🏠</span>Heimnetz</div>
    ${z2(t3("Geräte online · davon WLAN"), k2.online != null ? `${k2.online}${k2.online_wlan != null ? ` · ${k2.online_wlan}` : ""}` : null)}
    <div class="gruppe"><span class="gr-ic">🌦️</span>${t3("Umgebung")}</div>
    ${z2(t3("Wetter"), k2.wetter ? [WETTER[k2.wetter] ? t3(WETTER[k2.wetter]) : k2.wetter, k2.temperatur != null && `${zahl(k2.temperatur, 1)} °C`, k2.feuchte != null && t3("{n} % Feuchte", { n: zahl(k2.feuchte) }), k2.wolken != null && t3("{n} % Wolken", { n: zahl(k2.wolken) })].filter(Boolean).join(" · ") : null)}
    ${z2(t3("Tag"), TAGESART[k2.tagesart] && t3(TAGESART[k2.tagesart]))}
    <p class="hinweis" style="margin-top:10px">${k2.mobil_quelle === "modem" ? t3("Funkwerte vom vorgeschalteten Modem – was es nicht liefert, fehlt.") : t3("Nicht verfügbar über die Schnittstelle der Box: genutztes Band, SINR, Bandbreite, MIMO, Carrier Aggregation.")}</p>
    ${loeschenTeil(p4, m3)}`;
}
function loeschenTeil(p4, m3) {
  const hinweis = b2`<p class="hinweis" style="margin-top:6px">${t3("Löschen dürfen nur Admins.")}</p>`;
  if (!p4.istAdmin) return hinweis;
  const b3 = p4._blatt;
  const teil = b3.frage ? b2`<div class="mg-frage"><b>${t3("Messung {zeit} löschen?", { zeit: zeit(m3.t) })}</b><br>${t3("Sie verschwindet aus Raster, Tagesverlauf, Auswertung und dieser Liste. Der Verlauf der Ookla-Entitäten in Home Assistant bleibt. Das lässt sich nicht rückgängig machen.")}
      ${b3.fehler ? b2`<p class="fein">${t3("Nicht gelöscht: {fehler}", { fehler: b3.fehler })}</p>` : A}
      <div class="dg-knoepfe" style="margin-top:10px"><button class="rot" ?disabled=${b3.loescht} @click=${() => p4.messungLoeschen()}>${b3.loescht ? t3("löscht …") : t3("Löschen")}</button>
        <button ?disabled=${b3.loescht} @click=${() => p4.messungFrage(false)}>${t3("Abbrechen")}</button></div></div>` : b2`<button class="mg-loeschen" @click=${() => p4.messungFrage(true)}>🗑 ${t3("Messung löschen")}</button>`;
  return b2`${teil}${hinweis}`;
}
var BELASTET_KURZ = { aus: merke("zählt nicht"), halb: merke("zählt ¼"), mit: merke("belastet") };
function kachelPopup(p4) {
  const k2 = p4._kachel, o7 = p4._opt.speedtest, d3 = k2.daten, TAGE2 = wochentage(true);
  const kopf = b2`<div class="kp-kopf"><b>${TAGE2[k2.tag]} ${stunden(k2.stunde)} · ${GROESSE_NAME[o7.groesse]}</b>
    ${k2.fest ? b2`<button class="zu-k" title=${t3("Schließen")} @click=${() => p4.kachelWeg(true)}>✕</button>` : b2`<span class="leise">${zeitraum(o7.tage)}</span>`}</div>`;
  const inhalt = k2.fehler ? b2`<div class="kp-werte">${t3("Nicht abrufbar: {fehler}", { fehler: k2.fehler })}</div>` : !d3 ? b2`<div class="kp-werte">${t3("lädt …")}</div>` : b2`<div class="kp-werte">Median <b>${zahl(d3.median, 1)} ${d3.einheit}</b> · ${t3("niedrigste {min} · höchste {max}", { min: zahl(d3.min, 1), max: zahl(d3.max, 1) })} · ${t3("{n} gezählt", { n: d3.anzahl })}${d3.belastet ? ` · ${t3("{n} belastet", { n: d3.belastet })} (${t3(BELASTET_KURZ[o7.grundlast])})` : ""}</div>
      <div class="kp-liste"><table class="t"><tr><th>${t3("Wann")}</th><th>Server</th><th class="r">${d3.einheit}</th><th>${t3("Netz")}</th><th class="r">Signal</th><th class="r">${t3("Grundlast")}</th><th></th></tr>
        ${d3.messungen.map((m3) => b2`<tr class=${m3.gewicht ? "" : "belastet"}><td>${zeit(m3.t)}</td><td>${m3.server ?? "–"}</td><td class="r">${zahl(m3.wert)}</td>
          <td>${m3.netz ?? "–"}</td><td class="r">${m3.rsrp != null ? zahl(m3.rsrp) : "–"}</td>
          <td class="r">${zahl(m3.last, 1)}</td><td>${m3.belastet ? b2`<span class="badge amber-b">${t3(BELASTET_KURZ[o7.grundlast])}</span>` : A}</td></tr>`)}
      </table></div>${d3.weitere ? b2`<div class="leise">${t3("… und {n} ältere", { n: d3.weitere })}</div>` : A}`;
  return b2`<div class="kpop glas-panel ${k2.fest ? "fest" : ""}" role="dialog" aria-label=${`${t3("Messungen")} ${TAGE2[k2.tag]} ${stunden(k2.stunde)}`}>${kopf}${inhalt}</div>`;
}
var WOCHENTAGE = [
  merke("alle Montage"),
  merke("alle Dienstage"),
  merke("alle Mittwoche"),
  merke("alle Donnerstage"),
  merke("alle Freitage"),
  merke("alle Samstage"),
  merke("alle Sonntage")
];
var GROESSE_NAME = { down: "Download", up: "Upload", ping: "Ping" };
function datumText(iso, vorTagen) {
  const d3 = /* @__PURE__ */ new Date(`${iso}T12:00`);
  return `${datum(d3)}${vorTagen === 0 ? ` (${t3("heute")})` : vorTagen === 1 ? ` (${t3("gestern")})` : ""}`;
}
function tagesverlauf(p4, d3) {
  const o7 = p4._opt.speedtest, v2 = d3.verlauf, ein = d3.einheit;
  const offen2 = o7.datum || o7.tag != null;
  const wahl = b2`<div class="leiste">
    ${seg(wochentage(true).map((x3, i6) => [i6, x3]), o7.datum ? null : o7.tag, (i6) => p4.setze("speedtest", { tag: i6, datum: null, stunde: null }))}
    <select style="font-size:12px;padding:5px 8px" @change=${(e6) => p4.setze("speedtest", { datum: e6.target.value || null, tag: null, stunde: null })}>
      <option value="" ?selected=${!o7.datum}>${t3("oder Datum …")}</option>
      ${d3.tage_liste.map((x3) => b2`<option value=${x3.datum} ?selected=${o7.datum === x3.datum}>${datumText(x3.datum, x3.vor_tagen)} · ${t3(x3.anzahl === 1 ? "{n} Messung" : "{n} Messungen", { n: x3.anzahl })}</option>`)}
      ${o7.datum && !d3.tage_liste.some((x3) => x3.datum === o7.datum) ? b2`<option value=${o7.datum} selected>${datumText(o7.datum)} · ${t3("keine Messung")}</option>` : A}
    </select>
    ${offen2 ? b2`<button class="chip glas-panel" title=${t3("Verlauf schließen")} @click=${() => p4.setze("speedtest", { tag: null, datum: null, stunde: null })}>✕</button>` : A}
  </div>`;
  if (!offen2) {
    return b2`<div class="tv"><div class="gruppe">${t3("Tagesverlauf")}</div>${wahl}
      <p class="hinweis">${t3("Tipp auf einen Wochentag (auch links im Raster) oder wähle ein Datum: Median je Stunde, dazu die niedrigste und höchste Messung.")}</p></div>`;
  }
  if (!v2 || (o7.datum ? v2.datum !== o7.datum : v2.tag !== o7.tag)) {
    return b2`<div class="tv"><div class="gruppe">${t3("Tagesverlauf")}</div>${wahl}<div class="leer">${p4._laedt ? t3("lädt …") : t3("Verlauf nicht geladen.")}</div></div>`;
  }
  const s4 = v2.stunden, mit = s4.map((x3, h3) => [h3, x3]).filter(([, x3]) => x3.anzahl);
  const titel = o7.datum ? datumText(o7.datum, d3.tage_liste.find((x3) => x3.datum === o7.datum)?.vor_tagen) : `${t3(WOCHENTAGE[o7.tag])} · ${zeitraum(o7.tage)}`;
  const kopf = b2`<div class="gruppe">${t3("Tagesverlauf")} · ${GROESSE_NAME[d3.groesse]} · ${titel}</div>`;
  if (!mit.length) return b2`<div class="tv">${kopf}${wahl}<div class="leer">${t3("An diesem Tag keine gezählte Messung.")}</div></div>`;
  const W3 = 720, H4 = 230, L4 = 40, R2 = 10, O = 14, U = 26, B2 = W3 - L4 - R2, HH = H4 - O - U, sw = B2 / 24;
  const tarif = d3.groesse !== "ping" ? d3.tarif : null;
  const ymax = Math.ceil(Math.max(tarif || 0, ...mit.map(([, x3]) => x3.max)) * 1.08 / 10) * 10 || 10;
  const x2 = (h3) => L4 + (h3 + 0.5) * sw, y4 = (w2) => O + HH - w2 / ymax * HH;
  const stuecke = (ok) => {
    const out = [];
    let cur = [];
    s4.forEach((w2, h3) => {
      if (w2.anzahl && ok(w2)) cur.push(h3);
      else {
        if (cur.length) out.push(cur);
        cur = [];
      }
    });
    if (cur.length) out.push(cur);
    return out;
  };
  const band = stuecke((w2) => w2.max > w2.min).map((st2) => {
    const b3 = st2.length === 1 ? 5 : 0;
    const oben = st2.map((h3, i6) => `${x2(h3) - (i6 === 0 ? b3 : 0)},${y4(s4[h3].max)}${st2.length === 1 ? ` ${x2(h3) + b3},${y4(s4[h3].max)}` : ""}`);
    const unten = [...st2].reverse().map((h3, i6) => `${x2(h3) + (i6 === 0 ? b3 : 0)},${y4(s4[h3].min)}${st2.length === 1 ? ` ${x2(h3) - b3},${y4(s4[h3].min)}` : ""}`);
    return w`<path class="band" d=${`M${[...oben, ...unten].join(" L")} Z`}></path>`;
  });
  const alle = mit.map(([h3, w2]) => `${x2(h3)},${y4(w2.median)}`).join(" ");
  const glatt = [];
  let lauf = [];
  s4.forEach((w2, h3) => {
    if (w2.glatt != null) lauf.push(`${x2(h3)},${y4(w2.glatt)}`);
    else {
      if (lauf.length > 1) glatt.push(lauf);
      lauf = [];
    }
  });
  if (lauf.length > 1) glatt.push(lauf);
  const linien = stuecke(() => true).filter((st2) => st2.length > 1).map((st2) => w`<polyline class="med" points=${st2.map((h3) => `${x2(h3)},${y4(s4[h3].median)}`).join(" ")}></polyline>`);
  const st = o7.stunde, gew = st != null ? s4[st] : null;
  const anzahl2 = (n4) => t3(n4 === 1 ? "{n} Messung" : "{n} Messungen", { n: n4 });
  const info = st != null ? gew.anzahl ? b2`<b>${stunden(st)}:</b> Median <b>${zahl(gew.median)} ${ein}</b>${gew.anzahl > 1 ? ` · ${t3("niedrigste {min} · höchste {max}", { min: zahl(gew.min), max: zahl(gew.max) })}` : ""} · ${anzahl2(gew.anzahl)}${gew.glatt != null ? ` · ${t3("geglättet {wert}", { wert: zahl(gew.glatt) })}` : ""}` : b2`<b>${stunden(st)}:</b> ${t3("keine Messung")}` : b2`<span class="leise">${v2.beste != null ? `${t3("Beste Stunde {stunde} ({wert})", { stunde: stunden(v2.beste), wert: `${zahl(s4[v2.beste].median)} ${ein}` })} · ${t3("schwächste {stunde} ({wert})", { stunde: stunden(v2.schwaechste), wert: `${zahl(s4[v2.schwaechste].median)} ${ein}` })} · ` : ""}${t3("Tipp auf eine Stunde zeigt die Werte")}</span>`;
  return b2`<div class="tv">${kopf}${wahl}
    <svg viewBox="0 0 ${W3} ${H4}" role="img" aria-label=${`${t3("Tagesverlauf")} ${GROESSE_NAME[d3.groesse]}`}>
      ${[0, 0.25, 0.5, 0.75, 1].map((f3) => w`<line class="gitter" x1=${L4} x2=${W3 - R2} y1=${y4(ymax * f3)} y2=${y4(ymax * f3)}></line><text x=${L4 - 6} y=${y4(ymax * f3) + 4} text-anchor="end">${zahl(ymax * f3)}</text>`)}
      ${tarif ? w`<line class="tarif" x1=${L4} x2=${W3 - R2} y1=${y4(tarif)} y2=${y4(tarif)}></line><text x=${W3 - R2 - 4} y=${y4(tarif) - 5} text-anchor="end">${t3("Tarif {wert}", { wert: zahl(tarif) })}</text>` : A}
      ${st != null ? w`<rect class="wahl" x=${L4 + st * sw} y=${O} width=${sw} height=${HH} rx="3"></rect>` : A}
      ${band}
      ${mit.length > 1 ? w`<polyline class="med luecke" points=${alle}></polyline>` : A}
      ${linien}
      ${glatt.map((l4) => w`<polyline class="glatt" points=${l4.join(" ")}></polyline>`)}
      ${mit.map(([h3, w2]) => w`<circle class="pkt" cx=${x2(h3)} cy=${y4(w2.median)} r=${st === h3 ? 5 : 3}></circle>`)}
      ${[0, 3, 6, 9, 12, 15, 18, 21].map((h3) => w`<text x=${L4 + h3 * sw} y=${H4 - 8} text-anchor="middle">${h3}</text>`)}
      ${w`<text x=${W3 - R2} y=${H4 - 8} text-anchor="end">${t3("{n} Uhr", { n: 24 })}</text>`}
      ${s4.map((w2, h3) => w`<rect class="h" x=${L4 + h3 * sw} y=${O} width=${sw} height=${HH} @click=${() => p4.setze("speedtest", { stunde: st === h3 ? null : h3 }, false)}><title>${stunden(h3)}: ${w2.anzahl ? `Median ${zahl(w2.median)} ${ein} · ${zahl(w2.min)}–${zahl(w2.max)} · ${anzahl2(w2.anzahl)}` : t3("keine Messung")}</title></rect>`)}
    </svg>
    <div class="info">${info}</div>
    <div class="legende"><span><i class="l-med"></i>${t3("Median je Stunde")}</span><span><i class="l-glatt"></i>${t3("Mittelwert geglättet (3 h)")}</span><span><i class="l-band"></i>${t3("niedrigste bis höchste Messung")}</span><span><i class="l-luecke"></i>${t3("Stunden ohne Messung überbrückt")}</span>${tarif ? b2`<span><i class="l-tarif"></i>${t3("Tarif")}</span>` : A}<span>${ein}</span></div>
    ${o7.datum ? b2`<p class="hinweis">${t3("Ein einzelner Tag hat meist nur wenige Messungen (Messplan) – Stunden ohne Messung bleiben leer, bei einer Messung gibt es kein Band.")}</p>` : A}
  </div>`;
}

// node_modules/lit-html/directive.js
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
var t4 = { ATTRIBUTE: 1, CHILD: 2, PROPERTY: 3, BOOLEAN_ATTRIBUTE: 4, EVENT: 5, ELEMENT: 6 };
var e4 = (t7) => (...e6) => ({ _$litDirective$: t7, values: e6 });
var i5 = class {
  constructor(t7) {
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  _$AT(t7, e6, i6) {
    this._$Ct = t7, this._$AM = e6, this._$Ci = i6;
  }
  _$AS(t7, e6) {
    return this.update(t7, e6);
  }
  update(t7, e6) {
    return this.render(...e6);
  }
};

// node_modules/lit-html/directive-helpers.js
/**
 * @license
 * Copyright 2020 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
var { I: t5 } = j;
var r4 = (o7) => void 0 === o7.strings;
var m2 = {};
var p3 = (o7, t7 = m2) => o7._$AH = t7;

// node_modules/lit-html/directives/live.js
/**
 * @license
 * Copyright 2020 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
var l3 = e4(class extends i5 {
  constructor(r5) {
    if (super(r5), r5.type !== t4.PROPERTY && r5.type !== t4.ATTRIBUTE && r5.type !== t4.BOOLEAN_ATTRIBUTE) throw Error("The `live` directive is not allowed on child or event bindings");
    if (!r4(r5)) throw Error("`live` bindings can only contain a single expression");
  }
  render(r5) {
    return r5;
  }
  update(i6, [t7]) {
    if (t7 === E || t7 === A) return t7;
    const o7 = i6.element, l4 = i6.name;
    if (i6.type === t4.PROPERTY) {
      if (t7 === o7[l4]) return E;
    } else if (i6.type === t4.BOOLEAN_ATTRIBUTE) {
      if (!!t7 === o7.hasAttribute(l4)) return E;
    } else if (i6.type === t4.ATTRIBUTE && o7.getAttribute(l4) === t7 + "") return E;
    return p3(i6), t7;
  }
});

// src/ansichten/wlan.js
function wlan(p4, d3) {
  if (!d3.verfuegbar) return b2`<div class="glas-panel block"><div class="leer">${t3("Die Box meldet gerade keine WLAN-Werte.")}</div></div>`;
  const band = (b3) => kachel(
    `${b3.band} GHz`,
    b3.an ? t3("Kanal {k}", { k: b3.kanal ?? "–" }) : t3("aus"),
    b3.an ? `${b3.auto ? t3("automatisch") : t3("fest")}${b3.standard ? ` · Wi-Fi ${standard(b3.standard)}` : ""} · ${t3(b3.geraete === 1 ? "{n} Gerät" : "{n} Geräte", { n: b3.geraete })}` : t3("abgeschaltet")
  );
  return b2`
    ${d3.befunde.length ? b2`<div class="glas-panel block">${d3.befunde.map((b3) => b2`<div class="befund"><span class="punkt ${punkt(b3.stufe)}"></span>
      <div><b>${b3.titel}</b><p>${b3.text}</p></div></div>`)}</div>` : A}
    <div class="glas-raster">
      ${d3.baender.map(band)}
      ${kachel(t3("Gast-WLAN"), d3.gast_an == null ? "–" : d3.gast_an ? t3("an") : t3("aus"), t3("nur lesen"))}
    </div>
    <div class="glas-panel block">
      <div class="block-kopf"><h3>${t3("Geräte im WLAN")}</h3><span class="leise">${t3("{n} verbunden · schwächstes zuerst", { n: d3.geraete.length })}</span></div>
      ${d3.geraete.length ? b2`<div class="tab-scroll"><table class="t">
        <tr><th>${t3("Gerät")}</th><th>Band</th><th>${t3("Empfang")}</th><th class="r">%</th><th class="r">Mbit/s</th></tr>
        ${d3.geraete.map((g2) => b2`<tr class="klick" @click=${() => p4.geraetOeffnen(g2.id)}>
          <td>${g2.name} ${g2.schwach ? b2`<span class="badge amber-b">${t3("schwach")}</span>` : A}${g2.gast ? b2` <span class="badge">${t3("Gast")}</span>` : A}</td>
          <td>${g2.band ? `${g2.band} GHz` : "–"}</td>
          <td><span class="sig"><i style="width:${Math.round((g2.lage ?? 0) * 100)}%;background:${farbe(g2.lage)}"></i></span></td>
          <td class="r">${g2.signal ?? "–"}</td><td class="r">${g2.mbit ?? "–"}</td></tr>`)}
      </table></div>` : b2`<div class="leer">${t3("Kein Gerät im WLAN.")}</div>`}
      <p class="hinweis">${t3("Empfang und Geschwindigkeit meldet die FRITZ!Box je Gerät; schwach = unter {n} % (⚙). Tippen öffnet den Verlauf des Geräts.", { n: d3.schwach_unter })}</p>
    </div>
    <div class="glas-panel block"><div class="block-kopf"><h3>${t3("Kanalwechsel")}</h3><span class="leise">${t3("letzte 7 Tage · die Box wählt selbst")}</span></div>
      ${d3.kanalwechsel.length ? d3.kanalwechsel.map((k2) => b2`<div class="ereig"><span class="punkt grau"></span><time>${zeit(k2.t)}</time><span>${k2.text}</span></div>`) : b2`<div class="leer">${t3("Kein Wechsel in den letzten 7 Tagen.")}</div>`}
    </div>`;
}
function standard(s4) {
  return { be: "7", ax: "6", ac: "5", n: "4" }[s4] ?? s4;
}

// src/ansichten/warnungen.js
var anzahl = (n4) => t3(n4 === 1 ? "{n} Gerät" : "{n} Geräte", { n: n4 });
var schalter = (an, klick) => b2`<button class="sw ${an ? "on" : ""}" role="switch" aria-checked=${an ? "true" : "false"} @click=${klick}><i></i></button>`;
var nurAdmin = (text) => b2`<p class="hinweis" style="padding-top:8px">${text}</p>`;
function artFormular({ symbol = "🏷️", name = "", platz, knopf, los, weg }) {
  const werte = (ev) => {
    const z2 = ev.target.closest(".art-form");
    return [z2.querySelector("[name=art-ic]").value, z2.querySelector("[name=art-name]").value];
  };
  return b2`<div class="ez art-form"><input name="art-ic" class="art-ic" maxlength="8" .value=${symbol} title=${t3("Symbol")} aria-label=${t3("Symbol")}>
    <input name="art-name" class="art-name" maxlength="30" .value=${name} placeholder=${platz}>
    <button class="knopf haupt" @click=${(ev) => los(...werte(ev))}>${knopf}</button><button class="leise" title=${t3("Abbrechen")} @click=${weg}>✕</button></div>`;
}
function artenTeil(p4) {
  if (!p4.istAdmin) return nurAdmin(t3("Eigene Arten legen nur Admins an."));
  const a3 = p4._daten.arten, b3 = p4._blatt;
  if (!a3) return p4._hinweisArten ? b2`<p class="fein">${p4._hinweisArten}</p>` : b2`<div class="leer">${t3("lädt …")}</div>`;
  const stelle = (werte) => {
    p4._blatt = { ...p4._blatt, artBearb: null, artLoe: null, artNeu: false, ...werte };
  };
  const eigen = a3.eigene.map((x2) => b3.artBearb === x2.name ? artFormular({ symbol: x2.symbol, name: x2.titel, knopf: t3("Speichern"), los: (s4, n4) => p4.artAendern(x2.name, s4, n4), weg: () => stelle({}) }) : b2`<div class="ez" data-art=${x2.name}><span>${x2.text}<small>${t3("eigene · {anzahl}", { anzahl: anzahl(x2.geraete) })}</small></span>
        <span class="art-k"><button class="leise blau" @click=${() => stelle({ artBearb: x2.name })}>${t3("✎ ändern")}</button><button class="leise rot-t" title=${t3("löschen")} @click=${() => stelle({ artLoe: x2.name })}>🗑</button></span></div>
      ${b3.artLoe === x2.name ? b2`<div class="mg-frage" style="margin:4px 0 8px"><b>${t3("„{text}“ löschen?", { text: x2.text })}</b><br>${t3(x2.geraete === 1 ? "{n} Gerät bekommt wieder die automatisch erkannte Art; Warnungen für diese Art fallen weg." : "{n} Geräte bekommen wieder die automatisch erkannte Art; Warnungen für diese Art fallen weg.", { n: x2.geraete })}
        <div class="dg-knoepfe" style="margin-top:8px"><button class="rot" @click=${() => p4.artLoeschen(x2.name)}>${t3("Löschen")}</button><button @click=${() => stelle({})}>${t3("Abbrechen")}</button></div></div>` : A}`);
  const neu = b3.artNeu ? artFormular({ platz: t3("Name, z. B. Werkstatt"), knopf: t3("Anlegen"), los: (s4, n4) => p4.artNeu(s4, n4), weg: () => stelle({}) }) : b2`<div class="dg-knoepfe" style="margin-top:4px"><button class="art-neu" ?disabled=${a3.eigene.length >= a3.hoechstens} @click=${() => stelle({ artNeu: true })}>${t3("＋ Neue Art")}</button></div>`;
  return b2`<div class="vs-stufe"><span>${t3("Eigene Arten")}</span><span>${a3.eigene.length}</span></div>
    ${a3.eigene.length ? eigen : b2`<p class="hinweis">${t3("noch keine")}</p>`}${neu}
    ${p4._hinweisArten ? b2`<p class="fein">${p4._hinweisArten}</p>` : A}
    <p class="hinweis" style="margin-top:6px">${t3("Zuordnen im Fenster eines Geräts (Reiter Geräte → Gerät antippen → Art). Eigene Arten gelten wie die festen: unter Geräte › nach Art und in ⚙ › 🔔 Warnungen.")}</p>
    <div class="vs-stufe"><span>${t3("Feste Arten")}</span><span>${a3.feste.length}</span></div>
    ${a3.feste.map((x2) => b2`<div class="ez"><span>${x2.text}<small>${t3("fest · {anzahl}", { anzahl: anzahl(x2.geraete) })}</small></span><span class="leise">${t3("automatisch erkannt")}</span></div>`)}`;
}
function warnungenTeil(p4) {
  if (!p4.istAdmin) return nurAdmin(t3("Warnungen stellen nur Admins ein."));
  const w2 = p4._daten.warnungen;
  if (!w2) return p4._hinweisWarn ? b2`<p class="fein">${p4._hinweisWarn}</p>` : b2`<div class="leer">${t3("lädt …")}</div>`;
  const setzen = (werte) => p4.warnungenSetzen(werte);
  const letzte = w2.verzoegerungen.length - 1;
  return b2`
    <div class="ez"><span>${t3("Nachricht an")}<small>${t3("notify-Dienst von Home Assistant")}</small></span>
      <select class="ga-wahl w-ziel" .value=${l3(w2.ziel)} @change=${(e6) => setzen({ ziel: e6.target.value })}>
        ${w2.ziele.map((z2) => b2`<option value=${z2.name} ?selected=${z2.name === w2.ziel}>${z2.text}</option>`)}</select></div>
    ${w2.ziel_fehlt ? b2`<div class="befund"><span class="punkt amber"></span><div><b>${t3("Dienst fehlt")}</b><p>${t3("Den gewählten notify-Dienst gibt es gerade nicht – Warnungen kommen nur als Ereignis und ins Journal.")}</p></div></div>` : A}
    <div class="ez"><span>${t3("Offline melden nach")}<small>${t3("so lange muss ein Gerät weg sein")}</small></span>${seg(w2.verzoegerungen.map((m3, i6) => [m3, i6 === letzte ? `${m3} min` : String(m3)]), w2.verzoegerung, (v2) => setzen({ verzoegerung: v2 }))}</div>
    <div class="dg-knoepfe" style="margin:2px 0 4px"><button class="w-test" @click=${() => p4.testnachricht()}>${t3("🔔 Testnachricht senden")}</button></div>
    ${p4._hinweisWarn ? b2`<p class="fein">${p4._hinweisWarn}</p>` : A}
    <div class="vs-stufe"><span>${t3("Überwachen nach Art")}</span><span>${t3("{n} von {gesamt} Geräten", { n: w2.ueberwacht, gesamt: w2.gesamt })}</span></div>
    ${w2.arten.map((a3) => b2`<div class="ez" data-art=${a3.name}><span>${a3.text}<small>${a3.hinweis || anzahl(a3.geraete)}</small></span>${schalter(a3.an, () => setzen({ art: a3.name, an: !a3.an }))}</div>`)}
    <div class="vs-stufe"><span>${t3("Einzeln abweichend")}</span><span>${w2.ausnahmen.length}</span></div>
    ${w2.ausnahmen.length ? w2.ausnahmen.map((x2) => b2`<div class="ez" data-ausnahme=${x2.id}><span>${x2.name}<small>${x2.wert === "immer" ? t3("wird immer gemeldet – abweichend von der Gruppe") : t3("wird nie gemeldet – abweichend von der Gruppe")}</small></span>
      <button class="leise blau" title=${t3("zurücksetzen")} @click=${() => p4.warnungGeraet(x2.id, "gruppe")}>✕</button></div>`) : b2`<p class="hinweis">${t3("keine")}</p>`}
    <p class="hinweis">${t3("Einzelne Geräte stellst du im Fenster des Geräts um (Reiter Geräte → Gerät antippen).")}</p>
    <div class="vs-stufe"><span>${t3("Außerdem melden")}</span><span></span></div>
    <div class="ez" data-schalter="wieder"><span>${t3("Wieder online")}<small>${t3("mit Dauer, nur wenn vorher gemeldet")}</small></span>${schalter(w2.wieder, () => setzen({ wieder: !w2.wieder }))}</div>
    <div class="ez" data-schalter="neu"><span>${t3("Neues unbekanntes Gerät")}<small>${t3("sobald sich ein noch nie gesehenes Gerät verbindet")}</small></span>${schalter(w2.neu, () => setzen({ neu: !w2.neu }))}</div>
    <div class="ez" data-schalter="internet"><span>${t3("Internet oder FRITZ!Box weg")}<small>${t3("kommt an, sobald es wieder geht – mit Dauer des Ausfalls")}</small></span>${schalter(w2.internet, () => setzen({ internet: !w2.internet }))}</div>
    <div class="vs-kopf" style="margin-top:8px"><span class="leise">${t3("Beispiel")}</span><br><b>Heimnetz</b> · ${w2.beispiel}</div>
    <p class="hinweis" style="margin-top:6px">${t3("Nachrichten an die Companion App laufen über den Push-Dienst von Google bzw. Apple – der Gerätename verlässt dabei das Heimnetz. Für jede Meldung gibt es zusätzlich das Ereignis „heimnetz_warnung“ für eigene Automationen.")}</p>`;
}

// src/ansichten/geraete.js
var TEILE = [["geraete", merke("Geräte")], ["wlan", merke("WLAN")]];
function geraeteReiter(p4, d3) {
  const teil = p4._opt.geraete.teil;
  return b2`<div class="leiste">${seg(tl(TEILE), teil, (v2) => p4.setze("geraete", { teil: v2 }), false)}</div>
    ${!d3 ? b2`<div class="glas-panel block"><div class="leer">${t3("lädt …")}</div></div>` : teil === "wlan" ? wlan(p4, d3) : geraete(p4, d3)}`;
}
var FILTER = [["alle", merke("Alle")], ["online", "Online"], ["offline", "Offline"], ["auff", merke("Auffällig")]];
var PUNKT = { an: ["", "online"], aus: ["grau", "offline"], neu: ["blau", merke("neu")], wackelt: ["amber", merke("wackelt")] };
var ZU = "WLAN, nicht verbunden";
var NACH = [["verb", merke("nach Verbindung")], ["art", merke("nach Art")]];
var SYMBOL = { LAN: "🔌", WLAN: "📶", Powerline: "⚡" };
var WARNEN = [["gruppe", merke("wie Gruppe")], ["immer", merke("immer")], ["nie", merke("nie")]];
var NEU = "neu";
function passt(g2, filter, suche) {
  if (filter === "online" && !g2.aktiv) return false;
  if (filter === "offline" && g2.aktiv) return false;
  if (filter === "auff" && !["neu", "wackelt"].includes(g2.einstufung)) return false;
  return !suche || `${g2.name} ${g2.ip}`.toLowerCase().includes(suche.toLowerCase());
}
function geraete(p4, d3) {
  const o7 = p4._opt.geraete;
  const liste = d3.geraete.filter((g2) => passt(g2, o7.filter, o7.suche));
  const nachArt = o7.nach === "art";
  return b2`<div class="glas-panel block">
    <div class="block-kopf"><h3>${t3("Geräte im Heimnetz")}</h3><span class="leise">${t3("{n} von {gesamt} online · letzte 24 h", { n: d3.online, gesamt: d3.bekannt })}</span></div>
    <div class="leiste">${seg(tl(NACH), o7.nach || "verb", (v2) => p4.setze("geraete", { nach: v2 }, false))}</div>
    <div class="leiste">${seg(tl(FILTER), o7.filter, (v2) => p4.setze("geraete", { filter: v2 }, false))}
      <input class="suche" placeholder=${t3("Suchen (Name oder IP)")} .value=${o7.suche} @input=${(e6) => p4.setze("geraete", { suche: e6.target.value }, false)}></div>
    ${!d3.box_erreichbar ? b2`<p class="fein">${t3("Die FRITZ!Box antwortet nicht – die Liste zeigt den letzten bekannten Stand.")}</p>` : A}
    ${liste.length ? (nachArt ? d3.gruppen_art || [] : d3.gruppen || []).map((gr) => gruppe(p4, gr, liste.filter((g2) => (nachArt ? g2.kat : g2.verbindung) === gr.name), nachArt)) : b2`<div class="leer">${t3("Kein Gerät passt.")}</div>`}
    <div class="gk-achse"><span></span><div class="achse"><span>${t3("vor {n} h", { n: 24 })}</span><span>${t3("jetzt")}</span></div></div>
    <p class="hinweis">${t3("Punkt: grün online, grau offline, amber wackelt, blau neu. Streifen: grün = im Heimnetz, schraffiert = keine Aufzeichnung. Das WLAN-Band kennt die Box nur bei verbundenen Geräten. „🔐 VPN (WireGuard)“ sind Geräte, die sich von unterwegs über VPN mit deiner Box verbinden. Tippen öffnet den Verlauf.")}</p>
  </div>`;
}
function gruppe(p4, gr, geraete2, nachArt) {
  if (!geraete2.length) return A;
  const zu = p4._opt.geraete.zu || [ZU];
  const offen2 = !zu.includes(gr.name);
  const umschalten = (e6) => {
    e6.preventDefault();
    p4.setze("geraete", { zu: offen2 ? [...zu, gr.name] : zu.filter((n4) => n4 !== gr.name) }, false);
  };
  return b2`<details class="ggr" ?open=${offen2}><summary @click=${umschalten}><span>${gr.text || gr.name}</span><span>${t3("{n} von {gesamt} online", { n: gr.online, gesamt: gr.gesamt })} ${offen2 ? "▾" : "▸"}</span></summary>
    ${offen2 ? geraete2.map((g2) => zeile(p4, g2, nachArt)) : A}</details>`;
}
function zeile(p4, g2, nachArt) {
  const [farbe2, schluessel] = PUNKT[g2.einstufung] ?? ["grau", g2.einstufung];
  const wort = t3(schluessel);
  const zusatz = nachArt ? g2.band || g2.art : g2.band;
  return b2`<div class="geraet gk" @click=${() => p4.geraetOeffnen(g2.id)}>
    <span>${SYMBOL[g2.art.split(" ")[0]] ?? "•"}</span>
    <span class="n">${g2.name}<small>${g2.ip || "–"}${zusatz ? ` · ${zusatz}` : ""}</small></span>
    ${streifen(g2.streifen)}<span class="punkt ${farbe2}" title=${wort} aria-label=${wort}></span></div>`;
}
function geraetBlatt(p4, b3) {
  const kopf = b2`<div class="griff"></div><button class="zu" @click=${() => p4.zu()}>✕</button>`;
  if (b3.laedt) return b2`${kopf}<div class="leer">${t3("lädt …")}</div>`;
  if (b3.fehler) return b2`${kopf}<p class="fein">${b3.fehler}</p>`;
  const g2 = b3.daten;
  return b2`${kopf}
    <h3>${g2.name}</h3>
    <div class="leise">${g2.ip || "–"} · ${g2.art} · ${t3("Adresse {quelle}", { quelle: g2.quelle })}${g2.zufallsadresse ? ` · ${t3("Zufalls-Adresse")}` : ""}${g2.zuerst ? ` · ${t3("zuerst gesehen {tag}", { tag: tag(g2.zuerst) })}` : ""}</div>
    ${g2.kategorien ? b2`<div class="zeile ga-zeile"><span>${t3("Art")} <span class="leise">· ${g2.art_quelle}</span></span>${p4.istAdmin ? b2`<select class="ga-wahl" .value=${l3(g2.art_selbst ? g2.kat : "auto")} @change=${(e6) => {
    if (e6.target.value !== NEU) {
      p4.geraetArt(g2.id, e6.target.value === "auto" ? null : e6.target.value);
      return;
    }
    p4._blatt = { ...b3, eigenNeu: true };
  }}>
          <option value="auto">${t3("automatisch")}</option>
          ${g2.kategorien.map((k2) => b2`<option value=${k2.name}>${k2.text}</option>`)}
          <option value=${NEU}>${t3("＋ eigene Art …")}</option></select>` : b2`<span class="leise">${(g2.kategorien.find((k2) => k2.name === g2.kat) || {}).text || g2.kat}</span>`}</div>` : A}
    ${b3.eigenNeu && p4.istAdmin ? b2`${artFormular({ platz: t3("Name der Art, z. B. Baustelle"), knopf: t3("Anlegen"), los: (s4, n4) => p4.artNeu(s4, n4, g2.id), weg: () => {
    p4._blatt = { ...b3, eigenNeu: false };
  } })}
      <p class="hinweis">${t3("Eigene Arten erscheinen unter Geräte › nach Art und in ⚙ › Warnungen; umbenennen und löschen unter ⚙ › 🏷️ Arten.")}</p>` : A}
    ${g2.warnen ? warnZeile(p4, g2) : A}
    <div class="glas-raster" style="grid-template-columns:repeat(3,1fr)">
      <div class="glas-panel block" style="padding:10px"><span class="glas-klein">${t3("online 7 Tage")}</span><span class="glas-wert">${g2.online_anteil == null ? "–" : zahl(g2.online_anteil * 100)}<small> %</small></span></div>
      <div class="glas-panel block" style="padding:10px"><span class="glas-klein">${t3("Abbrüche")}</span><span class="glas-wert">${g2.abbrueche}</span></div>
      <div class="glas-panel block" style="padding:10px"><span class="glas-klein">${t3("jetzt")}</span><span class="glas-wert" style="font-size:18px">${g2.aktiv ? "online" : "offline"}</span></div>
    </div>
    <div class="gruppe">${t3("Letzte 7 Tage")}</div>
    ${g2.tage.map((x2) => b2`<div style="display:flex;gap:10px;align-items:center;font-size:12px"><span class="leise" style="width:66px">${tag(x2.tag)}</span>${streifen(x2.streifen)}</div>`)}
    <div class="achse" style="padding-left:76px"><span>0</span><span>6</span><span>12</span><span>18</span><span>24</span></div>
    <div class="gruppe">${t3("Ereignisse")}</div>
    ${g2.ereignisse.length ? g2.ereignisse.map((e6) => b2`<div class="ereig"><span class="punkt ${punkt(e6.stufe)}"></span><time>${zeit(e6.t)}</time><span>${e6.text}</span></div>`) : b2`<div class="leer">${t3("Keine Ereignisse in den letzten 7 Tagen.")}</div>`}`;
}
function warnZeile(p4, g2) {
  const w2 = g2.warnen;
  const unter = w2.wert !== "gruppe" ? t3("eigene Einstellung") : w2.gruppe ? t3("wie Gruppe (an)") : t3("wie Gruppe (aus)");
  const wort = { gruppe: w2.gruppe ? t3("wie Gruppe (an)") : t3("wie Gruppe (aus)"), immer: t3("immer"), nie: t3("nie") }[w2.wert];
  return b2`<div class="zeile ga-zeile ga-warnen"><span>${t3("🔔 Bei offline warnen")} <span class="leise">· ${unter}</span></span>${p4.istAdmin ? seg(tl(WARNEN), w2.wert, (v2) => v2 !== w2.wert && p4.warnungGeraet(g2.id, v2)) : b2`<span class="leise">${wort}</span>`}</div>`;
}

// src/karte.js
var import_leaflet = __toESM(require_leaflet(), 1);

// src/leaflet-stil.js
var leaflet_stil_default = String.raw`/* required styles */

.leaflet-pane,
.leaflet-tile,
.leaflet-marker-icon,
.leaflet-marker-shadow,
.leaflet-tile-container,
.leaflet-pane > svg,
.leaflet-pane > canvas,
.leaflet-zoom-box,
.leaflet-image-layer,
.leaflet-layer {
	position: absolute;
	left: 0;
	top: 0;
	}
.leaflet-container {
	overflow: hidden;
	}
.leaflet-tile,
.leaflet-marker-icon,
.leaflet-marker-shadow {
	-webkit-user-select: none;
	   -moz-user-select: none;
	        user-select: none;
	  -webkit-user-drag: none;
	}
/* Prevents IE11 from highlighting tiles in blue */
.leaflet-tile::selection {
	background: transparent;
}
/* Safari renders non-retina tile on retina better with this, but Chrome is worse */
.leaflet-safari .leaflet-tile {
	image-rendering: -webkit-optimize-contrast;
	}
/* hack that prevents hw layers "stretching" when loading new tiles */
.leaflet-safari .leaflet-tile-container {
	width: 1600px;
	height: 1600px;
	-webkit-transform-origin: 0 0;
	}
.leaflet-marker-icon,
.leaflet-marker-shadow {
	display: block;
	}
/* .leaflet-container svg: reset svg max-width decleration shipped in Joomla! (joomla.org) 3.x */
/* .leaflet-container img: map is broken in FF if you have max-width: 100% on tiles */
.leaflet-container .leaflet-overlay-pane svg {
	max-width: none !important;
	max-height: none !important;
	}
.leaflet-container .leaflet-marker-pane img,
.leaflet-container .leaflet-shadow-pane img,
.leaflet-container .leaflet-tile-pane img,
.leaflet-container img.leaflet-image-layer,
.leaflet-container .leaflet-tile {
	max-width: none !important;
	max-height: none !important;
	width: auto;
	padding: 0;
	}

.leaflet-container img.leaflet-tile {
	/* See: https://bugs.chromium.org/p/chromium/issues/detail?id=600120 */
	mix-blend-mode: plus-lighter;
}

.leaflet-container.leaflet-touch-zoom {
	-ms-touch-action: pan-x pan-y;
	touch-action: pan-x pan-y;
	}
.leaflet-container.leaflet-touch-drag {
	-ms-touch-action: pinch-zoom;
	/* Fallback for FF which doesn't support pinch-zoom */
	touch-action: none;
	touch-action: pinch-zoom;
}
.leaflet-container.leaflet-touch-drag.leaflet-touch-zoom {
	-ms-touch-action: none;
	touch-action: none;
}
.leaflet-container {
	-webkit-tap-highlight-color: transparent;
}
.leaflet-container a {
	-webkit-tap-highlight-color: rgba(51, 181, 229, 0.4);
}
.leaflet-tile {
	filter: inherit;
	visibility: hidden;
	}
.leaflet-tile-loaded {
	visibility: inherit;
	}
.leaflet-zoom-box {
	width: 0;
	height: 0;
	-moz-box-sizing: border-box;
	     box-sizing: border-box;
	z-index: 800;
	}
/* workaround for https://bugzilla.mozilla.org/show_bug.cgi?id=888319 */
.leaflet-overlay-pane svg {
	-moz-user-select: none;
	}

.leaflet-pane         { z-index: 400; }

.leaflet-tile-pane    { z-index: 200; }
.leaflet-overlay-pane { z-index: 400; }
.leaflet-shadow-pane  { z-index: 500; }
.leaflet-marker-pane  { z-index: 600; }
.leaflet-tooltip-pane   { z-index: 650; }
.leaflet-popup-pane   { z-index: 700; }

.leaflet-map-pane canvas { z-index: 100; }
.leaflet-map-pane svg    { z-index: 200; }

.leaflet-vml-shape {
	width: 1px;
	height: 1px;
	}
.lvml {
	behavior: url(#default#VML);
	display: inline-block;
	position: absolute;
	}


/* control positioning */

.leaflet-control {
	position: relative;
	z-index: 800;
	pointer-events: visiblePainted; /* IE 9-10 doesn't have auto */
	pointer-events: auto;
	}
.leaflet-top,
.leaflet-bottom {
	position: absolute;
	z-index: 1000;
	pointer-events: none;
	}
.leaflet-top {
	top: 0;
	}
.leaflet-right {
	right: 0;
	}
.leaflet-bottom {
	bottom: 0;
	}
.leaflet-left {
	left: 0;
	}
.leaflet-control {
	float: left;
	clear: both;
	}
.leaflet-right .leaflet-control {
	float: right;
	}
.leaflet-top .leaflet-control {
	margin-top: 10px;
	}
.leaflet-bottom .leaflet-control {
	margin-bottom: 10px;
	}
.leaflet-left .leaflet-control {
	margin-left: 10px;
	}
.leaflet-right .leaflet-control {
	margin-right: 10px;
	}


/* zoom and fade animations */

.leaflet-fade-anim .leaflet-popup {
	opacity: 0;
	-webkit-transition: opacity 0.2s linear;
	   -moz-transition: opacity 0.2s linear;
	        transition: opacity 0.2s linear;
	}
.leaflet-fade-anim .leaflet-map-pane .leaflet-popup {
	opacity: 1;
	}
.leaflet-zoom-animated {
	-webkit-transform-origin: 0 0;
	    -ms-transform-origin: 0 0;
	        transform-origin: 0 0;
	}
svg.leaflet-zoom-animated {
	will-change: transform;
}

.leaflet-zoom-anim .leaflet-zoom-animated {
	-webkit-transition: -webkit-transform 0.25s cubic-bezier(0,0,0.25,1);
	   -moz-transition:    -moz-transform 0.25s cubic-bezier(0,0,0.25,1);
	        transition:         transform 0.25s cubic-bezier(0,0,0.25,1);
	}
.leaflet-zoom-anim .leaflet-tile,
.leaflet-pan-anim .leaflet-tile {
	-webkit-transition: none;
	   -moz-transition: none;
	        transition: none;
	}

.leaflet-zoom-anim .leaflet-zoom-hide {
	visibility: hidden;
	}


/* cursors */

.leaflet-interactive {
	cursor: pointer;
	}
.leaflet-grab {
	cursor: -webkit-grab;
	cursor:    -moz-grab;
	cursor:         grab;
	}
.leaflet-crosshair,
.leaflet-crosshair .leaflet-interactive {
	cursor: crosshair;
	}
.leaflet-popup-pane,
.leaflet-control {
	cursor: auto;
	}
.leaflet-dragging .leaflet-grab,
.leaflet-dragging .leaflet-grab .leaflet-interactive,
.leaflet-dragging .leaflet-marker-draggable {
	cursor: move;
	cursor: -webkit-grabbing;
	cursor:    -moz-grabbing;
	cursor:         grabbing;
	}

/* marker & overlays interactivity */
.leaflet-marker-icon,
.leaflet-marker-shadow,
.leaflet-image-layer,
.leaflet-pane > svg path,
.leaflet-tile-container {
	pointer-events: none;
	}

.leaflet-marker-icon.leaflet-interactive,
.leaflet-image-layer.leaflet-interactive,
.leaflet-pane > svg path.leaflet-interactive,
svg.leaflet-image-layer.leaflet-interactive path {
	pointer-events: visiblePainted; /* IE 9-10 doesn't have auto */
	pointer-events: auto;
	}

/* visual tweaks */

.leaflet-container {
	background: #ddd;
	outline-offset: 1px;
	}
.leaflet-container a {
	color: #0078A8;
	}
.leaflet-zoom-box {
	border: 2px dotted #38f;
	background: rgba(255,255,255,0.5);
	}


/* general typography */
.leaflet-container {
	font-family: "Helvetica Neue", Arial, Helvetica, sans-serif;
	font-size: 12px;
	font-size: 0.75rem;
	line-height: 1.5;
	}


/* general toolbar styles */

.leaflet-bar {
	box-shadow: 0 1px 5px rgba(0,0,0,0.65);
	border-radius: 4px;
	}
.leaflet-bar a {
	background-color: #fff;
	border-bottom: 1px solid #ccc;
	width: 26px;
	height: 26px;
	line-height: 26px;
	display: block;
	text-align: center;
	text-decoration: none;
	color: black;
	}
.leaflet-bar a,
.leaflet-control-layers-toggle {
	background-position: 50% 50%;
	background-repeat: no-repeat;
	display: block;
	}
.leaflet-bar a:hover,
.leaflet-bar a:focus {
	background-color: #f4f4f4;
	}
.leaflet-bar a:first-child {
	border-top-left-radius: 4px;
	border-top-right-radius: 4px;
	}
.leaflet-bar a:last-child {
	border-bottom-left-radius: 4px;
	border-bottom-right-radius: 4px;
	border-bottom: none;
	}
.leaflet-bar a.leaflet-disabled {
	cursor: default;
	background-color: #f4f4f4;
	color: #bbb;
	}

.leaflet-touch .leaflet-bar a {
	width: 30px;
	height: 30px;
	line-height: 30px;
	}
.leaflet-touch .leaflet-bar a:first-child {
	border-top-left-radius: 2px;
	border-top-right-radius: 2px;
	}
.leaflet-touch .leaflet-bar a:last-child {
	border-bottom-left-radius: 2px;
	border-bottom-right-radius: 2px;
	}

/* zoom control */

.leaflet-control-zoom-in,
.leaflet-control-zoom-out {
	font: bold 18px 'Lucida Console', Monaco, monospace;
	text-indent: 1px;
	}

.leaflet-touch .leaflet-control-zoom-in, .leaflet-touch .leaflet-control-zoom-out  {
	font-size: 22px;
	}


/* layers control */

.leaflet-control-layers {
	box-shadow: 0 1px 5px rgba(0,0,0,0.4);
	background: #fff;
	border-radius: 5px;
	}
.leaflet-control-layers-toggle {
	background-image: url(images/layers.png);
	width: 36px;
	height: 36px;
	}
.leaflet-retina .leaflet-control-layers-toggle {
	background-image: url(images/layers-2x.png);
	background-size: 26px 26px;
	}
.leaflet-touch .leaflet-control-layers-toggle {
	width: 44px;
	height: 44px;
	}
.leaflet-control-layers .leaflet-control-layers-list,
.leaflet-control-layers-expanded .leaflet-control-layers-toggle {
	display: none;
	}
.leaflet-control-layers-expanded .leaflet-control-layers-list {
	display: block;
	position: relative;
	}
.leaflet-control-layers-expanded {
	padding: 6px 10px 6px 6px;
	color: #333;
	background: #fff;
	}
.leaflet-control-layers-scrollbar {
	overflow-y: scroll;
	overflow-x: hidden;
	padding-right: 5px;
	}
.leaflet-control-layers-selector {
	margin-top: 2px;
	position: relative;
	top: 1px;
	}
.leaflet-control-layers label {
	display: block;
	font-size: 13px;
	font-size: 1.08333em;
	}
.leaflet-control-layers-separator {
	height: 0;
	border-top: 1px solid #ddd;
	margin: 5px -10px 5px -6px;
	}

/* Default icon URLs */
.leaflet-default-icon-path { /* used only in path-guessing heuristic, see L.Icon.Default */
	background-image: url(images/marker-icon.png);
	}


/* attribution and scale controls */

.leaflet-container .leaflet-control-attribution {
	background: #fff;
	background: rgba(255, 255, 255, 0.8);
	margin: 0;
	}
.leaflet-control-attribution,
.leaflet-control-scale-line {
	padding: 0 5px;
	color: #333;
	line-height: 1.4;
	}
.leaflet-control-attribution a {
	text-decoration: none;
	}
.leaflet-control-attribution a:hover,
.leaflet-control-attribution a:focus {
	text-decoration: underline;
	}
.leaflet-attribution-flag {
	display: inline !important;
	vertical-align: baseline !important;
	width: 1em;
	height: 0.6669em;
	}
.leaflet-left .leaflet-control-scale {
	margin-left: 5px;
	}
.leaflet-bottom .leaflet-control-scale {
	margin-bottom: 5px;
	}
.leaflet-control-scale-line {
	border: 2px solid #777;
	border-top: none;
	line-height: 1.1;
	padding: 2px 5px 1px;
	white-space: nowrap;
	-moz-box-sizing: border-box;
	     box-sizing: border-box;
	background: rgba(255, 255, 255, 0.8);
	text-shadow: 1px 1px #fff;
	}
.leaflet-control-scale-line:not(:first-child) {
	border-top: 2px solid #777;
	border-bottom: none;
	margin-top: -2px;
	}
.leaflet-control-scale-line:not(:first-child):not(:last-child) {
	border-bottom: 2px solid #777;
	}

.leaflet-touch .leaflet-control-attribution,
.leaflet-touch .leaflet-control-layers,
.leaflet-touch .leaflet-bar {
	box-shadow: none;
	}
.leaflet-touch .leaflet-control-layers,
.leaflet-touch .leaflet-bar {
	border: 2px solid rgba(0,0,0,0.2);
	background-clip: padding-box;
	}


/* popup */

.leaflet-popup {
	position: absolute;
	text-align: center;
	margin-bottom: 20px;
	}
.leaflet-popup-content-wrapper {
	padding: 1px;
	text-align: left;
	border-radius: 12px;
	}
.leaflet-popup-content {
	margin: 13px 24px 13px 20px;
	line-height: 1.3;
	font-size: 13px;
	font-size: 1.08333em;
	min-height: 1px;
	}
.leaflet-popup-content p {
	margin: 17px 0;
	margin: 1.3em 0;
	}
.leaflet-popup-tip-container {
	width: 40px;
	height: 20px;
	position: absolute;
	left: 50%;
	margin-top: -1px;
	margin-left: -20px;
	overflow: hidden;
	pointer-events: none;
	}
.leaflet-popup-tip {
	width: 17px;
	height: 17px;
	padding: 1px;

	margin: -10px auto 0;
	pointer-events: auto;

	-webkit-transform: rotate(45deg);
	   -moz-transform: rotate(45deg);
	    -ms-transform: rotate(45deg);
	        transform: rotate(45deg);
	}
.leaflet-popup-content-wrapper,
.leaflet-popup-tip {
	background: white;
	color: #333;
	box-shadow: 0 3px 14px rgba(0,0,0,0.4);
	}
.leaflet-container a.leaflet-popup-close-button {
	position: absolute;
	top: 0;
	right: 0;
	border: none;
	text-align: center;
	width: 24px;
	height: 24px;
	font: 16px/24px Tahoma, Verdana, sans-serif;
	color: #757575;
	text-decoration: none;
	background: transparent;
	}
.leaflet-container a.leaflet-popup-close-button:hover,
.leaflet-container a.leaflet-popup-close-button:focus {
	color: #585858;
	}
.leaflet-popup-scrolled {
	overflow: auto;
	}

.leaflet-oldie .leaflet-popup-content-wrapper {
	-ms-zoom: 1;
	}
.leaflet-oldie .leaflet-popup-tip {
	width: 24px;
	margin: 0 auto;

	-ms-filter: "progid:DXImageTransform.Microsoft.Matrix(M11=0.70710678, M12=0.70710678, M21=-0.70710678, M22=0.70710678)";
	filter: progid:DXImageTransform.Microsoft.Matrix(M11=0.70710678, M12=0.70710678, M21=-0.70710678, M22=0.70710678);
	}

.leaflet-oldie .leaflet-control-zoom,
.leaflet-oldie .leaflet-control-layers,
.leaflet-oldie .leaflet-popup-content-wrapper,
.leaflet-oldie .leaflet-popup-tip {
	border: 1px solid #999;
	}


/* div icon */

.leaflet-div-icon {
	background: #fff;
	border: 1px solid #666;
	}


/* Tooltip */
/* Base styles for the element that has a tooltip */
.leaflet-tooltip {
	position: absolute;
	padding: 6px;
	background-color: #fff;
	border: 1px solid #fff;
	border-radius: 3px;
	color: #222;
	white-space: nowrap;
	-webkit-user-select: none;
	-moz-user-select: none;
	-ms-user-select: none;
	user-select: none;
	pointer-events: none;
	box-shadow: 0 1px 3px rgba(0,0,0,0.4);
	}
.leaflet-tooltip.leaflet-interactive {
	cursor: pointer;
	pointer-events: auto;
	}
.leaflet-tooltip-top:before,
.leaflet-tooltip-bottom:before,
.leaflet-tooltip-left:before,
.leaflet-tooltip-right:before {
	position: absolute;
	pointer-events: none;
	border: 6px solid transparent;
	background: transparent;
	content: "";
	}

/* Directions */

.leaflet-tooltip-bottom {
	margin-top: 6px;
}
.leaflet-tooltip-top {
	margin-top: -6px;
}
.leaflet-tooltip-bottom:before,
.leaflet-tooltip-top:before {
	left: 50%;
	margin-left: -6px;
	}
.leaflet-tooltip-top:before {
	bottom: 0;
	margin-bottom: -12px;
	border-top-color: #fff;
	}
.leaflet-tooltip-bottom:before {
	top: 0;
	margin-top: -12px;
	margin-left: -6px;
	border-bottom-color: #fff;
	}
.leaflet-tooltip-left {
	margin-left: -6px;
}
.leaflet-tooltip-right {
	margin-left: 6px;
}
.leaflet-tooltip-left:before,
.leaflet-tooltip-right:before {
	top: 50%;
	margin-top: -6px;
	}
.leaflet-tooltip-left:before {
	right: 0;
	margin-right: -12px;
	border-left-color: #fff;
	}
.leaflet-tooltip-right:before {
	left: 0;
	margin-left: -12px;
	border-right-color: #fff;
	}

/* Printing */

@media print {
	/* Prevent printers from removing background-images of controls. */
	.leaflet-control {
		-webkit-print-color-adjust: exact;
		print-color-adjust: exact;
		}
	}
`;

// src/karte.js
var L3 = import_leaflet.default.noConflict();
var BASEMAP = (ebene) => `https://mapsneu.wien.gv.at/basemap/${ebene}/normal/google3857/{z}/{y}/{x}.png`;
var QUELLE_BASEMAP = () => `${t3("Grundkarte")}: <a href="https://basemap.at" target="_blank" rel="noopener">basemap.at</a>`;
var GRUNDLAGEN = {
  bmap: { url: BASEMAP("geolandbasemap"), quelle: QUELLE_BASEMAP },
  grau: { url: BASEMAP("bmapgrau"), quelle: QUELLE_BASEMAP },
  osm: {
    url: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
    quelle: () => `© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>${t3("-Mitwirkende")}`
  }
};
var WAHL = { auto: merke("Automatisch"), bmap: "basemap.at", grau: merke("basemap.at grau"), osm: "OpenStreetMap" };
var SPEICHER = "heimnetz.karte.grundlage";
var SPEICHER_OSM = "heimnetz.karte.osm";
var lesen = (schluessel) => localStorage.getItem(schluessel) ?? localStorage.getItem(schluessel.replace(/^heimnetz\./, "netzwerk."));
var QUELLE_OSM_MASTEN = () => `${t3("Masten")} © <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>${t3("-Mitwirkende")}`;
var NAH = 15;
var FARBEN = { blau: ["--blau", "#64a8ff"], amber: ["--amber", "#ff9f0a"], grau: ["--ink2", "#8e8e93"], ring: ["--ink", "#ffffff"] };
function osmGemerkt() {
  try {
    return lesen(SPEICHER_OSM) !== "aus";
  } catch {
    return true;
  }
}
function gemerkt() {
  try {
    const w2 = lesen(SPEICHER);
    return Object.hasOwn(WAHL, w2 ?? "") ? w2 : "auto";
  } catch {
    return "auto";
  }
}
var sicher = (t7) => String(t7 ?? "").replace(/[&<>"']/g, (c4) => `&#${c4.charCodeAt(0)};`);
function grundlage(wahl, dunkel) {
  if (wahl === "auto") return { ...GRUNDLAGEN[dunkel ? "grau" : "bmap"], abdunkeln: dunkel };
  return { ...Object.hasOwn(GRUNDLAGEN, wahl) ? GRUNDLAGEN[wahl] : GRUNDLAGEN.bmap, abdunkeln: false };
}
var HeimnetzKarte = class extends i4 {
  // `sprache` nur, damit die Karte bei einem Wechsel der Sprache neu beschriftet
  static properties = { daten: { attribute: false }, dunkel: { type: Boolean }, sprache: { attribute: false }, _wahl: { state: true }, _osm: { state: true }, _voll: { state: true }, _info: { state: true } };
  static styles = [r(leaflet_stil_default), i`
    :host { display: block; }
    .rahmen { position: relative; border-radius: 16px; overflow: hidden; }
    #karte { width: 100%; aspect-ratio: 15 / 8; min-height: 240px; background: rgba(127,127,127,.15); }
    .kachel-dunkel { filter: invert(1) hue-rotate(180deg) brightness(.9) contrast(.9); }
    .k-zoom { position: absolute; left: 10px; top: 10px; z-index: 500; display: flex; flex-direction: column; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,.3); }
    /* deckend: auf heller wie dunkler Grundlage gut lesbar */
    .k-zoom button { width: 34px; height: 34px; border: 0; font: inherit; font-size: 18px; cursor: pointer; background: rgba(28,28,30,.88); color: #fff; }
    .k-zoom button + button { border-top: 1px solid rgba(255,255,255,.18); }
    /* Vollbild: über die ganze Seite (Fullscreen-API, sonst fest über dem Fenster) */
    .rahmen.voll, .rahmen:fullscreen { position: fixed; inset: 0; z-index: 9999; border-radius: 0; background: #111; }
    .rahmen.voll #karte, .rahmen:fullscreen #karte { aspect-ratio: auto; height: 100%; min-height: 0; }
    .k-voll-zu { position: absolute; left: 50%; transform: translateX(-50%); top: 10px; z-index: 600; font: inherit; font-size: 14px; padding: 6px 14px; border-radius: 10px; border: 1px solid rgba(255,255,255,.18); background: rgba(28,28,30,.88); color: #fff; cursor: pointer; }
    .k-info { position: absolute; left: 10px; right: 10px; bottom: 26px; z-index: 600; display: flex; flex-direction: column; gap: 3px; padding: 10px 36px 10px 12px; border-radius: 12px; background: rgba(28,28,30,.92); color: #fff; font-size: 13px; }
    .k-info .leise { color: rgba(255,255,255,.65); } .k-info .passt { color: var(--amber, #ff9f0a); }
    .k-info-zu { position: absolute; right: 6px; top: 4px; background: none; border: 0; color: #fff; font-size: 16px; cursor: pointer; }
    .osm-dreieck { cursor: pointer; }
    .k-osm { position: absolute; right: 10px; top: 48px; z-index: 500; font: inherit; font-size: 13px; padding: 6px 10px; border-radius: 10px; border: 1px solid rgba(255,255,255,.18); background: rgba(28,28,30,.88); color: rgba(255,255,255,.6); cursor: pointer; }
    .k-osm.an { color: #fff; border-color: var(--amber, #ff9f0a); }
    .osm-dreieck { position: relative; width: 16px; height: 15px; background: #8e8e93; clip-path: polygon(50% 0, 100% 100%, 0 100%); }
    .osm-dreieck.passt { width: 22px; height: 20px; background: var(--amber, #ff9f0a); }
    .osm-dreieck.passt::after { content: ''; position: absolute; inset: 4px 4px 2px; background: #8e8e93; clip-path: polygon(50% 0, 100% 100%, 0 100%); }
    .k-lage { position: absolute; right: 10px; top: 10px; z-index: 500; font: inherit; font-size: 13px; padding: 6px 8px; border-radius: 10px; border: 1px solid rgba(255,255,255,.18); background: rgba(28,28,30,.88); color: #fff; }
    /* Beschriftungen als Tooltips: Leaflet legt sie selbst links oder rechts, je nachdem wo Platz ist */
    .leaflet-tooltip.k-name { background: none; border: 0; box-shadow: none; padding: 0 14px; font-size: 13px; font-weight: 600; color: #fff; white-space: nowrap; text-shadow: 0 0 3px rgba(0,0,0,.9), 0 0 2px rgba(0,0,0,.9); }
    .leaflet-tooltip.k-name::before { display: none; }
    .leaflet-tooltip.k-name.klein { font-size: 11px; font-weight: 500; padding: 0 8px; }
    /* Zellnamen erst beim Hineinzoomen – weiter weg liegen sie aufeinander */
    .leaflet-container:not(.nah) .leaflet-tooltip.klein { display: none; }
    .leaflet-container { font: inherit; }
    .leaflet-control-attribution { font-size: 10px; }
  `];
  constructor() {
    super();
    this._wahl = gemerkt();
    this._osm = osmGemerkt();
    this._voll = false;
    this._info = null;
    this._karte = null;
    this._gezeigt = false;
  }
  render() {
    const info = this._osm && this._info !== null ? this.daten?.osm?.[this._info] : null;
    return b2`<div class="rahmen ${this._voll ? "voll" : ""}">
      ${this._voll ? b2`<button class="k-voll-zu" title=${t3("Vollbild schließen")} @click=${() => this._vollbild(false)}>✕</button>` : ""}
      <div id="karte" role="img" aria-label=${t3("Karte: Wohnung, Zellen und geschätzter Mast")}></div>
      <div class="k-zoom">
        <button title=${t3("Näher")} aria-label=${t3("Näher")} @click=${() => this._karte?.zoomIn()}>＋</button>
        <button title=${t3("Weiter weg")} aria-label=${t3("Weiter weg")} @click=${() => this._karte?.zoomOut()}>−</button>
        <button title=${t3("Alles zeigen")} aria-label=${t3("Alles zeigen")} @click=${() => this._alles()}>⌖</button>
        <button title=${this._voll ? t3("Vollbild schließen") : t3("Vollbild")} aria-label=${t3("Vollbild")} @click=${() => this._vollbild(!this._voll)}>⛶</button>
      </div>
      ${this.daten?.osm?.length ? b2`<button class="k-osm ${this._osm ? "an" : ""}" title=${t3("Funkmasten aus OpenStreetMap ein/aus")} aria-pressed=${this._osm ? "true" : "false"} @click=${() => this._osmUmschalten()}>📡 ${t3("Masten (OSM)")}</button>` : ""}
      ${info ? this._infofeld(info) : ""}
      <select class="k-lage" title=${t3("Kartengrundlage")} @change=${(e6) => this._waehlen(e6.target.value)}>
        ${Object.entries(WAHL).map(([k2, name]) => b2`<option value=${k2} ?selected=${k2 === this._wahl}>🗺️ ${t3(name)}</option>`)}
      </select>
    </div>`;
  }
  willUpdate(geaendert) {
    if (geaendert.has("daten") && JSON.stringify(this.daten?.osm || []) !== this._osmText) this._info = null;
  }
  updated(geaendert) {
    const neu = !this._karte && this._anlegen();
    if (!this._karte) return;
    const sprache2 = geaendert.has("sprache") && geaendert.get("sprache") !== void 0;
    if (neu || sprache2 || geaendert.has("_wahl") || geaendert.has("dunkel")) this._grundlage();
    if (neu || sprache2 || geaendert.has("daten") || geaendert.has("dunkel")) this._zeichnen();
    const osmText = JSON.stringify(this.daten?.osm || []);
    if (neu || sprache2 || geaendert.has("_osm") || geaendert.has("_wahl") || osmText !== this._osmText) {
      this._osmText = osmText;
      this._osmZeichnen();
    }
    this._erstesMal();
  }
  /** Den Rahmen der Integration zeigen, sobald Daten da sind und die Karte eine Größe hat (sonst zeigt Leaflet die
   *  ganze Welt); danach bleibt die Ansicht des Nutzers, bis er ⌖ drückt. */
  _erstesMal() {
    const ziel = this.renderRoot.querySelector("#karte");
    if (this._gezeigt || !this.daten || !ziel || !ziel.clientWidth) return;
    this._karte.invalidateSize();
    this._alles();
    this._gezeigt = true;
  }
  disconnectedCallback() {
    super.disconnectedCallback();
    document.removeEventListener("fullscreenchange", this._vollAus);
    document.removeEventListener("keydown", this._esc);
    if (document.fullscreenElement && this.renderRoot.contains(document.fullscreenElement)) document.exitFullscreen?.().catch(() => {
    });
    this._voll = false;
    this._info = null;
    this._beobachter?.disconnect();
    this._karte?.remove();
    this._karte = this._kacheln = this._ebene = this._osmEbene = this._osmText = this._osmQuelle = null;
    this._gezeigt = false;
  }
  connectedCallback() {
    super.connectedCallback();
    this._vollAus ??= () => {
      if (!document.fullscreenElement && this._voll) {
        this._voll = false;
        this.updateComplete.then(() => this._karte?.invalidateSize());
      }
    };
    document.addEventListener("fullscreenchange", this._vollAus);
    this._esc ??= (e6) => {
      if (e6.key === "Escape" && this._voll) this._vollbild(false);
    };
    document.addEventListener("keydown", this._esc);
    if (this.hasUpdated) this.requestUpdate();
  }
  _anlegen() {
    const ziel = this.renderRoot.querySelector("#karte");
    if (!ziel) return false;
    this._karte = L3.map(ziel, { zoomControl: false, attributionControl: true });
    this._karte.attributionControl.setPrefix('<a href="https://leafletjs.com" target="_blank" rel="noopener">Leaflet</a>');
    L3.control.scale({ imperial: false, position: "bottomleft" }).addTo(this._karte);
    this._karte.createPane("osm").style.zIndex = 350;
    this._osmEbene = L3.layerGroup().addTo(this._karte);
    this._ebene = L3.layerGroup().addTo(this._karte);
    this._karte.on("zoomend", () => this._nah());
    if (typeof ResizeObserver !== "undefined") {
      this._beobachter = new ResizeObserver(() => {
        this._karte?.invalidateSize();
        this._erstesMal();
      });
      this._beobachter.observe(ziel);
    }
    return true;
  }
  _grundlage() {
    const g2 = grundlage(this._wahl, this.dunkel);
    this._kacheln?.remove();
    this._kacheln = L3.tileLayer(g2.url, { maxZoom: 19, attribution: g2.quelle(), className: g2.abdunkeln ? "kachel-dunkel" : "" }).addTo(this._karte);
  }
  _waehlen(wahl) {
    this._wahl = wahl;
    try {
      localStorage.setItem(SPEICHER, wahl);
    } catch {
    }
  }
  /** Infofeld zu einem angetippten Mast (Werte kommen fertig von der Integration). */
  _infofeld(o7) {
    const zu = () => {
      this._info = null;
    };
    return b2`<div class="k-info" role="dialog" aria-label=${t3("Funkmast")}>
      <button class="k-info-zu" title=${t3("Schließen")} aria-label=${t3("Schließen")} @click=${zu}>✕</button>
      <b>${t3("Funkmast")} (OpenStreetMap)${o7.betreiber ? ` · ${o7.betreiber}` : ""}${o7.passt ? b2` · <span class="passt">${o7.warum === "lage" ? t3("am nächsten am geschätzten Mast") : t3("passt zur Entfernung laut Box")}</span>` : ""}</b>
      <span class="leise">${t3("{entfernung} {richtung} von der Wohnung", { entfernung: o7.entfernung, richtung: o7.richtung })}</span>
      ${o7.anbieter ? b2`<span>📶 ${o7.anbieter.join(" · ")}${o7.technik?.length ? ` · ${o7.technik.join(" · ")}` : ""}</span>
          <span class="leise">${t3(o7.zellen === 1 ? "laut OpenCellID: {n} Zelle in höchstens 500 m – geschätzt, nicht amtlich" : "laut OpenCellID: {n} Zellen in höchstens 500 m – geschätzt, nicht amtlich", { n: o7.zellen })}</span>` : b2`<span class="leise">${t3("Anbieter und Technik unbekannt – OpenCellID kennt hier keine Zellen (oder es ist kein Schlüssel eingetragen). Im Senderkataster nachsehen.")}</span>`}
    </div>`;
  }
  /** Vollbild über die Fullscreen-API; wo sie fehlt (z. B. iPhone), fest über dem Fenster. */
  async _vollbild(an) {
    const rahmen = this.renderRoot.querySelector(".rahmen");
    this._voll = an;
    try {
      if (an && rahmen?.requestFullscreen && !document.fullscreenElement) await rahmen.requestFullscreen();
      else if (!an && document.fullscreenElement) await document.exitFullscreen();
    } catch {
    }
    await this.updateComplete;
    this._karte?.invalidateSize();
  }
  _osmUmschalten() {
    this._osm = !this._osm;
    if (!this._osm) this._info = null;
    try {
      localStorage.setItem(SPEICHER_OSM, this._osm ? "an" : "aus");
    } catch {
    }
    this.dispatchEvent(new CustomEvent("osm-umgeschaltet", { detail: this._osm, bubbles: true, composed: true }));
  }
  /** Funkmasten aus OpenStreetMap: graue Dreiecke, der passende orange umrandet und beschriftet. */
  _osmZeichnen() {
    const e6 = this._osmEbene, liste = this.daten?.osm || [];
    if (!e6) return;
    e6.clearLayers();
    if (this._osmQuelle) this._karte.attributionControl.removeAttribution(this._osmQuelle);
    this._osmQuelle = null;
    if (!this._osm || !liste.length) return;
    if (grundlage(this._wahl, this.dunkel).url !== GRUNDLAGEN.osm.url) {
      this._osmQuelle = QUELLE_OSM_MASTEN();
      this._karte.attributionControl.addAttribution(this._osmQuelle);
    }
    for (const [i6, o7] of liste.entries()) {
      const gross = o7.passt ? [22, 20] : [16, 15];
      const m3 = L3.marker(o7.ort, {
        keyboard: false,
        zIndexOffset: o7.passt ? 100 : 0,
        pane: "osm",
        title: t3("Funkmast – antippen für Infos"),
        icon: L3.divIcon({ className: "", html: `<div class="osm-dreieck${o7.passt ? " passt" : ""}"></div>`, iconSize: gross, iconAnchor: [gross[0] / 2, gross[1] / 2] })
      }).addTo(e6);
      m3.on("click", () => {
        this._info = this._info === i6 ? null : i6;
      });
      if (o7.passt) {
        m3.bindTooltip(sicher(`${t3("Funkmast")} (OSM) · ${o7.entfernung} ${o7.richtung} · ${t3("passt")}`), {
          permanent: true,
          direction: "auto",
          className: "k-name",
          interactive: false
        });
      }
    }
  }
  /** ⌖ und beim ersten Öffnen: der Rahmen der Integration (Ring, Masten, nahe Zellen). */
  _alles() {
    const d3 = this.daten;
    if (!this._karte || !d3?.rahmen) return;
    const [s4, w2, n4, o7] = d3.rahmen;
    this._karte.fitBounds([[s4, w2], [n4, o7]]);
  }
  /** Zellnamen erst ab Zoomstufe NAH (sonst liegen sie aufeinander). */
  _nah() {
    this._karte?.getContainer().classList.toggle("nah", this._karte.getZoom() >= NAH);
  }
  _zeichnen() {
    const d3 = this.daten, e6 = this._ebene;
    if (!e6) return;
    e6.clearLayers();
    if (!d3 || !d3.wohnung) return;
    const stil2 = getComputedStyle(this);
    const f3 = Object.fromEntries(Object.entries(FARBEN).map(([k2, [v2, ersatz2]]) => [k2, stil2.getPropertyValue(v2).trim() || ersatz2]));
    const name = (lage, text, klein, richtung = "auto") => lage.bindTooltip(sicher(text), {
      permanent: true,
      direction: richtung,
      offset: [0, richtung === "top" ? -10 : 0],
      // Abstand zur Seite: Rand im CSS (Leaflet zieht den Versatz links ab)
      className: `k-name${klein ? " klein" : ""}`,
      interactive: false
    });
    if (d3.ring_m) L3.circle(d3.wohnung, { radius: d3.ring_m, color: f3.ring, weight: 1.5, opacity: 0.7, dashArray: "6 6", fill: false, interactive: false }).addTo(e6);
    for (const p4 of d3.punkte) {
      const c4 = p4.anker ? f3.blau : f3.grau;
      if (p4.genau_m) L3.circle(p4.ort, { radius: p4.genau_m, color: c4, weight: 1, opacity: 0.6, dashArray: "3 4", fillColor: c4, fillOpacity: 0.08, interactive: false }).addTo(e6);
      name(L3.circleMarker(p4.ort, { radius: 5, color: "#fff", weight: 1.5, fillColor: c4, fillOpacity: 1, interactive: false }).addTo(e6), p4.name, true);
    }
    for (const m3 of d3.masten) {
      L3.polyline([d3.wohnung, m3.ort], { color: f3.amber, weight: 3, interactive: false }).addTo(e6);
      name(
        L3.circleMarker(m3.ort, { radius: 10, color: "#fff", weight: 2, fillColor: f3.amber, fillOpacity: 1, interactive: false }).addTo(e6),
        `${t3("Mast {name}", { name: m3.name })}${m3.fuenf_g ? " · 4G + 5G?" : ""} · ${m3.entfernung}`,
        false
      );
    }
    name(L3.circleMarker(d3.wohnung, { radius: 9, color: "#fff", weight: 2, fillColor: f3.blau, fillOpacity: 1, interactive: false }).addTo(e6), t3("Wohnung"), false, "top");
    this._nah();
  }
};
if (!customElements.get("heimnetz-karte")) customElements.define("heimnetz-karte", HeimnetzKarte);

// src/ansichten/mobilfunk.js
var W = 600;
var H2 = 170;
var UNTEN = -120;
var OBEN = -75;
var y3 = (v2) => (OBEN - Math.max(UNTEN, Math.min(OBEN, v2))) / (OBEN - UNTEN) * H2;
function linie(punkte, von, bis) {
  if (!punkte.length) return "";
  const x2 = (t7) => (t7 - von) / Math.max(1, bis - von) * W;
  return punkte.map(([t7, v2], i6) => `${i6 ? "L" : "M"}${x2(t7).toFixed(1)},${y3(v2).toFixed(1)}`).join("");
}
function mobilfunk(p4, d3) {
  if (!d3.verfuegbar) return b2`<div class="glas-panel block"><div class="leer">${t3("Die Box meldet gerade keine Mobilfunkwerte.")}</div></div>`;
  const o7 = p4._opt.mobilfunk;
  const bis = Date.now() / 1e3;
  const von = bis - o7.tage * 86400;
  return b2`
    <details class="glas-panel klapp befund-k">
      <summary><span class="punkt" style="background:${farbe(d3.befund.lage)}"></span><b>${d3.befund.titel}</b><span class="mehr">ⓘ</span></summary>
      <p class="hinweis">${d3.befund.text}</p>
    </details>
    ${d3.zellen.length ? b2`<div class="glas-panel block">
      <div class="block-kopf"><h3>${t3("Verbindung zur Basisstation")}</h3><span class="leise">${[d3.technik, d3.strecke?.anbieter, d3.herkunft === "modem" ? d3.herkunft_text : ""].filter(Boolean).join(" · ")}</span></div>
      ${d3.strecke ? strecke(d3.strecke) : A}
      <div class="zellen">${d3.zellen.map(zelle)}</div>
      <details class="klapp"><summary><span class="leise">ⓘ ${t3("Was zeigt die Liste?")}</span></summary>
        <p class="hinweis">${d3.zellen.length > 1 ? `${t3("Die Box hält gleichzeitig mehrere Zellen: die Ankerzelle trägt die Verbindung, die übrigen bündeln dazu.")} ` : ""}${t3("Balken = Signalstärke (RSRP), daneben die Signalqualität (RSRQ).")}</p></details>
    </div>` : A}
    ${d3.karte && d3.karte.rahmen ? karte(p4, d3.karte, !!(p4.hass && p4.hass.themes && p4.hass.themes.darkMode)) : A}
    <div class="glas-raster">
      ${kachel(t3("Verbunden seit"), d3.laufzeit ?? "–", d3.letzter_abbruch ? t3("Neueinwahl {zeit}", { zeit: zeit(d3.letzter_abbruch) }) : t3("ohne Neueinwahl (7 Tage)"))}
      ${kachel(t3("Abbrüche"), b2`${d3.abbrueche_7}`, t3("Neueinwahlen, letzte 7 Tage"))}
      ${kachel(t3("Bänder"), d3.baender ? b2`<span style="font-size:15px">${d3.baender}</span>` : "–", d3.baender_unter)}
    </div>
    <div class="glas-panel block">
      <div class="block-kopf"><h3>${t3("Verlauf Signalstärke")}</h3>${seg([[1, "24 h"], [7, t3("{n} Tage", { n: 7 })], [30, t3("{n} Tage", { n: 30 })]], o7.tage, (v2) => p4.setze("mobilfunk", { tage: v2 }))}</div>
      ${d3.verlauf.anker.length || d3.verlauf.nr.length ? b2`<svg class="dia" viewBox="-30 -6 ${W + 36} ${H2 + 24}">
        ${[-80, -90, -100, -110, -120].map((v2) => w`<line class="gitter" x1="0" x2=${W} y1=${y3(v2)} y2=${y3(v2)}></line><text x="-4" y=${y3(v2) + 3} text-anchor="end">${v2}</text>`)}
        ${w`<rect x="0" y=${y3(d3.schwach_unter)} width=${W} height=${H2 - y3(d3.schwach_unter)} fill="var(--rot)" opacity=".08"></rect>`}
        ${w`<path d=${linie(d3.verlauf.anker, von, bis)} fill="none" stroke="var(--s1)" stroke-width="1.6"></path>`}
        ${w`<path d=${linie(d3.verlauf.nr, von, bis)} fill="none" stroke="var(--s2)" stroke-width="1.6"></path>`}
        ${w`<text x="0" y=${H2 + 16}>${o7.tage === 1 ? t3("vor {n} h", { n: 24 }) : t3("vor {n} Tagen", { n: o7.tage })}</text><text x=${W} y=${H2 + 16} text-anchor="end">${t3("jetzt")}</text>`}
      </svg>
      <div class="legende"><span><i style="background:var(--s1)"></i>${t3("4G-Anker")}</span><span><i style="background:var(--s2)"></i>5G</span><span><i style="background:var(--rot);opacity:.3"></i>${t3("schwach (unter {n} dBm)", { n: d3.schwach_unter })}</span></div>
      <p class="hinweis">${t3("Steigt die Linie nach dem Umstellen der Box um etwa 10 dBm, war der Standort die Bremse.")}</p>` : b2`<div class="leer">${t3("Noch kein Verlauf aufgezeichnet.")}</div>`}
      ${A}
    </div>`;
}
function stufen(n4, lage) {
  return b2`<span class="stufen">${[1, 2, 3, 4].map((i6) => b2`<i style="height:${i6 * 25}%;${i6 <= n4 ? `background:${farbe(lage)}` : ""}"></i>`)}</span>`;
}
function zelle(z2) {
  const titel = z2.anker && z2.rolle_art === "anker" ? t3("4G-Anker") : t3("{art}-Zelle", { art: z2.art });
  const kennung = [z2.band ? t3("Band {band}", { band: z2.band }) : "", z2.sinr != null ? `SINR ${zahl(z2.sinr, 1)} dB` : "", z2.tac ? `TAC ${z2.tac}` : "", z2.plmn ? `PLMN ${z2.plmn}` : ""].filter(Boolean).join(" · ");
  const wo = z2.fund ? b2`<span class="z-wo">📍 ${z2.fund.quelle}${z2.fund.genau ? ` · ±${z2.fund.genau}` : ""}</span>` : z2.such ? b2`<span class="z-wo">${z2.such}</span>` : A;
  return b2`<div class="zelle"><span class="badge ${z2.anker ? "blau-b" : ""}">${z2.art}</span>
    <span class="z-name"><b>${titel}</b><span class="leise">${z2.kennung ? `${t3("Zelle {kennung}", { kennung: z2.kennung })} · ` : ""}${z2.rolle}</span>
      <span class="leise">${kennung}${kennung && (z2.fund || z2.such) ? " · " : ""}${wo}</span></span>
    ${stufen(z2.stufen, z2.lage)}<span class="z-wert">${z2.rsrp ?? "–"}<small> dBm</small><span class="leise">${z2.rsrq ?? "–"} dB</span></span></div>`;
}
function strecke(s4) {
  const f3 = farbe(s4.lage);
  const masten = s4.masten.length ? s4.masten : ["4G"];
  const mitte = 530 - (masten.length - 1) * 30;
  const mast = (x2, t7) => w`<g transform="translate(${x2},0)">
    <path d="M0,46 L-17,104 M0,46 L17,104 M-11,82 L11,82 M-14,94 L14,94 M-8,70 L8,70" stroke="var(--ink2)" stroke-width="2" fill="none" stroke-linecap="round"></path>
    <path d="M-10,36 a14,14 0 0 1 0,-20 M10,36 a14,14 0 0 0 0,-20 M-17,42 a24,24 0 0 1 0,-32 M17,42 a24,24 0 0 0 0,-32" stroke="var(--ink2)" stroke-width="1.6" fill="none" opacity=".7"></path>
    <circle cx="0" cy="62" r="13" fill="var(--sheet)" stroke="var(--panel-rand)"></circle><text x="0" y="66" text-anchor="middle" class="m-t">${t7}</text></g>`;
  return b2`<svg class="strecke" viewBox="0 0 600 132" role="img" aria-label=${t3("Verbindung von {geraet} zur Basisstation", { geraet: s4.geraet ?? "FRITZ!Box" })}>
    <rect x="30" y="22" width="44" height="74" rx="9" fill="var(--panel)" stroke="var(--ink2)" stroke-width="2"></rect>
    <rect x="30" y="84" width="44" height="12" rx="4" fill="var(--s2)"></rect>
    <line x1="58" y1="44" x2="66" y2="44" stroke="var(--ink2)" stroke-width="2"></line><line x1="58" y1="50" x2="66" y2="50" stroke="var(--ink2)" stroke-width="2"></line>
    <text x="52" y="122" text-anchor="middle" class="m-t">${s4.geraet ?? "FRITZ!Box"}</text>
    <line x1="96" y1="62" x2=${mitte - 60} y2="62" stroke=${f3} stroke-width="5" stroke-linecap="round"></line>
    <line class="fluss" x1="96" y1="62" x2=${mitte - 60} y2="62" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-dasharray="2 22" opacity=".45"></line>
    ${s4.entfernung ? w`<text x=${(36 + mitte) / 2} y="48" text-anchor="middle" class="m-w">↔ ${s4.entfernung}</text>` : A}
    ${s4.rsrp != null ? w`<text x=${(36 + mitte) / 2} y="86" text-anchor="middle" class="m-t">${t3("Signal {wort} · {n} dBm", { wort: s4.wort, n: s4.rsrp })}</text>` : A}
    ${masten.map((t7, i6) => mast(mitte + i6 * 60, t7))}
    <text x=${mitte + (masten.length - 1) * 30} y="122" text-anchor="middle" class="m-t">${t3("Basisstation")}</text></svg>`;
}
var STAND = {
  ohne_schluessel: merke("BeaconDB kennt diese Zellen nicht. Mit einem Schlüssel von opencellid.org (Einstellungen → Geräte & Dienste → Heimnetz → Konfigurieren) fragt die Integration zusätzlich OpenCellID."),
  nicht_gefunden: merke("Weder OpenCellID noch BeaconDB kennen diese Zellen – die Karte zeigt nur die Entfernung laut Box."),
  fehler: merke("Der Dienst für den Standort der Zellen war nicht erreichbar; neuer Versuch in einer Stunde."),
  schluessel_ungueltig: merke("OpenCellID lehnt den Schlüssel ab – unter Geräte & Dienste → Heimnetz → Konfigurieren prüfen."),
  ohne_kennung: merke("Die Box nennt für keine Zelle eine vollständige Kennung – die Karte zeigt nur die Entfernung.")
};
function karte(p4, k2, dunkel) {
  return b2`<div class="glas-panel block">
    <div class="block-kopf"><h3>${t3("Wo steht der Mast?")}</h3><span class="leise">${k2.gefunden ? t3("geschätzt · {n} von {gesamt} Zellen gefunden", { n: k2.gefunden, gesamt: k2.zellen }) : t3("Entfernung laut Box")}</span></div>
    <heimnetz-karte .daten=${k2} ?dunkel=${dunkel} .sprache=${sprache()} @osm-umgeschaltet=${() => p4.requestUpdate()}></heimnetz-karte>
    <div class="legende"><span><i style="background:var(--blau)"></i>${t3("Wohnung")}</span>
      ${k2.masten.map((m3) => b2`<span><i style="background:var(--amber)"></i>${t3("Mast {name} (geschätzt)", { name: m3.name })}${m3.fuenf_g ? ` · ${t3("4G + 5G (vermutlich)")}` : ""} · ${m3.entfernung} ${m3.richtung}${m3.genau ? ` (± ${m3.genau})` : ""}</span>`)}
      ${k2.punkte.length ? b2`<span><i class="punkt-l" style="background:var(--blau)"></i>${t3("Ankerzelle")}</span><span><i class="punkt-l" style="background:var(--ink2)"></i>${t3("weitere Zellen")}</span><span><i class="genau-l"></i>${t3("Genauigkeit")}</span>` : A}
      ${k2.osm?.length && osmGemerkt() ? b2`<span><i class="osm-l"></i>${t3("Funkmast laut OpenStreetMap")}${k2.osm.some((o7) => o7.passt) ? ` ${t3("(orange umrandet: passt am besten)")}` : ""}</span>` : A}
      ${k2.ring ? b2`<span><i class="ring"></i>${t3("{ring} laut Box", { ring: k2.ring })}</span>` : A}</div>
    ${STAND[k2.stand] ? b2`<p class="hinweis">${t3(STAND[k2.stand])}</p>` : A}
    <details class="klapp"><summary><span class="leise">ⓘ ${t3("Woher kommt das?")}</span></summary>
      <p class="hinweis">${t3(WOHER)}</p></details>
  </div>`;
}
var WOHER = merke("Die Box meldet nur die Entfernung (Ring), nicht die Richtung. Jede Zelle mit voller Kennung schlägt die Integration bei BeaconDB (ohne Schlüssel) und – mit eigenem Schlüssel – bei OpenCellID nach und merkt sich das Ergebnis; es zählt der genauere Fund. Hinaus geht nur die Kennung der Zelle, nie dein Standort. Beide Dienste kennen nicht den Mast selbst, sondern die Orte, an denen Nutzer die Zelle empfangen haben – daher der Kreis für die Genauigkeit. Zellen derselben Sendeanlage (Kennung vor dem Bindestrich) hängen am selben Mast; sein Standort ist das Mittel ihrer Punkte, genauere zählen mehr. Zellen, von denen die Box nur die PCI nennt, lassen sich nicht nachschlagen – auch 5G nicht: Die Box nennt für 5G nur diese Nummer. Bei 5G-NSA hängt die 5G-Zelle aber meist am selben Mast wie die LTE-Ankerzelle, deshalb steht dort „4G + 5G (vermutlich)“, solange 5G mitläuft. Die Namen der Zellen erscheinen beim Hineinzoomen. Zoomen mit ＋/−, Mausrad oder zwei Fingern, ziehen zum Verschieben, ⌖ zeigt wieder alles. Die Kartenkacheln lädt dein Browser von basemap.at (Server der Stadt Wien) oder OpenStreetMap; der Anbieter sieht dabei den Kartenausschnitt, nicht mehr. Die gewählte Grundlage merkt sich dein Browser. „📡 Masten (OSM)“ zeigt Funkmasten, die in OpenStreetMap eingetragen sind – echte Bauwerke, aber meist ohne Betreiber. Orange umrandet ist der Mast, der am nächsten am geschätzten Mast der Zellen steht (höchstens 1,5 km daneben); ist der nicht bekannt, der Mast, dessen Entfernung am besten zur Entfernung laut Box passt – die schwankt je Zelle aber stark. Ein Hinweis, kein Beweis. Zellen einer Sendeanlage, die einmal gefunden wurden, zählen einen Monat lang mit – auch wenn die Box gerade an einem Sektor hängt, den keine Datenbank kennt. Antippen eines Masts zeigt Entfernung und Richtung und – mit OpenCellID-Schlüssel – Anbieter und Technik der Zellen, die OpenCellID in höchstens 500 m Abstand kennt (aus dem Datenabzug für ganz Österreich, einmal im Monat geladen und hier ausgewertet). ⛶ öffnet die Karte über die ganze Seite. Die Integration fragt dafür einmal im Monat einen großen Ausschnitt auf festem Raster bei OpenStreetMap ab; daraus lässt sich deine Wohnung nur auf etwa 22 × 15 km eingrenzen.");

// src/ansichten/internet.js
var SYMBOL2 = { mobilfunk: "📶", dsl: "☎️", glasfaser: "💡", kabel: "📺", extern: "📶" };
var ABZEICHEN = { gut: "gruen", knapp: "amber-b", schlecht: "rot-b" };
var QUELLE = { automatisch: merke("automatisch erkannt"), festgelegt: merke("festgelegt") };
var lade = () => b2`<div class="glas-panel block"><div class="leer">${t3("lädt …")}</div></div>`;
var wert = (w2, stellen = 1) => w2 == null ? "–" : zahl(w2, stellen);
function ik(titel, w2, unter, cls = "") {
  return b2`<div class="glas-k glas-panel ${cls}"><span class="glas-klein">${titel}</span><span class="glas-wert">${w2}</span><span class="glas-kwk">${unter}</span></div>`;
}
function iz(name, w2, unter = "") {
  return b2`<div class="ez"><span>${name}${unter ? b2`<small>${unter}</small>` : A}</span><span class="iz-w">${w2}</span></div>`;
}
function zugangZeile(p4, z2) {
  return b2`<div class="glas-panel block iq">
    <span class="iq-ic">${SYMBOL2[z2.art] ?? "🌐"}</span>
    <span><b>${z2.titel}</b><small>${[z2.geraet, z2.weg_text, z2.ersatz_text ? t3("Ersatz: {text}", { text: z2.ersatz_text }) : ""].filter(Boolean).join(" · ")}</small>
      ${z2.abweichung ? b2`<small class="amber-t">${t3("Die FRITZ!Box meldet etwas anderes: {vorschlag}", { vorschlag: z2.abweichung })}</small>` : A}</span>
    <span class="iq-r"><span class="badge">${t3(QUELLE[z2.quelle] ?? z2.quelle)}</span>
      ${p4.istAdmin ? b2`<button class="leise blau" @click=${() => p4.einstellungenOeffnen("zugang")}>${t3("ändern ›")}</button>` : A}</span>
  </div>`;
}
function internet(p4, d3) {
  if (!d3) return lade();
  const z2 = d3.zugang;
  const sicht = p4._opt.internet.sicht === "ersatz" && d3.ersatz ? "ersatz" : "haupt";
  const knoepfe = [["haupt", `${SYMBOL2[z2.art] ?? "🌐"} ${art(z2)}`], ...d3.ersatz ? [["ersatz", t3("📶 Ersatz")]] : []];
  const inhalt = sicht === "ersatz" ? ersatz(d3.ersatz) : z2.art === "dsl" ? dsl(d3.dsl) : z2.art === "glasfaser" ? glasfaser(d3.glasfaser) : z2.art === "kabel" ? kabel(d3.kabel) : z2.art === "extern" ? extern(p4, d3) : z2.art === "mobilfunk" && d3.mobilfunk ? mobilfunk(p4, d3.mobilfunk) : b2`<div class="glas-panel block"><div class="leer">${t3("Die Box meldet noch nicht, woher das Internet kommt – sie wird alle 10 Minuten gefragt.")}</div></div>`;
  return b2`${zugangZeile(p4, z2)}
    ${knoepfe.length > 1 ? b2`<div class="leiste">${seg(knoepfe, sicht, (v2) => p4.setze("internet", { sicht: v2 }, false), false)}</div>` : A}
    ${inhalt}`;
}
function art(z2) {
  return { mobilfunk: t3("Mobilfunk"), dsl: "DSL", glasfaser: t3("Glasfaser"), kabel: t3("Kabel"), extern: t3("Vorgeschaltet") }[z2.art] ?? t3("Internet");
}
function bewertung(b3) {
  const rahmen = b3.stufe === "knapp" ? "border-color:color-mix(in srgb, var(--amber) 60%, var(--panel-rand))" : b3.stufe === "schlecht" ? "border-color:color-mix(in srgb, var(--rot) 60%, var(--panel-rand))" : "";
  return b2`<div class="glas-panel block" style=${rahmen}>
    <div class="block-kopf"><h3>${b3.titel}</h3>${b3.abzeichen ? b2`<span class="badge ${ABZEICHEN[b3.stufe] ?? ""}">${b3.abzeichen}</span>` : A}</div>
    ${b3.text ? b2`<p class="hinweis" style="font-size:13px">${b3.text}</p>` : A}</div>`;
}
var fehlt = (text) => b2`<span class="leise" title=${text}>–</span>`;
function dsl(d3) {
  if (!d3) return b2`<div class="glas-panel block"><div class="leer">${t3("Die Box meldet gerade keine DSL-Werte.")}</div></div>`;
  const moeglich = (m3, tarif) => [m3 != null ? t3("möglich {n}", { n: zahl(m3, 1) }) : "", tarif ? t3("Tarif {n}", { n: zahl(tarif) }) : ""].filter(Boolean).join(" · ") || t3("laut Box");
  return b2`${bewertung(d3.bewertung)}
    <div class="glas-raster">
      ${ik(t3("Synchron Download"), b2`${wert(d3.sync_down)}<small> Mbit/s</small>`, moeglich(d3.max_down, d3.tarif_down))}
      ${ik(t3("Synchron Upload"), b2`${wert(d3.sync_up)}<small> Mbit/s</small>`, moeglich(d3.max_up, d3.tarif_up))}
      ${ik(t3("Störabstand ↓ / ↑"), b2`${wert(d3.marge_down)} / ${wert(d3.marge_up)}<small> dB</small>`, t3("Marge, gut ab {n} dB", { n: zahl(d3.marge_gut) }), ["knapp", "schlecht"].includes(d3.marge_stufe) ? "amber-k" : "")}
      ${ik(t3("Dämpfung ↓ / ↑"), b2`${wert(d3.daempfung_down)} / ${wert(d3.daempfung_up)}<small> dB</small>`, t3("laut Box"))}
    </div>
    <div class="glas-panel block"><div class="block-kopf"><h3>${t3("Leitung")}</h3><span class="leise">${t3("laut FRITZ!Box")}</span></div>
      ${iz(t3("Status"), d3.status)}
      ${iz(t3("Verfahren"), d3.verfahren ?? fehlt(d3.fehlt), t3("Vectoring: {text}", { text: d3.fehlt }))}
      ${iz(t3("Verbunden seit"), d3.seit_text ?? "–", d3.seit ? t3("letzte Neusynchronisierung {zeit}", { zeit: zeit(d3.seit) }) : t3("seit dem Start von Heimnetz keine Neusynchronisierung gesehen"))}
      ${iz(t3("Fehler je Stunde"), d3.crc_h == null && d3.fec_h == null ? "–" : `CRC ${wert(d3.crc_h, 0)} · FEC ${wert(d3.fec_h, 0)}`, t3("CRC = nicht korrigierbar, FEC = korrigiert"))}
      ${iz(t3("Neusynchronisierungen"), t3("{n} in 7 Tagen", { n: d3.neusync_7 }))}
      ${iz(t3("Gegenstelle (DSLAM)"), fehlt(d3.fehlt), d3.fehlt)}
    </div>
    ${verlauf(t3("Verlauf 7 Tage"), t3("Synchron-Download und Störabstand"), [
    { punkte: d3.verlauf.sync, farbe: "var(--s1)", name: t3("Synchron-Download (Mbit/s)") },
    { punkte: d3.verlauf.marge, farbe: "var(--amber)", name: t3("Störabstand Download (dB)") }
  ], d3.neusync.map((n4) => n4.t))}`;
}
function glasfaser(g2) {
  if (!g2) return b2`<div class="glas-panel block"><div class="leer">${t3("Die Box meldet gerade keine Glasfaser-Werte.")}</div></div>`;
  const bereich = (b3, abwaerts) => b3 ? t3("gut {von} … {bis}", { von: zahl(b3[abwaerts ? 1 : 0], 1), bis: zahl(b3[abwaerts ? 0 : 1], 1) }) : t3("Bereich meldet die Box nicht");
  return b2`${bewertung(g2.bewertung)}
    <div class="glas-raster">
      ${ik(t3("Empfangene Lichtleistung"), b2`${wert(g2.rx)}<small> dBm</small>`, bereich(g2.rx_bereich, true), g2.bewertung.stufe === "knapp" || g2.bewertung.stufe === "schlecht" ? "amber-k" : "")}
      ${ik(t3("Gesendete Lichtleistung"), b2`${wert(g2.tx)}<small> dBm</small>`, bereich(g2.tx_bereich, false))}
      ${ik(t3("Verbindung"), g2.modus ?? "–", g2.down_mbit ? `${zahl(g2.down_mbit)} / ${zahl(g2.up_mbit)} Mbit/s` : t3("laut Box"))}
      ${ik(t3("Status"), "–", g2.fehlt)}
    </div>
    <div class="glas-panel block"><div class="block-kopf"><h3>${t3("Glasfaser-Anschluss")}</h3><span class="leise">${t3("laut FRITZ!Box")}</span></div>
      ${iz(t3("Verbunden seit"), g2.seit_text ?? "–", g2.resyncs != null ? t3("{n} Neusynchronisierungen laut Box", { n: g2.resyncs }) : "")}
      ${iz(t3("Fehler je Stunde"), g2.fehler_h == null ? "–" : wert(g2.fehler_h, 0), t3("fehlerhaft empfangene Pakete"))}
      ${iz(t3("Temperatur Modul"), fehlt(g2.fehlt), g2.fehlt)}
      ${iz(t3("Anschluss-Kennung"), b2`<span class="amber-t">${t3("⟨nur in der Box⟩")}</span>`, t3("Seriennummer und Kennung zeigt die Seite nicht"))}
    </div>
    ${verlauf(t3("Verlauf 7 Tage"), t3("Lichtleistung"), [{ punkte: g2.verlauf.rx, farbe: "var(--s1)", name: t3("empfangene Lichtleistung (dBm)") }], [], g2.rx_bereich)}
    <p class="hinweis">${t3("Mit einem eigenen Glasfaser-Modem (ONT) vor der FRITZ!Box: unter ⚙ › 🌐 Zugang „Glasfaser über eigenes Modem“ wählen. Heimnetz erkennt das ONT; seine Werte liest es noch nicht.")}</p>`;
}
function kabel(k2) {
  if (!k2) return lade();
  return b2`<div class="glas-panel block"><div class="block-kopf"><h3>${k2.verbunden === false ? t3("Kabelanschluss getrennt") : t3("Kabelanschluss verbunden")}</h3>
      <span class="badge ${k2.verbunden === false ? "rot-b" : "gruen"}">${k2.verbunden === false ? t3("getrennt") : t3("verbunden")}</span></div>
    <p class="hinweis" style="font-size:13px">${t3("Kanäle, Pegel und Fehler des Kabelmodems gibt die Schnittstelle der FRITZ!Box (TR-064) nicht heraus – nur die Geschwindigkeit der Verbindung.")}</p></div>
    <div class="glas-raster">
      ${ik(t3("Verbindung"), k2.down_mbit ? b2`${zahl(k2.down_mbit)}<small> / ${zahl(k2.up_mbit)} Mbit/s</small>` : "–", t3("laut Box"))}
      ${ik(t3("Empfangskanäle"), "–", k2.fehlt)}
      ${ik(t3("Empfangspegel"), "–", k2.fehlt)}
      ${ik(t3("Signal/Rausch (MER)"), "–", k2.fehlt)}
    </div>
    <div class="glas-panel block"><div class="block-kopf"><h3>${t3("Kanäle")}</h3><span class="leise">${t3("laut FRITZ!Box")}</span></div>
      ${iz(t3("Sendepegel"), "–", k2.fehlt)}
      ${iz(t3("Fehler korrigiert / nicht korrigierbar"), "–", k2.fehlt)}
      ${iz(t3("Kanalliste"), "–", k2.fehlt)}
    </div>`;
}
var PUNKT2 = { grau: "grau", amber: "amber", rot: "rot" };
function extern(p4, d3) {
  const v2 = d3.vorgeschaltet || {};
  const b3 = v2.befund;
  const kopf = b3 ? b2`<div class="befund"><span class="punkt ${PUNKT2[b3.lage] ?? "grau"}"></span><div><b>${b3.titel}</b><p>${b3.text}</p></div></div>` : b2`<div class="befund"><span class="punkt grau"></span><div><b>${t3("Werte vom vorgeschalteten Modem (Beta)")}</b>
      <p>${v2.quelle === "integration" ? t3("Die FRITZ!Box hängt hinter dem {geraet} und kennt das Funknetz nicht. Die Werte kommen aus dessen Integration in Home Assistant. Was sie nicht liefert, steht als „–“.", { geraet: v2.geraet ?? t3("Modem") }) : t3("Die FRITZ!Box hängt hinter dem {geraet} und kennt das Funknetz nicht. Heimnetz liest Zelle und Signal direkt am Gerät (Anmeldung mit dem in ⚙ › 🌐 Zugang hinterlegten Kennwort). Was es nicht liefert, steht als „–“.", { geraet: v2.geraet ?? t3("Modem") })}${v2.gelesen ? ` ${t3("Zuletzt gelesen {zeit}.", { zeit: zeit(v2.gelesen) })}` : ""}</p></div></div>`;
  const knoepfe = p4.istAdmin && b3 ? b2`<div class="dg-knoepfe"><button @click=${() => p4.einstellungenOeffnen("zugang")}>${t3("🌐 Zugang ›")}</button><button @click=${() => p4.einstellungenOeffnen("diag")}>${t3("🔬 Rohdaten abfragen ›")}</button></div>` : A;
  return b2`<div class="glas-panel block">${kopf}${knoepfe}</div>
    ${d3.mobilfunk ? mobilfunk(p4, d3.mobilfunk) : A}`;
}
function ersatz(e6) {
  return b2`<div class="glas-panel block"><div class="block-kopf"><h3>${t3("Ersatzzugang Mobilfunk")}</h3>
      <span class="badge ${e6.aktiv ? "amber-b" : ""}">${e6.aktiv ? t3("aktiv") : t3("bereit · nicht aktiv")}</span></div>
    <p class="hinweis" style="font-size:13px">${e6.text}${e6.letzte ? ` · ${t3("zuletzt aktiv {zeit}", { zeit: zeit(e6.letzte) })}` : ""}${e6.rsrp != null ? ` · ${t3("Signal gerade {n} dBm", { n: e6.rsrp })}${e6.technik ? ` (${e6.technik})` : ""}` : ""}</p></div>
    <div class="glas-raster">
      ${ik(t3("Umschaltungen"), b2`${e6.umschaltungen_30}`, t3("letzte 30 Tage"))}
      ${ik(t3("Über Ersatz"), e6.dauer_30 ?? "–", t3("letzte 30 Tage"))}
      ${ik(t3("Datenmenge"), "–", t3("über Ersatz: meldet die Box nicht getrennt"))}
    </div>`;
}
function verlauf(titel, unter, linien, marken = [], band = null) {
  const W3 = 600, H4 = 150;
  const bis = Date.now() / 1e3, von = bis - 7 * 86400;
  const x2 = (z2) => (z2 - von) / (bis - von) * W3;
  const da = linien.some((l4) => l4.punkte.length);
  const pfad = (l4) => {
    const v2 = l4.punkte.map((q) => q[1]).concat(band ? band : []);
    const lo = Math.min(...v2), hi = Math.max(...v2), spanne = hi - lo || 1;
    const y4 = (w2) => H4 - (w2 - lo) / spanne * (H4 - 10) - 5;
    return { d: l4.punkte.map(([z2, w2], i6) => `${i6 ? "L" : "M"}${x2(z2).toFixed(1)},${y4(w2).toFixed(1)}`).join(""), y: y4 };
  };
  const erste = da ? pfad(linien[0]) : null;
  return b2`<div class="glas-panel block"><div class="block-kopf"><h3>${titel}</h3><span class="leise">${unter}</span></div>
    ${da ? b2`<svg class="dia" viewBox="0 -6 ${W3} ${H4 + 24}">
        ${band && erste ? w`<rect x="0" y=${Math.min(erste.y(band[0]), erste.y(band[1]))} width=${W3} height=${Math.abs(erste.y(band[0]) - erste.y(band[1]))} fill="var(--s3)" opacity=".1"></rect>` : A}
        ${linien.map((l4) => w`<path d=${pfad(l4).d} fill="none" stroke=${l4.farbe} stroke-width="1.6"></path>`)}
        ${marken.map((m3) => w`<circle cx=${x2(m3)} cy=${H4 - 4} r="4" fill="var(--rot)"></circle>`)}
        ${w`<text x="0" y=${H4 + 16}>${t3("vor {n} Tagen", { n: 7 })}</text><text x=${W3} y=${H4 + 16} text-anchor="end">${t3("jetzt")}</text>`}
      </svg>
      <div class="legende">${linien.map((l4) => b2`<span><i style="background:${l4.farbe}"></i>${l4.name}</span>`)}${marken.length ? b2`<span><i style="background:var(--rot)"></i>${t3("Neusynchronisierung")}</span>` : A}</div>` : b2`<div class="leer">${t3("Noch kein Verlauf aufgezeichnet.")}</div>`}
  </div>`;
}

// node_modules/lit-html/directives/unsafe-html.js
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
var e5 = class extends i5 {
  constructor(i6) {
    if (super(i6), this.it = A, i6.type !== t4.CHILD) throw Error(this.constructor.directiveName + "() can only be used in child bindings");
  }
  render(r5) {
    if (r5 === A || null == r5) return this._t = void 0, this.it = r5;
    if (r5 === E) return r5;
    if ("string" != typeof r5) throw Error(this.constructor.directiveName + "() called with a non-string value");
    if (r5 === this.it) return this._t;
    this.it = r5;
    const s4 = [r5];
    return s4.raw = s4, this._t = { _$litType$: this.constructor.resultType, strings: s4, values: [] };
  }
};
e5.directiveName = "unsafeHTML", e5.resultType = 1;
var o5 = e4(e5);

// node_modules/lit-html/directives/unsafe-svg.js
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
var t6 = class extends e5 {
};
t6.directiveName = "unsafeSVG", t6.resultType = 2;
var o6 = e4(t6);

// src/ansichten/melden.js
var MB_MAX = 3;
var MB_PX = 1600;
var ICON_MELDEN = '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" d="M4 5h16v11H9l-5 4z"/><path stroke="currentColor" stroke-width="1.8" stroke-linecap="round" d="M12 8v3.5M12 13.6v.2"/></svg>';
var ARTEN = [["fehler", merke("Fehler")], ["wunsch", merke("Wunsch")], ["anregung", merke("Anregung")]];
var ART_FARBE = { fehler: "rot-b", wunsch: "blau-b", anregung: "amber-b" };
var STATUS_FARBE = { neu: "amber-b", angenommen: "blau-b", in_arbeit: "blau-b", geloest: "gruen" };
var zeit2 = (iso) => {
  const ms = Date.parse(iso || "");
  return Number.isNaN(ms) ? "–" : zeit(ms / 1e3);
};
var FRAGE = { fehler: merke("Was ist passiert, was hättest du erwartet?"), wunsch: merke("Was wünschst du dir?"), anregung: merke("Deine Idee") };
var offen = (m3) => !!m3.offen;
function meldenKnopf(p4, imBlatt = false) {
  return b2`<button class="melden-knopf glas-panel ${imBlatt ? "im-sheet" : ""}" title=${t3("Fehler, Wunsch oder Anregung melden")} aria-label=${t3("Melden")} @click=${() => p4.meldenAuf()}>${o6(ICON_MELDEN)}</button>`;
}
function bilderBox(p4, f3) {
  const B2 = f3.bilder, pc = !p4.narrow;
  const auf = pc && typeof navigator !== "undefined" && navigator.mediaDevices && navigator.mediaDevices.getDisplayMedia;
  const gewaehlt = (e6) => {
    const dateien = [...e6.target.files || []];
    if (!dateien.length) p4.toast(t3("Kein Bild gewählt"));
    dateien.forEach((x2) => p4.bildDatei(x2, merke("Bild gewählt")));
    e6.target.value = "";
  };
  return b2`<div class="mb-box"><div class="mb-kopf"><b>📷 Screenshot</b><span class="leise">${t3("{n} von {gesamt}", { n: B2.length, gesamt: MB_MAX })}</span></div>
    ${B2.length >= MB_MAX ? A : b2`<div class="mb-knoepfe"><label>📎 ${t3("Bild wählen")}<input type="file" accept="image/*" @change=${gewaehlt}></label>${auf ? b2`<button @click=${() => p4.fensterAufnehmen()}>🖥 ${t3("Fenster aufnehmen")}</button>` : A}</div>`}
    <div class="leise">${pc ? b2`${t3("oder einen Screenshot mit")} <b>${t3("Strg+V")}</b> ${t3("einfügen (z. B. nach Win+Shift+S)")}` : t3("Screenshot mit den Handy-Tasten machen, dann „Bild wählen“ – der neueste steht in der Galerie vorne")} · ${t3("wird auf höchstens {n} px verkleinert", { n: MB_PX })}</div>
    ${B2.length ? b2`<div class="mb-bilder">${B2.map((x2, i6) => b2`<div class="mb-bild"><img src=${x2.url} alt=${t3("Bild {n}", { n: i6 + 1 })}><button class="x" aria-label=${t3("Bild entfernen")} @click=${() => {
    B2.splice(i6, 1);
    p4.requestUpdate();
    p4.entwurfMerken();
  }}>✕</button><small>${x2.b}×${x2.h} · ${x2.kb} KB</small></div>`)}</div>` : A}</div>`;
}
function meldenBlatt(p4) {
  const f3 = p4._blatt.form;
  const setze = (k2, v2) => {
    f3[k2] = v2;
    p4.requestUpdate();
    p4.entwurfMerken();
  };
  return b2`<div class="griff"></div><button class="zu" @click=${() => p4.meldenZu()}>✕</button>
    <h3>${t3("Melden")}</h3><div class="leise">${t3("Fehler, Wunsch oder Anregung – wird ein lokales Ticket; öffentlich über GitHub erreicht es den Entwickler.")}</div>
    ${seg(tl(ARTEN), f3.art, (v2) => setze("art", v2), false)}
    <label class="feld">${t3(FRAGE[f3.art])}<textarea rows="4" name="ml-text" placeholder=${t3("kurz beschreiben")} .value=${l3(f3.text)} @input=${(e6) => {
    f3.text = e6.target.value;
    p4.entwurfMerken();
  }}></textarea></label>
    <div class="ml-kontext"><div><span class="leise">${t3("Reiter")}</span> ${f3.kontext}</div><div><span class="leise">Version</span> ${f3.version} · ${f3.geraet}</div></div>
    ${bilderBox(p4, f3)}
    <div class="zeile"><div><b>${t3("Stand der Seite mitschicken")}</b><div class="leise">${t3("Reiter, Filter und offener Dialog – hilft beim Nachstellen, ohne Zugangsdaten")}</div></div>
      <button class="sw ${f3.stand ? "on" : ""}" role="switch" aria-checked=${f3.stand ? "true" : "false"} @click=${() => setze("stand", !f3.stand)}><i></i></button></div>
    ${f3.fehler ? b2`<p class="fein">${f3.fehler}</p>` : A}
    <button class="knopf breit amber ml-senden" ?disabled=${f3.sendet} @click=${() => p4.meldungSenden()}>${f3.sendet ? t3("sendet …") : t3("Senden")}</button>
    <button class="knopf breit ml-github" ?disabled=${f3.sendet} @click=${() => p4.githubAuf()}>${t3("Senden + öffentlich auf GitHub")} ↗</button>
    <div class="leise mitte">${t3("GitHub: für den Entwickler sichtbar, auch wenn er dein Heimnetz nicht kennt – mit deinem eigenen GitHub-Konto")}</div>
    <button class="knopf breit leise-k" @click=${() => p4.meldenZu()}>${t3("Abbrechen")}</button>`;
}
function githubBlatt(p4) {
  const b3 = p4._blatt, f3 = b3.vorher.form, v2 = b3.vorschau, n4 = f3.bilder.length;
  return b2`<div class="griff"></div><button class="zu" @click=${() => p4.meldenZu()}>✕</button>
    <h3>${t3("Öffentlich auf GitHub melden")}</h3><div class="leise">${t3("Das Issue ist für alle sichtbar. Du siehst hier genau, was mitgeht; auf GitHub kannst du es vor dem Absenden noch ändern.")}</div>
    ${v2 ? b2`<div class="gh-vorschau"><b>${v2.titel}</b>

${v2.text}</div>` : b2`<div class="leer">${b3.fehler || t3("lädt …")}</div>`}
    ${v2 && v2.gekuerzt ? b2`<div class="leise">${t3("Der Text ist für den Link zu lang und wurde gekürzt – ganz steht er im lokalen Ticket.")}</div>` : A}
    <div class="zeile"><div><b>${t3("Zell- und Signaldaten mitsenden")}</b><div class="leise">${v2 && !v2.zelle_da ? t3("Im Moment keine Zelldaten von der Box") : t3("Zellkennung, Signal, Entfernung zum Mast – hilft bei Fehlern im Mobilfunk-Reiter")}</div></div>
      <button class="sw ${f3.zelle ? "on" : ""}" role="switch" aria-checked=${f3.zelle ? "true" : "false"} ?disabled=${f3.sendet} @click=${() => p4.githubZelle(!f3.zelle)}><i></i></button></div>
    ${f3.zelle ? b2`<div class="gh-warn"><b>${t3("Achtung:")}</b> ${t3("Aus Zellkennung und Entfernung lässt sich ungefähr bestimmen, wo du wohnst. Nur mitsenden, wenn es für den Fehler nötig ist.")}</div>` : A}
    <div class="leise">${t3("Nie dabei: Gerätenamen, Hardware-Adressen, IP-Adressen, Standort von Home Assistant, Kennwörter.")}${n4 ? ` · ${t3(n4 === 1 ? "Dein Bild kann GitHub nicht über den Link übernehmen – nach dem Öffnen ins Issue ziehen." : "Deine {n} Bilder kann GitHub nicht über den Link übernehmen – nach dem Öffnen ins Issue ziehen.", { n: n4 })}` : ""}</div>
    ${f3.fehler ? b2`<p class="fein">${f3.fehler}</p>` : A}
    <button class="knopf breit amber gh-senden" ?disabled=${f3.sendet || !v2} @click=${() => p4.meldungSenden(true)}>${f3.sendet ? t3("sendet …") : b2`${t3("Speichern und weiter zu GitHub")} ↗`}</button>
    <button class="knopf breit leise-k" ?disabled=${f3.sendet} @click=${() => p4.githubZurueck()}>${t3("Zurück")}</button>`;
}
function ticket(p4, m3) {
  const auf = offen(m3);
  const letzte = (m3.verlauf || []).filter((v2) => v2.notiz || v2.version || v2.commit).at(-1);
  return b2`<div class="ml ${auf ? "" : "erledigt"}"><div class="ml-kopf"><span><b>${m3.ticket}</b> <span class="badge ${ART_FARBE[m3.art] || ""}">${m3.art_text}</span> <span class="badge ${STATUS_FARBE[m3.status] || ""}">${m3.status_text}</span></span>
      <span class="leise">${zeit2(m3.zeit)} · ${m3.geraet || "–"} · v${m3.version || "–"}</span></div>
    <div class="ml-text">${m3.text}</div>${m3.kontext ? b2`<div class="leise">${m3.kontext}</div>` : A}
    ${(m3.bilder || []).length ? b2`<div class="ml-bilder">${m3.bilder.map((_2, i6) => {
    const u3 = p4.meldungBild(m3, i6);
    return u3 ? b2`<img src=${u3} alt=${t3("Bild {n}", { n: i6 + 1 })} @click=${() => p4.bildGross(m3, i6)}>` : b2`<i></i>`;
  })}</div>` : A}
    ${letzte ? b2`<div class="ml-notiz">${[letzte.von, letzte.version && `v${letzte.version}`, letzte.commit && `Commit ${letzte.commit}`, letzte.notiz].filter(Boolean).join(" · ")}</div>` : A}
    ${p4.istAdmin ? b2`<div class="ml-k"><button class="chip glas-panel" @click=${() => p4.meldungStatus(m3, auf ? "geschlossen" : "neu")}>${auf ? `✓ ${t3("Schließen")}` : `↺ ${t3("wieder öffnen")}`}</button><button class="chip glas-panel" @click=${() => p4.meldungLoeschen(m3)}>${t3("Löschen")}</button></div>` : A}</div>`;
}
function meldungenBlatt(p4) {
  const alle = p4._daten.meldungen, f3 = p4._blatt.filter || "offen";
  const anzahl2 = (k2) => !alle ? "" : k2 === "alle" ? alle.length : alle.filter((m3) => k2 === "offen" === offen(m3)).length;
  const liste = (alle || []).filter((m3) => f3 === "alle" || f3 === "offen" === offen(m3));
  return b2`<div class="griff"></div><button class="zu" @click=${() => p4.zu()}>✕</button>
    <h3>${t3("Meldungen")}</h3><div class="leise">${t3("Jede Meldung ist ein Ticket: FE Fehler, WU Wunsch, AN Anregung")}</div>
    ${seg([["offen", `${t3("offen")} ${anzahl2("offen")}`], ["erledigt", `${t3("erledigt")} ${anzahl2("erledigt")}`], ["alle", `${t3("alle")} ${anzahl2("alle")}`]], f3, (v2) => {
    p4._blatt = { ...p4._blatt, filter: v2 };
  })}
    ${!alle ? b2`<div class="leer">${t3("lädt …")}</div>` : liste.length ? liste.map((m3) => ticket(p4, m3)) : b2`<div class="leer">${t3("Keine Meldungen")}</div>`}
    ${alle && alle.length ? b2`<div class="ml-k"><button class="chip glas-panel" @click=${() => p4.meldungenKopieren()}>${t3("Als Markdown kopieren")}</button></div>` : A}
    <p class="hinweis">${t3("Die Tickets bleiben lokal in Home Assistant und liegen lesbar unter heimnetz/meldungen.md. Ist eines erledigt, wird es geschlossen; passt es nicht, hier wieder öffnen.")}${p4.istAdmin ? "" : ` ${t3("Schließen und löschen dürfen nur Admins.")}`}</p>`;
}
function bildBlatt(p4) {
  const { m: m3, i: i6 } = p4._blatt, u3 = p4.meldungBild(m3, i6);
  return b2`<div class="griff"></div><button class="zu" @click=${() => p4.meldungenOeffnen()}>✕</button>
    <h3>${m3.ticket} · ${t3("Bild {n}", { n: i6 + 1 })}</h3>${u3 ? b2`<img class="mb-gross" src=${u3} alt=${t3("Bild {n}", { n: i6 + 1 })}>` : b2`<div class="leer">${t3("lädt …")}</div>`}`;
}
function meldungenZeile(p4) {
  const alle = p4._daten.meldungen, n4 = alle ? alle.filter(offen).length : null;
  return b2`<div class="ez"><span>${t3("Tickets aus dem Melden-Knopf")}<small>${t3("Fehler, Wünsche, Anregungen – lokal gespeichert")}</small></span>
    <button class="blau" @click=${() => p4.meldungenOeffnen()}>${alle ? t3("{n} offen · {erledigt} erledigt", { n: n4, erledigt: alle.length - n4 }) : "–"} ›</button></div>`;
}
function alsMarkdown(liste) {
  return liste.map((m3) => `- [${offen(m3) ? " " : "x"}] **${m3.ticket} ${m3.art_text}** (${m3.status_text}, ${zeit2(m3.zeit)}, v${m3.version || "–"}, ${m3.geraet || "–"}, ${m3.kontext || "–"}): ${m3.text}`).join("\n");
}

// src/ansichten/einstellungen.js
var MODI = [["aus", merke("weglassen")], ["halb", "¼"], ["mit", merke("voll")]];
var TAKTE = [[1, "1 h"], [2, "2 h"], [4, "4 h"], [6, "6 h"], [12, "12 h"], [24, "24 h"]];
var VERKEHR = [["warten", merke("verschieben")], ["messen", merke("messen")]];
var SERIE = [[2, "2"], [3, "3"], [4, "4"], [5, "5"]];
var SCHWACH = [[30, "30 %"], [40, "40 %"], [50, "50 %"]];
var TEILE2 = [
  ["speed", "📈 Speedtest"],
  ["plan", merke("⏱️ Messplan")],
  ["wlan", merke("📶 WLAN")],
  ["arten", merke("🏷️ Arten")],
  ["warn", merke("🔔 Warnungen")],
  ["meld", merke("💬 Meldungen")],
  ["zugang", merke("🌐 Zugang")],
  ["einr", merke("🧩 Einrichtung")],
  ["diag", merke("🔬 Diagnose")]
];
var WAHL2 = {
  auto: [merke("Automatisch (empfohlen)"), ""],
  box_mobil: [merke("Mobilfunk über die FRITZ!Box"), merke("eingebautes Modem oder Stick")],
  extern: [merke("Mobilfunk über ein vorgeschaltetes Modem"), merke("ZTE, Huawei, TP-Link … (Beta)")],
  dsl: [merke("DSL über die FRITZ!Box"), merke("ADSL, VDSL, Supervectoring")],
  glasfaser: [merke("Glasfaser über die FRITZ!Box"), merke("eingebautes Glasfaser-Modem (z. B. FRITZ!Box 5590 Fiber)")],
  ont: [merke("Glasfaser über ein eigenes Modem"), merke("ONT von Nokia, Huawei, Zyxel … – nur erkennen (Beta)")],
  kabel: [merke("Kabel"), merke("über die FRITZ!Box")]
};
var ERSATZ = [["auto", merke("automatisch")], ["kein", merke("keiner")]];
var STUFEN = { muss: merke("Muss"), soll: merke("Soll – empfohlen"), kann: merke("Kann – optional") };
var ZEICHEN = { ok: "✓", fehlt: "!", muss: "✕", aus: "–" };
function einstellungenBlatt(p4) {
  const e6 = p4._daten.einstellungen;
  const teil = p4._blatt.teil || "speed";
  const kopf = b2`<div class="griff"></div><button class="zu" @click=${() => p4.zu()}>✕</button>
    <h3>${t3("Einstellungen")}</h3><div class="leise">${p4.istAdmin ? t3("gelten für die ganze Seite") : t3("nur Admins ändern")}</div>
    <div class="seg e-reiter">${TEILE2.map(([k2, name]) => b2`<button class=${k2 === teil ? "on" : ""} @click=${() => {
    p4._blatt = { ...p4._blatt, teil: k2 };
    p4.teilLaden(k2);
  }}>${t3(name)}${k2 === "einr" ? punkt2(p4) : A}</button>`)}</div>`;
  if (teil === "einr") return b2`${kopf}<div class="ek"><div class="ek-inhalt">${einrichtung(p4)}</div></div>`;
  if (teil === "diag") return b2`${kopf}<div class="ek"><div class="ek-inhalt">${diagnose(p4)}</div></div>`;
  if (teil === "zugang") return b2`${kopf}<div class="ek"><div class="ek-inhalt">${zugang(p4)}</div></div>`;
  if (teil === "arten") return b2`${kopf}<div class="ek"><div class="ek-inhalt">${artenTeil(p4)}</div></div>`;
  if (teil === "warn") return b2`${kopf}<div class="ek"><div class="ek-inhalt">${warnungenTeil(p4)}</div></div>`;
  if (!e6) return b2`${kopf}<div class="leer">${t3("lädt …")}</div>`;
  const inhalt = { speed: auswertung, plan: messplan, wlan: wlan2, meld: (q) => meldungenZeile(q) }[teil](p4, e6);
  return b2`${kopf}<div class="ek"><div class="ek-inhalt">${inhalt}</div></div>`;
}
function feld(name, wert2, einheit, admin, typ = "number") {
  return b2`<label class="ein"><input name=${name} type=${typ} min="0" step="1" .value=${wert2 ?? ""} ?disabled=${!admin}>${einheit ? b2`<small>${einheit}</small>` : A}</label>`;
}
function auswertung(p4, e6) {
  const admin = p4.istAdmin;
  const speichern = (ev) => {
    const f3 = ev.target.closest(".sheet");
    p4.einstellungenSpeichern({
      tarif_down: f3.querySelector("[name=tarif_down]").value || null,
      tarif_up: f3.querySelector("[name=tarif_up]").value || null,
      ab: f3.querySelector("[name=ab]").value || null
    });
  };
  return b2`
    <div class="ez"><span>${t3("Tarif Download")}</span>${feld("tarif_down", e6.tarif_down, "Mbit/s", admin)}</div>
    <div class="ez"><span>${t3("Tarif Upload")}</span>${feld("tarif_up", e6.tarif_up, "Mbit/s", admin)}</div>
    <div class="ez"><span>${t3("Auswerten ab")}<small>${t3("ältere Messungen zählen nicht")}</small></span>${feld("ab", e6.ab, "", admin, "date")}</div>
    ${admin ? b2`<div class="leiste" style="justify-content:flex-end;padding:4px 0"><button class="knopf haupt" @click=${speichern}>${t3("Speichern")}</button></div>` : A}
    ${p4._hinweis ? b2`<p class="fein">${p4._hinweis}</p>` : A}
    <div class="ez"><span>${t3("Belastete Messungen")}<small>${t3("über {n} Mbit/s Verkehr vor der Messung", { n: zahl(e6.schwelle) })}</small></span>${seg(tl(MODI), p4._opt.speedtest.grundlast, (v2) => p4.setze("speedtest", { grundlast: v2 }, p4._reiter === "speedtest"))}</div>
    <p class="hinweis">${t3("Die Auswahl „belastete Messungen“ gilt für das Wochenraster auf diesem Gerät.")}</p>`;
}
function messplan(p4, e6) {
  if (!e6.messplan) return A;
  const m3 = e6.messplan, z2 = e6.plan, o7 = e6.ookla, admin = p4.istAdmin;
  const setzen = (werte) => p4.messplanSetzen(werte);
  const belastet = e6.verkehr_mbit != null && e6.verkehr_mbit > e6.schwelle;
  const naechste = !m3.an ? `– (${t3("aus")})` : z2.misst ? t3("misst gerade …") : z2.wartet ? t3("verschoben – neuer Versuch {uhr}", { uhr: uhr(z2.neuer_versuch) }) : z2.naechste ? zeit(z2.naechste) : "–";
  return b2`<p class="hinweis" style="margin:2px 0 4px">${t3("Gemessen wird von der Ookla-Integration; dieser Plan sagt ihr, wann.")}</p>
    ${!o7.vorhanden ? b2`<div class="befund"><span class="punkt rot"></span><div><b>${t3("Ookla-Integration fehlt")}</b><p>${t3("Ohne sie kann der Plan nicht messen.")}</p></div></div>` : A}
    ${o7.misst_selbst ? b2`<div class="befund"><span class="punkt amber"></span><div><b>${t3("Ookla misst zusätzlich nach eigenem Takt")}</b><p>${t3("In den Ookla-Einstellungen ist „manuell“ aus – dann misst Ookla neben diesem Plan. Für einen einzigen Plan dort „manuell“ einschalten.")}</p></div></div>` : A}
    <div class="ez"><span>${t3("Automatisch messen")}</span><button class="sw ${m3.an ? "on" : ""}" role="switch" aria-checked=${m3.an ? "true" : "false"} ?disabled=${!admin} @click=${() => setzen({ an: !m3.an })}><i></i></button></div>
    <div class="ez"><span>${t3("Wie oft")}</span>${admin ? seg(TAKTE, m3.takt_h, (v2) => setzen({ takt_h: v2 })) : b2`<span class="leise">${t3("alle {n} h", { n: m3.takt_h })}</span>`}</div>
    ${volumen(e6.volumen)}
    <div class="ez"><span>${t3("Nur zwischen")}</span><span>
      <label class="ein"><input type="time" .value=${l3(m3.von === "24:00" ? "00:00" : m3.von)} ?disabled=${!admin} @change=${(ev) => setzen({ von: ev.target.value || "00:00" })}></label> –
      <label class="ein"><input type="time" .value=${l3(m3.bis === "24:00" ? "00:00" : m3.bis)} ?disabled=${!admin} @change=${(ev) => setzen({ bis: ev.target.value === "00:00" ? "24:00" : ev.target.value || "24:00" })}></label></span></div>
    <div class="ez"><span>${t3("Bei Verkehr im Heimnetz")}<small>${t3("über {n} Mbit/s", { n: zahl(e6.schwelle) })}</small></span>${admin ? seg(tl(VERKEHR), m3.verkehr, (v2) => setzen({ verkehr: v2 })) : b2`<span class="leise">${m3.verkehr === "warten" ? t3("verschieben") : t3("trotzdem messen")}</span>`}</div>
    <div class="ez"><span>${t3("Serie „{n}× messen“", { n: m3.serie })}<small>${t3("Durchläufe hintereinander, Ergebnis als Median")}</small></span>${admin ? seg(SERIE, m3.serie, (v2) => setzen({ serie: v2 })) : b2`<span class="leise">${m3.serie}×</span>`}</div>
    <div class="ez"><span>${t3("Server der Serie")}<small>${t3("alle Ookla-Tests reihum")}${o7.server ? ` – ${o7.server}` : ""}</small></span><span class="leise">${o7.tests ?? 0} ${o7.tests === 1 ? "Test" : "Tests"}</span></div>
    <div class="ez"><span>${t3("Verkehr gerade")}</span><span class=${belastet ? "rot-t" : "leise"}>${e6.verkehr_mbit == null ? "–" : `${zahl(e6.verkehr_mbit, 1)} Mbit/s – ${belastet ? t3("belastet") : t3("ruhig")}`}</span></div>
    <div class="ez"><span>${t3("Nächste Messung")}</span><span class="leise">${naechste}</span></div>
    <div class="ez"><span>${t3("Server und „manuell“")}<small>${t3("in Ookla eingestellt")}</small></span><button class="blau" @click=${() => {
    p4.zu();
    p4.oeffne("/config/integrations/integration/ookla_speedtest");
  }}>Ookla ›</button></div>
    ${p4._hinweisPlan ? b2`<p class="fein">${p4._hinweisPlan}</p>` : A}
    <p class="hinweis">${t3("Wird verschoben, versucht es der Plan alle 5 Minuten neu, höchstens 30 Minuten lang; danach misst er trotzdem und die Messung gilt als belastet.")}</p>`;
}
function volumen(v2) {
  if (!v2) return A;
  const text = v2.je_test_mb == null ? t3("Jede Messung kostet Datenvolumen – bei schnellen Anschlüssen einige hundert MB. Bei Mobilfunk mit Datenlimit lieber selten messen.") : v2.tests_tag ? t3(
    "Jede Messung kostet etwa {mb} MB Datenvolumen; mit diesem Plan {n} Messungen am Tag, rund {tag} MB am Tag und {monat} GB im Monat. Bei Mobilfunk mit Datenlimit lieber selten messen.",
    { mb: zahl(v2.je_test_mb), n: v2.tests_tag, tag: zahl(v2.tag_mb), monat: zahl(v2.monat_gb, 1) }
  ) : t3("Jede Messung kostet etwa {mb} MB Datenvolumen.", { mb: zahl(v2.je_test_mb) });
  return b2`<p class="hinweis volumen" style="margin:0 0 4px">${text}</p>`;
}
function wlan2(p4, e6) {
  const admin = p4.istAdmin;
  return b2`
    <div class="ez"><span>${t3("Schwacher Empfang unter")}<small>${t3("so meldet die Box den Empfang je Gerät")}</small></span>${admin ? seg(SCHWACH, e6.wlan_schwach, (v2) => p4.einstellungenSpeichern({ wlan_schwach: v2 })) : b2`<span class="leise">${e6.wlan_schwach} %</span>`}</div>
    <p class="hinweis">${t3("Kanal, Gast-WLAN und Bänder stellst du in der FRITZ!Box ein – die Seite ändert dort nichts.")}</p>`;
}
function zugang(p4) {
  if (!p4.istAdmin) return b2`<p class="hinweis" style="padding-top:8px">${t3("Den Zugang legen nur Admins fest.")}</p>`;
  const z2 = p4._daten.zugang;
  if (!z2) return p4._hinweisZugang ? b2`<p class="fein">${p4._hinweisZugang}</p>` : b2`<div class="leer">${t3("lädt …")}</div>`;
  const vorgeschaltet = z2.wahl === "extern" || z2.wahl === "ont" || z2.wahl === "auto" && z2.vorschlag_art === "extern";
  const adresseFeld = (ev) => ev.target.closest(".sheet").querySelector("input[name=zg-adresse]");
  const kennwortFeld = (ev) => ev.target.closest(".sheet").querySelector("input[name=zg-kennwort]");
  const speichern = (ev) => {
    const kw = kennwortFeld(ev);
    const werte = { adresse: adresseFeld(ev).value.trim() || null };
    if (kw && kw.value) werte.kennwort = kw.value;
    p4.zugangSetzen(werte, kw);
  };
  return b2`
    <div class="vs-kopf"><b>${t3("Vorschlag: {text}", { text: z2.vorschlag })}</b><br><span class="leise">${z2.belege.map((b3, i6) => b2`${i6 ? b2`<br>` : A}✓ ${b3}`)}</span></div>
    <div class="vs-stufe"><span>${t3("Internet kommt über")}</span><span></span></div>
    ${z2.wahlen.map((k2) => {
    const [name, unter] = WAHL2[k2] || [k2, ""];
    const text = k2 === "auto" ? t3("jetzt: {text}", { text: z2.vorschlag }) : t3(unter);
    return b2`<button class="zg" data-wahl=${k2} @click=${() => z2.wahl !== k2 && p4.zugangSetzen({ wahl: k2 })}><span class="zg-r ${z2.wahl === k2 ? "on" : ""}"></span><span>${t3(name)}<small>${text}</small></span></button>`;
  })}
    ${vorgeschaltet ? b2`<div class="vs-stufe"><span>${t3("Vorgeschaltetes Gerät")}</span><span></span></div>
      <label class="dg-feld">${t3("Adresse")}<input name="zg-adresse" inputmode="decimal" list="zg-adressen" .value=${l3(z2.adresse || z2.adresse_jetzt || z2.adressen[0] || "")}>
        <small>${t3("vorgeschlagen: {liste} – nur Adressen im eigenen Heimnetz", { liste: z2.adressen.join(", ") })}</small></label>
      <datalist id="zg-adressen">${z2.adressen.map((a3) => b2`<option value=${a3}></option>`)}</datalist>
      <label class="dg-feld">${t3("Kennwort der Weboberfläche")}<input name="zg-kennwort" type="password" autocomplete="off" placeholder=${z2.kennwort ? t3("hinterlegt – zum Ändern neu eingeben") : t3("wie beim Anmelden im Browser")}>
        <small>${t3("wird in Home Assistant gespeichert (wie bei anderen Integrationen), nie angezeigt")}</small></label>
      <div class="dg-knoepfe"><button class="amber" @click=${speichern}>${t3("Speichern")}</button>${z2.kennwort ? b2`<button @click=${() => p4.zugangSetzen({ kennwort_loeschen: true })}>${t3("Kennwort entfernen")}</button>` : A}</div>
      ${erkannt(z2.vorgeschaltet)}` : A}
    <div class="vs-stufe"><span>${t3("Ersatzzugang bei Ausfall")}</span><span></span></div>
    <div class="ez"><span>${t3("Ersatz")}<small>${t3("z. B. Mobilfunk-Stick an der FRITZ!Box, wenn DSL ausfällt")}</small></span>${seg(tl(ERSATZ), z2.ersatz_wahl, (v2) => p4.zugangSetzen({ ersatz: v2 }))}</div>
    ${p4._hinweisZugang ? b2`<p class="fein">${p4._hinweisZugang}</p>` : A}
    <div class="dg-knoepfe" style="margin-top:8px"><button @click=${() => p4.zugangSuchen()}>${t3("↻ Erneut suchen")}</button>
      <button @click=${() => p4.zuDiagnose(vorgeschaltet ? z2.adresse || z2.adresse_jetzt || z2.adressen[0] : null)}>${t3("🔬 Rohdaten abfragen ›")}</button></div>
    <p class="hinweis" style="margin-top:8px">${t3("Gesucht wird nur an der gespeicherten Adresse, am Vorschlag der FRITZ!Box und an den üblichen Modem-Adressen ({liste}) – kein Absuchen des Heimnetzes. Heimnetz liest nur.", { liste: z2.adressen.join(", ") })}</p>`;
}
function erkannt(v2) {
  if (!v2) return A;
  const unter = [v2.adresse, v2.quelle === "integration" ? t3("über die Integration in Home Assistant") : "", v2.gelesen ? t3("zuletzt gelesen {zeit}", { zeit: zeit(v2.gelesen) }) : ""].filter(Boolean).join(" · ");
  return b2`<div class="ez"><span>${t3("Erkannt")}<small>${unter || t3("noch nicht gesucht")}</small></span><span class="leise" style="color:var(--ink)">${v2.geraet ? `${v2.geraet}${v2.befund ? "" : " ✓"}` : "–"}</span></div>
    ${v2.befund ? b2`<div class="befund"><span class="punkt ${v2.befund.lage}"></span><div><b>${v2.befund.titel}</b><p>${v2.befund.text}</p></div></div>` : A}`;
}
function punkt2(p4) {
  const d3 = p4.istAdmin && p4._daten.einrichtung;
  if (!d3 || !d3.punkt) return A;
  return b2`<span class="e-punkt ${d3.punkt === "rot" ? "rot" : ""}"></span>`;
}
function einrichtung(p4) {
  if (!p4.istAdmin) return b2`<p class="hinweis" style="padding-top:8px">${t3("Was eingerichtet ist, sehen nur Admins.")}</p>`;
  const d3 = p4._daten.einrichtung;
  if (p4._hinweisEinr) return b2`<p class="fein">${p4._hinweisEinr}</p>`;
  if (!d3) return b2`<div class="leer">${t3("lädt …")}</div>`;
  const kopf = d3.muss_fehlt ? b2`<div class="vs-kopf"><b class="rot-t">${t3(d3.muss_fehlt === 1 ? "{n} Voraussetzung fehlt" : "{n} Voraussetzungen fehlen", { n: d3.muss_fehlt })}</b> – ${t3("was dann fehlt, steht in der Zeile. Fehlen FRITZ!Box Tools oder Recorder, auch unter Einstellungen › System › Reparaturen.")}</div>` : d3.soll_fehlt ? b2`<div class="vs-kopf"><b class="amber-t">${t3("{n} empfohlen", { n: d3.soll_fehlt })}</b> – ${t3(d3.soll_fehlt === 1 ? "Heimnetz läuft, mit diesem Teil zeigt es mehr." : "Heimnetz läuft, mit diesen Teilen zeigt es mehr.")}</div>` : b2`<div class="vs-kopf"><b class="ok">${t3("Alles Nötige ist eingerichtet.")}</b></div>`;
  return b2`${kopf}
    ${d3.stufen.map((s4) => b2`<div class="vs-stufe"><span>${t3(STUFEN[s4.stufe] || s4.stufe)}</span><span>${t3("{ok} von {von}", { ok: s4.ok, von: s4.von })}</span></div>
      ${s4.teile.map((x2) => b2`<div class="vs" data-teil=${x2.schluessel}><span class="vs-st ${x2.status}">${ZEICHEN[x2.status] || ""}</span><span>${x2.name}<small>${x2.wofuer}</small></span>
        <span class="vs-r">${x2.stand ? b2`<span class="leise">${x2.stand}</span>` : A}${x2.hinweis ? b2`<span class="leise">${x2.hinweis}</span>` : A}${x2.aktionen.map((a3) => b2`<button class=${a3.blau ? "blau" : ""} @click=${() => p4.einrichtungAktion(a3)}>${a3.text}</button>`)}</span></div>`)}`)}
    <p class="hinweis" style="margin-top:8px">${t3("Heimnetz installiert nichts selbst: die Knöpfe öffnen Home Assistant oder HACS an der richtigen Stelle. Nach einem Download aus HACS Home Assistant neu starten, dann einrichten. Geprüft wird beim Öffnen dieses Reiters.")}</p>`;
}
var ROH = "⟨geschwärzt⟩";
function diagnose(p4) {
  if (!p4.istAdmin) return b2`<p class="hinweis" style="padding-top:8px">${t3("Diese Abfrage können nur Admins starten.")}</p>`;
  const d3 = p4._diag;
  const kopf = b2`
    <p class="hinweis" style="margin:4px 0 6px">${t3("Hier fragt Heimnetz ein Gerät vor der FRITZ!Box (5G/LTE-Modem, Glasfaser-Modem) ab: erkennt Hersteller und Schnittstelle und zeigt alle Rohdaten, geschwärzt – damit der Entwickler weitere Geräte unterstützen kann.")} <span class="neu">BETA</span></p>
    <label class="dg-feld">${t3("Adresse des Modems")}<input name="adresse" inputmode="decimal" .value=${l3(d3.adresse)} ?disabled=${d3.laeuft} @input=${(ev) => {
    p4._diag = { ...p4._diag, adresse: ev.target.value };
  }}></label>
    <label class="dg-feld">${t3("Kennwort der Weboberfläche (optional)")}<input name="kennwort" type="password" autocomplete="off" placeholder=${t3("wie beim Anmelden im Browser")} ?disabled=${d3.laeuft}><small>${t3("wird nur für diese Abfrage verwendet und nicht gespeichert – leer: das unter 🌐 Zugang für diese Adresse hinterlegte")}</small></label>
    <div class="dg-knoepfe"><button class="amber" ?disabled=${d3.laeuft} @click=${() => p4.modemAbfragen()}>${d3.laeuft ? t3("⏳ fragt ab …") : t3("▶ Abfragen")}</button></div>
    ${d3.fehler ? b2`<p class="fein">${d3.fehler}</p>` : A}`;
  if (!d3.antwort) return b2`${kopf}<p class="hinweis" style="margin-top:8px">${t3("Nur Adressen im eigenen Heimnetz (z. B. 192.168.x.x). Heimnetz liest nur und ändert am Modem nichts.")}</p>`;
  return b2`${kopf}${ergebnis(p4, d3.antwort)}`;
}
function befundBlock(a3) {
  const b3 = a3.hinweis;
  if (!b3) return A;
  return b2`<div class="befund" style="margin-top:8px"><span class="punkt ${b3.lage}"></span><div><b>${b3.titel}</b><p>${b3.text}</p></div></div>`;
}
function erkanntZeile(e6) {
  if (!e6) return A;
  return b2`<div class="ez"><span>${t3("Erkannt")}<small>${e6.werte ? t3("Heimnetz liest dieses Gerät laufend") : t3("nur erkennen – Werte noch nicht unterstützt")}</small></span><span class="leise" style="color:var(--ink)">${e6.name}</span></div>`;
}
function rohAnzeige(daten) {
  const text = JSON.stringify(daten, null, 2);
  return text.split(ROH).flatMap((s4, i6) => i6 === 0 ? [s4] : [b2`<i>${ROH}</i>`, s4]);
}
function ergebnis(p4, a3) {
  if (!a3.abfragen.length) {
    return b2`${befundBlock(a3)}${a3.befund === "anmeldung_abgelehnt" ? b2`<div class="dg-knoepfe"><button @click=${() => p4.modemSpeichern()}>${t3("⬇ Trotzdem als Datei speichern")}</button></div>` : A}`;
  }
  const s4 = a3.summen;
  return b2`${befundBlock(a3)}${erkanntZeile(a3.erkannt)}
    <div class="vs-stufe" style="margin-top:6px"><span>${t3("Ergebnis")}</span><span>${t3("{ok} von {gesamt} Abfragen · {werte} Werte · {geschwaerzt} geschwärzt", { ok: s4.ok, gesamt: s4.gesamt, werte: s4.werte, geschwaerzt: s4.geschwaerzt })}</span></div>
    ${a3.abfragen.map((ab) => b2`<div class="dg-ab"><span class="vs-st ${ab.status === "ok" ? "ok" : "aus"}" style="width:18px;height:18px;font-size:10px">${ab.status === "ok" ? "✓" : "–"}</span><span>${ab.name}</span><code>${ab.angabe}</code></div>`)}
    <div class="dg-roh">${rohAnzeige(a3.daten)}</div>
    <div class="gh-warn"><b>${t3("Geschwärzt:")}</b> ${t3("IMEI, IMSI, ICCID, Rufnummer, Seriennummer, MAC- und öffentliche IP-Adressen, WLAN-Namen und -Kennwörter. Die Zellkennung bleibt drin – daraus lässt sich ungefähr bestimmen, wo das Modem steht.")}</div>
    <div class="dg-knoepfe"><button class="amber" @click=${() => p4.modemSpeichern()}>${t3("⬇ Als Datei speichern")}</button><button @click=${() => p4.modemKopieren()}>${t3("⧉ Kopieren")}</button></div>
    <p class="hinweis" style="margin-top:8px">${t3("Datei an den Entwickler schicken – per Mail oder als Anhang an ein GitHub-Issue. Heimnetz sendet selbst nichts.")}</p>`;
}

// src/ansichten/verbrauch.js
var W2 = 600;
var H3 = 160;
function verbrauch(p4, d3) {
  const o7 = p4._opt.verbrauch;
  if (!d3.verfuegbar) {
    return b2`<div class="glas-panel block"><div class="leer">${t3("Keine Zähler von FRITZ!Box Tools gefunden („GB empfangen/gesendet“).")}</div></div>`;
  }
  const k2 = d3.kacheln;
  const tage = d3.tage;
  const max = Math.max(0.1, ...tage.map((x2) => x2.down + x2.up)) * 1.1;
  const bw = W2 / Math.max(1, tage.length);
  const balken = tage.map((x2, i6) => {
    const h1 = x2.down / max * H3, h22 = x2.up / max * H3, h3 = Math.min(x2.speedtest, x2.down + x2.up) / max * H3;
    const d0 = /* @__PURE__ */ new Date(`${x2.tag}T12:00`);
    return w`<g><title>${datum(d0)}: ↓ ${zahl(x2.down, 1)} GB, ↑ ${zahl(x2.up, 1)} GB, ${t3("davon Speedtests {gb} GB", { gb: zahl(x2.speedtest, 2) })}</title>
      <rect x=${i6 * bw + 1} y=${H3 - h1} width=${Math.max(1, bw - 2)} height=${h1} rx="2" fill="var(--s1)"></rect>
      <rect x=${i6 * bw + 1} y=${H3 - h1 - h22} width=${Math.max(1, bw - 2)} height=${h22} rx="2" fill="var(--s2)"></rect>
      <rect x=${i6 * bw + 1} y=${H3 - h3} width=${Math.max(1, bw - 2)} height=${h3} fill="var(--s4)" opacity=".9"></rect></g>`;
  });
  return b2`
    ${k2 ? b2`<div class="glas-raster">
      ${kachel(t3("Heute"), b2`${zahl(k2.heute.down + k2.heute.up, 1)}<small> GB</small>`, `↓ ${zahl(k2.heute.down, 1)} · ↑ ${zahl(k2.heute.up, 1)}`)}
      ${kachel(t3("Diese Woche"), b2`${zahl(k2.woche, 1)}<small> GB</small>`, t3("seit Montag"))}
      ${kachel(t3("Dieser Monat"), b2`${zahl(k2.monat, 1)}<small> GB</small>`, t3("seit dem 1."))}
      ${kachel(t3("Ø je Tag"), b2`${zahl(k2.schnitt, 1)}<small> GB</small>`, t3("letzte {n} Tage", { n: o7.tage }))}
      ${kachel(t3("Davon Speedtests"), b2`${zahl(k2.speedtest, 1)}<small> GB</small>`, t3("geschätzt"))}
    </div>` : A}
    <div class="glas-panel block">
      <div class="block-kopf"><h3>${t3("Datenverbrauch der ganzen Box")}</h3>${seg([[7, t3("{n} Tage", { n: 7 })], [30, t3("{n} Tage", { n: 30 })]], o7.tage, (v2) => p4.setze("verbrauch", { tage: v2 }))}</div>
      <svg class="dia" viewBox="-30 -6 ${W2 + 36} ${H3 + 24}">
        ${[0, 0.25, 0.5, 0.75, 1].map((f3) => w`<line class="gitter" x1="0" x2=${W2} y1=${H3 - f3 * H3} y2=${H3 - f3 * H3}></line><text x="-4" y=${H3 - f3 * H3 + 3} text-anchor="end">${zahl(f3 * max)}</text>`)}
        ${balken}
        ${w`<text x="0" y=${H3 + 16}>${t3("vor {n} Tagen", { n: tage.length - 1 })}</text><text x=${W2} y=${H3 + 16} text-anchor="end">${t3("heute")}</text>`}
      </svg>
      <div class="legende"><span><i style="background:var(--s1)"></i>Download</span><span><i style="background:var(--s2)"></i>Upload</span><span><i style="background:var(--s4)"></i>${t3("davon Speedtests")}</span><span>${t3("GB je Tag")}</span></div>
      <p class="hinweis">${t3("Die FRITZ!Box zählt nur gesamt, nicht je Gerät.")}</p>
    </div>`;
}

// src/ansichten/protokoll.js
var ARTEN2 = [["journal", merke("Journal")], ["internet", "Internet"], ["wlan", merke("WLAN")], ["system", "System"]];
function protokoll(p4, d3) {
  const o7 = p4._opt.protokoll;
  const gruppen = [];
  for (const z2 of d3.eintraege) {
    const ueber = z2.t == null ? t3("ohne Zeit") : tag(z2.t);
    if (!gruppen.length || gruppen[gruppen.length - 1][0] !== ueber) gruppen.push([ueber, []]);
    gruppen[gruppen.length - 1][1].push(z2);
  }
  const journal = o7.art === "journal";
  return b2`<div class="glas-panel block">
    <div class="block-kopf"><h3>${journal ? t3("Journal – was hat sich geändert?") : t3("Protokoll der FRITZ!Box")}</h3>
      <span class="leise">${journal ? t3("aus den Prüfungen dieser Seite") : t3("Ereignisse der Box")}</span></div>
    <div class="leiste">${seg(tl(ARTEN2), o7.art, (v2) => p4.setze("protokoll", { art: v2 }), false)}</div>
    <div class="leiste">
      <input class="suche" placeholder=${t3("Suchen (Enter)")} .value=${o7.suche} @change=${(e6) => p4.setze("protokoll", { suche: e6.target.value })}>
      ${journal ? b2`<label class="leise" style="display:flex;gap:6px;align-items:center"><input type="checkbox" .checked=${o7.nur_warnungen}
        @change=${(e6) => p4.setze("protokoll", { nur_warnungen: e6.target.checked })}> ${t3("nur Warnungen")}</label>` : A}
    </div>
    ${gruppen.length ? gruppen.map(([ueber, zeilen]) => b2`<div class="gruppe">${ueber}</div>
      ${zeilen.map((z2) => b2`<div class="ereig"><span class="punkt ${journal ? punkt(z2.stufe) : "grau"}"></span>
        <time>${z2.t == null ? z2.roh_zeit : zeit(z2.t).split(" ").slice(-1)[0]}</time><span>${z2.text}</span></div>`)}`) : b2`<div class="leer">${t3("Keine Einträge.")}</div>`}
  </div>`;
}

// src/heimnetz-panel.js
var VERSION = true ? "0.28.1" : "entwicklung";
var REITER = [
  ["uebersicht", merke("Übersicht")],
  ["speedtest", merke("Speedtest")],
  ["geraete", merke("Geräte")],
  ["internet", merke("Internet")],
  // WU-0009: vorher „Funk“; WLAN steht jetzt unter Geräte
  ["verbrauch", merke("Verbrauch")],
  ["protokoll", merke("Protokoll")]
];
var ANSICHT = { uebersicht, speedtest, geraete: geraeteReiter, internet, verbrauch, protokoll };
var NEU_LADEN_MS = 6e4;
var KACHEL_WARTEN_MS = 150;
var ENTWURF = "heimnetz-melden-entwurf";
var meldeFelder = (f3) => ({ art: f3.art, text: f3.text.trim(), kontext: f3.kontext, version: f3.version, geraet: f3.geraet });
function istBildDatei(datei) {
  return !!datei && (!datei.type || datei.type.startsWith("image/"));
}
var TITEL = {
  ok: merke("Alles in Ordnung"),
  warnung: merke("Hinweise"),
  kritisch: merke("Störung"),
  box_fehlt: merke("FRITZ!Box nicht erreichbar")
};
var PUNKT3 = { ok: "", warnung: "amber", kritisch: "rot", box_fehlt: "grau" };
var standZeit = (s4) => zeit(s4).replace(new RegExp(`^${t3("Heute {uhr}", { uhr: "" })}`), "");
var HeimnetzPanel = class extends i4 {
  static properties = {
    hass: { attribute: false },
    narrow: { type: Boolean },
    panel: { attribute: false },
    _reiter: { state: true },
    _daten: { state: true },
    _opt: { state: true },
    _fehler: { state: true },
    _laedt: { state: true },
    _blatt: { state: true },
    _hinweis: { state: true },
    _hinweisPlan: { state: true },
    _hinweisEinr: { state: true },
    _diag: { state: true },
    _hinweisZugang: { state: true },
    _hinweisArten: { state: true },
    _hinweisWarn: { state: true },
    _toast: { state: true },
    _kachel: { state: true }
  };
  static styles = stil;
  constructor() {
    super();
    this._reiter = "uebersicht";
    this._daten = {};
    this._fehler = "";
    this._hinweis = "";
    this._hinweisPlan = "";
    this._hinweisEinr = "";
    this._diag = { adresse: "192.168.0.1", laeuft: false, antwort: null, fehler: "" };
    this._hinweisZugang = "";
    this._hinweisArten = "";
    this._hinweisWarn = "";
    this._blatt = null;
    this._toast = "";
    this._bilder = /* @__PURE__ */ new Map();
    const entwurf = this._entwurfLesen();
    if (entwurf) this._blatt = { art: "melden", form: { ...entwurf, version: VERSION }, vorher: null };
    this._opt = {
      speedtest: { tage: 84, groesse: "down", grundlast: "aus", server: "", tag: null, datum: null, stunde: null },
      geraete: { filter: "alle", suche: "", teil: "geraete" },
      internet: { sicht: "haupt" },
      // haupt = Zugangsart, ersatz = Ersatzzugang
      mobilfunk: { tage: 1 },
      verbrauch: { tage: 30 },
      protokoll: { art: "journal", nur_warnungen: false, suche: "" }
    };
  }
  connectedCallback() {
    super.connectedCallback();
    this._klickDaneben = (e6) => {
      if (!this._kachel || !this._kachel.fest) return;
      const pfad = e6.composedPath();
      if (!pfad.some((x2) => x2.classList && (x2.classList.contains("kpop") || x2.classList.contains("kachel")))) this.kachelWeg(true);
    };
    this.addEventListener("click", this._klickDaneben);
    this._takt = setInterval(() => this.laden(), NEU_LADEN_MS);
    this._einfuegen = (e6) => {
      if (!this._blatt || this._blatt.art !== "melden") return;
      const teile = [...e6.clipboardData && e6.clipboardData.items || []];
      const it = teile.find((i6) => i6.type && i6.type.startsWith("image/"));
      if (!it || teile.some((i6) => i6.type === "text/plain")) return;
      e6.preventDefault();
      this.bildDatei(it.getAsFile(), merke("Bild eingefügt"));
    };
    window.addEventListener("paste", this._einfuegen);
    if (this.hasUpdated && this.hass) this.laden();
  }
  disconnectedCallback() {
    clearTimeout(this._kachelTakt);
    this.removeEventListener("click", this._klickDaneben);
    clearInterval(this._takt);
    window.removeEventListener("paste", this._einfuegen);
    clearTimeout(this._toastZeit);
    clearTimeout(this._serieTakt);
    this._serieTakt = null;
    super.disconnectedCallback();
  }
  /** Sprache der Seite nach der Sprache des Nutzers in HA, bevor gezeichnet wird. */
  willUpdate(geaendert) {
    if (!geaendert.has("hass")) return;
    const vorher = sprache();
    if (waehle(this.hass) !== vorher && geaendert.get("hass")) this._sprachWechsel = true;
  }
  updated(geaendert) {
    if (this._kachel && (geaendert.has("_kachel") || geaendert.has("_daten"))) this._kachelLage();
    if (geaendert.has("hass") && !geaendert.get("hass") && this.hass) this.laden();
    else if (this._sprachWechsel) {
      this._sprachWechsel = false;
      this.laden();
    }
    const serie = this._daten.einstellungen && this._daten.einstellungen.serie;
    if (serie && !this._serieTakt) this._serieTakt = setTimeout(() => {
      this._serieTakt = null;
      this.laden();
    }, 1e4);
  }
  ws(typ, parameter = {}) {
    return this.hass.callWS({ type: `heimnetz/${typ}`, ...parameter, sprache: sprache() });
  }
  /** Übersicht (für den Kopf) und den gewählten Reiter laden. Nur die Antwort der neuesten Abfrage zählt –
   *  eine langsamere ältere (z. B. vor dem Wechsel des Zeitraums) darf nichts überschreiben. */
  async laden() {
    if (!this.hass) return;
    const nummer = this._abfrage = (this._abfrage || 0) + 1;
    const reiter = this._datenReiter;
    const auftraege = { uebersicht: this.ws("uebersicht") };
    if (reiter !== "uebersicht") auftraege[reiter] = this.ws(reiter, this._parameter(reiter));
    if (reiter === "speedtest" || this._blatt && this._blatt.art === "einstellungen") auftraege.einstellungen = this.ws("einstellungen");
    this._laedt = true;
    try {
      const werte = await Promise.all(Object.values(auftraege));
      if (nummer !== this._abfrage) return;
      const neu = { ...this._daten };
      Object.keys(auftraege).forEach((k2, i6) => {
        neu[k2] = werte[i6];
      });
      this._daten = neu;
      this._fehler = "";
      this._kachelSpeicher = /* @__PURE__ */ new Map();
      if (this._kachel && this._kachel.daten && reiter === "speedtest") this._kachelHolen(this._kachel.tag, this._kachel.stunde, this._kachel.fest, true);
    } catch (err) {
      if (nummer === this._abfrage) this._fehler = err && err.message || String(err);
    } finally {
      if (nummer === this._abfrage) this._laedt = false;
    }
  }
  /** Welche Daten der gewählte Reiter braucht; „Geräte“ lädt nur den gewählten Teil (Geräte oder WLAN). */
  get _datenReiter() {
    return this._reiter === "geraete" && this._opt.geraete.teil === "wlan" ? "wlan" : this._reiter;
  }
  _parameter(reiter) {
    const o7 = this._opt[reiter];
    switch (reiter) {
      case "speedtest":
        return {
          tage: o7.tage,
          groesse: o7.groesse,
          grundlast: o7.grundlast,
          ...o7.server ? { server: o7.server } : {},
          ...o7.datum ? { datum: o7.datum } : o7.tag != null ? { tag: o7.tag } : {}
        };
      case "internet":
        return { tage: this._opt.mobilfunk.tage };
      // Zeitraum des Mobilfunk-Verlaufs
      case "mobilfunk":
      case "verbrauch":
        return { tage: o7.tage };
      case "protokoll":
        return { art: o7.art, nur_warnungen: o7.nur_warnungen, suche: o7.suche };
      default:
        return {};
    }
  }
  geh(reiter) {
    this._reiter = reiter;
    this.kachelWeg(true);
    const scroll = this.shadowRoot && this.shadowRoot.querySelector(".scroll");
    if (scroll) scroll.scrollTop = 0;
    this.laden();
  }
  /** Auswahl eines Reiters ändern; `laden` = neu abfragen (Filter, die nur die Anzeige betreffen, nicht). */
  setze(reiter, werte, laden = true) {
    if (reiter === "speedtest" && laden) this._kachel = null;
    this._opt = { ...this._opt, [reiter]: { ...this._opt[reiter], ...werte } };
    if (laden) this.laden();
  }
  /** AN-0005: Popup zur Stundenkachel. Desktop beim Überfahren (`fest` = false), Klick oder Tipp hält es fest. Die
   *  Messungen holt die Integration nur für diese Kachel; die Antwort zählt nur, wenn noch dieselbe Kachel gezeigt wird. */
  kachelZeigen(tag2, stunde, fest) {
    clearTimeout(this._kachelTakt);
    const gleich = this._kachel && this._kachel.tag === tag2 && this._kachel.stunde === stunde;
    if (fest) {
      if (gleich && this._kachel.fest) {
        this._kachel = null;
        return;
      }
      if (gleich) {
        this._kachel = { ...this._kachel, fest };
        return;
      }
      this._kachelHolen(tag2, stunde, true);
      return;
    }
    if (gleich || this._kachel && this._kachel.fest) return;
    this._kachelTakt = setTimeout(() => this._kachelHolen(tag2, stunde, false), KACHEL_WARTEN_MS);
  }
  /** Messungen der Kachel holen – gemerkt je Auswahl, bis zum nächsten Laden des Reiters. */
  async _kachelHolen(tag2, stunde, fest, neu = false) {
    const o7 = this._opt.speedtest;
    const parameter = { tage: o7.tage, groesse: o7.groesse, grundlast: o7.grundlast, ...o7.server ? { server: o7.server } : {}, tag: tag2, stunde };
    const schluessel = JSON.stringify(parameter);
    this._kachelSpeicher = this._kachelSpeicher || /* @__PURE__ */ new Map();
    const gemerkt2 = !neu && this._kachelSpeicher.get(schluessel);
    if (!neu) this._kachel = { tag: tag2, stunde, fest, daten: gemerkt2 || null };
    if (gemerkt2) return;
    let ergebnis2;
    try {
      const daten = await this.ws("speedtest/kachel", parameter);
      this._kachelSpeicher.set(schluessel, daten);
      ergebnis2 = { daten };
    } catch (err) {
      ergebnis2 = { fehler: err && err.message || String(err) };
    }
    const k2 = this._kachel;
    if (k2 && k2.tag === tag2 && k2.stunde === stunde) this._kachel = { tag: tag2, stunde, fest: k2.fest, daten: null, ...ergebnis2 };
  }
  /** WU-0005: alle Werte einer Messung (Zeile in „Letzte Messungen“). */
  messungOeffnen(m3) {
    this.kachelWeg(true);
    this._blatt = { art: "messung", m: m3 };
  }
  /** AN-0007: Rückfrage im Fenster einer Messung zeigen oder zurücknehmen. */
  messungFrage(an) {
    const b3 = this._blatt;
    if (b3 && b3.art === "messung") this._blatt = { art: "messung", m: b3.m, frage: an };
  }
  /** AN-0007: Messung löschen (nur Admins; Kennung = Zeitpunkt wie in heimnetz/speedtest). Danach Fenster zu, Meldung,
   *  Ansicht neu laden; ein Fehler bleibt in der Rückfrage stehen. */
  async messungLoeschen() {
    const b3 = this._blatt;
    if (!b3 || b3.art !== "messung" || !this.istAdmin) return;
    const laufend = { ...b3, loescht: true, fehler: "" };
    this._blatt = laufend;
    try {
      await this.ws("messung/loeschen", { t: b3.m.t });
    } catch (err) {
      if (this._blatt === laufend) this._blatt = { ...laufend, loescht: false, fehler: err && err.message || String(err) };
      return;
    }
    if (this._blatt === laufend) this._blatt = null;
    this.toast(t3("Messung {zeit} gelöscht", { zeit: zeit(b3.m.t) }));
    this.laden();
  }
  kachelWeg(fest) {
    clearTimeout(this._kachelTakt);
    if (!this._kachel || this._kachel.fest && !fest) return;
    this._kachel = null;
  }
  /** Popup unter die Kachel setzen, bei zu wenig Platz darüber; seitlich innerhalb der Seite. */
  _kachelLage() {
    const w2 = this.shadowRoot;
    const pop = w2 && w2.querySelector(".kpop");
    const el = w2 && w2.querySelector(`.wr i[data-k="${this._kachel.tag}-${this._kachel.stunde}"]`);
    const app = w2 && w2.querySelector(".app");
    if (!pop || !el || !app) return;
    const a3 = app.getBoundingClientRect(), r5 = el.getBoundingClientRect();
    const x2 = Math.min(Math.max(8, r5.left - a3.left + r5.width / 2 - pop.offsetWidth / 2), a3.width - pop.offsetWidth - 8);
    const unten = r5.bottom - a3.top + 6, oben = r5.top - a3.top - pop.offsetHeight - 6;
    pop.style.left = `${Math.max(8, x2)}px`;
    pop.style.top = `${unten + pop.offsetHeight < a3.height - 8 || oben < 8 ? unten : oben}px`;
  }
  /** Einblendung öffnen; die Antwort zählt nur, wenn noch dieselbe Einblendung offen ist (nicht geschlossen,
   *  kein anderes Gerät angetippt). */
  async geraetOeffnen(kennung) {
    const blatt = { art: "geraet", kennung, laedt: true };
    this._blatt = blatt;
    let neu;
    try {
      neu = { art: "geraet", kennung, daten: await this.ws("geraet", { geraet: kennung, tage: 7 }) };
    } catch (err) {
      neu = { art: "geraet", kennung, fehler: err && err.message || String(err) };
    }
    if (this._blatt === blatt) this._blatt = neu;
  }
  zu() {
    this._blatt = null;
  }
  /** Art eines Geräts selbst wählen oder wieder automatisch (AN-0001, nur Admins). */
  async geraetArt(kennung, art2) {
    try {
      const daten = await this.ws("geraet/art", { geraet: kennung, art: art2 });
      if (this._blatt && this._blatt.kennung === kennung) this._blatt = { art: "geraet", kennung, daten };
      this.laden();
    } catch (err) {
      this.toast(t3("Art nicht gespeichert: {fehler}", { fehler: err && err.message || err }));
      this.requestUpdate();
    }
  }
  /** Fenster „Einstellungen“ (⚙ im Kopf); `teil` öffnet gleich einen Reiter (z. B. „zugang“ aus dem Reiter Internet). */
  einstellungenOeffnen(teil) {
    this._blatt = { art: "einstellungen", ...teil ? { teil } : {} };
    const z2 = this._daten.internet && this._daten.internet.zugang || this._daten.zugang;
    if (teil === "diag" && z2 && z2.adresse) this._diag = { ...this._diag, adresse: z2.adresse };
    this.laden();
    this.meldungenLaden();
    this.einrichtungLaden();
    if (teil && teil !== "einr") this.teilLaden(teil);
  }
  /** Reiter im Fenster Einstellungen gewählt: was nur dieser Reiter braucht, frisch von der Integration. */
  teilLaden(teil) {
    const laden = { einr: this.einrichtungLaden, zugang: this.zugangLaden, arten: this.artenLaden, warn: this.warnungenLaden }[teil];
    if (laden) laden.call(this);
  }
  /* ---- WU-0010: eigene Arten (⚙ › 🏷️ Arten, Fenster eines Geräts; nur Admins) ---- */
  async artenLaden() {
    if (!this.istAdmin) return;
    try {
      this._daten = { ...this._daten, arten: await this.ws("arten") };
      this._hinweisArten = "";
    } catch (err) {
      this._hinweisArten = t3("Arten nicht abrufbar: {fehler}", { fehler: err && err.message || err });
    }
  }
  /** Eigene Art anlegen; aus dem Fenster eines Geräts (`geraet`) gleich diesem zugeordnet. */
  async artNeu(symbol, name, geraet = null) {
    try {
      const a3 = await this.ws("art/neu", { symbol, name, ...geraet ? { geraet } : {} });
      this._daten = { ...this._daten, arten: a3 };
      this._hinweisArten = "";
      if (geraet) {
        const daten = await this.ws("geraet", { geraet, tage: 7 });
        if (this._blatt && this._blatt.kennung === geraet) this._blatt = { art: "geraet", kennung: geraet, daten };
      } else if (this._blatt) this._blatt = { ...this._blatt, artNeu: false };
      this.toast(t3("Art angelegt"));
      this.laden();
    } catch (err) {
      const text = err && err.message || String(err);
      if (geraet) this.toast(t3("Art nicht angelegt: {fehler}", { fehler: text }));
      else this._hinweisArten = text;
    }
  }
  async artAendern(art2, symbol, name) {
    try {
      this._daten = { ...this._daten, arten: await this.ws("art/aendern", { art: art2, symbol, name }) };
      this._hinweisArten = "";
      if (this._blatt) this._blatt = { ...this._blatt, artBearb: null };
      this.laden();
    } catch (err) {
      this._hinweisArten = err && err.message || String(err);
    }
  }
  async artLoeschen(art2) {
    try {
      this._daten = { ...this._daten, arten: await this.ws("art/loeschen", { art: art2 }) };
      this._hinweisArten = "";
      if (this._blatt) this._blatt = { ...this._blatt, artLoe: null };
      this.toast(t3("Art gelöscht"));
      this.laden();
    } catch (err) {
      this._hinweisArten = err && err.message || String(err);
    }
  }
  /* ---- WU-0010: Warnungen (⚙ › 🔔 Warnungen, Fenster eines Geräts; nur Admins) ---- */
  async warnungenLaden() {
    if (!this.istAdmin) return;
    try {
      this._daten = { ...this._daten, warnungen: await this.ws("warnungen") };
      this._hinweisWarn = "";
    } catch (err) {
      this._hinweisWarn = t3("Warnungen nicht abrufbar: {fehler}", { fehler: err && err.message || err });
    }
  }
  async warnungenSetzen(werte) {
    try {
      this._daten = { ...this._daten, warnungen: await this.ws("warnungen/setzen", werte) };
      this._hinweisWarn = "";
    } catch (err) {
      this._hinweisWarn = err && err.message || String(err);
      this.requestUpdate();
    }
  }
  /** Ausnahme eines Geräts: immer, nie oder wie seine Gruppe (Fenster des Geräts und ⚙ › Warnungen). */
  async warnungGeraet(kennung, wert2) {
    try {
      const daten = await this.ws("warnungen/geraet", { geraet: kennung, wert: wert2 });
      if (daten && this._blatt && this._blatt.art === "geraet" && this._blatt.kennung === kennung) this._blatt = { art: "geraet", kennung, daten };
      if (this._blatt && this._blatt.art === "einstellungen") this.warnungenLaden();
    } catch (err) {
      this.toast(t3("Nicht gespeichert: {fehler}", { fehler: err && err.message || err }));
    }
  }
  async testnachricht() {
    try {
      const { dienste } = await this.ws("warnungen/test");
      const w2 = this._daten.warnungen;
      const ziel = w2 && (w2.ziele.find((z2) => z2.name === w2.ziel) || {}).text;
      this.toast(dienste.length ? t3("Testnachricht an {ziel} geschickt", { ziel: ziel || dienste.join(", ") }) : t3("Keine Nachricht eingestellt – nur das Ereignis „heimnetz_warnung“ ausgelöst"));
      this._hinweisWarn = "";
    } catch (err) {
      this._hinweisWarn = err && err.message || String(err);
    }
  }
  /* ---- WU-0009: ⚙ › 🌐 Zugang (nur Admins; erkennen und prüfen macht die Integration) ---- */
  async zugangLaden() {
    if (!this.istAdmin) return;
    try {
      this._daten = { ...this._daten, zugang: await this.ws("zugang") };
      this._hinweisZugang = "";
    } catch (err) {
      this._hinweisZugang = t3("Zugang nicht abrufbar: {fehler}", { fehler: err && err.message || err });
    }
  }
  /** Wahl, Adresse, Ersatz oder Kennwort speichern. Das Kennwort geht nur mit diesem Befehl mit, wird nie im
   *  Zustand behalten und danach im Feld gelöscht; zurück kommt nur „hinterlegt ja/nein“. */
  async zugangSetzen(werte, feld2 = null) {
    try {
      this._daten = { ...this._daten, zugang: await this.ws("zugang/setzen", werte) };
      this._hinweisZugang = "";
      if (feld2) feld2.value = "";
      this.laden();
    } catch (err) {
      this._hinweisZugang = err && err.message || String(err);
      this.requestUpdate();
    }
  }
  async zugangSuchen() {
    try {
      const { gesucht, ...zugang2 } = await this.ws("zugang/suchen");
      this._daten = { ...this._daten, zugang: zugang2 };
      this._hinweisZugang = "";
      this.toast(!gesucht ? t3("Eben erst gesucht – in einer halben Minute wieder") : zugang2.vorgeschaltet ? t3("Gesucht: FRITZ!Box und vorgeschaltetes Gerät neu gefragt") : t3("Gesucht: FRITZ!Box neu gefragt"));
      this.laden();
    } catch (err) {
      this._hinweisZugang = err && err.message || String(err);
    }
  }
  /** „🔬 Rohdaten abfragen ›“: in den Reiter Diagnose, die Adresse des vorgeschalteten Geräts übernehmen. */
  zuDiagnose(adresse) {
    if (adresse) this._diag = { ...this._diag, adresse };
    this._blatt = { ...this._blatt, teil: "diag" };
  }
  /** WU-0007: was eingerichtet ist und was fehlt – geprüft beim Öffnen (nur Admins; die Integration erkennt). */
  async einrichtungLaden() {
    if (!this.istAdmin) return;
    try {
      const d3 = await this.ws("einrichtung");
      this._daten = { ...this._daten, einrichtung: d3 };
      this._hinweisEinr = "";
    } catch (err) {
      this._hinweisEinr = t3("Einrichtung nicht abrufbar: {fehler}", { fehler: err && err.message || err });
    }
  }
  /** WU-0007: Knopf einer Voraussetzung – extern im neuen Fenster, sonst Home Assistant an der Stelle öffnen. */
  einrichtungAktion(a3) {
    if (a3.extern) {
      window.open(a3.ziel, "_blank", "noopener");
      return;
    }
    this.zu();
    this.oeffne(a3.ziel);
  }
  /** WU-0008: Rohdaten eines vorgeschalteten Modems abfragen (nur Admins). Das Kennwort geht nur mit dieser Abfrage
      mit, wird nie im Zustand behalten und nach der Abfrage im Feld gelöscht. */
  async modemAbfragen() {
    const blatt = this.shadowRoot.querySelector(".sheet");
    const feld2 = blatt && blatt.querySelector("input[name=kennwort]");
    const adresse = (blatt && blatt.querySelector("input[name=adresse]").value || "").trim();
    const kennwort = feld2 && feld2.value || null;
    this._diag = { ...this._diag, adresse, laeuft: true, fehler: "" };
    try {
      const antwort = await this.ws("modem", { adresse, kennwort });
      this._diag = { ...this._diag, adresse, laeuft: false, antwort, fehler: "" };
    } catch (err) {
      this._diag = { ...this._diag, laeuft: false, fehler: t3("Abfrage nicht möglich: {fehler}", { fehler: err && err.message || err }) };
    } finally {
      if (feld2) feld2.value = "";
    }
  }
  /** WU-0008: geschwärzte Antwort als Datei – Inhalt = Antwort des WS-Befehls plus Heimnetz-Version und Zeitpunkt. */
  _modemDatei() {
    return JSON.stringify({ heimnetz: VERSION, zeit: (/* @__PURE__ */ new Date()).toISOString(), antwort: this._diag.antwort }, null, 2);
  }
  modemSpeichern() {
    if (!this._diag.antwort) return;
    const name = `heimnetz-modem-${(/* @__PURE__ */ new Date()).toISOString().slice(0, 10)}.json`;
    const blob = new Blob([this._modemDatei()], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a3 = document.createElement("a");
    a3.href = url;
    a3.download = name;
    a3.click();
    setTimeout(() => URL.revokeObjectURL(url), 1e3);
    this.toast(t3("Gespeichert: {name}", { name }));
  }
  modemKopieren() {
    if (!this._diag.antwort) return;
    if (navigator.clipboard) navigator.clipboard.writeText(this._modemDatei()).catch(() => {
    });
    this.toast(t3("Kopiert – {n} Werte", { n: this._diag.antwort.summen.werte }));
  }
  /* ---- Melden (Tickets) ---- */
  toast(text) {
    this._toast = text;
    clearTimeout(this._toastZeit);
    this._toastZeit = setTimeout(() => {
      this._toast = "";
    }, 3500);
  }
  meldenAuf() {
    const reiter = t3((REITER.find(([k2]) => k2 === this._reiter) || [, this._reiter])[1]);
    const kontext = [
      reiter,
      this._teilText(),
      this._blatt ? t3("Dialog „{art}“", { art: this._blatt.art }) : ""
    ].filter(Boolean).join(" · ");
    const form = { art: "fehler", text: "", kontext, version: VERSION, geraet: this.narrow ? t3("Handy") : "Desktop", stand: true, zelle: false, bilder: [] };
    this._blatt = { art: "melden", form, vorher: this._blatt };
    this.entwurfMerken();
  }
  /** Gewählter Teil des Reiters in Worten (für den Kontext einer Meldung). */
  _teilText() {
    if (this._reiter === "geraete" && this._opt.geraete.teil === "wlan") return t3("WLAN");
    if (this._reiter !== "internet") return "";
    if (this._opt.internet.sicht === "ersatz") return t3("Ersatz");
    const z2 = this._daten.internet && this._daten.internet.zugang;
    return z2 ? z2.titel : "";
  }
  /** Teil des Reiters als Kennung (Stand der Seite einer Meldung). */
  get _teil() {
    return this._reiter === "geraete" ? this._opt.geraete.teil : this._reiter === "internet" ? this._opt.internet.sicht : null;
  }
  meldenZu() {
    const b3 = this._blatt && this._blatt.art === "github" ? this._blatt.vorher : this._blatt;
    this._blatt = b3 && b3.vorher || null;
    this._entwurfWeg();
  }
  /* ---- WU-0006: öffentlich auf GitHub melden ---- */
  /** Vom Melde-Dialog zur Vorschau des Issues; ohne Text geht es nicht weiter (wie „Senden“). */
  githubAuf() {
    const melden = this._blatt, f3 = melden.form;
    if (!f3.text.trim()) {
      f3.fehler = t3("Bitte kurz beschreiben");
      this.requestUpdate();
      return;
    }
    f3.fehler = "";
    this._blatt = { art: "github", vorher: melden, vorschau: null };
    this._githubVorschau();
  }
  githubZurueck() {
    if (this._blatt && this._blatt.art === "github") this._blatt = this._blatt.vorher;
  }
  githubZelle(an) {
    const b3 = this._blatt;
    if (b3.vorher.form.sendet) return;
    b3.vorher.form.zelle = an;
    this._blatt = { ...b3, vorschau: null };
    this.entwurfMerken();
    this._githubVorschau();
  }
  /** Titel, Text und Link baut die Integration; die Antwort zählt nur, solange noch dieselbe Vorschau offen ist. */
  async _githubVorschau() {
    const b3 = this._blatt, melden = b3.vorher;
    let neu;
    try {
      neu = { ...b3, vorschau: await this.ws("meldung/github", { meldung: meldeFelder(melden.form), zelle: !!melden.form.zelle }), fehler: "" };
    } catch (err) {
      neu = { ...b3, fehler: t3("Vorschau nicht abrufbar: {fehler}", { fehler: err && err.message || err }) };
    }
    if (this._blatt === b3) this._blatt = neu;
  }
  /** Entwurf (Art, Text, Bilder …) im Browser merken; Speicher voll oder gesperrt → ohne Sicherung weiter. */
  entwurfMerken() {
    const b3 = this._blatt && this._blatt.art === "github" ? this._blatt.vorher : this._blatt;
    if (!b3 || b3.art !== "melden") return;
    const { sendet, fehler, ...form } = b3.form;
    try {
      sessionStorage.setItem(ENTWURF, JSON.stringify(form));
    } catch {
      try {
        sessionStorage.setItem(ENTWURF, JSON.stringify({ ...form, bilder: [] }));
      } catch {
        this._entwurfWeg();
      }
    }
  }
  _entwurfLesen() {
    try {
      const f3 = JSON.parse(sessionStorage.getItem(ENTWURF) || "null");
      return f3 && typeof f3.text === "string" && Array.isArray(f3.bilder) ? f3 : null;
    } catch {
      return null;
    }
  }
  _entwurfWeg() {
    try {
      sessionStorage.removeItem(ENTWURF);
    } catch {
    }
  }
  /** Meldung senden, danach jedes Bild einzeln; die Rückmeldung sagt, wie viele Bilder angekommen sind.
   *  `github` (WU-0006): aus der Vorschau – das vorausgefüllte Issue, genau wie gezeigt, in einem neuen Fenster öffnen
   *  (noopener: GitHub bekommt keinen Zugriff auf diese Seite) und lokal speichern wie bisher. Geöffnet wird noch im
   *  Klick, vor jeder Antwort – danach sperren Safari und die App von Home Assistant das Fenster. */
  async meldungSenden(github = false) {
    const b3 = this._blatt, melden = b3.art === "github" ? b3.vorher : b3, f3 = melden.form;
    if (!f3.text.trim()) {
      f3.fehler = t3("Bitte kurz beschreiben");
      this.requestUpdate();
      return;
    }
    const vorschau = github ? b3.vorschau : null;
    if (github && !vorschau) return;
    if (vorschau) window.open(vorschau.url, "_blank", "noopener");
    const seite = f3.stand ? { reiter: this._reiter, teil: this._teil, dialog: melden.vorher ? melden.vorher.art : null } : null;
    f3.sendet = true;
    f3.fehler = "";
    this.requestUpdate();
    let neu;
    try {
      neu = await this.ws("meldung/neu", { meldung: { ...meldeFelder(f3), seite } });
    } catch (err) {
      f3.sendet = false;
      f3.fehler = t3("Nicht gesendet: {fehler}", { fehler: err && err.message || err });
      this.requestUpdate();
      return;
    }
    let angekommen = 0, fehler = "";
    for (const bild of f3.bilder) {
      try {
        angekommen = (await this.ws("meldung/bild", { meldung_id: neu.id, bild: bild.url })).bilder;
      } catch (err) {
        fehler = err && err.message || String(err);
      }
    }
    if (this._blatt === b3) this._blatt = melden.vorher || null;
    this._entwurfWeg();
    delete this._daten.meldungen;
    const mit = angekommen ? t3(angekommen === 1 ? " mit {n} Bild" : " mit {n} Bildern", { n: angekommen }) : "";
    const fehlt2 = f3.bilder.length - angekommen;
    const verloren = fehlt2 ? t3(fehlt2 === 1 ? " · {n} Bild kam nicht an" : " · {n} Bilder kamen nicht an", { n: fehlt2 }) + (fehler ? ` (${fehler})` : "") : "";
    const gemeldet = !vorschau ? t3("Danke – gemeldet als {ticket}", { ticket: neu.ticket }) : vorschau.ticket === neu.ticket ? t3("Gemeldet als {ticket} – GitHub öffnet sich in einem neuen Fenster", { ticket: neu.ticket }) : t3("Gemeldet als {ticket} – im Issue auf GitHub steht {vorher}, bitte dort ändern", { ticket: neu.ticket, vorher: vorschau.ticket });
    this.toast(gemeldet + mit + verloren);
  }
  /** Bild/Video → verkleinertes JPEG in das offene Melde-Fenster. */
  bildAus(quelle, b3, h3, wie) {
    const blatt = this._blatt;
    if (!blatt || blatt.art !== "melden") return;
    const B2 = blatt.form.bilder;
    if (B2.length >= MB_MAX) {
      this.toast(t3("Höchstens {n} Bilder", { n: MB_MAX }));
      return;
    }
    const k2 = Math.min(1, MB_PX / Math.max(b3, h3)), c4 = document.createElement("canvas");
    c4.width = Math.round(b3 * k2);
    c4.height = Math.round(h3 * k2);
    c4.getContext("2d").drawImage(quelle, 0, 0, c4.width, c4.height);
    const url = c4.toDataURL("image/jpeg", 0.82);
    B2.push({ url, b: c4.width, h: c4.height, kb: Math.round(url.length * 0.75 / 1024) });
    this.requestUpdate();
    this.entwurfMerken();
    this.toast(t3(wie));
  }
  /** FE-0001: jede Datei versuchen, die kein anderer bekannter Typ ist; geladen über eine Objekt-Adresse (der Browser
   *  erkennt das Bild am Inhalt, auch ohne Typ). Jeder Schritt meldet sich – nie mehr stilles „0 von 3“. */
  bildDatei(datei, wie) {
    if (!datei) return;
    if (!istBildDatei(datei)) {
      this.toast(t3("Kein Bild ({typ}) – bitte ein Bild wählen", { typ: datei.type }));
      return;
    }
    this.toast(t3("Bild wird geladen …"));
    let adresse;
    try {
      adresse = URL.createObjectURL(datei);
    } catch {
      this.toast(t3("Bild nicht lesbar"));
      return;
    }
    const img = new Image();
    const fertig = () => URL.revokeObjectURL(adresse);
    img.onload = () => {
      try {
        this.bildAus(img, img.naturalWidth || img.width, img.naturalHeight || img.height, wie);
      } catch (err) {
        this.toast(t3("Bild nicht übernommen: {fehler}", { fehler: err && err.message || err }));
      } finally {
        fertig();
      }
    };
    img.onerror = () => {
      fertig();
      this.toast(t3("Bild nicht lesbar – bitte ein anderes wählen"));
    };
    img.src = adresse;
  }
  async fensterAufnehmen() {
    let strom;
    try {
      strom = await navigator.mediaDevices.getDisplayMedia({ video: { displaySurface: "browser" }, preferCurrentTab: true });
      const v2 = document.createElement("video");
      v2.srcObject = strom;
      v2.muted = true;
      await v2.play();
      await new Promise((r5) => setTimeout(r5, 300));
      if (!v2.videoWidth || !v2.videoHeight) throw new Error("leer");
      this.bildAus(v2, v2.videoWidth, v2.videoHeight, merke("Bild aufgenommen"));
    } catch {
      this.toast(t3("Aufnahme abgebrochen"));
    } finally {
      if (strom) strom.getTracks().forEach((t7) => t7.stop());
    }
  }
  async meldungenLaden() {
    try {
      this._daten = { ...this._daten, meldungen: await this.ws("meldungen") };
    } catch (err) {
      this.toast(t3("Meldungen nicht abrufbar: {fehler}", { fehler: err && err.message || err }));
    }
  }
  meldungenOeffnen() {
    this._blatt = { art: "meldungen", filter: this._blatt && this._blatt.filter || "offen" };
    this.meldungenLaden();
  }
  /** Bild eines Tickets für die Liste; lädt beim ersten Zeigen nach (nur über die Verbindung). */
  meldungBild(m3, i6) {
    const k2 = `${m3.id}:${i6}`;
    if (!this._bilder.has(k2)) {
      this._bilder.set(k2, null);
      this.ws("meldung/bild_zeigen", { meldung_id: m3.id, nr: i6 }).then((r5) => {
        this._bilder.set(k2, r5.url);
        this.requestUpdate();
      }).catch(() => {
        this._bilder.delete(k2);
      });
    }
    return this._bilder.get(k2);
  }
  bildGross(m3, i6) {
    this._blatt = { art: "bild", m: m3, i: i6, filter: this._blatt && this._blatt.filter };
  }
  async meldungStatus(m3, status) {
    try {
      await this.ws("meldung/status", { meldung_id: m3.id, status });
      await this.meldungenLaden();
    } catch (err) {
      this.toast(t3("Nicht geändert: {fehler}", { fehler: err && err.message || err }));
    }
  }
  async meldungLoeschen(m3) {
    try {
      await this.ws("meldung/loeschen", { meldung_id: m3.id });
      this.toast(t3("{ticket} gelöscht", { ticket: m3.ticket }));
      await this.meldungenLaden();
    } catch (err) {
      this.toast(t3("Nicht gelöscht: {fehler}", { fehler: err && err.message || err }));
    }
  }
  meldungenKopieren() {
    const liste = this._daten.meldungen || [];
    if (navigator.clipboard) navigator.clipboard.writeText(alsMarkdown(liste)).catch(() => {
    });
    this.toast(t3("{n} Meldungen als Markdown kopiert", { n: liste.length }));
  }
  async einstellungenSpeichern(werte) {
    try {
      const neu = await this.ws("einstellungen/setzen", werte);
      this._daten = { ...this._daten, einstellungen: neu };
      this._hinweis = "";
      this.laden();
    } catch (err) {
      this._hinweis = err && err.message || String(err);
    }
  }
  async messplanSetzen(werte) {
    try {
      const neu = await this.ws("messplan/setzen", werte);
      this._daten = { ...this._daten, einstellungen: neu };
      this._hinweisPlan = "";
    } catch (err) {
      this._hinweisPlan = err && err.message || String(err);
      this.requestUpdate();
    }
  }
  /** WU-0001: Serie „n× messen“ starten; während sie läuft, öfter nachsehen. */
  async serieStarten() {
    try {
      const neu = await this.ws("serie");
      this._daten = { ...this._daten, einstellungen: neu };
      this._hinweisPlan = "";
    } catch (err) {
      this._hinweisPlan = err && err.message || String(err);
    }
  }
  async jetztMessen() {
    try {
      const neu = await this.ws("messen");
      this._daten = { ...this._daten, einstellungen: neu };
      this._hinweisPlan = "";
    } catch (err) {
      this._hinweisPlan = err && err.message || String(err);
    }
  }
  /** Andere Seite von Home Assistant öffnen (z. B. Ookla-Einstellungen). */
  oeffne(pfad) {
    history.pushState(null, "", pfad);
    window.dispatchEvent(new CustomEvent("location-changed", { detail: { replace: false } }));
  }
  get istAdmin() {
    return !!(this.hass && this.hass.user && this.hass.user.is_admin);
  }
  _kopf(u3) {
    if (!u3) return b2`<div class="glas-panel glas-kopf"><div class="glas-klein">Heimnetz</div><div class="leise">${t3("lädt …")}</div></div>`;
    const befunde = u3.befunde || [];
    const kritisch = befunde.filter((b3) => b3.stufe === "kritisch").length;
    const warnung = befunde.filter((b3) => b3.stufe === "warnung").length;
    const unter = !u3.box_erreichbar ? t3("Die Box antwortet nicht · Home Assistant versucht es jede Minute") : [u3.zugang ? u3.zugang.kopf : u3.internet && u3.internet.technik, u3.internet && u3.internet.ok ? t3("Internet erreichbar") : t3("kein Internet")].filter(Boolean).join(" · ");
    return b2`
      <div class="glas-panel glas-kopf">
        <div>
          <div class="glas-klein">Heimnetz · ${t3("Stand {zeit}", { zeit: standZeit(u3.stand) })}</div>
          <div class="kopf-titel" style="margin-top:6px">
            <span class="punkt ${PUNKT3[u3.gesamt] ?? "grau"}"></span>
            <span class="glas-kw" style="font-size:30px">${TITEL[u3.gesamt] ? t3(TITEL[u3.gesamt]) : u3.gesamt}</span>
          </div>
          <div class="leise" style="margin-top:6px">${unter}</div>
        </div>
        <div class="chips">
          ${kritisch ? b2`<button class="chip glas-panel rot" @click=${() => this.geh("uebersicht")}>● ${t3(kritisch > 1 ? "{n} Störungen" : "{n} Störung", { n: kritisch })}</button>` : A}
          ${warnung ? b2`<button class="chip glas-panel amber" @click=${() => this.geh("uebersicht")}>⚠ ${t3(warnung > 1 ? "{n} Hinweise" : "{n} Hinweis", { n: warnung })}</button>` : A}
          <button class="chip glas-panel" title=${t3("Einstellungen")} @click=${() => this.einstellungenOeffnen()}>⚙</button>
        </div>
      </div>`;
  }
  _blattInhalt() {
    const b3 = this._blatt;
    if (!b3) return A;
    const art2 = { einstellungen: einstellungenBlatt, melden: meldenBlatt, github: githubBlatt, meldungen: meldungenBlatt, bild: bildBlatt, messung: messungBlatt }[b3.art];
    return art2 ? art2(this) : geraetBlatt(this, b3);
  }
  render() {
    const hell = !(this.hass && this.hass.themes && this.hass.themes.darkMode);
    const u3 = this._daten.uebersicht;
    const ansicht = ANSICHT[this._reiter];
    const daten = this._reiter === "uebersicht" ? u3 : this._daten[this._datenReiter];
    return b2`
      <div class="wurzel ${hell ? "hell" : ""}" lang=${sprache()}>
        <div class="ui"><div class="app">
          <div class="glas-bg" data-phase=${phase(this.hass && this.hass.states["sun.sun"])}>
            <i class="k1"></i><i class="k2"></i><i class="k3"></i>
          </div>
          ${this.narrow ? b2`<button class="menue-knopf glas-panel" title=${t3("Menü")} @click=${() => this.dispatchEvent(new Event("hass-toggle-menu", { bubbles: true, composed: true }))}>☰</button>` : A}
          <nav class="glas-nav glas-panel sechs">
            ${REITER.map(([k2, name]) => b2`<button class=${k2 === this._reiter ? "on" : ""} @click=${() => this.geh(k2)}>${t3(name)}</button>`)}
          </nav>
          <div class="scroll" @scroll=${() => this.kachelWeg(true)}><div class="seite ${this._laedt ? "laden" : ""}">
            ${this._kopf(u3)}
            ${this._fehler ? b2`<div class="glas-panel fehler-band">${t3("Daten nicht abrufbar: {fehler}", { fehler: this._fehler })}</div>` : A}
            ${daten || this._reiter === "geraete" ? ansicht(this, daten) : b2`<div class="glas-panel block"><div class="leer">${t3("lädt …")}</div></div>`}
            <div class="leise" style="text-align:center;padding:8px">Heimnetz ${VERSION}</div>
          </div></div>
          <div class="schleier ${this._blatt ? "an" : ""}" @click=${() => this.zu()}></div>
          <div class="sheet glas-panel ${this._blatt ? "an" : ""}">${this._blatt && !["melden", "github"].includes(this._blatt.art) ? meldenKnopf(this, true) : A}${this._blattInhalt()}</div>
          ${this._blatt ? A : meldenKnopf(this)}
          <div class="toast glas-panel ${this._toast ? "an" : ""}" role="status">${this._toast}</div>
          ${this._kachel && this._reiter === "speedtest" ? kachelPopup(this) : A}
        </div></div>
      </div>`;
  }
};
if (!customElements.get("heimnetz-panel")) customElements.define("heimnetz-panel", HeimnetzPanel);
export {
  HeimnetzPanel,
  REITER,
  VERSION,
  istBildDatei
};
