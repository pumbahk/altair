using System;
using System.Windows.Forms;
using System.Collections.Generic;
using System.Text;
using System.Net;
using System.IO;
using System.Threading;
using System.Text.RegularExpressions;
using System.Drawing;
using System.Drawing.Imaging;

namespace TECImageWriterGateway
{
    class Server
    {
        static MIMER.IPattern compositeMIPattern = new MIMER.RFC2045.Pattern.CompositeTypePattern();
        static MIMER.IPattern parameterPattern = new MIMER.RFC2045.Pattern.ParameterPattern();
        HttpListener listener;
        RendererForm renderer;
        Thread uiThread;
        Thread netThread;

        static DirectoryInfo CreateTemporaryDirectory()
        {
            string tempDir = Path.GetTempPath();
            DirectoryInfo retval = null;
            for (; ; )
            {
                string path = Path.Combine(tempDir, Path.GetRandomFileName());
                try
                {
                    retval = Directory.CreateDirectory(path);
                    break;
                }
                catch (IOException e)
                {
                    if (e is PathTooLongException || e is DirectoryNotFoundException)
                        throw;
                }
            }
            return retval;
        }

        static void RemoveAll(FileSystemInfo info)
        {
            if (info is FileInfo)
            {
                info.Delete();
            }
            else
            {
                DirectoryInfo _info = info as DirectoryInfo;
                foreach (FileInfo item in _info.GetFiles())
                {
                    RemoveAll(item);
                }
                foreach (DirectoryInfo item in _info.GetDirectories())
                {
                    RemoveAll(item);
                }
            }
        }

        class BadRequest : Exception { }

        static void SendBadRequest(HttpListenerResponse resp)
        {
            resp.StatusCode = 400;
            resp.StatusDescription = "Bad Request";
            StreamWriter writer = new StreamWriter(resp.OutputStream);
            writer.WriteLine("Bad Request");
            writer.Close();
        }

        static void SendInternalServerError(HttpListenerResponse resp)
        {
            resp.StatusCode = 500;
            resp.StatusDescription = "Internal Server Error";
            StreamWriter writer = new StreamWriter(resp.OutputStream);
            writer.WriteLine("Internal Server Error");
            writer.Close();
        }

        static MIMER.RFC2045.ContentTypeField ParseContentTypeField(string fieldValue)
        {
            IList<MIMER.RFC822.Field> fields = new List<MIMER.RFC822.Field>();
            new MIMER.RFC2045.ContentTypeFieldParser(new MIMER.RFC822.FieldParser()).Parse(fields, "Content-Type: " + fieldValue);
            return (MIMER.RFC2045.ContentTypeField)fields[fields.Count - 1];
        }

        class NullEndCriteria: MIMER.IEndCriteriaStrategy
        {
            public bool IsEndReached(char[] data, int size)
            {
                return false;   
            }
        }

        Dictionary<string, MIMER.RFC2045.IEntity> ParseMultipart(Stream stream, string boundary)
        {
            Dictionary<string, MIMER.RFC2045.IEntity> retval = new Dictionary<string, MIMER.RFC2045.IEntity>();
            MIMER.RFC2045.MultipartEntity ety = new MIMER.RFC2045.MultipartEntity();
            ety.Delimiter = boundary;
            new MIMER.RFC2045.MailReader().ReadCompositeEntity(
                stream, ety, new NullEndCriteria()
            );
            foreach (MIMER.RFC2045.IEntity part in ety.BodyParts)
            {
                MIMER.RFC2183.ContentDispositionField contentDisposition = null;
                foreach (MIMER.RFC822.Field field in part.Fields)
                {
                    if (field is MIMER.RFC2183.ContentDispositionField)
                    {
                        contentDisposition = field as MIMER.RFC2183.ContentDispositionField;
                    }
                }
                if (contentDisposition == null)
                    throw new BadRequest();
                if (contentDisposition.Disposition != "form-data")
                    throw new BadRequest();
                if (contentDisposition.Parameters["name"] == null)
                    throw new BadRequest();
                retval[contentDisposition.Parameters["name"]] = part;
            }
            return retval;
        }

