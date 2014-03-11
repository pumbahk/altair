﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace QR
{
    public interface IConfirmOneStatusInfo {
        string PerformanceName {get; set;}
        string PerformanceDate {get; set;}

        string UserName {get; set;}

        string OrderNo {get; set;}
        string ProductName {get; set;}
        string SeatName {get; set;}
        string PrintedAt {get; set;}
    }

    public class ConfirmOneEvent : AbstractEvent,IInternalEvent
    {
        public IConfirmOneStatusInfo StatusInfo { get; set; }

        public PrintUnit PrintUnit { get; set; }
        public string PrintUnitString { get; set; }

        public void SetData(TicketData tdata)
        {
            var statusInfo = this.StatusInfo;
            statusInfo.PerformanceName = tdata.additional.performance.name;
            statusInfo.PerformanceDate = tdata.additional.performance.date;

            statusInfo.UserName = tdata.additional.user;
            statusInfo.OrderNo = tdata.additional.order.order_no;
            statusInfo.ProductName = tdata.product.name;
            statusInfo.SeatName = tdata.seat.name;
            statusInfo.PrintedAt = tdata.printed_at;
        }
    }
}
