/*     */ package jp.co.sej.od.util;
/*     */ 
/*     */ import java.io.BufferedReader;
/*     */ import java.io.InputStreamReader;
/*     */ import java.io.PrintStream;
/*     */ import java.net.URLDecoder;
/*     */ import java.util.ArrayList;
/*     */ import java.util.logging.Level;
/*     */ import java.util.logging.Logger;
/*     */ import org.apache.commons.cli.CommandLine;
/*     */ import org.apache.commons.cli.CommandLineParser;
/*     */ import org.apache.commons.cli.HelpFormatter;
/*     */ import org.apache.commons.cli.Option;
/*     */ import org.apache.commons.cli.OptionBuilder;
/*     */ import org.apache.commons.cli.Options;
/*     */ import org.apache.commons.cli.PosixParser;
/*     */ 
/*     */ public class SejPaymentSignCheck
/*     */ {
/*     */   private static final String KEY_OPTION_SECRET_KEY = "k";
/*     */   private static final String KEY_OPTION_L_FLG = "l";
/*     */   private static final int RET_OK = 0;
/*     */   private static final int RET_NG = -1;
/*     */   private static final int RET_CHECK_OK = 0;
/*     */   private static final int RET_CHECK_NG = 1;
/*     */ 
/*     */   public static void main(String[] args)
/*     */   {
/*  62 */     Logger.getLogger("org.apache.commons.httpclient").setLevel(Level.SEVERE);
/*     */ 
/*  67 */     Options options = new Options();
/*  68 */     CommandLine commandLine = null;
/*     */ 
/*  70 */     SejPaymentInterface sejpayment = new SejPayment();
/*  71 */     sejpayment.Clear();
/*     */ 
/*  73 */     SejPaymentCommon.PrintLog("started");
/*     */ 
/*  77 */     commandLine = GetOtion(options, args);
/*  78 */     if (commandLine == null) {
/*  79 */       Usage(options);
/*  80 */       SejPaymentCommon.PrintLog("aborted:1");
/*  81 */       System.exit(1);
/*     */     }
/*     */ 
/*  86 */     SetOption(commandLine, sejpayment);
/*     */ 
/*  90 */     if (SetParam(commandLine, sejpayment) != 0) {
/*  91 */       Usage(options);
/*  92 */       SejPaymentCommon.PrintLog("aborted:1");
/*  93 */       System.exit(1);
/*     */     }
/*     */ 
/*     */     try
/*     */     {
/*  99 */       boolean bRtn = sejpayment.CheckSign();
/* 100 */       if (!bRtn) {
/* 101 */         System.out.println(sejpayment.GetErrorMsg());
/* 102 */         SejPaymentCommon.PrintLog("aborted:1");
/* 103 */         System.exit(1);
/*     */       }
/*     */     } catch (Exception e) {
/* 106 */       System.out.println(sejpayment.GetErrorMsg());
/* 107 */       SejPaymentCommon.PrintLog("aborted:1");
/* 108 */       System.exit(1);
/*     */     }
/*     */ 
/* 111 */     SejPaymentCommon.PrintLog("completed");
/* 112 */     System.exit(0);
/*     */   }
/*     */ 
/*     */   private static CommandLine GetOtion(Options _options, String[] _args)
/*     */   {
/* 128 */     SejPaymentCommon.PrintDebugLog(0, "*** GetOtion Start:");
/*     */     try
/*     */     {
/* 134 */       OptionBuilder.hasArg(true);
/* 135 */       OptionBuilder.withArgName("secret key");
/* 136 */       OptionBuilder.isRequired(true);
/* 137 */       OptionBuilder.withDescription("16 bytes secret key. (must be set)");
/* 138 */       Option optionSecretKey = OptionBuilder.create("k");
/* 139 */       _options.addOption(optionSecretKey);
/* 140 */       SejPaymentCommon.PrintDebugLog(0, "    setting option <k>");
/*     */ 
/* 143 */       OptionBuilder.hasArg(false);
/* 144 */       OptionBuilder.withArgName("stdin option");
/* 145 */       OptionBuilder.isRequired(false);
/* 146 */       OptionBuilder.withDescription("Use CR or CR+LF");
/* 147 */       Option optionLFlg = OptionBuilder.create("l");
/* 148 */       _options.addOption(optionLFlg);
/* 149 */       SejPaymentCommon.PrintDebugLog(0, "    setting option <l>");
/*     */ 
/* 152 */       CommandLineParser parser = new PosixParser();
/* 153 */       CommandLine line = parser.parse(_options, _args);
/*     */ 
/* 155 */       SejPaymentCommon.PrintDebugLog(0, "*** GetOtion End: return -> CommandLine");
/* 156 */       return line;
/*     */     }
/*     */     catch (Exception e)
/*     */     {
/* 160 */       SejPaymentCommon.PrintDebugLog(0, "*** GetOtion error: return -> null");
/* 161 */       SejPaymentCommon.PrintDebugLog(0, e);
/* 162 */     }return null;
/*     */   }
/*     */ 
/*     */   private static void SetOption(CommandLine _commandLine, SejPaymentInterface _payment)
/*     */   {
/* 177 */     SejPaymentCommon.PrintDebugLog(0, "*** SetOtion Start:");
/*     */ 
/* 181 */     String sOptShopKey = _commandLine.getOptionValue("k");
/* 182 */     _payment.SetSecretKey(sOptShopKey);
/* 183 */     SejPaymentCommon.PrintDebugLog(0, "    _hmpOptionData.put <k>:" + sOptShopKey);
/* 184 */     SejPaymentCommon.PrintDebugLog(0, "*** SetOtion End:");
/*     */   }
/*     */ 
/*     */   private static int SetParam(CommandLine _commandLine, SejPaymentInterface _payment)
/*     */   {
/* 200 */     SejPaymentCommon.PrintDebugLog(0, "*** SetParam Start:");
/*     */     try
/*     */     {
/* 203 */       ArrayList aryParam = new ArrayList();
/* 204 */       ArrayList aryCommandLine = new ArrayList(_commandLine.getArgList());
/*     */ 
/* 207 */       if ((aryCommandLine.size() > 0) && (_commandLine.hasOption("l"))) {
/* 208 */         System.out.println("Bad parameter:l");
/* 209 */         SejPaymentCommon.PrintDebugLog(0, "*** SetParam error: return -> NG");
/* 210 */         return -1;
/*     */       }
/*     */ 
/* 214 */       if (aryCommandLine.size() == 0) {
/* 215 */         SejPaymentCommon.PrintDebugLog(0, "    input param system in");
/*     */ 
/* 217 */         BufferedReader in = new BufferedReader(new InputStreamReader(System.in));
/* 218 */         String sParam = null;
/*     */ 
/* 221 */         if (_commandLine.hasOption("l")) {
/* 222 */           int iCount = 1;
/*     */           while (true) {
/* 224 */             sParam = in.readLine();
/*     */ 
/* 227 */             if ((sParam == null) || (sParam.length() <= 0))
/*     */             {
/*     */               break;
/*     */             }
/* 231 */             aryParam.add(sParam);
/* 232 */             iCount++;
/*     */           }
/*     */         } else {
/* 235 */           sParam = in.readLine();
/* 236 */           if ((sParam != null) && 
/* 237 */             (sParam.length() > 0)) {
/* 238 */             String[] argc = sParam.split("&");
/* 239 */             for (int i = 0; i < argc.length; i++) {
/* 240 */               aryParam.add(argc[i]);
/*     */             }
/*     */           }
/*     */         }
/*     */ 
/* 245 */         in.close();
/*     */       }
/*     */       else
/*     */       {
/* 249 */         SejPaymentCommon.PrintDebugLog(0, "    input param command line");
/* 250 */         String arg = (String)aryCommandLine.get(0);
/* 251 */         String[] argc = arg.split("&");
/* 252 */         for (int i = 0; i < argc.length; i++) {
/* 253 */           aryParam.add(argc[i]);
/*     */         }
/*     */ 
/*     */       }
/*     */ 
/* 258 */       for (int i = 0; i < aryParam.size(); i++) {
/* 259 */         System.out.println("==> " + aryParam.get(i));
/*     */       }
/*     */ 
/* 263 */       String sParam = null;
/* 264 */       for (int i = 0; i < aryParam.size(); i++) {
/* 265 */         sParam = String.valueOf(aryParam.get(i));
/*     */ 
/* 267 */         int equal_dist = sParam.indexOf("=");
/*     */ 
/* 269 */         if (equal_dist > 0)
/*     */         {
/* 271 */           String buffer_key = "";
/* 272 */           String buffer_value = "";
/* 273 */           if (!_commandLine.hasOption("l")) {
/* 274 */             buffer_key = URLDecoder.decode(sParam.substring(0, equal_dist), "Windows-31J");
/* 275 */             buffer_value = URLDecoder.decode(sParam.substring(equal_dist + 1), "Windows-31J");
/*     */           } else {
/* 277 */             buffer_key = sParam.substring(0, equal_dist);
/* 278 */             buffer_value = sParam.substring(equal_dist + 1);
/*     */           }
/*     */ 
/* 282 */           _payment.Addinput(buffer_key, buffer_value);
/* 283 */           SejPaymentCommon.PrintDebugLog(0, "    input key:" + buffer_key + "    " + "input value:" + buffer_value);
/*     */         }
/*     */         else
/*     */         {
/* 288 */           System.out.println("Bad parameter:" + sParam);
/* 289 */           SejPaymentCommon.PrintDebugLog(0, "*** SetParam error: return -> NG");
/* 290 */           return -1;
/*     */         }
/*     */       }
/*     */ 
/* 294 */       SejPaymentCommon.PrintDebugLog(0, "*** SetParam End: return -> OK");
/* 295 */       return 0;
/*     */     }
/*     */     catch (Exception e)
/*     */     {
/* 299 */       System.out.print("Param read failed:");
/* 300 */       System.out.println(e);
/* 301 */       SejPaymentCommon.PrintDebugLog(0, "*** SetParam error: return -> NG");
/* 302 */     }return -1;
/*     */   }
/*     */ 
/*     */   private static void Usage(Options _options)
/*     */   {
/* 312 */     SejPaymentCommon.PrintDebugLog(0, "*** Usage Start");
/*     */ 
/* 315 */     System.out.println("========================================================================");
/* 316 */     System.out.println("======     SejPaymentSignCheck                                    ======");
/* 317 */     System.out.println("========================================================================");
/* 318 */     System.out.println("              Copyright (C) Nomura Research Institute,Ltd.              ");
/* 319 */     System.out.println("                                                                        ");
/*     */ 
/* 322 */     HelpFormatter helpFormatter = new HelpFormatter();
/* 323 */     helpFormatter.printHelp("\njava [-java options] jp.co.sej.od.util.SejPaymentSignCheck [flags] form_data \njava [-java options] jp.co.sej.od.util.SejPaymentSignCheck [flags] (params come from stdin)", _options);
/*     */ 
/* 325 */     SejPaymentCommon.PrintDebugLog(0, "*** Usage End:");
/*     */   }
/*     */ }

/* Location:           /Users/mistat/Dropbox/Sourcecode/altair-devel/altair/Sej/lib/SejPayment-20100215.002328.jar
 * Qualified Name:     jp.co.sej.od.util.SejPaymentSignCheck
 * JD-Core Version:    0.6.0
 */