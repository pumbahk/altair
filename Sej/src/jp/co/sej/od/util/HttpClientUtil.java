/*     */ package jp.co.sej.od.util;
/*     */ 
/*     */ import java.io.IOException;
/*     */ import java.io.InputStream;
/*     */ import java.io.UnsupportedEncodingException;
/*     */ import java.util.HashMap;
/*     */ import java.util.Iterator;
/*     */ import java.util.Map;
/*     */ import java.util.Set;
/*     */ import org.apache.commons.httpclient.DefaultMethodRetryHandler;
/*     */ import org.apache.commons.httpclient.Header;
/*     */ import org.apache.commons.httpclient.HostConfiguration;
/*     */ import org.apache.commons.httpclient.HttpClient;
/*     */ import org.apache.commons.httpclient.HttpException;
/*     */ import org.apache.commons.httpclient.HttpState;
/*     */ import org.apache.commons.httpclient.UsernamePasswordCredentials;
/*     */ import org.apache.commons.httpclient.methods.EntityEnclosingMethod;
/*     */ import org.apache.commons.httpclient.methods.PostMethod;
/*     */ 
/*     */ public class HttpClientUtil
/*     */ {
/*  28 */   private static String CHAR_SET = "Windows-31J";
/*     */   private static final String ISO = "ISO-8859-1";
/*     */   private static final String UTF8 = "UTF-8";
/*  39 */   private HttpClient httpClient = null;
/*     */ 
/*  43 */   private HttpState httpState = null;
/*     */ 
/*  47 */   private EntityEnclosingMethod method = null;
/*     */ 
/*  51 */   private PostMethod post = null;
/*     */ 
/*     */   public HttpClientUtil()
/*     */   {
/*  57 */     this.httpClient = new HttpClient();
/*     */   }
/*     */ 
/*     */   public HttpClientUtil(String proxyUrl, int proxyPort)
/*     */   {
/*  67 */     this();
/*  68 */     HostConfiguration conf = new HostConfiguration();
/*  69 */     conf.setProxy(proxyUrl, proxyPort);
/*  70 */     this.httpClient.setHostConfiguration(conf);
/*     */   }
/*     */ 
/*     */   public HttpClientUtil(String proxyUrl, int proxyPort, String usrNamePassWord)
/*     */   {
/*  83 */     this(proxyUrl, proxyPort);
/*     */ 
/*  87 */     HttpState state = new HttpState();
/*  88 */     state.setAuthenticationPreemptive(true);
/*  89 */     state.setProxyCredentials(null, proxyUrl, new UsernamePasswordCredentials(usrNamePassWord));
/*     */ 
/*  94 */     this.httpClient.setState(state);
/*     */   }
/*     */ 
/*     */   public void conenectHttpPost(String url)
/*     */   {
/* 108 */     this.post = new PostMethod(url);
/* 109 */     this.method = this.post;
/*     */ 
/* 121 */     DefaultMethodRetryHandler handler = new DefaultMethodRetryHandler();
/* 122 */     handler.setRetryCount(0);
/* 123 */     this.method.setMethodRetryHandler(handler);
/*     */   }
/*     */ 
/*     */   public void addHeaderHttpPost(String headerName, String headerVal)
/*     */   {
/* 137 */     this.post.setRequestHeader(headerName, headerVal);
/*     */   }
/*     */ 
/*     */   public int executeHttpPost(Map queryMap, int timeout)
/*     */     throws HttpException, IOException
/*     */   {
/* 153 */     if ((queryMap != null) && (!queryMap.isEmpty())) {
/* 154 */       Iterator it = queryMap.keySet().iterator();
/* 155 */       while (it.hasNext()) {
/* 156 */         String key = (String)it.next();
/*     */ 
/* 158 */         Object val = queryMap.get(key);
/* 159 */         if ((val instanceof String[])) {
/* 160 */           String[] vals = (String[])val;
/* 161 */           for (int i = 0; i < vals.length; i++) this.post.addParameter(encode(key, CHAR_SET), encode(vals[i], CHAR_SET)); 
/*     */         }
/*     */         else
/*     */         {
/* 164 */           this.post.addParameter(encode(key, CHAR_SET), encode(val.toString(), CHAR_SET));
/*     */         }
/*     */       }
/*     */     }
/*     */ 
/* 169 */     this.httpClient.setConnectionTimeout(timeout);
/*     */ 
/* 171 */     this.httpClient.setTimeout(timeout);
/*     */ 
/* 173 */     int statusCd = 0;
/*     */ 
/* 176 */     statusCd = this.httpClient.executeMethod(this.post);
/*     */ 
/* 178 */     return statusCd;
/*     */   }
/*     */ 
/*     */   private String encode(String str, String set)
/*     */     throws UnsupportedEncodingException
/*     */   {
/* 191 */     return new String(str.getBytes(set), "ISO-8859-1");
/*     */   }
/*     */ 
/*     */   public Object getBody(Class cl)
/*     */     throws IOException, Exception
/*     */   {
/* 203 */     Object retOb = null;
/*     */ 
/* 205 */     if (this.method == null) {
/* 206 */       return null;
/*     */     }
/*     */ 
/* 210 */     if (String.class.equals(cl)) {
/* 211 */       byte[] ret = this.method.getResponseBody();
/*     */ 
/* 214 */       if (ret == null)
/*     */       {
/* 216 */         return "";
/*     */       }
/* 218 */       return new String(ret, CHAR_SET);
/*     */     }
/*     */ 
/* 223 */     throw new Exception(cl.getName() + "is invalid class.");
/*     */   }
/*     */ 
/*     */   public InputStream getInputStreamBody()
/*     */     throws IOException
/*     */   {
/* 236 */     if (this.method == null) {
/* 237 */       return null;
/*     */     }
/*     */ 
/* 240 */     return this.method.getResponseBodyAsStream();
/*     */   }
/*     */ 
/*     */   public Map getResponseHeader()
/*     */   {
/* 252 */     HashMap retMap = new HashMap();
/* 253 */     Header[] headers = this.method.getResponseHeaders();
/* 254 */     for (int i = 0; i < headers.length; i++) {
/* 255 */       retMap.put(headers[i].getName(), headers[i].getValue());
/*     */     }
/* 257 */     return retMap;
/*     */   }
/*     */ 
/*     */   public void release()
/*     */   {
/* 265 */     if (this.method != null) {
/* 266 */       this.method.releaseConnection();
/* 267 */       this.method = null;
/*     */     }
/*     */   }
/*     */ 
/*     */   public String getStatusMsg()
/*     */   {
/* 275 */     if (this.method == null) {
/* 276 */       return null;
/*     */     }
/*     */ 
/* 279 */     String sStatusMsg = this.method.getStatusText();
/*     */ 
/* 281 */     return sStatusMsg;
/*     */   }
/*     */ }

/* Location:           /Users/mistat/Dropbox/Sourcecode/altair-devel/altair/Sej/lib/SejPayment-20100215.002328.jar
 * Qualified Name:     jp.co.sej.od.util.HttpClientUtil
 * JD-Core Version:    0.6.0
 */