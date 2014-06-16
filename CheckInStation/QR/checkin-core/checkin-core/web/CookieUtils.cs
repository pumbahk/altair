using NLog;
using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;
using checkin.core.support;

namespace checkin.core.web
{
    public class CookieUtils
    {
        private static Logger logger = LogManager.GetCurrentClassLogger();
        public static CookieContainer GetCookiesFromResponseHeaders (string uriString, HttpResponseHeaders headers)
        {
            var uri = new Uri(uriString);
            var domain = new Uri(String.Format("{0}://{1}", uri.Scheme , uri.DnsSafeHost));
            var container = new CookieContainer();
            IEnumerable<string> setCookiesSentences;            

            if (headers.TryGetValues ("Set-Cookie", out setCookiesSentences)) {
                logger.Debug("domain: {0}".WithMachineName(), domain);
                foreach (var k in setCookiesSentences) {
                    //foo=bar; boo
                    var expr = k.Substring(0, k.IndexOf(";"));
                    var nameAndValue = expr.Split('=');
                    logger.Debug("Cookie: name={0}, value={1}".WithMachineName(), nameAndValue[0], nameAndValue[1]);
                    container.Add(domain, new Cookie(nameAndValue[0], nameAndValue[1]));
                }
            }
            return container;
        }

        public static void PutCokkiesToRequestHandler (HttpClientHandler handler , CookieContainer container)
        {
            if (container != null){
                handler.CookieContainer = container;
                logger.Debug("cookie: {0}".WithMachineName(), container);
            }
        }
    }
}

