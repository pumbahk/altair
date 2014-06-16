using System;
using System.Net.Http;
using System.Threading;
using System.Threading.Tasks;

namespace checkin.core.web
{
    public class FakeHttpMessageHandler : HttpMessageHandler
    {
        private HttpResponseMessage response;

        public FakeHttpMessageHandler (HttpResponseMessage response)
        {
            this.response = response;
        }

        protected override Task<HttpResponseMessage>
        SendAsync (HttpRequestMessage request,
                   CancellationToken cancellationToken)
        {
            var responseTask =
                new TaskCompletionSource<HttpResponseMessage> ();
            responseTask.SetResult (response);

            return responseTask.Task;
        }
    }
}

