import views.View;
import views.Workspace;
import views.ComponentFactory;
import views.RendererFactory;

interface DiagramEditorApplication implements Application {
    public var view(default, null):View;
    public var workspace(default, null):Workspace;
    public var componentFactory(default, null):ComponentFactory;
    public var rendererFactory(default, null):RendererFactory;
}
