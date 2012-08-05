package jp.ticketstar.ticketing.printing;


import javax.swing.ComboBoxModel;

public class GenericComboBoxModel<T> extends GenericListModel<T> implements ComboBoxModel {
	private static final long serialVersionUID = 1L;
	T selectedItem;
	
	public T getSelectedItem() {
		return selectedItem;
	}

	@SuppressWarnings("unchecked")
	public void setSelectedItem(Object item) {
		selectedItem = (T)item;
	}
}
