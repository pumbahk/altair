package jp.ticketstar.ticketing.qrreader;

import java.util.HashMap;
import java.util.Map;

public class CollectionUtils {
	@SuppressWarnings("unchecked")
	public static <T> Map<T, String> stringValuedMap(Map<T, ?> map) {
		Map<T, String> retval;
		try {
			retval = map.getClass().newInstance();
		} catch (Exception e) {
			retval = new HashMap<T, String>();
		}
		for (Map.Entry<T, ?> entry: map.entrySet()) {
			final Object value = entry.getValue();
			retval.put(entry.getKey(), value == null ? null: value.toString());
		}
		return retval;
	}
}
