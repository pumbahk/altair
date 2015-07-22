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

namespace checkin.core.models
{

    public class TicketImageData
    {
        public readonly TicketImageDataType Type;        
        public string ticket_id {get;set;}
        public string token_id { get; set; }

        public byte[] image { get; set; }

        public string xaml {get; set;}
        public TicketImageData(TicketImageDataType t){
            this.Type = t;
        }

        public static TicketImageData XamlTicketData(string token_id, string ticket_id, string xaml){
            return new TicketImageData (TicketImageDataType.xaml){ token_id = token_id, xaml = xaml, ticket_id = ticket_id };
        }
        public static TicketImageData ImageTicketData(string token_id, string ticket_id, byte[] image){
            return new TicketImageData (TicketImageDataType.image){ token_id = token_id, image = image, ticket_id = ticket_id };
        }
    }

    /* TODO: split file
     * IImageFromSvg, ImageFromSvg, ImageFromSvgPostMultiPart
     */

}
