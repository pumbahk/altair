using System;
using System.Net.Http;
using System.Threading.Tasks;
using System.Collections.Generic;
using QR.message;
using NLog;

namespace QR
{
	class MainClass
	{
		private static Logger logger = LogManager.GetCurrentClassLogger ();

		public static void Main (string[] args)
		{
			Console.WriteLine ("Hello World!");

			//log sample
			logger.Trace("Sample trace message");
			logger.Debug("Sample debug message");
			logger.Info("Sample informational message");
			logger.Warn("Sample warning message");
			logger.Error("Sample error message");
			logger.Fatal("Sample fatal error message");
			
			//var t = GetJsonData ();
			var app = new Application ();
			var t = app.Run (new CaseAuthInput (app.Resource));
			t.Wait ();
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
			var auth = new Authentication (resource, "");
			ResultTuple<string, AuthInfo> result = await auth.AuthAsync ("ts-rt-admin", "admin");
			if (result.Status) {
				Console.WriteLine ("authinfo: {0}", result.Right);
			} else {
				Console.WriteLine ("failure: {0}", result.Left);
			}
		}
	}
}
