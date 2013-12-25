using System;
using System.Runtime.Serialization;

namespace QR
{
    [DataContract]
	public class QRSign
	{
		[DataMember]
		internal string qrcode;
		[DataMember]
		internal string region; //どこでe.g.(check in station 1)
	}
}

