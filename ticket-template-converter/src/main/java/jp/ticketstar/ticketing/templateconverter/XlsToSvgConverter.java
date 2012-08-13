package jp.ticketstar.ticketing.templateconverter;

import java.awt.Font;
import java.awt.font.FontRenderContext;
import java.awt.geom.AffineTransform;
import java.awt.geom.Point2D;
import java.awt.geom.Rectangle2D;
import java.util.ArrayList;
import java.util.List;

import org.apache.commons.lang3.StringUtils;
import org.apache.poi.hssf.usermodel.HSSFAnchor;
import org.apache.poi.hssf.usermodel.HSSFClientAnchor;
import org.apache.poi.hssf.usermodel.HSSFFont;
import org.apache.poi.hssf.usermodel.HSSFPatriarch;
import org.apache.poi.hssf.usermodel.HSSFRichTextString;
import org.apache.poi.hssf.usermodel.HSSFRow;
import org.apache.poi.hssf.usermodel.HSSFShape;
import org.apache.poi.hssf.usermodel.HSSFSheet;
import org.apache.poi.hssf.usermodel.HSSFTextbox;
import org.apache.poi.hssf.usermodel.HSSFWorkbook;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;

import org.w3c.dom.Document;
import org.w3c.dom.Element;


public class XlsToSvgConverter {
	static final String SVG_NAMESPACE = "http://www.w3.org/2000/svg";

	final double standardUnitCharacterWidthInPoint;
	final HSSFWorkbook workbook;
	final FontRenderContext fontRenderContext;
	
    double getUnitCharacterWidth(HSSFFont hssfFont) {
    	final Font f = new Font(hssfFont.getFontName(), Font.PLAIN, hssfFont.getFontHeightInPoints());
    	final Rectangle2D bounds = f.getStringBounds("01234567", fontRenderContext);
    	return bounds.getWidth() / 8;
    }

    static double getRowHeight(HSSFSheet sheet, int rowNum) {
    	final HSSFRow row = sheet.getRow(rowNum);
    	return row == null ?
    		sheet.getDefaultRowHeightInPoints():
		    row.getHeightInPoints();
    }
 
    Point2D.Double getAbsoluteCellPosition(HSSFSheet sheet, int row, int col) {
    	double x = 0, y = 0;
    	for (int i = 0; i < row; i++)
    		y += getRowHeight(sheet, i);
    	for (int i = 0; i < col; i++)
    		x += sheet.getColumnWidth(i) * standardUnitCharacterWidthInPoint;
    	return new Point2D.Double(x / 256., y);
    }
    
    Rectangle2D.Double anchorToRectangle(HSSFSheet sheet, HSSFAnchor anchor) {
    	if (anchor instanceof HSSFClientAnchor) {
    		final HSSFClientAnchor _anchor = (HSSFClientAnchor)anchor;
    		final Point2D.Double pos1 = getAbsoluteCellPosition(sheet, _anchor.getRow1(), _anchor.getCol1());
    		final Point2D.Double pos2 = getAbsoluteCellPosition(sheet, _anchor.getRow2(), _anchor.getCol2());
    		pos1.setLocation(
    				pos1.getX() + sheet.getColumnWidth((int)_anchor.getCol1()) * standardUnitCharacterWidthInPoint * _anchor.getDx1() / 1024. / 256.,
    				pos1.getY() + getRowHeight(sheet, _anchor.getRow1()) * _anchor.getDy1() / 256.);
    		pos2.setLocation(
    				pos2.getX() + sheet.getColumnWidth((int)_anchor.getCol2()) * standardUnitCharacterWidthInPoint * _anchor.getDx2() / 1024. / 256.,
    				pos2.getY() + getRowHeight(sheet, _anchor.getRow2()) * _anchor.getDy2() / 256.);
    		return new Rectangle2D.Double(Math.min(pos1.getX(), pos2.getX()), Math.min(pos1.getY(), pos2.getY()), Math.abs(pos2.getX() - pos1.getX()), Math.abs(pos2.getY() - pos1.getY()));
    	} else {
	    	return null;
    	}
    }
    
	private static void populateFlowSpan(Element flowSpan, HSSFFont currentFont) {
		flowSpan.setAttribute("font-family", currentFont.getFontName());
		flowSpan.setAttribute("font-size", Short.toString(currentFont.getFontHeightInPoints()));
		flowSpan.setAttribute("font-weight", currentFont.getBoldweight() == HSSFFont.BOLDWEIGHT_BOLD ? "bold": "normal");
		{
			List<String> decorations = new ArrayList<String>();
			if (currentFont.getStrikeout())
				decorations.add("line-through");
			if (currentFont.getUnderline() != HSSFFont.U_NONE)
				decorations.add("underline");
			if (decorations.size() > 0)
				flowSpan.setAttribute("text-decoration", StringUtils.join(decorations, " "));
		}
	}
   
