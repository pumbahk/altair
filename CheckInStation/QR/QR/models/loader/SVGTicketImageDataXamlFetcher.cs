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

    /// <summary>
    /// SVG ticket image data xaml fetcher. SVGデータをxamlとして受け取る版
    /// </summary>
    public class SVGTicketImageDataXamlFetcher :ISVGTicketImageDataFetcher{
        private static Logger logger = LogManager.GetCurrentClassLogger ();
        public IResource Resource {get;set;}

        public SVGTicketImageDataXamlFetcher(IResource resource)
        {
            this.Resource = resource;
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
            try{
                var response = await SVGFetcherForOne.GetSvgDataList (Resource.HttpWrapperFactory, tdata, GetSvgOneURL ());                
                var svg_list = SVGFetcherForOne.ParseSvgDataList (response);
                var coll = new List<TicketImageData> ();
                foreach (SVGData svgdata in svg_list) {
                if (svgdata.token_id != tdata.ordered_product_item_token_id) {
                    throw new ArgumentException (String.Format ("assert svgdata.token_id = ordered_product_item_token_id, {0} = {1}", svgdata.token_id, tdata.ordered_product_item_token_id));
                    }
                    coll.Add (TicketImageData.XamlTicketData (svgdata.token_id, svgdata.template.id, svgdata.svg));
                }
            return new Success<string, List<TicketImageData>> (coll);
            } catch (System.Xml.XmlException e) {
                logger.ErrorException (":", e);
                return new Failure<string,List<TicketImageData>> (Resource.GetInvalidOutputMessage ());
            } catch (Exception e) {
                logger.ErrorException (":", e);
                return new Failure<string, List<TicketImageData>> (Resource.GetDefaultErrorMessage ());
            }
        }

        public async Task<ResultTuple<string, List<TicketImageData>>> FetchImageDataForAllAsync(TicketDataCollection collection)
        {
            string response;
            IEnumerable<SVGData> svg_list;

            try
            {
                using (new TimeIt(String.Format("    {0}@FetchImageDataForAllAsync@GetSvgDataList", this.GetType())))
                {
                    response = await SVGFetcherForAll.GetSvgDataList(Resource.HttpWrapperFactory, collection, GetSvgAllURL()).ConfigureAwait(false);
                }

                using (new TimeIt(String.Format("    {0}@FetchImageDataForAllAsync@ParseSVGDataList", this.GetType())))
                {
                    svg_list = SVGFetcherForAll.ParseSvgDataList(response);
                }

                using (new TimeIt(String.Format("    {0}@FetchImageDataForAllAsync@ConvertSVGDataList", this.GetType())))
                {
                    var r = new List<TicketImageData>();
                    foreach (SVGData svgdata in svg_list)
                    {
                        r.Add(TicketImageData.XamlTicketData(svgdata.token_id, svgdata.template.id, svgdata.svg));
                    }
                    return new Success<string, List<TicketImageData>>(r);
                }
            }
            catch (System.Xml.XmlException e)
            {
                logger.ErrorException(":", e);
                return new Failure<string, List<TicketImageData>>(Resource.GetInvalidOutputMessage());
            }
            catch (Exception e)
            {
                logger.ErrorException(":", e);
                return new Failure<string, List<TicketImageData>>(Resource.GetDefaultErrorMessage());
            }
        }

    }
        
}
