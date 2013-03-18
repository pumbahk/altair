using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using System.Threading;

namespace TECImageWriterGateway
{
    public delegate void RendererCallback(RenderingResult result);

    public partial class RendererForm : Form
    {
        class RenderingRequest
        {
            Uri url;
            RendererCallback callback;

            public Uri Url
            {
                get { return url; }
            }

            public RendererCallback Callback
            {
                get { return callback; }
            }

            public RenderingRequest(Uri url, RendererCallback callback)
            {
                this.url = url;
                this.callback = callback;
            }
        }

        private BlockingQueue<RenderingRequest> queue = new BlockingQueue<RenderingRequest>();
        private Thread worker;
        private RenderingRequest currentRequest;
        private TimeSpan maximumRenderingTime;
        private TECImageWriterPoller poller = new TECImageWriterPoller();

        public TimeSpan MaximumRenderingTime
        {
            get { return maximumRenderingTime; }
        }

        public RendererForm(): this(new TimeSpan(0, 0, 8)) {}

        public RendererForm(TimeSpan maximumRenderingTime)
        {
            this.maximumRenderingTime = maximumRenderingTime;
            InitializeComponent();
            poller.ImageAvailable += delegate(object src, TECImageWriterPollerImageAvailableEventArgs args)
            {
                try
                {
                    Invoke(new MethodInvoker(delegate()
                    {
                        RenderingRequest currentRequest = this.currentRequest;
                        Monitor.Enter(currentRequest);
                        try
                        {
                            Monitor.Pulse(currentRequest);
                        }
                        finally
                        {
                            Monitor.Exit(currentRequest);
                        }
                        currentRequest.Callback(new RenderingResult(args.Image));
                    }));
                }
                catch (Exception e)
                {
                    currentRequest.Callback(new RenderingResult(e));
                }
            };
            poller.Start();
        }

        private void RendererForm_Load(object sender, EventArgs args)
        {
            worker = new Thread(
                delegate()
                {
                    while (queue != null)
                    {
                        RenderingRequest currentRequest = queue.Poll(1000);
                        if (currentRequest == null)
                            continue;
                        this.currentRequest = currentRequest;
                        webBrowser1.Invoke(new MethodInvoker(
                            delegate
                            {
                                webBrowser1.Navigate(currentRequest.Url);
                                WebBrowserDocumentCompletedEventHandler hdlr = null;
                                hdlr =
                                    delegate
                                    {
                                        webBrowser1.DocumentCompleted -= hdlr;
                                        System.Timers.Timer t = new System.Timers.Timer(maximumRenderingTime.TotalMilliseconds);
                                        t.Elapsed += delegate(object src, System.Timers.ElapsedEventArgs _args)
                                        {
                                            t.Stop();
                                            t.Dispose();
                                            try
                                            {
                                                webBrowser1.Invoke(new MethodInvoker(
                                                    delegate()
                                                    {
                                                        webBrowser1.Print();
                                                    }));
                                            }
                                            catch (Exception e)
                                            {
                                                currentRequest.Callback(new RenderingResult(e));
                                            }
                                        };
                                        t.Start();
                                    };
                                webBrowser1.DocumentCompleted += hdlr;
                            }
                        ));
                        Monitor.Enter(currentRequest);
                        try
                        {
                            Monitor.Wait(currentRequest);
                        }
                        finally
                        {
                            Monitor.Exit(currentRequest);
                        }
                    }
                }
            );
            worker.Start();
        }

        public void Render(System.Uri url, RendererCallback callback)
        {
            queue.Enqueue(new RenderingRequest(url, callback));
        }

        public Image Render(System.Uri url)
        {
            return Render(url, new TimeSpan());
        }

        public Image Render(System.Uri url, TimeSpan timeout)
        {
            RenderingResult result = null;
            RendererCallback callback = null;
            callback = delegate(RenderingResult _result)
            {
                result = _result;
                Monitor.Enter(callback);
                try
                {
                    Monitor.Pulse(callback);
                }
                finally
                {
                    Monitor.Exit(callback);
                }
            };
            Render(url, callback);
            Monitor.Enter(callback);
            try
            {
                if (timeout == new TimeSpan())
                {
                    Monitor.Wait(callback);
                }
                else
                {
                    if (!Monitor.Wait(callback, (int)timeout.TotalMilliseconds))
                        return null;
                }
            }
            finally
            {
                Monitor.Exit(callback);
            }
            if (result.Type == RenderingResultType.Fail)
                throw result.Exception;
            return result.Image;
        }

        private void RendererForm_FormClosed(object sender, FormClosedEventArgs e)
        {
            poller.Stop();
            queue = null;
        }
    }
}