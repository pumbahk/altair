package jp.ticketstar.ticketing.printing;

import java.awt.Cursor;
import java.awt.Point;
import java.awt.geom.AffineTransform;
import java.awt.geom.Dimension2D;
import java.awt.print.PrinterJob;
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.net.URI;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executor;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.logging.Logger;

import javax.print.PrintService;
import javax.swing.event.ListDataEvent;

import jp.ticketstar.ticketing.InTime;
import jp.ticketstar.ticketing.LoggingUtils;
import jp.ticketstar.ticketing.printing.gui.IAppWindow;
import jp.ticketstar.ticketing.svg.ExtendedSVG12BridgeContext;
import jp.ticketstar.ticketing.svg.ExtendedSVG12OMDocument;
import jp.ticketstar.ticketing.svg.OurDocumentLoader;
import jp.ticketstar.ticketing.swing.ExtendedListDataListener;

import org.apache.batik.bridge.BridgeExtension;
import org.apache.batik.bridge.UserAgent;
import org.apache.batik.gvt.event.EventDispatcher;
import org.apache.batik.gvt.text.Mark;
import org.apache.batik.swing.svg.SVGDocumentLoader;
import org.apache.batik.swing.svg.SVGDocumentLoaderEvent;
import org.apache.batik.swing.svg.SVGDocumentLoaderListener;
import org.apache.batik.swing.svg.SVGUserAgentGUIAdapter;
import org.w3c.dom.Element;
import org.w3c.dom.svg.SVGAElement;
import org.w3c.dom.svg.SVGDocument;

public abstract class BasicAppService extends SVGUserAgentGUIAdapter implements MinimumAppService, UserAgent {
	private static final Logger logger = Logger.getLogger(BasicAppService.class.getName());
	protected AppModel model;
	protected volatile SVGDocumentLoader documentLoader;
	protected IAppWindow appWindow;
	protected LinkedList<Runnable> pendingTasks = new LinkedList<Runnable>();
	protected List<PageEventListener> pageEventListeners = new ArrayList<PageEventListener>();
	protected PropertyChangeListener pageSetModelChanged = new PropertyChangeListener() {
		@Override
		public void propertyChange(PropertyChangeEvent evt) {
			final PageSetModel _model = (PageSetModel)evt.getNewValue();
			if(_model == null) {
				return;
			}
			_model.getPages().addListDataListener(new ExtendedListDataListener() {
				volatile List<Page> pagesToBeRemoved = null;

				@Override
				public void contentsChanged(ListDataEvent e) {}

				@Override
				public void intervalAdded(ListDataEvent e) {
					@SuppressWarnings("unchecked")
					final List<Page> _model = (List<Page>)e.getSource();
					final int index0 = e.getIndex0(), index1 = e.getIndex1();
					for (int i = index0; i < index1; i++) {
						firePageAddedEvent(new PageEvent(BasicAppService.this, _model.get(i)));
					}
				}

				@Override
				public void intervalRemoved(ListDataEvent e) {
					final List<Page> pagesToBeRemoved = this.pagesToBeRemoved;
					for (Page p: pagesToBeRemoved) {
						firePageRemovedEvent(new PageEvent(BasicAppService.this, p));
					}
				}

				@Override
				public void intervalBeingRemoved(ListDataEvent e) {
					final List<Page> pagesToBeRemoved = new ArrayList<Page>();
					@SuppressWarnings("unchecked")
					final List<Page> _model = (List<Page>)e.getSource();
					final int index0 = e.getIndex0(), index1 = e.getIndex1();
					for (int i = index0; i < index1; i++) {
						pagesToBeRemoved.add(_model.get(i));
					}
					this.pagesToBeRemoved = pagesToBeRemoved;
				}
			});			
		}
	};

	protected class LoaderListener<T extends ExtendedSVG12OMDocument> implements SVGDocumentLoaderListener, Future<T> {
		protected ExtendedSVG12BridgeContext bridgeContext;
		protected volatile boolean done = false;
		protected T result = null;
		protected Exception exception = null;

		@Override
		public boolean cancel(boolean mayInterruptIfRunning) {
			return false;
		}

		@Override
		public synchronized T get() throws InterruptedException, ExecutionException {
			if (!done)
				wait();
			if (exception != null)
				throw new ExecutionException(exception);
			return result;
		}

