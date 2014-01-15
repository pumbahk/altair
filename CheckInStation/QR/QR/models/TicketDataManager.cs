using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace QR
{
	public class TicketDataManager
	{
		public IResource Resource { get; set; }

		public TicketDataManager (IResource resource)
		{
			Resource = resource;
		}

		public Task<bool> UpdatePrintedAtAsync (IEnumerable<string> ids)
		{
			return Task.Run (() => {
				Console.WriteLine ("updated! {0}", ids.ToArray ());
				return true;
			});
		}
	}
}

