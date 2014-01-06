using System;
using System.Threading.Tasks;

namespace QR
{
	/// <summary>
	/// Caseの使われ方
	/// Case.configure(); if(Case.Verify()) then Case.OnSuccess() else Case.OnFailure();
	/// </summary>
	public interface ICase
	{
		IResource Resource{ get; set; }

		Task ConfigureAsync (IInternalEvent ev);

		Task ConfigureAsync ();

		ICase OnSuccess (IFlow flow);

		ICase OnFailure (IFlow flow);

		Task<bool> VerifyAsync ();
	}
}

