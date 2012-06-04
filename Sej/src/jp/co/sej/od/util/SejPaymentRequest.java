/*     */ package jp.co.sej.od.util;
/*     */ 
/*     */ import java.io.PrintStream;
/*     */ import java.util.logging.Level;
/*     */ import java.util.logging.Logger;
/*     */ import org.apache.commons.cli.CommandLine;
/*     */ import org.apache.commons.cli.HelpFormatter;
/*     */ import org.apache.commons.cli.Option;
/*     */ import org.apache.commons.cli.OptionBuilder;
/*     */ import org.apache.commons.cli.Options;
/*     */ 
/*     */ public class SejPaymentRequest
/*     */ {
/*     */   private static final String KEY_OPTION_RESEND_FLG = "R";
/*     */ 
/*     */   public static void main(String[] args)
/*     */   {
/*  47 */     Logger.getLogger("org.apache.commons.httpclient").setLevel(Level.SEVERE);
/*     */ 
/*  52 */     Options options = new Options();
/*  53 */     CommandLine commandLine = null;
/*     */ 
/*  55 */     SejPaymentInterface sejpayment = new SejPayment();
/*  56 */     sejpayment.Clear();
/*     */ 
/*  58 */     SejPaymentCommon.PrintLog("started");
/*     */ 
/*  62 */     commandLine = GetOtion(options, args);
/*  63 */     if (commandLine == null) {
/*  64 */       Usage(options);
/*  65 */       SejPaymentCommon.PrintLog("aborted:1");
/*  66 */       System.exit(1);
/*     */     }
/*     */ 
/*  71 */     if (SejPaymentCommon.CheckParam(commandLine) != 0) {
/*  72 */       Usage(options);
/*  73 */       SejPaymentCommon.PrintLog("aborted:1");
/*  74 */       System.exit(1);
/*     */     }
/*     */ 
/*  79 */     SejPaymentCommon.SetOption(commandLine, sejpayment);
/*     */ 
/*  83 */     if (SejPaymentCommon.SetParam(commandLine, sejpayment) != 0) {
/*  84 */       Usage(options);
/*  85 */       SejPaymentCommon.PrintLog("aborted:1");
/*  86 */       System.exit(1);
/*     */     }
/*     */ 
/*  91 */     if (SejPaymentCommon.SetConf(sejpayment) != 0) {
/*  92 */       Usage(options);
/*  93 */       SejPaymentCommon.PrintLog("aborted:1");
/*  94 */       System.exit(1);
/*     */     }
/*     */     try
/*     */     {
/*  98 */       boolean resendFlg = false;
/*  99 */       if (commandLine.hasOption("R")) {
/* 100 */         resendFlg = true;
/*     */       }
/*     */ 
/* 104 */       int iRtn = sejpayment.Request(resendFlg);
/* 105 */       if (iRtn != 0) {
/* 106 */         System.out.println(sejpayment.GetErrorMsg());
/* 107 */         SejPaymentCommon.PrintLog("aborted:" + iRtn);
/* 108 */         System.exit(iRtn);
/*     */       }
/*     */     } catch (Exception e) {
/* 111 */       System.out.println(sejpayment.GetErrorMsg());
/* 112 */       SejPaymentCommon.PrintLog("aborted:999");
/* 113 */       System.exit(999);
/*     */     }
/*     */ 
/* 118 */     String outMesg = sejpayment.GetOutputAll();
/* 119 */     if ((outMesg != null) && (outMesg.length() > 0)) {
/* 120 */       System.out.println(outMesg);
/* 121 */       SejPaymentCommon.PrintLog("completed");
/* 122 */       System.exit(0);
/*     */     } else {
/* 124 */       System.out.println(sejpayment.GetErrorMsg());
/* 125 */       SejPaymentCommon.PrintLog("aborted:999");
/* 126 */       System.exit(999);
/*     */     }
/*     */   }
/*     */ 
/*     */   protected static CommandLine GetOtion(Options _options, String[] _args)
/*     */   {
/* 143 */     CommandLine commandline = null;
/*     */ 
/* 146 */     OptionBuilder.hasArg(false);
/* 147 */     OptionBuilder.withArgName(" ");
/* 148 */     OptionBuilder.isRequired(false);
/* 149 */     OptionBuilder.withDescription("Retry the request.");
/* 150 */     Option optionReSendFlg = OptionBuilder.create("R");
/* 151 */     _options.addOption(optionReSendFlg);
/*     */ 
/* 155 */     commandline = SejPaymentCommon.GetOtion(_options, _args);
/* 156 */     return commandline;
/*     */   }
/*     */ 
/*     */   private static void Usage(Options _options)
/*     */   {
/* 165 */     SejPaymentCommon.PrintDebugLog(0, "*** Usage Start");
/*     */ 
/* 168 */     System.out.println("========================================================================");
/* 169 */     System.out.println("=======     SejPaymentRequest                                    =======");
/* 170 */     System.out.println("========================================================================");
/* 171 */     System.out.println("              Copyright (C) Nomura Research Institute,Ltd.              ");
/* 172 */     System.out.println("                                                                        ");
/*     */ 
/* 175 */     HelpFormatter helpFormatter = new HelpFormatter();
/* 176 */     helpFormatter.printHelp("\njava [-java options] jp.co.sej.od.util.SejPaymentRequest [flags] url params.... \njava [-java options] jp.co.sej.od.util.SejPaymentRequest [flags] url (params come from stdin)", _options);
/*     */ 
/* 178 */     SejPaymentCommon.PrintDebugLog(0, "*** Usage End:");
/*     */   }
/*     */ }

/* Location:           /Users/mistat/Dropbox/Sourcecode/altair-devel/altair/Sej/lib/SejPayment-20100215.002328.jar
 * Qualified Name:     jp.co.sej.od.util.SejPaymentRequest
 * JD-Core Version:    0.6.0
 */