package rendering.js.dom;

import js.JQuery;
import rendering.js.Html5Dom.HTMLCanvasElement;
import rendering.js.Html5Dom.CanvasRenderingContext2D;

class VerticalRulerRenderer extends RulerRenderer {
    static function __init__() {
        Spi.rendererRegistry.addImplementation(Ruler, VerticalRulerRenderer, 'vertical');
    }

    public override function setup():JQuery {
        super.setup();
        return new JQuery('<div class="renderable-vertical_ruler" style="width:20px;"><canvas width="20"></canvas></div>');
    }

    public override function refresh():Void {
        var interval = graduations[0];
        var canvas:HTMLCanvasElement = untyped n[0].firstChild;
        canvas.height = n.innerHeight();
        var ctx:CanvasRenderingContext2D = untyped canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        var offsetInUnit = UnitUtils.inchToAny(unit, offset);
        var minimumGraduation = getMinimumGraduation();
        var minimumGraduationWidth = graduations[minimumGraduation];
        var i = minimumGraduationWidth + Math.floor(offsetInUnit / minimumGraduationWidth) * minimumGraduationWidth;
        while (true) { 
            var y = view_.inchToPixel(UnitUtils.anyToInch(unit, i - offsetInUnit));
            if (Std.int(y) >= canvas.height)
                break;
            ctx.strokeRect(0, 0, canvas.width, canvas.height);
            if (Math.floor(i / minimumGraduationWidth) % 10 == 0) {
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(20, y);
                var text = Std.string(Std.int(i));
                ctx.stroke();
                ctx.fillText(text, 20 - ctx.measureText(text).width, y + 10);
            } else {
                ctx.beginPath();
                ctx.moveTo(12, y);
                ctx.lineTo(20, y);
                ctx.stroke();
            }
            i += minimumGraduationWidth;
        }
    }
}
