using System;
using System.IO;
using System.Collections.Generic;
using System.Threading.Tasks;
using NLog;
using System.Windows.Media.Imaging;
using checkin.core.support;

namespace checkin.core.models
{
    public enum CollectorState
    {
        starting,
        running,
        ending
    }

    public class ImageUtil
    {
        public static BitmapImage LoadImage(byte[] imageData)
        {
            if (imageData == null || imageData.Length == 0) return null;
            var image = new BitmapImage();
            using (var mem = new MemoryStream(imageData))
            {
                mem.Position = 0;
                image.BeginInit();
                image.CreateOptions = BitmapCreateOptions.PreservePixelFormat;
                image.CacheOption = BitmapCacheOption.OnLoad;
                image.UriSource = null;
                image.StreamSource = mem;
                image.EndInit();
            }
            image.Freeze();
            return image;
        }
    }

    public class AdImageCollector
    {
        private HashSet<string> urlSet;
        private List<BitmapImage> imageSet;
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
            this.imageSet = new List<BitmapImage> ();
            this.State = CollectorState.starting;
            this.imageCount = 0;
        }

        public async Task<byte[]> fetchImageAsync(string url)
        {
            /* TODO: get from cache
            var filepath = this.urlFromSavePath (url);
            if (File.Exists (filepath)) {
                File.Read
            }
            */
            logger.Info(String.Format("get ad image. url:{0}".WithMachineName(), url));
            var wrapper = Resource.HttpWrapperFactory.Create(url);
            var response = await wrapper.GetAsync().ConfigureAwait(false);
            response.EnsureSuccessStatusCodeExtend();
            return await response.Content.ReadAsByteArrayAsync().ConfigureAwait(false);
        }

        public void Add (BitmapImage data)
        {
            this.imageSet.Add (data);
        }
        public void Add (Byte[] data)
        {
            this.imageSet.Add(this.CreateImage(data));
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
                logger.Debug("image: Length={0}".WithMachineName(), img.Length);
                this.Add(this.CreateImage(img));
            }
            this.State = CollectorState.ending;
        }

        public BitmapImage CreateImage (Byte[] data){
            return ImageUtil.LoadImage(data);
        }

        public BitmapImage GetImage ()
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

