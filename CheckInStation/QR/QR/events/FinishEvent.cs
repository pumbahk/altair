﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace QR
{
    public enum FinishStatus{
        starting,
        requesting,
        saved,
        finished,
    }

    public interface IFinishStatusInfo
    {
        FinishStatus Status { get; set; }
    }

    class FinishEvent :AbstractEvent,IInternalEvent
    {
        public IFinishStatusInfo StatusInfo { get; set; }

        public void ChangeState(FinishStatus s)
        {
            this.StatusInfo.Status = s;
        }
    }
}
