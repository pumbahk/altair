package jp.ticketstar.sej;

import py4j.GatewayServer;

/**
 * Created with IntelliJ IDEA.
 * User: mistat
 * Date: 4/19/12
 * Time: 9:36 PM
 * To change this template use File | Settings | File Templates.
 */
public class Gateway {

    public static void main(String[] args) {
        GatewayServer server = new GatewayServer(new Gateway());
        server.start();
        System.out.println("Gateway Server Started");
    }

}
