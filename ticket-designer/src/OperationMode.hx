enum OperationMode {
    CURSOR;
    MOVE;
    PLACE(item:Class<views.Component>);
}
