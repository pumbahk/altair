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
using checkin.core.flow;

namespace checkin.presentation.gui.page
{
  
    class PageConfirmAllDataContext : InputDataContext, IConfirmAllStatusInfo, INotifyPropertyChanged
    {
        public PageConfirmAllDataContext(Page page) : base(page) { }
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
            set { this._TicketDataCollection = value; this.OnPropertyChanged("TicketDataCollection"); }
        }

        private int _PartOrAll;
        public int PartOrAll
        {
            get { return this._PartOrAll; }
            set { this._PartOrAll = value; this.OnPropertyChanged("PartOrAll"); }
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

        private int _NumberOfSelectableTicket;
        public int NumberOfSelectableTicket
        {
            get { return this._NumberOfSelectableTicket; }
            set { this._NumberOfSelectableTicket = value; }
        }

        private int _TotalNumberOfTicket;
        public int TotalNumberOfTicket
        {
            get { return this._TotalNumberOfTicket; }
            set { this._TotalNumberOfTicket = value; this.OnPropertyChanged("TotalNumberOfTicket"); }
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
    public partial class PageConfirmAll : Page//, IDataContextHasCase
    {
        private Logger logger = LogManager.GetCurrentClassLogger();
        private bool loadingLock;

        public PageConfirmAll()
        {
            InitializeComponent();
            this.loadingLock = false;
            this.DataContext = this.CreateDataContext();
        }

        public PageConfirmAll(AbstractCase c)
        {
            InitializeComponent();
            this.loadingLock = false;
            this.DataContext = this.CreateDataContext(c);
        }

        private InputDataContext CreateDataContext()
        {
            var ctx = new PageConfirmAllDataContext(this)
            {
                Broker = AppUtil.GetCurrentBroker(),
                Status = ConfirmAllStatus.starting,
                DisplayTicketDataCollection = new DisplayTicketDataCollection(),
                RefreshModeVisibility = Visibility.Hidden,
                NotPrintVisibility = Visibility.Hidden
            };
            ctx.Event = new ConfirmAllEvent() { StatusInfo = ctx };
            ctx.PropertyChanged += Status_OnPrepared;
            return ctx;
        }

        private InputDataContext CreateDataContext(AbstractCase c)
        {
            var ctx = new PageConfirmAllDataContext(this)
            {
                Broker = AppUtil.GetCurrentBroker(),
                Status = ConfirmAllStatus.starting,
                DisplayTicketDataCollection = new DisplayTicketDataCollection(),
                RefreshModeVisibility = Visibility.Hidden,
                NotPrintVisibility = Visibility.Hidden
            };
            ctx.Event = new ConfirmAllEvent() { StatusInfo = ctx };
            var e = ctx.Event as ConfirmAllEvent;
            e.StatusInfo.TicketDataCollection = (c.PresentationChanel as ConfirmAllEvent).StatusInfo.TicketDataCollection;
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
            foreach (var tdata in source.collection)
            {
                var dtdata = new DisplayTicketData(ctx, tdata);
                if (ctx.ReadTicketData != null)
                {
                    // QRを読み込んだものだけ初期発券予定とする。
                    if (ctx.ReadTicketData.ordered_product_item_token_id != tdata.ordered_product_item_token_id)
                    {
                        //dtdata.IsSelected = false;
                        ctx.NumberOfPrintableTicket--;
                    }
                    else if(tdata.printed_at == null)
                    {
                        dtdata.IsSelected = true;
                    }
                }
                dtdata.PropertyChanged += OnCountChangePrintableTicket;
                displayColl.Add(dtdata);
            }
            ctx.NumberOfPrintableTicket = source.collection.Where(o => o.is_selected && o.printed_at == null).Count();
            ctx.NumberOfSelectableTicket = source.collection.Where(o => o.printed_at == null).Count();
            ctx.TotalNumberOfTicket = source.collection.Count();
            if (ctx.NumberOfSelectableTicket > 0)
            {
                ctx.NotPrintVisibility = Visibility.Visible;
            }
        }

        void OnCountChangePrintableTicket(object sender, PropertyChangedEventArgs e)
        {
            var ctx = this.DataContext as PageConfirmAllDataContext;
            var DisplayTicketData = (sender as DisplayTicketData);
            if (e.PropertyName == "IsSelected")
            {
                var delta = DisplayTicketData.IsSelected ? 1 : -1;
                this.Dispatcher.InvokeAsync(() => {
                    ctx.NumberOfPrintableTicket += delta;
                });
            }
        }

        private async void OnLoaded(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as PageConfirmAllDataContext;
            if (AppUtil.GetCurrentResource().RefreshMode)
            {
                ctx.RefreshModeVisibility = Visibility.Visible;
            }
            ctx.Description = "データを取得しています。少々お待ちください";
            await ctx.PrepareAsync();
            ctx.Description = ctx.Case.Description;
            var s = await ctx.VerifyAsync();
            this.loadingLock = true;

            if(!s){
                this.OnSubmitWithBoundContext(sender, e); //xxx:
            }
             
            new BindingErrorDialogAction(ctx, this.ErrorDialog).Bind();
        }

        private async void OnSubmitWithBoundContext(object sender, RoutedEventArgs e)
        {
            if (!this.loadingLock)
            {
                logger.Warn("too early.");
                return;
            }
            var ctx = this.DataContext as InputDataContext;
            var pageCtx = ctx as PageConfirmAllDataContext;
            if (sender is System.Windows.Controls.Button)
            {
                if (pageCtx.NumberOfPrintableTicket == 0 && pageCtx.NumberOfSelectableTicket > 0)
                {
                    pageCtx.ErrorMessage = "発券したいチケットを選択してください";
                    return;
                }
            }
            await ProgressSingletonAction.ExecuteWhenWaiting(ctx, async () =>
            {
                var case_ = await ctx.SubmitAsync();
                ctx.TreatErrorMessage();

                //unregister event
                int notPrintedCount = 0;
                foreach (var dc in pageCtx.DisplayTicketDataCollection)
                {
                    dc.PropertyChanged -= OnCountChangePrintableTicket;
                    if (dc.PrintedAt == null)
                    {
                        notPrintedCount++;
                    }
                }

                if (notPrintedCount == 0)
                {
                    pageCtx.Description = "このチケットは発券済みです";
                    pageCtx.ErrorMessage = "このチケットは発券済みです";
                    this.Backward.Visibility = Visibility.Hidden;
                    return;
                }
                //this.NavigationService.Navigate(new PagePrintingConfirm());
                AppUtil.GetNavigator().NavigateToMatchedPage(case_, this);
            });
        }

        private async void OnBackwardWithBoundContext(object sender, RoutedEventArgs e)
        {
            if (!this.loadingLock)
            {
                logger.Warn("too early.");
                return;
            }
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

        private async void OnGotoWelcome(object sender, RoutedEventArgs e)
        {
            e.Handled = true;
            var ctx = this.DataContext as InputDataContext;
            await ProgressSingletonAction.ExecuteWhenWaiting(ctx, async () =>
            {
                AppUtil.GotoWelcome(this);
            });
        }
    }
}
