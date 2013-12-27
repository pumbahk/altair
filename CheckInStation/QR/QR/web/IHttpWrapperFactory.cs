using System;
using System.Collections.Generic;

namespace QR
{
	public interface IHttpWrapperFactory<T>
		where T: IHttpWrapper
	{
		T Create (IUrlBuilder builder);
		T Create (String url);

		void AddCookies(IEnumerable<string> cookies);
		void ClearCookies();
	}
}

