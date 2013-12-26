using System;
using System.Threading.Tasks;

namespace QR
{
	public class Authentication :IAuthentication
	{
		public Authentication ()
		{
		}

		public async virtual Task<ResultTuple<string, AuthInfo>> authAsync (IResource resource, string name, string password)
		{
			throw new NotImplementedException ();
		}

		public virtual Success<string, AuthInfo> OnSuccess (IResource resource)
		{
			throw new NotImplementedException (); //TODO:implement;
		}

		public Failure<string, AuthInfo> OnFailure (IResource resource)
		{
			var fmt = resource.SettingValue ("message.auth.failure.format.0");
			var message = string.Format (fmt);
			return new Failure<string,AuthInfo> (message);
		}
	}
}