    static void populateWithFlowSpans(HSSFWorkbook workbook, Element flowDiv, HSSFRichTextString richstr) {
    	int startPos = 0, nextPos = 0;
    	HSSFFont currentFont = null;
    	Document doc = flowDiv.getOwnerDocument();
    	final String str = richstr.getString();
    	Element flowPara = doc.createElementNS(SVG_NAMESPACE, "flowPara");
    	for (int i = 0, l = richstr.numFormattingRuns(); i <= l; i++) {
    		if (i == l)
    			nextPos = richstr.length();
    		else
	    		nextPos = richstr.getIndexOfFormattingRun(i);
    		if (nextPos > startPos) {
    			final String chunk = str.substring(startPos, nextPos);
    			final String[] lines = chunk.split("\\r\\n|\\r|\\n");
    			for (int j = 0; j < lines.length; j++) {
    				if (j > 0) {
    					flowDiv.appendChild(flowPara);
    					flowPara = doc.createElementNS(SVG_NAMESPACE, "flowPara");
    				}
	    			final Element flowSpan = doc.createElementNS(SVG_NAMESPACE, "flowSpan");
	    			flowSpan.appendChild(doc.createTextNode(lines[j]));
	    			populateFlowSpan(flowSpan, currentFont);
	    			flowPara.appendChild(flowSpan);
    			}
    		}
    		if (i < l)
	    		currentFont = workbook.getFontAt(richstr.getFontOfFormattingRun(i));
    		startPos = nextPos;
    	}
    	flowDiv.appendChild(flowPara);
    }

	public XlsToSvgConverter(HSSFWorkbook workbook, FontRenderContext frc) {
		this.workbook = workbook;
		this.fontRenderContext = frc;
		// standardUnitCharacterWidthInPoint = getUnitCharacterWidth(workbook.getFontAt((short)0));
		standardUnitCharacterWidthInPoint = workbook.getFontAt((short)0).getFontHeightInPoints() * 0.5625;
	}

	public Document convertSheet(HSSFSheet sheet) throws ParserConfigurationException {
		final DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
		final DocumentBuilder db = dbf.newDocumentBuilder();
		final Document doc = db.newDocument();
		final Element svgElement = doc.createElementNS(SVG_NAMESPACE, "svg");
		final HSSFPatriarch patriarch = sheet.getDrawingPatriarch();
		final AffineTransform af = AffineTransform.getScaleInstance(90. / 96, 90. / 96); // 96dpi => 90dpi
		for (final HSSFShape shape: patriarch.getChildren()) {
			if (shape instanceof HSSFTextbox) {
				final Rectangle2D.Double rect = anchorToRectangle(sheet, shape.getAnchor());
				final double[] _rect = new double[] { rect.getMinX(), rect.getMinY(), rect.getMaxX(), rect.getMaxY() };
				af.transform(_rect, 0, _rect, 0, 2);
				final HSSFTextbox textBox = (HSSFTextbox)shape;
				final Element flowRootElement = doc.createElementNS(SVG_NAMESPACE, "flowRoot");
				{
					final Element flowRegionElement = doc.createElementNS(SVG_NAMESPACE, "flowRegion");
					final Element rectElement = doc.createElementNS(SVG_NAMESPACE, "rect");
					rectElement.setAttribute("x", Double.toString(_rect[0]) + "pt");
					rectElement.setAttribute("y", Double.toString(_rect[1]) + "pt");
					rectElement.setAttribute("width", Double.toString(_rect[2] - _rect[0])+ "pt");
					rectElement.setAttribute("height", Double.toString(_rect[3] - _rect[1]) + "pt");
					rectElement.setAttribute("fill", "none");
					rectElement.setAttribute("stroke", "none");
					flowRegionElement.appendChild(rectElement);
					flowRootElement.appendChild(flowRegionElement);
				}
				{
					final Element flowDivElement = doc.createElementNS(SVG_NAMESPACE, "flowDiv");
					String alignment = null;
					switch (textBox.getHorizontalAlignment()) {
					case HSSFTextbox.HORIZONTAL_ALIGNMENT_CENTERED:	
						alignment = "middle";
						break;
					case HSSFTextbox.HORIZONTAL_ALIGNMENT_RIGHT:
						alignment = "end";
						break;
					case HSSFTextbox.HORIZONTAL_ALIGNMENT_LEFT:
					default:
						alignment = "start";
						break;
					case HSSFTextbox.HORIZONTAL_ALIGNMENT_JUSTIFIED:
						alignment = "justify";
						break;
					}
					flowDivElement.setAttributeNS(null, "style", "text-anchor:" + alignment + ";" + "line-height:100%");
					populateWithFlowSpans(this.workbook, flowDivElement, textBox.getString());
					flowRootElement.appendChild(flowDivElement);
				}
				svgElement.appendChild(flowRootElement);
			}
		}
		doc.appendChild(svgElement);
		return doc;
	}
}
