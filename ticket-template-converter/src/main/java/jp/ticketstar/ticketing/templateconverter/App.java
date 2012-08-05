package jp.ticketstar.ticketing.templateconverter;

import java.awt.Font;
import java.awt.Graphics2D;
import java.awt.geom.Point2D;
import java.awt.geom.Rectangle2D;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import javax.swing.JOptionPane;

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
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;

import org.w3c.dom.Document;
import org.w3c.dom.Element;

public class App {
	static final String SVG_NAMESPACE = "http://www.w3.org/2000/svg";
	
    public static void main(String[] args) {
    	AppWindow appWindow = new AppWindow();
    	appWindow.show();
    }

    static int getUnitCharacterWidth(HSSFFont hssfFont) {
    	final Font f = new Font(hssfFont.getFontName(), Font.PLAIN, hssfFont.getFontHeightInPoints());
    	final BufferedImage bi = new BufferedImage(1, 1, BufferedImage.TYPE_INT_ARGB);
    	final Graphics2D g = (Graphics2D)bi.getGraphics();
    	final int retval = (g.getFontMetrics(f).charsWidth("0123abcx".toCharArray(), 0, 8) + 7) / 8; // unit character
    	g.dispose();
    	return retval;
    }

    static double getStandardUnitCharacterWidthInPoint(HSSFWorkbook workbook) {
		return getUnitCharacterWidth(workbook.getFontAt((short)0)) * 72 / 90.;
    }

    static double getRowHeight(HSSFSheet sheet, int rowNum) {
    	final HSSFRow row = sheet.getRow(rowNum);
    	return row == null ?
    		sheet.getDefaultRowHeightInPoints():
		    row.getHeightInPoints();
    }
 
    static Point2D.Double getAbsoluteCellPosition(HSSFSheet sheet, int row, int col) {
    	double x = 0, y = 0;
    	for (int i = 0; i < row; i++)
    		y += getRowHeight(sheet, i);
    	final double unitCharacterWidthInPoint = getStandardUnitCharacterWidthInPoint(sheet.getWorkbook());
    	for (int i = 0; i < col; i++)
    		x += sheet.getColumnWidth(i) * unitCharacterWidthInPoint;
    	return new Point2D.Double(x / 256., y);
    }
    
    public static Rectangle2D.Double anchorToRectangle(HSSFSheet sheet, HSSFAnchor anchor) {
    	if (anchor instanceof HSSFClientAnchor) {
    		final HSSFClientAnchor _anchor = (HSSFClientAnchor)anchor;
	    	final double unitCharacterWidthInPoint = getStandardUnitCharacterWidthInPoint(sheet.getWorkbook());
    		final Point2D.Double pos1 = getAbsoluteCellPosition(sheet, _anchor.getRow1(), _anchor.getCol1());
    		final Point2D.Double pos2 = getAbsoluteCellPosition(sheet, _anchor.getRow2(), _anchor.getCol2());
    		pos1.setLocation(
    				pos1.getX() + sheet.getColumnWidth((int)_anchor.getCol1()) * unitCharacterWidthInPoint * _anchor.getDx1() / 1024. / 256.,
    				pos1.getY() + getRowHeight(sheet, _anchor.getRow1()) * _anchor.getDy1() / 256.);
    		pos2.setLocation(
    				pos2.getX() + sheet.getColumnWidth((int)_anchor.getCol2()) * unitCharacterWidthInPoint * _anchor.getDx2() / 1024. / 256.,
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
			flowSpan.setAttribute("text-decoration", StringUtils.join(decorations, " "));
		}
	}
   
    static void populateWithFlowSpans(HSSFWorkbook workbook, Element flowDiv, HSSFRichTextString richstr) {
    	int startPos = 0, nextPos = 0;
    	HSSFFont currentFont = null;
    	Document doc = flowDiv.getOwnerDocument();
    	final String str = richstr.getString();
    	for (int i = 0, l = richstr.numFormattingRuns(); i < l; i++) {
    		nextPos = richstr.getIndexOfFormattingRun(i);
    		if (nextPos > startPos) {
    			final Element flowSpan = doc.createElementNS(SVG_NAMESPACE, "flowSpan");
    			flowSpan.appendChild(doc.createTextNode(str.substring(startPos, nextPos)));
    			populateFlowSpan(flowSpan, currentFont);
    			flowDiv.appendChild(flowSpan);
    		}
    		currentFont = workbook.getFontAt(richstr.getFontOfFormattingRun(i));
    		startPos = nextPos;
    	}
    	nextPos = richstr.length();
    	if (nextPos > startPos) {
			final Element flowSpan = doc.createElementNS(SVG_NAMESPACE, "flowSpan");
			flowSpan.appendChild(doc.createTextNode(str.substring(startPos, nextPos)));
			populateFlowSpan(flowSpan, currentFont);
			flowDiv.appendChild(flowSpan);
    	}
    }

	public static void doConvert(File file) {
		if (!file.exists()) {
			JOptionPane.showMessageDialog(null, "ファイルがありません: " + file);
			return;
		}
		try {
			final DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
			final DocumentBuilder db = dbf.newDocumentBuilder();
			final Document doc = db.newDocument();
			final Element svgElement = doc.createElementNS(SVG_NAMESPACE, "svg");
			final HSSFWorkbook workbook = new HSSFWorkbook(new FileInputStream(file));
			final HSSFSheet sheet = workbook.getSheetAt(0);
			final HSSFPatriarch patriarch = sheet.getDrawingPatriarch();
			for (final HSSFShape shape: patriarch.getChildren()) {
				if (shape instanceof HSSFTextbox) {
					final Rectangle2D.Double rect = anchorToRectangle(sheet, shape.getAnchor());
					final HSSFTextbox textBox = (HSSFTextbox)shape;
					final Element flowRootElement = doc.createElementNS(SVG_NAMESPACE, "flowRoot");
					{
						final Element flowRegionElement = doc.createElementNS(SVG_NAMESPACE, "flowRegion");
						final Element rectElement = doc.createElementNS(SVG_NAMESPACE, "rect");
						rectElement.setAttribute("x", Double.toString(rect.getX()) + "pt");
						rectElement.setAttribute("y", Double.toString(rect.getY()) + "pt");
						rectElement.setAttribute("width", Double.toString(rect.getWidth()) + "pt");
						rectElement.setAttribute("height", Double.toString(rect.getHeight()) + "pt");
						rectElement.setAttribute("fill", "none");
						rectElement.setAttribute("stroke", "none");
						flowRegionElement.appendChild(rectElement);
						flowRootElement.appendChild(flowRegionElement);
					}
					{
						final Element flowDivElement = doc.createElementNS(SVG_NAMESPACE, "flowDiv");
						populateWithFlowSpans(workbook, flowDivElement, textBox.getString());
						flowRootElement.appendChild(flowDivElement);
					}
					svgElement.appendChild(flowRootElement);
				}
			}
			doc.appendChild(svgElement);
			TransformerFactory.newInstance().newTransformer().transform(new DOMSource(doc), new StreamResult(System.err));
		} catch (IOException e) {
			e.printStackTrace();
			JOptionPane.showMessageDialog(null, "ファイルを開けません: " + file + "\n" + e);
		} catch (Exception e) {
			e.printStackTrace();
			JOptionPane.showMessageDialog(null, "予期せぬエラー: " + e);
		}
	}
}
