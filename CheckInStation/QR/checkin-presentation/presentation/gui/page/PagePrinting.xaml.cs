using NLog;
using System;
using System.Collections.Generic;
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
using checkin.core.support;
using checkin.core.events;

namespace checkin.presentation.gui.page
{

    class PagePrintingDataContext : InputDataContext, IPrintingStatusInfo, INotifyPropertyChanged
    {
        private int _finishedPrinted;
        private int _totalPrinted;
        private PrintingStatus _status;
        private string _subDescription;

        public int TotalPrinted {
            get { return this._totalPrinted;}
            set { this._totalPrinted = value; this.OnPropertyChanged("TotalPrinted"); }
        }
        public int FinishedPrinted {
            get { return this._finishedPrinted; }
            set { this._finishedPrinted = value; this.OnPropertyChanged("FinishedPrinted"); }
        }
        public BitmapImage AdImage { get; set; }
        public PrintingStatus Status 
        {
            get {return this._status;}
            set
            {
                this._status = value;
                this.OnPropertyChanged("Status");
            }
        }

        public string SubDescription
        {
            get { return this._subDescription; }
            set
            {
                this._subDescription = value;
                this.OnPropertyChanged("SubDescription");
            }
        }

        public override void OnSubmit()
        {
            var ev = this.Event as IInternalEvent;
            base.OnSubmit();
        }
        
        public string SubDescriptionFromStatus(PrintingStatus status){
            switch (status)
            {
                case PrintingStatus.starting:
                    return "データを取得しています";
                case PrintingStatus.prepared:
                    return "データ取得完了しました";
                case PrintingStatus.requesting:
                    return "印刷しています";
                case PrintingStatus.printing:
                    return "印刷しています";
                case PrintingStatus.finished:
                    return "印刷完了しました";
                default:
                    return "-";
            }
        }
    }


    /// <summary>
    /// Interaction logic for PagePrinting.xaml
    /// </summary>
    public partial class PagePrinting : Page//, IDataContextHasCase
    {
        private Logger logger = LogManager.GetCurrentClassLogger();

        public PagePrinting()
        {
            InitializeComponent();
            this.DataContext = this.CreateDataContext();
        }

        private InputDataContext CreateDataContext()
        {
            var resource = AppUtil.GetCurrentResource();
            var ctx = new PagePrintingDataContext()
            {
                Broker = AppUtil.GetCurrentBroker(),
                AdImage = resource.AdImageCollector.GetImage(),
            };
            ctx.SubDescription = ctx.SubDescriptionFromStatus(ctx.Status);

            ctx.Event = new PrintingEvent() {
                CurrentDispatcher = this.Dispatcher,
                StatusInfo = ctx as IPrintingStatusInfo,
            };
            ctx.PropertyChanged += ctx_PropertyChanged;
            ctx.TotalPrinted = 0;
            ctx.FinishedPrinted = 0;
            return ctx;
        }

        void ctx_PropertyChanged(object sender, PropertyChangedEventArgs e)
        {
            if (e.PropertyName == "Status")
            {
                var ctx = sender as PagePrintingDataContext;
                ctx.SubDescription = ctx.SubDescriptionFromStatus(ctx.Status);
            }
        }

        private async void OnLoaded(object sender, RoutedEventArgs e)
        {
            this.LoadingAdorner.ShowAdorner();
            await (this.DataContext as PagePrintingDataContext).PrepareAsync();
            await OnPrintingStart();
        }

        private async Task OnPrintingStart()
        {
            var ctx = this.DataContext as PagePrintingDataContext;
            await ProgressSingletonAction.ExecuteWhenWaiting(ctx, async () =>
          {
              ctx.Status = PrintingStatus.requesting;
              logger.Trace("** status is requesting".WithMachineName());

              var case_ = await ctx.SubmitAsync();
              ctx.TreatErrorMessage();
              AppUtil.GetNavigator().NavigateToMatchedPage(case_, this);
          });
        }
    }
}

