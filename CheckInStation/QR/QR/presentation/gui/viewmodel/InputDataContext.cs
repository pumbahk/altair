﻿using NLog;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace QR.presentation.gui
{
    public class InputDataContext : INotifyPropertyChanged
    {
        public event PropertyChangedEventHandler PropertyChanged;

        public RequestBroker Broker { get; set; }
        public IInternalEvent Event { get; set; }
        private string errorMessage;

        protected Logger logger = LogManager.GetCurrentClassLogger();

        protected virtual void OnPropertyChanged(string propName)
        {
            var handler = this.PropertyChanged;
            if (handler != null)
                handler(this, new PropertyChangedEventArgs(propName));
        }

        public ICase Case
        {
            get
            {
                var case_ = this.Broker.FlowManager.Peek().Case;
                logger.Debug(String.Format("Case: {0}", case_));
                return case_;  //なぜかこれを直接Bindingで呼び出したとき""が返るっぽい。
            }
        }

        public virtual void OnSubmit()
        {
        }

        public virtual async Task<ICase> SubmitAsync()
        {
            this.OnSubmit();
            var result = await this.Broker.Submit(this.Event).ConfigureAwait(false);
            this.OnPropertyChanged("CaseName");
            return result;
        }

        public virtual void OnVerify()
        {
        }

        public virtual async Task<bool> VerifyAsync()
        {
            this.OnVerify();
            var result = await this.Broker.VerifyAsync(this.Event).ConfigureAwait(false);
            return result;
        }

        public virtual void OnPrepare()
        {
        }

        public virtual async Task PrepareAsync()
        {
            this.OnPrepare();
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
            this.ErrorMessage = String.Join(",", coll.ToArray<string>());
        }
    }
}
