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

using checkin.core.events;
using checkin.presentation.gui.control;
using checkin.core.message;
using checkin.core.events;
using checkin.core.models;
using checkin.core.support;

namespace checkin.presentation.gui.page
{
    /// <summary>
    /// Interaction logic for PageOrodernoRefreshTelInput.xaml
    /// </summary>
    public partial class PageOrodernoRefreshTelInput : Page
    {
        public PageOrodernoRefreshTelInput()
        {
            InitializeComponent();
            this.DataContext = this.CreateDataContext();
        }

        private InputDataContext CreateDataContext()
        {
            var ctx = new InputDataContext(this) { Event = new EmptyEvent(), Broker = AppUtil.GetCurrentBroker() };
            ctx.Description = "[再発券許可] 購入時の電話番号を入力してください.";
            return ctx;
        }

        private void OnLoaded(object sender, RoutedEventArgs e)
        {
            new BindingErrorDialogAction(this.DataContext as InputDataContext, this.ErrorDialog).Bind();
        }

        private async void OnSubmitWithBoundContext(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as InputDataContext;
            await ProgressSingletonAction.ExecuteWhenWaiting(ctx, async () =>
            {
                var navigator = AppUtil.GetRefreshPageNavigator();
                var status = await this.SubmitAsync(navigator.State);
                if (status)
                {
                    navigator.State.Forward();
                   // navigator.NavigateToMatchedPage(this);
                }
            });
        }

        private async Task<bool> SubmitAsync(RefreshPageState state) //todo: move
        {
            var ctx = this.DataContext as InputDataContext;
            ctx.Description = "対応した受付番号の注文のチケットを再発券許可しています";
            var resource = AppUtil.GetCurrentResource();
            ResultTuple<string, string> result = await new DispatchResponse<string>(resource).Dispatch(() => new TicketRefreshedAtUpdater2(resource).UpdateRefreshedAtAsync(state.Orderno, state.Tel));
            if (result.Status)
            {
                ctx.Event.NotifyFlushMessage(String.Format("受付番号「{0}」のチケットを再発券許可しました", result.Right));
                ctx.TreatErrorMessage();
                ctx.Event.Status = InternalEventStaus.success;//xxx:
                return true;
            }
            else
            {
                ctx.Event.NotifyFlushMessage(result.Left);
                ctx.TreatErrorMessage();
                ctx.Event.Status = InternalEventStaus.failure;//xxx:
                return false;
            }
        }

        private async void OnBackward(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as InputDataContext;
            if (ctx.Progress == DataContextProgress.finished)
            {
                var navigator = AppUtil.GetRefreshPageNavigator();
                navigator.NavigateToMatchedPage(this);
            }
            else
            {
                await ProgressSingletonAction.ExecuteWhenWaiting(ctx, async () =>
                {
                    var navigator = AppUtil.GetRefreshPageNavigator();
                    navigator.State.Backward();
                    navigator.NavigateToMatchedPage(this);
                    ctx.Event.Status = InternalEventStaus.success;//xxx:
                });
            }
        }

        private void KeyPad_KeyPadFinish(object sender, RoutedEventArgs e)
        {
            //hmm.
            e.Handled = true;
            AppUtil.GetRefreshPageNavigator().State.Tel = (sender as VirtualKeyboard).Text;
            this.OnSubmitWithBoundContext(sender, e);
        }

        private void Button_Click(object sender, RoutedEventArgs e)
        {
            (this.KeyPad as VirtualKeyboard).RaiseVirtualkeyboardFinishEvent();
        }
    }
}
