using System;
using System.IO;
using System.Collections.Generic;
using System.Threading.Tasks;
using NLog;

namespace QR
{
	public enum CollectorState
	{
		starting,
		running,
		ending
	}

	public class AdImageCollector
	{
		private HashSet<string> urlSet;
		private List<byte[]> imageSet;
		public int imageCount;

		public IResource Resource { get; set; }

		public CollectorState State { get; set; }

		private static Logger logger = LogManager.GetCurrentClassLogger ();

		public string urlFromSavePath (string url)
		{
			var dirname = Path.GetTempPath ();
			return Path.Combine (dirname, Path.GetFileName (url));
		}

		public AdImageCollector (IResource resource)
		{
			this.Resource = resource;

			this.urlSet = new HashSet<string> ();	
			this.imageSet = new List<byte[]> ();
			this.State = CollectorState.starting;
			this.imageCount = 0;
		}

		public async Task<byte[]> fetchImageAsync (string url)
		{
			/* TODO: get from cache
			var filepath = this.urlFromSavePath (url);
			if (File.Exists (filepath)) {
				File.Read
			}
			*/
			logger.Info (String.Format ("get ad image. url:{0}", url));
			var wrapper = Resource.HttpWrapperFactory.Create (url);
			using (var response = await wrapper.GetAsync ().ConfigureAwait (false)) {
				return await response.Content.ReadAsByteArrayAsync ().ConfigureAwait (false);
			}
		}

		public void Add (byte[] data)
		{
			this.imageSet.Add (data);
		}

		public async Task Run (IEnumerable<string>urls)
		{
			this.State = CollectorState.running;
			var tq = new List<Task<byte[]>> ();
			foreach (var url in urls) {
				if (!this.urlSet.Contains (url)) {
					this.urlSet.Add (url);
					tq.Add (this.fetchImageAsync (url));
				}
			}
			var images = await Task.WhenAll (tq);
			foreach (var img in images) {
//				Console.WriteLine (string.Format ("image:raw: {0}", img.Length));
				this.Add (img);
			}
			this.State = CollectorState.ending;
		}

		public byte[] GetImage ()
		{
			if (this.State != CollectorState.ending) {
				throw new InvalidOperationException ("fetching image is not ending.");
			}
			if (this.imageCount >= this.imageSet.Count) {
				this.imageCount = 0;
			} 
			var result = this.imageSet [this.imageCount];
			this.imageCount += 1;
			return result;
		}
	}
}

