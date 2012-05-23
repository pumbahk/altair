package render;

import render.impl.RendererImpl;
import model.HallView;
import model.Element;
import model.ShapeCircle;
import model.ShapePath;
import model.ShapeRect;
import model.Shape;

class Renderer {

    private var _callback:RendererCallback;
    private var _impl:RendererImpl;
    private var _hall_view:HallView;
    private var _store_to_reflesh:Hash<Element>;

    public function new(cb:RendererCallback, hall_view:HallView, impl:Class<RendererImpl>):Void
    {
        this._hall_view = hall_view;
        this._callback = cb;
        this._impl = Type.createInstance(impl, [this]);
        this._store_to_reflesh = new Hash<Element>();

        this.refleshAll();
    }

    public function nortifyDataSetChanged():Void
    {
        this.reflesh();
    }

    public function draw(e:Element):Void
    {
        if (e.hasShape()) {
            this._impl.draw(e.id(), e.getShape(), e.style());
        }
    }

    public function storeToReflesh(elm:Element, overwrite:Bool=true):Void
    {
        if (overwrite || !this._store_to_reflesh.exists(elm.id()))
            this._store_to_reflesh.set(elm.id(), elm);
    }

    public function reflesh():Void
    {
        for(e in this._store_to_reflesh) {
            this.draw(e);
        }
        this._store_to_reflesh = new Hash<Element>();
    }

    public function refleshAll():Void
    {
        var i:Int = 0;
        for(e in this._hall_view) {
            e.zIndex(i);
            e.style({zIndex: e.zIndex(), fill: {color: [255,255,255,255]}, stroke: {width: 0.5, color: [0, 0, 0, 255]}});
            this.draw(e);
            i++;
        }
    }

    public function onClick(id:String):Void
    {
        var e:Element = this._hall_view.getById(id);
        this._callback.onClick(e);
    }

    public function onSelect(ids:Array<String>):Void
    {
        var e:Hash<Element> = this._hall_view.getByIds(ids);
        this._callback.onSelect(e);
    }

    public function onMouseOver(id:String):Void
    {
        var e:Element = this._hall_view.getById(id);
        this._callback.onMouseOver(e);
    }

    public function onMouseOut(id:String):Void
    {
        var e:Element = this._hall_view.getById(id);
        this._callback.onMouseOut(e);
    }
}