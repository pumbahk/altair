using System;
using System.Threading.Tasks;

namespace QR
{
	public interface IFlow
	{
		Task<IFlow> Forward ();
		//TODO:implement
		Task<IFlow> Backward ();

		void Finish ();

		ICase Case { get; set; }

		IFlowDefinition GetFlowDefinition ();

		bool IsAutoForwarding ();
	}
}

