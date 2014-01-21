using System;
using System.Threading.Tasks;

namespace QR
{
	public interface IFlow
	{
		Task<IFlow> Forward ();
		//TODO:implement
		Task<IFlow> Backward ();

        Task PrepareAsync();
        Task<bool> VerifyAsync();

		void Finish ();

		ICase Case { get; set; }

		IFlowDefinition GetFlowDefinition ();

		bool IsAutoForwarding ();
	}
}

