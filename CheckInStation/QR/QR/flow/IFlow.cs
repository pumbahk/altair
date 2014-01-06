using System;
using System.Threading.Tasks;

namespace QR
{
	public interface IFlow
	{
		Task<IFlow> Forward ();
		//TODO:implement
		Task<IFlow> Backward ();
		//TODO:implement
		void Finish();
		ICase Case { get; set;}
		IFlowDefinition GetFlowDefinition();
	}
}

