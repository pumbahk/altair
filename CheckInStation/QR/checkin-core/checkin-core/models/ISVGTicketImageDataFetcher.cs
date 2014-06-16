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

    /* TODO: split file
     * IImageFromSvg, ImageFromSvg, ImageFromSvgPostMultiPart
     */

    public interface ISVGTicketImageDataFetcher{
        Task<ResultTuple<string, List<TicketImageData>>> FetchImageDataForOneAsync (TicketData tdata);
        Task<ResultTuple<string, List<TicketImageData>>>FetchImageDataForAllAsync (TicketDataCollection collection);
        string GetSvgOneURL ();
        string GetSvgAllURL ();
    }

}
