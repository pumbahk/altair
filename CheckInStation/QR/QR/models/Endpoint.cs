using System;
using System.Runtime.Serialization;

namespace QR
{
	[DataContract]
	public class EndPoint
	{
		[DataMember]
		internal string LoginStatus;
		public EndPoint(dynamic json)
		{
			this.LoginStatus = json.login_status;
		}
	}
}

