
using NLog;
namespace QR
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
            logger.Info("*http client* request url: {0}", this.Url);
            return Url;
        }
    }
}

