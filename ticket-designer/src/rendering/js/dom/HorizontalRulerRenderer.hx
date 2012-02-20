package rendering.js.dom;

import js.JQuery;
import rendering.js.Html5Dom.HTMLCanvasElement;
import rendering.js.Html5Dom.CanvasRenderingContext2D;

class HorizontalRulerRenderer extends RulerRenderer {
    static function __init__() {
        Spi.rendererFactory.addImplementation(Ruler, HorizontalRulerRenderer, 'horizontal');
    }

    public override function setup():JQuery {
        return new JQuery('<div class="renderable-horizontal_ruler" style="height:20px; line-height:20px;"><canvas height="20"></canvas></div>');
    }

    public override function refresh():Void {
        var interval = graduations[0];
        var canvas:HTMLCanvasElement = untyped n[0].firstChild;
        canvas.width = n.innerWidth();
        var ctx:CanvasRenderingContext2D = untyped canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        var offsetInUnit = UnitUtils.inchToAny(unit, offset);
        var minimumGraduation = getMinimumGraduation();
        var minimumGraduationWidth = graduations[minimumGraduation];
        var i = minimumGraduationWidth + Math.floor(offsetInUnit / minimumGraduationWidth) * minimumGraduationWidth;
        while (true) { 
            var x = view_.inchToPixel(UnitUtils.anyToInch(unit, i - offsetInUnit));
            if (Std.int(x) >= canvas.width)
                break;
            ctx.strokeRect(0, 0, canvas.width, canvas.height);
            if (Math.floor(i / minimumGraduationWidth) % 10 == 0) {
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, 20);
                ctx.fillText(Std.string(Std.int(i)), x + 2, 10);
                ctx.stroke();
            } else {
                ctx.beginPath();
                ctx.moveTo(x, 14);
                ctx.lineTo(x, 20);
                ctx.stroke();
            }
            i += minimumGraduationWidth;
        }
    }
}
