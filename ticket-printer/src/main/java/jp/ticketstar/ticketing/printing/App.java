package jp.ticketstar.ticketing.printing;

import jp.ticketstar.ticketing.printing.gui.AppWindowService;
import jp.ticketstar.ticketing.printing.gui.AppWindow;
import jp.ticketstar.ticketing.printing.gui.AppWindowModel;
import jp.ticketstar.ticketing.printing.gui.IAppWindow;

public class App {
	public static void main(String[] args) {
    	final AppWindowModel model = new AppWindowModel();
    	final AppWindowService appService = new AppWindowService(model);
    	final IAppWindow appWindow = new AppWindow(appService);
    	appWindow.show();
    }
}
