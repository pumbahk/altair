package jp.ticketstar.ticketing.templateconverter;

import java.awt.font.FontRenderContext;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;

import javax.swing.JOptionPane;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;

import org.w3c.dom.Document;

import org.apache.poi.hssf.usermodel.HSSFWorkbook;

public class App {
    public static void main(String[] args) {
    	AppWindow appWindow = new AppWindow();
    	appWindow.show();
    }
    
	public static void doConvert(File file, FontRenderContext frc) {
		if (!file.exists()) {
			JOptionPane.showMessageDialog(null, "ファイルがありません: " + file);
			return;
		}
		try {
			final HSSFWorkbook workbook = new HSSFWorkbook(new FileInputStream(file));
			final Document doc = new XlsToSvgConverter(workbook, frc).convertSheet(workbook.getSheetAt(0));
			final Transformer transformer = TransformerFactory.newInstance().newTransformer();
			transformer.setOutputProperty(OutputKeys.INDENT, "yes");
			final File outputFile = new File(file.getParentFile(), file.getName() + ".svg");
			transformer.transform(new DOMSource(doc), new StreamResult(new FileOutputStream(outputFile)));
		} catch (IOException e) {
			e.printStackTrace();
			JOptionPane.showMessageDialog(null, "ファイルを開けません: " + file + "\n" + e);
		} catch (Exception e) {
			e.printStackTrace();
			JOptionPane.showMessageDialog(null, "予期せぬエラー: " + e);
		}
	}
}
