using System;
using System.Net.Http;
using System.Threading.Tasks;
using System.Collections.Generic;

namespace QR
{
	class MainClass
	{
		public static void Main (string[] args)
		{
			Console.WriteLine ("Hello World!");
			//var t = GetJsonData ();
			var t = GetAuthData ();
			t.Wait ();
		}

		public static async Task GetJsonData ()
		{
			var url = "http://localhost:8000/qrdata.json";
			using (HttpClient client = new HttpClient (){ Timeout = TimeSpan.FromMinutes (1000) })
			using (HttpResponseMessage response = await client.GetAsync (url))
			using (HttpContent content = response.Content) {
				var s = await content.ReadAsStringAsync ();
				Console.WriteLine (s);
			}
		}

		public class LoginUser
		{
			public string login_id { get; set; }

			public string password { get; set; }
		}

		public static async Task GetAuthData ()
		{
			var url = "http://oshigoto:8040/login";
			var user = new LoginUser (){ login_id = "ts-rt-admin", password = "admin" };
			var factory = new HttpWrapperFactory<HttpWrapper> ();
			var wrapper = factory.Create (url);

			using (HttpResponseMessage r = await wrapper.PostAsJsonAsync (user)) {
				System.Console.WriteLine (r.Headers);
				var loginOutput = await r.Content.ReadAsStringAsync ();
				var headers = r.Headers;

				// cookie取得
				var cookies = CookieUtils.GetCookiesFromResponseHeaders (headers);

				Console.WriteLine ("login output: ", loginOutput);

				var url2 = "http://oshigoto:8040/login/status";
				factory.AddCookies (cookies as IEnumerable<string>);
				var wrapper2 = factory.Create (url2);

				var loginStatus = await wrapper2.GetStringAsync ();
				Console.WriteLine ("login status: {0}", loginStatus);
			}
		}
	}
}
