package jp.ticketstar.ticketing.printing.gui;

import java.awt.Component;

import javax.swing.DefaultListCellRenderer;
import javax.swing.JLabel;
import javax.swing.JList;

import jp.ticketstar.ticketing.printing.OurPageFormat;

class PageFormatCellRenderer extends DefaultListCellRenderer {
	private static final long serialVersionUID = 1L;

	@Override
	public Component getListCellRendererComponent(JList list, Object value, int index, boolean isSelected, boolean cellHasFocus) {
		JLabel label = (JLabel)super.getListCellRendererComponent(list, value, index, isSelected, cellHasFocus);
		if (value != null)
			label.setText(((OurPageFormat)value).getName());
		return label;
	}
}