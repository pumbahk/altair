using System;
using System.IO;
using System.Net;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;

namespace checkin.core.web
{
    public class FakeHttpContent : HttpContent
    {
        public string Content { get; set; }

        public FakeHttpContent (string content)
        {
            Content = content;
        }

        protected async override Task SerializeToStreamAsync (Stream stream,
                                                              TransportContext context)
        {
            //byte[] byteArray00 = Encoding.ASCII.GetBytes (Content); //we need UTF-8 string, usually
            byte[] byteArray = Encoding.UTF8.GetBytes (Content); //without BOM 
            await stream.WriteAsync (byteArray, 0, byteArray.Length);
        }

        protected override bool TryComputeLength (out long length)
        {
            length = Content.Length;
            return true;
        }
    }
}

