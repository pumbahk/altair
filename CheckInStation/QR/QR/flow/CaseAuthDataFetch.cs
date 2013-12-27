using System;
using System.Threading.Tasks;

namespace QR
{
	/// <summary>
	/// Case Auth data fetch. Authデータ取得中
	/// </summary>
	public class CaseAuthDataFetch : AbstractCase, ICase
	{
		public string LoginName { get; set; }

		public string LoginPassword { get; set; }

		public AuthenticationEvent PresentationChanel { get; set; }

		public CaseAuthDataFetch (IResource resource, string name, string password, AuthenticationEvent ev) : base (resource)
		{
			LoginName = name;
			LoginPassword = password;
			PresentationChanel = ev;
		}

		public override bool Verify ()
		{
			Task<ResultTuple<string, AuthInfo>> t = Resource.Authentication.AuthAsync (Resource, LoginName, LoginPassword);
			t.Wait (); //TODO:xxxx:
			if (t.Result.Status) {
				Resource.AuthInfo = t.Result.Right;
				return true;
			} else {
				//modelからpresentation層へのメッセージ
				NotifyValidationFailure (t.Result as Failure<string ,AuthInfo>);
				return false;
			}
		}

		public void NotifyValidationFailure (Failure<string, AuthInfo> failure)
		{
			if (PresentationChanel == null) {
				//TODO:logなりメッセージ
			} else {
				PresentationChanel.AuthenticationFailure (failure.Result);
			}
		}

		public override ICase OnSuccess (IFlow flow)
		{
			return new CaseEventSelect (Resource);
		}
	}
}
