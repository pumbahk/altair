using System;
using System.Threading.Tasks;
using System.Net.Http;
using QR.message;
using Codeplex.Data;

namespace QR
{
	public class Authentication :IAuthentication
	{
		public Authentication ()
		{
		}

		public class LoginUser
		{
			public string login_id { get; set; }

			public string password { get; set; }
		}
		// url
		public string GetLoginURL (IResource resource)
		{
			return resource.GetLoginURL ();
		}
		/*
		 * API Response
		 * 
		 * {endpoint: {"login_status": "http://foo"}}
		 */
		public async Task<EndPoint> TryLoginRequest (IResource resource, string name, string password)
		{
			IHttpWrapperFactory<HttpWrapper> factory = resource.HttpWrapperFactory;
			using (var wrapper = factory.Create (GetLoginURL (resource))) {
				var user = new LoginUser (){ login_id = name, password = password };
				using (HttpResponseMessage response = await wrapper.PostAsJsonAsync (user).ConfigureAwait (false)) {
					// cookie取得
					var headers = response.Headers;
					var cookies = CookieUtils.GetCookiesFromResponseHeaders (headers);
					factory.AddCookies (cookies);
					var result = DynamicJson.Parse (await response.Content.ReadAsStringAsync ().ConfigureAwait (false));
					return new EndPoint (result.endpoint);
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
		public async Task<AuthInfo> TryLoginStatusRequest (IResource resource, string url)
		{
			IHttpWrapperFactory<HttpWrapper> factory = resource.HttpWrapperFactory;
			using (var wrapper = factory.Create (url)) {
				var s = await wrapper.GetStringAsync ().ConfigureAwait (false);
				var result = DynamicJson.Parse (s);
				return new AuthInfo (result);
			}
		}

		public async virtual Task<ResultTuple<string, AuthInfo>> AuthAsync (IResource resource, string name, string password)
		{
			EndPoint endpoint;
			try {
				try {
					endpoint = await TryLoginRequest (resource, name, password);
				} catch (System.Xml.XmlException e) {
					return OnFailure (resource);
				}
				try {
					var statusData = await TryLoginStatusRequest (resource, endpoint.LoginStatus);
					if (statusData.login) {
						return OnSuccess (resource, endpoint, statusData);
					} else {
						//TODO:log LoginStatusFailure
						return OnFailure (resource);
					}
				} catch (System.Xml.XmlException e) {
					return OnFailure (e.ToString ());
				}
			} catch (System.Net.WebException e) {
				//TODO:log
				// e.ToString()はうるさすぎ
				return	OnFailure (resource.GetWebExceptionMessage ());
			}
		}

		public virtual Success<string, AuthInfo> OnSuccess (IResource resource, EndPoint endpoint, AuthInfo statusData)
		{
			resource.EndPoint = endpoint;
			return new Success<string,AuthInfo> (statusData);
		}

		public Failure<string, AuthInfo> OnFailure (IResource resource)
		{
			var message = string.Format (resource.GetLoginFailureMessageFormat ());
			return new Failure<string,AuthInfo> (message);
		}

		public Failure<string, AuthInfo> OnFailure (string message)
		{
			return new Failure<string,AuthInfo> (message);
		}
	}
}

