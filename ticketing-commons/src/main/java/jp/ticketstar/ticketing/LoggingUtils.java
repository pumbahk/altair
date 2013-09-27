package jp.ticketstar.ticketing;

import com.google.gson.Gson;
import com.google.gson.JsonNull;
import com.google.gson.JsonObject;
import com.google.gson.JsonArray;

public final class LoggingUtils {
	private static JsonObject throwableToJsonObject(final Throwable e) {
		final JsonObject jo = new JsonObject();
		jo.addProperty("className", e.getClass().getName());
		jo.addProperty("classCanonicalName", e.getClass().getCanonicalName());
		{
			final StackTraceElement[] stackTraceElements = e.getStackTrace();
			final JsonArray stackTraceJson = new JsonArray();
			for (final StackTraceElement stackTraceElement: stackTraceElements) {
				final JsonObject stackTraceElementJson = new JsonObject();
				stackTraceElementJson.addProperty("fileName", stackTraceElement.getFileName());
				stackTraceElementJson.addProperty("lineNumber", stackTraceElement.getLineNumber());
				stackTraceElementJson.addProperty("className", stackTraceElement.getClassName());
				stackTraceElementJson.addProperty("methodName", stackTraceElement.getMethodName());
				stackTraceElementJson.addProperty("isNativeMethod", stackTraceElement.isNativeMethod());
				stackTraceJson.add(stackTraceElementJson);
			}
			jo.add("stackTrace", stackTraceJson);
		}
		jo.add("cause", e.getCause() != null ? throwableToJsonObject(e.getCause()): JsonNull.INSTANCE);
		return jo;
	}
	
	public static String formatException(final Throwable e) {
		return new Gson().toJson(throwableToJsonObject(e));
	}
}
