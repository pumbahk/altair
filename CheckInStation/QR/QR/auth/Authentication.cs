using System;
using System.Threading.Tasks;
using System.Net.Http;

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
			return resource.SettingValue ("endpoint.auth.login.url");
		}

		public string GetLoginStatusURL (IResource resource)
		{
			return resource.SettingValue ("endpoint.auth.login.status.url");
		}

		public async Task<bool> TryLoginRequest (IResource resource, string name, string password)
		{
			IHttpWrapperFactory<HttpWrapper> factory = resource.HttpWrapperFactory;
			using (var wrapper = factory.Create (GetLoginURL (resource))) {
				var user = new LoginUser (){ login_id = name, password = password };
				using (HttpResponseMessage response = await wrapper.PostAsJsonAsync (user).ConfigureAwait (false)) {
					// cookie取得
					var headers = response.Headers;
					var cookies = CookieUtils.GetCookiesFromResponseHeaders (headers);
					factory.AddCookies (cookies);
					return true;
				}
			}
		}

		public async Task<LoginStatusData> TryLoginStatusRequest (IResource resource)
		{
			IHttpWrapperFactory<HttpWrapper> factory = resource.HttpWrapperFactory;
			using (var wrapper = factory.Create (GetLoginStatusURL (resource)))
			using (HttpResponseMessage dataResponse = await wrapper.GetAsync ().ConfigureAwait (false)) {
				return await dataResponse.Content.ReadAsAsync<LoginStatusData> ();
			}
		}

		public async virtual Task<ResultTuple<string, AuthInfo>> AuthAsync (IResource resource, string name, string password)
		{
			try {
				if (!await TryLoginRequest (resource, name, password)) {
					//TODO:log LoginFailure
					return OnFailure (resource);
				}
				var statusData = await TryLoginStatusRequest (resource);
				if (statusData.login) {
					return OnSuccess (resource, statusData);
				} else {
					//TODO:log LoginStatusFailure
					return OnFailure (resource);
				}
			} catch (System.Net.WebException e) {
				//TODO:log
				// e.ToString()はうるさすぎ
				return	OnFailure (MessageResourceUtil.GetWebExceptionMessage(resource));
			}
		}

		public virtual Success<string, AuthInfo> OnSuccess (IResource resource, LoginStatusData statusData)
		{
			return new Success<string, AuthInfo> (new AuthInfo () {
				organization_id = statusData.organization.id,
				loginname = statusData.loginuser.name,
				secret = "*dummy*",
			});
		}

		public Failure<string, AuthInfo> OnFailure (IResource resource)
		{
			var message = string.Format (MessageResourceUtil.GetLoginFailureMessageFormat (resource));
			return new Failure<string,AuthInfo> (message);
		}

		public Failure<string, AuthInfo> OnFailure (string message)
		{
			return new Failure<string,AuthInfo> (message);
		}
	}
}

