using System;
using System.Configuration;

namespace QR
{
	public class Configurator : IConfigurator
	{
		public IResource Resource { get; set; }

		public Configurator (IResource resource)
		{
			Resource = resource;
		}

		public bool Verify()
		{
			if (Resource == null) {
				throw new InvalidOperationException ("Configurator.Resource is null");
			}
			return Resource.Verify ();
		}
		public void Include (Action<IConfigurator> includeFunction)
		{
			includeFunction (this);
		}

		public string AppSettingValue (String key)
		{
			return Resource.SettingValue (key);
		}
	}
}

