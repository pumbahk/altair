package jp.ticketstar.ticketing.printing.gui;

import java.awt.CardLayout;
import java.awt.Component;
import java.awt.Container;
import java.awt.EventQueue;

import javax.print.PrintService;
import javax.swing.JFrame;
import java.awt.BorderLayout;

import javax.swing.JToolBar;
import javax.swing.JButton;
import javax.swing.ImageIcon;
import javax.swing.JSplitPane;
import javax.swing.JList;

import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;
import java.awt.event.ComponentEvent;
import java.awt.event.ComponentListener;
import java.awt.event.ItemEvent;
import java.awt.event.ItemListener;
import java.awt.geom.AffineTransform;
import java.awt.geom.Dimension2D;

import javax.swing.ListSelectionModel;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;

import java.awt.Dimension;
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.util.Collection;

import javax.swing.JPanel;

import javax.swing.JComboBox;

import jp.ticketstar.ticketing.swing.GenericComboBoxModel;
import jp.ticketstar.ticketing.printing.AppService;
import jp.ticketstar.ticketing.printing.BoundingBoxOverlay;
import jp.ticketstar.ticketing.printing.GuidesOverlay;
import jp.ticketstar.ticketing.printing.AppModel;
import jp.ticketstar.ticketing.printing.JGVTComponent;
import jp.ticketstar.ticketing.printing.OurPageFormat;
import jp.ticketstar.ticketing.printing.Page;
import jp.ticketstar.ticketing.printing.PageSetModel;

import org.apache.batik.swing.gvt.Overlay;

public class AppWindow implements IAppWindow {
	AppService appService;
	AppModel model;
	
	private JFrame frame;
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

		public void componentShown(ComponentEvent e) {}
	};
	
	private PropertyChangeListener ticketSetModelChangeListener = new PropertyChangeListener() {
		@SuppressWarnings("unchecked")
		public void propertyChange(PropertyChangeEvent evt) {
			if (evt.getNewValue() != null) {
				list.clearSelection();
				final PageSetModel ticketSetModel = (PageSetModel)evt.getNewValue();
				panel.removeAll();
				for (Page ticket: ticketSetModel.getPages()) {
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
				list.setModel(ticketSetModel.getPages());
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
				if (printServices.size() > 0)
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
				if (pageFormats.size() > 0)
					comboBoxPageFormat.setSelectedIndex(0);
			}
		}
	};
	private JButton btnPrint;
	private JComboBox comboBoxPrintService;
	private JComboBox comboBoxPageFormat;

	/**
	 * Create the application.
	 */
	public AppWindow(AppService appService) {
		this.appService = appService;
		initialize();
		appService.setAppWindow(this);
		guidesOverlay = new GuidesOverlay(model);
		boundingBoxOverlay = new BoundingBoxOverlay(model);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindow#unbind()
	 */
	public void unbind() {
		if (model == null)
			return;

		model.removePropertyChangeListener(ticketSetModelChangeListener);
		model.removePropertyChangeListener(printServicesChangeListener);
		model.removePropertyChangeListener(printServiceChangeListener);
		model.removePropertyChangeListener(pageFormatsChangeListener);
		model.removePropertyChangeListener(pageFormatChangeListener);
	}
	
	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindow#bind(jp.ticketstar.ticketing.printing.gui.AppWindowModel)
	 */
	public void bind(AppModel model) {
		unbind();
		model.addPropertyChangeListener("ticketSetModel", ticketSetModelChangeListener);
		model.addPropertyChangeListener("printServices", printServicesChangeListener);
		model.addPropertyChangeListener("printService", printServiceChangeListener);
		model.addPropertyChangeListener("pageFormats", pageFormatsChangeListener);
		model.addPropertyChangeListener("pageFormat", pageFormatChangeListener);
		model.refresh();
		this.model = model;
	}

	/**
	 * Initialize the contents of the frame.
	 */
	private void initialize() {
		frame = new JFrame();
		frame.setBounds(100, 100, 450, 300);
		frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		frame.getContentPane().setLayout(new BorderLayout(0, 0));
		
		JToolBar toolBar = new JToolBar();
		frame.getContentPane().add(toolBar, BorderLayout.NORTH);
		
		JButton btnOpen = new JButton("Open");
		btnOpen.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				appService.openFileDialog();
			}
		});
		btnOpen.setIcon(new ImageIcon(AppWindow.class.getResource("/toolbarButtonGraphics/general/Open24.gif")));
		toolBar.add(btnOpen);
		
		btnPrint = new JButton("Print");
		btnPrint.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				appService.printAll();
			}
		});
		btnPrint.setIcon(new ImageIcon(AppWindow.class.getResource("/toolbarButtonGraphics/general/Print24.gif")));
		toolBar.add(btnPrint);
		
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
		
		JSplitPane splitPane = new JSplitPane();
		frame.getContentPane().add(splitPane, BorderLayout.CENTER);
		
		list = new JList();
		list.setPreferredSize(new Dimension(128, 0));
		list.setRequestFocusEnabled(false);
		list.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
		list.setCellRenderer(new TicketCellRenderer());
		list.addListSelectionListener(new ListSelectionListener() {
			public void valueChanged(ListSelectionEvent arg0) {
				((CardLayout)panel.getLayout()).show(panel, ((Page)((JList)arg0.getSource()).getSelectedValue()).getName());
			}
		});
		splitPane.setLeftComponent(list);
		
		panel = new JPanel();
		panel.setLayout(new CardLayout());
		splitPane.setRightComponent(panel);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindow#getFrame()
	 */
	public Container getFrame() {
		return frame;
	}
	
	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindow#show()
	 */
	public void show() {
		EventQueue.invokeLater(new Runnable() {
			public void run() {
				try {
					frame.setVisible(true);
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		});
	}
}