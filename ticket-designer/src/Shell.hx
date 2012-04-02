private enum State {
    NONE;
    DRAGGING(initialScrollPosition:Point, initialPosition:Point);
}

class Shell {
    public var operationMode(default, set_operationMode):OperationMode;
    public var view(default, null):View;
    public var operationModeCallback:OperationMode->Void;
    public var ghost:ComponentRenderer;
    public var ghostData:Dynamic;
    public var componentFactory:ComponentFactory;

    private function set_operationMode(newOperationMode:OperationMode):OperationMode {
        if (operationMode == OperationMode.MOVE) {
            view.stage.releaseMouse();
            view.stage.bind(PRESS, null);
            view.stage.bind(RELEASE, null);
            view.stage.bind(MOUSEMOVE, null);
        }
        discardGhost();
        switch (newOperationMode) {
        case CURSOR:
            view.stage.cursor = MouseCursorKind.DEFAULT;  
        case MOVE:
            view.stage.cursor = MouseCursorKind.MOVE;
            var state:State = NONE;
            view.stage.bind(PRESS, function(e:Event) {
                state = DRAGGING(view.viewport.scrollPosition, cast(e).position);
            });
            view.stage.bind(RELEASE, function(e:Event) {
                state = NONE;
            });
            view.stage.bind(MOUSEMOVE, function(e:Event) {
                var e_:MouseEvent = cast(e);
                switch (state) {
                case NONE:
                case DRAGGING(initialScrollPosition, initialPosition):
                    var offset = {
                        x: e_.position.x - initialPosition.x,
                        y: e_.position.y - initialPosition.y
                    };
                    var newScrollPosition = {
                        x: initialScrollPosition.x - offset.x,
                        y: initialScrollPosition.y - offset.y
                    };
                    if (newScrollPosition.x < 0.) {
                        newScrollPosition.x = 0.;
                        state = DRAGGING(initialScrollPosition, {
                            x: e_.position.x + newScrollPosition.x,
                            y: initialPosition.y
                        });
                    }
                    if (newScrollPosition.y < 0.) {
                        state = DRAGGING(initialScrollPosition, {
                            x: initialPosition.x,
                            y: e_.position.y + newScrollPosition.y
                        });
                        newScrollPosition.y = 0.;
                    }
                    view.viewport.scrollPosition = newScrollPosition;
                }
            });
            view.stage.captureMouse();
        case PLACE(item):
            view.stage.cursor = MouseCursorKind.POINTER;
            prepareGhost(item);
        }
        if (operationModeCallback != null)
            operationModeCallback(newOperationMode);
        operationMode = newOperationMode;
        return newOperationMode;
    }

    public function discardGhost() {
        if (ghost == null)
            return;
        ghost.releaseMouse();
        view.stage.remove(ghost);
        ghost = null;
        ghostData = null;
    }

    public function prepareGhost(klass:Class<Component>) {
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
            component.refresh();
        });
        ghost.realize(ghostData);
        ghost.captureMouse();
    }

    public function zoomIn() {
      view.zoom *= 1.1;
    }

    public function zoomOut() {
      view.zoom /= 1.1;
    }

    public function new(view:View, componentFactory:ComponentFactory) {
        this.view = view;
        this.componentFactory = componentFactory;
    }
}
