package jp.ticketstar.ticketing.printing.svg.extension;

import org.apache.batik.dom.AbstractDocument;
import org.apache.batik.dom.svg.SVGGraphicsElement;
import org.apache.batik.dom.svg.SVGOMAnimatedLength;
import org.apache.batik.dom.svg.TraitInformation;
import org.apache.batik.util.DoublyIndexedTable;
import org.apache.batik.util.SVGTypes;
import org.w3c.dom.Node;
import org.w3c.dom.svg.SVGTransformable;

import com.google.zxing.qrcode.decoder.ErrorCorrectionLevel;

public class QRCodeElement extends SVGGraphicsElement implements SVGTransformable {
	private static final long serialVersionUID = 1L;

	final static DoublyIndexedTable xmlTraitInformation = buildXmlTraitInformation();

	final static DoublyIndexedTable buildXmlTraitInformation() {
		final DoublyIndexedTable retval = new DoublyIndexedTable();
		retval.put(null, "x", new TraitInformation(true, SVGTypes.TYPE_LENGTH, PERCENTAGE_VIEWPORT_WIDTH));
		retval.put(null, "y", new TraitInformation(true, SVGTypes.TYPE_LENGTH, PERCENTAGE_VIEWPORT_WIDTH));
		retval.put(null, "width", new TraitInformation(true, SVGTypes.TYPE_LENGTH, PERCENTAGE_VIEWPORT_WIDTH));
		retval.put(null, "height", new TraitInformation(true, SVGTypes.TYPE_LENGTH, PERCENTAGE_VIEWPORT_WIDTH));
		return retval;
	}

	SVGOMAnimatedLength x;
	SVGOMAnimatedLength y;
	SVGOMAnimatedLength width;
	SVGOMAnimatedLength height;
	ErrorCorrectionLevel errorCorrectionLevel = ErrorCorrectionLevel.H;
	String encoding;
	
	public QRCodeElement() {
		super();
		initializeLiveAttributes();
	}
	
	public QRCodeElement(String prefix, AbstractDocument owner) {
		super(prefix, owner);
		initializeLiveAttributes();
	}

	@Override
	protected Node newNode() {
		return new QRCodeElement();
	}
	
	@Override
	public String getNamespaceURI() {
		return QRCodeExtensionConstants.TS_SVG_EXTENSION_NAMESPACE;
	}

	@Override
	public String getLocalName() {
		return QRCodeExtensionConstants.TS_QRCODE_TAG;
	}

	@Override
	protected void initializeAllLiveAttributes() {
		super.initializeAllLiveAttributes();
		initializeLiveAttributes();
	}

	protected void initializeLiveAttributes() {
		x = createLiveAnimatedLength(null, "x", "0", SVGOMAnimatedLength.HORIZONTAL_LENGTH, false);
		y = createLiveAnimatedLength(null, "y", "0", SVGOMAnimatedLength.VERTICAL_LENGTH, false);
		width = createLiveAnimatedLength(null, "width", "0", SVGOMAnimatedLength.HORIZONTAL_LENGTH, true);
		height = createLiveAnimatedLength(null, "height", "0", SVGOMAnimatedLength.VERTICAL_LENGTH, true);
	}
	
    protected DoublyIndexedTable getTraitInformationTable() {
        return xmlTraitInformation;
    }

	public SVGOMAnimatedLength getX() {
		return x;
	}

	public void setX(SVGOMAnimatedLength x) {
		this.x = x;
	}

	public SVGOMAnimatedLength getY() {
		return y;
	}

	public void setY(SVGOMAnimatedLength y) {
		this.y = y;
	}

	public SVGOMAnimatedLength getWidth() {
		return width;
	}

	public void setWidth(SVGOMAnimatedLength width) {
		this.width = width;
	}

	public SVGOMAnimatedLength getHeight() {
		return height;
	}

	public void setHeight(SVGOMAnimatedLength height) {
		this.height = height;
	}

	public ErrorCorrectionLevel getErrorCorrectionLevel() {
		if (this.errorCorrectionLevel == null) {
			final ErrorCorrectionLevel errorCorrectionLevel = QRCodeElementSupport.resolveECLevelString(getAttributeNS(null, "eclevel"));
			this.errorCorrectionLevel = errorCorrectionLevel;
		}
		return this.errorCorrectionLevel;
	}

	public void setErrorCorrectionLevel(ErrorCorrectionLevel errorCollectionLevel) {
		setAttributeNS(null, "eclevel", QRCodeElementSupport.resolveECLevelName(errorCollectionLevel));
		this.errorCorrectionLevel = errorCollectionLevel;
	}

	public String getContent() {
		return getAttributeNS(null, "content");
	}

	public void setContent(String content) {
		setAttributeNS(null, "content", content);
	}

	public String getEncoding() {
		final String retval = getAttributeNS(null, "encoding");
		if (retval.length() == 0)
			return null;
		else
			return retval;
	}

	public void setEncoding(String encoding) {
		setAttributeNS(null, "encoding", encoding);
	}
}