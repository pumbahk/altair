using System;
using System.Collections.Generic;

namespace QR
{
	public class EmptyEvent :AbstractEvent, IInternalEvent
	{
		public override string GetMessageFormat ()
		{
			return "empty: message: {0}";
		}

		public EmptyEvent () : base ()
		{
		}
	}
}

