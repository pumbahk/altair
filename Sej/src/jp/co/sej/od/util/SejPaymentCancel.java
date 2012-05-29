/*     */ package jp.co.sej.od.util;
/*     */ 
/*     */ import java.io.PrintStream;
/*     */ import java.util.logging.Level;
/*     */ import java.util.logging.Logger;
/*     */ import org.apache.commons.cli.CommandLine;
/*     */ import org.apache.commons.cli.HelpFormatter;
/*     */ import org.apache.commons.cli.Options;
/*     */ 
/*     */ public class SejPaymentCancel
/*     */ {
/*     */   public static void main(String[] args)
/*     */   {
/*  43 */     Logger.getLogger("org.apache.commons.httpclient").setLevel(Level.SEVERE);
/*     */ 
/*  48 */     Options options = new Options();
/*  49 */     CommandLine commandLine = null;
/*     */ 
/*  51 */     SejPaymentInterface sejpayment = new SejPayment();
/*  52 */     sejpayment.Clear();
/*     */ 
/*  54 */     SejPaymentCommon.PrintLog("started");
/*     */ 
/*  58 */     commandLine = SejPaymentCommon.GetOtion(options, args);
/*  59 */     if (commandLine == null) {
/*  60 */       Usage(options);
/*  61 */       SejPaymentCommon.PrintLog("aborted:1");
/*  62 */       System.exit(1);
/*     */     }
/*     */ 
/*  67 */     if (SejPaymentCommon.CheckParam(commandLine) != 0) {
/*  68 */       Usage(options);
/*  69 */       SejPaymentCommon.PrintLog("aborted:1");
/*  70 */       System.exit(1);
/*     */     }
/*     */ 
/*  75 */     SejPaymentCommon.SetOption(commandLine, sejpayment);
/*     */ 
/*  79 */     if (SejPaymentCommon.SetParam(commandLine, sejpayment) != 0) {
/*  80 */       Usage(options);
/*  81 */       SejPaymentCommon.PrintLog("aborted:1");
/*  82 */       System.exit(1);
/*     */     }
/*     */ 
/*  87 */     if (SejPaymentCommon.SetConf(sejpayment) != 0) {
/*  88 */       Usage(options);
/*  89 */       SejPaymentCommon.PrintLog("aborted:1");
/*  90 */       System.exit(1);
/*     */     }
/*     */ 
/*     */     try
/*     */     {
/*  96 */       int iRtn = sejpayment.Request(false);
/*  97 */       if (iRtn != 0) {
/*  98 */         System.out.println(sejpayment.GetErrorMsg());
/*  99 */         SejPaymentCommon.PrintLog("aborted:" + iRtn);
/* 100 */         System.exit(iRtn);
/*     */       }
/*     */     } catch (Exception e) {
/* 103 */       System.out.println(sejpayment.GetErrorMsg());
/* 104 */       SejPaymentCommon.PrintLog("aborted:999");
/* 105 */       System.exit(999);
/*     */     }
/*     */ 
/* 108 */     SejPaymentCommon.PrintLog("completed");
/* 109 */     System.exit(0);
/*     */   }
/*     */ 
/*     */   private static void Usage(Options _options)
/*     */   {
/* 118 */     SejPaymentCommon.PrintDebugLog(0, "*** Usage Start");
/*     */ 
/* 121 */     System.out.println("========================================================================");
/* 122 */     System.out.println("========     SejPaymentCancel                                   ========");
/* 123 */     System.out.println("========================================================================");
/* 124 */     System.out.println("              Copyright (C) Nomura Research Institute,Ltd.              ");
/* 125 */     System.out.println("                                                                        ");
/*     */ 
/* 128 */     HelpFormatter helpFormatter = new HelpFormatter();
/* 129 */     helpFormatter.printHelp("\njava [-java options] jp.co.sej.od.util.SejPaymentCancel [flags] url params.... \njava [-java options] jp.co.sej.od.util.SejPaymentCancel [flags] url (params come from stdin)", _options);
/*     */ 
/* 131 */     SejPaymentCommon.PrintDebugLog(0, "*** Usage End:");
/*     */   }
/*     */ }

/* Location:           /Users/mistat/Dropbox/Sourcecode/altair-devel/altair/Sej/lib/SejPayment-20100215.002328.jar
 * Qualified Name:     jp.co.sej.od.util.SejPaymentCancel
 * JD-Core Version:    0.6.0
 */