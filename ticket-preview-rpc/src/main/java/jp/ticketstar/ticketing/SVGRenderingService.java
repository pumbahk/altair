package jp.ticketstar.ticketing.svgrpc;
import java.net.URL;

public interface SVGRenderingService {
    URL renderSVG(String svg, String fetchURL) throws AppException;
    URL renderSVG(String svg, String fetchURL, String fileType) throws AppException;
    int inc(int x);
}