		@Override
		public synchronized T get(long timeout, TimeUnit unit) throws InterruptedException,
				ExecutionException, TimeoutException {
			if (!done) {
				wait(unit.toMillis(timeout));
				if (!done) {
					throw new TimeoutException();
				}
			}
			if (exception != null)
				throw new ExecutionException(exception);
			return result;
		}

		@Override
		public boolean isCancelled() {
			return false;
		}

		@Override
		public boolean isDone() {
			return done;
		}

		private void next(T result, Exception exception) {
			appWindow.setInteractionEnabled(true);
			BasicAppService.this.documentLoader = null;
			synchronized (this) {
				this.result = result;
				this.exception = exception;
				done = true;
				notifyAll();
			}
			BasicAppService.this.doPendingTasks(null);
		}
	
		public void documentLoadingCancelled(SVGDocumentLoaderEvent arg0) {
			logger.info("load canceled");
			next(null, null);
			displayError("Load canceled");
		}

		public void documentLoadingCompleted(SVGDocumentLoaderEvent arg0) {
			// TODO: do it async!
			try {
				bridgeContext.setInteractive(false);
				bridgeContext.setDynamic(false);
				@SuppressWarnings("unchecked")
				T svgDocument = (T)arg0.getSVGDocument();
				BasicAppService.this.model.setPageSetModel(new PageSetModel(bridgeContext, svgDocument));				
				next(svgDocument, null);
			} catch (Exception e) {
				e.printStackTrace();
				next(null, e);
				displayError("Failed to load document\nReason: " + e);
			} finally {
				logger.info("Load completed");
			}
		}

		public void documentLoadingFailed(SVGDocumentLoaderEvent arg0) {
			logger.severe(LoggingUtils.formatException(((SVGDocumentLoader)arg0.getSource()).getException()));
			next(null, ((SVGDocumentLoader)arg0.getSource()).getException());
			displayError("Failed to load document\nReason: " + ((SVGDocumentLoader)arg0.getSource()).getException());
		}

		public void documentLoadingStarted(SVGDocumentLoaderEvent arg0) {
			logger.info("load started");
			appWindow.setInteractionEnabled(false);
		}

		public LoaderListener(ExtendedSVG12BridgeContext bridgeContext) {
			this.bridgeContext = bridgeContext;
		}
	}

	public void setAppWindow(IAppWindow appWindow) {
		parentComponent = appWindow.getFrame();
		appWindow.bind(model);
		this.appWindow = appWindow;
	}

	public void deselectAll() {
		// TODO Auto-generated method stub
		
	}

	public SVGDocument getBrokenLinkDocument(Element arg0, String arg1,
			String arg2) {
		// TODO Auto-generated method stub
		return null;
	}

	public Point getClientAreaLocationOnScreen() {
		// TODO Auto-generated method stub
		return null;
	}

	public EventDispatcher getEventDispatcher() {
		// TODO Auto-generated method stub
		return null;
	}

	public AffineTransform getTransform() {
		// TODO Auto-generated method stub
		return null;
	}

	public Dimension2D getViewportSize() {
		// TODO Auto-generated method stub
		return null;
	}

	public boolean hasFeature(String arg0) {
		// TODO Auto-generated method stub
		return false;
	}

	public void openLink(SVGAElement arg0) {
		// TODO Auto-generated method stub
		
	}

	public void registerExtension(BridgeExtension arg0) {
		// TODO Auto-generated method stub
		
	}

	public void setSVGCursor(Cursor arg0) {
		// TODO Auto-generated method stub
		
	}

	public void setTextSelection(Mark arg0, Mark arg1) {
		// TODO Auto-generated method stub
		
	}

	public void setTransform(AffineTransform arg0) {
		// TODO Auto-generated method stub	
	}

	public synchronized Future<ExtendedSVG12OMDocument> loadDocument(URI uri) {		
		if (this.documentLoader != null)
			throw new IllegalStateException("Document is being loaded");
		final OurDocumentLoader loader = new OurDocumentLoader(this);
		final SVGDocumentLoader documentLoader = new SVGDocumentLoader(uri.toString(), loader);
		this.documentLoader = documentLoader;
		final LoaderListener<ExtendedSVG12OMDocument> retval = new LoaderListener<ExtendedSVG12OMDocument>(new ExtendedSVG12BridgeContext(this, loader));
		documentLoader.addSVGDocumentLoaderListener(retval);
		documentLoader.start();
		return retval;
	}
	
