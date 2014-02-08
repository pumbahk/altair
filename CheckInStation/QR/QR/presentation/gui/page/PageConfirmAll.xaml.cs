using NLog;
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
    class DisplayTicketData : ViewModel
    {
        public DisplayTicketData(TicketDataMinumum tdata)
        {
            this.coreData = tdata;
            this.ProductName = tdata.product.name;
            this.SeatName = tdata.seat.name;
            this.PrintedAt = tdata.printed_at; //null?
            this.TokenId = tdata.ordered_product_item_token_id;
        }

		private readonly TicketDataMinumum coreData;
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

    class PageConfirmAllDataContext : InputDataContext, IConfirmAllStatusInfo, INotifyPropertyChanged
    {
        private ConfirmAllStatus _status;
        private TicketDataCollection _ticketDataCollection;
        private string _performanceName;
        private string _performanceDate;
        public ConfirmAllStatus Status
        {
            get { return this._status; }
            set { this._status = value; this.OnPropertyChanged("Status"); }
        }
        public TicketDataCollection TicketDataCollection
        {
            get { return this._ticketDataCollection; }
            set { this._ticketDataCollection = value;  this.OnPropertyChanged("TicketDataCollection"); }
        }
        public string PerformanceName
        {
            get { return this._performanceName; }
            set { this._performanceName = value; this.OnPropertyChanged("PerformanceName"); }
        }
        public string PerformanceDate
        {
            get { return this._performanceDate; }
            set { this._performanceDate = value; this.OnPropertyChanged("PerformanceDate"); }
        }

        public ObservableCollection<DisplayTicketData> DisplayTicketDataCollection { get; set; }

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
                DisplayTicketDataCollection = new ObservableCollection<DisplayTicketData>()
            };
            ctx.Event = new ConfirmAllEvent() { StatusInfo = ctx };
            ctx.PropertyChanged += Status_OnPrepared;
            return ctx;
        }

        private async void Status_OnPrepared(object sender, PropertyChangedEventArgs e)
        {
            var ctx = sender as PageConfirmAllDataContext;
            if (e.PropertyName == "Status" && ctx.Status == ConfirmAllStatus.prepared)
            {
                ctx.Status = ConfirmAllStatus.requesting;
                if (ctx.TicketDataCollection != null)
                {
                    this.Dispatcher.Invoke(this.BuildDisplayItems);
                }
                else
                {
                    //?G???[???o???????????????G???[???????J??
                    await this.Dispatcher.InvokeAsync(async () => {
                       var case_ = await ctx.SubmitAsync();
                       ctx.TreatErrorMessage();
                       AppUtil.GetNavigator().NavigateToMatchedPage(case_, this);
                    });
                }
            }
        }

        private void BuildDisplayItems()
        {
            var source = this.DataContext as PageConfirmAllDataContext;
            var displayColl = source.DisplayTicketDataCollection;
            var performance = source.TicketDataCollection.additional.performance;
            source.PerformanceName = performance.name;
            source.PerformanceDate = performance.date;

            foreach (var tdata in source.TicketDataCollection.collection)
            {
                displayColl.Add(new DisplayTicketData(tdata));
            }
        }

        private async void OnLoaded(object sender, RoutedEventArgs e)
        {
            await(this.DataContext as PageConfirmAllDataContext).PrepareAsync().ConfigureAwait(false);
        }

        private async void OnSubmitWithBoundContext(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as InputDataContext;
            await ProgressSingletonAction.ExecuteWhenWaiting(ctx, async () =>
            {
                var case_ = await ctx.SubmitAsync();
                ctx.TreatErrorMessage();
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
                AppUtil.GetNavigator().NavigateToMatchedPage(case_, this);
            });
        }
    }
}
