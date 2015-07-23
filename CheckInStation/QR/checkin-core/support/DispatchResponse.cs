using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using checkin.core.message;
using checkin.core.models;
using NLog;
using System.Net;
using System.Text.RegularExpressions;
using checkin.core.support;

namespace checkin.core.support
{
    public class DispatchResponse<T>
    {
        private static Logger logger = LogManager.GetCurrentClassLogger ();

        public readonly IResource Resource;
        

        public DispatchResponse(IResource resource)
        {
            this.Resource = resource;
        }
        public static Regex ExcludeNumber= new Regex("[^0-9]");

        public async Task<ResultTuple<string, T>> Dispatch(Func<Task<ResultTuple<string,T>>> fn){
            try{
                return await fn().ConfigureAwait(false);
            }          
            catch (System.Net.WebException e)
            {
                logger.ErrorException("net:".WithMachineName(), e);
                return new Failure<string, T>(String.Format("{0} ({1})", Resource.GetWebExceptionMessage(), ((HttpWebResponse)(e.Response)).StatusCode));
            }
            catch (System.Net.Sockets.SocketException e)
            {
                logger.ErrorException("net(socket):".WithMachineName(), e);
                return new Failure<string, T>(String.Format("{0} (X{1})", Resource.GetWebExceptionMessage(), e.ErrorCode));
            }
            catch (System.Net.Http.HttpRequestException e)
            {
                logger.ErrorException("httprequest".WithMachineName(), e);
                return new Failure<string, T>(String.Format("{0} ({1})", Resource.GetWebExceptionMessage(), DispatchResponse<T>.ExcludeNumber.Replace(e.Message, "")));
            }
           catch (System.Xml.XmlException e)
            {
                logger.ErrorException("xml:".WithMachineName(), e);
                return new Failure<string, T>(String.Format("{0} (xxx)", Resource.GetWebExceptionMessage()));
           }
           catch (TaskCanceledException e)
            {
                logger.ErrorException("task cancel".WithMachineName(), e);
                return new Failure<string, T>(Resource.GetGuessTimeoutErrorMessage());
            }
            catch (TransparentMessageException e)
            {
                return new Failure<string, T>(e.Message);
            }
        }

        public async Task<ResultTuple<string, T>> Dispatch(Func<Task<T>> fn)
        {
            try
            {
                return new Success<string, T>(await fn().ConfigureAwait(false));
            }
            catch (System.Net.WebException e)
            {
                logger.ErrorException("net:".WithMachineName(), e);
                return new Failure<string, T>(String.Format("{0} ({1})", Resource.GetWebExceptionMessage(), ((HttpWebResponse)(e.Response)).StatusCode));
            }
            catch (System.Net.Sockets.SocketException e)
            {
                logger.ErrorException("net(socket):".WithMachineName(), e);
                return new Failure<string, T>(String.Format("{0} (X{1})", Resource.GetWebExceptionMessage(), e.ErrorCode));
            }
            catch (System.Net.Http.HttpRequestException e)
            {
                logger.ErrorException("httprequest".WithMachineName(), e);
                return new Failure<string, T>(String.Format("{0} ({1})", Resource.GetWebExceptionMessage(), DispatchResponse<T>.ExcludeNumber.Replace(e.Message, "")));
            }
            catch (System.Xml.XmlException e)
            {
                logger.ErrorException("xml:".WithMachineName(), e);
                return new Failure<string, T>(e.ToString());
            }
            catch (TaskCanceledException e)
            {
                logger.ErrorException("task cancel".WithMachineName(), e);
                return new Failure<string, T>(Resource.GetGuessTimeoutErrorMessage());
            }
            catch (TransparentMessageException e)
            {
                return new Failure<string, T>(e.Message);
            }
        }
    }
}
