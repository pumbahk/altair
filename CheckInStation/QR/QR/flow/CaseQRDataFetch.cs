using System;
using System.Threading.Tasks;
using QR.message;

namespace QR
{
	/// <summary>
	/// Case QR data fetch. QRからデータ取得中
	/// </summary>
	public class CaseQRDataFetch : AbstractCase, ICase
	{
		public string QRCode { get; set; }

		public TicketData TicketData { get; set; }

		public CaseQRDataFetch (IResource resource, string qrcode) : base (resource)
		{
			QRCode = qrcode;
		}

		public override async Task<bool> VerifyAsync ()
		{
			return await Resource.QRCodeVerifier.VerifyAsync (QRCode);
		}

		public override ICase OnSuccess (IFlow flow)
		{
			return new CaseQRConfirmForOne (Resource);
		}
	}
}

