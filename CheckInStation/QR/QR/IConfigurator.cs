using System;

namespace QR
{
	public interface IConfigurator
	{
		void Include (Action<IConfigurator> c);
		IResource Resource { get; set; }
	}
}

