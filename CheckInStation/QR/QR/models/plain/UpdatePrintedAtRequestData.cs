using System;

namespace QR
{
	public class UpdatePrintedAtRequestData
	{
		public string[] token_id_list { get; set; }

		public string order_no{ get; set; }

		public string secret{ get; set; }

		public UpdatePrintedAtRequestData ()
		{
		}
	}
}

