exports.DEFAULT = {
  ZOOM_RATIO: 0.8,
  STYLES: {
    label: {
      fill: new Fashion.Color('#000'),
      stroke: null
    },
    seat: {
      fill: new Fashion.Color('#fff'),
      stroke: new Fashion.Color('#000')
    },
    glayout: {
      fill: new Fashion.FloodFill(new Fashion.Color('#ccc')),
      stroke: new Fashion.Stroke(new Fashion.Color('#999'), 2)
    }
  },

  MASK_STYLE: {
    fill:   new Fashion.FloodFill(new Fashion.Color("#0064ff80")),
    stroke: new Fashion.Stroke(new Fashion.Color("#0080FF"), 2)
  },

  SEAT_STYLE: {
    text_color: "#000",
    fill:   { color: "#fff" }
  },

  OVERLAYS: {
    highlighted: {
      fill: null,
      stroke: { color: "#F63", width: 3, pattern: 'solid' }
    },
    highlighted_block: {
      fill: null,
      stroke: { color: "#F44", width: 5, pattern: 'solid' }
    }
  },

  AUGMENTED_STYLE: {
    selected: {
      text_color: "#FFF",
      fill:   { color: "#009BE1" },
      stroke: { color: "#FFF", width: 3 }
    },
    unselectable: {
      text_color: "#888",
      fill:   { color: "#eee" },
      stroke: { color: "#ccc" }
    }
  }
};
