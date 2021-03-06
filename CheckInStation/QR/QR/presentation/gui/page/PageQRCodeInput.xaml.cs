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
using QR.support;

namespace QR.presentation.gui.page
{

    class PageQRCodeInputDataContext : InputDataContext
    {
        public PageQRCodeInputDataContext(Page page): base(page){}

        private string _QRCode;
        public string QRCode
        {
            get { return this._QRCode; }
            set { this._QRCode = value; this.OnPropertyChanged("QRCode"); }
        }

        public override void OnSubmit()
        {
            var ev = this.Event as QRInputEvent;
            ev.QRCode = this.QRCode;
            this.QRCode = ""; //QRのsubmitに失敗した時のことを見越して空にしておく
            base.OnSubmit();
        }
    }


    /// <summary>
    /// Interaction logic for PageQRCodeInput.xaml
    /// </summary>
    public partial class PageQRCodeInput : Page//, IDataContextHasCase
    {
        private Logger logger = LogManager.GetCurrentClassLogger();

        public PageQRCodeInput()
        {
            InitializeComponent();
            //disable IME!!!!!!!!!!!!
            InputMethod.Current.ImeState = InputMethodState.Off;

            this.DataContext = this.CreateDataContext();
            logger.Info("!initialize page: {0}, context: {1}, event: {2}, case: ".WithMachineName(), this, this.DataContext, (this.DataContext as PageQRCodeInputDataContext).Event, (this.DataContext as PageQRCodeInputDataContext).Case);
        }

        private InputDataContext CreateDataContext()
        {
            return new PageQRCodeInputDataContext(this)
            {
                Broker = AppUtil.GetCurrentBroker(),
                Event = new QRInputEvent()
            };
        }

        private async void OnLoaded(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as PageQRCodeInputDataContext;
            await ctx.PrepareAsync().ConfigureAwait(true);
            new BindingErrorDialogAction(ctx, this.ErrorDialog).Bind();
        }

        private async void OnSubmitWithBoundContext(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as PageQRCodeInputDataContext;
            logger.Info("PRessed!!".WithMachineName());
            await ProgressSingletonAction.ExecuteWhenWaiting(ctx, async () =>
            {
                ctx.QRCode = this.QRCodeInput.Text;
                //QRのsubmitに失敗した時のことを見越して空にしておく            
                this.QRCodeInput.Text= "";
                var case_ = await ctx.SubmitAsync();
                ctx.TreatErrorMessage();              
                if (ctx.Event.Status == InternalEventStaus.success)
                {
                    case_ = await ctx.SubmitAsync();
                    ctx.TreatErrorMessage();
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
                AppUtil.GetNavigator().NavigateToMatchedPage(case_, this);
            });
        }

        private void OnKeyDownHandler(object sender, KeyEventArgs e)
        {
            if (e.Key == Key.Return)
            {
                this.Dispatcher.InvokeAsync(() => {
                    this.OnSubmitWithBoundContext(this, new RoutedEventArgs());
                });
            }
        }

        private void OnGotoAnotherMode(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as InputDataContext;
            try
            {
                var broker = AppUtil.GetCurrentBroker();
                var current = broker.FlowManager.Peek().Case;
                var another = broker.RedirectAlternativeCase(current);
                AppUtil.GetNavigator().NavigateToMatchedPage(another, this);
            }
            catch (Exception ex)
            {
                logger.ErrorException("goto another mode".WithMachineName(), ex);
            }
        }

        private void ErrorDialog_MessageDialogComplete(object sender, RoutedEventArgs e)
        {
            this.QRCodeInput.Focus();
        }
    }
}
