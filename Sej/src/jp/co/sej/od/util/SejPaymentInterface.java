package jp.co.sej.od.util;

public abstract interface SejPaymentInterface
{
  public abstract void Addinput(String paramString1, String paramString2);

  public abstract void SetURL(String paramString);

  public abstract void SetSecretKey(String paramString);

  public abstract void SetProxyServerHost(String paramString);

  public abstract void SetProxyServerPort(int paramInt);

  public abstract void SetProxyAuth(String paramString);

  public abstract void SetTimeOut(int paramInt);

  public abstract void SetRetryCount(int paramInt);

  public abstract void SetRetryInterval(int paramInt);

  public abstract int Request(boolean paramBoolean)
    throws Exception;

  public abstract int Cancel()
    throws InterruptedException;

  public abstract String GetOutput(String paramString);

  public abstract String GetOutputAll();

  public abstract String GetErrorMsg();

  public abstract void Clear();

  public abstract String GetErrorMsg2(String paramString);

  public abstract boolean CheckSign()
    throws Exception;
}

/* Location:           /Users/mistat/Dropbox/Sourcecode/altair-devel/altair/Sej/lib/SejPayment-20100215.002328.jar
 * Qualified Name:     jp.co.sej.od.util.SejPaymentInterface
 * JD-Core Version:    0.6.0
 */