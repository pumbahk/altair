using System;
using System.Net.Http;
using System.Threading.Tasks;
using System.Collections.Generic;
using checkin.core.message;
using NLog;
using checkin.core.support;
using checkin.core.models;
using checkin.core.auth;

namespace checkin.core
{
    class MainClass
    {
        private static Logger logger = LogManager.GetCurrentClassLogger ();

        public static void Main_ (string[] args)
        {
            Console.WriteLine ("Hello World!");

            //log sample
            logger.Trace ("Sample trace message");
            logger.Debug ("Sample debug message");
            logger.Info ("Sample informational message");
            logger.Warn ("Sample warning message");
            logger.Error ("Sample error message");
            logger.Fatal ("Sample fatal error message");
        }

        public static async Task GetJsonData ()
        {
            var url = "http://localhost:8000/qrdata.json";
            using (HttpClient client = new HttpClient (){ Timeout = TimeSpan.FromMinutes (1000) })
            using (HttpResponseMessage response = await client.GetAsync (url))
            using (HttpContent content = response.Content) {
                var s = await content.ReadAsStringAsync ();
                Console.WriteLine (s);
            }
        }

        public static async Task GetAuthData (IResource resource)
        {
            var auth = new Authentication (resource, "");
            ResultTuple<string, AuthInfo> result = await auth.AuthAsync ("ts-rt-admin", "admin");
            if (result.Status) {
                Console.WriteLine ("authinfo: {0}", result.Right);
            } else {
                Console.WriteLine ("failure: {0}", result.Left);
            }
        }
    }
}
