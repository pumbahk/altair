package jp.ticketstar.ticketing.printing;

public class NESW implements Cloneable {
	public static final NESW ZERO = new NESW();
	
	double top;
	double bottom;
	double left;
	double right;

	public NESW clone() {
		return new NESW(top, right, bottom, left);
	}
	
	public double getTop() {
		return top;
	}
	
	public double getBottom() {
		return bottom;
	}
	
	public double getLeft() {
		return left;
	}
	
	public double getRight() {
		return right;
	}

	public NESW() {}

	public NESW(double v) {
		this(v, v, v, v);
	}
	
	public NESW(double ns, double ew) {
		this(ns, ew, ns, ew);
	}
	
	public NESW(double top, double right, double bottom, double left) {
		this.top = top;
		this.right = right;
		this.bottom = bottom;
		this.left = left;
	}
}
