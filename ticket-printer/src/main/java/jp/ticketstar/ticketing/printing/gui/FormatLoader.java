package jp.ticketstar.ticketing.printing.gui;

import java.awt.PageAttributes;
import java.awt.geom.Rectangle2D;
import java.net.URLConnection;
import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import jp.ticketstar.ticketing.printing.ApplicationException;
import jp.ticketstar.ticketing.printing.DDimension2D;
import jp.ticketstar.ticketing.printing.OurPageFormat;
import jp.ticketstar.ticketing.printing.PrintingUtils;
import jp.ticketstar.ticketing.printing.TicketFormat;
import jp.ticketstar.ticketing.printing.URLConnectionFactory;
import jp.ticketstar.ticketing.printing.URLFetcher;
import jp.ticketstar.ticketing.printing.UnitUtils;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

public class FormatLoader {
	protected URLConnectionFactory connFactory;
	
	public static class FormatPair {
		public List<OurPageFormat> pageFormats;
		public List<TicketFormat> ticketFormats;
		FormatPair(List<OurPageFormat> pageFormats, List<TicketFormat> ticketFormats) {
			this.pageFormats = pageFormats;
			this.ticketFormats = ticketFormats;
		}
	}
	
	private static int resolveOrientationString(String orientation) {
		if (orientation.equalsIgnoreCase("landscape")) {
			return OurPageFormat.LANDSCAPE;
		} else if (orientation.equalsIgnoreCase("portrait")) {
			return OurPageFormat.PORTRAIT;
		}
		throw new ApplicationException("Invalid orientation string: " + orientation);
	}

	private static boolean notNull(JsonElement elem) {
		return elem != null && !elem.isJsonNull();
	}

	static final Map<String, PageAttributes.MediaType> mediaTypeMap = new HashMap<String, PageAttributes.MediaType>();
	
	static {
		mediaTypeMap.put("A0", PageAttributes.MediaType.A0);
		mediaTypeMap.put("A1", PageAttributes.MediaType.A1);
		mediaTypeMap.put("A2", PageAttributes.MediaType.A2);
		mediaTypeMap.put("A3", PageAttributes.MediaType.A3);
		mediaTypeMap.put("A4", PageAttributes.MediaType.A4);
		mediaTypeMap.put("A5", PageAttributes.MediaType.A5);
		mediaTypeMap.put("A6", PageAttributes.MediaType.A6);
		mediaTypeMap.put("B0", PageAttributes.MediaType.B0);
		mediaTypeMap.put("B1", PageAttributes.MediaType.B1);
		mediaTypeMap.put("B2", PageAttributes.MediaType.B2);
		mediaTypeMap.put("B3", PageAttributes.MediaType.B3);
		mediaTypeMap.put("B4", PageAttributes.MediaType.B4);
		mediaTypeMap.put("B5", PageAttributes.MediaType.B5);
		mediaTypeMap.put("B6", PageAttributes.MediaType.B6);
		mediaTypeMap.put("JIS_B0", PageAttributes.MediaType.JIS_B0);
		mediaTypeMap.put("JIS_B1", PageAttributes.MediaType.JIS_B1);
		mediaTypeMap.put("JIS_B2", PageAttributes.MediaType.JIS_B2);
		mediaTypeMap.put("JIS_B3", PageAttributes.MediaType.JIS_B3);
		mediaTypeMap.put("JIS_B4", PageAttributes.MediaType.JIS_B4);
		mediaTypeMap.put("JIS_B5", PageAttributes.MediaType.JIS_B5);
		mediaTypeMap.put("JIS_B6", PageAttributes.MediaType.JIS_B6);
	}
	
	protected static PageAttributes.MediaType resolveMediaTypeString(String mediaType) {
		final PageAttributes.MediaType retval = mediaTypeMap.get(mediaType);
		if (retval == null)
			throw new ApplicationException("Invalid media type string: " + mediaType);
		return retval;
	}

