
namespace QR
{
	public class TrasparentUrlBuilder :IUrlBuilder
	{
		public string Url{ get; set; }

		public TrasparentUrlBuilder (string url)
		{
			Url = url;
		}

		public string Build ()
		{
			return Url;
		}
	}
}

