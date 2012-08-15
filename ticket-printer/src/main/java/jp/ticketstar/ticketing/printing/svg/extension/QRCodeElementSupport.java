package jp.ticketstar.ticketing.printing.svg.extension;

import org.w3c.dom.DOMException;

import com.google.common.collect.BiMap;
import com.google.common.collect.EnumHashBiMap;
import com.google.zxing.qrcode.decoder.ErrorCorrectionLevel;

public class QRCodeElementSupport {
	static final BiMap<ErrorCorrectionLevel, String> ecLevelNameMap = buildECLevelNameMap();

	static BiMap<ErrorCorrectionLevel, String> buildECLevelNameMap() {
		BiMap<ErrorCorrectionLevel, String> retval = EnumHashBiMap.create(ErrorCorrectionLevel.class);
		retval.put(ErrorCorrectionLevel.H, "h");
		retval.put(ErrorCorrectionLevel.L, "l");
		retval.put(ErrorCorrectionLevel.M, "m");
		retval.put(ErrorCorrectionLevel.Q, "q");
		return retval;
	}
	
	public static String resolveECLevelName(ErrorCorrectionLevel ecLevel) {
		if (ecLevel == null)
			return null;
		final String retval = ecLevelNameMap.get(ecLevel);
		if (retval == null)
			throw new DOMException(DOMException.NOT_SUPPORTED_ERR, "Invalid EC level: " + ecLevel);
		return retval;
	}

	public static ErrorCorrectionLevel resolveECLevelString(String ecLevelString) {
		if (ecLevelString == null)
			return null;
		final ErrorCorrectionLevel retval = ecLevelNameMap.inverse().get(ecLevelString.toLowerCase());
		if (retval == null)
			throw new DOMException(DOMException.NOT_SUPPORTED_ERR, "Invalid EC level name: " + ecLevelString);
		return retval;
	}
}
