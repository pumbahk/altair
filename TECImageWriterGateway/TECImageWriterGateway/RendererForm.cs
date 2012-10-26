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
    public delegate void RendererCallback(Image image);

    public partial class RendererForm : Form
    {
        class RenderRequest
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

            public RenderRequest(Uri url, RendererCallback callback)
            {
                this.url = url;
                this.callback = callback;
            }
        }

        private BlockingQueue<RenderRequest> queue = new BlockingQueue<RenderRequest>();
        private Thread worker;
        private RenderRequest currentRequest;
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
                Invoke(new MethodInvoker(delegate()
                {
                    RenderRequest currentRequest = this.currentRequest;
                    Monitor.Enter(currentRequest);
                    try
                    {
                        Monitor.Pulse(currentRequest);
                    }
                    finally
                    {
                        Monitor.Exit(currentRequest);
                    }
                    currentRequest.Callback(args.Image);
                }));
            };
            poller.Start();
        }

        private void RendererForm_Load(object sender, EventArgs e)
        {
            worker = new Thread(
                delegate()
                {
                    while (queue != null)
                    {
                        RenderRequest currentRequest = queue.Poll(1000);
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
                                        t.Elapsed += delegate(object src, System.Timers.ElapsedEventArgs args)
                                        {
                                            t.Stop();
                                            t.Dispose();
                                            webBrowser1.Invoke(new MethodInvoker(
                                                delegate() {
                                                    webBrowser1.Print();
                                                }));
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
            queue.Enqueue(new RenderRequest(url, callback));
        }

        private void RendererForm_FormClosed(object sender, FormClosedEventArgs e)
        {
            poller.Stop();
            queue = null;
        }
    }
}