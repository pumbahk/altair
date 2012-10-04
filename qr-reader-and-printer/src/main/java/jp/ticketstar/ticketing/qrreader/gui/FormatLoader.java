package jp.ticketstar.ticketing.qrreader.gui;

import java.awt.PageAttributes;
import java.awt.geom.Rectangle2D;
import java.io.StringReader;
import java.net.URLConnection;
import java.nio.charset.Charset;
import java.util.List;
import java.util.Map;
import java.util.Collection;
import java.util.ArrayList;
import java.util.HashMap;

import jp.ticketstar.ticketing.ApplicationException;
import jp.ticketstar.ticketing.DDimension2D;
import jp.ticketstar.ticketing.qrreader.MustacheTicketTemplate;
import jp.ticketstar.ticketing.qrreader.OurPageFormat;
import jp.ticketstar.ticketing.qrreader.TicketFormat;
import jp.ticketstar.ticketing.qrreader.TicketTemplate;
import jp.ticketstar.ticketing.PrintingUtils;
import jp.ticketstar.ticketing.URLConnectionFactory;
import jp.ticketstar.ticketing.URLFetcher;
import jp.ticketstar.ticketing.UnitUtils;

import com.github.mustachejava.Mustache;
import com.github.mustachejava.MustacheFactory;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

public class FormatLoader {
	protected URLConnectionFactory connFactory;
	protected MustacheFactory mustacheFactory;

	public static class LoaderResult {
		public final Collection<TicketFormat> ticketFormats;
		public final List<OurPageFormat> pageFormats;
		public final List<TicketTemplate> ticketTemplates;

		public LoaderResult(Collection<TicketFormat> ticketFormats,
						    List<OurPageFormat> pageFormats,
							List<TicketTemplate> ticketTemplates) {
			this.ticketFormats = ticketFormats;
			this.pageFormats = pageFormats;
			this.ticketTemplates = ticketTemplates;
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
	
	private static boolean notNull(JsonElement elem) {
		return elem != null && !elem.isJsonNull();
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
	

	Map<Integer, TicketFormat> buildTicketFormats(final JsonArray result) {
		final Map<Integer, TicketFormat> retval = new HashMap<Integer, TicketFormat>();
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
			retval.put(ticketFormat.getId(), ticketFormat);
		}
		return retval;
	}
	
	List<TicketTemplate> buildTicketTemplates(final Map<Integer, TicketFormat> ticketFormats, final JsonArray result) {
		final List<TicketTemplate> retval = new ArrayList<TicketTemplate>();
		for (final JsonElement _ticketTemplateDatum: result) {
			final JsonObject ticketTemplateDatum = _ticketTemplateDatum.getAsJsonObject();
			final int ticketFormatId = ticketTemplateDatum.get("ticket_format_id").getAsInt();
			final TicketFormat ticketFormat = ticketFormats.get(ticketFormatId);
			if (ticketFormat == null)
				throw new ApplicationException("No such ticket template: id=" + ticketFormatId);
			final String name = ticketTemplateDatum.get("name").getAsString();
			final Mustache mustache = mustacheFactory.compile(new StringReader(ticketTemplateDatum.get("drawing").getAsString()), name);
			final MustacheTicketTemplate ticketTemplate = new MustacheTicketTemplate(
					ticketTemplateDatum.get("id").getAsInt(),
					name,
					ticketFormat,
					mustache);
			retval.add(ticketTemplate);
		}
		return retval;
	}
	
	public LoaderResult fetchTicketTemplates(AppAppletConfiguration config) {
		JsonObject result;
		try {
			final URLConnection conn = connFactory.newURLConnection(config.ticketTemplatesUrl);
			final URLFetcher.FetchResult fr = URLFetcher.fetch(conn, null);
			result = new JsonParser().parse(Charset.forName(fr.encoding != null ? fr.encoding: "UTF-8").decode(fr.buf).toString()).getAsJsonObject();
		} catch (Exception e) {
			throw new ApplicationException(e);
		}
		if (!result.get("status").getAsString().equals("success"))
			throw new ApplicationException("Failed to fetch page formats");
		JsonObject data = result.get("data").getAsJsonObject();
		Map<Integer, TicketFormat> ticketFormats = buildTicketFormats(data.get("ticket_formats").getAsJsonArray());
		return new LoaderResult(
				ticketFormats.values(),
				buildPageFormats(data.get("page_formats").getAsJsonArray()),
				buildTicketTemplates(
					ticketFormats,
					data.get("ticket_templates").getAsJsonArray()));
	}

	public FormatLoader(URLConnectionFactory connFactory, MustacheFactory mustacheFactory) {
		this.connFactory = connFactory;
		this.mustacheFactory = mustacheFactory;
	}
}
