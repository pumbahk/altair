package jp.ticketstar.ticketing.printing.util;

import java.net.InetSocketAddress;
import java.net.Proxy;

import com.sun.jna.platform.win32.WinReg;
import com.sun.jna.platform.win32.WinReg.HKEY;

import static com.sun.jna.platform.win32.Advapi32Util.registryGetIntValue;
import static com.sun.jna.platform.win32.Advapi32Util.registryGetStringValue;
import static com.sun.jna.platform.win32.Advapi32Util.registryValueExists;

public class SystemConfiguration implements ProxyFactory {
	private static final HKEY root = WinReg.HKEY_CURRENT_USER;
	private static final String key = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Internet Settings";
	
	@SuppressWarnings("unused")
	private static boolean valueExists(String name) {
		return registryValueExists(root, key, name);
	}
	
	private static String getString(String name) {
		return registryGetStringValue(root, key, name);
	}
	
	private static int getInt(String name) {
		return registryGetIntValue(root, key, name);
	}
	
	private static SystemConfiguration instance = null;
	public static SystemConfiguration getInstance() {
		if (instance == null) {
			instance = new SystemConfiguration();
		}
		return instance;
	}
	
	public Proxy getProxy() {
		String proxyServerSetting = null;
		try {
			if (getInt("ProxyEnable") != 1) {
				return null;
			}
			proxyServerSetting = getString("ProxyServer");
		} catch(RuntimeException e) {
			return null;
		}
		String[] proxyServers = proxyServerSetting.split(";", -1);
		if (proxyServers.length == 0) {
			return null;
		}
		for(String p: proxyServers) {
			String[] elements = p.split(":", -1);
			if(elements.length == 3 && elements[0].startsWith("http") && elements[1].startsWith("//")) {
				return new Proxy(Proxy.Type.HTTP, new InetSocketAddress(elements[1].substring(2), Integer.parseInt(elements[2])));
			} else if(elements.length == 2 && elements[0].equals("http") && elements[1].startsWith("//")) {
				return new Proxy(Proxy.Type.HTTP, new InetSocketAddress(elements[1].substring(2), 80));
			} else if(elements.length == 2 && elements[1].matches("\\d+")) {
				return new Proxy(Proxy.Type.HTTP, new InetSocketAddress(elements[0], Integer.parseInt(elements[1])));
			} else if(elements.length == 1) {
				return new Proxy(Proxy.Type.HTTP, new InetSocketAddress(elements[0], 80));
			}
		}
		throw new RuntimeException("Unsupported proxy settings: " + proxyServerSetting);
	}
}
