/*      */ package jp.co.sej.od.util;
/*      */ 
/*      */ import java.io.BufferedReader;
/*      */ import java.io.FileInputStream;
/*      */ import java.io.FileNotFoundException;
/*      */ import java.io.FileOutputStream;
/*      */ import java.io.InputStream;
/*      */ import java.io.InputStreamReader;
/*      */ import java.io.PrintStream;
/*      */ import java.net.URL;
/*      */ import java.text.SimpleDateFormat;
/*      */ import java.util.ArrayList;
/*      */ import java.util.Date;
/*      */ import java.util.HashMap;
/*      */ import java.util.Iterator;
/*      */ import java.util.Properties;
/*      */ import java.util.Set;
/*      */ import java.util.StringTokenizer;
/*      */ import java.util.logging.Level;
/*      */ import java.util.logging.Logger;
/*      */ import java.util.zip.Inflater;
/*      */ import java.util.zip.InflaterInputStream;
/*      */ import org.apache.commons.cli.CommandLine;
/*      */ import org.apache.commons.cli.CommandLineParser;
/*      */ import org.apache.commons.cli.HelpFormatter;
/*      */ import org.apache.commons.cli.Option;
/*      */ import org.apache.commons.cli.OptionBuilder;
/*      */ import org.apache.commons.cli.Options;
/*      */ import org.apache.commons.cli.PosixParser;
/*      */ 
/*      */ public class SejPaymentGetFile
/*      */ {
/*      */   private static final int DEBUG_FLG = 0;
/*      */   private static final int RES_STATUS_NOMAL = 200;
/*      */   private static final int RES_STATUS_OK = 800;
/*      */   private static final int RES_STATUS_NG_WWW = 500;
/*      */   private static final int RES_STATUS_NG_ASP = 900;
/*      */   private static final int RES_STATUS_NG_INPUT = 902;
/*      */   private static final int RES_STATUS_NG_NO_DATA = 911;
/*      */   private static final int RES_STATUS_NG_SYSTEM = 920;
/*      */   private static final String HEADER_REQ_USER_AGENT = "SejPaymentForJava/2.00";
/*      */   private static final String HEADER_RES_FILESIZE_ORG = "Filesize-Org";
/*      */   private static final String HEADER_RES_FILESIZE_ZIP = "Filesize-Zip";
/*      */   private static final String HEADER_RES_CONTENT_TYPE = "Content-Type";
/*      */   private static final String KEY_OPTION_SECRET_KEY = "k";
/*      */   private static final String KEY_OPTION_OUTPUT_FILE_PATH = "o";
/*      */   private static final String KEY_OPTION_PROXY_SERVER = "p";
/*      */   private static final String KEY_OPTION_PROXY_USER_AND_PASSWORD = "u";
/*      */   private static final String KEY_OPTION_CONF_FILE_PATH = "c";
/*      */   private static final String KEY_CONF_RETRY_COUNT = "RETRY_COUNT";
/*      */   private static final String KEY_CONF_RETRY_INTERVAL = "RETRY_INTERVAL";
/*      */   private static final String KEY_CONF_TIMEOUT = "TIMEOUT";
/*      */   private static final String KEY_PROXY_HOST = "HOST";
/*      */   private static final String KEY_PROXY_PORT = "PORT";
/*      */   private static final String KEY_PROXY_AUTH = "AUTH";
/*      */   private static final String KEY_INPUT_URL = "URL";
/*      */   private static final String DATA_TAGNAME = "SENBDATA";
/*      */   private static final String EOF_STRING = "DATA=END";
/*      */   private static final int RET_OK = 0;
/*      */   private static final int RET_NG = -1;
/*      */   private static final int RET_NG_PARAM = 1;
/*      */   private static final int RET_NG_URL_PROXY = 4;
/*      */   private static final int RET_NG_WWW_SERVER = 5;
/*      */   private static final int RET_NG_CONNECTION = 10;
/*      */   private static final int RET_NG_RECEIVE_DATA = 11;
/*      */   private static final int RET_NG_SIGNATURE = 101;
/*      */   private static final int RET_NG_INPUT_DATA = 102;
/*      */   private static final int RET_NG_NO_RECEIVE = 111;
/*      */   private static final int RET_NG_ELSE = 999;
/*      */   private static final int INIT_RETRY_COUNT = 5;
/*      */   private static final int INIT_RETRY_INTERVAL = 5000;
/*      */   private static final int INIT_TIMEOUT = 30000;
/*      */   private static final String INIT_PROXY_HOST = "";
/*      */   private static final int INIT_PROXY_PORT = -1;
/*      */ 
/*      */   public static void main(String[] args)
/*      */   {
/*  136 */     Logger.getLogger("org.apache.commons.httpclient").setLevel(Level.SEVERE);
/*      */ 
/*  141 */     HashMap hmpOptionData = new HashMap();
/*  142 */     HashMap hmpParamData = new HashMap();
/*  143 */     HashMap hmpConfData = new HashMap();
/*      */ 
/*  145 */     HashMap hmpSendData = new HashMap();
/*      */ 
/*  147 */     int iRet = 0;
/*      */ 
/*  149 */     Options options = new Options();
/*  150 */     CommandLine commandLine = null;
/*  151 */     HttpClientUtil httpCilentUtil = null;
/*      */ 
/*  158 */     commandLine = GetOtion(options, args);
/*  159 */     if (commandLine == null)
/*      */     {
/*  161 */       Usage(options);
/*      */ 
/*  163 */       PrintDebugLog(0, "---->戻り値:1");
/*  164 */       System.exit(1);
/*      */     }
/*      */ 
/*  169 */     SetOption(commandLine, hmpOptionData);
/*      */ 
/*  173 */     iRet = CheckURL(commandLine);
/*  174 */     if (iRet != 0)
/*      */     {
/*  176 */       Usage(options);
/*      */ 
/*  178 */       PrintDebugLog(0, "---->戻り値:1");
/*  179 */       System.exit(1);
/*      */     }
/*      */ 
/*  184 */     SimpleDateFormat sdfLogDate = new SimpleDateFormat("yyyy/MM/dd HH:mm:ss");
/*  185 */     Date dtStart = new Date();
/*  186 */     System.out.println(" [" + sdfLogDate.format(dtStart) + "] started. ==");
/*      */ 
/*  190 */     iRet = SetParam(commandLine, hmpParamData);
/*  191 */     if (iRet != 0)
/*      */     {
/*  194 */       Date dtEnd = new Date();
/*  195 */       System.out.println(" [" + sdfLogDate.format(dtEnd) + "] aborted:" + 1 + ". ==");
/*  196 */       System.exit(1);
/*      */     }
/*      */ 
/*  201 */     iRet = SetConf(hmpOptionData, hmpConfData);
/*  202 */     if (iRet != 0);
/*  209 */     httpCilentUtil = SetProxy(hmpOptionData);
/*  210 */     if (httpCilentUtil == null)
/*      */     {
/*  213 */       Date dtEnd = new Date();
/*  214 */       System.out.println(" [" + sdfLogDate.format(dtEnd) + "] aborted:" + 4 + ". ==");
/*  215 */       System.exit(4);
/*      */     }
/*      */ 
/*  219 */     CreateFormParam(hmpOptionData, hmpParamData, hmpSendData);
/*      */ 
/*  223 */     iRet = GetFileData(httpCilentUtil, hmpOptionData, hmpParamData, hmpConfData, hmpSendData);
/*      */ 
/*  225 */     Date dtEnd = new Date();
/*      */ 
/*  227 */     if (iRet == 0)
/*  228 */       System.out.println(" [" + sdfLogDate.format(dtEnd) + "] completed. ==");
/*  229 */     else if (iRet == 1)
/*  230 */       System.out.println("open: No such file or directory");
/*      */     else {
/*  232 */       System.out.println(" [" + sdfLogDate.format(dtEnd) + "] aborted:" + iRet + ". ==");
/*      */     }
/*      */ 
/*  237 */     PrintDebugLog(0, "---->戻り値:" + iRet);
/*  238 */     System.exit(iRet);
/*      */   }
/*      */ 
/*      */   private static CommandLine GetOtion(Options _options, String[] _args)
/*      */   {
/*  255 */     PrintDebugLog(0, "========GetOtion Start========");
/*      */     try
/*      */     {
/*  261 */       OptionBuilder.hasArg(true);
/*  262 */       OptionBuilder.withArgName("secret key");
/*  263 */       OptionBuilder.isRequired(true);
/*  264 */       OptionBuilder.withDescription("16 bytes secret key. (must be set)");
/*  265 */       Option optionSecretKey = OptionBuilder.create("k");
/*  266 */       _options.addOption(optionSecretKey);
/*  267 */       PrintDebugLog(0, "    setting option <k>");
/*      */ 
/*  270 */       OptionBuilder.hasArg(true);
/*  271 */       OptionBuilder.withArgName("file path");
/*  272 */       OptionBuilder.isRequired(true);
/*  273 */       OptionBuilder.withDescription("File path to be output. (must be set) \n* Specify '-' when output to stdout. \n(ex. -o c:\\data\\out.dat  or  -o - )");
/*  274 */       Option optionOutputFileName = OptionBuilder.create("o");
/*  275 */       _options.addOption(optionOutputFileName);
/*  276 */       PrintDebugLog(0, "    setting option <o>");
/*      */ 
/*  279 */       OptionBuilder.hasArg(true);
/*  280 */       OptionBuilder.withArgName("proxy host");
/*  281 */       OptionBuilder.isRequired(false);
/*  282 */       OptionBuilder.withDescription("Use proxy server. (ex. -p http://www.proxy.com:8080)");
/*  283 */       Option optionProxyUrl = OptionBuilder.create("p");
/*  284 */       _options.addOption(optionProxyUrl);
/*  285 */       PrintDebugLog(0, "    setting option <p>");
/*      */ 
/*  288 */       OptionBuilder.hasArg(true);
/*  289 */       OptionBuilder.withArgName("proxy user/pwd");
/*  290 */       OptionBuilder.isRequired(false);
/*  291 */       OptionBuilder.withDescription("Use proxy authorization. (ex. -u user:pwd)");
/*  292 */       Option optionProxyUserAndPssword = OptionBuilder.create("u");
/*  293 */       _options.addOption(optionProxyUserAndPssword);
/*  294 */       PrintDebugLog(0, "    setting option <u>");
/*      */ 
/*  297 */       OptionBuilder.hasArg(true);
/*  298 */       OptionBuilder.withArgName("config file");
/*  299 */       OptionBuilder.isRequired(false);
/*  300 */       OptionBuilder.withDescription("Specify config file path.");
/*  301 */       Option optionConfFileName = OptionBuilder.create("c");
/*  302 */       _options.addOption(optionConfFileName);
/*  303 */       PrintDebugLog(0, "    setting option <c>");
/*      */ 
/*  307 */       CommandLineParser parser = new PosixParser();
/*  308 */       CommandLine line = parser.parse(_options, _args);
/*  309 */       PrintDebugLog(0, "    parse command line");
/*      */ 
/*  311 */       PrintDebugLog(0, "return -> CommandLine");
/*  312 */       return line;
/*      */     }
/*      */     catch (Exception e)
/*      */     {
/*  316 */       PrintDebugLog(0, "*** GetOtion error:");
/*  317 */       PrintDebugLog(0, e);
/*  318 */       PrintDebugLog(0, "return -> null");
/*  319 */     }return null;
/*      */   }
/*      */ 
/*      */   private static void SetOption(CommandLine _commandLine, HashMap _hmpOptionData)
/*      */   {
/*  336 */     PrintDebugLog(0, "========SetOption Start========");
/*      */ 
/*  339 */     _hmpOptionData.put("k", "");
/*  340 */     _hmpOptionData.put("o", "");
/*  341 */     _hmpOptionData.put("p", "");
/*  342 */     _hmpOptionData.put("u", "");
/*  343 */     _hmpOptionData.put("c", "");
/*  344 */     PrintDebugLog(0, "    init _hmpOptionData");
/*      */ 
/*  348 */     String sOptShopKey = _commandLine.getOptionValue("k");
/*  349 */     _hmpOptionData.put("k", sOptShopKey);
/*  350 */     PrintDebugLog(0, "    _hmpOptionData.put <k>:" + sOptShopKey);
/*      */ 
/*  353 */     String sOptFilePath = _commandLine.getOptionValue("o");
/*  354 */     _hmpOptionData.put("o", sOptFilePath);
/*  355 */     PrintDebugLog(0, "    _hmpOptionData.put <o>:" + sOptFilePath);
/*      */ 
/*  358 */     if (_commandLine.hasOption("p")) {
/*  359 */       String sOptProxyServer = _commandLine.getOptionValue("p");
/*  360 */       _hmpOptionData.put("p", sOptProxyServer);
/*  361 */       PrintDebugLog(0, "    _hmpOptionData.put <p>:" + sOptProxyServer);
/*      */     }
/*      */ 
/*  364 */     if (_commandLine.hasOption("u")) {
/*  365 */       String sOptProxyUserPwd = _commandLine.getOptionValue("u");
/*  366 */       _hmpOptionData.put("u", sOptProxyUserPwd);
/*  367 */       PrintDebugLog(0, "    _hmpOptionData.put <u>:" + sOptProxyUserPwd);
/*      */     }
/*      */ 
/*  371 */     if (_commandLine.hasOption("c")) {
/*  372 */       String sOptConfPath = _commandLine.getOptionValue("c");
/*  373 */       _hmpOptionData.put("c", sOptConfPath);
/*  374 */       PrintDebugLog(0, "    _hmpOptionData.put <c>:" + sOptConfPath);
/*      */     }
/*      */   }
/*      */ 
/*      */   private static int CheckURL(CommandLine _commandLine)
/*      */   {
/*  392 */     PrintDebugLog(0, "========CheckURL Start========");
/*      */ 
/*  394 */     String sURL = null;
/*  395 */     ArrayList aryParam = null;
/*      */ 
/*  398 */     ArrayList aryCommandLine = new ArrayList(_commandLine.getArgList());
/*  399 */     PrintDebugLog(0, "    get command line");
/*      */ 
/*  402 */     if (aryCommandLine.size() <= 0) {
/*  403 */       PrintDebugLog(0, "*** SetParam error:size check");
/*  404 */       PrintDebugLog(0, "return -> -1");
/*  405 */       return -1;
/*      */     }
/*  407 */     PrintDebugLog(0, "    size check ok");
/*      */ 
/*  410 */     return 0;
/*      */   }
/*      */ 
/*      */   private static int SetParam(CommandLine _commandLine, HashMap _hmpParamData)
/*      */   {
/*  428 */     PrintDebugLog(0, "========SetParam Start========");
/*      */     try
/*      */     {
/*  431 */       String sURL = null;
/*  432 */       ArrayList aryParam = null;
/*      */ 
/*  435 */       ArrayList aryCommandLine = new ArrayList(_commandLine.getArgList());
/*  436 */       PrintDebugLog(0, "    get command line");
/*      */ 
/*  440 */       sURL = String.valueOf(aryCommandLine.get(0));
/*  441 */       _hmpParamData.put("URL", sURL);
/*  442 */       PrintDebugLog(0, "    _hmpParamData.put <URL>:" + sURL);
/*      */ 
/*  445 */       if (aryCommandLine.size() == 1) {
/*  446 */         PrintDebugLog(0, "    input param system in");
/*      */ 
/*  448 */         BufferedReader in = new BufferedReader(new InputStreamReader(System.in));
/*  449 */         String sParam = null;
/*  450 */         aryParam = new ArrayList();
/*      */ 
/*  452 */         int iCount = 1;
/*      */         while (true)
/*      */         {
/*  455 */           System.out.print("input param" + iCount + ":");
/*  456 */           sParam = in.readLine();
/*      */ 
/*  459 */           if ((sParam == null) || (sParam.length() <= 0))
/*      */           {
/*      */             break;
/*      */           }
/*  463 */           aryParam.add(sParam);
/*  464 */           iCount++;
/*      */         }
/*  466 */         in.close();
/*      */       }
/*      */       else
/*      */       {
/*  470 */         PrintDebugLog(0, "    input param command line");
/*      */ 
/*  472 */         aryParam = new ArrayList(aryCommandLine.subList(1, aryCommandLine.size()));
/*      */       }
/*      */ 
/*  475 */       for (int i = 0; i < aryParam.size(); i++) {
/*  476 */         System.out.println("==> " + aryParam.get(i));
/*      */       }
/*      */ 
/*  480 */       String sParam = null;
/*  481 */       for (int i = 0; i < aryParam.size(); i++) {
/*  482 */         sParam = String.valueOf(aryParam.get(i));
/*      */ 
/*  484 */         int equal_dist = sParam.indexOf("=");
/*      */ 
/*  486 */         if (equal_dist > 0)
/*      */         {
/*  488 */           String buffer_key = sParam.substring(0, equal_dist);
/*  489 */           String buffer_value = sParam.substring(equal_dist + 1);
/*      */ 
/*  491 */           _hmpParamData.put(buffer_key, buffer_value);
/*  492 */           PrintDebugLog(0, "    input key:" + buffer_key);
/*  493 */           PrintDebugLog(0, "    input value:" + buffer_value);
/*      */         }
/*      */         else
/*      */         {
/*  497 */           System.out.println("Bad parameter:" + sParam);
/*  498 */           PrintDebugLog(0, "return -> -1");
/*  499 */           return -1;
/*      */         }
/*      */       }
/*      */ 
/*  503 */       PrintDebugLog(0, "return -> 0");
/*  504 */       return 0;
/*      */     }
/*      */     catch (Exception e)
/*      */     {
/*  508 */       System.out.print("Param read failed:");
/*  509 */       System.out.println(e);
/*  510 */       PrintDebugLog(0, "return -> -1");
/*  511 */     }return -1;
/*      */   }
/*      */ 
/*      */   private static int SetConf(HashMap _hmpOptionData, HashMap _hmpConfData)
/*      */   {
/*  531 */     PrintDebugLog(0, "========SetConf Start========");
/*      */     try
/*      */     {
/*  535 */       _hmpConfData.put("RETRY_COUNT", String.valueOf(5));
/*  536 */       _hmpConfData.put("RETRY_INTERVAL", String.valueOf(5000));
/*  537 */       _hmpConfData.put("TIMEOUT", String.valueOf(30000));
/*  538 */       PrintDebugLog(0, "    init _hmpConfData");
/*      */ 
/*  541 */       String sConfPath = String.valueOf(_hmpOptionData.get("c"));
/*  542 */       if (sConfPath.equals(""))
/*      */       {
/*  544 */         PrintDebugLog(0, "    no setting conf path");
/*  545 */         PrintDebugLog(0, "return -> 0");
/*  546 */         return 0;
/*      */       }
/*      */ 
/*  550 */       Properties p = new Properties();
/*  551 */       FileInputStream fis = new FileInputStream(sConfPath);
/*  552 */       p.load(fis);
/*  553 */       fis.close();
/*  554 */       PrintDebugLog(0, "    read conf file");
/*      */ 
/*  558 */       String sRetryCount = p.getProperty("RETRY_COUNT");
/*  559 */       if ((sRetryCount != null) && (sRetryCount.length() > 0)) {
/*  560 */         _hmpConfData.put("RETRY_COUNT", String.valueOf(Integer.parseInt(sRetryCount)));
/*  561 */         PrintDebugLog(0, "    _hmpConfData.put<RETRY_COUNT>:" + sRetryCount);
/*      */       }
/*      */ 
/*  564 */       String sRetryInterval = p.getProperty("RETRY_INTERVAL");
/*  565 */       if ((sRetryInterval != null) && (sRetryInterval.length() > 0)) {
/*  566 */         _hmpConfData.put("RETRY_INTERVAL", String.valueOf(Integer.parseInt(sRetryInterval) * 1000));
/*  567 */         PrintDebugLog(0, "    _hmpConfData.put<RETRY_INTERVAL>:" + sRetryInterval);
/*      */       }
/*      */ 
/*  570 */       String sTimeOut = p.getProperty("TIMEOUT");
/*  571 */       if ((sTimeOut != null) && (sTimeOut.length() > 0)) {
/*  572 */         _hmpConfData.put("TIMEOUT", String.valueOf(Integer.parseInt(sTimeOut) * 1000));
/*  573 */         PrintDebugLog(0, "    _hmpConfData.put<TIMEOUT>:" + sTimeOut);
/*      */       }
/*      */ 
/*  576 */       PrintDebugLog(0, "return -> 0");
/*  577 */       return 0;
/*      */     }
/*      */     catch (Exception e)
/*      */     {
/*  581 */       PrintDebugLog(0, "*** SetConf error:");
/*  582 */       PrintDebugLog(0, e);
/*  583 */       PrintDebugLog(0, "return -> -1");
/*  584 */     }return -1;
/*      */   }
/*      */ 
/*      */   private static HttpClientUtil SetProxy(HashMap _hmpOptionData)
/*      */   {
/*  604 */     PrintDebugLog(0, "========SetProxy Start========");
/*      */     try
/*      */     {
/*  607 */       HttpClientUtil httpClientUtil = null;
/*      */ 
/*  610 */       String sHost = "";
/*  611 */       int iPort = -1;
/*  612 */       PrintDebugLog(0, "    init host&port");
/*      */ 
/*  615 */       String sProxySever = String.valueOf(_hmpOptionData.get("p"));
/*  616 */       PrintDebugLog(0, "    sProxySever:" + sProxySever);
/*      */ 
/*  619 */       if ((sProxySever.length() < 4) || (!sProxySever.substring(0, 4).equals("http"))) {
/*  620 */         sProxySever = "http://" + sProxySever;
/*  621 */         PrintDebugLog(0, "    sProxySever:" + sProxySever);
/*      */       }
/*      */ 
/*  624 */       String sAuth = String.valueOf(_hmpOptionData.get("u"));
/*  625 */       PrintDebugLog(0, "    sAuth:" + sAuth);
/*      */ 
/*  628 */       if (!sProxySever.equals(""))
/*      */       {
/*  630 */         URL url = new URL(sProxySever);
/*  631 */         PrintDebugLog(0, "    new URL");
/*      */ 
/*  634 */         if (url.getHost() != null) {
/*  635 */           sHost = url.getHost();
/*  636 */           PrintDebugLog(0, "    sHost:" + sHost);
/*      */         }
/*      */ 
/*  640 */         iPort = url.getPort();
/*  641 */         PrintDebugLog(0, "    iPort:" + iPort);
/*      */       }
/*      */ 
/*  646 */       if ((sHost.equals("")) && (iPort < 0)) {
/*  647 */         httpClientUtil = new HttpClientUtil();
/*  648 */         PrintDebugLog(0, "    PROXYを介さないで接続");
/*      */       }
/*  651 */       else if (((!sHost.equals("")) || (iPort >= 0)) && (sAuth.equals(""))) {
/*  652 */         httpClientUtil = new HttpClientUtil(sHost, iPort);
/*  653 */         PrintDebugLog(0, "    PROXYを介して接続(認証なし)");
/*      */       }
/*      */       else
/*      */       {
/*  657 */         httpClientUtil = new HttpClientUtil(sHost, iPort, sAuth);
/*  658 */         PrintDebugLog(0, "    PROXYを介して接続(認証あり)");
/*      */       }
/*      */ 
/*  662 */       PrintDebugLog(0, "return -> HttpClientUtil");
/*  663 */       return httpClientUtil;
/*      */     }
/*      */     catch (Exception e)
/*      */     {
/*  668 */       System.out.print("Proxy Setting failed:");
/*  669 */       System.out.println(e);
/*  670 */       PrintDebugLog(0, "return -> null");
/*  671 */     }return null;
/*      */   }
/*      */ 
/*      */   private static void CreateFormParam(HashMap _hmpOptionData, HashMap _hmpParamData, HashMap _hmpSendData)
/*      */   {
/*  690 */     PrintDebugLog(0, "========CreateFormParam Start========");
/*      */ 
/*  693 */     String sShopKey = String.valueOf(_hmpOptionData.get("k"));
/*  694 */     PrintDebugLog(0, "    sShopKey:" + sShopKey);
/*      */ 
/*  697 */     Iterator names = _hmpParamData.keySet().iterator();
/*  698 */     while (names.hasNext()) {
/*  699 */       String name = (String)names.next();
/*  700 */       if (name.startsWith("X_")) {
/*  701 */         _hmpSendData.put(name, _hmpParamData.get(name));
/*  702 */         PrintDebugLog(0, "    _hmpSendData.put<" + name + ">:" + _hmpParamData.get(name));
/*      */       }
/*      */ 
/*      */     }
/*      */ 
/*  707 */     String hash = MD5MessageDigest.createHash(_hmpSendData, sShopKey);
/*  708 */     _hmpSendData.put("xcode", hash);
/*  709 */     PrintDebugLog(0, "    xcode：" + hash);
/*      */   }
/*      */ 
/*      */   private static int GetFileData(HttpClientUtil _httpClientUtil, HashMap _hmpOptionData, HashMap _hmpParamData, HashMap _hmpConfData, HashMap _hmpSendData)
/*      */   {
/*  735 */     PrintDebugLog(0, "========GetFile Start========");
/*      */     try
/*      */     {
/*  739 */       int iRet = 0;
/*      */ 
/*  742 */       int iRetryCount = Integer.parseInt(String.valueOf(_hmpConfData.get("RETRY_COUNT")));
/*  743 */       PrintDebugLog(0, "    iRetryCount:" + iRetryCount);
/*      */ 
/*  746 */       int iRetryInterval = Integer.parseInt(String.valueOf(_hmpConfData.get("RETRY_INTERVAL")));
/*  747 */       PrintDebugLog(0, "    iRetryInterval:" + iRetryInterval);
/*      */ 
/*  750 */       for (int i = 0; i < iRetryCount + 1; i++)
/*      */       {
/*  753 */         PrintDebugLog(0, "     Start!! <" + (i + 1) + ">");
/*  754 */         if (i > 0)
/*      */         {
/*  756 */           System.out.println("! Retry after " + iRetryInterval / 1000 + " second...");
/*  757 */           Thread.sleep(iRetryInterval);
/*      */         }
/*      */ 
/*  761 */         iRet = Request2(_httpClientUtil, _hmpOptionData, _hmpParamData, _hmpConfData, _hmpSendData);
/*  762 */         PrintDebugLog(0, "    Request2 return:" + iRet);
/*      */ 
/*  764 */         if ((iRet == 120) || (iRet == 5))
/*      */           continue;
/*  766 */         PrintDebugLog(0, "*** GetFile retry break");
/*  767 */         break;
/*      */       }
/*      */ 
/*  772 */       PrintDebugLog(0, "return -> " + iRet);
/*  773 */       return iRet;
/*      */     }
/*      */     catch (Exception e)
/*      */     {
/*  777 */       System.out.print("File get failed:");
/*  778 */       System.out.println(e);
/*  779 */       PrintDebugLog(0, "return -> 999");
/*  780 */     }return 999;
/*      */   }
/*      */ 
/*      */   private static int Request2(HttpClientUtil _httpClientUtil, HashMap _hmpOptionData, HashMap _hmpParamData, HashMap _hmpConfData, HashMap _hmpSendData)
/*      */   {
/*  814 */     PrintDebugLog(0, "========Request2 Start========");
/*      */ 
/*  816 */     int iRet = 0;
/*  817 */     int iStatusCd = 0;
/*  818 */     int iResFileSizeOrg = 0;
/*  819 */     int iResFileSizeZip = 0;
/*      */ 
/*  822 */     String sUrl = String.valueOf(_hmpParamData.get("URL"));
/*  823 */     PrintDebugLog(0, "    sUrl:" + sUrl);
/*      */ 
/*  825 */     int iTimeOut = Integer.parseInt(String.valueOf(_hmpConfData.get("TIMEOUT")));
/*  826 */     PrintDebugLog(0, "    iTimeOut:" + iTimeOut);
/*      */ 
/*  828 */     String sFileName = String.valueOf(_hmpOptionData.get("o"));
/*  829 */     PrintDebugLog(0, "    sFileName:" + sFileName);
/*      */ 
/*  832 */     _hmpSendData.put("retry_cnt", "1");
/*  833 */     PrintDebugLog(0, "    retry_cnt:1");
/*      */     try
/*      */     {
/*  839 */       _httpClientUtil.conenectHttpPost(sUrl);
/*  840 */       PrintDebugLog(0, "    conenect server:" + sUrl);
/*      */ 
/*  843 */       _httpClientUtil.addHeaderHttpPost("User-Agent", "SejPaymentForJava/2.00");
/*  844 */       _httpClientUtil.addHeaderHttpPost("Connection", "close");
/*  845 */       PrintDebugLog(0, "    set header:User-Agent=SejPaymentForJava/2.00");
/*  846 */       PrintDebugLog(0, "    set header:Connection=close");
/*      */ 
/*  849 */       PrintDebugLog(0, "    send request!!");
/*  850 */       iStatusCd = _httpClientUtil.executeHttpPost(_hmpSendData, iTimeOut);
/*  851 */       PrintDebugLog(0, "    iStatusCd:" + iStatusCd);
/*      */     }
/*      */     catch (Exception e)
/*      */     {
/*  856 */       System.out.print("Connection failed:");
/*  857 */       System.out.println(e);
/*      */ 
/*  859 */       _httpClientUtil.release();
/*      */ 
/*  861 */       PrintDebugLog(0, "return -> 10");
/*  862 */       return 10;
/*      */     }
/*      */ 
/*  867 */     if (iStatusCd != 800)
/*      */     {
/*  869 */       String sStatusMsg = _httpClientUtil.getStatusMsg();
/*  870 */       PrintDebugLog(0, "    sStatusMsg:" + sStatusMsg);
/*      */ 
/*  875 */       if (iStatusCd == 200) {
/*  876 */         iStatusCd = 900;
/*  877 */         sStatusMsg = "Script syntax error";
/*      */       }
/*      */ 
/*  880 */       System.out.println("http status:" + iStatusCd + " " + sStatusMsg);
/*      */     }
/*      */ 
/*  886 */     HashMap hmpResHeader = new HashMap(_httpClientUtil.getResponseHeader());
/*  887 */     String sContentType = String.valueOf(hmpResHeader.get("Content-Type"));
/*  888 */     PrintDebugLog(0, "    sContentType:" + sContentType);
/*      */ 
/*  890 */     if (sContentType.indexOf("application/zip") >= 0)
/*      */     {
/*  894 */       iRet = ProcessBinaryContents(_httpClientUtil, iStatusCd, sFileName);
/*      */     }
/*      */     else
/*      */     {
/*  900 */       iRet = ProcessTextContents(_httpClientUtil, iStatusCd);
/*      */     }
/*      */ 
/*  903 */     _httpClientUtil.release();
/*      */ 
/*  914 */     if (iStatusCd >= 900) {
/*  915 */       PrintDebugLog(0, "return -> (" + iStatusCd + " - 800)");
/*  916 */       return iStatusCd - 800;
/*  917 */     }if (iStatusCd != 800) {
/*  918 */       PrintDebugLog(0, "return -> (" + iStatusCd + "  / 100)");
/*  919 */       return iStatusCd / 100;
/*      */     }
/*  921 */     if (iRet != 0) {
/*  922 */       PrintDebugLog(0, "return -> " + iRet);
/*  923 */       return iRet;
/*      */     }
/*      */ 
/*  926 */     PrintDebugLog(0, "return -> 0");
/*  927 */     return 0;
/*      */   }
/*      */ 
/*      */   private static int ProcessBinaryContents(HttpClientUtil _httpClientUtil, int _iStatusCd, String _sFileName)
/*      */   {
/*  948 */     String sUnZipBody = null;
/*  949 */     String outputString = null;
/*  950 */     InputStream inBody = null;
/*  951 */     Inflater inflater = null;
/*  952 */     InflaterInputStream in = null;
/*  953 */     int iResFileSizeOrg = 0;
/*  954 */     int iResFileSizeZip = 0;
/*  955 */     int iFileSizeOrg = 0;
/*  956 */     int iFileSizeZip = 0;
/*      */ 
/*  958 */     PrintDebugLog(0, "========ProcessBinaryContents Start========");
/*  959 */     PrintDebugLog(0, "    _sFileName:" + _sFileName);
/*      */     try
/*      */     {
/*  964 */       HashMap hmpResHeader = new HashMap(_httpClientUtil.getResponseHeader());
/*      */ 
/*  966 */       iResFileSizeOrg = Integer.parseInt(String.valueOf(hmpResHeader.get("Filesize-Org")));
/*  967 */       iResFileSizeZip = Integer.parseInt(String.valueOf(hmpResHeader.get("Filesize-Zip")));
/*  968 */       PrintDebugLog(0, "    iResFileSizeOrg:" + iResFileSizeOrg);
/*  969 */       PrintDebugLog(0, "    iResFileSizeZip:" + iResFileSizeZip);
/*      */     }
/*      */     catch (Exception e)
/*      */     {
/*  973 */       System.out.print("Response get failed:");
/*  974 */       System.out.println(e);
/*  975 */       PrintDebugLog(0, "return -> 11");
/*  976 */       return 11;
/*      */     }
/*      */ 
/*      */     try
/*      */     {
/*  984 */       int iBuffer = 10240;
/*  985 */       byte[] bytBuffer = new byte[iBuffer];
/*      */ 
/*  987 */       inBody = _httpClientUtil.getInputStreamBody();
/*      */ 
/*  989 */       inflater = new Inflater();
/*  990 */       in = new InflaterInputStream(inBody, inflater, iBuffer);
/*      */ 
/*  995 */       if ((_sFileName != null) && (!_sFileName.equals("-"))) {
/*  996 */         PrintDebugLog(0, "    output file");
/*      */ 
/*  998 */         FileOutputStream out = new FileOutputStream(_sFileName);
/*  999 */         PrintDebugLog(0, "    file open");
/*      */         while (true)
/*      */         {
/* 1003 */           int iReader = in.read(bytBuffer);
/* 1004 */           if (iReader < 0)
/*      */           {
/*      */             break;
/*      */           }
/* 1008 */           out.write(bytBuffer, 0, iReader);
/*      */         }
/*      */ 
/* 1011 */         in.close();
/*      */ 
/* 1013 */         out.flush();
/* 1014 */         out.close();
/*      */ 
/* 1016 */         PrintDebugLog(0, "    file close");
/*      */       }
/*      */       else
/*      */       {
/* 1022 */         PrintDebugLog(0, "    output system out");
/*      */         while (true)
/*      */         {
/* 1025 */           int iReader = in.read(bytBuffer);
/* 1026 */           if (iReader < 0)
/*      */           {
/*      */             break;
/*      */           }
/* 1030 */           System.out.write(bytBuffer, 0, iReader);
/*      */         }
/*      */       }
/* 1033 */       in.close();
/*      */     }
/*      */     catch (FileNotFoundException e)
/*      */     {
/* 1037 */       PrintDebugLog(0, "*** ProcessBinaryContents error:");
/* 1038 */       PrintDebugLog(0, e);
/* 1039 */       PrintDebugLog(0, "return -> 1");
/* 1040 */       return 1;
/*      */     }
/*      */     catch (Exception e)
/*      */     {
/* 1044 */       System.out.print("Incomplete response: unzip error: ");
/* 1045 */       System.out.println(e);
/* 1046 */       PrintDebugLog(0, "return -> 11");
/* 1047 */       return 11;
/*      */     }
/*      */ 
/* 1052 */     iFileSizeZip = inflater.getTotalIn();
/* 1053 */     iFileSizeOrg = inflater.getTotalOut();
/* 1054 */     PrintDebugLog(0, "    iFileSizeZip:" + iFileSizeZip);
/* 1055 */     PrintDebugLog(0, "    iFileSizeOrg:" + iFileSizeOrg);
/*      */ 
/* 1059 */     if ((iResFileSizeOrg != iFileSizeOrg) || (iResFileSizeZip != iFileSizeZip))
/*      */     {
/* 1061 */       System.out.println("Incomplete response: size unmatch (Org:" + iResFileSizeOrg + "=>" + iFileSizeOrg + ") (Zip:" + iResFileSizeZip + "=>" + iFileSizeZip + ")");
/* 1062 */       PrintDebugLog(0, "return -> 11");
/* 1063 */       return 11;
/*      */     }
/*      */ 
/* 1066 */     PrintDebugLog(0, "return -> 0");
/* 1067 */     return 0;
/*      */   }
/*      */ 
/*      */   private static int ProcessTextContents(HttpClientUtil _httpClientUtil, int _iStatusCd)
/*      */   {
/* 1087 */     String sUnZipBody = null;
/* 1088 */     String outputString = null;
/* 1089 */     int iFileSizeOrg = 0;
/* 1090 */     int iFileSizeZip = 0;
/*      */ 
/* 1092 */     PrintDebugLog(0, "========ProcessTextContents Start========");
/* 1093 */     PrintDebugLog(0, "    _iStatusCd:" + _iStatusCd);
/*      */ 
/* 1098 */     if (_iStatusCd != 902)
/*      */     {
/* 1100 */       if (_iStatusCd == 800)
/*      */       {
/* 1102 */         HashMap hmpResHeader = new HashMap(_httpClientUtil.getResponseHeader());
/* 1103 */         String sContentType = String.valueOf(hmpResHeader.get("Content-Type"));
/*      */ 
/* 1105 */         System.out.println("Incomplete response: content-type error: " + sContentType);
/*      */       }
/* 1107 */       PrintDebugLog(0, "return -> 11");
/* 1108 */       return 11;
/*      */     }
/*      */ 
/* 1112 */     String sBody = null;
/*      */     try {
/* 1114 */       sBody = String.valueOf(_httpClientUtil.getBody(String.class));
/*      */     }
/*      */     catch (Exception e)
/*      */     {
/* 1118 */       System.out.print("Response get failed:");
/* 1119 */       System.out.println(e);
/*      */ 
/* 1121 */       PrintDebugLog(0, "return -> 11");
/* 1122 */       return 11;
/*      */     }
/*      */ 
/* 1127 */     String sRetMsg = ParseTag(sBody, "SENBDATA");
/* 1128 */     if (sRetMsg == null)
/*      */     {
/* 1130 */       System.out.println("Incomplete response: no tag found.");
/* 1131 */       return 11;
/*      */     }
/*      */ 
/* 1135 */     HashMap hmpError = ParseString(sRetMsg);
/*      */ 
/* 1139 */     System.out.println("Error_Type=" + hmpError.get("Error_Type"));
/* 1140 */     System.out.println("Error_Msg=" + hmpError.get("Error_Msg"));
/* 1141 */     System.out.println("Error_Field=" + hmpError.get("Error_Field"));
/*      */ 
/* 1143 */     return 0;
/*      */   }
/*      */ 
/*      */   private static String ParseTag(String _sBody, String _sTagname)
/*      */   {
/* 1159 */     PrintDebugLog(0, "    -----ParseTag Start-----");
/* 1160 */     PrintDebugLog(0, "    _sBody:" + _sBody);
/* 1161 */     PrintDebugLog(0, "    _sTagname:" + _sTagname);
/*      */ 
/* 1163 */     String sTag = "";
/* 1164 */     String eTag = "";
/*      */ 
/* 1166 */     String body = null;
/*      */ 
/* 1168 */     StringBuffer sbufwTag = new StringBuffer();
/* 1169 */     StringBuffer sbufwBody = new StringBuffer();
/* 1170 */     StringBuffer sbufbody = new StringBuffer();
/*      */ 
/* 1173 */     int f_tagstart = 0;
/* 1174 */     int f_start = 0;
/*      */ 
/* 1176 */     sTag = _sTagname;
/* 1177 */     eTag = "/" + _sTagname;
/*      */ 
/* 1179 */     for (int i = 0; i < _sBody.length(); i++)
/*      */     {
/* 1181 */       PrintDebugLog(0, "    _sBody.charAt(i):" + _sBody.charAt(i));
/*      */ 
/* 1183 */       if (_sBody.charAt(i) == '<')
/*      */       {
/* 1185 */         f_tagstart = 1;
/* 1186 */         sbufwTag = new StringBuffer();
/*      */       }
/*      */       else {
/* 1189 */         if (f_tagstart == 1)
/*      */         {
/* 1191 */           if (_sBody.charAt(i) == '>')
/*      */           {
/* 1193 */             if (sbufwTag.toString().compareTo(sTag) == 0)
/*      */             {
/* 1195 */               f_start = 1;
/* 1196 */               sbufwBody = new StringBuffer();
/*      */             }
/* 1199 */             else if ((sbufwTag.toString().compareTo(eTag) == 0) && (f_start == 1))
/*      */             {
/* 1201 */               sbufbody.append(sbufwBody);
/* 1202 */               PrintDebugLog(0, "    sbufbody.toString():" + sbufbody.toString());
/* 1203 */               f_start = 0;
/*      */             }
/* 1205 */             f_tagstart = 0;
/* 1206 */             continue;
/*      */           }
/*      */         }
/* 1209 */         if (f_tagstart == 1) {
/* 1210 */           sbufwTag.append(_sBody.charAt(i));
/* 1211 */           PrintDebugLog(0, "    sbufwTag.toString():" + sbufwTag.toString());
/*      */         }
/* 1214 */         else if (f_start == 1) {
/* 1215 */           sbufwBody.append(_sBody.charAt(i));
/* 1216 */           PrintDebugLog(0, "    sbufwBody.toString():" + sbufwBody.toString());
/*      */         }
/*      */       }
/*      */     }
/*      */ 
/* 1221 */     body = sbufbody.toString();
/*      */ 
/* 1223 */     PrintDebugLog(0, "    body:" + body);
/* 1224 */     PrintDebugLog(0, "    DATA=END以降の文字を削除");
/* 1225 */     if (body.length() != 0) {
/* 1226 */       int iEnd = body.indexOf("DATA=END");
/* 1227 */       if (iEnd < 0) {
/* 1228 */         PrintDebugLog(0, "    DATA=ENDが存在しない場合は body = null");
/* 1229 */         body = null;
/* 1230 */         return body;
/*      */       }
/* 1232 */       body = body.substring(0, iEnd);
/*      */     } else {
/* 1234 */       PrintDebugLog(0, "    Body部が存在しない場合は body = null");
/* 1235 */       body = null;
/* 1236 */       return body;
/*      */     }
/*      */ 
/* 1239 */     PrintDebugLog(0, "    body:" + body);
/* 1240 */     return body;
/*      */   }
/*      */ 
/*      */   private static HashMap ParseString(String sRetMsg)
/*      */   {
/* 1253 */     PrintDebugLog(0, "    -----ParseString Start-----");
/*      */ 
/* 1255 */     String sKey = "";
/* 1256 */     String sVal = "";
/*      */ 
/* 1259 */     HashMap hmpOutputData = new HashMap();
/* 1260 */     PrintDebugLog(0, "    m_hmpOutputData = new HashMap()！！");
/*      */ 
/* 1262 */     StringTokenizer st = new StringTokenizer(sRetMsg, "&");
/* 1263 */     PrintDebugLog(0, "    &で文字列を分解");
/* 1264 */     while (st.hasMoreTokens()) {
/* 1265 */       String work = st.nextToken();
/* 1266 */       PrintDebugLog(0, "    work:" + work);
/* 1267 */       int iRet = work.indexOf("=");
/* 1268 */       if ((iRet < 0) || (iRet == 0) || (iRet == work.length() - 1))
/*      */       {
/* 1271 */         PrintDebugLog(0, "    =が先頭、末尾、存在しない場合は出力用MAPに入れない");
/* 1272 */         continue;
/*      */       }
/* 1274 */       sKey = work.substring(0, iRet);
/* 1275 */       sVal = work.substring(iRet + 1);
/*      */ 
/* 1277 */       hmpOutputData.put(sKey, sVal);
/* 1278 */       PrintDebugLog(0, "    出力用MAPに登録");
/* 1279 */       PrintDebugLog(0, "    sKey:" + sKey);
/* 1280 */       PrintDebugLog(0, "    sVal:" + sVal);
/*      */     }
/* 1282 */     PrintDebugLog(0, "    hmpOutputData.size():" + hmpOutputData.size());
/*      */ 
/* 1284 */     return hmpOutputData;
/*      */   }
/*      */ 
/*      */   private static void Usage(Options _options)
/*      */   {
/* 1294 */     PrintDebugLog(0, "========Usage Start========");
/*      */ 
/* 1297 */     System.out.println("========================================================================");
/* 1298 */     System.out.println("=======     SejPaymentGetFile                                    =======");
/* 1299 */     System.out.println("========================================================================");
/* 1300 */     System.out.println("              Copyright (C) Nomura Research Institute,Ltd.              ");
/* 1301 */     System.out.println("                                                                        ");
/*      */ 
/* 1304 */     HelpFormatter helpFormatter = new HelpFormatter();
/* 1305 */     helpFormatter.printHelp("\njava [-java options] jp.co.sej.od.util.SejPaymentGetFile [flags] url params.... \njava [-java options] jp.co.sej.od.util.SejPaymentGetFile [flags] url (params come from stdin)", _options);
/*      */   }
/*      */ 
/*      */   private static void PrintDebugLog(int _DebugFlg, Object _objDebugMsg)
/*      */   {
/* 1315 */     if (_DebugFlg == 1)
/* 1316 */       System.out.println(_objDebugMsg);
/*      */   }
/*      */ }

/* Location:           /Users/mistat/Dropbox/Sourcecode/altair-devel/altair/Sej/lib/SejPayment-20100215.002328.jar
 * Qualified Name:     jp.co.sej.od.util.SejPaymentGetFile
 * JD-Core Version:    0.6.0
 */