        void HandleRequest(IAsyncResult result)
        {
            try
            {
                HttpListenerContext ctx = listener.EndGetContext(result);
                HttpListenerRequest req = ctx.Request;
                HttpListenerResponse resp = ctx.Response;

                try
                {
                    if (req.HttpMethod.ToUpper() != "POST")
                    {
                        throw new BadRequest();
                    }

                    MIMER.RFC2045.ContentTypeField contentType = req.ContentType == null ? null : ParseContentTypeField(req.ContentType);
                    if (contentType == null || contentType.Type != "multipart" || contentType.SubType != "form-data")
                    {
                        throw new BadRequest();
                    }
                    string boundary = contentType.Parameters["boundary"];
                    if (boundary == null)
                    {
                        throw new BadRequest();
                    }
                    Dictionary<string, MIMER.RFC2045.IEntity> data = ParseMultipart(req.InputStream, boundary);
                    MIMER.RFC2045.IEntity template = data["template"], ptct = data["ptct"];
                    if (template == null || ptct == null)
                        throw new BadRequest();
                    DirectoryInfo tempDir = CreateTemporaryDirectory();
                    try
                    {
                        string templateFile = Path.Combine(tempDir.FullName, "template.html");
                        File.WriteAllBytes(templateFile, template.Body);
                        File.WriteAllBytes(Path.Combine(tempDir.FullName, "ptct.xml"), ptct.Body);
                        Image resultingImage = null;
                        RendererCallback callback = null;
                        callback = delegate(Image image)
                            {
                                resultingImage = image;
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
                        renderer.Render(new Uri(templateFile), callback);
                        Monitor.Enter(callback);
                        try
                        {
                            if (!Monitor.Wait(callback, 20000))
                            {
                                SendInternalServerError(resp);
                                return;
                            }
                            resp.StatusCode = 200;
                            resp.StatusDescription = "OK";
                            resp.ContentType = "image/png";
                            using (MemoryStream outStream = new MemoryStream())
                            {
                                resultingImage.Save(outStream, ImageFormat.Png);
                                resp.ContentLength64 = outStream.Length;
                                outStream.Flush();
                                byte[] buffer = outStream.GetBuffer();
                                resp.OutputStream.Write(buffer, 0, buffer.Length);
                            }
                        }
                        finally
                        {
                            Monitor.Exit(callback);
                        }
                    }
                    finally
                    {
                        RemoveAll(tempDir);
                    }
                }
                catch (BadRequest)
                {
                    SendBadRequest(resp);
                }
                catch (Exception e)
                {
                    Console.WriteLine(e);
                    SendInternalServerError(resp);
                }
                finally
                {
                    resp.Close();
                }
            }
            catch (HttpListenerException)
            {
            }
        }

        public void Start()
        {
            uiThread.Start();
            netThread.Start();
        }

        public void Stop()
        {
            listener.Stop();
            renderer.Invoke(new MethodInvoker(delegate() { renderer.Close(); }));
        }

        public void Wait()
        {
            try
            {
                netThread.Join();
            }
            catch (ThreadStateException)
            {
            }
            try
            {
                uiThread.Join();
            }
            catch (ThreadStateException)
            {
            }
        }

        public void Run()
        {
            Start();
            Wait();
        }

        public Server(string prefix)
        {
            renderer = new RendererForm();
            listener = new HttpListener();
            listener.Prefixes.Add(prefix);
            netThread = new Thread(
                delegate()
                {
                    listener.Start();
                    while (listener.IsListening)
                    {
                        IAsyncResult result = listener.BeginGetContext(HandleRequest, listener);
                        result.AsyncWaitHandle.WaitOne(1000);
                    }
                }
            );
            netThread.Name = "NetThread";
            uiThread = new Thread(
                delegate()
                {
                    Application.Run(renderer);
                }
            );
            uiThread.Name = "UIThread";
            uiThread.SetApartmentState(ApartmentState.STA);
        }
    }
}
