package jp.ticketstar.ticketing.printing;

/**
 * Hello world!
 *
 */
public class App {
	public static void main(String[] args) {
    	final AppWindowModel model = new AppWindowModel();
    	final AppService appService = new AppService(model);
    	final AppWindow appWindow = new AppWindow(appService);
    	appWindow.show();
    }
}
