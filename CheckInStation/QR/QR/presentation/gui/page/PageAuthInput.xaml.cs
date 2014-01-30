using NLog;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;
using System.Printing;
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

    class AuthInputDataContext : InputDataContext
    {
        private PasswordBox input;
                
        public AuthInputDataContext(PasswordBox input)
        {
            this.input = input;
        }
        public string LoginName { get; set; }
        public string LoginPassword { get { return this.input.Password; } }
        public ObservableCollection<PrintQueue> AvailablePrinters { get; set; }
        public string _selectedPrinterName;
        public string SelectedPrinterName {
            get { return this._selectedPrinterName; }
            set { this._selectedPrinterName = value; this.OnPropertyChanged("SelectedPrinterName"); }
        }

        public override void OnSubmit()
        {
            var ev = this.Event as AuthenticationEvent;
            ev.LoginName = this.LoginName;
            ev.LoginPassword = this.LoginPassword; //TODO:use seret string
            //logger.Info(String.Format("Submit: Name:{0}, Password:{1}", ev.LoginName, ev.LoginPassword));
            base.OnSubmit();
        }
    }


    /// <summary>
    /// Interaction logic for PageAuthInput.xaml
    /// </summary>
    public partial class PageAuthInput : Page//, IDataContextHasCase
    {
        private Logger logger = LogManager.GetCurrentClassLogger();
        public PageAuthInput()
        {
            InitializeComponent();
            //PasswordBox is not Dependency Property. so.
            this.DataContext = this.CreateDataContext();
        }

        private InputDataContext CreateDataContext()
        {
            var printers = new ObservableCollection<PrintQueue>();
            var printing = AppUtil.GetCurrentResource().TicketImagePrinting;
            printers.Add(printing.DefaultPrinter);
            foreach (var q in printing.AvailablePrinters())
            {
                if (printing.DefaultPrinter.FullName != q.FullName)
                {
                    printers.Add(q);
                }
            }
            return new AuthInputDataContext(this.PasswordInput)
            {
                Broker = AppUtil.GetCurrentBroker(),
                Event = new AuthenticationEvent(),
                AvailablePrinters = printers,
                SelectedPrinterName = printing.DefaultPrinter.FullName
            };
        }

        private async void OnLoaded(object sender, RoutedEventArgs e)
        {
            await(this.DataContext as AuthInputDataContext).PrepareAsync().ConfigureAwait(false);
        }

        private void OnPrinterSelected(object sender, SelectionChangedEventArgs e)
        {
            var selected = (sender as ListBox).SelectedItem as PrintQueue;
            AppUtil.GetCurrentResource().TicketImagePrinting.DefaultPrinter = selected;
            (this.DataContext as AuthInputDataContext).SelectedPrinterName = selected.FullName;
        }

        private async void OnSubmitWithBoundContext(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as InputDataContext;
            await ProgressSingletonAction.ExecuteWhenWaiting(ctx, async () =>
            {
                var case_ = await ctx.SubmitAsync(); //入力値チェック

                if (ctx.Event.Status == InternalEventStaus.success)
                {
                    case_ = await ctx.SubmitAsync(); // call login api
                    if (ctx.Event.Status == InternalEventStaus.success)
                    {
                        //ここである必要はあまりないけれど。裏側で広告用の画像をとる
                        var resource = AppUtil.GetCurrentResource();
                        if (resource.AdImageCollector.State == CollectorState.starting)
                        {
                            await resource.AdImageCollector.Run(resource.EndPoint.AdImages).ConfigureAwait(false);
                        }
                    }
                }
                ctx.TreatErrorMessage();
                AppUtil.GetNavigator().NavigateToMatchedPage(case_, this);   
            });
        }
    }
}
