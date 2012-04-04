import views.View;
import views.Component;
import views.ComponentRenderer;
import views.ComponentFactory;
import views.MouseCursorKind;
import views.EventKind;
import views.MouseEvent;
import views.Workspace;

private enum State {
    NONE;
    DRAGGING(initialScrollPosition:Point, initialPosition:Point);
}

class Shell {
    public var operationMode(default, set_operationMode):OperationMode;
    public var view(default, null):View;
    public var workspace(default, null):Workspace;
    public var operationModeCallback:OperationMode->Void;
    public var lastKey:Int;

    var ghost:ComponentRenderer;
    var ghostData:Dynamic;
    var componentFactory:ComponentFactory;
    var inMoveMode:Bool;

    private function set_operationMode(newOperationMode:OperationMode):OperationMode {
        discardGhost();
        finishMoveMode();
        switch (newOperationMode) {
        case CURSOR:
            view.stage.cursor = MouseCursorKind.DEFAULT;  
        case MOVE:
            view.stage.cursor = MouseCursorKind.MOVE;
            beginMoveMode();
        case PLACE(item):
            view.stage.cursor = MouseCursorKind.POINTER;
            prepareGhost(item);
        }
        if (operationModeCallback != null)
            operationModeCallback(newOperationMode);
        operationMode = newOperationMode;
        return newOperationMode;
    }

    function discardGhost() {
        if (ghost == null)
            return;
        view.stage.remove(ghost);
        ghost.dispose();
        ghost = null;
        ghostData = null;
    }

    function prepareGhost(klass:Class<Component>) {
        if (ghost != null)
            throw new IllegalStateException("Ghost already exists");
        ghost = cast componentFactory.rendererFactory.create(cast klass);
        ghost.opacity = .5;
        ghostData = {
            position: { x: 0, y: -30 },
            text: "text",
            fontSize: 10.5,
            size: { x: 0.25, y: 0.16 }
        };
        view.stage.add(ghost);
        ghost.opacity = .5;
        ghost.bind(EventKind.MOUSEMOVE, function(e:Event) {
            ghostData.position = { x:(cast e).position.x - ghost.innerRenderSize.x / 2, y:(cast e).position.y - ghost.innerRenderSize.y / 2 };
            ghost.realize(ghostData);
        });
        ghost.bind(EventKind.PRESS, function(e:Event) {
            var component:Component = componentFactory.create(klass);
            for (field in Reflect.fields(ghostData)) {
                if (Reflect.hasField(component, field)) {
                    Reflect.setField(component, field,
                        Reflect.field(ghostData, field));
                }
            }
            attachController(component);
            component.refresh();
        });
        ghost.realize(ghostData);
        ghost.captureMouse();
    }

    function attachController(component:Component) {
        component.on.press.do_(function (e) {
            if (!component.selected && lastKey != 16) {
                workspace.clearSelection();
                component.putResizeBox();
            }
            if (lastKey == 16) {
                if (component.selected)
                    component.unselect();
                else
                    component.select();
            } else {
                component.select();
            }
        });
        component.on.dragstart.do_(function (e) {
            component.hideResizeBox();
        });
        component.on.dragend.do_(function (e) {
            if (workspace.numOfSelections == 1)
                component.putResizeBox();
        });
        component.on.blur.do_(function (e) {
            component.hideResizeBox();
        });
        workspace.add(component);
    }

    function finishMoveMode() {
        if (!inMoveMode)
            return;
        view.stage.releaseMouse();
        view.stage.bind(PRESS, onStagePressed);
        view.stage.bind(RELEASE, null);
        view.stage.bind(MOUSEMOVE, null);
        inMoveMode = false;
    }

    function beginMoveMode() {
        if (inMoveMode)
            return;
        var state:State = NONE;
        view.stage.bind(PRESS, function(e:Event) {
            state = DRAGGING(view.viewport.scrollPosition, cast(e).screenPosition);
        });
        view.stage.bind(RELEASE, function(e:Event) {
            state = NONE;
        });
        view.stage.bind(MOUSEMOVE, function(e:Event) {
            var e_:MouseEvent = cast(e);
            switch (state) {
            case NONE:
            case DRAGGING(initialScrollPosition, initialPosition):
                var offset = view.pixelToInchP({
                    x: e_.screenPosition.x - initialPosition.x,
                    y: e_.screenPosition.y - initialPosition.y
                });
                var newScrollPosition = {
                    x: initialScrollPosition.x - offset.x,
                    y: initialScrollPosition.y - offset.y
                };
                if (newScrollPosition.x < 0.) {
                    initialScrollPosition = {
                        x: 0.,
                        y: initialScrollPosition.y,
                    };
                    initialPosition = {
                        x: e_.screenPosition.x,
                        y: initialPosition.y
                    };
                    state = DRAGGING(initialScrollPosition, initialPosition);
                    newScrollPosition.x = 0.;
                }
                if (newScrollPosition.y < 0.) {
                    initialScrollPosition = {
                        x: initialScrollPosition.x,
                        y: 0.,
                    };
                    initialPosition = {
                        x: initialPosition.x,
                        y: e_.screenPosition.y
                    };
                    state = DRAGGING(initialScrollPosition, initialPosition);
                    newScrollPosition.y = 0.;
                }
                view.viewport.scrollPosition = newScrollPosition;
            }
        });
        view.stage.captureMouse();
        inMoveMode = true;
    }

    public function zoomIn() {
      view.zoom *= 1.1;
    }

    public function zoomOut() {
      view.zoom /= 1.1;
    }

    public function onStagePressed(e:Event) {
        workspace.clearSelection();
    }

    public function new(view:View, componentFactory:ComponentFactory, workspace:Workspace) {
        this.view = view;
        this.componentFactory = componentFactory;
        this.workspace = workspace;
        this.inMoveMode = false;
        this.lastKey = 0;
        view.stage.bind(PRESS, onStagePressed);
    }
}
