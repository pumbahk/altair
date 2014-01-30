using NLog;
using System;
using System.Collections.Generic;
using System.Net.Http.Headers;

namespace QR
{
	public class CookieUtils
	{
        private static Logger logger = LogManager.GetCurrentClassLogger();
		public static IEnumerable<string>GetCookiesFromResponseHeaders (HttpResponseHeaders headers)
		{

			IEnumerable<string> setCookiesSentences;
			ICollection<string> cookies = new List<string> ();

			if (headers.TryGetValues ("Set-Cookie", out setCookiesSentences)) {
				foreach (var k in setCookiesSentences) {
					//TODO: refine. this is tiny implementation.
					cookies.Add (k.Substring (0, k.IndexOf (';')));
				}
			}
			return cookies as IEnumerable<string>;
		}

		public static void PutCokkiesToRequestHeaders (HttpRequestHeaders headers, ICollection<string>cookies)
		{
            headers.Add("Accept", "*/*");
			if (cookies.Count > 0) {
				var cookieBody = String.Join (", ", cookies);
				//Console.WriteLine (cookieBody);
				//headers.Add ("Cookie", cookieBody);
                headers.Add("Cookie", "checkinstation.auth_tkt=\"bf43e5e81a529cb98a75582bb3febdff52ea3e24NTlANQ%3D%3D!userid_type:b64str\"; checkinstation.auth_tkt=\"bf43e5e81a529cb98a75582bb3febdff52ea3e24NTlANQ%3D%3D!userid_type:b64str\"");
                logger.Debug("headers: {0}", headers);
			}
		}
	}
}

