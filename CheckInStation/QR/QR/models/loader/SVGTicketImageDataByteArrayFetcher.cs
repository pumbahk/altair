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
            //todo:???s??????????????(status!=200)
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
    /// <summary>
    /// SVG ticket image data byte array fetcher. svgデータを画像として受け取る版
    /// </summary>
    public class SVGTicketImageDataByteArrayFetcher :ISVGTicketImageDataFetcher
    {
        private static Logger logger = LogManager.GetCurrentClassLogger ();
        public IImageFromSvg ImageFromSvg { get; set; }
        public IResource Resource { get; set; }

        public SVGTicketImageDataByteArrayFetcher (IResource resource)
        {
            Resource = resource;
            this.ImageFromSvg = new ImageFromSvg(resource);
        }

        public SVGTicketImageDataByteArrayFetcher(IResource resource, IImageFromSvg imageFromSVG)
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
                var response = await SVGFetcherForOne.GetSvgDataList (Resource.HttpWrapperFactory, tdata, GetSvgOneURL ());
                var svg_list = SVGFetcherForOne.ParseSvgDataList (response);
                var r = new List<TicketImageData> ();
                foreach (SVGData svgdata in svg_list) {

                    var image = await GetImageFromSvg (svgdata.svg);
                    if (image == null)                    
                    {
                        logger.Error("image fetching is failure. token_id={0}", svgdata.token_id);
                        return new Failure<string, List<TicketImageData>>(Resource.GetInvalidOutputMessage());
                    }

                    if (svgdata.token_id != tdata.ordered_product_item_token_id) {
                        throw new ArgumentException (String.Format ("assert svgdata.token_id = ordered_product_item_token_id, {0} = {1}", svgdata.token_id, tdata.ordered_product_item_token_id));
                    }
                    r.Add (TicketImageData.ImageTicketData(svgdata.token_id, svgdata.template.id, image));
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
                var response = await SVGFetcherForAll.GetSvgDataList (Resource.HttpWrapperFactory, collection, GetSvgAllURL ()).ConfigureAwait (false);
                var svg_list = SVGFetcherForAll.ParseSvgDataList (response);
                var r = new List<TicketImageData> ();
                foreach (SVGData svgdata in svg_list) {
                    var image = await GetImageFromSvg (svgdata.svg).ConfigureAwait (false);
                    r.Add (TicketImageData.ImageTicketData(svgdata.token_id, svgdata.template.id, image));
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
