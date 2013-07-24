/*
 * Copyright (c) 2012, Moriyoshi Koizumi.  All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 
 * Redistributions of source code must retain the above copyright notice,
 * this list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution.
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */
(function ($) {
  "use strict";
  var PALETTE_TABLES = {
    dark: [
      "e3e3e7","e5e5e6","ecdfec","e6dfec","dfdfe6","dfe6e6","dfe6df","e8e8e0","f9f2df","f4e9df","ecdfdf","e5e4e2",
      "c7c7cf","cacbcd","d9bfd9","ccbfd9","bfbfcc","bfcccc","bfccbf","d1d1c0","f2e6bf","e9d4bf","d9bfbf","ccc8c5",
      "ababb7","b0b1b4","c69fc6","b39fc6","9f9fb3","9fb3b3","9fb39f","babaa1","ecd99f","ddbe9f","c69f9f","b2ada7",
      "8f8f9f","96979b","b380b3","9980b3","808099","809999","809980","a4a481","e6cc80","d2a980","b38080","99928a",
      "727287","7b7d81","9f609f","80609f","606080","608080","608060","8d8d62","dfbf60","c79360","9f6060","7f766d",
      "56566f","616368","8c408c","66408c","404066","406666","406640","767642","d9b340","bc7d40","8c4040","655b50",
      "3a3a57","46494f","792079","4d2079","20204d","204d4d","204d20","5f5f23","d2a620","b06820","792020","4c3f32",
      "1e1e3f","2c2f36","660066","330066","000033","003333","003300","484803","cc9900","a55200","660000","322415"
    ],
    neutral: [
      "f2dfec","ece6f2","dfdff2","e6ecf9","dfecec","e6ece6","f2f2df","fff9df","fceddf","f2dfdf","ece6df","ffffff",
      "e6bfd9","d9cce6","bfbfe6","ccd9f2","bfd9d9","ccd9cc","e6e6bf","fff2bf","f8dabf","e6bfbf","d9ccbf","d8d8d8",
      "d99fc6","c6b3d9","9f9fd9","b3c6ec","9fc6c6","b3c6b3","d9d99f","ffec9f","f5c89f","d99f9f","c6b39f","b6b6b6",
      "cc80b3","b399cc","8080cc","99b3e6","80b3b3","99b399","cccc80","ffe680","f2b580","cc8080","b39980","929292",
      "bf609f","9f80bf","6060bf","809fdf","609f9f","809f80","bfbf60","ffdf60","eea360","bf6060","9f8060","6d6d6d",
      "b3408c","8c66b3","4040b3","668cd9","408c8c","668c66","b3b340","ffd940","eb9040","b34040","8c6640","494949",
      "a62079","794da6","2020a6","4d79d2","207979","4d794d","a6a620","ffd220","e77e20","a62020","794d20","242424",
      "990066","663399","000099","3366CC","006666","336633","999900","FFCC00","E46B00","990000","663300","000000"
    ],
    bright: [
      "fbdbee","ffdfff","f2dfff","ecdfff","dfdff9","e6ecff","dff2f2","dff2df","f2f9df","ffffdf","ffecdf","ffdfdf",
      "ffbfe6","ffbfff","e6bfff","d9bfff","bfbff2","ccd9ff","bfe6e6","bfe6bf","e6f2bf","ffffbf","ffd9bf","ffbfbf",
      "ff9fd9","ff9fff","d99fff","c69fff","9f9fec","b3c6ff","9fd9d9","9fd99f","d9ec9f","ffff9f","ffc69f","ff9f9f",
      "ff80cc","ff80ff","cc80ff","b380ff","8080e6","99b3ff","80cccc","80cc80","cce680","ffff80","ffb380","ff8080",
      "ff60bf","ff60ff","bf60ff","9f60ff","6060df","809fff","60bfbf","60bf60","bfdf60","ffff60","ff9f60","ff6060",
      "ff40b3","ff40ff","b340ff","8c40ff","4040d9","668cff","40b3b3","40b340","b3d940","ffff40","ff8c40","ff4040",
      "ff20a6","ff20ff","a620ff","7920ff","2020d2","4d79ff","20a6a6","20a620","a6d220","ffff20","ff7920","ff2020",
      "ff0099","ff00ff","9900ff","6600ff","0000cc","3366ff","009999","009900","99cc00","ffff00","ff6600","ff0000"
    ]
  };
  var DEFAULT_CATEGORY = 'neutral';
  var opened = [];

  function buildPaletteTable(categoryName, options) {
    var palette = PALETTE_TABLES[categoryName];
    var paletteElement = $('<ul class="decentcolorpicker-palette-table"></table>').addClass("decentcolorpicker-palette-table-" + categoryName);
    var li = null;
    for (var i = 0; i < palette.length; i++) {
      if (i % 12 == 0) {
        if (li)
          li.addClass('decentcolorpicker-palette-tile-last');
      }
      li = $('<li class="decentcolorpicker-palette-tile"></li>');
      if (i % 12 == 0)
        li.addClass('decentcolorpicker-palette-tile-first');
      li.addClass('decentcolorpicker-palette-color-' + palette[i]);
      li.css('background-color', '#' + palette[i]);
      paletteElement.append(li);
    }
    if (li)
      li.addClass('decentcolorpicker-palette-tile-last');
    return paletteElement;
  }

  function buildHTML(options) {
    var container = $('<div class="decentcolorpicker-wrapper"></div>');
    var header = $('<div class="decentcolorpicker-header"></div>').appendTo(container);
    var colorValue = !options.noColorValue ? $('<input type="text" value="" class="decentcolorpicker-preview" />').appendTo(header): null;
    var categorySwitcher = $('<ul class="decentcolorpicker-category-switcher"></ul>').appendTo(header);
    var paletteContainer = $('<div class="decentcolorpicker-palette-container"></div>').appendTo(container);
    var palettes = {};
    for (var categoryName in PALETTE_TABLES) {
      var li = $('<li></li>')
        .addClass('decentcolorpicker-category-switcher-' + categoryName)
        .appendTo(categorySwitcher);
      $('<a href="#"></a>').text(categoryName).appendTo(li);
      paletteContainer.addClass('decentcolorpicker-palette-' + categoryName);
      var paletteElement = buildPaletteTable(categoryName, options);
      paletteElement.css('display', 'none');
      paletteContainer.append(paletteElement);
      palettes[categoryName] = paletteElement;
    }
    return {
      container: container,
      header: header,
      colorValue: colorValue,
      categorySwitcher: categorySwitcher,
      paletteContainer: paletteContainer,
      palettes: palettes
    };
  }

  function defaultColorParser(str) {
    var retval = [255, 255, 255];
    var format = 'hash';
    var g = /^\s*(?:#(?:([0-9A-Fa-f])([0-9A-Fa-f])([0-9A-Fa-f])|([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})([0-9A-Fa-f]{2}))|rgb\(([^)]*)\))\s*$/.exec(str);
    if (g) {
      if (g[1]) {
        for (var i = 1; i <= 3; i++) {
          var v = parseInt(g[i], 16);
          if (isNaN(v))
            return null;
          retval[i - 1] = v | (v << 4);
        }
        format = 'hash';
      } else if (g[4]) {
        for (var i = 4; i <= 6 && g[i]; i++) {
          var v = parseInt(g[i], 16);
          if (isNaN(v))
            return null;
          retval[i - 4] = v;
        }
        format = 'hash';
      } else if (g[7]) {
        var s = g[7].split(/\s*,\s*/);
        if (s.length == 3) {
          for (var i = 0; i < 3; i++) {
            var v = parseInt(s[i]);
            if (isNaN(v))
              return null;
            retval[i] = v;
          }
        }
        format = 'rgb';
      }
    } else {
      return null;
    }
    return { format: format, r: retval[0], g: retval[1], b: retval[2] };
  }

  function toHashColor(color) {
    return '#'
           + (color.r < 16 ? "0": "") + color.r.toString(16)
           + (color.g < 16 ? "0": "") + color.g.toString(16)
           + (color.b < 16 ? "0": "") + color.b.toString(16);
  }

  function defaultColorSerializer(color) {
    switch (color.format) {
      case 'hash':
        return color.hash;
      case 'rgb':
        return 'rgb(' + [color.r, color.g, color.b].join(', ') + ')';
    }
  }

  function initUI(ctx) {
    var prevCategory = null;
    ctx.choice = null;
    function selectPalette(category) {
      ctx.category = category;
      if (prevCategory) {
        ctx.elements.palettes[prevCategory].css('display', 'none');
        ctx.elements.categorySwitcher.find('.decentcolorpicker-category-switcher-' + prevCategory).removeClass('active');
      }
      ctx.elements.palettes[category].css('display', 'block');
      ctx.elements.categorySwitcher.find('.decentcolorpicker-category-switcher-' + category).addClass('active');
      prevCategory = category;
    }
    function selectColor(color, noCallback) {
      if (ctx.choice)
        ctx.elements.paletteContainer.find('.decentcolorpicker-palette-color-' + toHashColor(ctx.choice).substring(1)).removeClass('decentcolorpicker-palette-tile-active');
      ctx.choice = color;
      if (color) {
        color.hash = toHashColor(color);
        if (ctx.elements.colorValue)
          ctx.elements.colorValue.val(color.hash);
        var x = ctx.elements.paletteContainer.find('.decentcolorpicker-palette-color-' + toHashColor(color).substring(1));
        if (x) {
          x.addClass('decentcolorpicker-palette-tile-active');
          var g = /decentcolorpicker-palette-table-(\S+)/.exec(x.parents("table").attr('class'));
          if (g)
            selectPalette(g[1]);
        }
        if (!noCallback)
          ctx.select && ctx.select.call(ctx, color);
      }
    }

    ctx.elements.categorySwitcher.find('a').click(function (e) {
      var g = /decentcolorpicker-category-switcher-(\S+)/.exec($(e.target).parent().attr('class'));
      if (g) {
        selectPalette(g[1]);
        selectColor(null);
      }
      return false; 
    });
    ctx.elements.paletteContainer.click(function (e) {
      var target = $(e.target);
      var g = /decentcolorpicker-palette-color-(\S+)/.exec(target.attr('class'));
      if (g) {
        ctx.selectColor({
          format: ctx.choice ? ctx.choice.format: 'hash',
          r: parseInt(g[1].substring(0, 2), 16),
          g: parseInt(g[1].substring(2, 4), 16),
          b: parseInt(g[1].substring(4, 6), 16)
        });
      }
    });
    ctx.elements.colorValue && ctx.elements.colorValue.change(function () {
      var color = ctx.options.colorParser(ctx.elements.colorValue.val());
      if (!color)
        return false;
      selectColor({
        format: ctx.choice ? ctx.choice.format: 'hash',
        r: color.r, g: color.g, b: color.b
      });
      return true;
    });
    selectPalette(DEFAULT_CATEGORY);
    ctx.selectPalette = selectPalette;
    ctx.selectColor = selectColor;
    ctx.elements.container.data('decentcolorpicker', ctx);
    return ctx;
  }

  $.fn.decentcolorpicker = function (options) {
    var self = this;
    if (this.length < 1)
      return;
    var isInputElement = this[0].nodeName.toLowerCase() == 'input';
    options = {
      noColorValue: options && options.noColorValue || isInputElement,
      select: options && options.select || null,
      modal: options && options.modal || isInputElement,
      colorParser: options && options.colorParser || defaultColorParser,
      colorSerializer: options && options.colorSerializer || defaultColorSerializer,
      value: options && options.value || isInputElement && function () { return self.val(); }
    };
    var elements = buildHTML(options);
    typeof(options.decorate) == 'function' && options.decorate(elements);
    var active = false;
    var outer = $('<div class="decentcolorpicker-float" style="display: none"><div class="decentcolorpicker-float-overlay"></div></div>');
    outer.click(function () {
      return false;
    });
    var ctx = initUI({ options: options, elements: elements });
    ctx.elements.container.appendTo(outer);
    $('<button class="decentcolorpicker-close-button">\u00d7</button>')
      .click(close)
      .appendTo(outer);
    outer.appendTo('body');
    function open() {
      if (active)
        return;
      var pos = self.offset();
      outer.css({ left: pos.left + 'px', top: pos.top + self.outerHeight() + 8 + 'px' });
      if (ctx.options.modal) {
        for (var i = opened.length; --i >= 0;)
          opened[i].close();
      }
      outer.css({ display: 'block', opacity: 0. });
      outer.animate({ opacity: 1. }, 100);
      active = true;
      opened.push(ctx);
    }
    function close() {
      outer.animate({ opacity: 0 }, 100, null, function () {
        active = false;
        for (var i = opened.length; --i >= 0;) {
          if (opened[i] === ctx) {
            opened.splice(i, 1);
            break;
          }
        }
        outer.css('display', 'none');
      });
    }
    ctx.close = close;
    if (isInputElement) {
      ctx.select = function (result) {
        self.val(ctx.options.colorSerializer(result));
        close(); 
        typeof(ctx.options.select) == 'function' && ctx.options.select(result);
      };
      this.focus(function () {
        if (!active)
          open();
        else
          close();
      });
    } else {
      ctx.select = function (result) {
        close(); 
        typeof(ctx.options.select) == 'function' && ctx.options.select(result);
      };
      this.click(function () {
        if (!active)
          open();
        else
          close();
      });
    }
    ctx.selectColor(ctx.options.colorParser(ctx.options.value()), true);
  }
  $.decentcolorpicker = function (options) {
    options = {
      noColorValue: options && options.noColorValue || false,
      select: options && options.select || null,
      colorParser: options && options.colorParser || defaultColorParser,
      colorSerializer: options && options.colorSerializer || defaultColorSerializer,
      value: options && options.value || null
    };
    var elements = buildHTML(options);
    typeof(options.decorate) == 'function' && options.decorate(elements);
    var ctx = initUI({ options: options, select: options.select, elements: elements });
    typeof(options.value) == 'function' && ctx.selectColor(options.colorParser(options.value()));
    return ctx.elements.container;
  }
})(jQuery);
  /*
 * vim: sts=2 sw=2 ts=2 et
 */
