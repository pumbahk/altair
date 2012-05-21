$estr = function() { return js.Boot.__string_rec(this,''); }
if(typeof models=='undefined') models = {}
models.Workspace = function() { }
models.Workspace.__name__ = ["models","Workspace"];
models.Workspace.prototype.__class__ = models.Workspace;
if(typeof views=='undefined') views = {}
if(!views.rendering) views.rendering = {}
if(!views.rendering.js) views.rendering.js = {}
if(!views.rendering.js.dom) views.rendering.js.dom = {}
views.rendering.js.dom.MouseEventsHandlerManager = function(p) {
	if( p === $_ ) return;
	this.nextId = 1;
	this.capturing = null;
	this.mouseEventsHandlers = new Hash();
	this.eventHandlerHash = new Hash();
}
views.rendering.js.dom.MouseEventsHandlerManager.__name__ = ["views","rendering","js","dom","MouseEventsHandlerManager"];
views.rendering.js.dom.MouseEventsHandlerManager.getEventNameFor = function(eventKind) {
	return views.rendering.js.dom.MouseEventsHandlerManager.eventNames[eventKind[1]];
}
views.rendering.js.dom.MouseEventsHandlerManager.buildEventHandlerKey = function(mouseEventsHandler,eventName) {
	return Std.string(mouseEventsHandler.id) + ":" + eventName;
}
views.rendering.js.dom.MouseEventsHandlerManager.prototype.nextId = null;
views.rendering.js.dom.MouseEventsHandlerManager.prototype.capturing = null;
views.rendering.js.dom.MouseEventsHandlerManager.prototype.mouseEventsHandlers = null;
views.rendering.js.dom.MouseEventsHandlerManager.prototype.eventHandlerHash = null;
views.rendering.js.dom.MouseEventsHandlerManager.prototype.captureMouse = function(mouseEventsHandler) {
	if(this.capturing != null) throw new IllegalStateException("mouse has already been captured by " + this.capturing);
	this.capturing = mouseEventsHandler;
	if(this.capturing.onPress != null) new js.JQuery(js.Lib.document).bind("mousedown",this.capturing.onPress);
	if(this.capturing.onRelease != null) new js.JQuery(js.Lib.document).bind("mouseup",this.capturing.onRelease);
	if(this.capturing.onMouseMove != null) new js.JQuery(js.Lib.document).bind("mousemove",this.capturing.onMouseMove);
}
views.rendering.js.dom.MouseEventsHandlerManager.prototype.releaseMouse = function(mouseEventsHandler) {
	if(this.capturing != mouseEventsHandler) return;
	if(this.capturing.onPress != null) new js.JQuery(js.Lib.document).unbind("mousedown",this.capturing.onPress);
	if(this.capturing.onRelease != null) new js.JQuery(js.Lib.document).unbind("mouseup",this.capturing.onRelease);
	if(this.capturing.onMouseMove != null) new js.JQuery(js.Lib.document).unbind("mousemove",this.capturing.onMouseMove);
	this.capturing = null;
}
views.rendering.js.dom.MouseEventsHandlerManager.prototype.bindEvent = function(mouseEventsHandler,eventKind) {
	var me = this;
	var eventName = views.rendering.js.dom.MouseEventsHandlerManager.eventNames[eventKind[1]];
	var key = Std.string(mouseEventsHandler.id) + ":" + eventName;
	if(this.eventHandlerHash.get(key) != null) throw new IllegalStateException("event " + eventName + " is already bound");
	var handlerFunction = mouseEventsHandler.getHandlerFunctionFor(eventKind);
	var closure = function(e) {
		if(me.capturing == null || me.capturing.n[0] == e.target) {
			handlerFunction(e);
			return false;
		}
		return true;
	};
	this.eventHandlerHash.set(key,closure);
	mouseEventsHandler.n.bind(eventName,closure);
}
views.rendering.js.dom.MouseEventsHandlerManager.prototype.unbindEvent = function(mouseEventsHandler,eventKind) {
	var eventName = views.rendering.js.dom.MouseEventsHandlerManager.eventNames[eventKind[1]];
	var key = Std.string(mouseEventsHandler.id) + ":" + eventName;
	var handlerFunction = this.eventHandlerHash.get(key);
	if(handlerFunction == null) throw new IllegalStateException("event " + eventName + " is not bound yet");
	mouseEventsHandler.n.unbind(eventName,handlerFunction);
	this.eventHandlerHash.remove(key);
}
views.rendering.js.dom.MouseEventsHandlerManager.prototype.registerHandler = function(mouseEventsHandler) {
	mouseEventsHandler.id = this.nextId++;
	this.mouseEventsHandlers.set(Std.string(mouseEventsHandler.id),mouseEventsHandler);
	return mouseEventsHandler;
}
views.rendering.js.dom.MouseEventsHandlerManager.prototype.unregisterHandler = function(mouseEventsHandler) {
	this.mouseEventsHandlers.remove(Std.string(mouseEventsHandler.id));
}
views.rendering.js.dom.MouseEventsHandlerManager.prototype.__class__ = views.rendering.js.dom.MouseEventsHandlerManager;
Identifiable = function() { }
Identifiable.__name__ = ["Identifiable"];
Identifiable.prototype.id = null;
Identifiable.prototype.__class__ = Identifiable;
views.RendererFactory = function() { }
views.RendererFactory.__name__ = ["views","RendererFactory"];
views.RendererFactory.prototype.create = null;
views.RendererFactory.prototype.__class__ = views.RendererFactory;
views.BasicRendererFactoryImpl = function(view,registry) {
	if( view === $_ ) return;
	this.view = view;
	this.registry = registry;
	this.nextId = 1;
}
views.BasicRendererFactoryImpl.__name__ = ["views","BasicRendererFactoryImpl"];
views.BasicRendererFactoryImpl.prototype.nextId = null;
views.BasicRendererFactoryImpl.prototype.registry = null;
views.BasicRendererFactoryImpl.prototype.view = null;
views.BasicRendererFactoryImpl.prototype.create = function(renderableKlass,options) {
	return Type.createInstance(this.registry.lookupImplementation(renderableKlass,options),[this.nextId++,this.view]);
}
views.BasicRendererFactoryImpl.prototype.__class__ = views.BasicRendererFactoryImpl;
views.BasicRendererFactoryImpl.__interfaces__ = [views.RendererFactory];
views.rendering.js.dom.Spi = function() { }
views.rendering.js.dom.Spi.__name__ = ["views","rendering","js","dom","Spi"];
views.rendering.js.dom.Spi.rendererRegistry = null;
views.rendering.js.dom.Spi.get_rendererRegistry = function() {
	if(views.rendering.js.dom.Spi.rendererRegistry == null) views.rendering.js.dom.Spi.rendererRegistry = new views.RendererRegistry();
	return views.rendering.js.dom.Spi.rendererRegistry;
}
views.rendering.js.dom.Spi.prototype.__class__ = views.rendering.js.dom.Spi;
EventListener = function() { }
EventListener.__name__ = ["EventListener"];
EventListener.prototype.call = null;
EventListener.prototype.__class__ = EventListener;
EventListeners = function(p) {
	if( p === $_ ) return;
	this.listeners = new Array();
}
EventListeners.__name__ = ["EventListeners"];
EventListeners.prototype.listeners = null;
EventListeners.prototype.do_ = function(listener) {
	this.listeners.push(listener);
}
EventListeners.prototype.call = function(context,event) {
	var throwables = new Array();
	var _g = 0, _g1 = this.listeners;
	while(_g < _g1.length) {
		var listener = _g1[_g];
		++_g;
		try {
			listener.call(context,event);
		} catch( e ) {
			if( js.Boot.__instanceof(e,Throwable) ) {
				throwables.push(e);
			} else throw(e);
		}
	}
	if(throwables.length > 0) throw new Throwables(throwables);
}
EventListeners.prototype.__class__ = EventListeners;
EventListeners.__interfaces__ = [EventListener];
views.MouseCapture = function() { }
views.MouseCapture.__name__ = ["views","MouseCapture"];
views.MouseCapture.prototype.captureMouse = null;
views.MouseCapture.prototype.releaseMouse = null;
views.MouseCapture.prototype.__class__ = views.MouseCapture;
Disposable = function() { }
Disposable.__name__ = ["Disposable"];
Disposable.prototype.dispose = null;
Disposable.prototype.__class__ = Disposable;
views.Stage = function() { }
views.Stage.__name__ = ["views","Stage"];
views.Stage.prototype.view = null;
views.Stage.prototype.size = null;
views.Stage.prototype.renderers = null;
views.Stage.prototype.cursor = null;
views.Stage.prototype.screenOffset = null;
views.Stage.prototype.add = null;
views.Stage.prototype.remove = null;
views.Stage.prototype.bind = null;
views.Stage.prototype.__class__ = views.Stage;
views.Stage.__interfaces__ = [views.MouseCapture,Disposable];
views.BasicStageImpl = function(view) {
	if( view === $_ ) return;
	this.renderers_ = new IdentifiableSet();
	this.view = view;
}
views.BasicStageImpl.__name__ = ["views","BasicStageImpl"];
views.BasicStageImpl.prototype.view = null;
views.BasicStageImpl.prototype.size = null;
views.BasicStageImpl.prototype.renderers = null;
views.BasicStageImpl.prototype.cursor = null;
views.BasicStageImpl.prototype.screenOffset = null;
views.BasicStageImpl.prototype.renderers_ = null;
views.BasicStageImpl.prototype.set_cursor = function(value) {
	this.cursor = value;
	return value;
}
views.BasicStageImpl.prototype.add = function(renderer) {
	this.renderers_.add(renderer);
	renderer.set_stage(this);
}
views.BasicStageImpl.prototype.remove = function(renderer) {
	renderer.set_stage(null);
	this.renderers_.remove(renderer);
}
views.BasicStageImpl.prototype.dispose = function() {
	var $it0 = this.renderers_.iterator();
	while( $it0.hasNext() ) {
		var renderer = $it0.next();
		var throwables = new Array();
		try {
			renderer.dispose();
		} catch( e ) {
			if( js.Boot.__instanceof(e,Throwable) ) {
				throwables.push(e);
			} else throw(e);
		}
		if(throwables.length > 0) throw new Throwables(throwables);
	}
}
views.BasicStageImpl.prototype.get_renderers = function() {
	return this.renderers_;
}
views.BasicStageImpl.prototype.get_size = function() {
	return null;
}
views.BasicStageImpl.prototype.set_size = function(value) {
	return value;
}
views.BasicStageImpl.prototype.captureMouse = function() {
}
views.BasicStageImpl.prototype.releaseMouse = function() {
}
views.BasicStageImpl.prototype.bind = function(event_kind,handler) {
}
views.BasicStageImpl.prototype.__class__ = views.BasicStageImpl;
views.BasicStageImpl.__interfaces__ = [views.Stage];
views.rendering.js.dom.JSDOMStage = function(view) {
	if( view === $_ ) return;
	views.BasicStageImpl.call(this,view);
	this.handlers = [null,null,null,null];
}
views.rendering.js.dom.JSDOMStage.__name__ = ["views","rendering","js","dom","JSDOMStage"];
views.rendering.js.dom.JSDOMStage.__super__ = views.BasicStageImpl;
for(var k in views.BasicStageImpl.prototype ) views.rendering.js.dom.JSDOMStage.prototype[k] = views.BasicStageImpl.prototype[k];
views.rendering.js.dom.JSDOMStage.prototype.n = null;
views.rendering.js.dom.JSDOMStage.prototype.size_ = null;
views.rendering.js.dom.JSDOMStage.prototype.mouseEventsHandler = null;
views.rendering.js.dom.JSDOMStage.prototype.handlers = null;
views.rendering.js.dom.JSDOMStage.prototype.refresh = function() {
	this.recalculateBasePageOffset();
	var actualSizeInPixel = ((function($this) {
		var $r;
		var $t = $this.view;
		if(Std["is"]($t,views.rendering.js.dom.JSDOMView)) $t; else throw "Class cast error";
		$r = $t;
		return $r;
	}(this))).inchToPixelP(this.get_size());
	this.n.css({ width : Std.string(actualSizeInPixel.x) + "px", height : Std.string(actualSizeInPixel.y) + "px"});
}
views.rendering.js.dom.JSDOMStage.prototype.set_n = function(value) {
	var me = this;
	if(this.n != null) ((function($this) {
		var $r;
		var $t = $this.view;
		if(Std["is"]($t,views.rendering.js.dom.JSDOMView)) $t; else throw "Class cast error";
		$r = $t;
		return $r;
	}(this))).mouseEventsHandlerManager.unregisterHandler(this.mouseEventsHandler);
	this.n = value;
	this.recalculateBasePageOffset();
	this.size_ = ((function($this) {
		var $r;
		var $t = $this.view;
		if(Std["is"]($t,views.rendering.js.dom.JSDOMView)) $t; else throw "Class cast error";
		$r = $t;
		return $r;
	}(this))).pixelToInchP({ x : 0. + this.n.innerWidth(), y : 0. + this.n.innerHeight()});
	this.mouseEventsHandler = ((function($this) {
		var $r;
		var $t = $this.view;
		if(Std["is"]($t,views.rendering.js.dom.JSDOMView)) $t; else throw "Class cast error";
		$r = $t;
		return $r;
	}(this))).mouseEventsHandlerManager.registerHandler(new views.rendering.js.dom.MouseEventsHandler(this.n,function(e) {
		var handlerFunction = me.handlers[views.EventKind.PRESS[1]];
		if(handlerFunction != null) handlerFunction(me.createMouseEvent(e));
	},function(e) {
		var handlerFunction = me.handlers[views.EventKind.RELEASE[1]];
		if(handlerFunction != null) handlerFunction(me.createMouseEvent(e));
	},function(e) {
		var handlerFunction = me.handlers[views.EventKind.MOUSEMOVE[1]];
		if(handlerFunction != null) handlerFunction(me.createMouseEvent(e));
	},function(e) {
		var handlerFunction = me.handlers[views.EventKind.MOUSEOUT[1]];
		if(handlerFunction != null) handlerFunction(me.createMouseEvent(e));
	}));
	return value;
}
views.rendering.js.dom.JSDOMStage.prototype.recalculateBasePageOffset = function() {
	var offset = this.n.offset();
	this.screenOffset = { x : 0. + offset.left, y : 0. + offset.top};
}
views.rendering.js.dom.JSDOMStage.prototype.get_size = function() {
	return this.size_;
}
views.rendering.js.dom.JSDOMStage.prototype.set_size = function(value) {
	this.size_ = value;
	this.refresh();
	return value;
}
views.rendering.js.dom.JSDOMStage.prototype.set_cursor = function(value) {
	switch( (value)[1] ) {
	case 0:
		this.n.css("cursor","default");
		break;
	case 1:
		this.n.css("cursor","pointer");
		break;
	case 2:
		this.n.css("cursor","crosshair");
		break;
	case 3:
		this.n.css("cursor","move");
		break;
	}
	return views.BasicStageImpl.prototype.set_cursor.call(this,value);
}
views.rendering.js.dom.JSDOMStage.prototype.captureMouse = function() {
	((function($this) {
		var $r;
		var $t = $this.view;
		if(Std["is"]($t,views.rendering.js.dom.JSDOMView)) $t; else throw "Class cast error";
		$r = $t;
		return $r;
	}(this))).mouseEventsHandlerManager.captureMouse(this.mouseEventsHandler);
}
views.rendering.js.dom.JSDOMStage.prototype.releaseMouse = function() {
	((function($this) {
		var $r;
		var $t = $this.view;
		if(Std["is"]($t,views.rendering.js.dom.JSDOMView)) $t; else throw "Class cast error";
		$r = $t;
		return $r;
	}(this))).mouseEventsHandlerManager.releaseMouse(this.mouseEventsHandler);
}
views.rendering.js.dom.JSDOMStage.prototype.bind = function(eventKind,handler) {
	var view_ = (function($this) {
		var $r;
		var $t = $this.view;
		if(Std["is"]($t,views.rendering.js.dom.JSDOMView)) $t; else throw "Class cast error";
		$r = $t;
		return $r;
	}(this));
	var existingHandler = this.handlers[eventKind[1]];
	if(existingHandler == null) {
		if(handler != null) view_.mouseEventsHandlerManager.bindEvent(this.mouseEventsHandler,eventKind);
	} else if(handler == null) view_.mouseEventsHandlerManager.unbindEvent(this.mouseEventsHandler,eventKind);
	this.handlers[eventKind[1]] = handler;
}
views.rendering.js.dom.JSDOMStage.prototype.createMouseEvent = function(e,extra) {
	return { source : this, cause : e, position : this.view.pixelToInchP({ x : (function($this) {
		var $r;
		var $t = e.pageX;
		if(Std["is"]($t,Float)) $t; else throw "Class cast error";
		$r = $t;
		return $r;
	}(this)) - this.screenOffset.x, y : (function($this) {
		var $r;
		var $t = e.pageY;
		if(Std["is"]($t,Float)) $t; else throw "Class cast error";
		$r = $t;
		return $r;
	}(this)) - this.screenOffset.y}), screenPosition : { x : 0. + e.pageX, y : 0. + e.pageY}, left : (e.which & 1) != 0, middle : (e.which & 2) != 0, right : (e.which & 3) != 0, extra : extra};
}
views.rendering.js.dom.JSDOMStage.prototype.__class__ = views.rendering.js.dom.JSDOMStage;
views.Renderer = function() { }
views.Renderer.__name__ = ["views","Renderer"];
views.Renderer.prototype.view = null;
views.Renderer.prototype.innerRenderSize = null;
views.Renderer.prototype.outerRenderSize = null;
views.Renderer.prototype.realize = null;
views.Renderer.prototype.bind = null;
views.Renderer.prototype.trigger = null;
views.Renderer.prototype.__class__ = views.Renderer;
views.Renderer.__interfaces__ = [Identifiable,views.MouseCapture,Disposable];
views.rendering.js.dom.JSDOMRenderer = function(id,view) {
	if( id === $_ ) return;
	this.id = id;
	this.view = view;
	this.view_ = (function($this) {
		var $r;
		var $t = view;
		if(Std["is"]($t,views.rendering.js.dom.JSDOMView)) $t; else throw "Class cast error";
		$r = $t;
		return $r;
	}(this));
	this.handlers = [null,null,null,null];
	this.n = this.setup();
	this.view_.addRenderer(this);
	this.registerMouseEventsHandler();
}
views.rendering.js.dom.JSDOMRenderer.__name__ = ["views","rendering","js","dom","JSDOMRenderer"];
views.rendering.js.dom.JSDOMRenderer.prototype.id = null;
views.rendering.js.dom.JSDOMRenderer.prototype.n = null;
views.rendering.js.dom.JSDOMRenderer.prototype.view = null;
views.rendering.js.dom.JSDOMRenderer.prototype.innerRenderSize = null;
views.rendering.js.dom.JSDOMRenderer.prototype.outerRenderSize = null;
views.rendering.js.dom.JSDOMRenderer.prototype.mouseEventsHandler = null;
views.rendering.js.dom.JSDOMRenderer.prototype.view_ = null;
views.rendering.js.dom.JSDOMRenderer.prototype.handlers = null;
views.rendering.js.dom.JSDOMRenderer.prototype.innerRenderSize_ = null;
views.rendering.js.dom.JSDOMRenderer.prototype.outerRenderSize_ = null;
views.rendering.js.dom.JSDOMRenderer.prototype.get_innerRenderSize = function() {
	return this.innerRenderSize_;
}
views.rendering.js.dom.JSDOMRenderer.prototype.get_outerRenderSize = function() {
	return this.outerRenderSize_;
}
views.rendering.js.dom.JSDOMRenderer.prototype.setup = function() {
	return null;
}
views.rendering.js.dom.JSDOMRenderer.prototype.dispose = function() {
	this.releaseMouse();
	this.bind(views.EventKind.PRESS,null);
	this.bind(views.EventKind.RELEASE,null);
	this.bind(views.EventKind.MOUSEMOVE,null);
	this.bind(views.EventKind.MOUSEOUT,null);
	if(this.n != null) this.n.remove();
}
views.rendering.js.dom.JSDOMRenderer.prototype.captureMouse = function() {
	if(this.mouseEventsHandler != null) this.view_.mouseEventsHandlerManager.captureMouse(this.mouseEventsHandler);
}
views.rendering.js.dom.JSDOMRenderer.prototype.releaseMouse = function() {
	if(this.mouseEventsHandler != null) this.view_.mouseEventsHandlerManager.releaseMouse(this.mouseEventsHandler);
}
views.rendering.js.dom.JSDOMRenderer.prototype.realize = function(renderable) {
}
views.rendering.js.dom.JSDOMRenderer.prototype.refresh = function() {
	this.innerRenderSize_ = this.view_.pixelToInchP({ x : 0. + this.n.innerWidth(), y : 0. + this.n.innerHeight()});
	this.outerRenderSize_ = this.view_.pixelToInchP({ x : 0. + this.n.outerWidth(), y : 0. + this.n.outerHeight()});
}
views.rendering.js.dom.JSDOMRenderer.prototype.createMouseEvent = function(e,extra) {
	return null;
}
views.rendering.js.dom.JSDOMRenderer.prototype.bind = function(eventKind,handler) {
	var view_ = (function($this) {
		var $r;
		var $t = $this.view;
		if(Std["is"]($t,views.rendering.js.dom.JSDOMView)) $t; else throw "Class cast error";
		$r = $t;
		return $r;
	}(this));
	var existingHandler = this.handlers[eventKind[1]];
	if(existingHandler == null) {
		if(handler != null) view_.mouseEventsHandlerManager.bindEvent(this.mouseEventsHandler,eventKind);
	} else if(handler == null) view_.mouseEventsHandlerManager.unbindEvent(this.mouseEventsHandler,eventKind);
	this.handlers[eventKind[1]] = handler;
}
views.rendering.js.dom.JSDOMRenderer.prototype.trigger = function(eventKind,event) {
	this.handlers[eventKind[1]](event);
}
views.rendering.js.dom.JSDOMRenderer.prototype.registerMouseEventsHandler = function() {
	var me = this;
	this.mouseEventsHandler = ((function($this) {
		var $r;
		var $t = $this.view;
		if(Std["is"]($t,views.rendering.js.dom.JSDOMView)) $t; else throw "Class cast error";
		$r = $t;
		return $r;
	}(this))).mouseEventsHandlerManager.registerHandler(new views.rendering.js.dom.MouseEventsHandler(this.n,function(e) {
		var handlerFunction = me.handlers[views.EventKind.PRESS[1]];
		if(handlerFunction != null) handlerFunction(me.createMouseEvent(e));
	},function(e) {
		var handlerFunction = me.handlers[views.EventKind.RELEASE[1]];
		if(handlerFunction != null) handlerFunction(me.createMouseEvent(e));
	},function(e) {
		var handlerFunction = me.handlers[views.EventKind.MOUSEMOVE[1]];
		if(handlerFunction != null) handlerFunction(me.createMouseEvent(e));
	},function(e) {
		var handlerFunction = me.handlers[views.EventKind.MOUSEOUT[1]];
		if(handlerFunction != null) handlerFunction(me.createMouseEvent(e));
	}));
}
views.rendering.js.dom.JSDOMRenderer.prototype.toString = function() {
	return Type.getClassName(Type.getClass(this)) + "{ id: " + this.id + " }";
}
views.rendering.js.dom.JSDOMRenderer.prototype.__class__ = views.rendering.js.dom.JSDOMRenderer;
views.rendering.js.dom.JSDOMRenderer.__interfaces__ = [views.Renderer];
views.ComponentRenderer = function() { }
views.ComponentRenderer.__name__ = ["views","ComponentRenderer"];
views.ComponentRenderer.prototype.opacity = null;
views.ComponentRenderer.prototype.stage = null;
views.ComponentRenderer.prototype.__class__ = views.ComponentRenderer;
views.ComponentRenderer.__interfaces__ = [views.Renderer];
views.rendering.js.dom.JSDOMComponentRenderer = function(id,view) {
	if( id === $_ ) return;
	views.rendering.js.dom.JSDOMRenderer.call(this,id,view);
	this.opacity = 1.0;
	this.stage_ = null;
}
views.rendering.js.dom.JSDOMComponentRenderer.__name__ = ["views","rendering","js","dom","JSDOMComponentRenderer"];
views.rendering.js.dom.JSDOMComponentRenderer.__super__ = views.rendering.js.dom.JSDOMRenderer;
for(var k in views.rendering.js.dom.JSDOMRenderer.prototype ) views.rendering.js.dom.JSDOMComponentRenderer.prototype[k] = views.rendering.js.dom.JSDOMRenderer.prototype[k];
views.rendering.js.dom.JSDOMComponentRenderer.prototype.stage_ = null;
views.rendering.js.dom.JSDOMComponentRenderer.prototype.opacity = null;
views.rendering.js.dom.JSDOMComponentRenderer.prototype.stage = null;
views.rendering.js.dom.JSDOMComponentRenderer.prototype.get_stage = function() {
	return this.stage_;
}
views.rendering.js.dom.JSDOMComponentRenderer.prototype.set_stage = function(stage) {
	if(this.n != null) this.n.detach();
	if(stage != null) {
		this.stage_ = (function($this) {
			var $r;
			var $t = stage;
			if(Std["is"]($t,views.rendering.js.dom.JSDOMStage)) $t; else throw "Class cast error";
			$r = $t;
			return $r;
		}(this));
		if(this.n != null) this.n.appendTo(this.stage_.n);
	} else this.stage_ = null;
	return stage;
}
views.rendering.js.dom.JSDOMComponentRenderer.prototype.refresh = function() {
	views.rendering.js.dom.JSDOMRenderer.prototype.refresh.call(this);
	this.n.css("opacity",Std.string(this.opacity));
}
views.rendering.js.dom.JSDOMComponentRenderer.prototype.createMouseEvent = function(e,extra) {
	return { source : this, cause : e, position : this.view_.pixelToInchP({ x : e.pageX - this.stage_.screenOffset.x, y : e.pageY - this.stage_.screenOffset.y}), screenPosition : { x : 0. + e.pageX, y : 0. + e.pageY}, left : (e.which & 1) != 0, middle : (e.which & 2) != 0, right : (e.which & 3) != 0, extra : extra};
}
views.rendering.js.dom.JSDOMComponentRenderer.prototype.__class__ = views.rendering.js.dom.JSDOMComponentRenderer;
views.rendering.js.dom.JSDOMComponentRenderer.__interfaces__ = [views.ComponentRenderer];
views.RendererRegistry = function(p) {
	if( p === $_ ) return;
	this.klassesMap = new Hash();
}
views.RendererRegistry.__name__ = ["views","RendererRegistry"];
views.RendererRegistry.prototype.klassesMap = null;
views.RendererRegistry.prototype.addImplementation = function(renderableKlass,rendererKlass,variant) {
	var className = Type.getClassName(renderableKlass);
	var klasses = this.klassesMap.get(className);
	if(klasses == null) this.klassesMap.set(className,klasses = new Hash());
	klasses.set(variant == null?"":variant,rendererKlass);
}
views.RendererRegistry.prototype.lookupImplementationInternal = function(renderableKlass,options) {
	var className = Type.getClassName(renderableKlass);
	var klasses = this.klassesMap.get(className);
	if(klasses != null) {
		var variant = options != null?options.variant:"";
		var klass = klasses.get(variant);
		if(klass != null) return klass;
	}
	var superKlass = Type.getSuperClass(renderableKlass);
	if(superKlass == null) return null;
	return this.lookupImplementationInternal(superKlass,options);
}
views.RendererRegistry.prototype.lookupImplementation = function(renderableKlass,options) {
	var klass = this.lookupImplementationInternal(renderableKlass,options);
	if(klass == null) throw new IllegalArgumentException("no implementation is registered for " + Type.getClassName(renderableKlass));
	return klass;
}
views.RendererRegistry.prototype.__class__ = views.RendererRegistry;
views.Component = function(factory,id,renderer) {
	if( factory === $_ ) return;
	this.factory = factory;
	this.renderer = renderer;
	this.id = id;
	var meta = haxe.rtti.Meta.getType(Type.getClass(this));
	var on = { click : null, dragstart : null, dragend : null};
	var events = ["click","doubleclick","dragstart","drag","dragend","focused","blur"];
	if(meta.events != null) events.concat(meta.events);
	var _g = 0;
	while(_g < events.length) {
		var eventKind = events[_g];
		++_g;
		on[eventKind] = new EventListeners();
	}
	this.on = on;
	this.draggable = true;
	this.state = views._Component.State.NONE;
	this.parent = null;
	this.position = { x : 0., y : 0.};
	this.size = { x : 0., y : 0.};
	this.previousCursor = null;
	this.defaultCursor = views.MouseCursorKind.DEFAULT;
	this.resizeBox = null;
	this.initialize();
}
views.Component.__name__ = ["views","Component"];
views.Component.prototype.id = null;
views.Component.prototype.renderer = null;
views.Component.prototype.factory = null;
views.Component.prototype.workspace = null;
views.Component.prototype.on = null;
views.Component.prototype.position = null;
views.Component.prototype.size = null;
views.Component.prototype.parent = null;
views.Component.prototype.defaultCursor = null;
views.Component.prototype.selected = null;
views.Component.prototype.draggable = null;
views.Component.prototype.state = null;
views.Component.prototype.previousCursor = null;
views.Component.prototype.resizeBox = null;
views.Component.prototype.set_workspace = function(value) {
	this.workspace = value;
	return value;
}
views.Component.prototype.initialize = function() {
	this.bindEvents();
}
views.Component.prototype.bindEvents = function() {
	var me = this;
	var pressed = false;
	var lastClickTime = 0.;
	this.renderer.bind(views.EventKind.PRESS,function(e) {
		var clickTime = Date.now().getTime();
		me.state = views._Component.State.PRESSED({ x : e.position.x - me.position.x, y : e.position.y - me.position.y});
		if(clickTime - lastClickTime < 300) me.on.doubleclick.call(me,e); else me.on.click.call(me,e);
		lastClickTime = clickTime;
		me.renderer.captureMouse();
	});
	this.renderer.bind(views.EventKind.MOUSEMOVE,function(e) {
		var _renderer = (function($this) {
			var $r;
			var $t = me.renderer;
			if(Std["is"]($t,views.ComponentRenderer)) $t; else throw "Class cast error";
			$r = $t;
			return $r;
		}(this));
		if(me.previousCursor == null) {
			me.previousCursor = _renderer.get_stage().cursor;
			_renderer.get_stage().set_cursor(me.defaultCursor);
		}
		var $e = (me.state);
		switch( $e[1] ) {
		case 1:
			var pof = $e[2];
			if(me.draggable) {
				me.state = views._Component.State.DRAGGING(pof);
				me.position = { x : e.position.x - pof.x, y : e.position.y - pof.y};
				_renderer.opacity = .5;
				me.on.dragstart.call(me,e);
				me.refresh();
			}
			break;
		case 2:
			var pof = $e[2];
			me.position = { x : e.position.x - pof.x, y : e.position.y - pof.y};
			me.refresh();
			me.on.drag.call(me,e);
			break;
		default:
		}
	});
	this.renderer.bind(views.EventKind.MOUSEOUT,function(e) {
		if(me.previousCursor != null) {
			((function($this) {
				var $r;
				var $t = me.renderer;
				if(Std["is"]($t,views.ComponentRenderer)) $t; else throw "Class cast error";
				$r = $t;
				return $r;
			}(this))).get_stage().set_cursor(me.previousCursor);
			me.previousCursor = null;
		}
	});
	this.renderer.bind(views.EventKind.RELEASE,function(e) {
		me.renderer.releaseMouse();
		switch( (me.state)[1] ) {
		case 2:
			((function($this) {
				var $r;
				var $t = me.renderer;
				if(Std["is"]($t,views.ComponentRenderer)) $t; else throw "Class cast error";
				$r = $t;
				return $r;
			}(this))).opacity = 1.;
			me.on.dragend.call(me,e);
			me.refresh();
			break;
		default:
		}
		me.state = views._Component.State.NONE;
	});
}
views.Component.prototype.select = function() {
	this.workspace.addToSelection(this,this);
}
views.Component.prototype.unselect = function() {
	this.workspace.removeFromSelection(this,this);
}
views.Component.prototype.hideResizeBox = function() {
	if(this.resizeBox == null) return;
	this.factory.stage.remove(this.resizeBox);
	this.resizeBox.dispose();
	this.resizeBox = null;
}
views.Component.prototype.putResizeBox = function() {
	var me = this;
	if(this.resizeBox != null) return;
	var resizeBox = this.factory.rendererFactory.create(Type.getClass(this),{ variant : "resize_box"});
	this.factory.stage.add(resizeBox);
	resizeBox.bind(views.EventKind.PRESS,function(e) {
		var startPosition = e.position;
		var initialPosition = me.position;
		var initialSize = me.size;
		if(e.extra == null) {
			me.renderer.trigger(views.EventKind.PRESS,e);
			resizeBox.bind(views.EventKind.RELEASE,function(e1) {
				me.renderer.trigger(views.EventKind.RELEASE,e1);
			});
		} else {
			var corner = (function($this) {
				var $r;
				var $t = e.extra;
				if(Std["is"]($t,Direction)) $t; else throw "Class cast error";
				$r = $t;
				return $r;
			}(this));
			resizeBox.bind(views.EventKind.MOUSEMOVE,function(e1) {
				switch( (corner)[1] ) {
				case 4:
					me.position = { x : initialPosition.x + (e1.position.x - startPosition.x), y : initialPosition.y + (e1.position.y - startPosition.y)};
					me.size = { x : initialSize.x - (e1.position.x - startPosition.x), y : initialSize.y - (e1.position.y - startPosition.y)};
					break;
				case 5:
					me.position = { x : initialPosition.x, y : initialPosition.y + (e1.position.y - startPosition.y)};
					me.size = { x : initialSize.x + (e1.position.x - startPosition.x), y : initialSize.y - (e1.position.y - startPosition.y)};
					break;
				case 6:
					me.position = { x : initialPosition.x + (e1.position.x - startPosition.x), y : initialPosition.y};
					me.size = { x : initialSize.x - (e1.position.x - startPosition.x), y : initialSize.y + (e1.position.y - startPosition.y)};
					break;
				case 7:
					me.size = { x : initialSize.x + (e1.position.x - startPosition.x), y : initialSize.y + (e1.position.y - startPosition.y)};
					break;
				default:
				}
				resizeBox.realize(me);
				me.renderer.realize(me);
			});
			resizeBox.bind(views.EventKind.RELEASE,function(e1) {
				resizeBox.releaseMouse();
				resizeBox.bind(views.EventKind.MOUSEMOVE,null);
				resizeBox.bind(views.EventKind.RELEASE,null);
			});
			resizeBox.captureMouse();
		}
	});
	resizeBox.realize(this);
	this.resizeBox = resizeBox;
}
views.Component.prototype.addedToSelection = function(cause) {
	this.selected = true;
	this.refresh();
	this.on.focused.call(this,{ source : this, cause : cause});
}
views.Component.prototype.removedFromSelection = function(cause) {
	this.selected = false;
	this.refresh();
	this.on.blur.call(this,{ source : this, cause : cause});
}
views.Component.prototype.refresh = function() {
	this.renderer.realize(this);
}
views.Component.prototype.__class__ = views.Component;
views.Component.__interfaces__ = [Identifiable];
views.HorizontalGuide = function(factory,id,renderer) {
	if( factory === $_ ) return;
	views.Component.call(this,factory,id,renderer);
}
views.HorizontalGuide.__name__ = ["views","HorizontalGuide"];
views.HorizontalGuide.__super__ = views.Component;
for(var k in views.Component.prototype ) views.HorizontalGuide.prototype[k] = views.Component.prototype[k];
views.HorizontalGuide.prototype.initialize = function() {
	views.Component.prototype.initialize.call(this);
	this.defaultCursor = views.MouseCursorKind.CROSSHAIR;
}
views.HorizontalGuide.prototype.__class__ = views.HorizontalGuide;
views.rendering.js.dom.HorizontalGuideRenderer = function(id,view) {
	if( id === $_ ) return;
	views.rendering.js.dom.JSDOMComponentRenderer.call(this,id,view);
}
views.rendering.js.dom.HorizontalGuideRenderer.__name__ = ["views","rendering","js","dom","HorizontalGuideRenderer"];
views.rendering.js.dom.HorizontalGuideRenderer.__super__ = views.rendering.js.dom.JSDOMComponentRenderer;
for(var k in views.rendering.js.dom.JSDOMComponentRenderer.prototype ) views.rendering.js.dom.HorizontalGuideRenderer.prototype[k] = views.rendering.js.dom.JSDOMComponentRenderer.prototype[k];
views.rendering.js.dom.HorizontalGuideRenderer.prototype.offset = null;
views.rendering.js.dom.HorizontalGuideRenderer.prototype.setup = function() {
	return new js.JQuery("<div class=\"component-horizontal_guide\"></div>");
}
views.rendering.js.dom.HorizontalGuideRenderer.prototype.realize = function(component) {
	this.offset = component.position.y;
	this.view_.scheduleRefresh(this);
}
views.rendering.js.dom.HorizontalGuideRenderer.prototype.refresh = function() {
	this.n.css({ left : "0px", top : Std.string(this.view_.inchToPixel(this.offset)) + "px", width : "100%", height : "0px", borderWidth : "1px"});
	views.rendering.js.dom.JSDOMComponentRenderer.prototype.refresh.call(this);
}
views.rendering.js.dom.HorizontalGuideRenderer.prototype.__class__ = views.rendering.js.dom.HorizontalGuideRenderer;
if(!views._Ruler) views._Ruler = {}
views._Ruler.State = { __ename__ : ["views","_Ruler","State"], __constructs__ : ["NONE","PRESSED","DRAGGING"] }
views._Ruler.State.NONE = ["NONE",0];
views._Ruler.State.NONE.toString = $estr;
views._Ruler.State.NONE.__enum__ = views._Ruler.State;
views._Ruler.State.PRESSED = function(position) { var $x = ["PRESSED",1,position]; $x.__enum__ = views._Ruler.State; $x.toString = $estr; return $x; }
views._Ruler.State.DRAGGING = function(pof) { var $x = ["DRAGGING",2,pof]; $x.__enum__ = views._Ruler.State; $x.toString = $estr; return $x; }
views.Ruler = function(renderer) {
	if( renderer === $_ ) return;
	this.renderer = renderer;
	this.unit = UnitKind.MILLIMETER;
	this.minimumGraduationWidthInPixel = 4;
	this.graduations = [1.,5.,10.,25.,50.,100.,250.,500.,1000.];
	var events = ["click","dragstart","drag","dragend"];
	this.on = { };
	var _g = 0;
	while(_g < events.length) {
		var event_kind = events[_g];
		++_g;
		this.on[event_kind] = new EventListeners();
	}
	this.state = views._Ruler.State.NONE;
	this.bindEvents();
}
views.Ruler.__name__ = ["views","Ruler"];
views.Ruler.prototype.renderer = null;
views.Ruler.prototype.on = null;
views.Ruler.prototype.offset = null;
views.Ruler.prototype.unit = null;
views.Ruler.prototype.minimumGraduationWidthInPixel = null;
views.Ruler.prototype.graduations = null;
views.Ruler.prototype.state = null;
views.Ruler.prototype.refresh = function() {
	this.renderer.realize(this);
}
views.Ruler.prototype.bindEvents = function() {
	var me = this;
	var pressed = false;
	this.renderer.bind(views.EventKind.PRESS,function(e) {
		me.state = views._Ruler.State.PRESSED({ x : e.position.x, y : e.position.y});
	});
	this.renderer.bind(views.EventKind.MOUSEMOVE,function(e) {
		var $e = (me.state);
		switch( $e[1] ) {
		case 1:
			var pof = $e[2];
			me.state = views._Ruler.State.DRAGGING(pof);
			me.renderer.captureMouse();
			me.on.dragstart.call(me,e);
			break;
		case 2:
			var pof = $e[2];
			me.on.drag.call(me,e);
			break;
		default:
		}
	});
	this.renderer.bind(views.EventKind.RELEASE,function(e) {
		switch( (me.state)[1] ) {
		case 1:
			me.on.click.call(me,e);
			break;
		case 2:
			me.renderer.releaseMouse();
			me.on.dragend.call(me,e);
			break;
		default:
		}
		me.state = views._Ruler.State.NONE;
	});
}
views.Ruler.prototype.__class__ = views.Ruler;
Throwable = function() { }
Throwable.__name__ = ["Throwable"];
Throwable.prototype.message = null;
Throwable.prototype.cause = null;
Throwable.prototype.toString = null;
Throwable.prototype.__class__ = Throwable;
views.rendering.js.dom.RulerRenderer = function(id,view) {
	if( id === $_ ) return;
	views.rendering.js.dom.JSDOMRenderer.call(this,id,view);
}
views.rendering.js.dom.RulerRenderer.__name__ = ["views","rendering","js","dom","RulerRenderer"];
views.rendering.js.dom.RulerRenderer.__super__ = views.rendering.js.dom.JSDOMRenderer;
for(var k in views.rendering.js.dom.JSDOMRenderer.prototype ) views.rendering.js.dom.RulerRenderer.prototype[k] = views.rendering.js.dom.JSDOMRenderer.prototype[k];
views.rendering.js.dom.RulerRenderer.prototype.offset = null;
views.rendering.js.dom.RulerRenderer.prototype.unit = null;
views.rendering.js.dom.RulerRenderer.prototype.minimumGraduationWidthInPixel = null;
views.rendering.js.dom.RulerRenderer.prototype.graduations = null;
views.rendering.js.dom.RulerRenderer.prototype.realize = function(ruler) {
	ruler = (function($this) {
		var $r;
		var $t = ruler;
		if(Std["is"]($t,views.Ruler)) $t; else throw "Class cast error";
		$r = $t;
		return $r;
	}(this));
	this.offset = ruler.offset;
	this.unit = ruler.unit;
	this.minimumGraduationWidthInPixel = ruler.minimumGraduationWidthInPixel;
	this.graduations = ruler.graduations;
	this.view_.scheduleRefresh(this);
}
views.rendering.js.dom.RulerRenderer.prototype.getMinimumGraduation = function() {
	var _g1 = 0, _g = this.graduations.length;
	while(_g1 < _g) {
		var i = _g1++;
		if(this.view_.inchToPixel(UnitUtils.anyToInch(this.unit,this.graduations[i])) >= this.minimumGraduationWidthInPixel) return i;
	}
	return this.graduations.length - 1;
}
views.rendering.js.dom.RulerRenderer.prototype.createMouseEvent = function(e,extra) {
	return { source : this, cause : e, position : this.view_.pixelToInchP({ x : e.pageX - this.view_.stage_.screenOffset.x, y : e.pageY - this.view_.stage_.screenOffset.y}), screenPosition : { x : 0. + e.pageX, y : 0. + e.pageY}, left : (e.which & 1) != 0, middle : (e.which & 2) != 0, right : (e.which & 3) != 0, extra : extra};
}
views.rendering.js.dom.RulerRenderer.prototype.__class__ = views.rendering.js.dom.RulerRenderer;
views.rendering.js.dom.HorizontalRulerRenderer = function(id,view) {
	if( id === $_ ) return;
	views.rendering.js.dom.RulerRenderer.call(this,id,view);
}
views.rendering.js.dom.HorizontalRulerRenderer.__name__ = ["views","rendering","js","dom","HorizontalRulerRenderer"];
views.rendering.js.dom.HorizontalRulerRenderer.__super__ = views.rendering.js.dom.RulerRenderer;
for(var k in views.rendering.js.dom.RulerRenderer.prototype ) views.rendering.js.dom.HorizontalRulerRenderer.prototype[k] = views.rendering.js.dom.RulerRenderer.prototype[k];
views.rendering.js.dom.HorizontalRulerRenderer.prototype.setup = function() {
	return new js.JQuery("<div class=\"renderable-horizontal_ruler\" style=\"height:20px; line-height:20px;\"><canvas height=\"20\"></canvas></div>");
}
views.rendering.js.dom.HorizontalRulerRenderer.prototype.refresh = function() {
	var interval = this.graduations[0];
	var canvas = this.n[0].firstChild;
	canvas.width = this.n.innerWidth();
	var ctx = canvas.getContext("2d");
	ctx.clearRect(0,0,canvas.width,canvas.height);
	var offsetInUnit = UnitUtils.inchToAny(this.unit,this.offset);
	var minimumGraduation = this.getMinimumGraduation();
	var minimumGraduationWidth = this.graduations[minimumGraduation];
	var i = minimumGraduationWidth + Math.floor(offsetInUnit / minimumGraduationWidth) * minimumGraduationWidth;
	while(true) {
		var x = this.view_.inchToPixel(UnitUtils.anyToInch(this.unit,i - offsetInUnit));
		if(Std["int"](x) >= canvas.width) break;
		ctx.strokeRect(0,0,canvas.width,canvas.height);
		if(Math.floor(i / minimumGraduationWidth) % 10 == 0) {
			ctx.beginPath();
			ctx.moveTo(x,0);
			ctx.lineTo(x,20);
			ctx.stroke();
			ctx.fillText(Std.string(Std["int"](i)),x + 2,10);
		} else {
			ctx.beginPath();
			ctx.moveTo(x,14);
			ctx.lineTo(x,20);
			ctx.stroke();
		}
		i += minimumGraduationWidth;
	}
}
views.rendering.js.dom.HorizontalRulerRenderer.prototype.__class__ = views.rendering.js.dom.HorizontalRulerRenderer;
UnitKind = { __ename__ : ["UnitKind"], __constructs__ : ["INCH","POINT","PICA","MILLIMETER","CENTIMETER","METER","PIXEL"] }
UnitKind.INCH = ["INCH",0];
UnitKind.INCH.toString = $estr;
UnitKind.INCH.__enum__ = UnitKind;
UnitKind.POINT = ["POINT",1];
UnitKind.POINT.toString = $estr;
UnitKind.POINT.__enum__ = UnitKind;
UnitKind.PICA = ["PICA",2];
UnitKind.PICA.toString = $estr;
UnitKind.PICA.__enum__ = UnitKind;
UnitKind.MILLIMETER = ["MILLIMETER",3];
UnitKind.MILLIMETER.toString = $estr;
UnitKind.MILLIMETER.__enum__ = UnitKind;
UnitKind.CENTIMETER = ["CENTIMETER",4];
UnitKind.CENTIMETER.toString = $estr;
UnitKind.CENTIMETER.__enum__ = UnitKind;
UnitKind.METER = ["METER",5];
UnitKind.METER.toString = $estr;
UnitKind.METER.__enum__ = UnitKind;
UnitKind.PIXEL = ["PIXEL",6];
UnitKind.PIXEL.toString = $estr;
UnitKind.PIXEL.__enum__ = UnitKind;
views.VerticalGuide = function(factory,id,renderer) {
	if( factory === $_ ) return;
	views.Component.call(this,factory,id,renderer);
}
views.VerticalGuide.__name__ = ["views","VerticalGuide"];
views.VerticalGuide.__super__ = views.Component;
for(var k in views.Component.prototype ) views.VerticalGuide.prototype[k] = views.Component.prototype[k];
views.VerticalGuide.prototype.initialize = function() {
	views.Component.prototype.initialize.call(this);
	this.defaultCursor = views.MouseCursorKind.CROSSHAIR;
}
views.VerticalGuide.prototype.__class__ = views.VerticalGuide;
Reflect = function() { }
Reflect.__name__ = ["Reflect"];
Reflect.hasField = function(o,field) {
	if(o.hasOwnProperty != null) return o.hasOwnProperty(field);
	var arr = Reflect.fields(o);
	var $it0 = arr.iterator();
	while( $it0.hasNext() ) {
		var t = $it0.next();
		if(t == field) return true;
	}
	return false;
}
Reflect.field = function(o,field) {
	var v = null;
	try {
		v = o[field];
	} catch( e ) {
	}
	return v;
}
Reflect.setField = function(o,field,value) {
	o[field] = value;
}
Reflect.callMethod = function(o,func,args) {
	return func.apply(o,args);
}
Reflect.fields = function(o) {
	if(o == null) return new Array();
	var a = new Array();
	if(o.hasOwnProperty) {
		for(var i in o) if( o.hasOwnProperty(i) ) a.push(i);
	} else {
		var t;
		try {
			t = o.__proto__;
		} catch( e ) {
			t = null;
		}
		if(t != null) o.__proto__ = null;
		for(var i in o) if( i != "__proto__" ) a.push(i);
		if(t != null) o.__proto__ = t;
	}
	return a;
}
Reflect.isFunction = function(f) {
	return typeof(f) == "function" && f.__name__ == null;
}
Reflect.compare = function(a,b) {
	return a == b?0:a > b?1:-1;
}
Reflect.compareMethods = function(f1,f2) {
	if(f1 == f2) return true;
	if(!Reflect.isFunction(f1) || !Reflect.isFunction(f2)) return false;
	return f1.scope == f2.scope && f1.method == f2.method && f1.method != null;
}
Reflect.isObject = function(v) {
	if(v == null) return false;
	var t = typeof(v);
	return t == "string" || t == "object" && !v.__enum__ || t == "function" && v.__name__ != null;
}
Reflect.deleteField = function(o,f) {
	if(!Reflect.hasField(o,f)) return false;
	delete(o[f]);
	return true;
}
Reflect.copy = function(o) {
	var o2 = { };
	var _g = 0, _g1 = Reflect.fields(o);
	while(_g < _g1.length) {
		var f = _g1[_g];
		++_g;
		o2[f] = Reflect.field(o,f);
	}
	return o2;
}
Reflect.makeVarArgs = function(f) {
	return function() {
		var a = new Array();
		var _g1 = 0, _g = arguments.length;
		while(_g1 < _g) {
			var i = _g1++;
			a.push(arguments[i]);
		}
		return f(a);
	};
}
Reflect.prototype.__class__ = Reflect;
views.Viewport = function() { }
views.Viewport.__name__ = ["views","Viewport"];
views.Viewport.prototype.view = null;
views.Viewport.prototype.on = null;
views.Viewport.prototype.scrollPosition = null;
views.Viewport.prototype.size = null;
views.Viewport.prototype.screenOffset = null;
views.Viewport.prototype.__class__ = views.Viewport;
views.Viewport.__interfaces__ = [Disposable];
views.rendering.js.dom.JSDOMViewport = function(view) {
	if( view === $_ ) return;
	var me = this;
	this.view_ = view;
	this.on = { scroll : new EventListeners()};
	this.set_n(null);
	this.onScroll = function(e) {
		me.refresh();
		me.on.scroll.call(me,{ source : me, cause : null, position : me.get_scrollPosition()});
	};
	this.screenOffset = null;
}
views.rendering.js.dom.JSDOMViewport.__name__ = ["views","rendering","js","dom","JSDOMViewport"];
views.rendering.js.dom.JSDOMViewport.prototype.view = null;
views.rendering.js.dom.JSDOMViewport.prototype.on = null;
views.rendering.js.dom.JSDOMViewport.prototype.scrollPosition = null;
views.rendering.js.dom.JSDOMViewport.prototype.size = null;
views.rendering.js.dom.JSDOMViewport.prototype.n = null;
views.rendering.js.dom.JSDOMViewport.prototype.screenOffset = null;
views.rendering.js.dom.JSDOMViewport.prototype.view_ = null;
views.rendering.js.dom.JSDOMViewport.prototype.onScroll = null;
views.rendering.js.dom.JSDOMViewport.prototype.set_n = function(value) {
	if(this.n != null) this.n.unbind("scroll",this.onScroll);
	this.n = value;
	if(this.n != null) {
		this.refresh();
		this.n.bind("scroll",this.onScroll);
		var tmp = this.n.offset();
		this.screenOffset = { x : 0. + tmp.left, y : 0. + tmp.top};
	}
	return value;
}
views.rendering.js.dom.JSDOMViewport.prototype.get_view = function() {
	return this.view_;
}
views.rendering.js.dom.JSDOMViewport.prototype.get_scrollPosition = function() {
	return this.scrollPosition;
}
views.rendering.js.dom.JSDOMViewport.prototype.set_scrollPosition = function(value) {
	this.scrollPosition = value;
	var positionInPixel = this.view_.inchToPixelP(value);
	this.n[0].scrollLeft = positionInPixel.x;
	this.n[0].scrollTop = positionInPixel.y;
	return value;
}
views.rendering.js.dom.JSDOMViewport.prototype.get_size = function() {
	return { x : 0. + this.n.innerWidth(), y : 0. + this.n.innerHeight()};
}
views.rendering.js.dom.JSDOMViewport.prototype.refresh = function() {
	if(this.view_.get_stage() != null) ((function($this) {
		var $r;
		var $t = $this.view_.get_stage();
		if(Std["is"]($t,views.rendering.js.dom.JSDOMStage)) $t; else throw "Class cast error";
		$r = $t;
		return $r;
	}(this))).recalculateBasePageOffset();
	this.set_scrollPosition(this.view_.pixelToInchP({ x : 0. + this.n[0].scrollLeft, y : 0. + this.n[0].scrollTop}));
}
views.rendering.js.dom.JSDOMViewport.prototype.dispose = function() {
	if(this.n != null) this.n.unbind("scroll",this.onScroll);
}
views.rendering.js.dom.JSDOMViewport.prototype.__class__ = views.rendering.js.dom.JSDOMViewport;
views.rendering.js.dom.JSDOMViewport.__interfaces__ = [views.Viewport];
views.Renderable = function() { }
views.Renderable.__name__ = ["views","Renderable"];
views.Renderable.prototype.renderer = null;
views.Renderable.prototype.refresh = null;
views.Renderable.prototype.__class__ = views.Renderable;
Command = function() { }
Command.__name__ = ["Command"];
Command.prototype.data = null;
Command.prototype.get_data = null;
Command.prototype.do_ = null;
Command.prototype.undo = null;
Command.prototype.__class__ = Command;
IntIter = function(min,max) {
	if( min === $_ ) return;
	this.min = min;
	this.max = max;
}
IntIter.__name__ = ["IntIter"];
IntIter.prototype.min = null;
IntIter.prototype.max = null;
IntIter.prototype.hasNext = function() {
	return this.min < this.max;
}
IntIter.prototype.next = function() {
	return this.min++;
}
IntIter.prototype.__class__ = IntIter;
Direction = { __ename__ : ["Direction"], __constructs__ : ["NORTH","SOUTH","WEST","EAST","NORTH_WEST","NORTH_EAST","SOUTH_WEST","SOUTH_EAST"] }
Direction.NORTH = ["NORTH",0];
Direction.NORTH.toString = $estr;
Direction.NORTH.__enum__ = Direction;
Direction.SOUTH = ["SOUTH",1];
Direction.SOUTH.toString = $estr;
Direction.SOUTH.__enum__ = Direction;
Direction.WEST = ["WEST",2];
Direction.WEST.toString = $estr;
Direction.WEST.__enum__ = Direction;
Direction.EAST = ["EAST",3];
Direction.EAST.toString = $estr;
Direction.EAST.__enum__ = Direction;
Direction.NORTH_WEST = ["NORTH_WEST",4];
Direction.NORTH_WEST.toString = $estr;
Direction.NORTH_WEST.__enum__ = Direction;
Direction.NORTH_EAST = ["NORTH_EAST",5];
Direction.NORTH_EAST.toString = $estr;
Direction.NORTH_EAST.__enum__ = Direction;
Direction.SOUTH_WEST = ["SOUTH_WEST",6];
Direction.SOUTH_WEST.toString = $estr;
Direction.SOUTH_WEST.__enum__ = Direction;
Direction.SOUTH_EAST = ["SOUTH_EAST",7];
Direction.SOUTH_EAST.toString = $estr;
Direction.SOUTH_EAST.__enum__ = Direction;
views.rendering.js.dom.ResizeBoxRenderer = function(id,view) {
	if( id === $_ ) return;
	views.rendering.js.dom.JSDOMComponentRenderer.call(this,id,view);
}
views.rendering.js.dom.ResizeBoxRenderer.__name__ = ["views","rendering","js","dom","ResizeBoxRenderer"];
views.rendering.js.dom.ResizeBoxRenderer.__super__ = views.rendering.js.dom.JSDOMComponentRenderer;
for(var k in views.rendering.js.dom.JSDOMComponentRenderer.prototype ) views.rendering.js.dom.ResizeBoxRenderer.prototype[k] = views.rendering.js.dom.JSDOMComponentRenderer.prototype[k];
views.rendering.js.dom.ResizeBoxRenderer.prototype.position = null;
views.rendering.js.dom.ResizeBoxRenderer.prototype.size = null;
views.rendering.js.dom.ResizeBoxRenderer.prototype.cornerHandlers = null;
views.rendering.js.dom.ResizeBoxRenderer.prototype.bind = function(eventKind,handler) {
	var existingHandler = this.handlers[eventKind[1]];
	if(existingHandler == null) {
		if(handler != null) {
			this.view_.mouseEventsHandlerManager.bindEvent(this.mouseEventsHandler,eventKind);
			var _g = 0, _g1 = views.rendering.js.dom.ResizeBoxRenderer.corners;
			while(_g < _g1.length) {
				var pair = _g1[_g];
				++_g;
				this.view_.mouseEventsHandlerManager.bindEvent(this.cornerHandlers[pair[1][1]],eventKind);
			}
		}
	} else if(handler == null) {
		this.view_.mouseEventsHandlerManager.unbindEvent(this.mouseEventsHandler,eventKind);
		var _g = 0, _g1 = views.rendering.js.dom.ResizeBoxRenderer.corners;
		while(_g < _g1.length) {
			var pair = _g1[_g];
			++_g;
			this.view_.mouseEventsHandlerManager.unbindEvent(this.cornerHandlers[pair[1][1]],eventKind);
		}
	}
	this.handlers[eventKind[1]] = handler;
}
views.rendering.js.dom.ResizeBoxRenderer.prototype.registerMouseEventsHandler = function() {
	var me = this;
	views.rendering.js.dom.JSDOMComponentRenderer.prototype.registerMouseEventsHandler.call(this);
	var _g = 0, _g1 = views.rendering.js.dom.ResizeBoxRenderer.corners;
	while(_g < _g1.length) {
		var pair = _g1[_g];
		++_g;
		(function(part,partEnum) {
			me.cornerHandlers[partEnum[1]] = me.view_.mouseEventsHandlerManager.registerHandler(new views.rendering.js.dom.MouseEventsHandler(me.n.find(part),function(e) {
				var handlerFunction = me.handlers[views.EventKind.PRESS[1]];
				if(handlerFunction != null) handlerFunction(me.createMouseEvent(e,partEnum));
			},function(e) {
				var handlerFunction = me.handlers[views.EventKind.RELEASE[1]];
				if(handlerFunction != null) handlerFunction(me.createMouseEvent(e,partEnum));
			},function(e) {
				var handlerFunction = me.handlers[views.EventKind.MOUSEMOVE[1]];
				if(handlerFunction != null) handlerFunction(me.createMouseEvent(e,partEnum));
			},function(e) {
				var handlerFunction = me.handlers[views.EventKind.MOUSEOUT[1]];
				if(handlerFunction != null) handlerFunction(me.createMouseEvent(e,partEnum));
			}));
		})(pair[0],pair[1]);
	}
}
views.rendering.js.dom.ResizeBoxRenderer.prototype.setup = function() {
	var n = new js.JQuery("<div class=\"component-resize_box\"><div class=\"corner nw\"></div><div class=\"corner ne\"></div><div class=\"corner sw\"></div><div class=\"corner se\"></div></div>");
	this.cornerHandlers = new Array();
	return n;
}
views.rendering.js.dom.ResizeBoxRenderer.prototype.realize = function(component) {
	this.position = component.position;
	this.size = component.size;
	this.view_.scheduleRefresh(this);
}
views.rendering.js.dom.ResizeBoxRenderer.prototype.refresh = function() {
	var position = this.view_.inchToPixelP(this.position);
	var size = this.view_.inchToPixelP(this.size);
	this.n.css({ left : Std.string(position.x) + "px", top : Std.string(position.y) + "px", width : Std.string(size.x) + "px", height : Std.string(size.y) + "px"});
	views.rendering.js.dom.JSDOMComponentRenderer.prototype.refresh.call(this);
}
views.rendering.js.dom.ResizeBoxRenderer.prototype.__class__ = views.rendering.js.dom.ResizeBoxRenderer;
ValueType = { __ename__ : ["ValueType"], __constructs__ : ["TNull","TInt","TFloat","TBool","TObject","TFunction","TClass","TEnum","TUnknown"] }
ValueType.TNull = ["TNull",0];
ValueType.TNull.toString = $estr;
ValueType.TNull.__enum__ = ValueType;
ValueType.TInt = ["TInt",1];
ValueType.TInt.toString = $estr;
ValueType.TInt.__enum__ = ValueType;
ValueType.TFloat = ["TFloat",2];
ValueType.TFloat.toString = $estr;
ValueType.TFloat.__enum__ = ValueType;
ValueType.TBool = ["TBool",3];
ValueType.TBool.toString = $estr;
ValueType.TBool.__enum__ = ValueType;
ValueType.TObject = ["TObject",4];
ValueType.TObject.toString = $estr;
ValueType.TObject.__enum__ = ValueType;
ValueType.TFunction = ["TFunction",5];
ValueType.TFunction.toString = $estr;
ValueType.TFunction.__enum__ = ValueType;
ValueType.TClass = function(c) { var $x = ["TClass",6,c]; $x.__enum__ = ValueType; $x.toString = $estr; return $x; }
ValueType.TEnum = function(e) { var $x = ["TEnum",7,e]; $x.__enum__ = ValueType; $x.toString = $estr; return $x; }
ValueType.TUnknown = ["TUnknown",8];
ValueType.TUnknown.toString = $estr;
ValueType.TUnknown.__enum__ = ValueType;
Type = function() { }
Type.__name__ = ["Type"];
Type.getClass = function(o) {
	if(o == null) return null;
	if(o.__enum__ != null) return null;
	return o.__class__;
}
Type.getEnum = function(o) {
	if(o == null) return null;
	return o.__enum__;
}
Type.getSuperClass = function(c) {
	return c.__super__;
}
Type.getClassName = function(c) {
	var a = c.__name__;
	return a.join(".");
}
Type.getEnumName = function(e) {
	var a = e.__ename__;
	return a.join(".");
}
Type.resolveClass = function(name) {
	var cl;
	try {
		cl = eval(name);
	} catch( e ) {
		cl = null;
	}
	if(cl == null || cl.__name__ == null) return null;
	return cl;
}
Type.resolveEnum = function(name) {
	var e;
	try {
		e = eval(name);
	} catch( err ) {
		e = null;
	}
	if(e == null || e.__ename__ == null) return null;
	return e;
}
Type.createInstance = function(cl,args) {
	if(args.length <= 3) return new cl(args[0],args[1],args[2]);
	if(args.length > 8) throw "Too many arguments";
	return new cl(args[0],args[1],args[2],args[3],args[4],args[5],args[6],args[7]);
}
Type.createEmptyInstance = function(cl) {
	return new cl($_);
}
Type.createEnum = function(e,constr,params) {
	var f = Reflect.field(e,constr);
	if(f == null) throw "No such constructor " + constr;
	if(Reflect.isFunction(f)) {
		if(params == null) throw "Constructor " + constr + " need parameters";
		return f.apply(e,params);
	}
	if(params != null && params.length != 0) throw "Constructor " + constr + " does not need parameters";
	return f;
}
Type.createEnumIndex = function(e,index,params) {
	var c = e.__constructs__[index];
	if(c == null) throw index + " is not a valid enum constructor index";
	return Type.createEnum(e,c,params);
}
Type.getInstanceFields = function(c) {
	var a = Reflect.fields(c.prototype);
	a.remove("__class__");
	return a;
}
Type.getClassFields = function(c) {
	var a = Reflect.fields(c);
	a.remove("__name__");
	a.remove("__interfaces__");
	a.remove("__super__");
	a.remove("prototype");
	return a;
}
Type.getEnumConstructs = function(e) {
	var a = e.__constructs__;
	return a.copy();
}
Type["typeof"] = function(v) {
	switch(typeof(v)) {
	case "boolean":
		return ValueType.TBool;
	case "string":
		return ValueType.TClass(String);
	case "number":
		if(Math.ceil(v) == v % 2147483648.0) return ValueType.TInt;
		return ValueType.TFloat;
	case "object":
		if(v == null) return ValueType.TNull;
		var e = v.__enum__;
		if(e != null) return ValueType.TEnum(e);
		var c = v.__class__;
		if(c != null) return ValueType.TClass(c);
		return ValueType.TObject;
	case "function":
		if(v.__name__ != null) return ValueType.TObject;
		return ValueType.TFunction;
	case "undefined":
		return ValueType.TNull;
	default:
		return ValueType.TUnknown;
	}
}
Type.enumEq = function(a,b) {
	if(a == b) return true;
	try {
		if(a[0] != b[0]) return false;
		var _g1 = 2, _g = a.length;
		while(_g1 < _g) {
			var i = _g1++;
			if(!Type.enumEq(a[i],b[i])) return false;
		}
		var e = a.__enum__;
		if(e != b.__enum__ || e == null) return false;
	} catch( e ) {
		return false;
	}
	return true;
}
Type.enumConstructor = function(e) {
	return e[0];
}
Type.enumParameters = function(e) {
	return e.slice(2);
}
Type.enumIndex = function(e) {
	return e[1];
}
Type.prototype.__class__ = Type;
views.MouseCursorKind = { __ename__ : ["views","MouseCursorKind"], __constructs__ : ["DEFAULT","POINTER","CROSSHAIR","MOVE"] }
views.MouseCursorKind.DEFAULT = ["DEFAULT",0];
views.MouseCursorKind.DEFAULT.toString = $estr;
views.MouseCursorKind.DEFAULT.__enum__ = views.MouseCursorKind;
views.MouseCursorKind.POINTER = ["POINTER",1];
views.MouseCursorKind.POINTER.toString = $estr;
views.MouseCursorKind.POINTER.__enum__ = views.MouseCursorKind;
views.MouseCursorKind.CROSSHAIR = ["CROSSHAIR",2];
views.MouseCursorKind.CROSSHAIR.toString = $estr;
views.MouseCursorKind.CROSSHAIR.__enum__ = views.MouseCursorKind;
views.MouseCursorKind.MOVE = ["MOVE",3];
views.MouseCursorKind.MOVE.toString = $estr;
views.MouseCursorKind.MOVE.__enum__ = views.MouseCursorKind;
if(typeof js=='undefined') js = {}
js.Boot = function() { }
js.Boot.__name__ = ["js","Boot"];
js.Boot.__unhtml = function(s) {
	return s.split("&").join("&amp;").split("<").join("&lt;").split(">").join("&gt;");
}
js.Boot.__trace = function(v,i) {
	var msg = i != null?i.fileName + ":" + i.lineNumber + ": ":"";
	msg += js.Boot.__unhtml(js.Boot.__string_rec(v,"")) + "<br/>";
	var d = document.getElementById("haxe:trace");
	if(d == null) alert("No haxe:trace element defined\n" + msg); else d.innerHTML += msg;
}
js.Boot.__clear_trace = function() {
	var d = document.getElementById("haxe:trace");
	if(d != null) d.innerHTML = "";
}
js.Boot.__closure = function(o,f) {
	var m = o[f];
	if(m == null) return null;
	var f1 = function() {
		return m.apply(o,arguments);
	};
	f1.scope = o;
	f1.method = m;
	return f1;
}
js.Boot.__string_rec = function(o,s) {
	if(o == null) return "null";
	if(s.length >= 5) return "<...>";
	var t = typeof(o);
	if(t == "function" && (o.__name__ != null || o.__ename__ != null)) t = "object";
	switch(t) {
	case "object":
		if(o instanceof Array) {
			if(o.__enum__ != null) {
				if(o.length == 2) return o[0];
				var str = o[0] + "(";
				s += "\t";
				var _g1 = 2, _g = o.length;
				while(_g1 < _g) {
					var i = _g1++;
					if(i != 2) str += "," + js.Boot.__string_rec(o[i],s); else str += js.Boot.__string_rec(o[i],s);
				}
				return str + ")";
			}
			var l = o.length;
			var i;
			var str = "[";
			s += "\t";
			var _g = 0;
			while(_g < l) {
				var i1 = _g++;
				str += (i1 > 0?",":"") + js.Boot.__string_rec(o[i1],s);
			}
			str += "]";
			return str;
		}
		var tostr;
		try {
			tostr = o.toString;
		} catch( e ) {
			return "???";
		}
		if(tostr != null && tostr != Object.toString) {
			var s2 = o.toString();
			if(s2 != "[object Object]") return s2;
		}
		var k = null;
		var str = "{\n";
		s += "\t";
		var hasp = o.hasOwnProperty != null;
		for( var k in o ) { ;
		if(hasp && !o.hasOwnProperty(k)) {
			continue;
		}
		if(k == "prototype" || k == "__class__" || k == "__super__" || k == "__interfaces__") {
			continue;
		}
		if(str.length != 2) str += ", \n";
		str += s + k + " : " + js.Boot.__string_rec(o[k],s);
		}
		s = s.substring(1);
		str += "\n" + s + "}";
		return str;
	case "function":
		return "<function>";
	case "string":
		return o;
	default:
		return String(o);
	}
}
js.Boot.__interfLoop = function(cc,cl) {
	if(cc == null) return false;
	if(cc == cl) return true;
	var intf = cc.__interfaces__;
	if(intf != null) {
		var _g1 = 0, _g = intf.length;
		while(_g1 < _g) {
			var i = _g1++;
			var i1 = intf[i];
			if(i1 == cl || js.Boot.__interfLoop(i1,cl)) return true;
		}
	}
	return js.Boot.__interfLoop(cc.__super__,cl);
}
js.Boot.__instanceof = function(o,cl) {
	try {
		if(o instanceof cl) {
			if(cl == Array) return o.__enum__ == null;
			return true;
		}
		if(js.Boot.__interfLoop(o.__class__,cl)) return true;
	} catch( e ) {
		if(cl == null) return false;
	}
	switch(cl) {
	case Int:
		return Math.ceil(o%2147483648.0) === o;
	case Float:
		return typeof(o) == "number";
	case Bool:
		return o === true || o === false;
	case String:
		return typeof(o) == "string";
	case Dynamic:
		return true;
	default:
		if(o == null) return false;
		return o.__enum__ == cl || cl == Class && o.__name__ != null || cl == Enum && o.__ename__ != null;
	}
}
js.Boot.__init = function() {
	js.Lib.isIE = typeof document!='undefined' && document.all != null && typeof window!='undefined' && window.opera == null;
	js.Lib.isOpera = typeof window!='undefined' && window.opera != null;
	Array.prototype.copy = Array.prototype.slice;
	Array.prototype.insert = function(i,x) {
		this.splice(i,0,x);
	};
	Array.prototype.remove = Array.prototype.indexOf?function(obj) {
		var idx = this.indexOf(obj);
		if(idx == -1) return false;
		this.splice(idx,1);
		return true;
	}:function(obj) {
		var i = 0;
		var l = this.length;
		while(i < l) {
			if(this[i] == obj) {
				this.splice(i,1);
				return true;
			}
			i++;
		}
		return false;
	};
	Array.prototype.iterator = function() {
		return { cur : 0, arr : this, hasNext : function() {
			return this.cur < this.arr.length;
		}, next : function() {
			return this.arr[this.cur++];
		}};
	};
	if(String.prototype.cca == null) String.prototype.cca = String.prototype.charCodeAt;
	String.prototype.charCodeAt = function(i) {
		var x = this.cca(i);
		if(x != x) return null;
		return x;
	};
	var oldsub = String.prototype.substr;
	String.prototype.substr = function(pos,len) {
		if(pos != null && pos != 0 && len != null && len < 0) return "";
		if(len == null) len = this.length;
		if(pos < 0) {
			pos = this.length + pos;
			if(pos < 0) pos = 0;
		} else if(len < 0) len = this.length + len - pos;
		return oldsub.apply(this,[pos,len]);
	};
	$closure = js.Boot.__closure;
}
js.Boot.prototype.__class__ = js.Boot;
views.ImageComponent = function(factory,id,renderer) {
	if( factory === $_ ) return;
	views.Component.call(this,factory,id,renderer);
}
views.ImageComponent.__name__ = ["views","ImageComponent"];
views.ImageComponent.__super__ = views.Component;
for(var k in views.Component.prototype ) views.ImageComponent.prototype[k] = views.Component.prototype[k];
views.ImageComponent.prototype.imageUrl = null;
views.ImageComponent.prototype.initialize = function() {
	views.Component.prototype.initialize.call(this);
	this.imageUrl = null;
	this.size = { x : 0.5, y : 0.5};
	this.defaultCursor = views.MouseCursorKind.POINTER;
}
views.ImageComponent.prototype.__class__ = views.ImageComponent;
IdentifiableSet = function(p) {
	if( p === $_ ) return;
	this.length = 0;
	this.items_ = new Hash();
}
IdentifiableSet.__name__ = ["IdentifiableSet"];
IdentifiableSet.prototype.length = null;
IdentifiableSet.prototype.items_ = null;
IdentifiableSet.prototype.iterator = function() {
	return this.items_.iterator();
}
IdentifiableSet.prototype.add = function(item) {
	var key = Std.string(item.id);
	if(!this.items_.exists(key)) {
		this.length++;
		this.items_.set(key,item);
		return true;
	} else return false;
}
IdentifiableSet.prototype.remove = function(item) {
	var key = Std.string(item.id);
	if(this.items_.exists(key)) {
		this.length--;
		this.items_.remove(Std.string(item.id));
		return true;
	} else return false;
}
IdentifiableSet.prototype.clear = function() {
	this.length = 0;
	this.items_ = new Hash();
}
IdentifiableSet.prototype.__class__ = IdentifiableSet;
views.rendering.js.dom.VerticalGuideRenderer = function(id,view) {
	if( id === $_ ) return;
	views.rendering.js.dom.JSDOMComponentRenderer.call(this,id,view);
}
views.rendering.js.dom.VerticalGuideRenderer.__name__ = ["views","rendering","js","dom","VerticalGuideRenderer"];
views.rendering.js.dom.VerticalGuideRenderer.__super__ = views.rendering.js.dom.JSDOMComponentRenderer;
for(var k in views.rendering.js.dom.JSDOMComponentRenderer.prototype ) views.rendering.js.dom.VerticalGuideRenderer.prototype[k] = views.rendering.js.dom.JSDOMComponentRenderer.prototype[k];
views.rendering.js.dom.VerticalGuideRenderer.prototype.offset = null;
views.rendering.js.dom.VerticalGuideRenderer.prototype.setup = function() {
	return new js.JQuery("<div class=\"component-vertical_guide\"></div>");
}
views.rendering.js.dom.VerticalGuideRenderer.prototype.realize = function(component) {
	this.offset = component.position.x;
	this.view_.scheduleRefresh(this);
}
views.rendering.js.dom.VerticalGuideRenderer.prototype.refresh = function() {
	this.n.css({ left : Std.string(this.view_.inchToPixel(this.offset)) + "px", top : "0px", width : "0px", height : "100%", borderWidth : "1px"});
	views.rendering.js.dom.JSDOMComponentRenderer.prototype.refresh.call(this);
}
views.rendering.js.dom.VerticalGuideRenderer.prototype.__class__ = views.rendering.js.dom.VerticalGuideRenderer;
views.rendering.js.Selection = function() { }
views.rendering.js.Selection.__name__ = ["views","rendering","js","Selection"];
views.rendering.js.Selection.prototype.anchorNode = null;
views.rendering.js.Selection.prototype.anchorOffset = null;
views.rendering.js.Selection.prototype.focusNode = null;
views.rendering.js.Selection.prototype.focusOffset = null;
views.rendering.js.Selection.prototype.isCollapsed = null;
views.rendering.js.Selection.prototype.rangeCount = null;
views.rendering.js.Selection.prototype.collapse = null;
views.rendering.js.Selection.prototype.collapseToStart = null;
views.rendering.js.Selection.prototype.collapseToEnd = null;
views.rendering.js.Selection.prototype.selectAllChildren = null;
views.rendering.js.Selection.prototype.deleteFromDocument = null;
views.rendering.js.Selection.prototype.getRangeAt = null;
views.rendering.js.Selection.prototype.addRange = null;
views.rendering.js.Selection.prototype.removeRange = null;
views.rendering.js.Selection.prototype.removeAllRanges = null;
views.rendering.js.Selection.prototype.stringifier = null;
views.rendering.js.Selection.prototype.__class__ = views.rendering.js.Selection;
views.rendering.js.MessagePortArray = function() { }
views.rendering.js.MessagePortArray.__name__ = ["views","rendering","js","MessagePortArray"];
views.rendering.js.MessagePortArray.prototype.__class__ = views.rendering.js.MessagePortArray;
views.rendering.js.MessagePort = function() { }
views.rendering.js.MessagePort.__name__ = ["views","rendering","js","MessagePort"];
views.rendering.js.MessagePort.prototype.postMessage = null;
views.rendering.js.MessagePort.prototype.start = null;
views.rendering.js.MessagePort.prototype.close = null;
views.rendering.js.MessagePort.prototype.onmessage = null;
views.rendering.js.MessagePort.prototype.__class__ = views.rendering.js.MessagePort;
Exception = function(message,cause) {
	if( message === $_ ) return;
	this.message_ = message;
	this.cause_ = cause;
}
Exception.__name__ = ["Exception"];
Exception.prototype.message_ = null;
Exception.prototype.cause_ = null;
Exception.prototype.message = null;
Exception.prototype.cause = null;
Exception.prototype.toString = function() {
	return this.message_;
}
Exception.prototype.get_message = function() {
	return this.message_;
}
Exception.prototype.get_cause = function() {
	return this.cause_;
}
Exception.prototype.__class__ = Exception;
Exception.__interfaces__ = [Throwable];
views.rendering.js.dom.VerticalRulerRenderer = function(id,view) {
	if( id === $_ ) return;
	views.rendering.js.dom.RulerRenderer.call(this,id,view);
}
views.rendering.js.dom.VerticalRulerRenderer.__name__ = ["views","rendering","js","dom","VerticalRulerRenderer"];
views.rendering.js.dom.VerticalRulerRenderer.__super__ = views.rendering.js.dom.RulerRenderer;
for(var k in views.rendering.js.dom.RulerRenderer.prototype ) views.rendering.js.dom.VerticalRulerRenderer.prototype[k] = views.rendering.js.dom.RulerRenderer.prototype[k];
views.rendering.js.dom.VerticalRulerRenderer.prototype.setup = function() {
	return new js.JQuery("<div class=\"renderable-vertical_ruler\" style=\"width:20px;\"><canvas width=\"20\"></canvas></div>");
}
views.rendering.js.dom.VerticalRulerRenderer.prototype.refresh = function() {
	var interval = this.graduations[0];
	var canvas = this.n[0].firstChild;
	canvas.height = this.n.innerHeight();
	var ctx = canvas.getContext("2d");
	ctx.clearRect(0,0,canvas.width,canvas.height);
	var offsetInUnit = UnitUtils.inchToAny(this.unit,this.offset);
	var minimumGraduation = this.getMinimumGraduation();
	var minimumGraduationWidth = this.graduations[minimumGraduation];
	var i = minimumGraduationWidth + Math.floor(offsetInUnit / minimumGraduationWidth) * minimumGraduationWidth;
	while(true) {
		var y = this.view_.inchToPixel(UnitUtils.anyToInch(this.unit,i - offsetInUnit));
		if(Std["int"](y) >= canvas.height) break;
		ctx.strokeRect(0,0,canvas.width,canvas.height);
		if(Math.floor(i / minimumGraduationWidth) % 10 == 0) {
			ctx.beginPath();
			ctx.moveTo(0,y);
			ctx.lineTo(20,y);
			ctx.stroke();
			var text = Std.string(Std["int"](i));
			ctx.fillText(text,20 - ctx.measureText(text).width,y + 10);
		} else {
			ctx.beginPath();
			ctx.moveTo(12,y);
			ctx.lineTo(20,y);
			ctx.stroke();
		}
		i += minimumGraduationWidth;
	}
}
views.rendering.js.dom.VerticalRulerRenderer.prototype.__class__ = views.rendering.js.dom.VerticalRulerRenderer;
views.View = function() { }
views.View.__name__ = ["views","View"];
views.View.prototype.ppi = null;
views.View.prototype.zoom = null;
views.View.prototype.viewport = null;
views.View.prototype.stage = null;
views.View.prototype.pixelToInch = null;
views.View.prototype.pixelToInchP = null;
views.View.prototype.inchToPixel = null;
views.View.prototype.inchToPixelP = null;
views.View.prototype.anyToPixel = null;
views.View.prototype.anyToPixelP = null;
views.View.prototype.dispose = null;
views.View.prototype.__class__ = views.View;
views.View.__interfaces__ = [Disposable];
Utils = function() { }
Utils.__name__ = ["Utils"];
Utils.deepcopy = function(v) {
	switch( (Type["typeof"](v))[1] ) {
	case 8:
		return null;
	case 4:
		if(Std["is"](v,Array)) {
			var obj = new Array();
			var v_ = (function($this) {
				var $r;
				var $t = v;
				if(Std["is"]($t,Array)) $t; else throw "Class cast error";
				$r = $t;
				return $r;
			}(this));
			var _g1 = 0, _g = v_.length;
			while(_g1 < _g) {
				var i = _g1++;
				obj.push(Utils.deepcopy(v_[i]));
			}
			return obj;
		} else {
			var klass = Type.getClass(v);
			if(klass == null) {
				var obj = { };
				var _g = 0, _g1 = Reflect.fields(v);
				while(_g < _g1.length) {
					var fieldName = _g1[_g];
					++_g;
					obj[fieldName] = Utils.deepcopy(Reflect.field(v,fieldName));
				}
				return obj;
			} else {
				var obj = Type.createEmptyInstance(Type.getClass(v));
				var _g = 0, _g1 = Reflect.fields(v);
				while(_g < _g1.length) {
					var fieldName = _g1[_g];
					++_g;
					obj[fieldName] = Utils.deepcopy(Reflect.field(v,fieldName));
				}
				return obj;
			}
		}
		break;
	case 1:
		return v;
	case 2:
		return v;
	case 3:
		return v;
	default:
		return v;
	}
	return null;
}
Utils.numberAsStringWithPrec = function(value,prec) {
	return value.toPrecision(prec);
}
Utils.prototype.__class__ = Utils;
StringBuf = function(p) {
	if( p === $_ ) return;
	this.b = new Array();
}
StringBuf.__name__ = ["StringBuf"];
StringBuf.prototype.add = function(x) {
	this.b[this.b.length] = x == null?"null":x;
}
StringBuf.prototype.addSub = function(s,pos,len) {
	this.b[this.b.length] = s.substr(pos,len);
}
StringBuf.prototype.addChar = function(c) {
	this.b[this.b.length] = String.fromCharCode(c);
}
StringBuf.prototype.toString = function() {
	return this.b.join("");
}
StringBuf.prototype.b = null;
StringBuf.prototype.__class__ = StringBuf;
UnitUtils = function() { }
UnitUtils.__name__ = ["UnitUtils"];
UnitUtils.anyToInch = function(unit,inch) {
	switch( (unit)[1] ) {
	case 0:
		return inch;
	case 3:
		return UnitUtils.mmToInch(inch);
	case 4:
		return UnitUtils.cmToInch(inch);
	case 5:
		return UnitUtils.meterToInch(inch);
	case 1:
		return UnitUtils.pointToInch(inch);
	case 2:
		return UnitUtils.picaToInch(inch);
	default:
		throw new IllegalArgumentException();
	}
}
UnitUtils.mmToInch = function(mm) {
	return mm / 25.4;
}
UnitUtils.cmToInch = function(cm) {
	return cm / 2.54;
}
UnitUtils.meterToInch = function(m) {
	return m / 0.0254;
}
UnitUtils.pointToInch = function(p) {
	return p / 72.;
}
UnitUtils.picaToInch = function(p) {
	return p / 12.;
}
UnitUtils.mmToInchP = function(mm) {
	return { x : mm.x / 25.4, y : mm.y / 25.4};
}
UnitUtils.cmToInchP = function(cm) {
	return { x : cm.x / 2.54, y : cm.y / 2.54};
}
UnitUtils.meterToInchP = function(m) {
	return { x : m.x / 0.0254, y : m.y / 0.0254};
}
UnitUtils.pointToInchP = function(p) {
	return { x : p.x / 72., y : p.y / 72.};
}
UnitUtils.picaToInchP = function(p) {
	return { x : p.x / 12., y : p.y / 12.};
}
UnitUtils.inchToAny = function(unit,inch) {
	switch( (unit)[1] ) {
	case 0:
		return inch;
	case 3:
		return UnitUtils.inchToMm(inch);
	case 4:
		return UnitUtils.inchToCm(inch);
	case 5:
		return UnitUtils.inchToMeter(inch);
	case 1:
		return UnitUtils.inchToPoint(inch);
	case 2:
		return UnitUtils.inchToPica(inch);
	default:
		throw new IllegalArgumentException();
	}
}
UnitUtils.inchToMm = function(inch) {
	return inch * 25.4;
}
UnitUtils.inchToCm = function(inch) {
	return inch * 2.54;
}
UnitUtils.inchToMeter = function(inch) {
	return inch * 0.0254;
}
UnitUtils.inchToPoint = function(inch) {
	return inch * 72.;
}
UnitUtils.inchToPica = function(inch) {
	return inch * 12.;
}
UnitUtils.inchToAnyP = function(unit,inch) {
	switch( (unit)[1] ) {
	case 0:
		return inch;
	case 3:
		return UnitUtils.inchToMmP(inch);
	case 4:
		return UnitUtils.inchToCmP(inch);
	case 5:
		return UnitUtils.inchToMeterP(inch);
	case 1:
		return UnitUtils.inchToPointP(inch);
	case 2:
		return UnitUtils.inchToPicaP(inch);
	default:
		throw new IllegalArgumentException();
	}
}
UnitUtils.inchToMmP = function(inch) {
	return { x : inch.x * 25.4, y : inch.y * 25.4};
}
UnitUtils.inchToCmP = function(inch) {
	return { x : inch.x * 2.54, y : inch.y * 2.54};
}
UnitUtils.inchToMeterP = function(inch) {
	return { x : inch.x * 0.0254, y : inch.y * 0.0254};
}
UnitUtils.inchToPointP = function(inch) {
	return { x : inch.x * 72., y : inch.y * 72.};
}
UnitUtils.inchToPicaP = function(inch) {
	return { x : inch.x * 12., y : inch.y * 12.};
}
UnitUtils.unitAsString = function(unit) {
	switch( (unit)[1] ) {
	case 0:
		return "in";
	case 3:
		return "mm";
	case 4:
		return "cm";
	case 5:
		return "m";
	case 1:
		return "pt";
	case 2:
		return "P";
	default:
		throw new IllegalArgumentException();
	}
}
UnitUtils.prototype.__class__ = UnitUtils;
views.rendering.js.dom.JSDOMView = function(base,viewport) {
	if( base === $_ ) return;
	this.batchRefreshNestCount = 0;
	this.refreshQueue = new Hash();
	this.renderers = new Hash();
	this.mouseEventsHandlerManager = new views.rendering.js.dom.MouseEventsHandlerManager();
	this.set_ppi(114);
	this.set_zoom(1.);
	this.viewport_ = new views.rendering.js.dom.JSDOMViewport(this);
	this.viewport_.set_n(viewport);
	this.stage_ = new views.rendering.js.dom.JSDOMStage(this);
	this.stage_.set_n(base);
	this.refreshAll();
}
views.rendering.js.dom.JSDOMView.__name__ = ["views","rendering","js","dom","JSDOMView"];
views.rendering.js.dom.JSDOMView.prototype.ppi = null;
views.rendering.js.dom.JSDOMView.prototype.zoom = null;
views.rendering.js.dom.JSDOMView.prototype.viewport = null;
views.rendering.js.dom.JSDOMView.prototype.stage = null;
views.rendering.js.dom.JSDOMView.prototype.viewport_ = null;
views.rendering.js.dom.JSDOMView.prototype.stage_ = null;
views.rendering.js.dom.JSDOMView.prototype.mouseEventsHandlerManager = null;
views.rendering.js.dom.JSDOMView.prototype.refreshQueue = null;
views.rendering.js.dom.JSDOMView.prototype.batchRefreshNestCount = null;
views.rendering.js.dom.JSDOMView.prototype.renderers = null;
views.rendering.js.dom.JSDOMView.prototype.set_ppi = function(value) {
	this.ppi = value;
	this.refreshAll();
	return value;
}
views.rendering.js.dom.JSDOMView.prototype.set_zoom = function(value) {
	if(this.viewport_ != null) {
		var oldViewportSize = this.pixelToInchP(this.viewport_.get_size());
		var oldScrollPosition = this.viewport_.get_scrollPosition();
		var center = { x : oldViewportSize.x / 2 + oldScrollPosition.x, y : oldViewportSize.y / 2 + oldScrollPosition.y};
		this.zoom = value;
		var newViewportSize = this.pixelToInchP(this.viewport_.get_size());
		var newScrollPosition = { x : center.x - newViewportSize.x / 2, y : center.y - newViewportSize.y / 2};
		this.viewport_.set_scrollPosition(newScrollPosition);
	} else this.zoom = value;
	this.refreshAll();
	return value;
}
views.rendering.js.dom.JSDOMView.prototype.get_viewport = function() {
	return this.viewport_;
}
views.rendering.js.dom.JSDOMView.prototype.get_stage = function() {
	return this.stage_;
}
views.rendering.js.dom.JSDOMView.prototype.dispose = function() {
	if(this.viewport_ != null) this.viewport_.dispose();
	if(this.stage_ != null) this.stage_.dispose();
}
views.rendering.js.dom.JSDOMView.prototype.pixelToInch = function(value) {
	return value / this.ppi / this.zoom;
}
views.rendering.js.dom.JSDOMView.prototype.pixelToInchP = function(value) {
	return { x : value.x / this.ppi / this.zoom, y : value.y / this.ppi / this.zoom};
}
views.rendering.js.dom.JSDOMView.prototype.inchToPixel = function(value) {
	return value * this.ppi * this.zoom;
}
views.rendering.js.dom.JSDOMView.prototype.inchToPixelP = function(value) {
	return { x : value.x * this.ppi * this.zoom, y : value.y * this.ppi * this.zoom};
}
views.rendering.js.dom.JSDOMView.prototype.anyToPixel = function(unit,value) {
	switch( (unit)[1] ) {
	case 0:
		return this.inchToPixel(value);
	case 1:
		return this.inchToPixel(UnitUtils.pointToInch(value));
	case 2:
		return this.inchToPixel(UnitUtils.picaToInch(value));
	case 3:
		return this.inchToPixel(UnitUtils.mmToInch(value));
	case 4:
		return this.inchToPixel(UnitUtils.cmToInch(value));
	case 5:
		return this.inchToPixel(UnitUtils.meterToInch(value));
	case 6:
		return value * this.zoom;
	}
}
views.rendering.js.dom.JSDOMView.prototype.anyToPixelP = function(unit,value) {
	switch( (unit)[1] ) {
	case 0:
		return this.inchToPixelP(value);
	case 1:
		return this.inchToPixelP(UnitUtils.pointToInchP(value));
	case 2:
		return this.inchToPixelP(UnitUtils.picaToInchP(value));
	case 3:
		return this.inchToPixelP(UnitUtils.mmToInchP(value));
	case 4:
		return this.inchToPixelP(UnitUtils.cmToInchP(value));
	case 5:
		return this.inchToPixelP(UnitUtils.meterToInchP(value));
	case 6:
		return { x : value.x * this.zoom, y : value.y * this.zoom};
	}
}
views.rendering.js.dom.JSDOMView.prototype.addRenderer = function(renderer) {
	this.renderers.set(Std.string(renderer.id),renderer);
}
views.rendering.js.dom.JSDOMView.prototype.beginBatchRefresh = function() {
	this.batchRefreshNestCount++;
}
views.rendering.js.dom.JSDOMView.prototype.endBatchRefresh = function() {
	if(this.batchRefreshNestCount == 0) throw new IllegalStateException("endBatchRefresh() called prior to beginBatcnRefresh()");
	if(--this.batchRefreshNestCount == 0) {
		var refreshQueue = this.refreshQueue;
		this.refreshQueue = new Hash();
		var $it0 = refreshQueue.keys();
		while( $it0.hasNext() ) {
			var id = $it0.next();
			this.renderers.get(id).refresh();
		}
	}
}
views.rendering.js.dom.JSDOMView.prototype.scheduleRefresh = function(what) {
	if(this.batchRefreshNestCount == 0) what.refresh(); else this.refreshQueue.set(Std.string(what.id),1);
}
views.rendering.js.dom.JSDOMView.prototype.refreshAll = function() {
	if(this.viewport_ != null) this.viewport_.refresh();
	if(this.stage_ != null) this.stage_.refresh();
	if(this.renderers != null) {
		if(this.batchRefreshNestCount == 0) {
			this.refreshQueue = new Hash();
			var $it0 = this.renderers.keys();
			while( $it0.hasNext() ) {
				var id = $it0.next();
				this.renderers.get(id).refresh();
			}
		} else {
			var $it1 = this.renderers.keys();
			while( $it1.hasNext() ) {
				var id = $it1.next();
				this.refreshQueue.set(id,1);
			}
		}
	}
}
views.rendering.js.dom.JSDOMView.prototype.__class__ = views.rendering.js.dom.JSDOMView;
views.rendering.js.dom.JSDOMView.__interfaces__ = [views.View];
if(typeof haxe=='undefined') haxe = {}
if(!haxe.rtti) haxe.rtti = {}
haxe.rtti.Meta = function() { }
haxe.rtti.Meta.__name__ = ["haxe","rtti","Meta"];
haxe.rtti.Meta.getType = function(t) {
	var meta = t.__meta__;
	return meta == null || meta.obj == null?{ }:meta.obj;
}
haxe.rtti.Meta.getStatics = function(t) {
	var meta = t.__meta__;
	return meta == null || meta.statics == null?{ }:meta.statics;
}
haxe.rtti.Meta.getFields = function(t) {
	var meta = t.__meta__;
	return meta == null || meta.fields == null?{ }:meta.fields;
}
haxe.rtti.Meta.prototype.__class__ = haxe.rtti.Meta;
OperationMode = { __ename__ : ["OperationMode"], __constructs__ : ["CURSOR","MOVE","PLACE"] }
OperationMode.CURSOR = ["CURSOR",0];
OperationMode.CURSOR.toString = $estr;
OperationMode.CURSOR.__enum__ = OperationMode;
OperationMode.MOVE = ["MOVE",1];
OperationMode.MOVE.toString = $estr;
OperationMode.MOVE.__enum__ = OperationMode;
OperationMode.PLACE = function(item) { var $x = ["PLACE",2,item]; $x.__enum__ = OperationMode; $x.toString = $estr; return $x; }
views.rendering.js.dom.MouseEventsHandler = function(n,onPress,onRelease,onMouseMove,onMouseOut) {
	if( n === $_ ) return;
	this.n = n;
	this.onPress = onPress;
	this.onRelease = onRelease;
	this.onMouseMove = onMouseMove;
	this.onMouseOut = onMouseOut;
}
views.rendering.js.dom.MouseEventsHandler.__name__ = ["views","rendering","js","dom","MouseEventsHandler"];
views.rendering.js.dom.MouseEventsHandler.prototype.id = null;
views.rendering.js.dom.MouseEventsHandler.prototype.n = null;
views.rendering.js.dom.MouseEventsHandler.prototype.onPress = null;
views.rendering.js.dom.MouseEventsHandler.prototype.onRelease = null;
views.rendering.js.dom.MouseEventsHandler.prototype.onMouseMove = null;
views.rendering.js.dom.MouseEventsHandler.prototype.onMouseOut = null;
views.rendering.js.dom.MouseEventsHandler.prototype.getHandlerFunctionFor = function(eventKind) {
	switch( (eventKind)[1] ) {
	case 0:
		return this.onPress;
	case 1:
		return this.onRelease;
	case 2:
		return this.onMouseMove;
	case 3:
		return this.onMouseOut;
	}
}
views.rendering.js.dom.MouseEventsHandler.prototype.__class__ = views.rendering.js.dom.MouseEventsHandler;
CommandSet = function(p) {
	if( p === $_ ) return;
	this.commands = new Array();
}
CommandSet.__name__ = ["CommandSet"];
CommandSet.prototype.data = null;
CommandSet.prototype.commands = null;
CommandSet.prototype.get_data = function() {
	return this.commands;
}
CommandSet.prototype.do_ = function() {
	var _g = 0, _g1 = this.commands;
	while(_g < _g1.length) {
		var command = _g1[_g];
		++_g;
		command.do_();
	}
}
CommandSet.prototype.undo = function() {
	var i = this.commands.length;
	while(--i >= 0) this.commands[i].undo();
}
CommandSet.prototype.add = function(command) {
	this.commands.push(command);
}
CommandSet.prototype.__class__ = CommandSet;
CommandSet.__interfaces__ = [Command];
views.EventKind = { __ename__ : ["views","EventKind"], __constructs__ : ["PRESS","RELEASE","MOUSEMOVE","MOUSEOUT"] }
views.EventKind.PRESS = ["PRESS",0];
views.EventKind.PRESS.toString = $estr;
views.EventKind.PRESS.__enum__ = views.EventKind;
views.EventKind.RELEASE = ["RELEASE",1];
views.EventKind.RELEASE.toString = $estr;
views.EventKind.RELEASE.__enum__ = views.EventKind;
views.EventKind.MOUSEMOVE = ["MOUSEMOVE",2];
views.EventKind.MOUSEMOVE.toString = $estr;
views.EventKind.MOUSEMOVE.__enum__ = views.EventKind;
views.EventKind.MOUSEOUT = ["MOUSEOUT",3];
views.EventKind.MOUSEOUT.toString = $estr;
views.EventKind.MOUSEOUT.__enum__ = views.EventKind;
views.TextComponent = function(factory,id,renderer) {
	if( factory === $_ ) return;
	views.Component.call(this,factory,id,renderer);
}
views.TextComponent.__name__ = ["views","TextComponent"];
views.TextComponent.__super__ = views.Component;
for(var k in views.Component.prototype ) views.TextComponent.prototype[k] = views.Component.prototype[k];
views.TextComponent.prototype.text = null;
views.TextComponent.prototype.fontSize = null;
views.TextComponent.prototype.initialize = function() {
	views.Component.prototype.initialize.call(this);
	this.text = "";
	this.fontSize = 10.5;
	this.size = { x : 0.25, y : 0.25};
	this.defaultCursor = views.MouseCursorKind.POINTER;
}
views.TextComponent.prototype.__class__ = views.TextComponent;
Hash = function(p) {
	if( p === $_ ) return;
	this.h = {}
	if(this.h.__proto__ != null) {
		this.h.__proto__ = null;
		delete(this.h.__proto__);
	}
}
Hash.__name__ = ["Hash"];
Hash.prototype.h = null;
Hash.prototype.set = function(key,value) {
	this.h["$" + key] = value;
}
Hash.prototype.get = function(key) {
	return this.h["$" + key];
}
Hash.prototype.exists = function(key) {
	try {
		key = "$" + key;
		return this.hasOwnProperty.call(this.h,key);
	} catch( e ) {
		for(var i in this.h) if( i == key ) return true;
		return false;
	}
}
Hash.prototype.remove = function(key) {
	if(!this.exists(key)) return false;
	delete(this.h["$" + key]);
	return true;
}
Hash.prototype.keys = function() {
	var a = new Array();
	for(var i in this.h) a.push(i.substr(1));
	return a.iterator();
}
Hash.prototype.iterator = function() {
	return { ref : this.h, it : this.keys(), hasNext : function() {
		return this.it.hasNext();
	}, next : function() {
		var i = this.it.next();
		return this.ref["$" + i];
	}};
}
Hash.prototype.toString = function() {
	var s = new StringBuf();
	s.b[s.b.length] = "{" == null?"null":"{";
	var it = this.keys();
	while( it.hasNext() ) {
		var i = it.next();
		s.b[s.b.length] = i == null?"null":i;
		s.b[s.b.length] = " => " == null?"null":" => ";
		s.add(Std.string(this.get(i)));
		if(it.hasNext()) s.b[s.b.length] = ", " == null?"null":", ";
	}
	s.b[s.b.length] = "}" == null?"null":"}";
	return s.b.join("");
}
Hash.prototype.__class__ = Hash;
views.rendering.js.dom.TextComponentRenderer = function(id,view) {
	if( id === $_ ) return;
	views.rendering.js.dom.JSDOMComponentRenderer.call(this,id,view);
}
views.rendering.js.dom.TextComponentRenderer.__name__ = ["views","rendering","js","dom","TextComponentRenderer"];
views.rendering.js.dom.TextComponentRenderer.__super__ = views.rendering.js.dom.JSDOMComponentRenderer;
for(var k in views.rendering.js.dom.JSDOMComponentRenderer.prototype ) views.rendering.js.dom.TextComponentRenderer.prototype[k] = views.rendering.js.dom.JSDOMComponentRenderer.prototype[k];
views.rendering.js.dom.TextComponentRenderer.prototype.text = null;
views.rendering.js.dom.TextComponentRenderer.prototype.position = null;
views.rendering.js.dom.TextComponentRenderer.prototype.size = null;
views.rendering.js.dom.TextComponentRenderer.prototype.fontSize = null;
views.rendering.js.dom.TextComponentRenderer.prototype.selected = null;
views.rendering.js.dom.TextComponentRenderer.prototype.setup = function() {
	return new js.JQuery("<div class=\"component-text\"></div>");
}
views.rendering.js.dom.TextComponentRenderer.prototype.realize = function(component) {
	this.text = component.text;
	this.position = component.position;
	this.fontSize = component.fontSize;
	this.size = component.size;
	this.selected = component.selected;
	this.view_.scheduleRefresh(this);
}
views.rendering.js.dom.TextComponentRenderer.prototype.refresh = function() {
	var position = this.view_.inchToPixelP(this.position);
	var size = this.view_.inchToPixelP(this.size);
	if(this.selected) this.n.addClass("selected"); else this.n.removeClass("selected");
	this.n.css({ left : Std.string(position.x) + "px", top : Std.string(position.y) + "px", fontSize : Std.string(this.view_.inchToPixel(UnitUtils.pointToInch(this.fontSize))) + "px", width : Std.string(size.x) + "px", height : Std.string(size.y) + "px"});
	this.n.text(this.text);
	views.rendering.js.dom.JSDOMComponentRenderer.prototype.refresh.call(this);
}
views.rendering.js.dom.TextComponentRenderer.prototype.__class__ = views.rendering.js.dom.TextComponentRenderer;
Std = function() { }
Std.__name__ = ["Std"];
Std["is"] = function(v,t) {
	return js.Boot.__instanceof(v,t);
}
Std.string = function(s) {
	return js.Boot.__string_rec(s,"");
}
Std["int"] = function(x) {
	if(x < 0) return Math.ceil(x);
	return Math.floor(x);
}
Std.parseInt = function(x) {
	var v = parseInt(x,10);
	if(v == 0 && x.charCodeAt(1) == 120) v = parseInt(x);
	if(isNaN(v)) return null;
	return v;
}
Std.parseFloat = function(x) {
	return parseFloat(x);
}
Std.random = function(x) {
	return Math.floor(Math.random() * x);
}
Std.prototype.__class__ = Std;
Throwables = function(throwables) {
	if( throwables === $_ ) return;
	this.throwables_ = throwables;
}
Throwables.__name__ = ["Throwables"];
Throwables.prototype.throwables_ = null;
Throwables.prototype.message = null;
Throwables.prototype.cause = null;
Throwables.prototype.push = function(throwable) {
	this.throwables_.push(throwable);
}
Throwables.prototype.toString = function() {
	var retval = "";
	var _g = 0, _g1 = this.throwables_;
	while(_g < _g1.length) {
		var throwable = _g1[_g];
		++_g;
		retval += throwable.toString();
		retval += "\n--\n";
	}
	return retval;
}
Throwables.prototype.get_message = function() {
	return "multiple throwables";
}
Throwables.prototype.get_cause = function() {
	return null;
}
Throwables.prototype.__class__ = Throwables;
Throwables.__interfaces__ = [Throwable];
views.ComponentFactory = function(stage,rendererFactory) {
	if( stage === $_ ) return;
	this.stage = stage;
	this.rendererFactory = rendererFactory;
	this.nextId = 1;
}
views.ComponentFactory.__name__ = ["views","ComponentFactory"];
views.ComponentFactory.prototype.nextId = null;
views.ComponentFactory.prototype.stage = null;
views.ComponentFactory.prototype.rendererFactory = null;
views.ComponentFactory.prototype.create = function(klass,options) {
	var renderer = (function($this) {
		var $r;
		var $t = $this.rendererFactory.create(klass,options);
		if(Std["is"]($t,views.ComponentRenderer)) $t; else throw "Class cast error";
		$r = $t;
		return $r;
	}(this));
	this.stage.add(renderer);
	return Type.createInstance(klass,[this,this.nextId++,renderer]);
}
views.ComponentFactory.prototype.__class__ = views.ComponentFactory;
if(!views._Component) views._Component = {}
views._Component.State = { __ename__ : ["views","_Component","State"], __constructs__ : ["NONE","PRESSED","DRAGGING"] }
views._Component.State.NONE = ["NONE",0];
views._Component.State.NONE.toString = $estr;
views._Component.State.NONE.__enum__ = views._Component.State;
views._Component.State.PRESSED = function(position) { var $x = ["PRESSED",1,position]; $x.__enum__ = views._Component.State; $x.toString = $estr; return $x; }
views._Component.State.DRAGGING = function(pof) { var $x = ["DRAGGING",2,pof]; $x.__enum__ = views._Component.State; $x.toString = $estr; return $x; }
views.rendering.js.dom.JQueryEventManager = function(n) {
	if( n === $_ ) return;
	this.set_n(n);
	this.handlerHash = new Hash();
}
views.rendering.js.dom.JQueryEventManager.__name__ = ["views","rendering","js","dom","JQueryEventManager"];
views.rendering.js.dom.JQueryEventManager.prototype.n = null;
views.rendering.js.dom.JQueryEventManager.prototype.handlerHash = null;
views.rendering.js.dom.JQueryEventManager.prototype.bind = function(eventName,handler) {
	var handlers = this.handlerHash.get(eventName);
	if(handlers == null) {
		handlers = new Array();
		this.handlerHash.set(eventName,handlers);
	}
	handlers.push(handler);
	if(this.n != null) this.n.bind(eventName,handler);
}
views.rendering.js.dom.JQueryEventManager.prototype.unbind = function(eventName,handler) {
	var handlers = this.handlerHash.get(eventName);
	if(handlers != null) {
		handlers.remove(handler);
		if(this.n != null) this.n.unbind(eventName,handler);
	}
	throw new Exception("No such handler");
}
views.rendering.js.dom.JQueryEventManager.prototype.unbindAllEvents = function() {
	var prevHandlerHash = this.handlerHash;
	this.handlerHash = new Hash();
	if(this.n != null) {
		var $it0 = prevHandlerHash.keys();
		while( $it0.hasNext() ) {
			var eventName = $it0.next();
			var handlers = prevHandlerHash.get(eventName);
			if(handlers != null) {
				var _g = 0;
				while(_g < handlers.length) {
					var handler = handlers[_g];
					++_g;
					this.n.unbind(eventName,handler);
				}
			}
		}
	}
}
views.rendering.js.dom.JQueryEventManager.prototype.set_n = function(value) {
	if(this.n != null) {
		var $it0 = this.handlerHash.keys();
		while( $it0.hasNext() ) {
			var eventName = $it0.next();
			var handlers = this.handlerHash.get(eventName);
			if(handlers != null) {
				var _g = 0;
				while(_g < handlers.length) {
					var handler = handlers[_g];
					++_g;
					this.n.unbind(eventName,handler);
				}
			}
		}
	}
	this.n = value;
	if(this.n != null) {
		var $it1 = this.handlerHash.keys();
		while( $it1.hasNext() ) {
			var eventName = $it1.next();
			var handlers = this.handlerHash.get(eventName);
			if(handlers != null) {
				var _g = 0;
				while(_g < handlers.length) {
					var handler = handlers[_g];
					++_g;
					this.n.bind(eventName,handler);
				}
			}
		}
	}
	return value;
}
views.rendering.js.dom.JQueryEventManager.prototype.__class__ = views.rendering.js.dom.JQueryEventManager;
views.Workspace = function(p) {
	if( p === $_ ) return;
	this.components_ = new IdentifiableSet();
	this.selection_ = new IdentifiableSet();
}
views.Workspace.__name__ = ["views","Workspace"];
views.Workspace.prototype.components = null;
views.Workspace.prototype.selection = null;
views.Workspace.prototype.numOfSelections = null;
views.Workspace.prototype.components_ = null;
views.Workspace.prototype.selection_ = null;
views.Workspace.prototype.get_components = function() {
	return this.components_;
}
views.Workspace.prototype.get_selection = function() {
	var retval = new Array();
	var $it0 = this.selection_.iterator();
	while( $it0.hasNext() ) {
		var component = $it0.next();
		retval.push(component);
	}
	return retval;
}
views.Workspace.prototype.get_numOfSelections = function() {
	return this.selection_.length;
}
views.Workspace.prototype.addToSelection = function(component,cause) {
	if(this.selection_.add(component)) component.addedToSelection(cause);
}
views.Workspace.prototype.removeFromSelection = function(component,cause) {
	if(this.selection_.remove(component)) component.removedFromSelection(cause);
}
views.Workspace.prototype.clearSelection = function() {
	var _g = 0, _g1 = this.get_selection();
	while(_g < _g1.length) {
		var component = _g1[_g];
		++_g;
		this.removeFromSelection(component,this);
	}
}
views.Workspace.prototype.add = function(component) {
	this.components_.add(component);
	component.set_workspace(this);
}
views.Workspace.prototype.remove = function(component) {
	component.set_workspace(null);
	this.components_.remove(component);
}
views.Workspace.prototype.__class__ = views.Workspace;
views.rendering.js.dom.ImageComponentRenderer = function(id,view) {
	if( id === $_ ) return;
	views.rendering.js.dom.JSDOMComponentRenderer.call(this,id,view);
}
views.rendering.js.dom.ImageComponentRenderer.__name__ = ["views","rendering","js","dom","ImageComponentRenderer"];
views.rendering.js.dom.ImageComponentRenderer.__super__ = views.rendering.js.dom.JSDOMComponentRenderer;
for(var k in views.rendering.js.dom.JSDOMComponentRenderer.prototype ) views.rendering.js.dom.ImageComponentRenderer.prototype[k] = views.rendering.js.dom.JSDOMComponentRenderer.prototype[k];
views.rendering.js.dom.ImageComponentRenderer.prototype.imageUrl = null;
views.rendering.js.dom.ImageComponentRenderer.prototype.position = null;
views.rendering.js.dom.ImageComponentRenderer.prototype.size = null;
views.rendering.js.dom.ImageComponentRenderer.prototype.selected = null;
views.rendering.js.dom.ImageComponentRenderer.prototype.canvasNode = null;
views.rendering.js.dom.ImageComponentRenderer.prototype.textNode = null;
views.rendering.js.dom.ImageComponentRenderer.prototype.setup = function() {
	var n = new js.JQuery("<div class=\"component-image\"><canvas></canvas><div class=\"text\"></div></div>");
	this.canvasNode = n.find("canvas")[0];
	this.textNode = n.find(".text");
	return n;
}
views.rendering.js.dom.ImageComponentRenderer.prototype.realize = function(component) {
	this.imageUrl = component.imageUrl;
	this.position = component.position;
	this.size = component.size;
	this.selected = component.selected;
	this.view_.scheduleRefresh(this);
}
views.rendering.js.dom.ImageComponentRenderer.prototype.refresh = function() {
	var position = this.view_.inchToPixelP(this.position);
	var size = this.view_.inchToPixelP(this.size);
	if(this.selected) this.n.addClass("selected"); else this.n.removeClass("selected");
	this.canvasNode.width = Std["int"](size.x);
	this.canvasNode.height = Std["int"](size.y);
	var ctx = this.canvasNode.getContext("2d");
	ctx.strokeStyle = "#888";
	ctx.fillStyle = "#fff";
	ctx.fillRect(0,0,this.canvasNode.width,this.canvasNode.height);
	ctx.strokeRect(0,0,this.canvasNode.width,this.canvasNode.height);
	if(this.imageUrl == null) {
		ctx.beginPath();
		ctx.moveTo(0,0);
		ctx.lineTo(this.canvasNode.width,this.canvasNode.height);
		ctx.stroke();
		ctx.beginPath();
		ctx.moveTo(0,this.canvasNode.height);
		ctx.lineTo(this.canvasNode.width,0);
		ctx.stroke();
	}
	var preferredUnit = UnitKind.MILLIMETER;
	var sizeInPreferredUnit = UnitUtils.inchToAnyP(preferredUnit,this.size);
	this.textNode.text(Utils.numberAsStringWithPrec(sizeInPreferredUnit.x,4) + "×" + Utils.numberAsStringWithPrec(sizeInPreferredUnit.y,4) + UnitUtils.unitAsString(preferredUnit));
	this.n.css({ left : Std.string(position.x) + "px", top : Std.string(position.y) + "px", width : Std.string(size.x) + "px", height : Std.string(size.y) + "px"});
	views.rendering.js.dom.JSDOMComponentRenderer.prototype.refresh.call(this);
}
views.rendering.js.dom.ImageComponentRenderer.prototype.__class__ = views.rendering.js.dom.ImageComponentRenderer;
if(typeof _Shell=='undefined') _Shell = {}
_Shell.State = { __ename__ : ["_Shell","State"], __constructs__ : ["NONE","DRAGGING"] }
_Shell.State.NONE = ["NONE",0];
_Shell.State.NONE.toString = $estr;
_Shell.State.NONE.__enum__ = _Shell.State;
_Shell.State.DRAGGING = function(initialScrollPosition,initialPosition) { var $x = ["DRAGGING",1,initialScrollPosition,initialPosition]; $x.__enum__ = _Shell.State; $x.toString = $estr; return $x; }
Shell = function(view,componentFactory,workspace) {
	if( view === $_ ) return;
	this.view = view;
	this.componentFactory = componentFactory;
	this.workspace = workspace;
	this.inMoveMode = false;
	this.lastKey = 0;
	view.get_stage().bind(views.EventKind.PRESS,$closure(this,"onStagePressed"));
}
Shell.__name__ = ["Shell"];
Shell.prototype.operationMode = null;
Shell.prototype.view = null;
Shell.prototype.workspace = null;
Shell.prototype.operationModeCallback = null;
Shell.prototype.lastKey = null;
Shell.prototype.ghost = null;
Shell.prototype.ghostData = null;
Shell.prototype.componentFactory = null;
Shell.prototype.inMoveMode = null;
Shell.prototype.set_operationMode = function(newOperationMode) {
	if(newOperationMode == this.operationMode) return newOperationMode;
	this.discardGhost();
	this.finishMoveMode();
	this.workspace.clearSelection();
	var $e = (newOperationMode);
	switch( $e[1] ) {
	case 0:
		this.view.get_stage().set_cursor(views.MouseCursorKind.DEFAULT);
		break;
	case 1:
		this.view.get_stage().set_cursor(views.MouseCursorKind.MOVE);
		this.beginMoveMode();
		break;
	case 2:
		var item = $e[2];
		this.view.get_stage().set_cursor(views.MouseCursorKind.POINTER);
		this.prepareGhost(item);
		break;
	}
	if(this.operationModeCallback != null) this.operationModeCallback(newOperationMode);
	this.operationMode = newOperationMode;
	return newOperationMode;
}
Shell.prototype.discardGhost = function() {
	if(this.ghost == null) return;
	this.view.get_stage().remove(this.ghost);
	this.ghost.dispose();
	this.ghost = null;
	this.ghostData = null;
}
Shell.prototype.prepareGhost = function(klass) {
	var me = this;
	if(this.ghost != null) throw new IllegalStateException("Ghost already exists");
	this.ghost = this.componentFactory.rendererFactory.create(klass);
	this.ghost.opacity = .5;
	this.ghostData = { position : { x : 0, y : -30}, text : "text", fontSize : 10.5, size : { x : 0.25, y : 0.16}};
	this.view.get_stage().add(this.ghost);
	this.ghost.opacity = .5;
	this.ghost.bind(views.EventKind.MOUSEMOVE,function(e) {
		me.ghostData.position = { x : e.position.x - me.ghost.get_innerRenderSize().x / 2, y : e.position.y - me.ghost.get_innerRenderSize().y / 2};
		me.ghost.realize(me.ghostData);
	});
	this.ghost.bind(views.EventKind.PRESS,function(e) {
		var component = me.componentFactory.create(klass);
		var _g = 0, _g1 = Reflect.fields(me.ghostData);
		while(_g < _g1.length) {
			var field = _g1[_g];
			++_g;
			if(Reflect.hasField(component,field)) component[field] = Reflect.field(me.ghostData,field);
		}
		me.attachController(component);
		component.refresh();
	});
	this.ghost.realize(this.ghostData);
	this.ghost.captureMouse();
}
Shell.prototype.attachController = function(component) {
	var me = this;
	component.on.click.do_(function(e) {
		if(!component.selected && me.lastKey != 16) {
			me.workspace.clearSelection();
			component.putResizeBox();
		}
		if(me.lastKey == 16) {
			if(component.selected) component.unselect(); else component.select();
		} else component.select();
	});
	component.on.doubleclick.do_(function(e) {
	});
	component.on.dragstart.do_(function(e) {
		component.hideResizeBox();
	});
	component.on.dragend.do_(function(e) {
		if(me.workspace.get_numOfSelections() == 1) component.putResizeBox();
	});
	component.on.blur.do_(function(e) {
		component.hideResizeBox();
	});
	this.workspace.add(component);
}
Shell.prototype.finishMoveMode = function() {
	if(!this.inMoveMode) return;
	this.view.get_stage().releaseMouse();
	this.view.get_stage().bind(views.EventKind.PRESS,$closure(this,"onStagePressed"));
	this.view.get_stage().bind(views.EventKind.RELEASE,null);
	this.view.get_stage().bind(views.EventKind.MOUSEMOVE,null);
	this.inMoveMode = false;
}
Shell.prototype.beginMoveMode = function() {
	var me = this;
	if(this.inMoveMode) return;
	var state = _Shell.State.NONE;
	this.view.get_stage().bind(views.EventKind.PRESS,function(e) {
		state = _Shell.State.DRAGGING(me.view.get_viewport().get_scrollPosition(),e.screenPosition);
	});
	this.view.get_stage().bind(views.EventKind.RELEASE,function(e) {
		state = _Shell.State.NONE;
	});
	this.view.get_stage().bind(views.EventKind.MOUSEMOVE,function(e) {
		var e_ = e;
		var $e = (state);
		switch( $e[1] ) {
		case 0:
			break;
		case 1:
			var initialPosition = $e[3], initialScrollPosition = $e[2];
			var offset = me.view.pixelToInchP({ x : e_.screenPosition.x - initialPosition.x, y : e_.screenPosition.y - initialPosition.y});
			var newScrollPosition = { x : initialScrollPosition.x - offset.x, y : initialScrollPosition.y - offset.y};
			if(newScrollPosition.x < 0.) {
				initialScrollPosition = { x : 0., y : initialScrollPosition.y};
				initialPosition = { x : e_.screenPosition.x, y : initialPosition.y};
				state = _Shell.State.DRAGGING(initialScrollPosition,initialPosition);
				newScrollPosition.x = 0.;
			}
			if(newScrollPosition.y < 0.) {
				initialScrollPosition = { x : initialScrollPosition.x, y : 0.};
				initialPosition = { x : initialPosition.x, y : e_.screenPosition.y};
				state = _Shell.State.DRAGGING(initialScrollPosition,initialPosition);
				newScrollPosition.y = 0.;
			}
			me.view.get_viewport().set_scrollPosition(newScrollPosition);
			break;
		}
	});
	this.view.get_stage().captureMouse();
	this.inMoveMode = true;
}
Shell.prototype.zoomIn = function() {
	var _g = this.view;
	_g.set_zoom(_g.zoom * 1.1);
}
Shell.prototype.zoomOut = function() {
	var _g = this.view;
	_g.set_zoom(_g.zoom / 1.1);
}
Shell.prototype.onStagePressed = function(e) {
	this.workspace.clearSelection();
}
Shell.prototype.__class__ = Shell;
TicketDesigner = function(view) {
	if( view === $_ ) return;
	var me = this;
	this.view = view;
	this.rendererFactory = new views.BasicRendererFactoryImpl(view,views.rendering.js.dom.Spi.get_rendererRegistry());
	this.componentFactory = new views.ComponentFactory(view.get_stage(),this.rendererFactory);
	this.workspace = new views.Workspace();
	this.shell = new Shell(view,this.componentFactory,this.workspace);
	this.horizontalRuler = this.createHorizontalRuler();
	this.verticalRuler = this.createVerticalRuler();
	this.view.get_viewport().on.scroll.do_(function(e) {
		me.horizontalRuler.offset = e.position.x;
		me.verticalRuler.offset = e.position.y;
		me.horizontalRuler.refresh();
		me.verticalRuler.refresh();
	});
}
TicketDesigner.__name__ = ["TicketDesigner"];
TicketDesigner.prototype.view = null;
TicketDesigner.prototype.shell = null;
TicketDesigner.prototype.rendererFactory = null;
TicketDesigner.prototype.horizontalRuler = null;
TicketDesigner.prototype.verticalRuler = null;
TicketDesigner.prototype.componentFactory = null;
TicketDesigner.prototype.workspace = null;
TicketDesigner.prototype.horizontalGuide = null;
TicketDesigner.prototype.verticalGuide = null;
TicketDesigner.prototype.horizontalRuler_dragstart = function(e) {
	this.horizontalGuide = this.componentFactory.create(views.HorizontalGuide);
	this.horizontalGuide.position = e.position;
	this.view.get_stage().set_cursor(views.MouseCursorKind.CROSSHAIR);
	this.horizontalGuide.refresh();
}
TicketDesigner.prototype.horizontalRuler_drag = function(e) {
	this.horizontalGuide.position = e.position;
	this.horizontalGuide.refresh();
}
TicketDesigner.prototype.horizontalRuler_dragend = function(e) {
	this.view.get_stage().set_cursor(views.MouseCursorKind.DEFAULT);
	if(e.screenPosition.y - this.view.get_viewport().screenOffset.y < 0) this.view.get_stage().remove((function($this) {
		var $r;
		var $t = $this.horizontalGuide.renderer;
		if(Std["is"]($t,views.ComponentRenderer)) $t; else throw "Class cast error";
		$r = $t;
		return $r;
	}(this)));
}
TicketDesigner.prototype.verticalRuler_dragstart = function(e) {
	this.verticalGuide = this.componentFactory.create(views.VerticalGuide);
	this.verticalGuide.position = e.position;
	this.view.get_stage().set_cursor(views.MouseCursorKind.CROSSHAIR);
	this.verticalGuide.refresh();
}
TicketDesigner.prototype.verticalRuler_drag = function(e) {
	this.verticalGuide.position = e.position;
	this.verticalGuide.refresh();
}
TicketDesigner.prototype.verticalRuler_dragend = function(e) {
	this.view.get_stage().set_cursor(views.MouseCursorKind.DEFAULT);
	if(e.screenPosition.x - this.view.get_viewport().screenOffset.x < 0) this.view.get_stage().remove((function($this) {
		var $r;
		var $t = $this.verticalGuide.renderer;
		if(Std["is"]($t,views.ComponentRenderer)) $t; else throw "Class cast error";
		$r = $t;
		return $r;
	}(this)));
}
TicketDesigner.prototype.createHorizontalRuler = function() {
	var ruler = new views.Ruler(this.rendererFactory.create(views.Ruler,{ variant : "horizontal"}));
	ruler.on.dragstart.do_($closure(this,"horizontalRuler_dragstart"));
	ruler.on.drag.do_($closure(this,"horizontalRuler_drag"));
	ruler.on.dragend.do_($closure(this,"horizontalRuler_dragend"));
	return ruler;
}
TicketDesigner.prototype.createVerticalRuler = function() {
	var ruler = new views.Ruler(this.rendererFactory.create(views.Ruler,{ variant : "vertical"}));
	ruler.on.dragstart.do_($closure(this,"verticalRuler_dragstart"));
	ruler.on.drag.do_($closure(this,"verticalRuler_drag"));
	ruler.on.dragend.do_($closure(this,"verticalRuler_dragend"));
	return ruler;
}
TicketDesigner.prototype.refresh = function() {
	this.horizontalRuler.refresh();
	this.verticalRuler.refresh();
}
TicketDesigner.prototype.__class__ = TicketDesigner;
IllegalArgumentException = function(message,cause) {
	if( message === $_ ) return;
	Exception.call(this,message,cause);
}
IllegalArgumentException.__name__ = ["IllegalArgumentException"];
IllegalArgumentException.__super__ = Exception;
for(var k in Exception.prototype ) IllegalArgumentException.prototype[k] = Exception.prototype[k];
IllegalArgumentException.prototype.__class__ = IllegalArgumentException;
js.Lib = function() { }
js.Lib.__name__ = ["js","Lib"];
js.Lib.isIE = null;
js.Lib.isOpera = null;
js.Lib.document = null;
js.Lib.window = null;
js.Lib.alert = function(v) {
	alert(js.Boot.__string_rec(v,""));
}
js.Lib.eval = function(code) {
	return eval(code);
}
js.Lib.setErrorHandler = function(f) {
	js.Lib.onerror = f;
}
js.Lib.prototype.__class__ = js.Lib;
IllegalStateException = function(message,cause) {
	if( message === $_ ) return;
	Exception.call(this,message,cause);
}
IllegalStateException.__name__ = ["IllegalStateException"];
IllegalStateException.__super__ = Exception;
for(var k in Exception.prototype ) IllegalStateException.prototype[k] = Exception.prototype[k];
IllegalStateException.prototype.__class__ = IllegalStateException;
$_ = {}
js.Boot.__res = {}
js.Boot.__init();
views.rendering.js.dom.Spi.get_rendererRegistry().addImplementation(views.HorizontalGuide,views.rendering.js.dom.HorizontalGuideRenderer);
views.rendering.js.dom.Spi.get_rendererRegistry().addImplementation(views.Ruler,views.rendering.js.dom.HorizontalRulerRenderer,"horizontal");
views.rendering.js.dom.Spi.get_rendererRegistry().addImplementation(views.Component,views.rendering.js.dom.ResizeBoxRenderer,"resize_box");
{
	Math.__name__ = ["Math"];
	Math.NaN = Number["NaN"];
	Math.NEGATIVE_INFINITY = Number["NEGATIVE_INFINITY"];
	Math.POSITIVE_INFINITY = Number["POSITIVE_INFINITY"];
	Math.isFinite = function(i) {
		return isFinite(i);
	};
	Math.isNaN = function(i) {
		return isNaN(i);
	};
}
views.rendering.js.dom.Spi.get_rendererRegistry().addImplementation(views.VerticalGuide,views.rendering.js.dom.VerticalGuideRenderer);
views.rendering.js.dom.Spi.get_rendererRegistry().addImplementation(views.Ruler,views.rendering.js.dom.VerticalRulerRenderer,"vertical");
{
	var q = window.jQuery;
	js.JQuery = q;
	q.fn.noBubble = q.fn.bind;
	q.fn.loadURL = q.fn.load;
	q.fn.toggleClick = q.fn.toggle;
	q.of = q;
	q.fn.iterator = function() {
		return { pos : 0, j : this, hasNext : function() {
			return this.pos < this.j.length;
		}, next : function() {
			return $(this.j[this.pos++]);
		}};
	};
}
views.rendering.js.dom.Spi.get_rendererRegistry().addImplementation(views.TextComponent,views.rendering.js.dom.TextComponentRenderer);
{
	String.prototype.__class__ = String;
	String.__name__ = ["String"];
	Array.prototype.__class__ = Array;
	Array.__name__ = ["Array"];
	Int = { __name__ : ["Int"]};
	Dynamic = { __name__ : ["Dynamic"]};
	Float = Number;
	Float.__name__ = ["Float"];
	Bool = { __ename__ : ["Bool"]};
	Class = { __name__ : ["Class"]};
	Enum = { };
	Void = { __ename__ : ["Void"]};
}
views.rendering.js.dom.Spi.get_rendererRegistry().addImplementation(views.ImageComponent,views.rendering.js.dom.ImageComponentRenderer);
{
	var d = Date;
	d.now = function() {
		return new Date();
	};
	d.fromTime = function(t) {
		var d1 = new Date();
		d1["setTime"](t);
		return d1;
	};
	d.fromString = function(s) {
		switch(s.length) {
		case 8:
			var k = s.split(":");
			var d1 = new Date();
			d1["setTime"](0);
			d1["setUTCHours"](k[0]);
			d1["setUTCMinutes"](k[1]);
			d1["setUTCSeconds"](k[2]);
			return d1;
		case 10:
			var k = s.split("-");
			return new Date(k[0],k[1] - 1,k[2],0,0,0);
		case 19:
			var k = s.split(" ");
			var y = k[0].split("-");
			var t = k[1].split(":");
			return new Date(y[0],y[1] - 1,y[2],t[0],t[1],t[2]);
		default:
			throw "Invalid date format : " + s;
		}
	};
	d.prototype["toString"] = function() {
		var date = this;
		var m = date.getMonth() + 1;
		var d1 = date.getDate();
		var h = date.getHours();
		var mi = date.getMinutes();
		var s = date.getSeconds();
		return date.getFullYear() + "-" + (m < 10?"0" + m:"" + m) + "-" + (d1 < 10?"0" + d1:"" + d1) + " " + (h < 10?"0" + h:"" + h) + ":" + (mi < 10?"0" + mi:"" + mi) + ":" + (s < 10?"0" + s:"" + s);
	};
	d.prototype.__class__ = d;
	d.__name__ = ["Date"];
}
{
	js.Lib.document = document;
	js.Lib.window = window;
	onerror = function(msg,url,line) {
		var f = js.Lib.onerror;
		if( f == null )
			return false;
		return f(msg,[url+":"+line]);
	}
}
views.rendering.js.dom.MouseEventsHandlerManager.eventNames = ["mousedown","mouseup","mousemove","mouseout"];
views.rendering.js.dom.ResizeBoxRenderer.corners = [[".nw",Direction.NORTH_WEST],[".sw",Direction.SOUTH_WEST],[".ne",Direction.NORTH_EAST],[".se",Direction.SOUTH_EAST]];
js.Lib.onerror = null;
