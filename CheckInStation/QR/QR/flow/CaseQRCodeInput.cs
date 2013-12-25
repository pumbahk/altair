using System;

namespace QR
{
	interface IFlow{
		IFlow OnSuccess();
	}

	public class CaseQRCodeInput
	{
		public Boolean IsVerified(){
		}
		public IFlow OnSuccess (){
		}
		public CaseQRCodeInput ()
		{
		}
	}

	public class CaseQRDataFetcher
	{

	}
}

