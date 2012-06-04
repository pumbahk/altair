package render;

import model.Element;

interface RendererCallback {
    public function onClick     (elm:Element):Void;
    public function onSelect    (elms:Hash<Element>):Void;
    public function onMouseOver (elms:Element):Void;
    public function onMouseOut  (elms:Element):Void;
}