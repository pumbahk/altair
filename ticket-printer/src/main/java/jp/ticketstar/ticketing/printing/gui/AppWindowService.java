package jp.ticketstar.ticketing.printing.gui;

import java.awt.geom.AffineTransform;
import java.awt.print.PrinterJob;
import java.io.File;
import java.net.URI;
import java.security.AccessController;
import java.security.PrivilegedAction;
import java.util.ArrayList;

import javax.swing.JFileChooser;

import org.apache.batik.swing.svg.SVGDocumentLoader;

import jp.ticketstar.ticketing.printing.AppModel;
import jp.ticketstar.ticketing.printing.BasicAppService;
import jp.ticketstar.ticketing.printing.Page;
import jp.ticketstar.ticketing.printing.TicketPrintable;
import jp.ticketstar.ticketing.svg.ExtendedSVG12BridgeContext;
import jp.ticketstar.ticketing.svg.OurDocumentLoader;

public class AppWindowService extends BasicAppService {
	public void openFileDialog() {
		JFileChooser chooser = new JFileChooser();
		chooser.setCurrentDirectory(new File(System.getProperty("user.dir")));
		if (chooser.showOpenDialog(parentComponent) == JFileChooser.APPROVE_OPTION) {
			loadDocument(chooser.getSelectedFile().toURI());
		}
	}

	public synchronized void loadDocument(URI uri) {
		if (this.documentLoader != null)
			return;
		final OurDocumentLoader loader = new OurDocumentLoader(this);
		final SVGDocumentLoader documentLoader = new SVGDocumentLoader(uri.toString(), loader);
		this.documentLoader = documentLoader;
		documentLoader.addSVGDocumentLoaderListener(new LoaderListener(new ExtendedSVG12BridgeContext(this, loader)));
		documentLoader.start();
	}

	protected TicketPrintable createTicketPrintable(PrinterJob job) {
		return new TicketPrintable(
			new ArrayList<Page>(model.getPageSetModel().getPages()), job,
			new AffineTransform(72. / 90, 0, 0, 72. / 90, 0, 0)
		);
	}

	public void printAll() {
		AccessController.doPrivileged(new PrivilegedAction<Object>() {
			public Object run() {
				try {
					final PrinterJob job = PrinterJob.getPrinterJob();
					job.setPrintService(model.getPrintService());
					job.setPrintable(createTicketPrintable(job), model.getPageFormat());
					job.print();
				} catch (Exception e) {
					displayError("Failed to print tickets\nReason: " + e);
				}
				return null;
			}
		});
	}

	public AppWindowService(AppModel model) {
		super(model);
	}
}
