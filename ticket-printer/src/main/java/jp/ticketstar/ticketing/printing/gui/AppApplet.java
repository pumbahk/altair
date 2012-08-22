package jp.ticketstar.ticketing.printing.gui;

import java.awt.BorderLayout;
import java.awt.Button;
import java.awt.CardLayout;
import java.awt.Component;
import java.awt.Container;
import java.awt.Dimension;
import java.awt.EventQueue;
import java.awt.Graphics;
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
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.net.URI;
import java.net.URL;
import java.util.Collection;

import javax.print.PrintService;
import javax.swing.ImageIcon;
import javax.swing.JApplet;
import javax.swing.JButton;
import javax.swing.JComboBox;
import javax.swing.JFrame;
import javax.swing.JList;
import javax.swing.JPanel;
import javax.swing.JSplitPane;
import javax.swing.JToolBar;
import javax.swing.ListSelectionModel;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;

import jp.ticketstar.ticketing.printing.AppService;
import jp.ticketstar.ticketing.printing.BoundingBoxOverlay;
import jp.ticketstar.ticketing.printing.GenericComboBoxModel;
import jp.ticketstar.ticketing.printing.GuidesOverlay;
import jp.ticketstar.ticketing.printing.JGVTComponent;
import jp.ticketstar.ticketing.printing.OurPageFormat;
import jp.ticketstar.ticketing.printing.Ticket;
import jp.ticketstar.ticketing.printing.TicketSetModel;

import org.apache.batik.swing.gvt.Overlay;
import org.apache.commons.io.IOUtils;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
  
/**
 * Created with IntelliJ IDEA.
 * User: mistat
 * Date: 8/9/12
 * Time: 10:00 PM
 * To change this template use File | Settings | File Templates.
 */
public class AppApplet extends JApplet implements IAppWindow  {
	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;

	public AppApplet() {
	}
	
	AppService appService;
	AppWindowModel model;
	
	//private JApplet frame;
	private JList list;
	private JPanel panel;

	private GuidesOverlay guidesOverlay;
	private BoundingBoxOverlay boundingBoxOverlay;
	private ComponentListener centeringListener = new ComponentListener() {
		public void componentHidden(ComponentEvent e) {}

		public void componentMoved(ComponentEvent e) {}

		public void componentResized(ComponentEvent e) {
			final Dimension2D documentSize = model.getTicketSetModel().getBridgeContext().getDocumentSize();
			final JGVTComponent source = (JGVTComponent)e.getSource();
			double ox = Math.max(0, (source.getWidth() - documentSize.getWidth()) / 2),
				   oy = Math.max(0, (source.getHeight() - documentSize.getHeight()) / 2);
			source.setPaintingTransform(new AffineTransform(1, 0, 0, 1, ox, oy));
		}

		public void componentShown(ComponentEvent e) {}
	};
	
