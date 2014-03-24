using System;
using System.Net;
using System.Net.Http;
using System.Net.Security;
using System.Security.Cryptography.X509Certificates;

namespace QR
{
    public class HttpCommunicationConfiguration
    {
        public enum ReleaseStageType
        {
            develop,
            staging,
            production
        }

        public static Uri DefaultBasicAuthURI = new Uri("https://backend.stg2.rt.ticketstar.jp/checkinstation/login");
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
                this.Certificate = new X509Certificate2(certfile, certpassword);
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
            var handler = new HttpClientHandler() { Credentials = this.CredentialCacheFactory() };
            CookieUtils.PutCokkiesToRequestHandler(handler, cookieContainer);
            return handler;
        }

        public HttpClientHandler CreateHandlerWithCertificate(CookieContainer cookieContainer)
        {
            var handler = new WebRequestHandler() { Credentials = this.CredentialCacheFactory() };
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

            //TODO: dispatch
            var env = new HttpCommunicationConfiguration(config, ReleaseStageType.production);
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

