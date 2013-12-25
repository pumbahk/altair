using System;

namespace QR
{
	public class FakeAuthentication :IAuthentication
	{
		public string OrganizationId { get; set;}
		public FakeAuthentication (string organizationId)
		{
			OrganizationId = organizationId;
		}

		public AuthInfo auth(IResource resource, string name, string password)
		{
			return new AuthInfo (){
				loginname = name,
				organization_id = OrganizationId,
				secret = "*dummy*"
				};
		}
	}
}

