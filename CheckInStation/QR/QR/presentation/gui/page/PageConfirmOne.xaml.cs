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

    class PageConfirmOneDataContext : InputDataContext, INotifyPropertyChanged, IConfirmOneStatusInfo
    {
        public string InputString { get; set;}
        public ObservableCollection<UnitPair> Candidates {get;set;}
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
         private string _printedAt ;

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
            };
            ctx.Event = new ConfirmOneEvent() { StatusInfo = ctx };
            return ctx;
        }

        private async void OnLoaded(object sender, RoutedEventArgs e)
        {
            await (this.DataContext as PageConfirmOneDataContext).PrepareAsync().ConfigureAwait(false);
        }

        private async void OnSubmitWithBoundContext(object sender, SelectionChangedEventArgs e)
        {
            var box = sender as ListBox;
            if (box.SelectedItem != null)
            {
                var pair = box.SelectedItem as UnitPair;
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
