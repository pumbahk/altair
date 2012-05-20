var SeatAdjacencies = _class("SeatAdjacencies", {

  props: {
    src      :null,
    tbl      :{},
    selector :null,
    _length  :1,
    _enable  :true
  },

  methods: {
    init: function(src) {
      this.src = src;
      this.initUI();
      this.initTable();
    },

    initUI: function() {
      var self = this;
      var holder = $('#adjacencies_selector');

      for (var i in this.src) {
        $('<option value="'+i+'">'+i+'</option>').appendTo(holder);
      }
      if (i) {
        holder.css("float", "right");
        holder.css("width", "50");
        holder.bind('change', function() {
          var val = $('#adjacencies_selector option:selected').val();
          self.length(parseInt(val));
        });
        this.selector = holder;
      } else {
        holder.css("display", "none");
      }
    },

    initTable: function() {
      for (var len in this.src) {
        this.tbl[len] = this.convertToTable(len, this.src[len]);
      }
    },

    getCandidates: function(id) {
      if (!this._enable) return [];
      if (this._length == 1) return [[id]];
      return this.tbl[this._length][id] || [];
    },

    convertToTable: function(len, src) {
      var rt = {};

      for (var i=0,l=src.length; i<l; i++) {
        // sort by string.
        src[i] = src[i].sort();
        for (var j=0;j<len;j++) {
          var id = src[i][j];
          if (!rt[id]) rt[id] = [];
          rt[id].push(src[i]);
        }
      }

      // sort by string-array.
      for (var i in rt) rt[i].sort().reverse();

      return rt;
    },

    length: function(len) {
      if (len) this._length = len;
      return this._length;
    },

    lengths: function() {
      var rt = [];
      for (var len in this.tbl) rt.push(len);
      return rt;
    },

    disable: function() {
      if (this.selector) this.selector.attr('disabled', 'disabled');
      this._enable = false;
    },

    enable: function() {
      if (this.selector) this.selector.removeAttr('disabled');
      this._enable = true;
    }
  }
});

/*
// test code
// ad == ad2

var ad = new SeatAdjacencies({"3": [["A1", "A2", "A3"], ["A2", "A3", "A4"], ["A3", "A4", "A5"], ["A4", "A5", "A6"]]});
var ad2 = new SeatAdjacencies({"3": [["A1", "A3", "A2"], ["A2", "A3", "A4"], ["A4", "A3", "A5"], ["A6", "A5", "A4"]]});
console.log(ad);
console.log(ad2);
*/