using NLog;
using QR.presentation.gui.viewmodel;
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

namespace QR.presentation.gui.page
{
  
    class PageConfirmAllDataContext : InputDataContext, IConfirmAllStatusInfo, INotifyPropertyChanged
    {
        private ConfirmAllStatus _Status;
        public ConfirmAllStatus Status
        {
            get { return this._Status; }
            set { this._Status = value; this.OnPropertyChanged("Status"); }
        }

        private TicketDataCollection _TicketDataCollection;
        public TicketDataCollection TicketDataCollection
        {
            get { return this._TicketDataCollection; }
            set { this._TicketDataCollection = value;  this.OnPropertyChanged("TicketDataCollection"); }
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
    }


    /// <summary>
    /// Interaction logic for PageConfirmAll.xaml
    /// </summary>
    public partial class PageConfirmAll : Page//, IDataContextHasCase
    {
        private Logger logger = LogManager.GetCurrentClassLogger();

        public PageConfirmAll()
        {
            InitializeComponent();
            this.DataContext = this.CreateDataContext();
        }

        private InputDataContext CreateDataContext()
        {
            var ctx = new PageConfirmAllDataContext()
            {
                Broker = AppUtil.GetCurrentBroker(),
                Status = ConfirmAllStatus.starting,
                DisplayTicketDataCollection = new DisplayTicketDataCollection()
            };
            ctx.Event = new ConfirmAllEvent() { StatusInfo = ctx };
            ctx.PropertyChanged += Status_OnPrepared;
            return ctx;
        }

        private void Status_OnPrepared(object sender, PropertyChangedEventArgs e)
        {
            var ctx = sender as PageConfirmAllDataContext;
            if (e.PropertyName == "Status" && ctx.Status == ConfirmAllStatus.prepared)
            {
                ctx.Status = ConfirmAllStatus.requesting;
                //後の継続を同期的に待つ必要ないのでawaitしない
                if (ctx.TicketDataCollection != null)
                {
                    this.Dispatcher.InvokeAsync(this.BuildDisplayItems);
                }
                else
                {
                    this.Dispatcher.InvokeAsync(async () => {
                       var case_ = await ctx.SubmitAsync();
                       ctx.TreatErrorMessage();
                       AppUtil.GetNavigator().NavigateToMatchedPage(case_, this);
                    });
                }
            }
        }

        private void BuildDisplayItems()
        {
            var ctx = this.DataContext as PageConfirmAllDataContext;
            var displayColl = ctx.DisplayTicketDataCollection;
            var source = ctx.TicketDataCollection;
            var performance = source.additional.performance;
            ctx.PerformanceName = performance.name;
            ctx.PerformanceDate = performance.date;
            ctx.Orderno = source.additional.order.order_no;
            ctx.CustomerName = source.additional.user;
            ctx.NumberOfPrintableTicket = source.collection.Where(o => o.is_selected).Count();
            foreach (var tdata in source.collection)
            {
                var dtdata = new DisplayTicketData(tdata);
                dtdata.PropertyChanged += OnCountChangePrintableTicket;
                displayColl.Add(dtdata);
            }
        }

        void OnCountChangePrintableTicket(object sender, PropertyChangedEventArgs e)
        {
            if (e.PropertyName == "IsSelected")
            {
                var delta = (sender as DisplayTicketData).IsSelected? 1 : -1;
                this.Dispatcher.InvokeAsync(() => {
                    var ctx = this.DataContext as PageConfirmAllDataContext;
                    ctx.NumberOfPrintableTicket += delta;
                });
            }
        }

        private async void OnLoaded(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as PageConfirmAllDataContext;
            ctx.Description = "データを取得しています。少々お待ちください";
            await ctx.PrepareAsync();
            ctx.Description = ctx.Case.Description;
            var s = await ctx.VerifyAsync();
            if(!s){
                this.OnSubmitWithBoundContext(sender, e); //xxx:
            }
        }

        private async void OnSubmitWithBoundContext(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as InputDataContext;
            await ProgressSingletonAction.ExecuteWhenWaiting(ctx, async () =>
            {
                var case_ = await ctx.SubmitAsync();
                ctx.TreatErrorMessage();

                //unregister event
                foreach (var dc in (ctx as PageConfirmAllDataContext).DisplayTicketDataCollection)
                {
                    dc.PropertyChanged -= OnCountChangePrintableTicket;
                }
                AppUtil.GetNavigator().NavigateToMatchedPage(case_, this);
            });
        }

        private async void OnBackwardWithBoundContext(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as InputDataContext;
            await ProgressSingletonAction.ExecuteWhenWaiting(ctx, async () =>
            {
                var case_ = await ctx.BackwardAsync();
                ctx.TreatErrorMessage();

                //unregister event
                foreach (var dc in (ctx as PageConfirmAllDataContext).DisplayTicketDataCollection)
                {
                    dc.PropertyChanged -= OnCountChangePrintableTicket;
                }
                AppUtil.GetNavigator().NavigateToMatchedPage(case_, this);
            });
        }
    }
}
