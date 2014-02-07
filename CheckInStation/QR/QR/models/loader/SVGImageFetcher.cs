using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Threading.Tasks;
using NLog;
using Codeplex.Data;
using QR.message;
using System.IO;
using System.Text;
using System.Net.Http.Headers;

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
     * IImageFromSvg, ImageFromSvg, ImageFromSvgPostMultiPart
     */

    public interface IImageFromSvg
    {
       Task<byte[]> GetImageFromSvg(string svg);
    }

    public class ImageFromSvg : IImageFromSvg
    {
        private static Logger logger = LogManager.GetCurrentClassLogger();
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
                    if (response.StatusCode == System.Net.HttpStatusCode.OK)
                    {
                        return await response.Content.ReadAsByteArrayAsync().ConfigureAwait(false);
                    }
                    else
                    {
                        logger.Info("image fetching status code: {0}", response.StatusCode);
                        return null; //Too-Bad!!
                    }                    
                }
            }
        }

    }

    public class ImageFromSvgPostMultipart : IImageFromSvg
    {
        private static Logger logger = LogManager.GetCurrentClassLogger();
        public ImageFromSvgPostMultipart(IResource resource)
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

            var data = new MultipartFormDataContent();

            data.Add(new StringContent("raw"), "true");
            var svgFileLike = new StreamContent(new MemoryStream(Encoding.UTF8.GetBytes(svg)));
            svgFileLike.Headers.ContentDisposition = new ContentDispositionHeaderValue("attachment")
            {
                FileName = "svg.svg",
                Name = "svgfile"
            };
            data.Add(svgFileLike);

            IHttpWrapperFactory<HttpWrapper> factory = Resource.HttpWrapperFactory;
            var wrapper = factory.Create(GetImageFromSvgURL());
            //todo:é∏îsÇµÇΩÇ∆Ç´ÇÃèàóù(status!=200)
            HttpResponseMessage response = await wrapper.PostAsJsonAsync(data).ConfigureAwait(false);
            response.EnsureSuccessStatusCode(); //throw exception?

            if (response.StatusCode == System.Net.HttpStatusCode.OK)
            {
                return await response.Content.ReadAsByteArrayAsync().ConfigureAwait(false);
            }
            else
            {
                logger.Info("image fetching status code: {0}", response.StatusCode);
                return null; //Too-bad!!
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

                    //TODO: ê^ñ ñ⁄Ç…èàóùèëÇ≠GetImageFromSvg
					var image = await GetImageFromSvg (svgdata.svg);
                    if (image == null)                    
                    {
                        logger.Error("image fetching is failure. token_id={0}", svgdata.token_id);
                        return new Failure<string, List<TicketImageData>>(Resource.GetInvalidOutputMessage());
                    }

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

