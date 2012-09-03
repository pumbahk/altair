package jp.ticketstar.ticketing.printing.gui;

import java.awt.PageAttributes;
import java.awt.geom.Rectangle2D;
import java.awt.print.PrinterJob;
import java.beans.PropertyChangeListener;
import java.beans.PropertyChangeSupport;
import java.net.URLConnection;
import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.print.PrintService;
import javax.swing.event.SwingPropertyChangeSupport;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import jp.ticketstar.ticketing.printing.ApplicationException;
import jp.ticketstar.ticketing.printing.DDimension2D;
import jp.ticketstar.ticketing.printing.GenericComboBoxModel;
import jp.ticketstar.ticketing.printing.AppModel;
import jp.ticketstar.ticketing.printing.OurPageFormat;
import jp.ticketstar.ticketing.printing.PageSetModel;
import jp.ticketstar.ticketing.printing.PrintingUtils;
import jp.ticketstar.ticketing.printing.TicketFormat;
import jp.ticketstar.ticketing.printing.URLConnectionFactory;
import jp.ticketstar.ticketing.printing.URLFetcher;
import jp.ticketstar.ticketing.printing.UnitUtils;

public class AppAppletModel implements AppModel {
	AppAppletConfiguration config;
	URLConnectionFactory connFactory;
	PropertyChangeSupport propertyChangeSupport = new SwingPropertyChangeSupport(this, true);
	PageSetModel ticketSetModel = null;
	PrintService printService = null;
	GenericComboBoxModel<PrintService> printServices;
	OurPageFormat pageFormat = null;
	GenericComboBoxModel<OurPageFormat> pageFormats;
	TicketFormat ticketFormat = null;
	GenericComboBoxModel<TicketFormat> ticketFormats;

	static class FormatPair {
		public List<OurPageFormat> pageFormats;
		public List<TicketFormat> ticketFormats;
		FormatPair(List<OurPageFormat> pageFormats, List<TicketFormat> ticketFormats) {
			this.pageFormats = pageFormats;
			this.ticketFormats = ticketFormats;
		}
	}
	
	public AppAppletModel(AppAppletConfiguration config, URLConnectionFactory connFactory) {
		this.config = config;
		this.connFactory = connFactory;
		reload();
	}

