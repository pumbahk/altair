package jp.ticketstar.ticketing.printing.gui;

import java.io.IOException;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.net.URL;
import java.net.URLConnection;
import java.awt.BorderLayout;
import java.awt.CardLayout;
import java.awt.Component;
import java.awt.Container;
import java.awt.Dimension;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.ComponentEvent;
import java.awt.event.ComponentListener;
import java.awt.event.ItemEvent;
import java.awt.event.ItemListener;
import java.awt.geom.AffineTransform;
import java.awt.geom.Dimension2D;
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.util.Collection;

import javax.print.PrintService;
import javax.swing.ImageIcon;
import javax.swing.JApplet;
import javax.swing.JButton;
import javax.swing.JComboBox;
import javax.swing.JList;
import javax.swing.JPanel;
import javax.swing.JSplitPane;
import javax.swing.JToolBar;
import javax.swing.ListSelectionModel;
import javax.swing.SwingUtilities;
import javax.swing.event.ListDataEvent;
import javax.swing.event.ListDataListener;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;

import jp.ticketstar.ticketing.printing.ApplicationException;
import jp.ticketstar.ticketing.printing.BoundingBoxOverlay;
import jp.ticketstar.ticketing.printing.GenericComboBoxModel;
import jp.ticketstar.ticketing.printing.GuidesOverlay;
import jp.ticketstar.ticketing.printing.AppModel;
import jp.ticketstar.ticketing.printing.JGVTComponent;
import jp.ticketstar.ticketing.printing.OurPageFormat;
import jp.ticketstar.ticketing.printing.Page;
import jp.ticketstar.ticketing.printing.PageSetModel;
import jp.ticketstar.ticketing.printing.RequestBodySender;
import jp.ticketstar.ticketing.printing.StandardAppService;
import jp.ticketstar.ticketing.printing.TicketFormat;
import jp.ticketstar.ticketing.printing.URLConnectionFactory;
import jp.ticketstar.ticketing.printing.gui.liveconnect.JSObjectPropertyChangeListenerProxy;

import netscape.javascript.JSObject;

import org.apache.batik.swing.gvt.Overlay;

import com.google.gson.JsonElement;
import com.google.gson.JsonParser;
import com.google.gson.stream.JsonWriter;
import javax.swing.JSeparator;
import javax.swing.SwingConstants;

/**
 * Created with IntelliJ IDEA.
 * User: mistat
 * Date: 8/9/12
 * Time: 10:00 PM
 * To change this template use File | Settings | File Templates.
 */
public class AppApplet extends JApplet implements IAppWindow, URLConnectionFactory {
	private static final long serialVersionUID = 1L;

	protected AppAppletService appService;
	protected AppAppletModel model;
	protected AppAppletConfiguration config;

	//private JApplet frame;
	private JList list;
	private JPanel panel;

	private GuidesOverlay guidesOverlay;
	private BoundingBoxOverlay boundingBoxOverlay;
	
	private ComponentListener centeringListener = new ComponentListener() {
		public void componentHidden(ComponentEvent e) {}

		public void componentMoved(ComponentEvent e) {}

		public void componentResized(ComponentEvent e) {
			final Dimension2D documentSize = model.getPageSetModel().getBridgeContext().getDocumentSize();
			final JGVTComponent source = (JGVTComponent)e.getSource();
			double ox = Math.max(0, (source.getWidth() - documentSize.getWidth()) / 2),
				   oy = Math.max(0, (source.getHeight() - documentSize.getHeight()) / 2);
			source.setPaintingTransform(new AffineTransform(1, 0, 0, 1, ox, oy));
		}

		public void componentShown(ComponentEvent e) {
			componentResized(e);
		}
	};
	
