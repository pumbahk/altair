using System;

namespace QR
{
	public interface IConfigrator
	{
		void include (Action<IConfigrator> c);
	}
}

