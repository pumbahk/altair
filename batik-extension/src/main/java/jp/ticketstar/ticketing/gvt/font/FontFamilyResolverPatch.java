package jp.ticketstar.ticketing.gvt.font;

import java.awt.Font;
import java.awt.GraphicsEnvironment;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.StringTokenizer;
import java.util.Locale;

import org.apache.batik.bridge.FontFace;
import org.apache.batik.bridge.FontFamilyResolver;
import org.apache.batik.gvt.font.AWTFontFamily;
import org.apache.batik.gvt.font.AWTGVTFont;
import org.apache.batik.gvt.font.GVTFontFamily;

/**
 * Almost same with DefaultFontFamilyResolver.
 * Force to set locale to ja_JP because of the preview server running on US locale.
 * See https://redmine.ticketstar.jp/issues/6179
 */

@SuppressWarnings("unchecked")
public class FontFamilyResolverPatch implements FontFamilyResolver {
    public static final FontFamilyResolverPatch SINGLETON = new FontFamilyResolverPatch();
    private static final AWTFontFamily DEFAULT_FONT_FAMILY = new AWTFontFamily("SansSerif");
    protected static final Map fonts = new HashMap();
    protected static final List awtFontFamilies = new ArrayList();
    protected static final List awtFonts = new ArrayList();
    protected static final Map resolvedFontFamilies;

    private FontFamilyResolverPatch() {
    }

    public AWTFontFamily resolve(String familyName, FontFace fontFace) {
        String fontName = (String)fonts.get(fontFace.getFamilyName().toLowerCase());
        if (fontName == null) {
            return null;
        } else {
            FontFace.createFontFace(fontName, fontFace);
            return new AWTFontFamily(fontFace);
        }
    }

    public GVTFontFamily loadFont(InputStream in, FontFace ff) throws Exception {
        Font font = Font.createFont(Font.TRUETYPE_FONT, in);
        return new AWTFontFamily(ff, font);
    }

    public GVTFontFamily resolve(String familyName) {
        familyName = familyName.toLowerCase();
        GVTFontFamily resolvedFF = (GVTFontFamily)resolvedFontFamilies.get(familyName);
        if (resolvedFF == null) {
            String awtFamilyName = (String)fonts.get(familyName);
            if (awtFamilyName != null) {
                resolvedFF = new AWTFontFamily(awtFamilyName);
            }

            resolvedFontFamilies.put(familyName, resolvedFF);
        }

        return (GVTFontFamily)resolvedFF;
    }

    public GVTFontFamily getFamilyThatCanDisplay(char c) {
        for(int i = 0; i < awtFontFamilies.size(); ++i) {
            AWTFontFamily fontFamily = (AWTFontFamily)awtFontFamilies.get(i);
            AWTGVTFont font = (AWTGVTFont)awtFonts.get(i);
            if (font.canDisplay(c) && !fontFamily.getFamilyName().contains("Song")) {
                return fontFamily;
            }
        }

        return null;
    }

    public GVTFontFamily getDefault() {
        return DEFAULT_FONT_FAMILY;
    }

    static {
        fonts.put("sans-serif", "SansSerif");
        fonts.put("serif", "Serif");
        fonts.put("times", "Serif");
        fonts.put("times new roman", "Serif");
        fonts.put("cursive", "Dialog");
        fonts.put("fantasy", "Symbol");
        fonts.put("monospace", "Monospaced");
        fonts.put("monospaced", "Monospaced");
        fonts.put("courier", "Monospaced");

        //
        // Load all fonts. Work around
        //

        GraphicsEnvironment env;
        env = GraphicsEnvironment.getLocalGraphicsEnvironment();
        Locale locale = new Locale("ja","JP");
        String[] fontNames = env.getAvailableFontFamilyNames(locale);

        int nFonts = fontNames != null ? fontNames.length : 0;

        for(int i = 0; i < nFonts; ++i) {
            fonts.put(fontNames[i].toLowerCase(), fontNames[i]);

            // also add the font name with the spaces removed
            StringTokenizer st = new StringTokenizer(fontNames[i]);

            StringBuilder fontNameWithoutSpaces;
            fontNameWithoutSpaces = new StringBuilder();
            while (st.hasMoreTokens()) {
                fontNameWithoutSpaces.append(st.nextToken());
            }

            fonts.put(fontNameWithoutSpaces.toString().toLowerCase(), fontNames[i]);
            String fontNameWithDashes = fontNames[i].replace(' ', '-');
            if (!fontNameWithDashes.equals(fontNames[i])) {
                fonts.put(fontNameWithDashes.toLowerCase(), fontNames[i]);
            }
        }

        Font[] allFonts = env.getAllFonts();
        for (Font f : allFonts) {
            fonts.put(f.getFontName().toLowerCase(), f.getFontName());
        }

        // first add the default font
        awtFontFamilies.add(DEFAULT_FONT_FAMILY);
        awtFonts.add(new AWTGVTFont(DEFAULT_FONT_FAMILY.getFamilyName(), 0, 12));
        Collection fontValues = fonts.values();

        for (Object fontValue : fontValues) {
            String fontFamily = (String) fontValue;
            AWTFontFamily awtFontFamily = new AWTFontFamily(fontFamily);
            awtFontFamilies.add(awtFontFamily);
            AWTGVTFont font = new AWTGVTFont(fontFamily, 0, 12);
            awtFonts.add(font);
        }

        resolvedFontFamilies = new HashMap();
    }
}