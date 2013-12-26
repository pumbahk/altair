using System;

namespace QR
{
	public class Application
	{
		public Application ()
		{
			var config = new Configurator (new Resource (true));

			if (config.Verify ()) {
				throw new InvalidProgramException ("configuration is not end");
			}
		}
	}
}

