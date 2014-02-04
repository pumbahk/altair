using System;
using System.Threading.Tasks;
using System.Net.Http;
using QR.message;
using Codeplex.Data;
using NLog;

namespace QR
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

		public class LoginUser
		{
			public string login_id { get; set; }

			public string password { get; set; }

            public string device_id { get; set; } //端末ごとにuniqueなid(e.g. xxxのPC)
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
		public async Task<EndPoint> TryLoginRequest (string name, string password)
		{
			IHttpWrapperFactory<HttpWrapper> factory = Resource.HttpWrapperFactory;
			using (var wrapper = factory.Create (GetLoginURL ())) {                
                var device_id = this.Resource.GetUniqueNameEachMachine();

				var user = new LoginUser (){ login_id = name, password = password, device_id = device_id};
				using (HttpResponseMessage response = await wrapper.PostAsJsonAsync (user).ConfigureAwait (false)) {
					// cookie取得
					var headers = response.Headers;
					factory.AddCookies(CookieUtils.GetCookiesFromResponseHeaders (GetLoginURL(), headers));
					

					// endpointの取得
					var result = DynamicJson.Parse (await wrapper.ReadAsStringAsync (response.Content).ConfigureAwait (false));
					var endpoint = new EndPoint (result.endpoint);

					//広告用の画像のurl設定
					string[] images = result.ad_images;
					endpoint.ConfigureAdImages (images); //xxx: bad-code

					return endpoint;
				}
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
				return new AuthInfo (result);
			}
		}

        public async virtual Task<ResultTuple<string, AuthInfo>> AuthAsync(string name, string password)
        {
            EndPoint endpoint;
            try
            {
                try
                {
                    endpoint = await TryLoginRequest(name, password);
                }
                catch (System.Xml.XmlException e)
                {
                    logger.ErrorException("xml:", e);
                    return OnFailure();
                }
                try
                {
                    var statusData = await TryLoginStatusRequest(endpoint.LoginStatus);
                    if (statusData.login)
                    {
                        return OnSuccess(endpoint, statusData);
                    }
                    else
                    {
                        //TODO:log LoginStatusFailure
                        return OnFailure();
                    }
                }
                catch (System.Xml.XmlException e)
                {
                    logger.ErrorException("xml:", e);
                    return OnFailure(e.ToString());

                }
            }
            catch (System.Net.WebException e)
            {
                logger.ErrorException("net:", e);
                return OnFailure(Resource.GetWebExceptionMessage());
            }
            catch (System.Net.Sockets.SocketException e)
            {
                logger.ErrorException("net(socket):", e);
                return OnFailure(Resource.GetWebExceptionMessage());
            }
            catch (System.Net.Http.HttpRequestException e)
            {
                logger.ErrorException("httprequest", e);
                return OnFailure(Resource.GetWebExceptionMessage());
            }

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

