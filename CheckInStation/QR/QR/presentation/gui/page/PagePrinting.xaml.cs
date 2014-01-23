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

namespace QR.presentation.gui.page
{

    class PagePrintingDataContext : InputDataContext, IPrintingStatusInfo, INotifyPropertyChanged
    {
        private int _finishedPrinted;
        private int _totalPrinted;
        private PrintingStatus _status;
        
        public int TotalPrinted {
            get { return this._totalPrinted;}
            set { this._totalPrinted = value; this.OnPropertyChanged("TotalPrinted"); }
        }
        public int FinishedPrinted {
            get { return this._finishedPrinted; }
            set { this._finishedPrinted = value; this.OnPropertyChanged("FinishedPrinted"); }
        }
        public PrintingStatus Status 
        {
            get {return this._status;}
            set {this._status = value;
                 this.OnPropertyChanged("Status");
            }
        } 

        public override void OnSubmit()
        {
            var ev = this.Event as IInternalEvent;
            base.OnSubmit();
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
            var ctx = new PagePrintingDataContext()
            {
                Broker = AppUtil.GetCurrentBroker(),
            };
            ctx.Event = new PrintingEvent() { StatusInfo = ctx as IPrintingStatusInfo };
            ctx.PropertyChanged += OnPrintingStart;
            return ctx;
        }

        private async void OnLoaded(object sender, RoutedEventArgs e)
        {
            await(this.DataContext as PagePrintingDataContext).PrepareAsync().ConfigureAwait(false);
        }

        private async void OnPrintingStart(object sender, PropertyChangedEventArgs e)
        {
            var ctx = sender as PagePrintingDataContext;
            if (ctx.Status == PrintingStatus.requesting)
            {
                logger.Debug("** status is requesting");
                await this.Dispatcher.InvokeAsync(async () =>
                {
                    var case_ = await ctx.SubmitAsync();
                    ctx.TreatErrorMessage();
                    AppUtil.GetNavigator().NavigateToMatchedPage(case_, this);
                });
            }
        }
    }
}
