using System;
using System.Net;
using System.Net.Http;
using System.Net.Security;
using System.Security.Cryptography.X509Certificates;
using NLog;
using checkin.core.support;
using checkin.core.models;
using checkin.core;
using checkin.core.web;

namespace checkin.config
{
    class LoggedClientHandler : WebRequestHandler
    {
        public static Logger logger = LogManager.GetCurrentClassLogger();
        protected override System.Threading.Tasks.Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, System.Threading.CancellationToken cancellationToken)
        {
            if(request.Content == null){
                logger.Info("*API Request* method={0}, url={1}".WithMachineName(), request.Method.Method, request.RequestUri.AbsoluteUri);
            }else{
                var t = request.Content.ReadAsStringAsync();
                t.Wait();
                logger.Info("*API Request* method={0}, url={1}, data={2}".WithMachineName(), request.Method.Method, request.RequestUri.AbsoluteUri, t.Result);                
            }
            return base.SendAsync(request, cancellationToken);
        }
    }

    public class HttpCommunicationConfiguration
    {
        public static Uri DefaultBasicAuthURI = new Uri("https://backend.stg.altr.jp/checkinstation/login");
        public static TimeSpan DefaultTimeout = TimeSpan.FromSeconds(10);

        public X509Certificate2 Certificate { get; set; }
        public Func<CredentialCache> CredentialCacheFactory { get; set; }

        public HttpCommunicationConfiguration(IConfigurator config, ReleaseStageType s)
        {
            switch (s)
            {
                case ReleaseStageType.staging:
                    this.CredentialCacheFactory = this.CreateCacheForStaging;
                    break;
                default:
                    this.CredentialCacheFactory = this.CreateCacheDefault;
                    break;
            }

            if (s == ReleaseStageType.production)
            {
                string certfile = config.Resource.SettingValue("https.client.certificate.p12file");
                string certpassword = config.Resource.SettingValue("https.client.certificate.password");
                if (certfile != null)
                {
                    this.Certificate = new X509Certificate2(certfile, certpassword);
                }
            }
        }


        public CredentialCache CreateCacheForStaging()
        {
            var cache = new CredentialCache();
            cache.Add(DefaultBasicAuthURI, "Basic", new NetworkCredential("kenta", "matsui"));
            return cache;
        }

        public CredentialCache CreateCacheDefault()
        {
            return new CredentialCache();
        }

        public HttpClientHandler CreateHandler(CookieContainer cookieContainer)
        {
            var handler = new LoggedClientHandler() { Credentials = this.CredentialCacheFactory() };
            CookieUtils.PutCokkiesToRequestHandler(handler, cookieContainer);
            return handler;
        }

        public HttpClientHandler CreateHandlerWithCertificate(CookieContainer cookieContainer)
        {
            var handler = new LoggedClientHandler() { Credentials = this.CredentialCacheFactory() };
            handler.ClientCertificateOptions = ClientCertificateOption.Manual;
            handler.ClientCertificates.Add(this.Certificate);
            CookieUtils.PutCokkiesToRequestHandler(handler, cookieContainer);
            return handler;
        }

        public HttpClient ConfigClient(HttpClient client)
        {
            client.Timeout = DefaultTimeout;
            client.DefaultRequestHeaders.ExpectContinue = false;
            return client;
        }

        public static void IncludeMe(IConfigurator config)
        {
            //temporary: 
            ServicePointManager.ServerCertificateValidationCallback =
           (object sender, X509Certificate certificate, X509Chain chain, SslPolicyErrors sslPolicyErrors) =>
           {
               return true;
           };

            var env = new HttpCommunicationConfiguration(config, config.ReleaseStageType);
            if (env.Certificate == null)
            {
                config.Resource.HttpWrapperFactory = new HttpWrapperFactory<HttpWrapper>(env.CreateHandler, env.ConfigClient);
            }
            else
            {
                config.Resource.HttpWrapperFactory = new HttpWrapperFactory<HttpWrapper>(env.CreateHandlerWithCertificate, env.ConfigClient);
            }
        }
    }
}

