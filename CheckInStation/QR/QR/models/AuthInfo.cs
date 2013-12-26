using System;
using System.Runtime.Serialization;

namespace QR
{
	[DataContract]
	public class AuthInfo
	{
		[DataMember]
		internal string loginname;
		[DataMember]
		internal string secret;
		[DataMember]
		internal string organization_id;
	}

	//なんか付加するような操作が必要;
}