	private PropertyChangeListener pageSetModelChangeListener = new PropertyChangeListener() {
		@SuppressWarnings("unchecked")
		public void propertyChange(PropertyChangeEvent evt) {
			if (evt.getNewValue() != null) {
				if (list != null)
					list.clearSelection();
				final PageSetModel pageSetModel = (PageSetModel)evt.getNewValue();
				SwingUtilities.invokeLater(new Runnable() {
					public void run() {
						if (panel != null) {
							panel.removeAll();
							for (Page page: pageSetModel.getPages()) {
								final JGVTComponent gvtComponent = new JGVTComponent(false, false);
								{
									Collection<Overlay> overlays = gvtComponent.getOverlays();
									overlays.add(guidesOverlay);
									overlays.add(boundingBoxOverlay);
								}
								gvtComponent.setPageFormat(model.getPageFormat());
								gvtComponent.addComponentListener(centeringListener);
								gvtComponent.setSize(new Dimension((int)panel.getWidth(), (int)panel.getHeight()));
								gvtComponent.setGraphicsNode(page.getGraphics());
								gvtComponent.setName(page.getName());
								panel.add(gvtComponent, page.getName());
							}
							panel.validate();
						}
						if (list != null)
							list.setModel(pageSetModel.getPages());
					}
				});
				pageSetModel.getPages().addListDataListener(new ListDataListener() {
					public void contentsChanged(ListDataEvent evt) {}

					public void intervalAdded(ListDataEvent evt) {}

					public void intervalRemoved(ListDataEvent evt) {
						final Component[] pageComponents = panel.getComponents();
						for (int i = evt.getIndex0(), j = evt.getIndex1(); i <= j; i++) {
							panel.remove(pageComponents[i]);
						}
						panel.validate();
					}
				});
			}
		}
	};
	
	private PropertyChangeListener printServiceChangeListener = new PropertyChangeListener() {
		public void propertyChange(PropertyChangeEvent evt) {
			if (evt.getNewValue() != null) {
				if (comboBoxPrintService != null) {
					PrintService printService = (PrintService)evt.getNewValue();
					comboBoxPrintService.setSelectedItem(printService);
				}
			}
		}
	};
	private PropertyChangeListener printServicesChangeListener = new PropertyChangeListener() {
		public void propertyChange(PropertyChangeEvent evt) {
			if (evt.getNewValue() != null) {
				if (comboBoxPrintService != null) {
					@SuppressWarnings("unchecked")
					GenericComboBoxModel<PrintService> printServices = (GenericComboBoxModel<PrintService>)evt.getNewValue();
					comboBoxPrintService.setModel(printServices);
					if (printServices.size() > 0)
						comboBoxPrintService.setSelectedIndex(0);
				}
			}
		}
	};
	private PropertyChangeListener pageFormatChangeListener = new PropertyChangeListener() {
		public void propertyChange(PropertyChangeEvent evt) {
			if (evt.getNewValue() != null) {
				doLoadTicketData();
				final OurPageFormat pageFormat = (OurPageFormat)evt.getNewValue();
				for (final PrintService printService: model.getPrintServices()) {
					if (printService.getName().equals(pageFormat.getPreferredPrinterName())) {
						model.setPrintService(printService);
						break;
					}
				}
				if (comboBoxPageFormat != null)
					comboBoxPageFormat.setSelectedItem(pageFormat);
			}
		}
	};
	private PropertyChangeListener pageFormatsChangeListener = new PropertyChangeListener() {
		public void propertyChange(PropertyChangeEvent evt) {
			if (evt.getNewValue() != null) {
				@SuppressWarnings("unchecked")
				GenericComboBoxModel<OurPageFormat> pageFormats = (GenericComboBoxModel<OurPageFormat>)evt.getNewValue();
				if (comboBoxPageFormat != null) {
					comboBoxPageFormat.setModel(pageFormats);
					if (pageFormats.size() > 0)
						comboBoxPageFormat.setSelectedIndex(0);
				}
			}
		}
	};
	private PropertyChangeListener ticketFormatChangeListener = new PropertyChangeListener() {
		public void propertyChange(PropertyChangeEvent evt) {
			if (evt.getNewValue() != null) {
				doLoadTicketData();
				if (comboBoxTicketFormat != null) {
					final TicketFormat ticketFormat = (TicketFormat)evt.getNewValue();
					comboBoxTicketFormat.setSelectedItem(ticketFormat);
				}
			}
		}
	};
	private PropertyChangeListener ticketFormatsChangeListener = new PropertyChangeListener() {
		public void propertyChange(PropertyChangeEvent evt) {
			if (evt.getNewValue() != null) {
				if (comboBoxTicketFormat != null) {
					@SuppressWarnings("unchecked")
					GenericComboBoxModel<TicketFormat> ticketFormats = (GenericComboBoxModel<TicketFormat>)evt.getNewValue();
					comboBoxTicketFormat.setModel(ticketFormats);
					if (ticketFormats.size() > 0)
						comboBoxTicketFormat.setSelectedIndex(0);
				}
			}
		}
	};
	private JButton btnPrint;
	private JComboBox comboBoxPrintService;
	private JComboBox comboBoxPageFormat;
	private JComboBox comboBoxTicketFormat;
	private JSeparator separator;

