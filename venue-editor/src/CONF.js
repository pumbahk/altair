exports.DEFAULT = {
  ZOOM_RATIO: 0.8,
  SHAPE_STYLE: {
    fill: new Fashion.FloodFill(new Fashion.Color('#fff')),
    stroke: new Fashion.Stroke(new Fashion.Color("#000"), 1)
  },

  TEXT_STYLE: {
    fill: new Fashion.FloodFill(new Fashion.Color('#000')),
    stroke: null
  },

  VENUE_STYLE: {
    fill: new Fashion.FloodFill(new Fashion.Color('#FFCB3F')),
    stroke: new Fashion.Stroke(new Fashion.Color('#5ABECD'), 1)
  },

  STYLES: {
    label: {
      fill: new Fashion.Color('#000'),
      stroke: null
    },
    seat: {
      fill: new Fashion.Color('#fff'),
      stroke: new Fashion.Color('#000')
    }
  },

  MASK_STYLE: {
    fill:   new Fashion.FloodFill(new Fashion.Color("#0064ff80")),
    stroke: new Fashion.Stroke(new Fashion.Color("#0080FF"), 2)
  },

  SEAT_STYLE: {
    text_color: "#000",
    fill:   { color: "#fff" },
    stroke: { color: "#000", width: 1 }
  },

  AUGMENTED_STYLE: {
    selected: {
      text_color: "#FFF",
      fill:   { color: "#009BE1" }
    },
    highlighted: {
      fill: null,
      stroke: { color: "#F63", width: 2, pattern: 'solid' }
    },
    unselectable: {
      text_color: "#888",
      fill:   { color: "#eee" },
      stroke: { color: "#ccc", width: 1 }
    }
  }
};
