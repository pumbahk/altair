/*    */ package jp.co.sej.od.util;
/*    */ 
/*    */ import sun.jvm.hotspot.utilities.UnsupportedPlatformException;

import java.io.UnsupportedEncodingException;
import java.security.MessageDigest;
/*    */ import java.security.NoSuchAlgorithmException;
/*    */ import java.util.Arrays;
/*    */ import java.util.HashMap;
/*    */ import java.util.Map;
/*    */ import java.util.Set;
/*    */ 
/*    */ public final class MD5MessageDigest
/*    */ {
/*    */   private static final String ALGORITHM_MD5 = "MD5";
/*    */ 
/*    */   public static String createHash(Map keys, String privateKey)
/*    */   {
/* 22 */     Map tmpKeys = new HashMap();
/* 23 */     Object[] keyArray = keys.keySet().toArray();
/* 24 */     for (int i = 0; i < keyArray.length; i++) {
/* 25 */       Object value = keys.get(keyArray[i]);
/* 26 */       keyArray[i] = keyArray[i].toString().toLowerCase();
/* 27 */       tmpKeys.put(keyArray[i], value);
/*    */     }
/* 29 */     Arrays.sort(keyArray);
/* 30 */     StringBuffer buf = new StringBuffer();
/* 31 */     for (int i = 0; i < keyArray.length; i++) {
/* 32 */       buf.append(tmpKeys.get(keyArray[i])).append(',');
/*    */     }
/* 34 */     buf.append(privateKey);
/*    */     try
/*    */     {
               System.out.println(buf.toString());
/* 37 */       String xcode= toHexString(MessageDigest.getInstance("MD5").digest(buf.toString().getBytes("UTF-8")));
        System.out.println(xcode);
        return xcode;
/*    */     }
/*    */     catch (NoSuchAlgorithmException e)
/*    */     {
/*    */     }
/*    */     catch (UnsupportedEncodingException e) {

    }
/* 43 */     return null;
/*    */   }
/*    */ 
/*    */   private static String toHexString(byte[] bytes)
/*    */   {
/* 48 */     StringBuffer buf = new StringBuffer();
/* 49 */     int i = 0; for (int max = bytes.length; i < max; i++) {
/* 50 */       int intValue = bytes[i];
/* 51 */       intValue &= 255;
/* 52 */       String str = Integer.toHexString(intValue).toLowerCase();
/* 53 */       if (str.length() == 1) {
/* 54 */         buf.append('0');
/*    */       }
/* 56 */       buf.append(str);
/*    */     }
/* 58 */     return buf.toString();
/*    */   }
/*    */ }

/* Location:           /Users/mistat/Dropbox/Sourcecode/altair-devel/altair/Sej/lib/SejPayment-20100215.002328.jar
 * Qualified Name:     jp.co.sej.od.util.MD5MessageDigest
 * JD-Core Version:    0.6.0
 */