	public void unbind() {
		if (model == null)
			return;

		model.removePropertyChangeListener(pageSetModelChangeListener);
		model.removePropertyChangeListener(printServicesChangeListener);
		model.removePropertyChangeListener(printServiceChangeListener);
		model.removePropertyChangeListener(pageFormatsChangeListener);
		model.removePropertyChangeListener(pageFormatChangeListener);
		model.removePropertyChangeListener(ticketFormatsChangeListener);
		model.removePropertyChangeListener(ticketFormatChangeListener);
	}
	
	public void bind(AppModel model) {
		unbind();
		model.addPropertyChangeListener("pageSetModel", pageSetModelChangeListener);
		model.addPropertyChangeListener("printServices", printServicesChangeListener);
		model.addPropertyChangeListener("printService", printServiceChangeListener);
		model.addPropertyChangeListener("pageFormats", pageFormatsChangeListener);
		model.addPropertyChangeListener("pageFormat", pageFormatChangeListener);
		model.addPropertyChangeListener("ticketFormats", ticketFormatsChangeListener);
		model.addPropertyChangeListener("ticketFormat", ticketFormatChangeListener);
		model.refresh();
		this.model = (AppAppletModel)model;
	}

	private AppAppletConfiguration getConfiguration() throws ApplicationException {
		final AppAppletConfiguration config = new AppAppletConfiguration();
		final String endpointsJson = getParameter("endpoints");
		if (endpointsJson == null)
			throw new ApplicationException("required parameter \"endpoints\" not specified");
		final String cookie = getParameter("cookie");
		if (cookie == null)
			throw new ApplicationException("required parameter \"cookie\" not specified");
		final String embedded = getParameter("embedded");
		config.cookie = cookie;
		config.embedded = embedded == null ? false: Boolean.valueOf(embedded);
		config.callback = getParameter("callback");
		try {
			final JsonElement elem = new JsonParser().parse(endpointsJson);
			config.formatsUrl = new URL(getCodeBase(), elem.getAsJsonObject().get("formats").getAsString());
			config.peekUrl = new URL(getCodeBase(), elem.getAsJsonObject().get("peek").getAsString());
			config.dequeueUrl = new URL(getCodeBase(), elem.getAsJsonObject().get("dequeue").getAsString());
		} catch (Exception e) {
			throw new ApplicationException(e);
		}
		return config;
	}

	public StandardAppService getService() {
		return appService;
	}
	
	public URLConnection newURLConnection(final URL url) throws IOException {
		URLConnection conn = url.openConnection();
		conn.setRequestProperty("Cookie", config.cookie);
		conn.setUseCaches(false);
		conn.setAllowUserInteraction(true);
		return conn;
	}

	protected void populateModel() {
		final FormatLoader.FormatPair formatPair = new FormatLoader(this).fetchFormats(config);
		if (formatPair.pageFormats.size() > 0) {
			model.getPageFormats().addAll(formatPair.pageFormats);
			model.setPageFormat(formatPair.pageFormats.get(0));
		}
		if (formatPair.ticketFormats.size() > 0) {
			model.getTicketFormats().addAll(formatPair.ticketFormats);
			model.setTicketFormat(formatPair.ticketFormats.get(0));
		}
	}