	protected TicketPrintable createTicketPrintable(PrinterJob job) {
		return new TicketPrintable(
			new ArrayList<Page>(model.getPageSetModel().getPages()), job,
			new AffineTransform(72. / 90, 0, 0, 72. / 90, 0, 0)
		);
	}

	public List<OurPageFormat> getPageFormats() {
		return model.getPageFormats() == null ?
			null: new ArrayList<OurPageFormat>(model.getPageFormats());
	}

	public OurPageFormat getPageFormat() {
		return model.getPageFormat();
	}
	
	public synchronized void setPageFormat(OurPageFormat pageFormat) {
		if (this.documentLoader != null)
			throw new IllegalStateException("Document is being loaded");
		model.setPageFormat(pageFormat);
	}

	public void addListenerForPageFormat(PropertyChangeListener listener) {
		model.addPropertyChangeListener("pageFormat", listener);
	}
	
	public List<PrintService> getPrintServices() {
		return model.getPrintServices() == null ?
			null: new ArrayList<PrintService>(model.getPrintServices());
	}

	public PrintService getPrintService() {
		return model.getPrintService();
	}
	
	public void setPrintService(PrintService printService) {
		model.setPrintService(printService);
	}

	public void addListenerForPrintService(PropertyChangeListener listener) {
		model.addPropertyChangeListener("printService", listener);
	}

	public List<Page> getPages() {
		final PageSetModel pageSetModel = model.getPageSetModel();
		return pageSetModel == null ? null: new ArrayList<Page>(pageSetModel.getPages());
	}

	public void addListenerForPages(PropertyChangeListener listener) {
		model.addPropertyChangeListener("pageSetModel", listener);
	}

	public boolean getPrintingStatus() {
		return model.getPrintingStatus();
	}

	public void addListenerForPrintingStatus(PropertyChangeListener listener) {
		model.addPropertyChangeListener("printingStatus", listener);
	}

	public void addPageEventListener(PageEventListener listener) {
		this.pageEventListeners.add(listener);
	}

	public void removePageEventListener(PageEventListener listener) {
		this.pageEventListeners.remove(listener);
	}

	protected void doPendingTasks(Executor executor) {
		logger.entering(getClass().getName(), "doPendingTasks()");
		ArrayList<Runnable> tasksToBeDone = null;
		synchronized (pendingTasks) {
			tasksToBeDone = new ArrayList<Runnable>(pendingTasks);
			pendingTasks.clear();
		}
		if (executor == null) {
			executor = InTime.getInstance();
		}
		{
			final List<Runnable> _tasksToBeDone = tasksToBeDone;
			executor.execute(new Runnable() {
				@Override
				public void run() {
					for (final Runnable task: _tasksToBeDone) {
						logger.finer("running task: " + task);
						try {
							task.run();
						} catch (Exception e) {
							logger.severe(LoggingUtils.formatException(e));
						}
					}	
				}
			});
		}
		logger.exiting(getClass().getName(), "doPendingTasks()");
	}
	
	public void invokeWhenDocumentReady(Runnable runnable, Executor executor) {
		logger.entering(getClass().getName(), "invokeWhenDocumentReady()");
		logger.finer("registering task: " + runnable);
		synchronized (pendingTasks) {
			pendingTasks.add(runnable);
		}
		if (documentLoader == null)
			doPendingTasks(executor);
		logger.exiting(getClass().getName(), "invokeWhenDocumentReady()");
	}

	protected void firePageAddedEvent(PageEvent evt) {
		for (PageEventListener listener: pageEventListeners) {
			listener.pageAdded(evt);
		}
	}

	protected void firePageRemovedEvent(PageEvent evt) {
		for (PageEventListener listener: pageEventListeners) {
			listener.pageRemoved(evt);
		}
	}

	protected void firePagePrintedEvent(PageEvent evt) {
		for (PageEventListener listener: pageEventListeners) {
			listener.pagePrinted(evt);
		}		
	}

	public BasicAppService(AppModel model) {
		super(null);
		this.model = model;
		this.model.addPropertyChangeListener("pageSetModel", pageSetModelChanged);
	}
}
