using System;

namespace QR
{
	public interface IFlow
	{
		IFlow Forward ();
		//TODO:implement
		IFlow Backward ();
		//TODO:implement
		void Finish();
	}
}

