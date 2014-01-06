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

		public override bool Verify ()
		{
			Task<ResultTuple<string, AuthInfo>> t = Resource.Authentication.AuthAsync (Resource, LoginName, LoginPassword);
			try {
				t.Wait (); //TODO:xxxx:
			} catch (AggregateException ex) {
				PresentationChanel.NotifyFlushMessage (ex.ToString ());
				PresentationChanel.NotifyFlushMessage (MessageResourceUtil.GetTaskCancelMessage (Resource));
				return false;
			}
			if (t.Result.Status) {
				Resource.AuthInfo = t.Result.Right;
				return true;
			} else {
				//modelからpresentation層へのメッセージ
				PresentationChanel.NotifyFlushMessage ((t.Result as Failure<string,AuthInfo>).Result);

				//TODO:こちらを削除
				NotifyValidationFailure (t.Result as Failure<string ,AuthInfo>);
				return false;
			}
		}

		public void NotifyValidationFailure (Failure<string, AuthInfo> failure)
		{
			if (PresentationChanel == null) {
				//TODO:logなりメッセージ
			} else {
				//TODO:fix. bad code
				(PresentationChanel as AuthenticationEvent).AuthenticationFailure (failure.Result);
			}
		}

		public override ICase OnSuccess (IFlow flow)
		{
			return new CaseEventSelect (Resource);
		}

		public override ICase OnFailure (IFlow flow)
		{
			return new CaseAuthInput (Resource);
		}
	}
}