	private PropertyChangeListener ticketSetModelChangeListener = new PropertyChangeListener() {
		@SuppressWarnings("unchecked")
		public void propertyChange(PropertyChangeEvent evt) {
			if (evt.getNewValue() != null) {
				list.clearSelection();
				final TicketSetModel ticketSetModel = (TicketSetModel)evt.getNewValue();
				panel.removeAll();
				for (Ticket ticket: ticketSetModel.getTickets()) {
					final JGVTComponent gvtComponent = new JGVTComponent(false, false);
					final Dimension2D documentSize = ticketSetModel.getBridgeContext().getDocumentSize();
					{
						Collection<Overlay> overlays = gvtComponent.getOverlays();
						overlays.add(guidesOverlay);
						overlays.add(boundingBoxOverlay);
					}
					gvtComponent.setPageFormat(model.getPageFormat());
					gvtComponent.addComponentListener(centeringListener);
					gvtComponent.setSize(new Dimension((int)documentSize.getWidth(), (int)documentSize.getHeight()));
					gvtComponent.setGraphicsNode(ticket.getGraphics());
					panel.add(gvtComponent, ticket.getName());
				}
				panel.doLayout();
				list.setModel(ticketSetModel.getTickets());
			}
		}
	};
	private PropertyChangeListener printServiceChangeListener = new PropertyChangeListener() {
		public void propertyChange(PropertyChangeEvent evt) {
			if (evt.getNewValue() != null) {
				PrintService printService = (PrintService)evt.getNewValue();
				comboBoxPrintService.setSelectedItem(printService);
			}
		}
	};
	private PropertyChangeListener printServicesChangeListener = new PropertyChangeListener() {
		public void propertyChange(PropertyChangeEvent evt) {
			if (evt.getNewValue() != null) {
				@SuppressWarnings("unchecked")
				GenericComboBoxModel<PrintService> printServices = (GenericComboBoxModel<PrintService>)evt.getNewValue();
				comboBoxPrintService.setModel(printServices);
				comboBoxPrintService.setSelectedIndex(0);
			}
		}
	};
	private PropertyChangeListener pageFormatChangeListener = new PropertyChangeListener() {
		public void propertyChange(PropertyChangeEvent evt) {
			if (evt.getNewValue() != null) {
				OurPageFormat pageFormat = (OurPageFormat)evt.getNewValue();
				comboBoxPageFormat.setSelectedItem(pageFormat);
				for (Component c: panel.getComponents())
					((JGVTComponent)c).setPageFormat(model.getPageFormat());
				panel.paintImmediately(0, 0, (int)panel.getSize().getWidth(), (int)panel.getSize().getHeight());
			}
		}
	};
	private PropertyChangeListener pageFormatsChangeListener = new PropertyChangeListener() {
		public void propertyChange(PropertyChangeEvent evt) {
			if (evt.getNewValue() != null) {
				@SuppressWarnings("unchecked")
				GenericComboBoxModel<OurPageFormat> pageFormats = (GenericComboBoxModel<OurPageFormat>)evt.getNewValue();
				comboBoxPageFormat.setModel(pageFormats);
				comboBoxPageFormat.setSelectedIndex(0);
			}
		}
	};
	private JButton btnPrint;
	private JComboBox comboBoxPrintService;
	private JComboBox comboBoxPageFormat;

	public void unbind() {
		if (model == null)
			return;

		model.removePropertyChangeListener(ticketSetModelChangeListener);
		model.removePropertyChangeListener(printServicesChangeListener);
		model.removePropertyChangeListener(printServiceChangeListener);
		model.removePropertyChangeListener(pageFormatsChangeListener);
		model.removePropertyChangeListener(pageFormatChangeListener);
	}
	
	public void bind(AppWindowModel model) {
		unbind();
		model.addPropertyChangeListener("ticketSetModel", ticketSetModelChangeListener);
		model.addPropertyChangeListener("printServices", printServicesChangeListener);
		model.addPropertyChangeListener("printService", printServiceChangeListener);
		model.addPropertyChangeListener("pageFormats", pageFormatsChangeListener);
		model.addPropertyChangeListener("pageFormat", pageFormatChangeListener);
		model.refresh();
		this.model = model;
	}
	
	public  void init () {
		
    	model = new AppWindowModel();
    	appService = new AppService(model);
		initialize();
    	
		appService.setAppWindow(this);
		guidesOverlay = new GuidesOverlay(model);
		boundingBoxOverlay = new BoundingBoxOverlay(model);
		
		String  queueApiUrl = getParameter("queueApiUrl");  
		if (queueApiUrl == null) {
			queueApiUrl = "http://0.0.0.0:7654/tickets/print/dequeue";
		}
		String params = "";
		
		appService.loadFromApi(queueApiUrl, params);

	}
	/**
	 * Initialize the contents of the frame.
	 */
	private void initialize() {
		this.setBounds(0, 0, 640, 300);
		this.getContentPane().setLayout(new BorderLayout(0, 0));
		
		JToolBar toolBar = new JToolBar();
		this.getContentPane().add(toolBar, BorderLayout.NORTH);
		
		comboBoxPrintService = new JComboBox();
		comboBoxPrintService.setRenderer(new PrintServiceCellRenderer());
		comboBoxPrintService.addItemListener(new ItemListener() {
			public void itemStateChanged(ItemEvent e) {
				model.setPrintService((PrintService)e.getItem());
			}
		});
		toolBar.add(comboBoxPrintService);
		
		comboBoxPageFormat = new JComboBox();
		comboBoxPageFormat.setRenderer(new PageFormatCellRenderer());
		comboBoxPageFormat.addItemListener(new ItemListener() {
			public void itemStateChanged(ItemEvent e) {
				model.setPageFormat((OurPageFormat)e.getItem());
			}
		});
		toolBar.add(comboBoxPageFormat);
		
		btnPrint = new JButton("印刷");
		btnPrint.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				appService.printAll();
			}
		});
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
				((CardLayout)panel.getLayout()).show(panel, ((Ticket)((JList)arg0.getSource()).getSelectedValue()).getName());
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

	
}
