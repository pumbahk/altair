import views.View;
import views.Component;
import views.ComponentRenderer;
import views.ComponentFactory;
import views.MouseCursorKind;
import views.EventKind;
import views.MouseEvent;
import views.Workspace;
import views.RubberBand;
import views.Renderer;
import views.Tooltip;

private enum State {
    NONE;
    DRAGGING(initialScrollPosition:Point, initialPosition:Point);
}

class Shell {
    public var application(default, null):DiagramEditorApplication;
    public var operationMode(default, set_operationMode):OperationMode;
    public var operationModeCallback:OperationMode->Void;
    public var lastKey:Int;

    var ghost:ComponentRenderer;
    var ghostData:Dynamic;
    var rubberBand:RubberBand;
    var tooltip:Tooltip;
    var resizeBox:Renderer;
    var workspaceController:WorkspaceController;

    private function set_operationMode(newOperationMode:OperationMode):OperationMode {
        if (newOperationMode == operationMode)
            return newOperationMode;
        discardGhost();
        endMoveMode();
        application.workspace.clearSelection();
        switch (newOperationMode) {
        case CURSOR:
            application.view.stage.cursor = MouseCursorKind.DEFAULT;  
        case MOVE:
            application.view.stage.cursor = MouseCursorKind.MOVE;
            beginMoveMode();
        case PLACE(item):
            application.view.stage.cursor = MouseCursorKind.POINTER;
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
        application.view.stage.remove(ghost);
        ghost.dispose();
        ghost = null;
        ghostData = null;
    }

    function createGhostData(klass:Class<Component>) {
        var ghostData:Dynamic = {
            position: { x: 0, y: -30 }
        };

        switch (klass) {
        case views.ImageComponent:
            ghostData.size = { x: 0.5, y: 0.5 };
            ghostData.preferredUnit = application.configuration.preferredUnit;
        case views.TextComponent:
            ghostData.text = "text";
            ghostData.fontSize = 10.5;
            ghostData.size = { x: 0.25, y: 0.16 };
        }
        return ghostData;
    }

    function prepareGhost(klass:Class<Component>) {
        if (ghost != null)
            throw new IllegalStateException("Ghost already exists");
        ghost = cast application.rendererFactory.create(cast klass);
        ghost.opacity = .5;
        ghostData = createGhostData(klass);
        application.view.stage.add(ghost);
        ghost.opacity = .5;
        ghost.bind(EventKind.MOUSEMOVE, function(e:Event) {
            ghostData.position = { x:(cast e).position.x - ghost.innerRenderSize.x / 2, y:(cast e).position.y - ghost.innerRenderSize.y / 2 };
            ghost.realize(ghostData);
        });
        ghost.bind(EventKind.PRESS, function(e:MouseEvent) {
            if (Utils.pointWithinRect(e.screenPosition, { position:application.view.viewport.screenOffset, size:application.view.viewport.size })) {
                var component:Component = application.componentFactory.create(klass);
                for (field in Reflect.fields(ghostData)) {
                    if (Reflect.hasField(component, field)) {
                        Reflect.setField(component, field,
                            Reflect.field(ghostData, field));
                    }
                }
                attachController(component);
                component.refresh();
            }
        });
        ghost.realize(ghostData);
        ghost.captureMouse();
    }

    public function putResizeBox(component:Component) {
        if (resizeBox != null)
            return;
        var resizeBox = application.rendererFactory.create(cast Type.getClass(component), { variant: "resize_box" });
        application.workspace.stage.add(cast resizeBox);
        resizeBox.bind(PRESS, function(e) {
            var corner = cast(e.extra, Direction);
            var startPosition = e.position;
            var initialPosition = component.position;
            var initialSize = component.size;
            resizeBox.bind(MOUSEMOVE, function(e) {
                switch (corner) {
                case NORTH_WEST:
                    component.position = {
                        x: initialPosition.x + (e.position.x - startPosition.x),
                        y: initialPosition.y + (e.position.y - startPosition.y)
                    };
                    component.size = {
                        x: initialSize.x - (e.position.x - startPosition.x),
                        y: initialSize.y - (e.position.y - startPosition.y),
                    };
                case NORTH_EAST:
                    component.position = {
                        x: initialPosition.x,
                        y: initialPosition.y + (e.position.y - startPosition.y)
                    };
                    component.size = {
                        x: initialSize.x + (e.position.x - startPosition.x),
                        y: initialSize.y - (e.position.y - startPosition.y),
                    };
                case SOUTH_WEST:
                    component.position = {
                        x: initialPosition.x + (e.position.x - startPosition.x),
                        y: initialPosition.y
                    };
                    component.size = {
                        x: initialSize.x - (e.position.x - startPosition.x),
                        y: initialSize.y + (e.position.y - startPosition.y),
                    };
                case SOUTH_EAST:
                    component.size = {
                        x: initialSize.x + (e.position.x - startPosition.x),
                        y: initialSize.y + (e.position.y - startPosition.y),
                    };
                default:
                }
                resizeBox.realize(component);
                component.refresh();
            });
            resizeBox.bind(RELEASE, function(e) {
                resizeBox.releaseMouse();
                resizeBox.bind(MOUSEMOVE, null);
                resizeBox.bind(RELEASE, null);
            });
            resizeBox.captureMouse();
        });
        resizeBox.realize(component);
        this.resizeBox = resizeBox;
    }

    public function hideResizeBox() {
        if (resizeBox == null)
            return;
        application.workspace.stage.remove(cast resizeBox);
        resizeBox.dispose();
        resizeBox = null;
    }

    public function beginMoveMode() {
        workspaceController.inMoveMode = true;
    }

    public function endMoveMode() {
        workspaceController.inMoveMode = false;
    }

    function attachController(component:Component) {
        component.on.press.do_(function (e) {
            if (workspaceController.inMoveMode)
                return;
            if (!component.selected && lastKey != 16) {
                application.workspace.clearSelection();
                putResizeBox(component);
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
        component.on.blur.do_(function (e) {
            hideResizeBox();
        });
        application.workspace.add(component);
    }

    function beginRubberBand(position:Point) {
        if (rubberBand != null)
            throw new IllegalStateException("Rubberband already exists");
        rubberBand = new RubberBand(
            cast application.rendererFactory.create(RubberBand));
        rubberBand.initialPosition = rubberBand.position = position;
        cast(rubberBand.renderer).opacity = .5;
        rubberBand.renderer.captureMouse();
        rubberBand.on.release.do_(function (e) {
            for (component in application.workspace.components) {
                if (Utils.rectWithinRect(component, rubberBand))
                    component.select();
            }
            endRubberBand();
        });
        application.view.stage.add(cast rubberBand.renderer);
    }

    function endRubberBand() {
        if (rubberBand == null)
            return;
        rubberBand.renderer.releaseMouse();
        application.view.stage.remove(cast rubberBand.renderer);
        rubberBand.renderer.dispose();
        rubberBand = null;
    }

    public function zoomIn() {
      application.view.zoom *= 1.1;
    }

    public function zoomOut() {
      application.view.zoom /= 1.1;
    }

    public function deleteSelected() {
        for (component in application.workspace.selection) {
            application.workspace.remove(component);
        }
    }

    public function new(application:DiagramEditorApplication) {
        this.application = application;
        this.workspaceController = new WorkspaceController(
                application.workspace,
                application.view,
                application.rendererFactory);
        this.lastKey = 0;
        application.workspace.on.press.do_(function (e) {
            if (workspaceController.inMoveMode || e.target != null)
                return;
            application.workspace.clearSelection();
            beginRubberBand(e.position);
        });
        application.workspace.on.release.do_(function (e) {
            endRubberBand();
        });
        workspaceController.on.dragstart.do_(function (e) {
            hideResizeBox();
        });
        workspaceController.on.dragend.do_(function (e) {
            if (application.workspace.selectionCount == 1)
                putResizeBox(application.workspace.selection[0]);
        });
    }
}
