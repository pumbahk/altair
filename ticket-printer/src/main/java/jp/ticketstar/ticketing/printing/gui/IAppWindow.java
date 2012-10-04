package jp.ticketstar.ticketing.printing.gui;

import java.awt.Container;

import jp.ticketstar.ticketing.printing.AppModel;

public interface IAppWindow {

	public abstract void unbind();

	public abstract void bind(AppModel model);

	public abstract Container getFrame();

	public abstract void show();

	public abstract void setInteractionEnabled(boolean enabled);
}