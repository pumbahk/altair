using System;
using System.Collections.Generic;
using System.Net;

namespace QR
{
	public interface IHttpWrapperFactory<T>
		where T: IHttpWrapper
	{
		T Create (IUrlBuilder builder);
		T Create (String url);

		void AddCookies(IEnumerable<Cookie> cookies);
        void AddCookies(CookieContainer container);
		void ClearCookies();
	}
}

