package jp.ticketstar.ticketing.printing;

import jp.ticketstar.ticketing.printing.gui.AppWindowService;

import java.io.IOException;

import org.kohsuke.args4j.CmdLineException;
import org.kohsuke.args4j.CmdLineParser;

import jp.ticketstar.ticketing.printing.gui.AppWindow;
import jp.ticketstar.ticketing.printing.gui.AppWindowModel;
import jp.ticketstar.ticketing.printing.gui.IAppWindow;

public class App {
	public static void main(String[] args) {
        Server appServer = new Server();
        CmdLineParser parser = new CmdLineParser(appServer);
        try {
            parser.parseArgument(args);
        } catch (CmdLineException e) {
            e.printStackTrace();
            return;
        }

    	final AppWindowModel model = new AppWindowModel();
    	final AppWindowService appService = new AppWindowService(model);

        if(appServer.acceptConnection()) {
			appServer.setModel(model);
			appServer.setService(appService);

			try {
				appServer.start();
			} catch(IOException e) {
				e.printStackTrace();
			}
			return;
		}

        final IAppWindow appWindow = new AppWindow(appService);
        appWindow.show();
    }
}
