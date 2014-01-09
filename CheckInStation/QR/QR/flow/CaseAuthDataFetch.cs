using System;
using System.Threading.Tasks;
using QR.message;

namespace QR
{
	/// <summary>
	/// Case Auth data fetch. Authデータ取得中
	/// </summary>
	public class CaseAuthDataFetch : AbstractCase, ICase
	{
		public string LoginName { get; set; }

		public string LoginPassword { get; set; }

		public CaseAuthDataFetch (IResource resource, string name, string password) : base (resource)
		{
			LoginName = name;
			LoginPassword = password;
		}

		public override async Task<bool> VerifyAsync ()
		{
			try {
				ResultTuple<string, AuthInfo> result = await Resource.Authentication.AuthAsync (LoginName, LoginPassword);
				if (result.Status) {
					Resource.AuthInfo = result.Right;
					return true;
				} else {
					//modelからpresentation層へのメッセージ
					PresentationChanel.NotifyFlushMessage ((result as Failure<string,AuthInfo>).Result);
					return false;
				}
			} catch (Exception ex) {
				PresentationChanel.NotifyFlushMessage (ex.ToString ());
				PresentationChanel.NotifyFlushMessage (MessageResourceUtil.GetTaskCancelMessage (Resource));
				return false;
			}
		}

		public override ICase OnSuccess (IFlow flow)
		{
			return new CaseQRInputStrategySelect (Resource);
		}

		public override ICase OnFailure (IFlow flow)
		{
			return new CaseAuthInput (Resource);
		}
	}
}
