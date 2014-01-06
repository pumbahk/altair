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
		[DataMember]
		internal string QRFetchData;

		public static string asURL (string url)
		{
			new Uri (url); //slackoff validation
			return url;
		}

		public EndPoint (dynamic json)
		{
			this.LoginStatus = EndPoint.asURL (json.login_status);
			this.QRFetchData = EndPoint.asURL (json.qr_ticketdata);
		}
	}
}

