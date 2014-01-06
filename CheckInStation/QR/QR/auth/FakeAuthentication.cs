using System;
using System.Threading.Tasks;

using QR.message;

namespace QR
{
	public class FakeAuthentication :Authentication, IAuthentication
	{
		public string OrganizationId { get; set; }

		public string ExpectedName { get; set; }

		public string ExpectedPassword { get; set; }

		public FakeAuthentication (string expectedName, string expectedPassowrd)
		{
			ExpectedName = expectedName;
			ExpectedPassword = expectedPassowrd;
		}

		public Success<string, AuthInfo> OnSuccess (IResource resource, string name, string password)
		{
			var authInfo = new AuthInfo () {
				loginname = name,
				organization_id = "1", //hmm
				secret = "*dummy*" //hmm
			};
			return new Success<string, AuthInfo>(authInfo);
		}

		public override Task<ResultTuple<string, AuthInfo>> AuthAsync (IResource resource, string name, string password)
		{
			if (!ExpectedName.Equals(name) || !ExpectedPassword.Equals(password)) {
				//Console.WriteLine ("{0} - {1}", name, password);
				//Console.WriteLine("{0} - {1}", ExpectedName, ExpectedPassword);
				return Task.Run<ResultTuple<string,AuthInfo>> (() => OnFailure (resource));
			}
			return Task.Run<ResultTuple<string,AuthInfo>> (() => OnSuccess (resource, name, password));
		}
	}
}

