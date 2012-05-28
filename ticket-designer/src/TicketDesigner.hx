import views.View;
import views.RendererFactory;
import views.ComponentFactory;
import views.Ruler;
import views.HorizontalGuide;
import views.VerticalGuide;
import views.MouseEvent;
import views.MouseCursorKind;
import views.ComponentRenderer;
import views.BasicRendererFactoryImpl;
import views.Workspace;
import views.BoundingBox;
import views.Tooltip;
import models.Document;
import models.Text;

class TicketDesigner implements DiagramEditorApplication {
    public var view(default, null):View;
    public var shell(default, null):Shell;
    public var rendererFactory(default, null):RendererFactory;
    public var horizontalRuler(default, null):Ruler;
    public var verticalRuler(default, null):Ruler;
    public var componentFactory(default, null):ComponentFactory;
    public var workspace(default, null):Workspace;
    public var configuration(default, null):Configuration;
    private var horizontalGuide:HorizontalGuide;
    private var verticalGuide:VerticalGuide;
    private var boundingBox:BoundingBox;
    private var currentDocument:Document;

    private function horizontalRuler_dragstart(e:MouseEvent) {
        horizontalGuide = componentFactory.create(HorizontalGuide);
        horizontalGuide.position = e.position;
        view.stage.cursor = MouseCursorKind.CROSSHAIR;
        horizontalGuide.refresh();
    }

    private function horizontalRuler_drag(e:MouseEvent) {
        horizontalGuide.position = e.position;
        horizontalGuide.refresh();
    }

    private function horizontalRuler_dragend(e:MouseEvent) {
        view.stage.cursor = MouseCursorKind.DEFAULT;
        if (e.screenPosition.y - view.viewport.screenOffset.y < 0)
            view.stage.remove(cast(horizontalGuide.renderer, ComponentRenderer));
    }

    private function verticalRuler_dragstart(e:MouseEvent) {
        verticalGuide = componentFactory.create(VerticalGuide);
        verticalGuide.position = e.position;
        view.stage.cursor = MouseCursorKind.CROSSHAIR;
        verticalGuide.refresh();
    }

    private function verticalRuler_drag(e:MouseEvent) {
        verticalGuide.position = e.position;
        verticalGuide.refresh();
    }

    private function verticalRuler_dragend(e:MouseEvent) {
        view.stage.cursor = MouseCursorKind.DEFAULT;
        if (e.screenPosition.x - view.viewport.screenOffset.x < 0)
            view.stage.remove(cast(verticalGuide.renderer, ComponentRenderer));
    }

    private function createHorizontalRuler():Ruler {
        var ruler:Ruler = new Ruler(rendererFactory.create(Ruler, { variant: 'horizontal' }));
        ruler.on.dragstart.do_(this.horizontalRuler_dragstart);
        ruler.on.drag.do_(this.horizontalRuler_drag);
        ruler.on.dragend.do_(this.horizontalRuler_dragend);
        return ruler;
    }

    private function createVerticalRuler():Ruler {
        var ruler:Ruler = new Ruler(rendererFactory.create(Ruler, { variant: 'vertical' }));
        ruler.on.dragstart.do_(this.verticalRuler_dragstart);
        ruler.on.drag.do_(this.verticalRuler_drag);
        ruler.on.dragend.do_(this.verticalRuler_dragend);
        return ruler;
    }

    public function showTooltip() {
    }

    public function new(view:View) {
        this.configuration = {
          preferredUnit: UnitKind.MILLIMETER
        };
        this.view = view;
        this.rendererFactory = new BasicRendererFactoryImpl(
            view, views.rendering.js.dom.Spi.rendererRegistry);
        this.componentFactory = new ComponentFactory(rendererFactory);
        this.workspace = new Workspace(view.stage);
        this.shell = new Shell(this);
        this.horizontalRuler = createHorizontalRuler();
        this.verticalRuler = createVerticalRuler();
        this.view.viewport.on.scroll.do_(function(e) {
            this.horizontalRuler.offset = e.position.x;
            this.verticalRuler.offset = e.position.y;
            this.horizontalRuler.refresh();
            this.verticalRuler.refresh();
        });
        this.boundingBox = new BoundingBox(
            cast rendererFactory.create(BoundingBox));
        this.view.stage.add(cast boundingBox.renderer);
    }

    public function refresh() {
        this.horizontalRuler.refresh();
        this.verticalRuler.refresh();
        this.boundingBox.refresh();
        this.view.refresh();
    }
}
