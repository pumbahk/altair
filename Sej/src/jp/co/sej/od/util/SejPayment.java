/*     */ package jp.co.sej.od.util;
/*     */ 
/*     */ import java.io.PrintStream;
/*     */ import java.text.SimpleDateFormat;
/*     */ import java.util.Arrays;
/*     */ import java.util.Date;
/*     */ import java.util.HashMap;
/*     */ import java.util.Iterator;
/*     */ import java.util.Set;
/*     */ import java.util.StringTokenizer;
/*     */ 
/*     */ public class SejPayment
/*     */   implements SejPaymentInterface
/*     */ {
/*     */   private static final int DEBUG_FLG = 0;
/*     */   private static final int MODE_ORDER_REQEST = 0;
/*     */   private static final int MODE_ORDER_CANCEL = 1;
/*     */   private static final int ERR_PARAMETER = 1;
/*     */   private static final int ERR_CONNECTION = 10;
/*     */   private static final int ERR_RESPONSE_READ = 11;
/*     */   private static final int STATUS_OK = 800;
/*     */   private static final String DATA_TAGNAME = "SENBDATA";
/*     */   private static final String EOF_STRING = "DATA=END";
/*     */   private static final String USER_AGENT = "SejPaymentForJava/2.00";
/*  60 */   private HashMap m_hmpInputData = null;
/*     */ 
/*  62 */   private HashMap m_hmpOutputData = null;
/*     */ 
/*  64 */   private String m_sErrMsg = "";
/*     */ 
/*  66 */   private HttpClientUtil m_HttpClientUtil = null;
/*     */ 
/*  68 */   private int m_iStatusCd = 0;
/*     */ 
/*  73 */   private String m_sUrl = "";
/*  74 */   private String m_sSecretKey = "";
/*  75 */   private String m_sProxyServerHost = "";
/*  76 */   private int m_iProxyServerPort = -1;
/*  77 */   private String m_sProxyAuth = "";
/*  78 */   private int m_iTimeOut = 30000;
/*  79 */   private int m_iRetryCount = 5;
/*  80 */   private int m_iRetryInterval = 5000;
/*     */ 
/*     */   public void Addinput(String _ItemName, String _ItemValue)
/*     */   {
/*  94 */     PrintDebugLog(0, "========Addinput Start========");
/*     */ 
/*  96 */     PrintDebugLog(0, "_ItemName:" + _ItemName);
/*  97 */     PrintDebugLog(0, "_ItemValue:" + _ItemValue);
/*     */ 
/*  99 */     if (this.m_hmpInputData == null) {
/* 100 */       this.m_hmpInputData = new HashMap();
/* 101 */       PrintDebugLog(0, "m_hmpInputData =new HashMap()!!!!");
/*     */     }
/* 103 */     if (!_ItemName.equals("")) {
/* 104 */       this.m_hmpInputData.put(_ItemName, _ItemValue);
/*     */     }
/*     */ 
/* 107 */     PrintDebugLog(0, "hmpInputData.size():" + this.m_hmpInputData.size());
/*     */   }
/*     */ 
/*     */   public int Request(boolean _RetryMode)
/*     */     throws Exception
/*     */   {
/* 131 */     PrintDebugLog(0, "========Request Start========");
/*     */ 
/* 133 */     PrintDebugLog(0, "プロパティー");
/* 134 */     PrintDebugLog(0, "Url:" + this.m_sUrl);
/* 135 */     PrintDebugLog(0, "SecretKey:" + this.m_sSecretKey);
/* 136 */     PrintDebugLog(0, "ProxyServerHost:" + this.m_sProxyServerHost);
/* 137 */     PrintDebugLog(0, "ProxyServerPort:" + this.m_iProxyServerPort);
/* 138 */     PrintDebugLog(0, "ProxyAuth:" + this.m_sProxyAuth);
/* 139 */     PrintDebugLog(0, "TimeOut:" + this.m_iTimeOut);
/* 140 */     PrintDebugLog(0, "RetryCount:" + this.m_iRetryCount);
/* 141 */     PrintDebugLog(0, "RetryInterval:" + this.m_iRetryInterval);
/*     */ 
/* 143 */     int iRet = 0;
/*     */ 
/* 146 */     if ((this.m_sUrl.equals("")) || (this.m_sSecretKey.equals(""))) {
/* 147 */       SetErrorMsg("Insufficient property");
/* 148 */       return 1;
/*     */     }
/* 150 */     if ((!this.m_sProxyServerHost.equals("")) && (this.m_iProxyServerPort < 0)) {
/* 151 */       SetErrorMsg("Insufficient property");
/* 152 */       return 1;
/*     */     }
/*     */ 
/* 156 */     CreateFormParam(this.m_sSecretKey);
/*     */ 
/* 158 */     iRet = SendRequest(0, _RetryMode);
/*     */ 
/* 160 */     return iRet;
/*     */   }
/*     */ 
/*     */   public String GetOutput(String _ItemName)
/*     */   {
/* 173 */     PrintDebugLog(0, "========GetOutput Start========");
/*     */ 
/* 175 */     return GetValue(_ItemName);
/*     */   }
/*     */ 
/*     */   public String GetOutputAll()
/*     */   {
/* 184 */     return GetAllValue();
/*     */   }
/*     */ 
/*     */   public int Cancel()
/*     */     throws InterruptedException
/*     */   {
/* 206 */     PrintDebugLog(0, "========Cancel Start========");
/*     */ 
/* 208 */     PrintDebugLog(0, "プロパティー");
/* 209 */     PrintDebugLog(0, "URL:" + this.m_sUrl);
/* 210 */     PrintDebugLog(0, "ProxyServerHost:" + this.m_sProxyServerHost);
/* 211 */     PrintDebugLog(0, "ProxyServerPort:" + this.m_iProxyServerPort);
/* 212 */     PrintDebugLog(0, "ProxyAuth:" + this.m_sProxyAuth);
/* 213 */     PrintDebugLog(0, "TimeOut:" + this.m_iTimeOut);
/* 214 */     PrintDebugLog(0, "RetryCount:" + this.m_iRetryCount);
/* 215 */     PrintDebugLog(0, "RetryInterval:" + this.m_iRetryInterval);
/*     */ 
/* 217 */     int iRet = 0;
/*     */ 
/* 220 */     if ((this.m_sUrl.equals("")) || (this.m_sSecretKey.equals(""))) {
/* 221 */       SetErrorMsg("Insufficient property");
/* 222 */       return 1;
/*     */     }
/* 224 */     if ((!this.m_sProxyServerHost.equals("")) && (this.m_iProxyServerPort < 0)) {
/* 225 */       SetErrorMsg("Insufficient property");
/* 226 */       return 1;
/*     */     }
/*     */ 
/* 230 */     CreateFormParam(this.m_sSecretKey);
/*     */ 
/* 232 */     iRet = SendRequest(1, false);
/*     */ 
/* 234 */     return iRet;
/*     */   }
/*     */ 
/*     */   public String GetErrorMsg()
/*     */   {
/* 245 */     PrintDebugLog(0, "========GetErrorMsg Start========");
/* 246 */     PrintDebugLog(0, "m_sErrMsg:" + this.m_sErrMsg);
/* 247 */     return this.m_sErrMsg;
/*     */   }
/*     */ 
/*     */   public void Clear()
/*     */   {
/* 258 */     PrintDebugLog(0, "========Clear Start========");
/* 259 */     if (this.m_hmpInputData != null) {
/* 260 */       PrintDebugLog(0, "clear前 入力項目件数:" + this.m_hmpInputData.size());
/*     */ 
/* 262 */       this.m_hmpInputData.clear();
/* 263 */       PrintDebugLog(0, "clear後 入力項目件数:" + this.m_hmpInputData.size());
/*     */     } else {
/* 265 */       PrintDebugLog(0, "clear前 入力項目未作成");
/*     */     }
/*     */ 
/* 268 */     if (this.m_hmpOutputData != null) {
/* 269 */       PrintDebugLog(0, "clear前 出力項目件数:" + this.m_hmpOutputData.size());
/*     */ 
/* 271 */       this.m_hmpOutputData.clear();
/* 272 */       PrintDebugLog(0, "clear後 出力項目件数:" + this.m_hmpOutputData.size());
/*     */     } else {
/* 274 */       PrintDebugLog(0, "clear前 出力項目未作成");
/*     */     }
/*     */   }
/*     */ 
/*     */   public String GetErrorMsg2(String _ErrItemName)
/*     */   {
/* 289 */     PrintDebugLog(0, "========GetErrorMsg2 Start========");
/*     */ 
/* 291 */     return GetValue(_ErrItemName);
/*     */   }
/*     */ 
/*     */   public boolean CheckSign()
/*     */     throws Exception
/*     */   {
/* 304 */     String xcode = "";
/* 305 */     String make_xcode = "";
/*     */ 
/* 307 */     if (this.m_sSecretKey.length() == 0) {
/* 308 */       SetErrorMsg("unset Secret Key.");
/* 309 */       return false;
/*     */     }
/*     */ 
/* 313 */     boolean rtn = false;
/* 314 */     if (this.m_hmpInputData != null) {
/* 315 */       Iterator ite = this.m_hmpInputData.keySet().iterator();
/* 316 */       while (ite.hasNext()) {
/* 317 */         Object key = ite.next();
/* 318 */         if (key.toString().toLowerCase().equals("xcode")) {
/* 319 */           xcode = (String)this.m_hmpInputData.get(key.toString());
/* 320 */           rtn = true;
/* 321 */           break;
/*     */         }
/*     */       }
/*     */     }
/* 325 */     if (!rtn) {
/* 326 */       SetErrorMsg("unset xcode.");
/* 327 */       return false;
/*     */     }
/*     */ 
/* 331 */     make_xcode = Createxcode(this.m_sSecretKey);
/* 332 */     if (!xcode.equals(make_xcode)) {
/* 333 */       SetErrorMsg("unmatch xcode.");
/* 334 */       return false;
/*     */     }
/* 336 */     Clear();
/* 337 */     return true;
/*     */   }
/*     */ 
/*     */   public void SetURL(String _sUrl)
/*     */   {
/* 351 */     PrintDebugLog(0, "========SetURL Start========");
/* 352 */     this.m_sUrl = _sUrl;
/* 353 */     PrintDebugLog(0, "m_sUrl:" + this.m_sUrl);
/*     */   }
/*     */ 
/*     */   public void SetSecretKey(String _sSecretKey)
/*     */   {
/* 364 */     PrintDebugLog(0, "========SetSecretKey Start========");
/* 365 */     this.m_sSecretKey = _sSecretKey;
/* 366 */     PrintDebugLog(0, "m_sSecretKey:" + this.m_sSecretKey);
/*     */   }
/*     */ 
/*     */   public void SetProxyServerHost(String _sProxyServerHost)
/*     */   {
/* 377 */     PrintDebugLog(0, "========SetProxyServerHost Start========");
/* 378 */     this.m_sProxyServerHost = _sProxyServerHost;
/* 379 */     PrintDebugLog(0, "m_sProxyServerHost:" + this.m_sProxyServerHost);
/*     */   }
/*     */ 
/*     */   public void SetProxyServerPort(int _iProxyServerPort)
/*     */   {
/* 391 */     PrintDebugLog(0, "========SetProxyServerPort Start========");
/* 392 */     this.m_iProxyServerPort = _iProxyServerPort;
/* 393 */     PrintDebugLog(0, "m_iProxyServerPort:" + this.m_iProxyServerPort);
/*     */   }
/*     */ 
/*     */   public void SetProxyAuth(String _sProxyAuth)
/*     */   {
/* 404 */     PrintDebugLog(0, "========SetProxyAuth Start========");
/* 405 */     this.m_sProxyAuth = _sProxyAuth;
/* 406 */     PrintDebugLog(0, "m_sProxyAuth:" + this.m_sProxyAuth);
/*     */   }
/*     */ 
/*     */   public void SetTimeOut(int _iTimeOut)
/*     */   {
/* 417 */     PrintDebugLog(0, "========SetTimeOut Start========");
/* 418 */     this.m_iTimeOut = (_iTimeOut * 1000);
/* 419 */     PrintDebugLog(0, "m_iTimeOut:" + this.m_iTimeOut);
/*     */   }
/*     */ 
/*     */   public void SetRetryCount(int _iRetryCount)
/*     */   {
/* 430 */     PrintDebugLog(0, "========SetRetryCount Start========");
/* 431 */     this.m_iRetryCount = _iRetryCount;
/* 432 */     PrintDebugLog(0, "m_iRetryCount:" + this.m_iRetryCount);
/*     */   }
/*     */ 
/*     */   public void SetRetryInterval(int _iRetryInterval)
/*     */   {
/* 443 */     PrintDebugLog(0, "========SetRetryInterval Start========");
/* 444 */     this.m_iRetryInterval = (_iRetryInterval * 1000);
/* 445 */     PrintDebugLog(0, "m_iRetryInterval:" + this.m_iRetryInterval);
/*     */   }
/*     */ 
/*     */   private String GetValue(String _ItemName)
/*     */   {
/* 460 */     PrintDebugLog(0, "    -----GetValue Start-----");
/* 461 */     PrintDebugLog(0, "    _ItemName:" + _ItemName);
/*     */ 
/* 463 */     if (this.m_hmpOutputData == null) {
/* 464 */       PrintDebugLog(0, "    戻りMAPは作成されていません！！");
/* 465 */       return "";
/*     */     }
/* 467 */     PrintDebugLog(0, "    ItemValue:" + (String)this.m_hmpOutputData.get(_ItemName));
/*     */ 
/* 469 */     String sRet = (String)this.m_hmpOutputData.get(_ItemName);
/*     */ 
/* 471 */     if (sRet == null) {
/* 472 */       sRet = "";
/*     */     }
/* 474 */     return sRet;
/*     */   }
/*     */ 
/*     */   private String GetAllValue()
/*     */   {
/* 483 */     PrintDebugLog(0, "    -----GetAllValue Start-----");
/* 484 */     String sRet = "";
/* 485 */     if (this.m_hmpOutputData == null) {
/* 486 */       PrintDebugLog(0, "    戻りMAPは作成されていません！！");
/* 487 */       return "";
/*     */     }
/*     */ 
/* 490 */     Object[] key_array = this.m_hmpOutputData.keySet().toArray();
/* 491 */     Arrays.sort(key_array);
/* 492 */     for (int i = 0; i < key_array.length; i++) {
/* 493 */       String values = (String)this.m_hmpOutputData.get(key_array[i]);
/* 494 */       if (sRet.length() != 0) {
/* 495 */         sRet = sRet + "&";
/*     */       }
/* 497 */       sRet = sRet + key_array[i] + "=" + values;
/*     */     }
/* 499 */     return sRet;
/*     */   }
/*     */ 
/*     */   private void SetErrorMsg(String _sMsg)
/*     */   {
/* 509 */     PrintDebugLog(0, "    -----SetErrorMsg Start-----");
/* 510 */     if (!_sMsg.equals("")) {
/* 511 */       this.m_sErrMsg = _sMsg;
/*     */     }
/* 513 */     PrintDebugLog(0, "    m_sErrMsg:" + this.m_sErrMsg);
/*     */   }
/*     */ 
/*     */   private void CreateFormParam(String _sKey)
/*     */   {
/* 524 */     PrintDebugLog(0, "    -----CreateFormParam Start-----");
/*     */ 
/* 526 */     String hash = Createxcode(_sKey);
/* 527 */     this.m_hmpInputData.put("xcode", hash);
/*     */   }
/*     */ 
/*     */   public String Createxcode(String _sKey)
/*     */   {
/* 538 */     PrintDebugLog(0, "    -----CreateXcode Start-----");
/*     */ 
/* 540 */     if (this.m_hmpInputData == null) {
/* 541 */       this.m_hmpInputData = new HashMap();
/* 542 */       PrintDebugLog(0, "m_hmpInputData =new HashMap()!!!!");
/*     */     }
/*     */ 
/* 545 */     Iterator names = this.m_hmpInputData.keySet().iterator();
/* 546 */     HashMap falsifyProps = new HashMap();
/* 547 */     while (names.hasNext()) {
/* 548 */       String name = (String)names.next();
/* 549 */       if (name.startsWith("X_")) {
/* 550 */         falsifyProps.put(name, this.m_hmpInputData.get(name));
/*     */       }
/*     */     }
/* 553 */     String hash = MD5MessageDigest.createHash(falsifyProps, _sKey);
/*     */ 
/* 555 */     PrintDebugLog(0, "    xcode：" + hash);
/* 556 */     PrintDebugLog(0, "    m_hmpInputData:" + this.m_hmpInputData.size());
/* 557 */     return hash;
/*     */   }
/*     */ 
/*     */   private int SendRequest(int _iMode, boolean _flgRetryFlg)
/*     */     throws InterruptedException
/*     */   {
/* 572 */     PrintDebugLog(0, "    -----SendRequest Start-----");
/* 573 */     PrintDebugLog(0, "    _iMode:" + _iMode);
/* 574 */     PrintDebugLog(0, "    _flgRetryFlg:" + _flgRetryFlg);
/*     */ 
/* 576 */     int iRet = 0;
/*     */ 
/* 578 */     for (int i = 0; i < this.m_iRetryCount + 1; i++)
/*     */     {
/* 581 */       if (i > 0) {
/* 582 */         PrintDebugLog(0, "    Sleep！！" + this.m_iRetryInterval + "秒");
/* 583 */         Thread.sleep(this.m_iRetryInterval);
/*     */       }
/* 585 */       Date date1 = new Date();
/* 586 */       SimpleDateFormat sdf1 = new SimpleDateFormat("yyyy.MM.dd HH:mm:ss");
/* 587 */       PrintDebugLog(0, "    " + (i + 1) + "回目Start！！(" + sdf1.format(date1) + ")");
/*     */ 
/* 589 */       iRet = SendRequest2(_iMode, _flgRetryFlg);
/* 590 */       PrintDebugLog(0, "    戻り値:" + iRet);
/* 591 */       if ((iRet != 120) && (iRet != 5))
/*     */       {
/*     */         break;
/*     */       }
/*     */ 
/*     */     }
/*     */ 
/* 598 */     return iRet;
/*     */   }
/*     */ 
/*     */   private int SendRequest2(int _iMode, boolean _flgRetryFlg)
/*     */   {
/* 614 */     PrintDebugLog(0, "    -----SendRequest2 Start-----");
/* 615 */     PrintDebugLog(0, "    _iMode" + _iMode);
/* 616 */     PrintDebugLog(0, "    _flgRetryFlg" + _flgRetryFlg);
/*     */ 
/* 618 */     int iRet = 0;
/*     */ 
/* 620 */     if (_flgRetryFlg) {
/* 621 */       this.m_hmpInputData.put("retry_cnt", "1");
/* 622 */       PrintDebugLog(0, "    retry_cnt:1");
/* 623 */       PrintDebugLog(0, "    m_hmpInputData.size():" + this.m_hmpInputData.size());
/*     */     }
/*     */ 
/*     */     try
/*     */     {
/* 630 */       if ((this.m_sProxyServerHost.equals("")) && (this.m_iProxyServerPort < 0)) {
/* 631 */         this.m_HttpClientUtil = new HttpClientUtil();
/* 632 */         PrintDebugLog(0, "    Proxyを介さずに接続");
/*     */       }
/* 635 */       else if (((!this.m_sProxyServerHost.equals("")) || (this.m_iProxyServerPort >= 0)) && (this.m_sProxyAuth.equals("")))
/*     */       {
/* 637 */         this.m_HttpClientUtil = new HttpClientUtil(this.m_sProxyServerHost, this.m_iProxyServerPort);
/*     */ 
/* 640 */         PrintDebugLog(0, "    proxyを介して接続 認証なし");
/*     */       }
/*     */       else
/*     */       {
/* 644 */         PrintDebugLog(0, "    proxyを介して接続 認証あり");
/* 645 */         this.m_HttpClientUtil = new HttpClientUtil(this.m_sProxyServerHost, this.m_iProxyServerPort, this.m_sProxyAuth);
/*     */       }
/*     */ 
/* 653 */       this.m_HttpClientUtil.conenectHttpPost(this.m_sUrl);
/* 654 */       PrintDebugLog(0, "    サーバに接続:" + this.m_sUrl);
/*     */ 
/* 657 */       this.m_HttpClientUtil.addHeaderHttpPost("User-Agent", "SejPaymentForJava/2.00");
/* 658 */       this.m_HttpClientUtil.addHeaderHttpPost("Connection", "close");
/* 659 */       PrintDebugLog(0, "    ヘッダー設定:User-Agent=SejPaymentForJava/2.00");
/* 660 */       PrintDebugLog(0, "    ヘッダー設定:Connection=close");
/*     */ 
/* 663 */       PrintDebugLog(0, "    送信！！");
/* 664 */       this.m_iStatusCd = this.m_HttpClientUtil.executeHttpPost(this.m_hmpInputData, this.m_iTimeOut);
/* 665 */       PrintDebugLog(0, "    m_iStatusCd:" + this.m_iStatusCd);
/*     */     }
/*     */     catch (Exception e) {
/* 668 */       String sMsg = e.getMessage();
/* 669 */       if (sMsg != null)
/* 670 */         SetErrorMsg(sMsg);
/*     */       else {
/* 672 */         SetErrorMsg("Send Request Exception:" + e.toString());
/*     */       }
/* 674 */       this.m_HttpClientUtil.release();
/* 675 */       return 10;
/*     */     }
/*     */ 
/* 679 */     String sStatusMsg = this.m_HttpClientUtil.getStatusMsg();
/*     */ 
/* 681 */     PrintDebugLog(0, "    エラーメッセージ取得");
/* 682 */     PrintDebugLog(0, "    sStatusMsg:" + sStatusMsg);
/*     */ 
/* 685 */     if (this.m_iStatusCd != 800) {
/* 686 */       if (this.m_iStatusCd == 200) {
/* 687 */         this.m_iStatusCd = 900;
/* 688 */         sStatusMsg = "Script syntax error";
/*     */       }
/* 690 */       this.m_sErrMsg = ("http status:" + this.m_iStatusCd + " " + sStatusMsg);
/* 691 */       PrintDebugLog(0, "    m_sErrMsg:" + this.m_sErrMsg);
/*     */     }
/*     */ 
/*     */     try
/*     */     {
/* 697 */       String sOutBody = (String)this.m_HttpClientUtil.getBody(String.class);
                System.out.println(sOutBody);
/* 698 */       PrintDebugLog(0, "    受信処理！！");
/*     */ 
/* 701 */       iRet = ProcessTextContents(_iMode, sOutBody);
/*     */     }
/*     */     catch (Exception e) {
/* 704 */       String sMsg = e.getMessage();
/* 705 */       if (sMsg != null) {
/* 706 */         SetErrorMsg(sMsg);
/*     */       }
/*     */       else {
/* 709 */         SetErrorMsg("Receive Response Exception:" + e.toString());
/*     */       }
/* 711 */       this.m_HttpClientUtil.release();
/* 712 */       return 11;
/*     */     }
/*     */     String sOutBody;
/* 716 */     this.m_HttpClientUtil.release();
/*     */ 
/* 719 */     if (this.m_iStatusCd >= 900) {
/* 720 */       PrintDebugLog(0, "    戻り値の設定(m_iStatusCd - 800):" + (this.m_iStatusCd - 800));
/* 721 */       return this.m_iStatusCd - 800;
/* 722 */     }if (this.m_iStatusCd != 800) {
/* 723 */       PrintDebugLog(0, "    戻り値の設定(m_iStatusCd / 100)):" + this.m_iStatusCd / 100);
/* 724 */       return this.m_iStatusCd / 100;
/*     */     }
/* 726 */     if (iRet != 0) {
/* 727 */       PrintDebugLog(0, "    戻り値の設定:" + iRet);
/* 728 */       return iRet;
/*     */     }
/*     */ 
/* 731 */     PrintDebugLog(0, "    戻り値の設定(正常):0");
/* 732 */     return 0;
/*     */   }
/*     */ 
/*     */   private int ProcessTextContents(int _iMode, String _sBody)
/*     */   {
/* 748 */     PrintDebugLog(0, "    -----ProcessTextContents Start-----");
/*     */ 
/* 750 */     if ((this.m_iStatusCd != 800) && (this.m_iStatusCd != 902) && (this.m_iStatusCd != 910))
/*     */     {
/* 754 */       PrintDebugLog(0, "    ステータス800，902，910以外の場合は終了　戻り値：0");
/* 755 */       return 0;
/*     */     }
/* 757 */     if ((this.m_iStatusCd == 800) && (_iMode == 1))
/*     */     {
/* 760 */       PrintDebugLog(0, "    キャンセルかつステータス800の場合は終了　戻り値：0");
/* 761 */       return 0;
/*     */     }
/*     */ 
/* 765 */     String sRetMsg = ParseTag(_sBody, "SENBDATA");
/*     */ 
/* 767 */     if (sRetMsg == null) {
/* 768 */       this.m_sErrMsg = "Incomplete response: no tag found.";
/* 769 */       return 11;
/*     */     }
/*     */ 
/* 773 */     ParseString(sRetMsg);
/*     */ 
/* 775 */     if ((this.m_iStatusCd == 902) || (this.m_iStatusCd == 910))
/*     */     {
/* 778 */       this.m_sErrMsg = (this.m_sErrMsg + "\nError_Type=" + GetValue("Error_Type"));
/* 779 */       this.m_sErrMsg = (this.m_sErrMsg + "\nError_Msg=" + GetValue("Error_Msg"));
/* 780 */       this.m_sErrMsg = (this.m_sErrMsg + "\nError_Field=" + GetValue("Error_Field"));
/*     */ 
/* 782 */       PrintDebugLog(0, "    ステータス902，910の場合はエラーメッセージをセット");
/* 783 */       PrintDebugLog(0, "    m_sErrMsg:" + this.m_sErrMsg);
/*     */     }
/*     */ 
/* 787 */     return 0;
/*     */   }
/*     */ 
/*     */   private String ParseTag(String _sBody, String _sTagneme)
/*     */   {
/* 803 */     PrintDebugLog(0, "    -----ParseTag Start-----");
/* 804 */     PrintDebugLog(0, "    _sBody:" + _sBody);
/* 805 */     PrintDebugLog(0, "    _sTagneme:" + _sTagneme);
/*     */ 
/* 807 */     String sTag = "";
/* 808 */     String eTag = "";
/*     */ 
/* 810 */     String body = null;
/*     */ 
/* 812 */     StringBuffer sbufwTag = new StringBuffer();
/* 813 */     StringBuffer sbufwBody = new StringBuffer();
/* 814 */     StringBuffer sbufbody = new StringBuffer();
/*     */ 
/* 817 */     int f_tagstart = 0;
/* 818 */     int f_start = 0;
/*     */ 
/* 820 */     sTag = _sTagneme;
/* 821 */     eTag = "/" + _sTagneme;
/*     */ 
/* 823 */     for (int i = 0; i < _sBody.length(); i++)
/*     */     {
/* 825 */       PrintDebugLog(0, "    _sBody.charAt(i):" + _sBody.charAt(i));
/*     */ 
/* 827 */       if (_sBody.charAt(i) == '<')
/*     */       {
/* 829 */         f_tagstart = 1;
/* 830 */         sbufwTag = new StringBuffer();
/*     */       }
/*     */       else {
/* 833 */         if (f_tagstart == 1)
/*     */         {
/* 835 */           if (_sBody.charAt(i) == '>')
/*     */           {
/* 837 */             if (sbufwTag.toString().compareTo(sTag) == 0)
/*     */             {
/* 839 */               f_start = 1;
/* 840 */               sbufwBody = new StringBuffer();
/*     */             }
/* 843 */             else if ((sbufwTag.toString().compareTo(eTag) == 0) && (f_start == 1))
/*     */             {
/* 845 */               sbufbody.append(sbufwBody);
/* 846 */               PrintDebugLog(0, "    sbufbody.toString():" + sbufbody.toString());
/* 847 */               f_start = 0;
/*     */             }
/* 849 */             f_tagstart = 0;
/* 850 */             continue;
/*     */           }
/*     */         }
/* 853 */         if (f_tagstart == 1) {
/* 854 */           sbufwTag.append(_sBody.charAt(i));
/* 855 */           PrintDebugLog(0, "    sbufwTag.toString():" + sbufwTag.toString());
/*     */         }
/* 858 */         else if (f_start == 1) {
/* 859 */           sbufwBody.append(_sBody.charAt(i));
/* 860 */           PrintDebugLog(0, "    sbufwBody.toString():" + sbufwBody.toString());
/*     */         }
/*     */       }
/*     */     }
/*     */ 
/* 865 */     body = sbufbody.toString();
/*     */ 
/* 867 */     PrintDebugLog(0, "    body:" + body);
/* 868 */     PrintDebugLog(0, "    DATA=END以降の文字を削除");
/* 869 */     if (body.length() != 0) {
/* 870 */       int iEnd = body.indexOf("DATA=END");
/* 871 */       if (iEnd < 0) {
/* 872 */         PrintDebugLog(0, "    DATA=ENDが存在しない場合は body = null");
/* 873 */         body = null;
/* 874 */         return body;
/*     */       }
/* 876 */       body = body.substring(0, iEnd);
/*     */     } else {
/* 878 */       PrintDebugLog(0, "    Body部が存在しない場合は body = null");
/* 879 */       body = null;
/* 880 */       return body;
/*     */     }
/*     */ 
/* 883 */     PrintDebugLog(0, "    body:" + body);
/* 884 */     return body;
/*     */   }
/*     */ 
/*     */   private void ParseString(String sRetMsg)
/*     */   {
/* 897 */     PrintDebugLog(0, "    -----ParseString Start-----");
/*     */ 
/* 899 */     String sKey = "";
/* 900 */     String sVal = "";
/*     */ 
/* 903 */     this.m_hmpOutputData = new HashMap();
/* 904 */     PrintDebugLog(0, "    m_hmpOutputData = new HashMap()！！");
/*     */ 
/* 906 */     StringTokenizer st = new StringTokenizer(sRetMsg, "&");
/* 907 */     PrintDebugLog(0, "    &で文字列を分解");
/* 908 */     while (st.hasMoreTokens()) {
/* 909 */       String work = st.nextToken();
/* 910 */       PrintDebugLog(0, "    work:" + work);
/* 911 */       int iRet = work.indexOf("=");
/* 912 */       if ((iRet < 0) || (iRet == 0) || (iRet == work.length() - 1))
/*     */       {
/* 915 */         PrintDebugLog(0, "    =が先頭、末尾、存在しない場合は出力用MAPに入れない");
/* 916 */         continue;
/*     */       }
/* 918 */       sKey = work.substring(0, iRet);
/* 919 */       sVal = work.substring(iRet + 1);
/*     */ 
/* 921 */       this.m_hmpOutputData.put(sKey, sVal);
/* 922 */       PrintDebugLog(0, "    出力用MAPに登録");
/* 923 */       PrintDebugLog(0, "    sKey:" + sKey);
/* 924 */       PrintDebugLog(0, "    sVal:" + sVal);
/*     */     }
/* 926 */     PrintDebugLog(0, "    m_hmpOutputData.size():" + this.m_hmpOutputData.size());
/*     */   }
/*     */ 
/*     */   private void PrintDebugLog(int _DebugFlg, String _sDebugMsg)
/*     */   {
/* 936 */     if (_DebugFlg == 1)
/* 937 */       System.out.print(_sDebugMsg + "\n");
/*     */   }
/*     */ }

/* Location:           /Users/mistat/Dropbox/Sourcecode/altair-devel/altair/Sej/lib/SejPayment-20100215.002328.jar
 * Qualified Name:     jp.co.sej.od.util.SejPayment
 * JD-Core Version:    0.6.0
 */