	protected static List<OurPageFormat> buildPageFormats(final JsonArray result) {
		final List<OurPageFormat> retval = new ArrayList<OurPageFormat>();
		for (final JsonElement _pageFormatDatum: result) {
			final JsonObject pageFormatDatum = _pageFormatDatum.getAsJsonObject();
			final OurPageFormat pageFormat = new OurPageFormat();
			pageFormat.setId(pageFormatDatum.get("id").getAsInt());
			pageFormat.setName(pageFormatDatum.get("name").getAsString());
			pageFormat.setOrientation(resolveOrientationString(pageFormatDatum.get("orientation").getAsString()));
			{
				final JsonElement paper = pageFormatDatum.get("paper");
				if (notNull(paper)) 
					pageFormat.setPreferredMediaType(resolveMediaTypeString(paper.getAsString()));
			}
			{
				final JsonElement printerName = pageFormatDatum.get("printer_name");
				if (notNull(printerName))
					pageFormat.setPreferredPrinterName(printerName.getAsString());
			}
			{
				final JsonObject size = pageFormatDatum.get("size").getAsJsonObject();
				final JsonObject printableArea = pageFormatDatum.get("printable_area").getAsJsonObject();
				pageFormat.setPaper(PrintingUtils.buildPaper(
						new DDimension2D(
								UnitUtils.convertToPoint(size.get("width").getAsString()),
								UnitUtils.convertToPoint(size.get("height").getAsString())),
						new Rectangle2D.Double(
								UnitUtils.convertToPoint(printableArea.get("x").getAsString()),
								UnitUtils.convertToPoint(printableArea.get("y").getAsString()),
								UnitUtils.convertToPoint(printableArea.get("width").getAsString()),
								UnitUtils.convertToPoint(printableArea.get("height").getAsString()))));
			}
			{
				final JsonObject perforations = pageFormatDatum.get("perforations").getAsJsonObject();
				{
					final JsonArray verticalPerforations = perforations.get("vertical").getAsJsonArray();
					final double[] values = new double[verticalPerforations.size()];
					for (int i = 0; i < verticalPerforations.size(); i++)
						values[i] = UnitUtils.convertToPoint(verticalPerforations.get(i).getAsString());
					pageFormat.setVerticalGuides(values);
				}
				{
					final JsonArray horizontalPerforations = perforations.get("horizontal").getAsJsonArray();
					final double[] values = new double[horizontalPerforations.size()];
					for (int i = 0; i < horizontalPerforations.size(); i++)
						values[i] = UnitUtils.convertToPoint(horizontalPerforations.get(i).getAsString());
					pageFormat.setHorizontalGuides(values);
				}
			}
			retval.add(pageFormat);
		}
		return retval;
	}
	
	protected static List<TicketFormat> buildTicketFormats(final JsonArray result) {
		final List<TicketFormat> retval = new ArrayList<TicketFormat>();
		for (final JsonElement _ticketFormatDatum: result) {
			final JsonObject ticketFormatDatum = _ticketFormatDatum.getAsJsonObject();
			final TicketFormat ticketFormat = new TicketFormat();
			ticketFormat.setId(ticketFormatDatum.get("id").getAsInt());
			ticketFormat.setName(ticketFormatDatum.get("name").getAsString());
			{
				final JsonObject size = ticketFormatDatum.get("size").getAsJsonObject();
				ticketFormat.setSize(
					new DDimension2D(
							UnitUtils.convertToPoint(size.get("width").getAsString()),
							UnitUtils.convertToPoint(size.get("height").getAsString())));
			}
			{
				final JsonArray printableAreas = ticketFormatDatum.get("printable_areas").getAsJsonArray();
				Rectangle2D[] values = new Rectangle2D[printableAreas.size()];
				for (int i = 0; i < printableAreas.size(); i++) {
					final JsonObject printableArea = printableAreas.get(i).getAsJsonObject();
					values[i] = new Rectangle2D.Double(
							UnitUtils.convertToPoint(printableArea.get("x").getAsString()),
							UnitUtils.convertToPoint(printableArea.get("y").getAsString()),
							UnitUtils.convertToPoint(printableArea.get("width").getAsString()),
							UnitUtils.convertToPoint(printableArea.get("height").getAsString()));
				}
				ticketFormat.setPrintableAreas(values);
			}
			{
				final JsonObject perforations = ticketFormatDatum.get("perforations").getAsJsonObject();
				{
					final JsonArray verticalPerforations = perforations.get("vertical").getAsJsonArray();
					final double[] values = new double[verticalPerforations.size()];
					for (int i = 0; i < verticalPerforations.size(); i++)
						values[i] = UnitUtils.convertToPoint(verticalPerforations.get(i).getAsString());
					ticketFormat.setVerticalGuides(values);
				}
				{
					final JsonArray horizontalPerforations = perforations.get("horizontal").getAsJsonArray();
					final double[] values = new double[horizontalPerforations.size()];
					for (int i = 0; i < horizontalPerforations.size(); i++)
						values[i] = UnitUtils.convertToPoint(horizontalPerforations.get(i).getAsString());
					ticketFormat.setHorizontalGuides(values);
				}
			}
			retval.add(ticketFormat);
		}
		return retval;
	}

	public static FormatPair buildFormatsFromJsonObject(final JsonObject data) {
		return new FormatPair(
			buildPageFormats(data.get("page_formats").getAsJsonArray()),
			buildTicketFormats(data.get("ticket_formats").getAsJsonArray()));
	}
	
	public FormatPair fetchFormats(AppAppletConfiguration config) {
		JsonObject result;
		try {
			final URLConnection conn = connFactory.newURLConnection(config.formatsUrl);
			final URLFetcher.FetchResult fr = URLFetcher.fetch(conn, null);
			result = new JsonParser().parse(Charset.forName(fr.encoding != null ? fr.encoding: "UTF-8").decode(fr.buf).toString()).getAsJsonObject();
		} catch (Exception e) {
			throw new ApplicationException(e);
		}
		if (!result.get("status").getAsString().equals("success"))
			throw new ApplicationException("Failed to fetch page formats");
		return buildFormatsFromJsonObject(result.get("data").getAsJsonObject());
	}

	public FormatLoader(URLConnectionFactory connFactory) {
		this.connFactory = connFactory;
	}
}
