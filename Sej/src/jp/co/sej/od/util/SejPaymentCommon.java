/*     */ package jp.co.sej.od.util;
/*     */ 
/*     */ import java.io.BufferedReader;
/*     */ import java.io.FileInputStream;
/*     */ import java.io.InputStreamReader;
/*     */ import java.io.PrintStream;
/*     */ import java.text.SimpleDateFormat;
/*     */ import java.util.ArrayList;
/*     */ import java.util.Date;
/*     */ import java.util.Properties;
/*     */ import org.apache.commons.cli.CommandLine;
/*     */ import org.apache.commons.cli.CommandLineParser;
/*     */ import org.apache.commons.cli.Option;
/*     */ import org.apache.commons.cli.OptionBuilder;
/*     */ import org.apache.commons.cli.Options;
/*     */ import org.apache.commons.cli.PosixParser;
/*     */ 
/*     */ public class SejPaymentCommon
/*     */ {
/*     */   public static final int DEBUG_FLG = 0;
/*     */   private static final String KEY_OPTION_SECRET_KEY = "k";
/*     */   private static final String KEY_OPTION_PROXY_SERVER = "p";
/*     */   private static final String KEY_OPTION_PROXY_USER_AND_PASSWORD = "u";
/*     */   private static final String KEY_OPTION_CONF_FILE_PATH = "c";
/*     */   private static final String KEY_CONF_RETRY_COUNT = "RETRY_COUNT";
/*     */   private static final String KEY_CONF_RETRY_INTERVAL = "RETRY_INTERVAL";
/*     */   private static final String KEY_CONF_TIMEOUT = "TIMEOUT";
/*     */   private static final int RET_OK = 0;
/*     */   private static final int RET_NG = -1;
/*     */   protected static final int RET_NG_PARAM = 1;
/*     */   protected static final int RET_NG_ELSE = 999;
/*  60 */   private static String m_ConfFileName = "";
/*     */ 
/*     */   public static CommandLine GetOtion(Options _options, String[] _args)
/*     */   {
/*  74 */     PrintDebugLog(0, "*** GetOtion Start:");
/*     */     try
/*     */     {
/*  80 */       OptionBuilder.hasArg(true);
/*  81 */       OptionBuilder.withArgName("secret key");
/*  82 */       OptionBuilder.isRequired(true);
/*  83 */       OptionBuilder.withDescription("16 bytes secret key. (must be set)");
/*  84 */       Option optionSecretKey = OptionBuilder.create("k");
/*  85 */       _options.addOption(optionSecretKey);
/*  86 */       PrintDebugLog(0, "    setting option <k>");
/*     */ 
/*  89 */       OptionBuilder.hasArg(true);
/*  90 */       OptionBuilder.withArgName("proxy host");
/*  91 */       OptionBuilder.isRequired(false);
/*  92 */       OptionBuilder.withDescription("Use proxy server. (ex. -p http://www.proxy.com:8080)");
/*  93 */       Option optionProxyUrl = OptionBuilder.create("p");
/*  94 */       _options.addOption(optionProxyUrl);
/*  95 */       PrintDebugLog(0, "    setting option <p>");
/*     */ 
/*  98 */       OptionBuilder.hasArg(true);
/*  99 */       OptionBuilder.withArgName("proxy user/pwd");
/* 100 */       OptionBuilder.isRequired(false);
/* 101 */       OptionBuilder.withDescription("Use proxy authorization. (ex. -u user:pwd)");
/* 102 */       Option optionProxyUserAndPssword = OptionBuilder.create("u");
/* 103 */       _options.addOption(optionProxyUserAndPssword);
/* 104 */       PrintDebugLog(0, "    setting option <u>");
/*     */ 
/* 107 */       OptionBuilder.hasArg(true);
/* 108 */       OptionBuilder.withArgName("config file");
/* 109 */       OptionBuilder.isRequired(false);
/* 110 */       OptionBuilder.withDescription("Specify config file path.");
/* 111 */       Option optionConfFileName = OptionBuilder.create("c");
/* 112 */       _options.addOption(optionConfFileName);
/* 113 */       PrintDebugLog(0, "    setting option <c>");
/*     */ 
/* 117 */       CommandLineParser parser = new PosixParser();
/* 118 */       CommandLine line = parser.parse(_options, _args);
/*     */ 
/* 120 */       PrintDebugLog(0, "*** GetOtion End: return -> CommandLine");
/* 121 */       return line;
/*     */     }
/*     */     catch (Exception e)
/*     */     {
/* 125 */       PrintDebugLog(0, "*** GetOtion error: return -> null");
/* 126 */       PrintDebugLog(0, e);
/* 127 */     }return null;
/*     */   }
/*     */ 
/*     */   public static void SetOption(CommandLine _commandLine, SejPaymentInterface _payment)
/*     */   {
/* 141 */     PrintDebugLog(0, "*** SetOtion Start:");
/*     */ 
/* 145 */     String sOptShopKey = _commandLine.getOptionValue("k");
/* 146 */     _payment.SetSecretKey(sOptShopKey);
/* 147 */     PrintDebugLog(0, "    _hmpOptionData.put <k>:" + sOptShopKey);
/*     */ 
/* 150 */     if (_commandLine.hasOption("p")) {
/* 151 */       String sOptProxy = _commandLine.getOptionValue("p");
/* 152 */       PrintDebugLog(0, "    _hmpOptionData.put <p>:" + sOptProxy);
/* 153 */       int idx = sOptProxy.lastIndexOf(":");
/* 154 */       if (idx > 0)
/*     */       {
/* 157 */         String sOptProxyPort = sOptProxy.substring(idx + 1);
/* 158 */         String sOptProxyServer = sOptProxy.substring(0, idx);
/*     */         try {
/* 160 */           int iPort = Integer.parseInt(sOptProxyPort);
/* 161 */           _payment.SetProxyServerPort(iPort);
/* 162 */           _payment.SetProxyServerHost(sOptProxyServer);
/*     */         }
/*     */         catch (Exception e) {
/* 165 */           _payment.SetProxyServerHost(sOptProxy);
/*     */         }
/*     */       }
/*     */       else {
/* 169 */         _payment.SetProxyServerHost(sOptProxy);
/*     */       }
/*     */     }
/*     */ 
/* 173 */     if (_commandLine.hasOption("u")) {
/* 174 */       String sOptProxyUserPwd = _commandLine.getOptionValue("u");
/* 175 */       _payment.SetProxyAuth(sOptProxyUserPwd);
/* 176 */       PrintDebugLog(0, "    _hmpOptionData.put <u>:" + sOptProxyUserPwd);
/*     */     }
/*     */ 
/* 180 */     if (_commandLine.hasOption("c")) {
/* 181 */       String sConfFileName = _commandLine.getOptionValue("c");
/* 182 */       m_ConfFileName = sConfFileName;
/* 183 */       PrintDebugLog(0, "    _hmpOptionData.put <c>:" + m_ConfFileName);
/*     */     }
/*     */ 
/* 186 */     PrintDebugLog(0, "*** SetOtion End:");
/*     */   }
/*     */ 
/*     */   public static int CheckParam(CommandLine _commandLine)
/*     */   {
/* 200 */     PrintDebugLog(0, "*** CheckParam Start:");
/*     */ 
/* 203 */     ArrayList aryCommandLine = new ArrayList(_commandLine.getArgList());
/*     */ 
/* 206 */     if (aryCommandLine.size() <= 0) {
/* 207 */       PrintDebugLog(0, "*** SetParam error:size check");
/* 208 */       PrintDebugLog(0, "*** CheckParam error:size check : return -> NG");
/* 209 */       return -1;
/*     */     }
/* 211 */     PrintDebugLog(0, "    size check ok");
/*     */ 
/* 214 */     PrintDebugLog(0, "*** CheckParam End: return -> OK");
/* 215 */     return 0;
/*     */   }
/*     */ 
/*     */   public static int SetParam(CommandLine _commandLine, SejPaymentInterface _payment)
/*     */   {
/* 232 */     PrintDebugLog(0, "*** SetParam Start:");
/*     */     try
/*     */     {
/* 235 */       ArrayList aryParam = null;
/*     */ 
/* 238 */       ArrayList aryCommandLine = new ArrayList(_commandLine.getArgList());
/*     */ 
/* 242 */       String _sURL = String.valueOf(aryCommandLine.get(0));
/* 243 */       _payment.SetURL(_sURL);
/*     */ 
/* 246 */       if (aryCommandLine.size() == 1) {
/* 247 */         PrintDebugLog(0, "    input param system in");
/*     */ 
/* 249 */         BufferedReader in = new BufferedReader(new InputStreamReader(System.in));
/* 250 */         String sParam = null;
/* 251 */         aryParam = new ArrayList();
/*     */ 
/* 253 */         int iCount = 1;
/*     */         while (true) {
/* 255 */           sParam = in.readLine();
/*     */ 
/* 258 */           if ((sParam == null) || (sParam.length() <= 0))
/*     */           {
/*     */             break;
/*     */           }
/* 262 */           aryParam.add(sParam);
/* 263 */           iCount++;
/*     */         }
/* 265 */         in.close();
/*     */       }
/*     */       else
/*     */       {
/* 269 */         PrintDebugLog(0, "    input param command line");
/*     */ 
/* 271 */         aryParam = new ArrayList(aryCommandLine.subList(1, aryCommandLine.size()));
/*     */       }
/*     */ 
/* 274 */       for (int i = 0; i < aryParam.size(); i++) {
/* 275 */         System.out.println("==> " + aryParam.get(i));
/*     */       }
/*     */ 
/* 279 */       String sParam = null;
/* 280 */       for (int i = 0; i < aryParam.size(); i++) {
/* 281 */         sParam = String.valueOf(aryParam.get(i));
/*     */ 
/* 283 */         int equal_dist = sParam.indexOf("=");
/*     */ 
/* 285 */         if (equal_dist > 0)
/*     */         {
/* 287 */           String buffer_key = sParam.substring(0, equal_dist);
/* 288 */           String buffer_value = sParam.substring(equal_dist + 1);
/*     */ 
/* 290 */           _payment.Addinput(buffer_key, buffer_value);
/* 291 */           PrintDebugLog(0, "    input key:" + buffer_key + "    " + "input value:" + buffer_value);
/*     */         }
/*     */         else
/*     */         {
/* 296 */           System.out.println("Bad parameter:" + sParam);
/* 297 */           PrintDebugLog(0, "*** SetParam error: return -> NG");
/* 298 */           return -1;
/*     */         }
/*     */       }
/*     */ 
/* 302 */       PrintDebugLog(0, "*** SetParam End: return -> OK");
/* 303 */       return 0;
/*     */     }
/*     */     catch (Exception e)
/*     */     {
/* 307 */       System.out.print("Param read failed:");
/* 308 */       System.out.println(e);
/* 309 */       PrintDebugLog(0, "*** SetParam error: return -> NG");
/* 310 */     }return -1;
/*     */   }
/*     */ 
/*     */   public static int SetConf(SejPaymentInterface _payment)
/*     */   {
/* 326 */     PrintDebugLog(0, "*** SetConf Start:");
/*     */     try
/*     */     {
/* 331 */       if (m_ConfFileName.equals(""))
/*     */       {
/* 333 */         PrintDebugLog(0, "    no setting conf path");
/* 334 */         PrintDebugLog(0, "*** SetConf End: return -> OK");
/* 335 */         return 0;
/*     */       }
/*     */ 
/* 339 */       Properties p = new Properties();
/* 340 */       FileInputStream fis = new FileInputStream(m_ConfFileName);
/* 341 */       p.load(fis);
/* 342 */       fis.close();
/*     */ 
/* 346 */       String sRetryCount = p.getProperty("RETRY_COUNT");
/* 347 */       if ((sRetryCount != null) && (sRetryCount.length() > 0)) {
/* 348 */         _payment.SetRetryCount(Integer.parseInt(sRetryCount));
/* 349 */         PrintDebugLog(0, "    _hmpConfData.put<RETRY_COUNT>:" + sRetryCount);
/*     */       }
/*     */ 
/* 352 */       String sRetryInterval = p.getProperty("RETRY_INTERVAL");
/* 353 */       if ((sRetryInterval != null) && (sRetryInterval.length() > 0)) {
/* 354 */         _payment.SetRetryInterval(Integer.parseInt(sRetryInterval));
/* 355 */         PrintDebugLog(0, "    _hmpConfData.put<RETRY_INTERVAL>:" + sRetryInterval);
/*     */       }
/*     */ 
/* 358 */       String sTimeOut = p.getProperty("TIMEOUT");
/* 359 */       if ((sTimeOut != null) && (sTimeOut.length() > 0)) {
/* 360 */         _payment.SetTimeOut(Integer.parseInt(sTimeOut));
/* 361 */         PrintDebugLog(0, "    _hmpConfData.put<TIMEOUT>:" + sTimeOut);
/*     */       }
/* 363 */       PrintDebugLog(0, "*** SetConf End: return -> OK");
/* 364 */       return 0;
/*     */     }
/*     */     catch (Exception e)
/*     */     {
/* 368 */       System.out.print("Config File read failed:");
/* 369 */       System.out.println(e);
/*     */ 
/* 371 */       PrintDebugLog(0, e);
/* 372 */       PrintDebugLog(0, "*** SetConf error: return -> NG");
/* 373 */     }return -1;
/*     */   }
/*     */ 
/*     */   public static void PrintDebugLog(int _DebugFlg, Object _objDebugMsg)
/*     */   {
/* 383 */     if (_DebugFlg == 1)
/* 384 */       System.out.println(_objDebugMsg);
/*     */   }
/*     */ 
/*     */   public static void PrintLog(String _msg)
/*     */   {
/* 390 */     Date nowDate = new Date();
/* 391 */     SimpleDateFormat sdf1 = new SimpleDateFormat("yyyy/MM/dd HH:mm:ss");
/* 392 */     System.out.println(" [" + sdf1.format(nowDate) + "] " + _msg + ". ==");
/*     */   }
/*     */ }

/* Location:           /Users/mistat/Dropbox/Sourcecode/altair-devel/altair/Sej/lib/SejPayment-20100215.002328.jar
 * Qualified Name:     jp.co.sej.od.util.SejPaymentCommon
 * JD-Core Version:    0.6.0
 */