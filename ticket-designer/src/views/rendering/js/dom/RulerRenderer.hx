package views.rendering.js.dom;

import js.JQuery.JqEvent;

class RulerRenderer extends JSDOMRenderer {
    var offset:Int;
    var unit:UnitKind;
    var minimumGraduationWidthInPixel:Float;
    var graduations:Array<Float>;

    public override function realize(ruler:Dynamic):Void {
        ruler = cast(ruler, Ruler);
        offset = ruler.offset;
        unit = ruler.unit;
        minimumGraduationWidthInPixel = ruler.minimumGraduationWidthInPixel;
        graduations = ruler.graduations;
        view_.scheduleRefresh(this);
    }

    function getMinimumGraduation():Int {
        for (i in 0 ... graduations.length) {
            if (view_.inchToPixel(UnitUtils.anyToInch(unit, graduations[i])) >= minimumGraduationWidthInPixel)
                return i;
        }
        return graduations.length - 1;
    }

    override function createMouseEvent(e:JqEvent):MouseEvent {
        return {
            source: this,
            cause: e,
            position: view_.pixelToInchP(
                { x: e.pageX - view_.stage_.screenOffset.x,
                  y: e.pageY - view_.stage_.screenOffset.y }),
            screenPosition: { x: 0. + e.pageX, y: 0. + e.pageY },
            left: (e.which & 1) != 0,
            middle: (e.which & 2) != 0,
            right: (e.which & 3) != 0 };
    }
}
