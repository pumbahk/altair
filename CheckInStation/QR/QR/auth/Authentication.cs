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

		public class LoginResponseData
		{
			public string message { get; set; }
			//ok,ng
		}

		public class _LoginUserData
		{
			public string type { get; set; }
			//TODO:ENUM{login,guest}
			public string id { get; set; }

			public string name { get; set; }
		}

		public class _OrganizationData
		{
			public string id { get; set; }
		}

		public class LoginStatusData
		{
			public bool login { get; set; }

			public _LoginUserData loginuser { get; set; }

			public _OrganizationData organization { get; set; }
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
			using (var wrapper = factory.Create (url))
			using (HttpResponseMessage dataResponse = await wrapper.GetAsync ().ConfigureAwait (false)) {
				var result = DynamicJson.Parse (await dataResponse.Content.ReadAsStringAsync ());
				return new AuthInfo (result);
			}
		}

		public async virtual Task<ResultTuple<string, AuthInfo>> AuthAsync (IResource resource, string name, string password)
		{
			try {
				var endpoint = await TryLoginRequest (resource, name, password);
				if (endpoint == null) {
					//TODO:log LoginFailure
					return OnFailure (resource);
				} else {
					resource.EndPoint = endpoint;
				}

				var statusData = await TryLoginStatusRequest (resource, endpoint.LoginStatus);
				if (statusData.login) {
					return OnSuccess (resource, statusData);
				} else {
					//TODO:log LoginStatusFailure
					return OnFailure (resource);
				}
			} catch (System.Net.WebException e) {
				//TODO:log
				// e.ToString()はうるさすぎ
				return	OnFailure (resource.GetWebExceptionMessage ());
			}
		}

		public virtual Success<string, AuthInfo> OnSuccess (IResource resource, AuthInfo statusData)
		{
			return new Success<string,AuthInfo>(statusData);
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

