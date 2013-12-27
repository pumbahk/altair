using System;
using System.Collections.Generic;
using System.Net.Http.Headers;

namespace QR
{
	public class CookieUtils
	{
		public static IEnumerable<string>GetCookiesFromResponseHeaders (HttpResponseHeaders headers)
		{

			IEnumerable<string> setCookiesSentences;
			ISet<string> cookies = new HashSet<string> ();

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
			if (cookies.Count > 0) {
				Console.WriteLine ("headers: {0}", headers);
				var cookieBody = String.Join (", ", cookies);
				//Console.WriteLine (cookieBody);
				headers.Add ("Cookie", cookieBody);
			}
		}
	}
}

