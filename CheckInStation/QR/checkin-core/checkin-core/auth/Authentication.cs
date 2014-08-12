using System;
using System.Threading.Tasks;
using System.Net.Http;
using checkin.core.message;
using Codeplex.Data;
using NLog;
using checkin.core.support;
using checkin.core.events;
using checkin.core.models;
using checkin.core.web;

namespace checkin.core.auth
{
    public class Authentication :IAuthentication
    {
        public IResource Resource { get; set; }

        private static Logger logger = LogManager.GetCurrentClassLogger ();

        public String LoginURL{ get; set; }

        public Authentication (IResource resource)
        {
            Resource = resource;
        }

        public Authentication (IResource resource, string loginURL) : this (resource)
        {
            LoginURL = loginURL;
        }

        // url
        public string GetLoginURL ()
        {
            return this.LoginURL;
        }
        /*
         * API Response
         * 
         * {endpoint: {"login_status": "http://foo"}, ad_images: ["http://foo.bar.jp/foo.jpg"]}
         */
        public async Task<EndPoint> TryLoginRequest(string name, string password)
        {
            IHttpWrapperFactory<HttpWrapper> factory = Resource.HttpWrapperFactory;
            using (var wrapper = factory.Create(GetLoginURL()))
            {
                var device_id = this.Resource.GetUniqueNameEachMachine();

                //@global ev:
                //GlobalStaticEvent.FireDescriptionMessageEvent(this, "ログイン処理中です");
                var user = new LoginUser() { login_id = name, password = password, device_id = device_id };
                HttpResponseMessage response = await wrapper.PostAsJsonAsync(user).ConfigureAwait(false);
                response.EnsureSuccessStatusCodeExtend();
                //成功後
                this.Resource.LoginUser = user;

                // cookie取得
                var headers = response.Headers;
                factory.AddCookies(CookieUtils.GetCookiesFromResponseHeaders(GetLoginURL(), headers));


                // endpointの取得
                //@global ev:
                GlobalStaticEvent.FireDescriptionMessageEvent(this, "アプリケーションに必要な情報を取得しています");
                var result = DynamicJson.Parse(await wrapper.ReadAsStreamAsync(response.Content).ConfigureAwait(false));
                logger.Info("*API Response* method=POST, url={0}, data={1}".WithMachineName(), this.GetLoginURL(), result.ToString());
                var endpoint = new EndPoint(result.endpoint);

                //広告用の画像のurl設定
                string[] images = result.ad_images;
                endpoint.ConfigureAdImages(images); //xxx: bad-code

                return endpoint;

            }
        }
        /*
         * API Response
         * 
         * {"login": True,
            "loginuser": {"type": u"login",
                          "id": unicode(operator.id),
                          "name": operator.name},
            "organization": {"id": operator.organization_id}}
          */
        public async Task<AuthInfo> TryLoginStatusRequest (string url)
        {
            IHttpWrapperFactory<HttpWrapper> factory = Resource.HttpWrapperFactory;
            using (var wrapper = factory.Create (url)) {
                var s = await wrapper.GetStringAsync ().ConfigureAwait (false);
                var result = DynamicJson.Parse (s);
                logger.Info("*API Response* method=GET, url={0}, data={1}".WithMachineName(), this.GetLoginURL(), result.ToString());
                return new AuthInfo (result);
            }
        }

        public async virtual Task<ResultTuple<string, AuthInfo>> AuthAsync(string name, string password)
        {
            EndPoint endpoint;
            endpoint = await TryLoginRequest(name, password);
            var statusData = await TryLoginStatusRequest(endpoint.LoginStatus);
            if (statusData.login)
                return OnSuccess(endpoint, statusData);
                else
                return OnFailure();
        }

        public virtual Success<string, AuthInfo> OnSuccess (EndPoint endpoint, AuthInfo statusData)
        {
            Resource.EndPoint = endpoint;
            return new Success<string,AuthInfo> (statusData);
        }

        public Failure<string, AuthInfo> OnFailure ()
        {
            var message = string.Format (Resource.GetLoginFailureMessageFormat ());
            return new Failure<string,AuthInfo> (message);
        }

        public Failure<string, AuthInfo> OnFailure (string message)
        {
            return new Failure<string,AuthInfo> (message);
        }
    }
}

