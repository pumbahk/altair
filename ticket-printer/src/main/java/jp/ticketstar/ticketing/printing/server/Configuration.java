package jp.ticketstar.ticketing.printing.server;

import java.util.List;

public interface Configuration {
    public String getListen();
    public List<String> getOriginHosts();
}