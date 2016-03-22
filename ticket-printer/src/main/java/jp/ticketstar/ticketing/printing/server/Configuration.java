package jp.ticketstar.ticketing.printing.server;

import java.util.List;

import jp.ticketstar.ticketing.printing.util.ProxyFactory;

public interface Configuration {
    public String getListen();
    public List<String> getOriginHosts();
    public long getGCInterval();
    public boolean getIgnoreWrongCert();
    public String getAuthString();
    public ProxyFactory getProxyFactory();
}