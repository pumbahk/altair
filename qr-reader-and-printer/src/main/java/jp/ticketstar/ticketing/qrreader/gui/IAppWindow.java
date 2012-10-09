package jp.ticketstar.ticketing.qrreader.gui;

import jp.ticketstar.ticketing.qrreader.AppModel;

public interface IAppWindow {

	public abstract void unbind();

	public abstract void bind(AppModel model);

	public abstract void show();

}
