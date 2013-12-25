using System;

namespace QR
{
	public interface IHttpWrapperFactory<T>
		where T: IHttpWrapper
	{
		T Create (IUrlBuilder builder);
		T Create (String url);
	}
}

