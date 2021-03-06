package jp.ticketstar.ticketing.printing.gui;

import java.awt.Component;

import javax.print.PrintService;
import javax.swing.DefaultListCellRenderer;
import javax.swing.JLabel;
import javax.swing.JList;

class PrintServiceCellRenderer extends DefaultListCellRenderer {
    private static final long serialVersionUID = 1L;

    @Override
    public Component getListCellRendererComponent(JList list, Object value, int index, boolean isSelected, boolean cellHasFocus) {
        JLabel label = (JLabel)super.getListCellRendererComponent(list, value, index, isSelected, cellHasFocus);
        if (value != null)
            label.setText(((PrintService)value).getName());
        return label;
    }
}