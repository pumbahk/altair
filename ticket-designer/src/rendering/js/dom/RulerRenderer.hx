package rendering.js.dom;

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
}
