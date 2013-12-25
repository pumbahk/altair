using System;
using System.Net.Http;
using System.Threading.Tasks;

namespace QR
{
	class MainClass
	{
		public static void Main (string[] args)
		{
			Console.WriteLine ("Hello World!");
			var t = GetJsonData ();
			t.Wait ();
		}

		public static async Task GetJsonData ()
		{
			var url = "http://localhost:8000/qrdata.json";
			using (HttpClient client = new HttpClient (){ Timeout = TimeSpan.FromMinutes(1000)})
			using (HttpResponseMessage response = await client.GetAsync (url))
			using (HttpContent content = response.Content) {
				var s = await content.ReadAsStringAsync ();
				Console.WriteLine (s);
			}
		}
	}
}
