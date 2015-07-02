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
using System.Diagnostics;
using Microsoft.Practices.EnterpriseLibrary.Logging;

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
                _info.Delete();
            }
        }

        class BadRequest : Exception
        {
            public BadRequest() : base() { }
            public BadRequest(string msg) : base(msg) { }
        }

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

        static void SendGatewayTimeout(HttpListenerResponse resp)
        {
            resp.StatusCode = 504;
            resp.StatusDescription = "Gateway Timeout";
            StreamWriter writer = new StreamWriter(resp.OutputStream);
            writer.WriteLine("Gateway Timeout");
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

        void LogRequest(HttpListenerRequest req)
        {
            Logger.Write(new LogEntry(
                String.Format("{0} {1} {2} {3}", req.HttpMethod, req.Url, req.UrlReferrer, req.UserAgent),
                "HttpRequest",
                4,
                0,
                TraceEventType.Transfer,
                req.HttpMethod + ":" + req.Url,
                null));
                
        }

        void HandleRequest(IAsyncResult result)
        {
            try
            {
                HttpListenerContext ctx = listener.EndGetContext(result);
                HttpListenerRequest req = ctx.Request;
                HttpListenerResponse resp = ctx.Response;

                LogRequest(req);

                try
                {
                    if (req.HttpMethod.ToUpper() != "POST")
                    {
                        throw new BadRequest("POST method required");
                    }

                    MIMER.RFC2045.ContentTypeField contentType = req.ContentType == null ? null : ParseContentTypeField(req.ContentType);
                    if (contentType == null || contentType.Type != "multipart" || contentType.SubType != "form-data")
                    {
                        throw new BadRequest("Content-Type is not multipart/form-data");
                    }
                    string boundary = contentType.Parameters["boundary"];
                    if (boundary == null)
                    {
                        throw new BadRequest("Content-Type header does not contain boundary parameter");
                    }
                    Dictionary<string, MIMER.RFC2045.IEntity> data = ParseMultipart(req.InputStream, boundary);
                    MIMER.RFC2045.IEntity template = data["template"], ptct = data["ptct"];
                    if (template == null || ptct == null)
                        throw new BadRequest("Request does not contain \"template\" and \"ptct\"");
                    DirectoryInfo tempDir = CreateTemporaryDirectory();
                    try
                    {
                        string templateFile = Path.Combine(tempDir.FullName, "template.html");
                        File.WriteAllBytes(templateFile, template.Body);
                        File.WriteAllBytes(Path.Combine(tempDir.FullName, "ptct.xml"), ptct.Body);
                        Image resultingImage = renderer.Render(new Uri(templateFile), new TimeSpan(0, 0, 20));
                        if (resultingImage == null)
                        {
                            throw new TimeoutException("Timeout");
                        }
                        resultingImage = ImageUtils.whiteAsAlpha(resultingImage as Bitmap);
                        resp.StatusCode = 200;
                        resp.StatusDescription = "OK";
                        resp.ContentType = "image/png";
                        using (MemoryStream outStream = new MemoryStream())
                        {
                            resultingImage.Save(outStream, ImageFormat.Png);
                            outStream.Flush();
                            resp.ContentLength64 = outStream.Length;
                            resp.OutputStream.Write(outStream.GetBuffer(), 0, (int)outStream.Length);
                        }
                    }
                    finally
                    {
                        RemoveAll(tempDir);
                    }
                }
                catch (BadRequest e)
                {
                    Logger.Write(e);
                    SendBadRequest(resp);
                }
                catch (TimeoutException e)
                {
                    Logger.Write(e);
                    SendGatewayTimeout(resp);
                }
                catch (Exception e)
                {
                    Logger.Write(e);
                    SendInternalServerError(resp);
                }
                finally
                {
                    resp.Close();
                }
            }
            catch (HttpListenerException e)
            {
                Logger.Write(e);
            }
            catch (Exception e)
            {
                Logger.Write(e);
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
            listener = new HttpListener();
            listener.Prefixes.Add(prefix);
            netThread = new Thread(
                delegate()
                {
                    listener.Start();
                    while (listener.IsListening)
                    {
                        IAsyncResult result = listener.BeginGetContext(HandleRequest, listener);
                        using (WaitHandle waitHandle = result.AsyncWaitHandle)
                        {
                            waitHandle.WaitOne();
                        }
                    }
                }
            );
            netThread.Name = "NetThread";
            uiThread = new Thread(
                delegate()
                {
                    renderer = new RendererForm();
                    Application.Run(renderer);
                }
            );
            uiThread.Name = "UIThread";
            uiThread.SetApartmentState(ApartmentState.STA);
        }
    }
}
