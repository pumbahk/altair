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

        private int _NumberOfTicketDisplayLimit = 10;
        public int NumberOfTicketDisplayLimit
        {
            get { return this._NumberOfTicketDisplayLimit; }
        }

        private int _TotalNumberOfTicket;
        public int TotalNumberOfTicket
        {
            get { return this._TotalNumberOfTicket; }
            set { this._TotalNumberOfTicket = value; this.OnPropertyChanged("TotalNumberOfTicket"); }
        }

        /// <summary>
        /// Used to observe the changes of tickets to be displayed
        /// </summary>
        public DisplayTicketDataCollection DisplayTicketDataCollection { get; set; }

        // added to cache all the ticket data
        public List<DisplayTicketData> TicketDataColl;

        // added to follow current index of item shown on top of list
        public int HeaderIndex;

        // indicator if bottom of list is shown
        private bool _isBottom;
        public bool isBottom
        {
            get { return this._isBottom; }
            set { this._isBottom = value; }
        }

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
        private Logger logger = LogManager.GetCurrentClassLogger();
        private bool loadingLock;

        public PageConfirmListAll()
        {
            InitializeComponent();
            this.loadingLock = false;
            this.DataContext = this.CreateDataContext();
            // set default visibility of UpButton and DownButton to be hidden
            ChangeButtonVisibility("UpButton", Visibility.Hidden);
            ChangeButtonVisibility("DownButton", Visibility.Hidden);
        }

        private InputDataContext CreateDataContext()
        {
            var ctx = new PageConfirmListAllDataContext(this)
            {
                Broker = AppUtil.GetCurrentBroker(),
                Status = ConfirmAllStatus.starting,
                RefreshModeVisibility = Visibility.Hidden,
                DisplayTicketDataCollection = new DisplayTicketDataCollection(),
                TicketDataColl = new List<DisplayTicketData>()
            };
            ctx.Event = new ConfirmAllEvent() { StatusInfo = ctx };
            ctx.PropertyChanged += Status_OnPrepared;
            return ctx;
        }

        private void Status_OnPrepared(object sender, PropertyChangedEventArgs e)
        {
            var ctx = sender as PageConfirmListAllDataContext;
            if (e.PropertyName == "Status" && ctx.Status == ConfirmAllStatus.prepared)
            {
                ctx.Status = ConfirmAllStatus.requesting;
                //後の継続を同期的に待つ必要ないのでawaitしない
                ctx.TicketDataCollection.collection = ctx.TicketDataCollection.collection.Where(o => o.printed_at == null).Cast<TicketDataMinumum>().ToArray();
                if (ctx.TicketDataCollection != null)
                {
                    this.Dispatcher.InvokeAsync(this.BuildDisplayItems);
                }
                else
                {
                    this.Dispatcher.InvokeAsync(async () =>
                    {
                        var case_ = await ctx.SubmitAsync();
                        ctx.TreatErrorMessage();
                        AppUtil.GetNavigator().NavigateToMatchedPage(case_, this);
                    });
                }
            }
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

            ctx.HeaderIndex = 0;

            // 20191209 added index to track how many tickets are processed in the loop
            foreach (var item in source.collection.Select((tdata, index) => new { tdata, index }))
            {
                var dtdata = new DisplayTicketData(ctx, item.tdata);
                if (ctx.ReadTicketData != null)
                {
                    dtdata.IsSelected = true;
                }
                dtdata.PropertyChanged += OnCountChangePrintableTicket;

                // 20191209 Caching all the ticket view model data to avoid creating new instance when showing overflown items
                ctx.TicketDataColl.Add(dtdata);

                // 20191209 ObservableCollection should contain only visible items
                if (item.index < ctx.NumberOfTicketDisplayLimit)
                {
                    displayColl.Add(dtdata);
                }
            }
            ctx.NumberOfPrintableTicket = source.collection.Where(o => o.is_selected && o.printed_at == null).Count();
            ctx.TotalNumberOfTicket = source.collection.Count();

            // 20191209 Manage the initial visibility of DownButton
            if (ctx.TotalNumberOfTicket > 10)
            {
                ChangeButtonVisibility("DownButton", Visibility.Visible);
            }
            //foreach (var tdata in source.collection)
            //{
            //    var dtdata = new DisplayTicketData(ctx, tdata);
            //    if (ctx.ReadTicketData != null)
            //    {
            //        dtdata.IsSelected = true;
            //    }
            //    dtdata.PropertyChanged += OnCountChangePrintableTicket;
            //    displayColl.Add(dtdata);
            //}
            //ctx.NumberOfPrintableTicket = source.collection.Where(o => o.is_selected && o.printed_at == null).Count();
        }

        void OnCountChangePrintableTicket(object sender, PropertyChangedEventArgs e)
        {
            var ctx = this.DataContext as PageConfirmListAllDataContext;
            var DisplayTicketData = (sender as DisplayTicketData);
            if (e.PropertyName == "IsSelected")
            {
                var delta = DisplayTicketData.IsSelected ? 1 : -1;
                this.Dispatcher.InvokeAsync(() =>
                {
                    ctx.NumberOfPrintableTicket += delta;
                });
            }
        }

        private async void OnLoaded(object sender, RoutedEventArgs e)
        {   
            var ctx = this.DataContext as PageConfirmListAllDataContext;
            new BindingErrorDialogAction(ctx, this.ErrorDialog).Bind();
            if (AppUtil.GetCurrentResource().RefreshMode)
            {
                ctx.RefreshModeVisibility = Visibility.Visible;
            }
            ctx.Description = "データを取得しています。少々お待ちください";
            await ctx.PrepareAsync();
            //ctx.Description = ctx.Case.Description;
            var s = await ctx.VerifyAsync();
            this.loadingLock = true;
            ctx.Description = "発券するチケットは以下でよろしいですか？よろしければ「発券する」ボタンを押してください";
            if (!s)
            {
                this.OnSubmitWithBoundContext(sender, e); //xxx:
            }
        }

        private async void OnSubmitWithBoundContext(object sender, RoutedEventArgs e)
        {
            if (!this.loadingLock)
            {
                logger.Warn("too early.");
                return;
            }
            var ctx = this.DataContext as InputDataContext;
            await ProgressSingletonAction.ExecuteWhenWaiting(ctx, async () =>
            {
                var case_ = await ctx.SubmitAsync();
                ctx.TreatErrorMessage();

                //unregister event
                int notPrintedCount = 0;
                var pageCtx = ctx as PageConfirmListAllDataContext;
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
                    pageCtx.NotPrintVisibility = Visibility.Hidden;
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
                foreach (var dc in (ctx as PageConfirmListAllDataContext).DisplayTicketDataCollection)
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

        // Conotrols to display items overflown above the list
        private void ShowItemsUpward(object sender, RoutedEventArgs e)
        {
            // Just manage ObservableCollection, DisplayTicketDataCollection,
            // since the change on collection is notified to GUI and change the display
            var ctx = this.DataContext as PageConfirmListAllDataContext;
            var dataColl = ctx.DisplayTicketDataCollection;
            var dataArr = ctx.TicketDataColl;
            int addedIndecies = ctx.HeaderIndex - 2;

            dataColl.RemoveAt(dataColl.Count - 1);

            if (ctx.TotalNumberOfTicket % 2 == 0)
            {
                dataColl.RemoveAt(dataColl.Count - 1);
            }
            else if (!ctx.isBottom)
            {
                dataColl.RemoveAt(dataColl.Count - 1);
            }

            var itemAdded = dataArr[addedIndecies + 1];
            dataColl.Insert(0, itemAdded);
            itemAdded = dataArr[addedIndecies];
            dataColl.Insert(0, itemAdded);

            ctx.HeaderIndex -= 2;
            ctx.isBottom = false;
            if (ctx.HeaderIndex == 0)
            {
                ((Button)sender).Visibility = Visibility.Hidden;
            }
            ChangeButtonVisibility("DownButton", Visibility.Visible);
        }

        // Conotrols to display items overflown below the list
        private void ShowItemsDownward(object sender, RoutedEventArgs e)
        {
            // Just manage ObservableCollection, DisplayTicketDataCollection,
            // since the change on collection is notified to GUI and change the display
            var ctx = this.DataContext as PageConfirmListAllDataContext;
            var dataColl = ctx.DisplayTicketDataCollection;
            var dataArr = ctx.TicketDataColl;
            int addedIndecies = ctx.HeaderIndex + 10;

            dataColl.RemoveAt(0);
            dataColl.RemoveAt(0);

            var itemAdded = dataArr[addedIndecies];
            dataColl.Add(itemAdded);
            if (addedIndecies < dataArr.Count - 1)
            {
                itemAdded = dataArr[addedIndecies + 1];
                dataColl.Add(itemAdded);
            }

            ctx.HeaderIndex += 2;
            if (ctx.HeaderIndex > 0)
            {
                ChangeButtonVisibility("UpButton", Visibility.Visible);
            }
            if ((addedIndecies + 1) == dataArr.Count || (addedIndecies + 2) == dataArr.Count)
            {
                ((Button)sender).Visibility = Visibility.Hidden;
                ctx.isBottom = true;
            }
        }

        private void ChangeButtonVisibility(string name, Visibility visibility)
        {
            object wantedNode = this.FindName(name);
            if (wantedNode is Button)
            {
                // Following executed if Text element was found.
                Button wantedChild = wantedNode as Button;
                wantedChild.Visibility = visibility;
            }
        }
    }
}
