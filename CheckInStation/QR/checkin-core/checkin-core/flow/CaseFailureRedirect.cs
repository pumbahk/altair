 using System;
using System.Threading.Tasks;
using checkin.core.message;
using NLog;
using checkin.core.support;
using checkin.core.models;
using checkin.core.events;

namespace checkin.core.flow
{
    /// <summary>
    /// Case failure redirect. エラー表示。 キャンセル済みなど予期しない状況の時にリダイレクトメッセージ表示する状況
    /// </summary>
    public class CaseFailureRedirect : AbstractCase, ICase, IAutoForwardingCase
    {
        private static Logger logger = LogManager.GetCurrentClassLogger ();

        public Func<Task> Modify { get; set; }

        private string _message;
        public string Message
        {
            get
            {
                var result = String.Format("{0} (マシン名:{2} 現在の時間: {1})", this._message, DateTime.Now.ToString("yyyy/M/d hh:mm:ss"), this.Resource.GetUniqueNameEachMachine());
                logger.Warn("error is occurred: `{0}`".WithMachineName(), result);
                return result;
            }
            set { this._message = value; }
        }

        public CaseFailureRedirect (IResource resource, string message) : base (resource)
        {
            this.Message = message;
        }

        public CaseFailureRedirect (IResource resource) : base (resource)
        {
            this.Message = resource.GetDefaultErrorMessage ();
        }

        public CaseFailureRedirect (IResource resource, Func<Task> modify) : base (resource)
        {
            this.Modify = modify;
            this.Message = resource.GetDefaultErrorMessage ();
        }

        public CaseFailureRedirect(IResource resource, Func<Task> modify, string message) : this(resource, message)
        {
            this.Modify = modify;
        }

        public override async Task PrepareAsync(IInternalEvent ev)
        {
            await base.PrepareAsync(ev).ConfigureAwait(false);
            var subject = ev as FailureEvent;
            subject.Message = this.Message;
        }

        public override async Task<bool> VerifyAsync ()
        {
            // message
            logger.Info("failure message {0}".WithMachineName(), this.Message);
            if (this.Modify != null) {
                await this.Modify ();
            }
            return true;
        }

        public override ICase OnSuccess (IFlow flow)
        {
            IFlowDefinition def = flow.GetFlowDefinition ();
            return def.AfterFailureRedirect (this.Resource);
        }
    }
}

