using System;
using System.Runtime.Serialization;

/* {"login": True,
	"loginuser": {"type": u"login",
		"id": unicode(operator.id),
		"name": operator.name},
	"organization": {"id": operator.organization_id}}
*/

namespace QR
{
	[DataContract]
	public class AuthInfo
	{
		[DataMember]
		internal bool login;
		[DataMember]
		internal string loginname;
		[DataMember]
		internal string secret;
		[DataMember]
		internal string organization_id;

		public AuthInfo (dynamic json)
		{
			login = json.login;
			loginname = json.loginuser.name;
			organization_id = json.organization.id;		
		}
	}
	//なんか付加するような操作が必要;
}

