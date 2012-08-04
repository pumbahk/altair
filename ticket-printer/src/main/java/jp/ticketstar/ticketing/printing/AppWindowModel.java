package jp.ticketstar.ticketing.printing;

import java.beans.PropertyChangeListener;
import java.beans.PropertyChangeSupport;

import javax.swing.event.SwingPropertyChangeSupport;

public class AppWindowModel {
	PropertyChangeSupport propertyChangeSupport = new SwingPropertyChangeSupport(this, true);
	TicketSetModel ticketSetModel = null;

	public void addPropertyChangeListener(PropertyChangeListener arg0) {
		propertyChangeSupport.addPropertyChangeListener(arg0);
	}

	public void addPropertyChangeListener(String arg0,
			PropertyChangeListener arg1) {
		propertyChangeSupport.addPropertyChangeListener(arg0, arg1);
	}

	public PropertyChangeListener[] getPropertyChangeListeners() {
		return propertyChangeSupport.getPropertyChangeListeners();
	}

	public PropertyChangeListener[] getPropertyChangeListeners(String arg0) {
		return propertyChangeSupport.getPropertyChangeListeners(arg0);
	}

	public boolean hasListeners(String arg0) {
		return propertyChangeSupport.hasListeners(arg0);
	}

	public void removePropertyChangeListener(PropertyChangeListener arg0) {
		propertyChangeSupport.removePropertyChangeListener(arg0);
	}

	public void removePropertyChangeListener(String arg0,
			PropertyChangeListener arg1) {
		propertyChangeSupport.removePropertyChangeListener(arg0, arg1);
	}

	public TicketSetModel getTicketSetModel() {
		return ticketSetModel;
	}

	public void setTicketSetModel(TicketSetModel ticketSetModel) {
		final TicketSetModel prevValue = this.ticketSetModel;
		this.ticketSetModel = ticketSetModel;
		propertyChangeSupport.firePropertyChange("ticketSetModel", prevValue, ticketSetModel);
	}

	public void refresh() {
		propertyChangeSupport.firePropertyChange("ticketSetModel", ticketSetModel, ticketSetModel);
	}
	
	public AppWindowModel() {
	}
}
