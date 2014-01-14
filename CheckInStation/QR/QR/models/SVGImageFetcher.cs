using System;
using QR.message;
using System.Threading.Tasks;
using System.Net.Http;
using Codeplex.Data;
using System.Collections.Generic;

namespace QR
{
	public class TicketTemplate
	{
		public string id { get; set; }

		public string name { get; set; }
	}

	public class SVGData
	{
		public string svg { get; set; }

		public TicketTemplate template { get; set; }
	}

	public class SVGImageFetcher
	{
		public IResource Resource { get; set; }

		public SVGImageFetcher (IResource resource)
		{
			Resource = resource;
		}

		public virtual string GetSvgOneURL ()
		{
			return Resource.EndPoint.QRSvgOne;
		}

		public virtual string GetImageFromSvgURL ()
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

		public IEnumerable<SVGData> ParseSvgOne (string response)
		{
			var json = DynamicJson.Parse (response); //throwable System.xml.XmlException
			var r = new List<SVGData> ();
			foreach (var data in json.datalist[0].svg_list) {
				var template = new TicketTemplate (){ id = data.ticket_template_id, name = data.ticket_template_name };
				r.Add (new SVGData (){ svg = data.svg, template = template });
			}
			return r;
		}

		public async Task<byte[]> GetImageFromSvg (string svg)
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
			try {
				var response = await GetSvgOne (tdata);
				var svg_list = ParseSvgOne (response);
				var r = new List<byte[]> ();
				foreach (SVGData svgdata in svg_list) {
					var image = await GetImageFromSvg (svgdata.svg);
					r.Add (image);
				}
				return new Success<string,List<byte[]>> (r);
			} catch (System.Xml.XmlException e) {
				Console.WriteLine (e.ToString ());
				return new Failure<string,List<byte[]>> (Resource.GetInvalidOutputMessage ());
			} catch (Exception e) {
				return new Failure<string,List<byte[]>> (e.ToString ());
			}
		}

		public Task<ResultTuple<string, bool>>PrintAllAsync ()
		{
			throw new NotImplementedException ();
		}
	}
}

