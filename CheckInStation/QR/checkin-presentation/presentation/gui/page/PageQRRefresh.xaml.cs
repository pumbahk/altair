using System;
using System.Collections.Generic;
using System.Linq;
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
using NLog;

//model ::xxx
using checkin.core.message;
using checkin.core.events;
using checkin.core.models;

namespace checkin.presentation.gui.page
{
    /// <summary>
    /// Interaction logic for PageQRRefresh.xaml
    /// </summary>
    public partial class PageQRRefresh : Page
    {
        public PageQRRefresh()
        {
            InitializeComponent();
            var ctx = new InputDataContext(this) { Event=new EmptyEvent(),Broker=AppUtil.GetCurrentBroker()};
            ctx.Description = "再発券を許可するために、QRリーダーにQRコードをかざしてください.";
            this.DataContext = ctx;
        }
        private Logger logger = LogManager.GetCurrentClassLogger();

        private void OnLoaded(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as InputDataContext;
            new BindingErrorDialogAction(ctx, this.ErrorDialog).Bind();
        }

        private async void OnSubmitWithBoundContext(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as InputDataContext;
            await ProgressSingletonAction.ExecuteWhenWaiting(ctx, async () =>
            {
                var qrcode = this.QRCodeInput.Text;
                //QRのsubmitに失敗した時のことを見越して空にしておく
                this.QRCodeInput.Text = "";
                await this.SubmitAsync(qrcode);
            });
        }

        private async Task SubmitAsync(string qrcode) //todo: move
        {
            var ctx = this.DataContext as InputDataContext;
            ctx.Description = "渡されたQRコードに結びついているチケットを再発券許可しています";
            var resource = AppUtil.GetCurrentResource();
            ResultTuple<string, string> result = await new DispatchResponse<string>(resource).Dispatch(() => new TicketRefreshedAtUpdater(resource).UpdateRefreshedAtAsync(qrcode));
            if (result.Status){
                ctx.Event.NotifyFlushMessage(String.Format("受付番号「{0}」のチケットを再発券許可しました", result.Right));
                ctx.TreatErrorMessage();
                ctx.Event.Status = InternalEventStaus.success;//xxx:
                //AppUtil.GetNavigator().NavigateToMatchedPage(ctx.Case, this);
            } else {
                ctx.Event.NotifyFlushMessage(result.Left);
                ctx.TreatErrorMessage();
                ctx.Event.Status = InternalEventStaus.failure;//xxx:
            }
        }

        private void OnBackward(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as InputDataContext;
            AppUtil.GetNavigator().NavigateToMatchedPage(ctx.Case, this);
        }

        private void OnKeyDownHandler(object sender, KeyEventArgs e)
        {
            if (e.Key == Key.Return)
            {
                this.Dispatcher.InvokeAsync(() =>
                {
                    this.OnSubmitWithBoundContext(this, new RoutedEventArgs());
                });
            }
        }

        private void ErrorDialog_MessageDialogComplete(object sender, RoutedEventArgs e)
        {
            this.QRCodeInput.Focus();
        }
    }
}
