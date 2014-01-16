using System;
using System.Runtime.Serialization;

namespace QR
{
	[DataContract]
	public class AdditionalData
	{
		[DataMember]
		internal string user;

		public AdditionalData (dynamic json)
		{
			this.user = json.user;
		}
	}
}

