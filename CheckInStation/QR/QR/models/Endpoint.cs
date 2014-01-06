using System;
using System.Runtime.Serialization;


/* 本当は以下のことのチェックが必要
- 抜けている属性が無いか
- validな値か
*/

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