	int resolveOrientationString(String orientation) {
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
	
	PageAttributes.MediaType resolveMediaTypeString(String mediaType) {
		final PageAttributes.MediaType retval = mediaTypeMap.get(mediaType);
		if (retval == null)
			throw new ApplicationException("Invalid media type string: " + mediaType);
		return retval;
	}

	List<OurPageFormat> buildPageFormats(final JsonArray result) {
		final List<OurPageFormat> retval = new ArrayList<OurPageFormat>();
		for (final JsonElement _pageFormatDatum: result) {
			final JsonObject pageFormatDatum = _pageFormatDatum.getAsJsonObject();
			final OurPageFormat pageFormat = new OurPageFormat();
			pageFormat.setId(pageFormatDatum.get("id").getAsInt());
			pageFormat.setName(pageFormatDatum.get("name").getAsString());
			pageFormat.setOrientation(resolveOrientationString(pageFormatDatum.get("orientation").getAsString()));
			{
				final JsonElement paper = pageFormatDatum.get("paper");
				if (paper != null)
					pageFormat.setPreferredMediaType(resolveMediaTypeString(paper.getAsString()));
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
	
	List<TicketFormat> buildTicketFormats(final JsonArray result) {
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
	
	FormatPair fetchFormats() {
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
		return new FormatPair(
			buildPageFormats(data.get("page_formats").getAsJsonArray()),
			buildTicketFormats(data.get("ticket_formats").getAsJsonArray()));
	}
	
	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#reload()
	 */
	public void reload() {
		final FormatPair formatPair = fetchFormats();
		{
			final GenericComboBoxModel<PrintService> printServices = new GenericComboBoxModel<PrintService>();
	        for (PrintService service: PrinterJob.lookupPrintServices())
	        	printServices.add(service);
	        final GenericComboBoxModel<PrintService> prevPrintServices = this.printServices;
	        this.printServices = printServices;
			propertyChangeSupport.firePropertyChange("printServices", prevPrintServices, printServices);
		}
		{
			final PrintService prevPrintService = this.printService;
			this.printService = this.printServices.size() > 0 ? this.printServices.get(0): null;
			propertyChangeSupport.firePropertyChange("printService", prevPrintService, printService);
		}
		{
	        final GenericComboBoxModel<OurPageFormat> prevPageFormats = this.pageFormats;
			final GenericComboBoxModel<OurPageFormat> pageFormats = new GenericComboBoxModel<OurPageFormat>();
			for (OurPageFormat pageFormat: formatPair.pageFormats)
				pageFormats.add(pageFormat);
			this.pageFormats = pageFormats;
			propertyChangeSupport.firePropertyChange("pageFormats", prevPageFormats, pageFormats);
		}
		{
	        final GenericComboBoxModel<TicketFormat> prevPageFormats = this.ticketFormats;
			final GenericComboBoxModel<TicketFormat> ticketFormats = new GenericComboBoxModel<TicketFormat>();
			for (TicketFormat ticketFormat: formatPair.ticketFormats)
				ticketFormats.add(ticketFormat);
			this.ticketFormats = ticketFormats;
			propertyChangeSupport.firePropertyChange("ticketFormats", prevPageFormats, ticketFormats);
		}
		{
			final OurPageFormat prevPageFormat = this.pageFormat;
			this.pageFormat = this.pageFormats.size() > 0 ? this.pageFormats.get(0): null;
			propertyChangeSupport.firePropertyChange("pageFormat", prevPageFormat, pageFormat);
		}
	}
	
	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#refresh()
	 */
	public void refresh() {
		propertyChangeSupport.firePropertyChange("ticketSetModel", null, ticketSetModel);
		propertyChangeSupport.firePropertyChange("printServices", null, printServices);
		propertyChangeSupport.firePropertyChange("printService", null, printService);
		propertyChangeSupport.firePropertyChange("pageFormats", null, pageFormats);
		propertyChangeSupport.firePropertyChange("pageFormat", null, pageFormat);
		propertyChangeSupport.firePropertyChange("ticketFormats", null, ticketFormats);
		propertyChangeSupport.firePropertyChange("ticketFormat", null, ticketFormat);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#addPropertyChangeListener(java.beans.PropertyChangeListener)
	 */
	public void addPropertyChangeListener(PropertyChangeListener arg0) {
		propertyChangeSupport.addPropertyChangeListener(arg0);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#addPropertyChangeListener(java.lang.String, java.beans.PropertyChangeListener)
	 */
	public void addPropertyChangeListener(String arg0,
			PropertyChangeListener arg1) {
		propertyChangeSupport.addPropertyChangeListener(arg0, arg1);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#getPropertyChangeListeners()
	 */
	public PropertyChangeListener[] getPropertyChangeListeners() {
		return propertyChangeSupport.getPropertyChangeListeners();
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#getPropertyChangeListeners(java.lang.String)
	 */
	public PropertyChangeListener[] getPropertyChangeListeners(String arg0) {
		return propertyChangeSupport.getPropertyChangeListeners(arg0);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#hasListeners(java.lang.String)
	 */
	public boolean hasListeners(String arg0) {
		return propertyChangeSupport.hasListeners(arg0);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#removePropertyChangeListener(java.beans.PropertyChangeListener)
	 */
	public void removePropertyChangeListener(PropertyChangeListener arg0) {
		propertyChangeSupport.removePropertyChangeListener(arg0);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#removePropertyChangeListener(java.lang.String, java.beans.PropertyChangeListener)
	 */
	public void removePropertyChangeListener(String arg0,
			PropertyChangeListener arg1) {
		propertyChangeSupport.removePropertyChangeListener(arg0, arg1);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#getPageSetModel()
	 */
	public PageSetModel getPageSetModel() {
		return ticketSetModel;
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#setPageSetModel(jp.ticketstar.ticketing.printing.PageSetModel)
	 */
	public void setPageSetModel(PageSetModel ticketSetModel) {
		final PageSetModel prevValue = this.ticketSetModel;
		this.ticketSetModel = ticketSetModel;
		propertyChangeSupport.firePropertyChange("ticketSetModel", prevValue, ticketSetModel);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#getPrintService()
	 */
	public PrintService getPrintService() {
		return printService;
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#setPrintService(javax.print.PrintService)
	 */
	public void setPrintService(PrintService printService) {
		final PrintService prevValue = this.printService;
		this.printService = printService;
		propertyChangeSupport.firePropertyChange("printService", prevValue, printService);
	}
	
	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#getPrintServices()
	 */
	public GenericComboBoxModel<PrintService> getPrintServices() {
		return printServices;
	}
	
	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#getPageFormat()
	 */
	public OurPageFormat getPageFormat() {
		return pageFormat;
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#setPageFormat(jp.ticketstar.ticketing.printing.OurPageFormat)
	 */
	public void setPageFormat(OurPageFormat pageFormat) {
		final OurPageFormat prevValue = this.pageFormat;
		this.pageFormat = pageFormat;
		propertyChangeSupport.firePropertyChange("pageFormat", prevValue, pageFormat);
	}

	/* (non-Javadoc)
	 * @see jp.ticketstar.ticketing.printing.gui.IAppWindowModel#getPageFormats()
	 */
	public GenericComboBoxModel<OurPageFormat> getPageFormats() {
		return pageFormats;
	}

	public TicketFormat getTicketFormat() {
		return ticketFormat;
	}

	public void setTicketFormat(TicketFormat ticketFormat) {
		final TicketFormat prevValue = this.ticketFormat;
		this.ticketFormat = ticketFormat;
		propertyChangeSupport.firePropertyChange("ticketFormat", prevValue, ticketFormat);
	}

	public GenericComboBoxModel<TicketFormat> getTicketFormats() {
		return ticketFormats;
	}
}