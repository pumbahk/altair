package jp.ticketstar.ticketing.qrreader.gui;

import java.awt.geom.Rectangle2D;
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
import jp.ticketstar.ticketing.qrreader.TicketFormat;
import jp.ticketstar.ticketing.qrreader.TicketTemplate;
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
		public final List<TicketTemplate> ticketTemplates;

		public LoaderResult(Collection<TicketFormat> ticketFormats,
							List<TicketTemplate> ticketTemplates) {
			this.ticketFormats = ticketFormats;
			this.ticketTemplates = ticketTemplates;
		}
	}
	
	private static boolean notNull(JsonElement elem) {
		return elem != null && !elem.isJsonNull();
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
			final Mustache mustache = mustacheFactory.compile(ticketTemplateDatum.get("drawing").getAsString());
			final MustacheTicketTemplate ticketTemplate = new MustacheTicketTemplate(
					ticketTemplateDatum.get("id").getAsInt(),
					ticketTemplateDatum.get("name").getAsString(),
					ticketFormat,
					mustache);
			retval.add(ticketTemplate);
		}
		return retval;
	}
	
	public LoaderResult fetchFormats(AppAppletConfiguration config) {
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
		JsonObject data = result.get("data").getAsJsonObject();
		Map<Integer, TicketFormat> ticketFormats = buildTicketFormats(data.get("ticket_formats").getAsJsonArray());
		return new LoaderResult(
				ticketFormats.values(),
				buildTicketTemplates(
					ticketFormats,
					data.get("ticket_templates").getAsJsonArray()));
	}

	public FormatLoader(URLConnectionFactory connFactory, MustacheFactory mustacheFactory) {
		this.connFactory = connFactory;
		this.mustacheFactory = mustacheFactory;
	}
}
