using System;
using System.Collections.Generic;

namespace checkin.core.models
{
    public class StatusResult <T>
    {
        public bool Status { get; set; }

        public IEnumerable<T> SuccessList { get; set; }

        public IEnumerable<T> FailureList { get; set; }
    }

    public class ResultStatusCollector<T>
    {
        protected bool status;
        protected HashSet<T> success_list;
        protected HashSet<T> failure_list;

        public ResultStatusCollector ()
        {
            this.status = true;
            this.success_list = new HashSet<T> ();
            this.failure_list = new HashSet<T> ();
        }

        public void Add (T id, bool status)
        {
            if (!this.failure_list.Contains (id)) {
                if (!status) {
                    this.failure_list.Add (id);
                    this.status = false;
                    if (this.success_list.Contains (id)) {
                        this.success_list.Remove (id);
                    }
                } else {
                    this.success_list.Add (id);
                }
            }
        }

        public void AddSuccess (T id)
        {
            this.Add (id, true);
        }

        public void AddFailure (T id)
        {
            this.Add (id, false);
        }

        public bool Status{ get { return this.status; } }

        public StatusResult<T> Result ()
        {
            return new StatusResult<T> () {
                Status = this.status,
                SuccessList = this.success_list,
                FailureList = this.failure_list
            };
        }
    }
}

