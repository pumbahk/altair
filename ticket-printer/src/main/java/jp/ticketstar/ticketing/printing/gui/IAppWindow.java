package jp.ticketstar.ticketing.printing.gui;

import java.awt.Container;

import javax.swing.JFrame;

public interface IAppWindow {

	public abstract void unbind();

	public abstract void bind(AppWindowModel model);

	public abstract Container getFrame();

	public abstract void show();

}