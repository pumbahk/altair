
using NLog;
using checkin.core.support;
namespace checkin.core.web
{
    public class TrasparentUrlBuilder :IUrlBuilder
    {
        private static Logger logger = LogManager.GetCurrentClassLogger();
        public string Url{ get; set; }

        public TrasparentUrlBuilder (string url)
        {
            Url = url;
        }

        public string Build ()
        {
            logger.Info("*http client* request url: {0}".WithMachineName(), this.Url);
            return Url;
        }
    }
}

