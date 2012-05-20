var Util = _class("Util", {
  class_methods: {
    eventKey: function(e) {
      var shift, ctrl;
      // Mozilla
      if (e != null) {
        keycode = e.which;
        ctrl    = typeof e.modifiers == 'undefined' ? e.ctrlKey : e.modifiers & Event.CONTROL_MASK;
        shift   = typeof e.modifiers == 'undefined' ? e.shiftKey : e.modifiers & Event.SHIFT_MASK;

      }
      // ie
      else {
        keycode = event.keyCode;
        ctrl    = event.ctrlKey;
        shift   = event.shiftKey;

      }

      keychar = String.fromCharCode(keycode).toUpperCase();

      return {
        ctrl:    (!!ctrl) || keycode === 17,
        shift:   (!!shift) || keycode === 16,
        keycode: keycode,
        keychar: keychar
      };

    },

    AsyncDataWaiter: Fashion._lib._class("AsyncDataWaiter", {
      props: {
        identifiers: [],
        after: function() {},
        stor: {},
        this_object: null
      },

      methods: {
        charge: function(idt, data) {
          this.stor[idt] = data;

          for (var i=0,l=this.identifiers.length; i<l; i++) {
            var id = this.identifiers[i];
            if (!this.stor.hasOwnProperty(id)) return;
          }

          // fire!! if all data has come.
          this.after.call(this.this_object, this.stor);
        }
      }
    }),

    convertToFashionStyle: function(style, gradient) {
      var filler = function(color) {
        if (gradient) return new Fashion.LinearGradientFill([[0, new Fashion.Color("#fff")], [1, new Fashion.Color(color || "#fff")]], .125);
        return new Fashion.FloodFill(new Fashion.Color(color || "#000"));
      };

      return {
        "fill": style.fill ? filler(style.fill.color): null,
        "stroke": style.stroke ? new Fashion.Stroke((style.stroke.color || "#000") + " " + (style.stroke.width ? style.stroke.width: 1) + " " + (style.stroke.pattern || "")) : null
      };
    },

    allAttributes: function(el) {
      var rt = {}, attrs=el.attributes, attr;
      for (var i=0, l=attrs.length; i<l; i++) {
        attr = attrs[i];
        rt[attr.nodeName] = attr.nodeValue;
      }
      return rt;
    },

    makeHitTester: function(a) {
      var pa = a.position(),
      sa = a.size(),
      ax0 = pa.x,
      ax1 = pa.x + sa.x,
      ay0 = pa.y,
      ay1 = pa.y + sa.y;

      return function(b) {
        var pb = b.position(),
        sb = b.size(),
        bx0 = pb.x,
        bx1 = pb.x + sb.x,
        by0 = pb.y,
        by1 = pb.y + sb.y;

        return ((((ax0 < bx0) && (bx0 < ax1)) || (( ax0 < bx1) && (bx1 < ax1)) || ((bx0 < ax0) && (ax1 < bx1))) && // x
                (((ay0 < by0) && (by0 < ay1)) || (( ay0 < by1) && (by1 < ay1)) || ((by0 < ay0) && (ay1 < by1))));  // y
      }
    }
  }
});
