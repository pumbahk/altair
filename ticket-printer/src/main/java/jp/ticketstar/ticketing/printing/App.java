package jp.ticketstar.ticketing.printing;

import java.util.ArrayList;
import java.util.List;

import jp.ticketstar.ticketing.printing.gui.AppWindowService;

import org.kohsuke.args4j.CmdLineException;
import org.kohsuke.args4j.CmdLineParser;
import org.kohsuke.args4j.Option;

import jp.ticketstar.ticketing.printing.gui.AppWindow;
import jp.ticketstar.ticketing.printing.gui.AppWindowModel;
import jp.ticketstar.ticketing.printing.gui.IAppWindow;
import jp.ticketstar.ticketing.printing.server.Server;

public class App {
    static class Configuration implements jp.ticketstar.ticketing.printing.server.Configuration { 
        @Option(name="--server")
        boolean acceptConnection = false;

        @Option(name="--listen")
        String listen = "127.0.0.1:8081";
        
        @Option(name="--origin")
        List<String> originHosts = new ArrayList<String>();

        public boolean isAcceptConnection() {
            return acceptConnection;
        }

        @Override
        public String getListen() {
            return listen;
        }

        @Override
        public List<String> getOriginHosts() {
            return originHosts;
        }
    }

    public static void main(String[] args) {
        Configuration config = new Configuration();
        final CmdLineParser parser = new CmdLineParser(config);
        try {
            parser.parseArgument(args);
        } catch (CmdLineException e) {
            e.printStackTrace();
            return;
        }

        final Server appServer = new Server(config);
        final AppWindowModel model = new AppWindowModel();
        final AppWindowService appService = new AppWindowService(model);

        if (config.isAcceptConnection()) {
            appServer.setService(appService);
            appServer.run();
        } else {
            final IAppWindow appWindow = new AppWindow(appService);
            appWindow.show();
        }
    }
}