	protected void doLoadTicketData() {
		try {
			final URLConnection conn = newURLConnection(config.peekUrl);
			appService.loadDocument(conn, new RequestBodySender() {
				public String getRequestMethod() {
					return "POST";
				}
				public void send(OutputStream out) throws IOException {
					final JsonWriter writer = new JsonWriter(new OutputStreamWriter(out, "utf-8"));
					writer.beginObject();
					writer.name("ticket_format_id");
					writer.value(model.getTicketFormat().getId());
					writer.name("page_format_id");
					writer.value(model.getPageFormat().getId());
					writer.endObject();
					writer.flush();
					writer.close();
				}
			});
		} catch (IOException e) {
			throw new ApplicationException(e);
		}
	}

	public void init() {
		config = getConfiguration();
		model = new AppAppletModel();
    	appService = new AppAppletService(this, model);
    	
		if (!config.embedded) {
			initialize();
			guidesOverlay = new GuidesOverlay(model);
			boundingBoxOverlay = new BoundingBoxOverlay(model);
		}
		
		appService.setAppWindow(this);
		populateModel();

		if (config.callback != null) {
			try {
				JSObject.getWindow(this).call(config.callback, new Object[] { this });
			} catch (Exception e) {
				// any exception from the JS callback will be silently ignored.
				e.printStackTrace(System.err);
			}
		}
	}
	/**
	 * Initialize the contents of the frame.
	 */
	private void initialize() {
		this.getContentPane().setLayout(new BorderLayout(0, 0));
		
		JToolBar toolBar = new JToolBar();
		toolBar.setFloatable(false);
		this.getContentPane().add(toolBar, BorderLayout.NORTH);
		
		comboBoxPageFormat = new JComboBox();
		comboBoxPageFormat.setRenderer(new PageFormatCellRenderer());
		comboBoxPageFormat.addItemListener(new ItemListener() {
			public void itemStateChanged(ItemEvent e) {
				model.setPageFormat((OurPageFormat)e.getItem());
			}
		});
		toolBar.add(comboBoxPageFormat);
		
		comboBoxTicketFormat = new JComboBox();
		comboBoxTicketFormat.setRenderer(new TicketFormatCellRenderer());
		comboBoxTicketFormat.addItemListener(new ItemListener() {
			public void itemStateChanged(ItemEvent e) {
				model.setTicketFormat((TicketFormat)e.getItem());
			}
		});
		toolBar.add(comboBoxTicketFormat);
		
		btnPrint = new JButton("印刷");
		btnPrint.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				appService.printAll();
			}
		});
		
		comboBoxPrintService = new JComboBox();
		comboBoxPrintService.setRenderer(new PrintServiceCellRenderer());
		comboBoxPrintService.addItemListener(new ItemListener() {
			public void itemStateChanged(ItemEvent e) {
				model.setPrintService((PrintService)e.getItem());
			}
		});
		
		separator = new JSeparator();
		separator.setMaximumSize(new Dimension(4, 32767));
		separator.setOrientation(SwingConstants.VERTICAL);
		toolBar.add(separator);
		toolBar.add(comboBoxPrintService);
		btnPrint.setIcon(new ImageIcon(AppWindow.class.getResource("/toolbarButtonGraphics/general/Print24.gif")));
		toolBar.add(btnPrint);
		
		JSplitPane splitPane = new JSplitPane();
		this.getContentPane().add(splitPane, BorderLayout.CENTER);
		
		list = new JList();
		list.setPreferredSize(new Dimension(128, 0));
		list.setRequestFocusEnabled(false);
		list.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
		list.setCellRenderer(new TicketCellRenderer());
		list.addListSelectionListener(new ListSelectionListener() {
			public void valueChanged(ListSelectionEvent arg0) {
				final Page page = (Page)((JList)arg0.getSource()).getSelectedValue();
				if (page != null)
					((CardLayout)panel.getLayout()).show(panel, page.getName());
			}
		});
		splitPane.setLeftComponent(list);
		
		panel = new JPanel();
		panel.setLayout(new CardLayout());
		splitPane.setRightComponent(panel);
	}

	public Container getFrame() {
		return this;
	}

	public static PropertyChangeListener createPropertyChangeListenerProxy(JSObject jsobj) {
		return new JSObjectPropertyChangeListenerProxy(jsobj);
	}
	
	public AppApplet() {
		setPreferredSize(new Dimension(2147483647, 2147483647));
	}
}
