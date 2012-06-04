import views.RendererFactory;
import views.Workspace;
import views.Component;
import views.View;
import views.WorkspaceEvent;

private enum State {
    NONE;
    PRESSED(position:Point);
    DRAGGING(pof:Point, selection:Array<Component>);
    MOVING(initialScrollPosition:Point, initialPosition:Point);
}

@events("dragstart", "drag", "dragend")
class WorkspaceController extends EventProducer {
    public var view(default, null):View;
    public var workspace(default, null):Workspace;
    public var rendererFactory(default, null):RendererFactory;
    public var inMoveMode:Bool;

    var state:State;

    function bindEvents() {
        var pressed = false;

        workspace.on.press.do_(function(e:WorkspaceEvent) {
            if (inMoveMode) {
                state = MOVING(view.viewport.scrollPosition, e.screenPosition);
                workspace.captureMouse();
            } else {
                if (e.target != null) {
                    state = PRESSED(e.position);
                    workspace.captureMouse();
                }
            }
        });
        workspace.on.mousemove.do_(function(e:WorkspaceEvent) {
            switch (state) {
            case PRESSED(pof):
                var selection = workspace.selection;
                state = DRAGGING(e.position, selection);
                var delta = {
                    x: e.position.x - pof.x,
                    y: e.position.y - pof.y
                };
                for (component in selection) {
                    if (!component.draggable)
                        continue;
                    cast(component.renderer).opacity = .5;
                    component.position =
                        PointUtils.add(component.position, delta);
                    component.refresh();
                }
                on.dragstart.call(this, e);
            case DRAGGING(pof, selection):
                state = DRAGGING(e.position, selection);
                var delta = {
                    x: e.position.x - pof.x,
                    y: e.position.y - pof.y
                };
                for (component in selection) {
                    if (!component.draggable)
                        continue;
                    cast(component.renderer).opacity = .5;
                    component.position =
                        PointUtils.add(component.position, delta);
                    component.refresh();
                }
                on.drag.call(this, e);
            case MOVING(initialScrollPosition, initialPosition):
                var offset = view.pixelToInchP(
                    PointUtils.sub(e.screenPosition, initialPosition));
                var newScrollPosition = PointUtils.sub(
                    initialScrollPosition, offset);
                if (newScrollPosition.x < 0.) {
                    initialScrollPosition = {
                        x: 0.,
                        y: initialScrollPosition.y,
                    };
                    initialPosition = {
                        x: e.screenPosition.x,
                        y: initialPosition.y
                    };
                    state = MOVING(initialScrollPosition, initialPosition);
                    newScrollPosition.x = 0.;
                }
                if (newScrollPosition.y < 0.) {
                    initialScrollPosition = {
                        x: initialScrollPosition.x,
                        y: 0.,
                    };
                    initialPosition = {
                        x: initialPosition.x,
                        y: e.screenPosition.y
                    };
                    state = MOVING(initialScrollPosition, initialPosition);
                    newScrollPosition.y = 0.;
                }
                view.viewport.scrollPosition = newScrollPosition;
            default:
            }
        });
        workspace.on.release.do_(function(e:WorkspaceEvent) {
            workspace.releaseMouse();
            switch (state) {
            case DRAGGING(_, selection):
                for (component in selection) {
                    if (!component.draggable)
                        continue;
                    cast(component.renderer).opacity = 1.;
                    component.refresh();
                }
                on.dragend.call(this, e);
            default:
            }
            state = NONE;
        });
    }

    public function new(workspace:Workspace, view:View, rendererFactory:RendererFactory) {
        super();
        this.workspace = workspace;
        this.view = view;
        this.rendererFactory = rendererFactory;
        this.state = NONE;
        this.inMoveMode = false;
        this.bindEvents();
    }
}
