using NLog;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;

namespace checkin.core.support
{
    public static class EnsureResponse
    {
        public static Logger logger = LogManager.GetCurrentClassLogger();

        public static string ERROR_MESSAGE_PREFIX = "E@:";

        public static bool HasSpecificErrorMessage(string s)
        {
            return s.StartsWith(ERROR_MESSAGE_PREFIX);
        }

        public static string StripHeader(string message)
        {
            var d = message.IndexOf(ERROR_MESSAGE_PREFIX);
            if (d > -1)
            {
                return message.Substring(d);
            }
            else
            {
                return message;
            }

        }

        public static HttpResponseMessage EnsureSuccessStatusCodeExtend(this HttpResponseMessage response){
            if (response.IsSuccessStatusCode)
            {
                return response;
            }
            if (response.StatusCode == System.Net.HttpStatusCode.BadRequest)
            {
                var t = response.Content.ReadAsStringAsync();
                t.Wait(300); //xxxx:
                if (t.Status == TaskStatus.RanToCompletion)
                {
                    throw new TransparentMessageException(StripHeader(t.Result));
                }
                logger.Warn("task timeout (wait time = 300millisec)".WithMachineName());
                return response.EnsureSuccessStatusCode();
            } else if(response.StatusCode == System.Net.HttpStatusCode.InternalServerError){
                var t = response.Content.ReadAsStringAsync();
                t.Wait(300); //xxxx:
                if (t.Status == TaskStatus.RanToCompletion)
                {
                    logger.Error("INTERNAL SERVER ERROR: message={0}".WithMachineName(),
                        StripHeader(t.Result));
                    return response.EnsureSuccessStatusCode();
                }
                logger.Warn("task timeout (wait time = 300millisec)".WithMachineName());
                return response.EnsureSuccessStatusCode();
            } else {
                return response.EnsureSuccessStatusCode();
            }
        }
    }
}
