class Shell {
    public var operationMode(default, set_operationMode):OperationMode;
    public var view(default, null):View;
    public var operationModeCallback:OperationMode->Void;

    private function set_operationMode(newOperationMode:OperationMode):OperationMode {
        switch (newOperationMode) {
        case CURSOR:
            view.stage.cursor = MouseCursorKind.DEFAULT;  
        case MOVE:
            view.stage.cursor = MouseCursorKind.MOVE;  
        case PLACE(item):
            view.stage.cursor = MouseCursorKind.DEFAULT;  
        }
        if (operationModeCallback != null)
            operationModeCallback(newOperationMode);
        operationMode = newOperationMode;
        return newOperationMode;
    }

    public function zoomIn() {
      view.zoom *= 1.1;
    }

    public function zoomOut() {
      view.zoom /= 1.1;
    }

    public function new(view:View) {
        this.view = view;
    }
}
