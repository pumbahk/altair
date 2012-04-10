package;

import util.JSONLoader;
import util.JSONLoaderCallback;
import model.HallModel;
import model.HallView;
import model.HallShape;
import render.Renderer;
import render.RendererCallback;
import render.impl.RendererImplFashion;
import model.Element;
import model.ElementType;

class HallViewer implements JSONLoaderCallback, implements RendererCallback {

    private static var layer0:Int = 0;
    private static var layer1:Int = 1;

    private var hall:HallModel;
    private var hall_view:HallView;
    private var hall_shape:HallShape;
    private var renderer:Renderer;
    private var layer0Data:Dynamic;
    private var layer1Data:Dynamic;


    public function new():Void
    {
        var r = new JSONLoader(this);

        this.layer0Data = null;
        this.layer1Data = null;

        r.load(CONF.SERVER+CONF.SRC_LO, HallViewer.layer0);
        r.load(CONF.SERVER+CONF.SRC_L1, HallViewer.layer1);
    }

    public function onError(msg:String, flag:Int):Void
    {
        Console.error(msg);
    }

    public function onSuccess(obj:Dynamic, flag:Int):Void
    {
        switch (flag) {
        case HallViewer.layer0:
            this.layer0Data = obj;

        case HallViewer.layer1:
            this.layer1Data = obj;
        }

        if (this.layer0Data != null && this.layer1Data != null) {
            this.composeModel();
        }
    }

    private function composeModel():Void
    {
        this.hall       = new HallModel(this.layer1Data);
        this.hall_shape = new HallShape(this.layer0Data);
        this.hall_view  = new HallView(this.hall_shape, this.hall);
        this.renderer   = new Renderer(this, this.hall_view, RendererImplFashion);
    }

    public function onClick(elm:Element):Void
    {
        Console.log("onClick:", elm);
    }

    public function onSelect(elms:Hash<Element>):Void
    {
        Console.log("onSelect", elms);
    }

    private function writeParents(elm:Element, main:Bool=false):Void
    {
        switch(elm.type()) {
        case ElementType.seat:
            js.Lib.document.getElementById("table_seat").innerHTML = elm.id();
            if (main) js.Lib.document.getElementById("table_seat_title").style.background = "#F77";

        case ElementType.row:
            js.Lib.document.getElementById("table_row").innerHTML = elm.name();
            if (main) js.Lib.document.getElementById("table_row_title").style.background = "#F77";

        case ElementType.col:
            js.Lib.document.getElementById("table_col").innerHTML = elm.name();
            if (main) js.Lib.document.getElementById("table_col_title").style.background = "#F77";

        case ElementType.block:
            js.Lib.document.getElementById("table_block").innerHTML = elm.name();
            if (main) js.Lib.document.getElementById("table_block_title").style.background = "#F77";

        case ElementType.floor:
            js.Lib.document.getElementById("table_floor").innerHTML = elm.name();
            if (main) js.Lib.document.getElementById("table_floor_title").style.background = "#F77";

        case ElementType.gate:
            js.Lib.document.getElementById("table_gate").innerHTML = elm.name();
            if (main) js.Lib.document.getElementById("table_gate_title").style.background = "#F77";

        default:
        }
    }

    private function writeChildren(elm:Element=null):Void
    {
        if (elm == null) {
            js.Lib.document.getElementById("table2").innerHTML = "<b>子要素</b><table style=\"width=250px\"><tr><th>列</th><th>番</th><th>ブロック</th><th>階</th><th>ゲート</th></tr></table>";
            return;
        }

        var line:String = "<b>子要素</b><table style=\"width=250px\"><tr><th>列</th><th>番</th><th>ブロック</th><th>階</th><th>ゲート</th></tr>";
        for (c in elm.children()) {
            var row:String = "";
            var col:String = "";
            var block:String = "";
            var floor:String = "";
            var gate:String = "";

            for (e in c.parents()) {
                switch(e.type()) {
                case ElementType.row: row = e.name();
                case ElementType.col: col = e.name();
                case ElementType.block: block = e.name();
                case ElementType.floor: floor = e.name();
                case ElementType.gate: gate = e.name();
                default:
                }
            }
            line += "<tr><td>"+row+"</td><td>"+col+"</td><td>"+block+"</td><td>"+floor+"</td><td>"+gate+"</td></tr>";
        }
        line += "</table>";

        js.Lib.document.getElementById("table2").innerHTML = line;
    }

    public function onMouseOver(elm:Element):Void
    {
        this.writeParents(elm, true);

        for (e in elm.parents()) {
            this.writeParents(e);
        }
        this.writeChildren(elm);

        elm.style({zIndex: elm.zIndex(), fill: {color: [255,127,127,255]}, stroke: {width: 0.5, color: [0, 0, 0, 255]}});
        this.renderer.storeToReflesh(elm, false);

        var elms_color:Array<Array<Dynamic>> = [
                 [elm.parentRow(), [204,255,204,255]],
                 [elm.parentCol(), [204,204,255,255]],
                 [elm.parentBlock(), [255,204,204,255]],
                 [elm.parentFloor(), [255,255,204,255]],
                 [elm.parentGate(), [204,204,204,255]]];

        for (ec in elms_color) {
            var p:Element = cast ec[0];

            if (p != null) {
                p.style({zIndex: p.zIndex(), fill: {color: ec[1]}, stroke: {width: 0.5, color: [0, 0, 0, 255]}});
                this.renderer.storeToReflesh(p, false);
                if (p.type() == ElementType.row || p.type() == ElementType.col) {
                    for (c in p.children()) {
                        if (c != elm) {
                            c.style({zIndex: c.zIndex(), fill: {color: ec[1]}, stroke: {width: 0.5, color: [0, 0, 0, 255]}});
                            this.renderer.storeToReflesh(c, false);
                        }
                    }
                }
            }
        }

        this.renderer.nortifyDataSetChanged();

    }

    public function onMouseOut(elm:Element):Void
    {
        js.Lib.document.getElementById("table_seat").innerHTML = "---";
        js.Lib.document.getElementById("table_row").innerHTML = "---";
        js.Lib.document.getElementById("table_col").innerHTML = "---";
        js.Lib.document.getElementById("table_block").innerHTML = "---";
        js.Lib.document.getElementById("table_floor").innerHTML = "---";
        js.Lib.document.getElementById("table_gate").innerHTML = "---";

        js.Lib.document.getElementById("table_seat_title").style.background = "#FFF";
        js.Lib.document.getElementById("table_row_title").style.background = "#FFF";
        js.Lib.document.getElementById("table_col_title").style.background = "#FFF";
        js.Lib.document.getElementById("table_block_title").style.background = "#FFF";
        js.Lib.document.getElementById("table_floor_title").style.background = "#FFF";
        js.Lib.document.getElementById("table_gate_title").style.background = "#FFF";

        this.writeChildren();

        for(e in this.hall_view) {
            e.style({zIndex: e.zIndex(), fill: {color: [255,255,255,255]}, stroke: {width: 0.5, color: [0, 0, 0, 255]}});
        }

        this.renderer.refleshAll();

    }

    private function reflesh(elms:Hash<Element>):Void
    {
        this.renderer.reflesh();
    }
}