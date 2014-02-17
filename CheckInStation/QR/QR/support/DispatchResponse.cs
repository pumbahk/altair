using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using QR.message;
using NLog;

namespace QR.support
{
    public class DispatchResponse<T>
    {
        private static Logger logger = LogManager.GetCurrentClassLogger ();

        public readonly IResource Resource;
        

        public DispatchResponse(IResource resource)
        {
            this.Resource = resource;
        }

        public async Task<ResultTuple<string, T>> Dispatch(Func<Task<ResultTuple<string,T>>> fn){
            try{
                return await fn().ConfigureAwait(false);
            }          
            catch (System.Net.WebException e)
            {
                logger.ErrorException("net:", e);
                return new Failure<string, T>(Resource.GetWebExceptionMessage());
            }
            catch (System.Net.Sockets.SocketException e)
            {
                logger.ErrorException("net(socket):", e);
                return new Failure<string, T>(Resource.GetWebExceptionMessage());
            }
            catch (System.Net.Http.HttpRequestException e)
            {
                logger.ErrorException("httprequest", e);
                return new Failure<string, T>(Resource.GetWebExceptionMessage());
            }
           catch (System.Xml.XmlException e)
            {
                logger.ErrorException("xml:", e);
                return new Failure<string, T>(e.ToString());
           }
        }

        public async Task<ResultTuple<string, T>> Dispatch(Func<Task<T>> fn)
        {
            try{
                return new Success<string,T>(await fn().ConfigureAwait(false));
                        }
            catch (System.Net.WebException e)
            {
                logger.ErrorException("net:", e);
                return new Failure<string, T>(Resource.GetWebExceptionMessage());
            }
            catch (System.Net.Sockets.SocketException e)
            {
                logger.ErrorException("net(socket):", e);
                return new Failure<string, T>(Resource.GetWebExceptionMessage());
            }
            catch (System.Net.Http.HttpRequestException e)
            {
                logger.ErrorException("httprequest", e);
                return new Failure<string, T>(Resource.GetWebExceptionMessage());
            }
           catch (System.Xml.XmlException e)
            {
                logger.ErrorException("xml:", e);
                return new Failure<string, T>(e.ToString());
           }
        }
    }
}
