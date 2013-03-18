using System;
using System.Collections.Generic;
using System.Text;
using System.Drawing;
using System.Threading;
using System.IO;
using System.Runtime.CompilerServices;

namespace TECImageWriterGateway
{
    class TECImageWriterPollerImageAvailableEventArgs: EventArgs
    {
        Image image;

        public TECImageWriterPollerImageAvailableEventArgs(Image image)
        {
            this.image = image;
        }

        public Image Image
        {
            get { return image; }
        }
    }

    class TECImageWriterPoller: IDisposable
    {
        private bool watcherIsRunning;
        private Thread watcher;
        private string imagePath;
        private long lastUpdated;
        private TimeSpan checkInterval;

        public string ImagePath
        {
            get { return imagePath; }
            private set
            {
                this.imagePath = value;
                this.lastUpdated = GetLastUpdated();
            }
        }

        public TimeSpan CheckInterval
        {
            get { return checkInterval; }
        }

        public EventHandler<TECImageWriterPollerImageAvailableEventArgs> ImageAvailable;

        public TECImageWriterPoller(): this(System.Environment.SystemDirectory + "\\TECIMAGE\\image.bmp")
        {
        }

        public TECImageWriterPoller(string imagePath): this(imagePath, new TimeSpan(0, 0, 1))
        {
        }

        public TECImageWriterPoller(string imagePath, TimeSpan checkInterval)
        {
            ImagePath = imagePath;
            this.checkInterval = checkInterval;
        }

        private long GetLastUpdated()
        {
            FileInfo fi = new FileInfo(ImagePath);
            try
            {
                return fi.LastWriteTime.ToBinary();
            }
            catch (IOException)
            {
            }
            return 0;
        }

        [MethodImpl(MethodImplOptions.Synchronized) ]
        public void Start()
        {
            watcherIsRunning = true;
            watcher = new Thread(
                delegate()
                {
                    while (watcherIsRunning)
                    {
                        long timestamp = GetLastUpdated();
                        if (timestamp != 0 && (lastUpdated == 0 || timestamp > lastUpdated))
                        {
                            Bitmap image = new Bitmap(imagePath);
                            image.RotateFlip(RotateFlipType.Rotate270FlipNone);
                            ImageAvailable.Invoke(this, new TECImageWriterPollerImageAvailableEventArgs(image));
                            lastUpdated = timestamp;
                        }
                        Thread.Sleep(checkInterval);
                    }
                    Monitor.Enter(watcher);
                    try
                    {
                        Monitor.Pulse(watcher);
                    }
                    finally
                    {
                        Monitor.Exit(watcher);
                    }
                }
            );
            watcher.Start();
        }

        [MethodImpl(MethodImplOptions.Synchronized)]
        public void Stop()
        {
            if (watcherIsRunning && watcher != null)
            {
                watcherIsRunning = false;
                Monitor.Enter(watcher);
                try
                {
                    Monitor.Wait(watcher);
                }
                finally
                {
                    Monitor.Exit(watcher);
                }
                watcher = null;
            }
        }

        public void Dispose()
        {
            Stop();
        }
    }
}
