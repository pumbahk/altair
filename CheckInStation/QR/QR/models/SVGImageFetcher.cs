using System;
using QR.message;
using System.Threading.Tasks;
using System.Net.Http;
using Codeplex.Data;
using System.Collections.Generic;
using System.Linq;
using NLog;

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

	public class _SVGImageFetcherForOne
	{
		public static async Task<string> GetSvgDataList (IHttpWrapperFactory<HttpWrapper> factory, TicketData tdata, string url)
		{
			var data = new {
				ordered_product_item_token_id = tdata.ordered_product_item_token_id
			};

			using (var wrapper = factory.Create (url)) {
				using (HttpResponseMessage response = await wrapper.PostAsJsonAsync (data).ConfigureAwait (false)) {
					return (await wrapper.ReadAsStringAsync (response.Content).ConfigureAwait (false));
				}
			}
		}

		public static IEnumerable<SVGData> ParseSvgDataList (string response)
		{
			var json = DynamicJson.Parse (response); //throwable System.xml.XmlException
			var r = new List<SVGData> ();
			foreach (var data in json.datalist[0].svg_list) {
				var template = new TicketTemplate (){ id = data.ticket_template_id, name = data.ticket_template_name };
				r.Add (new SVGData (){ svg = data.svg, template = template });
			}
			return r;
		}
	}

	public class _SVGImageFetcherForAll
	{
		public static async Task<string> GetSvgDataList (IHttpWrapperFactory<HttpWrapper> factory, TicketDataCollection collection, string url)
		{
			var parms = new {
				token_id_list = collection.collection.Select (o => o.ordered_product_item_token_id).ToArray ()
			};

			using (var wrapper = factory.Create (url)) {
				using (HttpResponseMessage response = await wrapper.PostAsJsonAsync (parms).ConfigureAwait (false)) {
					return (await wrapper.ReadAsStringAsync (response.Content).ConfigureAwait (false));
				}
			}
		}

		public static IEnumerable<SVGData> ParseSvgDataList (string response)
		{
			var json = DynamicJson.Parse (response); //throwable System.xml.XmlException
			var r = new List<SVGData> ();
			foreach (var datalist in json.datalist) {
				foreach (var data in datalist.svg_list) {
					var template = new TicketTemplate (){ id = data.ticket_template_id, name = data.ticket_template_name };
					r.Add (new SVGData (){ svg = data.svg, template = template });
				}
			}
			return r;
		}
	}

	public class SVGImageFetcher
	{
		private static Logger logger = LogManager.GetCurrentClassLogger ();

		public IResource Resource { get; set; }

		public SVGImageFetcher (IResource resource)
		{
			Resource = resource;
		}

		public virtual string GetSvgOneURL ()
		{
			return Resource.EndPoint.QRSvgOne;
		}

		public virtual string GetSvgAllURL ()
		{
			return Resource.EndPoint.QRSvgAll;
		}

		public virtual string GetImageFromSvgURL ()
		{
			return Resource.EndPoint.ImageFromSvg;
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

		public async Task<ResultTuple<string, List<byte[]>>> FetchImageForOneAsync (TicketData tdata)
		{
			try {
				var response = await _SVGImageFetcherForOne.GetSvgDataList (Resource.HttpWrapperFactory, tdata, GetSvgOneURL ());
				var svg_list = _SVGImageFetcherForOne.ParseSvgDataList (response);
				var r = new List<byte[]> ();
				foreach (SVGData svgdata in svg_list) {
					var image = await GetImageFromSvg (svgdata.svg);
					r.Add (image);
				}
				return new Success<string,List<byte[]>> (r);
			} catch (System.Xml.XmlException e) {
				logger.ErrorException ("exception:", e);
				return new Failure<string,List<byte[]>> (Resource.GetInvalidOutputMessage ());
			} catch (Exception e) {
				logger.ErrorException ("exception:", e);
				return new Failure<string, List<byte[]>> (Resource.GetDefaultErrorMessage ());
			}
		}

		public async Task<ResultTuple<string, List<Byte[]>>>FetchImageForAllAsync (TicketDataCollection collection)
		{
			try {
				var response = await _SVGImageFetcherForAll.GetSvgDataList (Resource.HttpWrapperFactory, collection, GetSvgAllURL ());
				var svg_list = _SVGImageFetcherForAll.ParseSvgDataList (response);
				var r = new List<byte[]> ();
				foreach (SVGData svgdata in svg_list) {
					var image = await GetImageFromSvg (svgdata.svg);
					r.Add (image);
				}
				return new Success<string,List<byte[]>> (r);
			} catch (System.Xml.XmlException e) {
				logger.ErrorException ("exception:", e);
				return new Failure<string,List<byte[]>> (Resource.GetInvalidOutputMessage ());
			} catch (Exception e) {
				logger.ErrorException ("exception:", e);
				return new Failure<string, List<byte[]>> (Resource.GetDefaultErrorMessage ());
			}
		}
	}
}

