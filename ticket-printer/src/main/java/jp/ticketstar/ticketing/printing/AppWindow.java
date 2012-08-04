package jp.ticketstar.ticketing.printing;

import java.awt.CardLayout;
import java.awt.Component;
import java.awt.EventQueue;

import javax.swing.JFrame;
import java.awt.BorderLayout;

import javax.swing.DefaultListCellRenderer;
import javax.swing.JLabel;
import javax.swing.JToolBar;
import javax.swing.JButton;
import javax.swing.ImageIcon;
import javax.swing.JSplitPane;
import javax.swing.JList;

import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;
import java.awt.geom.Dimension2D;

import javax.swing.ListSelectionModel;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;

import java.awt.Dimension;
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;

import javax.swing.JPanel;

import jp.ticketstar.ticketing.printing.svg.JGVTComponent;

class TicketCellRenderer extends DefaultListCellRenderer {
	private static final long serialVersionUID = 1L;

	@Override
	public Component getListCellRendererComponent(JList list, Object value, int index, boolean isSelected, boolean cellHasFocus) {
		JLabel label = (JLabel)super.getListCellRendererComponent(list, value, index, isSelected, cellHasFocus);
		label.setText(((Ticket)value).getName());
		return label;
	}
}

public class AppWindow {
	AppService appService;
	AppWindowModel model;
	
	private JFrame frame;
	private JList list;
	private JPanel panel;
	
	private PropertyChangeListener ticketSetModelChangeListener = new PropertyChangeListener() {
		public void propertyChange(PropertyChangeEvent evt) {
			if (evt.getNewValue() != null) {
				final TicketSetModel ticketSetModel = (TicketSetModel)evt.getNewValue();
				panel.removeAll();
				for (Ticket ticket: ticketSetModel.getTickets()) {
					final JGVTComponent gvtComponent = new JGVTComponent(false, false);
					final Dimension2D documentSize = ticketSetModel.getBridgeContext().getDocumentSize();
					gvtComponent.setSize(new Dimension((int)documentSize.getWidth(), (int)documentSize.getHeight()));
					gvtComponent.setGraphicsNode(ticket.getGraphics());
					panel.add(gvtComponent, ticket.getName());
				}
				list.setModel(ticketSetModel.getTickets());
			}
		}
	};

	/**
	 * Create the application.
	 */
	public AppWindow(AppService appService) {
		this.appService = appService;
		appService.setAppWindow(this);
		initialize();
	}

	public void unbind() {
		if (model == null)
			return;

		model.removePropertyChangeListener(ticketSetModelChangeListener);
	}
	
	public void bind(AppWindowModel model) {
		unbind();
		model.addPropertyChangeListener("ticketSetModel", ticketSetModelChangeListener);
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
		
		JSplitPane splitPane = new JSplitPane();
		frame.getContentPane().add(splitPane, BorderLayout.CENTER);
		
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

	public JFrame getFrame() {
		return frame;
	}
	
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