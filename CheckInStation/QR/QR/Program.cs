using System;
using System.Net.Http;
using System.Threading.Tasks;
using System.Collections.Generic;

using QR.message;
namespace QR
{
	class MainClass
	{
		public static void Main (string[] args)
		{
			Console.WriteLine ("Hello World!");
			//var t = GetJsonData ();
			var app = new Application ();
			app.Run (new CaseAuthInput (app.Resource));
			// var t = GetAuthData (resource);
			// t.Wait ();
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
			ResultTuple<string, AuthInfo> result = await auth.AuthAsync (resource, "ts-rt-admin", "admin");
			if (result.Status) {
				Console.WriteLine ("authinfo: {0}", result.Right);
			} else {
				Console.WriteLine ("failure: {0}", result.Left);
			}
		}
	}
}
