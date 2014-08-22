using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Threading.Tasks;
using NLog;
using Codeplex.Data;
using checkin.core.message;
using System.IO;
using System.Text;
using System.Net.Http.Headers;
using checkin.core.support;

namespace checkin.core.models
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
                var fetcher = new SVGFetcherForOne(this.GetSvgOneURL(), this.Resource);
                var response = await fetcher.GetSvgDataList (Resource.HttpWrapperFactory, tdata);                
                var svg_list = fetcher.ParseSvgDataList (response);
                var coll = new List<TicketImageData> ();
                foreach (SVGData svgdata in svg_list) {
                if (svgdata.token_id != tdata.ordered_product_item_token_id) {
                    throw new ArgumentException (String.Format ("assert svgdata.token_id = ordered_product_item_token_id, {0} = {1}", svgdata.token_id, tdata.ordered_product_item_token_id));
                    }
                    coll.Add (TicketImageData.XamlTicketData (svgdata.token_id, svgdata.template.id, svgdata.svg));
                }
            return new Success<string, List<TicketImageData>> (coll);
            } catch (System.Xml.XmlException e) {
                logger.ErrorException (":".WithMachineName(), e);
                return new Failure<string,List<TicketImageData>> (Resource.GetInvalidOutputMessage ());
            } catch (Exception e) {
                logger.ErrorException (":".WithMachineName(), e);
                return new Failure<string, List<TicketImageData>> (Resource.GetDefaultErrorMessage ());
            }
        }

        public async Task<ResultTuple<string, List<TicketImageData>>> FetchImageDataForAllAsync(TicketDataCollection collection)
        {
            try
            {
                var fetcher = new SVGFetcherForAll(this.GetSvgAllURL(), this.Resource);
                var response = await fetcher.GetSvgDataList(Resource.HttpWrapperFactory, collection).ConfigureAwait(false);

                var svg_list = fetcher.ParseSvgDataList(response);

                var r = new List<TicketImageData>();
                foreach (SVGData svgdata in svg_list)
                {
                    r.Add(TicketImageData.XamlTicketData(svgdata.token_id, svgdata.template.id, svgdata.svg));
                }
                return new Success<string, List<TicketImageData>>(r);
            }
            catch (System.Xml.XmlException e)
            {
                logger.ErrorException(":".WithMachineName(), e);
                return new Failure<string, List<TicketImageData>>(Resource.GetInvalidOutputMessage());
            }
            catch (Exception e)
            {
                logger.ErrorException(":".WithMachineName(), e);
                return new Failure<string, List<TicketImageData>>(Resource.GetDefaultErrorMessage());
            }
        }
    }
}
