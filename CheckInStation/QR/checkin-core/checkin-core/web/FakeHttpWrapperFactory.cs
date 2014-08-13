using System;
using System.Net.Http;

namespace checkin.core.web
{
    public class FakeHttpWrapperFactory<T> : HttpWrapperFactory<T>, IHttpWrapperFactory<T>
        where T : IHttpWrapper, new()
    {
        public String MockContentString { get; set; }

        public FakeHttpWrapperFactory (String mockContentString) : base ()
        {
            MockContentString = mockContentString;
        }

        public override HttpClient CreateHttpClient ()
        {
            var responseMessage = new HttpResponseMessage ();
            responseMessage.Content = new FakeHttpContent (this.MockContentString);
            var messageHandler = new FakeHttpMessageHandler (responseMessage);

            var client = new HttpClient (messageHandler);
            return ClientAttachedSomething (client);
        }
    }
}