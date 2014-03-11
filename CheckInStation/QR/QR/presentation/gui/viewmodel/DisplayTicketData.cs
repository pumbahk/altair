using QR.presentation.gui;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace QR.presentation.gui.viewmodel
{
    public class DisplayTicketData : ViewModel
    {
        public DisplayTicketData()
        {
            this.coreData = new TicketDataMinumum();
            this.Today = DateTime.Today;
            //for designer preview
        }

        public DisplayTicketData(TicketDataMinumum tdata)
        {
            this.Today = DateTime.Today;
            this.coreData = tdata;
            this.ProductName = tdata.product.name;
            this.SeatName = tdata.seat.name;
            this.PrintedAt = tdata.printed_at; //null?
            this.TokenId = tdata.ordered_product_item_token_id;
        }

        private readonly TicketDataMinumum coreData;
        public DateTime Today { get; set; }
        public string ProductName { get; set; }
        public string SeatName { get; set; }
        public bool IsSelected
        {
            get { return this.coreData.is_selected; }
            set { this.coreData.is_selected = value; this.OnPropertyChanged("IsSelected"); }
        }
        public string TokenId { get; set; }
        public string PrintedAt { get; set; }
    }

    public class DisplayTicketDataCollection : ObservableCollection<DisplayTicketData>
    {
        public DisplayTicketDataCollection() { }
    }

    /// <summary>
    /// dummy for d:DataContext
    /// </summary>
    public class DisplayTicketDataContext
    {
        public DisplayTicketDataCollection DisplayTicketDataCollection { get; set; }
        public string Description { get; set; }

        public string Orderno { get; set; }
        public string CustomerName { get; set; }
        public string PerformanceDate { get; set; }
        public string PerformanceName { get; set; }
        public int NumberOfPrintableTicket { get; set; }

    }
}
