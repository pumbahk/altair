class UnitUtils {
    public static function anyToInch(unit:UnitKind, inch:Float):Float {
        switch (unit) {
        case INCH:
            return inch;
        case MILLIMETER:
            return mmToInch(inch);
        case CENTIMETER:
            return cmToInch(inch);
        case METER:
            return meterToInch(inch);
        case POINT:
            return pointToInch(inch);
        case PICA:
            return picaToInch(inch);
        default:
            throw new IllegalArgumentException();
        }
    }

    public static function mmToInch(mm:Float):Float {
        return mm / 25.4;
    }

    public static function cmToInch(cm:Float):Float {
        return cm / 2.54;
    }

    public static function meterToInch(m:Float):Float {
        return m / 0.0254;
    }

    public static function pointToInch(p:Float):Float {
        return p / 72.;
    }

    public static function picaToInch(p:Float):Float {
        return p / 12.;
    }

    public static function mmToInchP(mm:Point):Point {
        return { x: mm.x / 25.4, y: mm.y / 25.4 };
    }

    public static function cmToInchP(cm:Point):Point {
        return { x: cm.x / 2.54, y: cm.y / 2.54 };
    }

    public static function meterToInchP(m:Point):Point {
        return { x: m.x / 0.0254, y: m.y / 0.0254 };
    }

    public static function pointToInchP(p:Point):Point {
        return { x: p.x / 72., y: p.y / 72. };
    }

    public static function picaToInchP(p:Point):Point {
        return { x: p.x / 12., y: p.y / 12. };
    }

    public static function inchToAny(unit:UnitKind, inch:Float):Float {
        switch (unit) {
        case INCH:
            return inch;
        case MILLIMETER:
            return inchToMm(inch);
        case CENTIMETER:
            return inchToCm(inch);
        case METER:
            return inchToMeter(inch);
        case POINT:
            return inchToPoint(inch);
        case PICA:
            return inchToPica(inch);
        default:
            throw new IllegalArgumentException();
        }
    }

    public static function inchToMm(inch:Float):Float {
        return inch * 25.4;
    }

    public static function inchToCm(inch:Float):Float {
        return inch * 2.54;
    }

    public static function inchToMeter(inch:Float):Float {
        return inch * 0.0254;
    }

    public static function inchToPoint(inch:Float):Float {
        return inch * 72.;
    }

    public static function inchToPica(inch:Float):Float {
        return inch * 12.;
    }

    public static function inchToMmP(inch:Point):Point {
        return { x: inch.x * 25.4, y: inch.y * 25.4 };
    }

    public static function inchToCmP(inch:Point):Point {
        return { x: inch.x * 2.54, y: inch.y * 2.54 };
    }

    public static function inchToMeterP(inch:Point):Point {
        return { x: inch.x * 0.0254, y: inch.y * 0.0254 };
    }

    public static function inchToPointP(inch:Point):Point {
        return { x: inch.x * 72., y: inch.y * 72. };
    }

    public static function inchToPicaP(inch:Point):Point {
        return { x: inch.x * 12., y: inch.y * 12. };
    }
}
