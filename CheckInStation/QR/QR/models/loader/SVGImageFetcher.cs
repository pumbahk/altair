using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Threading.Tasks;
using NLog;
using Codeplex.Data;
using QR.message;

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

		public string token_id { get; set; }

		public TicketTemplate template { get; set; }
	}

	public class TicketImageData
	{
		public string token_id { get; set; }

		public byte[] image { get; set; }
	}

	public class _SVGImageFetcherForOne
	{
		public static async Task<string> GetSvgDataList (IHttpWrapperFactory<HttpWrapper> factory, TicketData tdata, string url)
		{
			var data = new {
				ordered_product_item_token_id = tdata.ordered_product_item_token_id,
				secret = tdata.secret
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
			string token_id = ((long)(json.datalist [0].ordered_product_item_token_id)).ToString ();
			foreach (var data in json.datalist[0].svg_list) {
				var template = new TicketTemplate (){ id = data.ticket_template_id, name = data.ticket_template_name };
				r.Add (new SVGData () {
					svg = data.svg,
					template = template,
					token_id = token_id
				});
			}
			return r;
		}
	}

	public class _SVGImageFetcherForAll
	{
		public static async Task<string> GetSvgDataList (IHttpWrapperFactory<HttpWrapper> factory, TicketDataCollection collection, string url)
		{
			var parms = new {
				token_id_list = collection.collection.Select (o => o.ordered_product_item_token_id).ToArray (),
				secret = collection.secret
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
				string token_id = ((long)(datalist.ordered_product_item_token_id)).ToString ();
				foreach (var data in datalist.svg_list) {
					var template = new TicketTemplate (){ id = data.ticket_template_id, name = data.ticket_template_name };
					r.Add (new SVGData (){ svg = data.svg, template = template, token_id = token_id });
				}
			}
			return r;
		}
	}

    /* TODO: split file
     * IImageFromSvg, ImageFromSvg, ImageFromSvgBase64
     */

    public interface IImageFromSvg
    {
       Task<byte[]> GetImageFromSvg(string svg);
    }

    public class ImageFromSvg : IImageFromSvg
    {
        public ImageFromSvg(IResource resource)
        {
            this.Resource = resource;
        }
        public IResource Resource { get; set; }
        public virtual string GetImageFromSvgURL()
        {
            return Resource.EndPoint.ImageFromSvg;
        }

        public async Task<byte[]> GetImageFromSvg(string svg)
        {
            var data = new
            {
                svg = svg
            };

            IHttpWrapperFactory<HttpWrapper> factory = Resource.HttpWrapperFactory;
            using (var wrapper = factory.Create(GetImageFromSvgURL()))
            {
                using (HttpResponseMessage response = await wrapper.PostAsJsonAsync(data).ConfigureAwait(false))
                {

                    return await response.Content.ReadAsByteArrayAsync().ConfigureAwait(false);
                }
            }
        }

    }

    public class ImageFromSvgBase64 : IImageFromSvg
    {
        public ImageFromSvgBase64(IResource resource)
        {
            this.Resource = resource;
        }

        public IResource Resource { get; set; }
        public virtual string GetImageFromSvgURL()
        {
            return Resource.EndPoint.ImageFromSvg;
        }

         // use preview server api instead of custom svg image api. this is adapter.
        public async Task<byte[]> GetImageFromSvg(string svg)
        {
            var data = new
            {
                svgfile = svg, raw=true
            };

            IHttpWrapperFactory<HttpWrapper> factory = Resource.HttpWrapperFactory;
            using (var wrapper = factory.Create(GetImageFromSvgURL()))
            {
                using (HttpResponseMessage response = await wrapper.PostAsJsonAsync(data).ConfigureAwait(false))
                {

                    return await response.Content.ReadAsByteArrayAsync().ConfigureAwait(false);
                }
            }
        }
    }

	public class SVGImageFetcher
	{
		private static Logger logger = LogManager.GetCurrentClassLogger ();
        public IImageFromSvg ImageFromSvg { get; set; }
		public IResource Resource { get; set; }

		public SVGImageFetcher (IResource resource)
		{
			Resource = resource;
            this.ImageFromSvg = new ImageFromSvg(resource);
		}

        public SVGImageFetcher(IResource resource, IImageFromSvg imageFromSVG)
        {
            Resource = resource;
            this.ImageFromSvg = imageFromSVG;
        }

        public Task<byte[]> GetImageFromSvg(string svg)
        {
            return this.ImageFromSvg.GetImageFromSvg(svg);
        }

		public virtual string GetSvgOneURL ()
		{
			return Resource.EndPoint.QRSvgOne;
		}

		public virtual string GetSvgAllURL ()
		{
			return Resource.EndPoint.QRSvgAll;
		}

		public async Task<ResultTuple<string, List<TicketImageData>>> FetchImageDataForOneAsync (TicketData tdata)
		{
			try {
				var response = await _SVGImageFetcherForOne.GetSvgDataList (Resource.HttpWrapperFactory, tdata, GetSvgOneURL ());
				var svg_list = _SVGImageFetcherForOne.ParseSvgDataList (response);
				var r = new List<TicketImageData> ();
				foreach (SVGData svgdata in svg_list) {
					var image = await GetImageFromSvg (svgdata.svg);
					if (svgdata.token_id != tdata.ordered_product_item_token_id) {
						throw new ArgumentException (String.Format ("assert svgdata.token_id = ordered_product_item_token_id, {0} = {1}", svgdata.token_id, tdata.ordered_product_item_token_id));
					}
					r.Add (new TicketImageData (){ token_id = svgdata.token_id, image = image });
				}
				return new Success<string,List<TicketImageData>> (r);
			} catch (System.Xml.XmlException e) {
				logger.ErrorException (":", e);
				return new Failure<string,List<TicketImageData>> (Resource.GetInvalidOutputMessage ());
			} catch (Exception e) {
				logger.ErrorException (":", e);
				return new Failure<string, List<TicketImageData>> (Resource.GetDefaultErrorMessage ());
			}
		}

		public async Task<ResultTuple<string, List<TicketImageData>>>FetchImageDataForAllAsync (TicketDataCollection collection)
		{
			try {
				var response = await _SVGImageFetcherForAll.GetSvgDataList (Resource.HttpWrapperFactory, collection, GetSvgAllURL ()).ConfigureAwait (false);
				var svg_list = _SVGImageFetcherForAll.ParseSvgDataList (response);
				var r = new List<TicketImageData> ();
				foreach (SVGData svgdata in svg_list) {
					var image = await GetImageFromSvg (svgdata.svg).ConfigureAwait (false);
					r.Add (new TicketImageData (){ token_id = svgdata.token_id, image = image });
				}
				return new Success<string,List<TicketImageData>> (r);
			} catch (System.Xml.XmlException e) {
				logger.ErrorException (":", e);
				return new Failure<string,List<TicketImageData>> (Resource.GetInvalidOutputMessage ());
			} catch (Exception e) {
				logger.ErrorException (":", e);
				return new Failure<string, List<TicketImageData>> (Resource.GetDefaultErrorMessage ());
			}
		}
	}
}

