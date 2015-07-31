using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Threading.Tasks;

using System.Net;

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
    class Api
    {
        private System.Windows.Threading.Dispatcher dispatcher;

        public Action<string> Print;
        public Action<string> PrintLine;

        public HttpListener listener;
        public Queue<Job> queue;

        public Api(System.Windows.Threading.Dispatcher d)
        {
            dispatcher = d;
        }

        public async Task ProcessAsync()
        {
            // contextをとってきて（ちょっと時間がかかるかも）
            HttpListenerContext ctx = await listener.GetContextAsync();

            // 別スレッドでさらにlistenしなおす
            Task.Factory.StartNew(() => ProcessAsync());

            // contextを処理する
            Perform(ctx);

            /*
            await ProcessAsync();
             */
        }

        private void Perform(HttpListenerContext ctx)
        {
            Uri uri = ctx.Request.Url;
            PrintLine(string.Format("Requested {0} {1}", ctx.Request.HttpMethod, uri));

            List<string> allowOrigin = new List<string>();
            allowOrigin.Add("http://p-strain.jp");

            // レスポンスを返す準備
            HttpListenerResponse response = ctx.Response;
            response.Headers.Add("Access-Control-Allow-Origin: http://p-strain.jp");
            StringBuilder responseString = new StringBuilder();

            try
            {
                // JSONのリクエストをパース
                Request r = null;
                if (ctx.Request.HttpMethod == "POST")
                {
                    // POST JSONデータ
                    try
                    {
                        using (StreamReader sr = new StreamReader(ctx.Request.InputStream))
                        {
                            var serializer = new JsonSerializer();
                            r = serializer.Deserialize<Request>(new JsonTextReader(sr));
                        }
                    }
                    catch (Exception ex)
                    {
                        // 不正なJSONの場合は...

                        PrintLine(ex.Message);
                        PrintLine(ex.StackTrace.ToString());
                        return;
                    }
                }

                // Originチェック
                if (ctx.Request.Headers["Origin"] != null)
                {
                    if (!allowOrigin.Contains(ctx.Request.Headers["Origin"]))
                    {
                        // アクセス拒否
                        responseString.Append("Sorry");

                        return; // finallyは実行される
                    }
                }
                else
                {
                    // Originが無い場合
                    responseString.Append("Sorry!!");

                    return; // finallyは実行される
                }

                if (ctx.Request.HttpMethod == "OPTIONS")
                {
                    response.Headers.Add("Access-Control-Allow-Methods: GET,POST,OPTIONS");
                    response.Headers.Add("Access-Control-Allow-Headers: Content-Type");
                }
                else if (uri.PathAndQuery.StartsWith("/favicon"))
                {
                    // do nothing
                }
                else if (uri.Query == "?printer")
                {
                    List<string> printers = new List<string>();
                    dispatcher.Invoke(() =>
                    {
                        foreach (string n in PrinterSettings.InstalledPrinters)
                        {
                            printers.Add(n);
                        }
                    });

                    response.ContentType = "application/json";
                    responseString.Append(JsonConvert.SerializeObject(new
                    {
                        status = "success",
                        printers = printers
                    }));
                }
                else if(r.Xaml != null)
                {
                    string result = dispatcher.Invoke<string>(() =>
                    {
                        // メインのUIスレッドで...

                        // プリンタが使えるかの確認をする
                        if (r.Printer != "")
                        {
                            try
                            {
                                var localPrintServer = new LocalPrintServer();
                                var printQueue = localPrintServer.GetPrintQueue(r.Printer);
                            }
                            catch (PrintQueueException ex)
                            {
                                // FIXME: むしろエラーを返したほうが...
                                responseString.Append(string.Format("No such printer or not available: {0}", r.Printer));
                                return "error";
                            }
                        }

                        // データを作る
                        Job job = new Job(r.Xaml);
                        job.PrinterName = r.Printer;

                        // キューに登録
                        lock (queue)
                        {
                            queue.Enqueue(job);
                        }
                        return "success";
                    });

                    if (result == "success")
                    {
                        response.ContentType = "application/json";
                        responseString.Append(JsonConvert.SerializeObject(new
                        {
                            status = "success"
                        }));
                    }
                }
                else if (r.Printer != null && r.Printer != "")
                {
                    string result = dispatcher.Invoke<string>(() =>
                    {
                        // メインのUIスレッドで...
                        try
                        {
                            var localPrintServer = new LocalPrintServer();
                            var printQueue = localPrintServer.GetPrintQueue(r.Printer);

                            return JsonConvert.SerializeObject(new
                            {
                                status = "success",
                                printer = new
                                {
                                    busy = printQueue.IsBusy,
                                    in_error = printQueue.IsInError,
                                    offline = printQueue.IsOffline,
                                    no_paper = printQueue.IsOutOfPaper,
                                    paused = printQueue.IsPaused,
                                    jobs = printQueue.NumberOfJobs,
                                }
                            });
                        }
                        catch(PrintQueueException ex)
                        {
                            return JsonConvert.SerializeObject(new
                            {
                                status = "failure",
                                exception = ex.Message
                            });
                        }
                    });
                    response.ContentType = "application/json";
                    responseString.Append(result);
                }
                else
                {
                    // 想定外
                }
            }
            catch (Exception ex)
            {
                responseString.Append(ex.StackTrace.ToString());
            }
            finally
            {
                byte[] buffer = Encoding.UTF8.GetBytes(responseString.ToString());
                response.ContentLength64 = buffer.Length;
                Stream output = response.OutputStream;
                output.Write(buffer, 0, buffer.Length);
                output.Close();
            }
        }
    }
}
