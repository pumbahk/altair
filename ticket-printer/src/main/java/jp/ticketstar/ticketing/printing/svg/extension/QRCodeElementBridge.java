package jp.ticketstar.ticketing.printing.svg.extension;

import java.awt.Rectangle;
import java.awt.Shape;
import java.awt.geom.AffineTransform;
import java.awt.geom.PathIterator;
import java.awt.geom.Point2D;
import java.awt.geom.Rectangle2D;
import java.awt.geom.Rectangle2D.Double;
import java.util.EnumMap;
import java.util.Map;

import org.apache.batik.bridge.Bridge;
import org.apache.batik.bridge.BridgeContext;
import org.apache.batik.bridge.BridgeException;
import org.apache.batik.bridge.SVGShapeElementBridge;
import org.apache.batik.dom.svg.AnimatedLiveAttributeValue;
import org.apache.batik.dom.svg.LiveAttributeException;
import org.apache.batik.gvt.ShapeNode;
import org.w3c.dom.Element;

import com.google.zxing.qrcode.encoder.ByteMatrix;
import com.google.zxing.qrcode.encoder.Encoder;
import com.google.zxing.qrcode.encoder.QRCode;
import com.google.zxing.EncodeHintType;
import com.google.zxing.WriterException;

class ByteMatrixPathIterator implements PathIterator {
	static class PathElement {
		public int op;
		public double[] args;
		PathElement(int op, double ... args) {
			this.op = op;
			this.args = args;
		}
	}

	int cursor;
	int x, y;
	PathElement[] currentPathElementSet;
	private Double rect;
	private ByteMatrix matrix;
	private AffineTransform transform;
	private double boxWidth;
	private double boxHeight;

	boolean nextPathElementSet() {
		for (;;) {
			if (x >= matrix.getWidth()) {
				x = 0;
				y++;
			}
			if (y >= matrix.getHeight())
				return false;
			if (matrix.get(x++, y) != 0)
				break;
		}
		double bx = rect.getX() + boxWidth * x,
			   by = rect.getY() + boxHeight * y;
		final double[] box = new double[] { bx, by, bx + boxWidth, by + boxHeight };
		transform.transform(box, 0, box, 0, 2);
		currentPathElementSet = new PathElement[] {
			new PathElement(SEG_MOVETO, box[0], box[1]),
			new PathElement(SEG_LINETO, box[2], box[1]),
			new PathElement(SEG_LINETO, box[2], box[3]),
			new PathElement(SEG_LINETO, box[0], box[3]),
			new PathElement(SEG_LINETO, box[0], box[1]),
			new PathElement(SEG_CLOSE)
		};
		cursor = 0;
		return true;
	}
	
	public int currentSegment(float[] arg0) {
		if (currentPathElementSet == null)
			nextPathElementSet();
		final PathElement elem = currentPathElementSet[cursor];
		for (int i = Math.min(arg0.length, elem.args.length); --i >= 0;)
			arg0[i] = (float)elem.args[i];
		return elem.op;
	}

	public int currentSegment(double[] arg0) {
		if (currentPathElementSet == null)
			nextPathElementSet();
		final PathElement elem = currentPathElementSet[cursor];
		System.arraycopy(elem.args, 0, arg0, 0, Math.min(arg0.length, elem.args.length));
		return elem.op;
	}

	public int getWindingRule() {
		return WIND_EVEN_ODD;
	}

	public boolean isDone() {
		return !((currentPathElementSet != null && cursor < currentPathElementSet.length) || nextPathElementSet());
	}

	public void next() {
		if (currentPathElementSet == null || ++cursor >= currentPathElementSet.length)
			nextPathElementSet();
	}

	public ByteMatrixPathIterator(Rectangle2D.Double rect, ByteMatrix matrix, AffineTransform transform) {
		this.rect = rect;
		this.matrix = matrix;
		this.transform = transform;
		this.x = 0;
		this.y = 0;
		this.cursor = 0;
		this.boxWidth = rect.getWidth() / (matrix.getWidth() + 2);
		this.boxHeight = rect.getHeight() / (matrix.getHeight() + 2);
	}
}
	
class ByteMatrixShape implements Shape {
	private Rectangle2D.Double rect;
	private ByteMatrix matrix;

	public boolean contains(Point2D p) {
		return rect.contains(p);
	}

	public boolean contains(Rectangle2D r) {
		return rect.contains(r);
	}

	public boolean contains(double x, double y) {
		return rect.contains(x, y);
	}

	public boolean contains(double x, double y, double w, double h) {
		return rect.contains(x, y, w, h);
	}

	public Rectangle getBounds() {
		return rect.getBounds();
	}

	public Rectangle2D getBounds2D() {
		return rect.getBounds2D();
	}

	public PathIterator getPathIterator(AffineTransform at) {
		return new ByteMatrixPathIterator(rect, matrix, at);
	}

	public PathIterator getPathIterator(AffineTransform at, double flatness) {
		return new ByteMatrixPathIterator(rect, matrix, at);
	}

	public boolean intersects(Rectangle2D r) {
		return rect.intersects(r);
	}

	public boolean intersects(double x, double y, double w, double h) {
		return rect.intersects(x, y, w, h);
	}

	public ByteMatrixShape(Rectangle2D.Double rect, ByteMatrix matrix) {
		this.rect = rect;
		this.matrix = matrix;
	}
}

public class QRCodeElementBridge extends SVGShapeElementBridge {
	@Override
    public String getNamespaceURI() {
    	return QRCodeExtensionConstants.TS_SVG_EXTENSION_NAMESPACE;
    }

	public String getLocalName() {
		return QRCodeExtensionConstants.TS_QRCODE_TAG;
	}

	public Bridge getInstance() {
		return new QRCodeElementBridge();
	}

	@Override
	public void handleAnimatedAttributeChanged(AnimatedLiveAttributeValue alav) {
		if (alav.getNamespaceURI() == null) {
			String ln = alav.getLocalName();
			if (ln.equals("x")
					|| ln.equals("y")
					|| ln.equals("width") 
					|| ln.equals("height")) {
				buildShape(ctx, e, (ShapeNode)node);
				handleGeometryChanged();
			}
		}
		super.handleAnimatedAttributeChanged(alav);
	}
	
	@Override
	protected void buildShape(BridgeContext ctx, Element _elem, ShapeNode node) {
		final QRCodeElement elem = (QRCodeElement)_elem;
		final Map<EncodeHintType, Object> hints = new EnumMap<EncodeHintType, Object>(EncodeHintType.class);
		final String encoding = elem.getEncoding();
		final QRCode qrcode = new QRCode();
		if (encoding != null)
			hints.put(EncodeHintType.CHARACTER_SET, encoding);
		try {
			Encoder.encode(elem.getContent(), elem.getErrorCorrectionLevel(), hints, qrcode);
			node.setShape(new ByteMatrixShape(
					new Rectangle2D.Double(
						elem.getX().getCheckedValue(),
						elem.getY().getCheckedValue(),
						elem.getWidth().getCheckedValue(),
						elem.getHeight().getCheckedValue()),
					qrcode.getMatrix()));
		} catch (LiveAttributeException e) {
			throw new BridgeException(ctx, e);
		} catch (WriterException e) {
			throw new BridgeException(ctx, elem, e, e.toString(), null);
		}
	}
}