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

		public string GetLoginFailureMessageFormat (IResource resource)
		{
			return resource.SettingValue ("message.auth.failure.format.0");
		}

		public async virtual Task<ResultTuple<string, AuthInfo>> authAsync (IResource resource, string name, string password)
		{
			IHttpWrapperFactory<HttpWrapper> factory = resource.HttpWrapperFactory;

			//TODO:resourceの不備のチェックもテストにしておきたい。
			using (var wrapper = factory.Create (GetLoginURL (resource))) {
				var user = new LoginUser (){ login_id = name, password = password };
				using (HttpResponseMessage response = await wrapper.PostAsJsonAsync (user).ConfigureAwait (false)) {
					// cookie取得
					var headers = response.Headers;
					var cookies = CookieUtils.GetCookiesFromResponseHeaders (headers);
					factory.AddCookies (cookies);

					using (var wrapper2 = factory.Create (GetLoginStatusURL (resource)))
					using (HttpResponseMessage dataResponse = await wrapper2.GetAsync ().ConfigureAwait (false)) {

						var statusData = await dataResponse.Content.ReadAsAsync<LoginStatusData> ();
						if (statusData.login) {
							return OnSuccess (resource, statusData);
						} else {
							return OnFailure (resource);
						}
					}
				}
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
			var message = string.Format (GetLoginFailureMessageFormat (resource));
			return new Failure<string,AuthInfo> (message);
		}
	}
}

