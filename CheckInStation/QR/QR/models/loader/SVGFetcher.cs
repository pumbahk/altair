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
using QR.support;

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

    public enum TicketImageDataType{
        image,
        xaml
    }


    public class SVGFetcherForOne
    {
        public readonly String Url;
        public static Logger logger = LogManager.GetCurrentClassLogger();
        public SVGFetcherForOne(string url)
        {
            this.Url = url;
        }
        public async Task<Stream> GetSvgDataList (IHttpWrapperFactory<HttpWrapper> factory, TicketData tdata)
        {
            var data = new {
                ordered_product_item_token_id = tdata.ordered_product_item_token_id,
                secret = tdata.secret
            };

            using (var wrapper = factory.Create(this.Url))
            {
                HttpResponseMessage response = await wrapper.PostAsJsonAsync(data).ConfigureAwait(false);
                response.EnsureSuccessStatusCodeExtend();
                return (await wrapper.ReadAsStreamAsync(response.Content).ConfigureAwait(false));
            }
        }

        public IEnumerable<SVGData> ParseSvgDataList (Stream response)
        {
            var json = DynamicJson.Parse (response); //throwable System.xml.XmlException
            logger.Info("*API Response* method=POST, url={0}, data={1}".WithMachineName(), this.Url, json.ToString());
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

    public class SVGFetcherForAll
    {
        public readonly string Url;
        public static Logger logger = LogManager.GetCurrentClassLogger();

        public SVGFetcherForAll(string url)
        {
            this.Url = url;
        }
        public async Task<Stream> GetSvgDataList(IHttpWrapperFactory<HttpWrapper> factory, TicketDataCollection collection)
        {
            var parms = new
            {
                token_id_list = collection.collection.Where(o => o.is_selected).Select(o => o.ordered_product_item_token_id).ToArray(),
                secret = collection.secret
            };
            using (var wrapper = factory.Create(this.Url))
            {
                HttpResponseMessage response = await wrapper.PostAsJsonAsync(parms).ConfigureAwait(false);
                response.EnsureSuccessStatusCodeExtend();
                return (await wrapper.ReadAsStreamAsync(response.Content).ConfigureAwait(false));
            }
        }
                
            
        

        public IEnumerable<SVGData> ParseSvgDataList (Stream response)
        {
            var json = DynamicJson.Parse (response); //throwable System.xml.XmlException
            logger.Info("*API Response* method=POST, url={0}, data={1}".WithMachineName(), this.Url, json.ToString());
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

}

