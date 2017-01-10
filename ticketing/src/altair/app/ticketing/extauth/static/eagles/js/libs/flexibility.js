/*! flexibility v0.2.2 | MIT Licensed | github.com/10up/flexibility */
flexibility={},/MSIE [8-9]\./i.test(navigator.userAgent)&&document.attachEvent("onreadystatechange",function(){"complete"===document.readyState&&flexibility.process(document.body)}),flexibility.each=function(t,e){for(var i=t.firstChild;i;)1===i.nodeType&&e(i),i=i.nextSibling},flexibility.measure=function(t){var e=t.onlayoutcomplete=t.onlayoutcomplete||{},i=t.runtimeStyle,n=i.cssText;i.cssText="border:0;display:inline-block;height:0;overflow:hidden;padding:0;width:0";var o=t.scrollWidth,l=t.scrollHeight;i.width="1em";var r=t.offsetWidth;i.cssText=n;var a={medium:4,none:0,thick:6,thin:2},f={borderTopWidth:0,borderRightWidth:0,borderBottomWidth:0,borderLeftWidth:0,marginTop:0,marginRight:0,marginBottom:0,marginLeft:0,paddingTop:0,paddingRight:0,paddingBottom:0,paddingLeft:0,minWidth:0,maxWidth:0,minHeight:0,maxHeight:0},c=document.createElement("x"),d=t.parentNode,m=t.currentStyle,s=c.runtimeStyle;s.cssText="border:0;clip:rect(0 0 0 0);display:block;font-size:"+r+"px;line-height:0;margin:0;padding:0;position:absolute",d.insertBefore(c,t);for(var h in f){var u=m[h];s.width=u in a?a[u]:u,e[h]=c.offsetWidth}return d.removeChild(c),e.fontSize=r,"none"===m.borderTopStyle&&(e.borderTopWidth=0),"none"===m.borderRightStyle&&(e.borderRightWidth=0),"none"===m.borderBottomStyle&&(e.borderBottomWidth=0),"none"===m.borderLeftStyle&&(e.borderLeftWidth=0),e.scrollWidth=o,e.scrollHeight=l,e.width=t.offsetWidth,e.height=t.offsetHeight,e.contentHeight=e.height-e.borderTopWidth-e.borderBottomWidth-e.paddingTop-e.paddingBottom,e.contentWidth=e.width-e.borderLeftWidth-e.borderRightWidth-e.paddingLeft-e.paddingRight,e},flexibility.process=function(t){if(1===t.nodeType){var e=t.runtimeStyle;flexibility.properties(t),flexibility.properties(t.parentElement);var i=t.onlayoutcomplete,n=t.parentElement.onlayoutcomplete,o=/flex$/.test(i.display)&&i.display,l=/flex$/.test(n.display)&&n.display;o&&!l&&(e.display="inline-block",e.verticalAlign="top","flex"===o&&(e.display="block"),e.width=t.offsetWidth+"px");for(var r,a=-1,f=t.childNodes;r=f[++a];)if(1===r.nodeType){if(o){var c=r;t.replaceChild(r=flexibility.process.clone(r),c);var d=r.runtimeStyle;d.display="inline-block",d.verticalAlign="top",d.width=r.offsetWidth+"px"}flexibility.process(r)}o&&(flexibility.measure(t),flexibility.transform(t))}},flexibility.process.clone=function(t){for(var e,i=document.createElement(t.nodeName),n=t.attributes,o=-1;e=n[++o];){var l=document.createAttribute(e.name);l.value=e.value,i.setAttributeNode(l)}for(;t.lastChild;)i.appendChild(t.firstChild);return i},flexibility.properties=function(t){var e=t.onlayoutcomplete=t.onlayoutcomplete||{},i=t.currentStyle;e.boxSizing=i.boxSizing||"content-box",e.display=i["-js-display"]||i.display;var n={alignContent:{initial:"stretch",valid:/^(flex-start|flex-end|center|space-between|space-around|stretch)/},alignItems:{initial:"stretch",valid:/^(flex-start|flex-end|center|baseline|stretch)$/},alignSelf:{initial:"auto",valid:/^(auto|flex-start|flex-end|center|baseline|stretch)$/},flexBasis:{initial:"auto",valid:/^((?:[-+]?0|[-+]?[0-9]*\.?[0-9]+(?:%|ch|cm|em|ex|in|mm|pc|pt|px|rem|vh|vmax|vmin|vw))|auto|fill|max-content|min-content|fit-content|content)$/},flexDirection:{initial:"row",valid:/^(row|row-reverse|column|column-reverse)$/},flexGrow:{initial:"0",valid:/^\+?(0|[1-9][0-9]*)$/},flexShrink:{initial:"0",valid:/^\+?(0|[1-9][0-9]*)$/},flexWrap:{initial:"nowrap",valid:/^(nowrap|wrap|wrap-reverse)$/},justifyContent:{initial:"flex-start",valid:/^(flex-start|flex-end|center|space-between|space-around)$/},order:{initial:"0",valid:/^([-+]?[0-9]+)$/}};for(var o in n){var l=(i[o.replace(/[A-Z]/g,"-$&").toLowerCase()]||"").toLowerCase();e[o]=n[o].valid.test(l)?l:n[o].initial}},flexibility.transform=function(t){var e=t.onlayoutcomplete,i=e.flexDirection,n=e.alignItems,o=e.justifyContent;flexibility.transform.align[i][n]&&flexibility.transform.align[i][n](t),flexibility.transform.justify[i][o]&&flexibility.transform.justify[i][o](t)},flexibility.transform.align={row:{"flex-start":function(t){var e=t.onlayoutcomplete;flexibility.each(t,function(t){flexibility.measure(t);var i=t.onlayoutcomplete;t.runtimeStyle.marginBottom=e.contentHeight-i.height-i.marginBottom})},center:function(t){var e=t.onlayoutcomplete;flexibility.each(t,function(t){flexibility.measure(t);var i=t.onlayoutcomplete;t.runtimeStyle.marginTop=(e.contentHeight-i.height)/2+"px"})},"flex-end":function(t){var e=t.onlayoutcomplete;flexibility.each(t,function(t){flexibility.measure(t);var i=t.onlayoutcomplete;t.runtimeStyle.marginTop=e.contentHeight-i.height-i.marginTop})},stretch:function(t){var e=t.onlayoutcomplete;flexibility.each(t,function(t){flexibility.measure(t);var i=t.onlayoutcomplete;t.runtimeStyle.height=e.contentHeight-i.marginTop-i.marginBottom+"px"})}},column:{"flex-start":function(t){var e=t.onlayoutcomplete;flexibility.each(t,function(t){flexibility.measure(t);var i=t.onlayoutcomplete;t.runtimeStyle.marginRight=e.contentWidth-i.width-i.marginRight})},"flex-end":function(t){var e=t.onlayoutcomplete;flexibility.each(t,function(t){flexibility.measure(t);var i=t.onlayoutcomplete;t.runtimeStyle.marginLeft=e.contentWidth-i.width-i.marginLeft})},center:function(t){var e=t.onlayoutcomplete;flexibility.each(t,function(t){flexibility.measure(t);var i=t.onlayoutcomplete,n=(e.contentWidth-i.width)/2+"px";t.runtimeStyle.marginLeft=t.runtimeStyle.marginRight=n})},stretch:function(t){var e=t.onlayoutcomplete;flexibility.each(t,function(t){flexibility.measure(t);var i=t.onlayoutcomplete;t.runtimeStyle.width=e.contentWidth-i.marginLeft-i.marginRight+"px"})}}},flexibility.transform.contentMeasurements=function(t){for(var e,i,n,o,l,r,a,f=t.childNodes,c=-1,d=[];e=f[++c];)1===e.nodeType&&(d.push(e),o||(o=e.runtimeStyle,i=e.offsetLeft,n=e.offsetTop),a=e.runtimeStyle,l=e.offsetLeft+e.offsetWidth,r=e.offsetTop+e.offsetHeight);return{children:d,startStyle:o,endStyle:a,width:l-i,height:r-n}},flexibility.transform.justify={row:{"flex-end":function(t){var e=t.onlayoutcomplete,i=flexibility.transform.contentMeasurements(t),n=i.children[i.children.length-1];flexibility.measure(n);var o=n.onlayoutcomplete,l=e.contentWidth-i.width-o.marginRight;i.startStyle.marginLeft=l+"px"},center:function(t){var e=t.onlayoutcomplete,i=flexibility.transform.contentMeasurements(t),n=(e.contentWidth-i.width)/2;i.startStyle.marginLeft=n,i.endStyle.marginRight=n}},column:{"space-around":function(t){for(var e,i=t.onlayoutcomplete,n=flexibility.transform.contentMeasurements(t),o=i.contentHeight-n.height,l=n.children.length,r=o/(2*l),a=-1;e=n.children[++a];)e.runtimeStyle.marginTop=r+"px",e.runtimeStyle.marginBottom=r+"px"}}};
//# sourceMappingURL=flexibility.js.map