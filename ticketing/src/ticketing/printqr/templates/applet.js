function writeAppletTag(options) {
  var buf = [];
  var version = options.version.split('.');
  var width = (0|options.width) || 100;
  var height = (0|options.height) || 100;
  var id = options.id;
  var code = options.code;
  var codebase = options.codebase;
  var archive = options.archive;
  var scriptable = options.scriptable || false;
  var params = options.params;

  function escapeHTMLSpecials(text) {
    return ("" + text)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function buildHTMLForIE() {
    buf.push(
      '<object',
      ' classid="clsid:8AD9C840-044E-11D1-B3E9-00805F499D93"',
      ' codebase="http://javadl-esd.sun.com/update/', version.slice(0, 3).join('.'), '/jinstall-6u35-windows-i586.cab#Version=', version.join(','), '"',
      ' width="', width, '"',
      ' height="', height, '"');
    if (id)
      buf.push(' id="', escapeHTMLSpecials(id), '"');
    buf.push('>');
    buf.push('<param name="type" value="application/x-java-applet;version=', version[0], '.', version[1], '" />');
    buf.push('<param name="code" value="', escapeHTMLSpecials(code), '" />');
    if (codebase)
      buf.push('<param name="codebase" value="', escapeHTMLSpecials(codebase), '" />');
    if (archive)
      buf.push('<param name="archive" value="', escapeHTMLSpecials(archive), '" />');
    buf.push('<param name="scriptable" value="', (scriptable ? 'true': 'false'), '" />');
    for (var k in params)
      buf.push('<param name="', escapeHTMLSpecials(k), '" value="', escapeHTMLSpecials(params[k]), '" />');
    buf.push('</object>');
  }

  function buildHTMLForOthers() {
    buf.push('<embed',
      ' type="application/x-java-applet;version=', version[0], '.', version[1], '"',
      ' pluginspage="http://java.sun.com/products/plugin/index.html#download"',
      ' code="', escapeHTMLSpecials(code), '"',
      ' width="', width, '"',
      ' height="', height, '"',
      ' scriptable="', (scriptable ? 'true': 'false'), '"');
    if (codebase)
      buf.push(' codebase="', escapeHTMLSpecials(codebase), '"');
    if (archive)
      buf.push(' archive="', escapeHTMLSpecials(archive), '"');
    if (id) {
      buf.push(' name="', escapeHTMLSpecials(id), '"');
      buf.push(' id="', escapeHTMLSpecials(id), '"');
    }
    for (var k in params)
      buf.push(' ', escapeHTMLSpecials(k), '="', escapeHTMLSpecials(params[k]), '"');
    buf.push('></embed>');
  }

  function buildHTMLApplet() {
    buf.push('<applet',
      ' code="', escapeHTMLSpecials(code), '"',
      ' width="', width, '"',
      ' height="', height, '"',
      ' scriptable="', (scriptable ? 'true': 'false'), '"');
    if (codebase)
      buf.push(' codebase="', escapeHTMLSpecials(codebase), '"');
    if (archive)
      buf.push(' archive="', escapeHTMLSpecials(archive), '"');
    if (id) {
      buf.push(' name="', escapeHTMLSpecials(id), '"');
      buf.push(' id="', escapeHTMLSpecials(id), '"');
    }
    buf.push('>');
    for (var k in params)
      buf.push('<param name="', escapeHTMLSpecials(k), '" value="', escapeHTMLSpecials(params[k]), '" />');
    buf.push('</applet>');
  }

  if (navigator.userAgent.indexOf('MSIE') >= 0)
    buildHTMLForIE();
  else
    buildHTMLForOthers();
  $("#applet").html(buf.join(""));
  //document.write(buf.join(''));
}
