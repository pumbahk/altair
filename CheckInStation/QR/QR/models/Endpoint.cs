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
		[DataMember]
		internal string QRSvgOne;
		[DataMember]
		internal string QRSvgAll;
		[DataMember]
		internal string ImageFromSvg;

		public static string asURL (string url)
		{
			new Uri (url); //slackoff validation
			return url;
		}

		public EndPoint (dynamic json)
		{
			this.LoginStatus = EndPoint.asURL (json.login_status);
			this.QRFetchData = EndPoint.asURL (json.qr_ticketdata);
			this.QRSvgOne = EndPoint.asURL (json.qr_svgsource_one);
			this.QRSvgAll = EndPoint.asURL (json.qr_svgsource_all);
			this.ImageFromSvg = EndPoint.asURL (json.image_from_svg);
		}
	}
}

