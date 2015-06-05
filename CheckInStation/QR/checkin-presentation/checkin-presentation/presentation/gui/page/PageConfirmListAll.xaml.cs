using NLog;
using checkin.presentation.gui.viewmodel;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;
using System.Security;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;
using checkin.core.events;
using checkin.core.models;

namespace checkin.presentation.gui.page
{

    class PageConfirmListAllDataContext : InputDataContext, IConfirmAllStatusInfo, INotifyPropertyChanged
    {
        public PageConfirmListAllDataContext(Page page) : base(page) { }

        private ConfirmAllStatus _Status;
        public ConfirmAllStatus Status
        {
            get { return this._Status; }
            set { this._Status = value; this.OnPropertyChanged("Status"); }
        }

        private int _PartOrAll;
        public int PartOrAll
        {
            get { return this._PartOrAll; }
            set { this._PartOrAll = value; this.OnPropertyChanged("PartOrAll"); }
        }

        private TicketDataCollection _TicketDataCollection;
        public TicketDataCollection TicketDataCollection
        {
            get { return this._TicketDataCollection; }
            set { this._TicketDataCollection = value; this.OnPropertyChanged("TicketDataCollection"); }
        }

        private TicketData _readTicketData;
        public TicketData ReadTicketData
        {
            get { return this._readTicketData; }
            set { this._readTicketData = value; this.OnPropertyChanged("ReadTicketData"); }
        }

        private string _PerformanceName;
        public string PerformanceName
        {
            get { return this._PerformanceName; }
            set { this._PerformanceName = value; this.OnPropertyChanged("PerformanceName"); }
        }

        private string _PerformanceDate;
        public string PerformanceDate
        {
            get { return this._PerformanceDate; }
            set { this._PerformanceDate = value; this.OnPropertyChanged("PerformanceDate"); }
        }

        private string _Orderno;
        public string Orderno
        {
            get { return this._Orderno; }
            set { this._Orderno = value; this.OnPropertyChanged("Orderno"); }
        }

        private string _CustomerName;
        public string CustomerName
        {
            get { return this._CustomerName; }
            set { this._CustomerName = value; this.OnPropertyChanged("CustomerName"); }
        }
        private int _NumberOfPrintableTicket;
        public int NumberOfPrintableTicket
        {
            get { return this._NumberOfPrintableTicket; }
            set { this._NumberOfPrintableTicket = value; this.OnPropertyChanged("NumberOfPrintableTicket"); }
        }

        public DisplayTicketDataCollection DisplayTicketDataCollection { get; set; }

        public override void OnSubmit()
        {
            var ev = this.Event as ConfirmAllEvent;
            base.OnSubmit();
        }

        private Visibility _notPrintVisibility;
        public Visibility NotPrintVisibility
        {
            get { return this._notPrintVisibility; }
            set { this._notPrintVisibility = value; this.OnPropertyChanged("NotPrintVisibility"); }
        }
        private Visibility _refreshModeVisibility;
        public Visibility RefreshModeVisibility
        {
            get { return this._refreshModeVisibility; }
            set { this._refreshModeVisibility = value; this.OnPropertyChanged("RefreshModeVisibility"); }
        }
    }


    /// <summary>
    /// Interaction logic for PageConfirmAll.xaml
    /// </summary>
    public partial class PageConfirmListAll : Page//, IDataContextHasCase
    {
        public PageConfirmListAll()
        {
            InitializeComponent();
            this.DataContext = this.CreateDataContext();
            this.BuildDisplayItems();
        }

        private InputDataContext CreateDataContext()
        {
            var broker = AppUtil.GetCurrentBroker();
            var ev = broker.GetInternalEvent() as ConfirmAllEvent;
            var numOfPrintableTicket = ev.StatusInfo.TicketDataCollection.collection.Where(o => o.is_selected).Count();
            var collection = ev.StatusInfo.TicketDataCollection.collection.Where(o => o.is_selected);
            ev.StatusInfo.TicketDataCollection.collection = collection.Cast<TicketDataMinumum>().ToArray();
            var ctx = new PageConfirmListAllDataContext(this)
            { 
                Broker = AppUtil.GetCurrentBroker(),
                NumberOfPrintableTicket = numOfPrintableTicket,
                TicketDataCollection = ev.StatusInfo.TicketDataCollection,
                DisplayTicketDataCollection = new DisplayTicketDataCollection()
            };
            ctx.Event = ev;
            return ctx;
        }

        private void BuildDisplayItems()
        {
            var ctx = this.DataContext as PageConfirmListAllDataContext;
            var displayColl = ctx.DisplayTicketDataCollection;
            var source = ctx.TicketDataCollection;
            var performance = source.additional.performance;
            ctx.PerformanceName = performance.name;
            ctx.PerformanceDate = performance.date;
            ctx.Orderno = source.additional.order.order_no;
            ctx.CustomerName = source.additional.user;
            foreach (var tdata in source.collection)
            {
                var dtdata = new DisplayTicketData(ctx, tdata);
                dtdata.IsSelected = true;
                displayColl.Add(dtdata);
            }
        }


        private async void OnLoaded(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as PageConfirmListAllDataContext;
            if (!AppUtil.GetCurrentResource().RefreshMode)
            {
                ctx.RefreshModeVisibility = Visibility.Hidden;
            }
        }

        private async void OnBackwardWithBoundContext(object sender, RoutedEventArgs e)
        {
            e.Handled = true;
            var ctx = this.DataContext as InputDataContext;
            var case_ = await ctx.BackwardAsync();
            AppUtil.GetNavigator().NavigateToMatchedPage(case_, this);
        }

        private void OnSubmitWithBoundContext(object sender, RoutedEventArgs e)
        {
            e.Handled = true;
            var broker = AppUtil.GetCurrentBroker();
            var case_ = broker.FlowManager.Peek().Case;
            AppUtil.GetNavigator().NavigateToMatchedPage(case_, this);
        }
 

        private void OnGotoWelcome(object sender, RoutedEventArgs e)
        {
            e.Handled = true;
            AppUtil.GotoWelcome(this);
        }

    }
}
