using System;
using System.Collections.Generic;
using System.IO;
using System.Configuration;
using System.Net;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;

using System.Xml;
using System.Drawing.Printing;
using System.Printing;
using System.Windows.Xps;
using System.Windows.Documents;
using System.Windows.Controls;

using Newtonsoft.Json;

using AltairPrinting.Altair.Document;

namespace AltairPrinting
{
    public partial class App : Application
    {
        private MainWindow window;

        // forcePreviewがtrueなら、印刷せずに、XPSビュアーウィンドウを開く
        private Boolean forcePreview;

        private void Application_Startup(object sender, StartupEventArgs e)
        {
            forcePreview = false;

            window = new MainWindow();
            window.Show();

            StartServer();
        }

        public void Print(string msg)
        {
            var dispatcher = Application.Current.Dispatcher;
            dispatcher.Invoke(() => {
                window.console.Text += msg;
            });
        }

        public void PrintLine(string msg)
        {
            Print(msg + "\n");
        }

        private void PreviewTest(String xaml)
        {
            Job t = new Job(xaml);
            t.Build();

            PreviewWindow win = new PreviewWindow();
            win.viewer.Document = t.Document;
            win.Show();
        }

        private void PrintTest(String xaml)
        {
            Job t = new Job(xaml);
            t.PrinterName = "Microsoft XPS Document Writer";
            t.Build();

            var localPrintServer = new LocalPrintServer();
            PrintQueue printQueue = localPrintServer.GetPrintQueue(t.PrinterName);
            var xpsDocWriter = PrintQueue.CreateXpsDocumentWriter(printQueue);
            xpsDocWriter.Write(t.Document);

            Environment.Exit(0);
        }

        private void StartServer()
        {
            Queue<Job> queue = new Queue<Job>();

            Task.Factory.StartNew(() =>
            {
                while (true)
                {
                    Job t = null;
                    lock (queue)
                    {
                        if (0 < queue.Count)
                        {
                            t = queue.Dequeue();
                        }
                    }
                    if(t != null)
                    {
                        var dispatcher = Application.Current.Dispatcher;
                        dispatcher.Invoke(() =>
                        {
                            if (t.PrinterName == null || t.PrinterName == "" || forcePreview)
                            {
                                PrintLine("Previewing...");
                                PreviewWindow win = new PreviewWindow();
                                t.Build();
                                win.viewer.Document = t.Document;
                                win.Show();
                            }
                            else
                            {
                                PrintLine(string.Format("Printing to {0}", t.PrinterName));
                                var localPrintServer = new LocalPrintServer();
                                PrintQueue printQueue = localPrintServer.GetPrintQueue(t.PrinterName);

                                var xpsDocWriter = PrintQueue.CreateXpsDocumentWriter(printQueue);
                                t.Build();
                                xpsDocWriter.Write(t.Document);
                            }
                        });
                    }
                    Thread.Sleep(1000);
                }
            });

            var listener = new HttpListener();
            listener.Prefixes.Add("http://localhost:8081/");
            //listener.Prefixes.Add("http://127.0.0.1:8081/");

            try
            {
                listener.Start();
            }
            catch (HttpListenerException ex)
            {
                MessageBox.Show("ポートが利用できません. 管理者権限でnetshコマンドを実行してURL予約を追加してください.");
                Environment.Exit(-1);
            }

            PrintLine("Listening at http://localhost:8081/");
            Api api = new Api(Application.Current.Dispatcher);
            api.Print = Print;
            api.PrintLine = PrintLine;
            api.queue = queue;
            api.listener = listener;
            Task.Factory.StartNew(() => api.ProcessAsync());
        }
    }
}
