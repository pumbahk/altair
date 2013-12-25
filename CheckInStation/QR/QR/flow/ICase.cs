using System;

namespace QR
{
/// <summary>
/// Caseの使われ方
/// Case.configure(); if(Case.Verify()) then Case.OnSuccess() else Case.OnFailure();
/// </summary>
	public interface ICase
	{
		IResource Resource{ get; set; }
		void Configure();
		ICase OnSuccess (IFlow flow);
		ICase OnFailure (IFlow flow);
		bool Verify();
	}
}

