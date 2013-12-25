using System;

namespace QR
{
	public class QRCodeLoader :IDataLoader<string>
	{
		public string Result { get; set;}
		public QRCodeLoader ()
		{
		}
	}
}

