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
using checkin.core.events;

namespace checkin.presentation.gui.page
{

    class PageConfirmOneDataContext : InputDataContext, INotifyPropertyChanged, IConfirmOneStatusInfo
    {
        public string InputString { get; set;}
        public ObservableCollection<UnitStringPair> Candidates {get;set;}
        public override void OnSubmit()
        {
            var ev = this.Event as ConfirmOneEvent;
            ev.PrintUnitString = this.InputString;
            base.OnSubmit();
        }

         private string _performanceName ;
         private string _performanceDate ;

         private string _userName ;

         private string _orderNo ;
         private string _productName ;
         private string _seatName ;
         private string _printedAt;
         private bool _nextEnable;
         private Visibility _nextButtonVisibility;
         private Visibility _allPrintedVisibility;
         private Visibility _multiPrintMode;
         private Visibility _refreshModeVisibility;

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

         public string UserName
         {
             get { return this._userName; }
             set { this._userName = value; this.OnPropertyChanged("UserName"); }
         }

         public string OrderNo
         {
             get { return this._orderNo; }
             set { this._orderNo = value; this.OnPropertyChanged("OrderNo"); }
         }
         public string ProductName
         {
             get { return this._productName; }
             set { this._productName = value; this.OnPropertyChanged("ProductName"); }
         }
         public string SeatName
         {
             get { return this._seatName; }
             set { this._seatName = value; this.OnPropertyChanged("SeatName"); }
         }
         public string PrintedAt
         {
             get { return this._printedAt; }
             set { this._printedAt = value; this.OnPropertyChanged("PrintedAt"); }
         }
         public bool NextEnable
         {
             get { return this._nextEnable; }
             set { this._nextEnable = value; this.OnPropertyChanged("NextEnable"); }
         }
         public Visibility NextButtonVisibility
         {
             get { return this._nextButtonVisibility; }
             set { this._nextButtonVisibility = value; this.OnPropertyChanged("NextButtonVisibility"); }
         }
         public Visibility AllPrintedVisibility
         {
             get { return this._allPrintedVisibility; }
             set { this._allPrintedVisibility = value; this.OnPropertyChanged("AllPrintedVisibility"); }
         }
         public Visibility MultiPrintModeVisibility
         {
             get { return this._multiPrintMode; }
             set { this._multiPrintMode = value; this.OnPropertyChanged("MultiPrintModeVisibility"); }
         }
         public Visibility RefreshModeVisibility
         {
             get { return this._refreshModeVisibility; }
             set { this._refreshModeVisibility = value; this.OnPropertyChanged("RefreshModeVisibility"); }
         }
    }


    /// <summary>
    /// Interaction logic for PageConfirmOne.xaml
    /// </summary>
    public partial class PageConfirmOne : Page//, IDataContextHasCase
    {
        private Logger logger = LogManager.GetCurrentClassLogger();

        public PageConfirmOne()
        {
            InitializeComponent();
            this.DataContext = this.CreateDataContext();
        }

        private InputDataContext CreateDataContext()
        {
            var ctx = new PageConfirmOneDataContext()
            {
                Candidates = CandidateCreator.PrintUnitCandidates(),
                Broker = AppUtil.GetCurrentBroker(),
                RefreshModeVisibility = Visibility.Hidden,
            };
            ctx.Event = new ConfirmOneEvent() { StatusInfo = ctx };
            return ctx;
        }

        private async void OnLoaded(object sender, RoutedEventArgs e)
        {
            var ctx = (this.DataContext as PageConfirmOneDataContext);
            await ctx.PrepareAsync().ConfigureAwait(false);
            ctx.NextEnable = true;
            ctx.NextButtonVisibility = Visibility.Visible;
            ctx.AllPrintedVisibility = Visibility.Hidden;

            if (AppUtil.GetCurrentResource().RefreshMode)
            {
                ctx.RefreshModeVisibility = Visibility.Visible;
            }

            if (!AppUtil.GetCurrentResource().MultiPrintMode)
            {
                ctx.MultiPrintModeVisibility = Visibility.Hidden;
            }

            // Ä”­Œ©ƒ‚[ƒh’†‚ÍAQR‚Å‚Íˆê–‡‚Ì‚Ý‚Ì”­Œ”
            if (AppUtil.GetCurrentResource().RefreshMode)
            {
                ctx.MultiPrintModeVisibility = Visibility.Hidden;
            }

            if (ctx.PrintedAt != null)
            {
                ctx.NextEnable = false;
                ctx.NextButtonVisibility = Visibility.Hidden;
                ctx.AllPrintedVisibility = Visibility.Visible;
                ctx.MultiPrintModeVisibility = Visibility.Hidden;
            }
        }

        /*
        private async void OnSubmitWithBoundContext(object sender, SelectionChangedEventArgs e)
        {
            var box = sender as ListBox;
            if (box.SelectedItem != null)
            {
                var pair = box.SelectedItem as UnitStringPair;
                var ctx = this.DataContext as PageConfirmOneDataContext;
                await ProgressSingletonAction.ExecuteWhenWaiting(ctx, async () =>
                {
                    ctx.InputString = pair.Value;

                    //submit
                    var case_ = await ctx.SubmitAsync();
                    ctx.TreatErrorMessage();
                    AppUtil.GetNavigator().NavigateToMatchedPage(case_, this);
                });
            }
        }
        */

        private async void OnCommonSubmit(string value)
        {
            var ctx = this.DataContext as PageConfirmOneDataContext;
            await ProgressSingletonAction.ExecuteWhenWaiting(ctx, async () =>
            {
                ctx.InputString = value;

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

        private void OnSubmitPrint(object sender, RoutedEventArgs e)
        {
            OnCommonSubmit(PrintUnit.one.ToString());
        }

        private void OnSubmitAllPrint(object sender, RoutedEventArgs e)
        {
            OnCommonSubmit(PrintUnit.all.ToString());
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
