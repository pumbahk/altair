using System;
using QR.message;
using System.Threading.Tasks;
using System.Net.Http;
using Codeplex.Data;
using System.Collections.Generic;

namespace QR
{
	public class SVGImage
	{
		public IResource Resource { get; set; }

		public SVGImage (IResource resource)
		{
			Resource = resource;
		}

		public string GetSvgOneURL ()
		{
			return Resource.EndPoint.QRSvgOne;
		}

		public string GetImageFromSvgURL()
		{
			return Resource.EndPoint.ImageFromSvg;
		}

		public async Task<string> GetSvgOne (TicketData tdata)
		{
			var data = new {
				ordered_product_item_token_id = tdata.ordered_product_item_token_id
			};

			IHttpWrapperFactory<HttpWrapper> factory = Resource.HttpWrapperFactory;
			using (var wrapper = factory.Create (GetSvgOneURL ())) {
				using (HttpResponseMessage response = await wrapper.PostAsJsonAsync (data).ConfigureAwait (false)) {
					return (await wrapper.ReadAsStringAsync (response.Content).ConfigureAwait (false));
				}
			}
		}

		public string[] ParseSvgOne (string response)
		{
			try {
				var json = DynamicJson.Parse (response);
				return json.datalist [0].svg_list;
			} catch (System.Xml.XmlException) {
				//hmm. log?
				return new string[] { };
			}
		}

		public async Task<byte[]> GetImageFromSvg(string svg)
		{
			var data = new {
				svg = svg
			};

			IHttpWrapperFactory<HttpWrapper> factory = Resource.HttpWrapperFactory;
			using (var wrapper = factory.Create (GetImageFromSvgURL ())) {
				using (HttpResponseMessage response = await wrapper.PostAsJsonAsync (data).ConfigureAwait (false)) {
					return await response.Content.ReadAsByteArrayAsync ().ConfigureAwait (false);
				}
			}
		}

		public async Task<ResultTuple<string, List<byte[]>>> FetchImageAsync (TicketData tdata)
		{
			var response = await GetSvgOne (tdata);
			var svg_list = ParseSvgOne (response);
			var r = new List<byte[]>();
			foreach (string svg in svg_list) {
				var image = await GetImageFromSvg (svg);
				r.Add(image);
			}
			return new Success<string,List<byte[]>>(r);
		}

		public Task<ResultTuple<string, bool>>PrintAllAsync ()
		{
			throw new NotImplementedException ();
		}
	}
}

