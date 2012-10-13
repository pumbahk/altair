var KeycodeMapping = (function(u){
    u.mappingTable = {0x69: [0x39, 0x39], 0x55: [0x75, 0x55], 0x6B: [0x2b, 0x2b], 0x54: [0x74, 0x54], 0xC0: [0x2d, 0x3d], 0x41: [0x61, 0x41], 0x42: [0x62, 0x42], 0x43: [0x63, 0x43], 0x44: [0x64, 0x44], 0x45: [0x65, 0x45], 0x46: [0x66, 0x46], 0x47: [0x67, 0x47], 0x48: [0x68, 0x48], 0x49: [0x69, 0x49], 0x64: [0x34, 0x34], 0x65: [0x35, 0x35], 0x53: [0x73, 0x53], 0x1B: [0x1b, 0x1b], 0x60: [0x30, 0x30], 0x61: [0x31, 0x31], 0x5A: [0x7a, 0x5A], 0x08: [0x08, 0x08], 0x09: [0x09, 0x09], 0xBB: [0x2b, 0x2b], 0x62: [0x32, 0x32], 0x20: [0x20, 0x20], 0xBA: [0x3b, 0x2b], 0xBF: [0x2f, 0x3f], 0xBD: [0x2d, 0x2d], 0x63: [0x33, 0x33], 0xDB: [0x60, 0x40], 0xDC: [0x5d, 0x7d], 0xDD: [0x5b, 0x7b], 0xDE: [0x3a, 0x2a], 0x67: [0x37, 0x37], 0x68: [0x38, 0x38], 0x35: [0x35, 0x25], 0x34: [0x34, 0x24], 0x37: [0x37, 0x27], 0x36: [0x36, 0x26], 0x31: [0x31, 0x21], 0x30: [0x30, ], 0x33: [0x33, 0x23], 0x32: [0x32, 0x22], 0x0D: [0x0d, 0x0d], 0x59: [0x79, 0x59], 0x58: [0x78, 0x58], 0x39: [0x39, 0x29], 0x38: [0x38, 0x28], 0x0C: [0x0c, 0x0c], 0x4A: [0x6a, 0x4A], 0x4B: [0x6b, 0x4B], 0x4C: [0x6c, 0x4C], 0x4D: [0x6d, 0x4D], 0x4E: [0x6e, 0x4E], 0x4F: [0x6f, 0x4F], 0x52: [0x72, 0x52], 0x6F: [0x2f, 0x2f], 0x66: [0x36, 0x36], 0x6D: [0x2d, 0x2d], 0x13: [0x13, 0x13], 0x51: [0x71, 0x51], 0x6A: [0x2a, 0x2a], 0xBE: [0x2e, 0x2e], 0x50: [0x70, 0x50], 0xBC: [0x2c, 0x2c], 0x57: [0x77, 0x57], 0x56: [0x76, 0x56]};
    
  u.translate = function(shiftKey, keyCode){
      if(u.mappingTable[keyCode]){
          return u.mappingTable[keyCode][shiftKey ? 1: 0];
      } else {
          return keyCode;
      }
  }
  return u;
})({});
