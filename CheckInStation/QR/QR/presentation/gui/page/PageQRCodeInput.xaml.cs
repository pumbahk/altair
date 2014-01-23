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

    class PageQRCodeInputDataContext : InputDataContext
    {
        public string QRCode { get; set; }
        public override void OnSubmit()
        {
            var ev = this.Event as QRInputEvent;
            ev.QRCode = this.QRCode;
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
            this.DataContext = this.CreateDataContext();
            logger.Info("!initialize page: {0}, context: {1}, event: {2}, case: ", this, this.DataContext, (this.DataContext as PageQRCodeInputDataContext).Event, (this.DataContext as PageQRCodeInputDataContext).Case);
        }

        private InputDataContext CreateDataContext()
        {
            return new PageQRCodeInputDataContext()
            {
                Broker = AppUtil.GetCurrentBroker(),
                Event = new QRInputEvent()
            };
        }

        private async void OnLoaded(object sender, RoutedEventArgs e)
        {
            await(this.DataContext as PageQRCodeInputDataContext).PrepareAsync().ConfigureAwait(false);
        }

        private async void OnSubmitWithBoundContext(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as InputDataContext;
            var case_ = await ctx.SubmitAsync();
            if (ctx.Event.Status == InternalEventStaus.success)
                case_ = await ctx.SubmitAsync();
            ctx.TreatErrorMessage();
            AppUtil.GetNavigator().NavigateToMatchedPage(case_, this);
        }

        private async void OnBackwardWithBoundContext(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as InputDataContext;
            var case_ = await ctx.BackwardAsync();
            ctx.TreatErrorMessage();
            AppUtil.GetNavigator().NavigateToMatchedPage(case_, this);
        }
    }
}
