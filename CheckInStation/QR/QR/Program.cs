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
			var resource = new Resource () {
				HttpWrapperFactory = new HttpWrapperFactory<HttpWrapper> ()
			};
			if (resource.HttpWrapperFactory == null) {
				throw new InvalidOperationException ("factory is null");
			}
			var t = GetAuthData (resource);
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

		public static async Task GetAuthData (IResource resource)
		{
			var auth = new Authentication ();
			ResultTuple<string, AuthInfo> result = await auth.authAsync (resource, "ts-rt-admin", "admin");
			if (result.Status) {
				Console.WriteLine ("authinfo: {0}", result.Right);
			} else {
				Console.WriteLine ("failure: {0}", result.Left);
			}
			}
		}
	}
