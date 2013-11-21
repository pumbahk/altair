package jp.ticketstar.ticketing.gvt.font;

import java.awt.GraphicsEnvironment;
import java.util.Collection;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.StringTokenizer;
import java.util.List;
import java.util.ArrayList;
import java.util.Locale;

import org.apache.batik.gvt.font.FontFamilyResolver;
import org.apache.batik.gvt.font.AWTFontFamily;
import org.apache.batik.gvt.font.AWTGVTFont;


/*

Using locale = ja_JP;
 */

public class FontFamilyResolverPatch extends FontFamilyResolver {
    static {
        /* refresh */
        fonts.clear();
        awtFontFamilies.clear();
        awtFonts.clear();

        // almost copy: batik-1.7/sources/org/apache/batik/gvt/font/FontFamilyResolver.java

        fonts.put("sans-serif",      "SansSerif");
        fonts.put("serif",           "Serif");
        fonts.put("times",           "Serif");
        fonts.put("times new roman", "Serif");
        fonts.put("cursive",         "Dialog");
        fonts.put("fantasy",         "Symbol");
        fonts.put("monospace",       "Monospaced");
        fonts.put("monospaced",      "Monospaced");
        fonts.put("courier",         "Monospaced");

        //
        // Load all fonts. Work around
        //

        GraphicsEnvironment env;
        env = GraphicsEnvironment.getLocalGraphicsEnvironment();
        Locale locale = new Locale("ja","JP");
        String[] fontNames = env.getAvailableFontFamilyNames(locale);

        int nFonts = fontNames != null ? fontNames.length : 0;
        for(int i=0; i<nFonts; i++){
            fonts.put(fontNames[i].toLowerCase(), fontNames[i]);

            // also add the font name with the spaces removed
            StringTokenizer st = new StringTokenizer(fontNames[i]);
            String fontNameWithoutSpaces = "";
            while (st.hasMoreTokens()) {
                fontNameWithoutSpaces += st.nextToken();
            }
            fonts.put(fontNameWithoutSpaces.toLowerCase(), fontNames[i]);

            // also add the font name with spaces replaced by dashes
            String fontNameWithDashes = fontNames[i].replace(' ', '-');
            if (!fontNameWithDashes.equals(fontNames[i])) {
               fonts.put(fontNameWithDashes.toLowerCase(), fontNames[i]);
            }
        }
        // first add the default font
        awtFontFamilies.add(defaultFont);
        awtFonts.add(new AWTGVTFont(defaultFont.getFamilyName(), 0, 12));

        Collection fontValues = fonts.values();
        Iterator iter = fontValues.iterator();
        while(iter.hasNext()) {
            String fontFamily = (String)iter.next();
            AWTFontFamily awtFontFamily = new AWTFontFamily(fontFamily);
            awtFontFamilies.add(awtFontFamily);
            AWTGVTFont font = new AWTGVTFont(fontFamily, 0, 12);
            awtFonts.add(font);
        }

    }
}
