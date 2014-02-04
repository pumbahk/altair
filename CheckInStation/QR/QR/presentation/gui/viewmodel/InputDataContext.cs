using NLog;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace QR.presentation.gui
{
    public enum DataContextProgress
    {
        waiting,
        runnig,
        finished
    }

    public class InputDataContext : ViewModel, INotifyPropertyChanged
    {
        public DataContextProgress Progress;
        public RequestBroker Broker { get; set; }
        private IInternalEvent _event;
        public IInternalEvent Event
        {
            get { logger.Debug("get event: parent={3} parent.id={0} value={1} value.id={2}", this.GetHashCode(), this._event, this._event.GetHashCode(), this); return this._event; }
            set { logger.Debug("set event: parent={3} parent.id={0} value={1} value.id={2}", this.GetHashCode(), value, value.GetHashCode(), this); this._event = value; }
        }
        //public IInternalEvent Event { get; set; }


        // 不要かもしれない
        private InternalEventStaus _submitStatus;
        public InternalEventStaus SubmitStatus
        {
            get { return this._submitStatus; }
            set
            {
                this._submitStatus = value;
                if(this._submitStatus==InternalEventStaus.failure){
                    this.OnPropertyChanged("IsSubmitNotSuccessYet");
                }
                this.OnPropertyChanged("SubmitStatus");
            }
        }
        public bool IsSubmitNotSuccessYet
        {
            get {
                return this._submitStatus != InternalEventStaus.success; 
            }
        }



        private string errorMessage;

        protected Logger logger = LogManager.GetCurrentClassLogger();

        public ICase Case
        {
            get
            {
                var case_ = this.Broker.FlowManager.Peek().Case;
                //logger.Debug(String.Format("Case: {0}", case_));
                return case_;  //なぜかこれを直接Bindingで呼び出したとき""が返るっぽい。
            }
        }

        public string Description
        {
            get {
                var result = this.Case.Description;
                logger.Debug("case:{0} description:{1}", this.Case, result);
                return result;
            }
        }

        public virtual void OnSubmit()
        {
           
        }

        public virtual async Task<ICase> SubmitAsync()
        {
            this.OnSubmit();
            logger.Debug("SubmitAsync this:{0}, Event:{1}, Case:{2}", this, this.Event, this.Case);
            var result = await this.Broker.SubmitAsync(this.Event).ConfigureAwait(false);
            this.SubmitStatus = this.Event.Status;
            //本当はOnPropertyChangeでCaseが変わり。そのOnProeprtyChangeでCaseNameが変わるのが良い。
            this.OnPropertyChanged("CaseName");
            this.OnPropertyChanged("Description");

            return result;
        }

        public virtual void OnBackward()
        {
        }

        public virtual async Task<ICase> BackwardAsync()
        {
            this.OnBackward();
            logger.Debug("BackwardAsync this:{0}, Event:{1}, Case:{2}", this, this.Event, this.Case);
            var result = await this.Broker.BackwardAsync().ConfigureAwait(false);
            this.OnPropertyChanged("CaseName");
            return result;
        }

        public virtual void OnVerify()
        {
        }

        public virtual async Task<bool> VerifyAsync()
        {
            this.OnVerify();
            logger.Debug("VerifyAsync this:{0}, Event:{1}, Case:{2}", this, this.Event, this.Case);
            var result = await this.Broker.VerifyAsync(this.Event).ConfigureAwait(false);
            this.SubmitStatus = this.Event.Status;
            return result;
        }

        public virtual void OnPrepare()
        {
        }

        public virtual async Task PrepareAsync()
        {
            this.OnPrepare();
            logger.Debug("PrepareAsync this:{0}, Event:{1}, Case:{2}", this, this.Event, this.Case);           
            await this.Broker.PrepareAsync(this.Event).ConfigureAwait(false);
        }


        public string CaseName { get { return this.Case.ToString(); } }
        public string ErrorMessage
        {
            get { return this.errorMessage == null ? "" : this.errorMessage; }
            set { this.errorMessage = value; this.OnPropertyChanged("ErrorMessage"); }
        }

        public void TreatErrorMessage()
        {
            var coll = new List<string>();
            this.Event.HandleEvent((string s) =>
            {
                coll.Add(s);
            });
            this.ErrorMessage = String.Join(Environment.NewLine, coll.ToArray<string>());
        }
    }
}
