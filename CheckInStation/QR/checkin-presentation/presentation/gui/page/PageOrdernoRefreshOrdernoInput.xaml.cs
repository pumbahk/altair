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
using NLog;
using checkin.core.events;
using checkin.core.flow;
using checkin.presentation.gui.control;

namespace checkin.presentation.gui.page
{
    /// <summary>
    /// Interaction logic for PageOrdernoRefreshOrdernoInput.xaml
    /// </summary>
    public partial class PageOrdernoRefreshOrdernoInput : Page
    {
       private Logger logger = LogManager.GetCurrentClassLogger();

        public PageOrdernoRefreshOrdernoInput()
        {
            InitializeComponent();
            this.DataContext = this.CreateDataContext();
        }

        private InputDataContext CreateDataContext()
        {  
            var ctx = new InputDataContext(this) { Event=new EmptyEvent(),Broker=AppUtil.GetCurrentBroker()};
            ctx.Description = "[再発券許可] 購入時の予約番号を入力してください.";
            return ctx;
        }

        private void OnLoaded(object sender, RoutedEventArgs e)
        {
            var orderno = AppUtil.GetCurrentResource().AuthInfo.organization_code;
            this.KeyPad.Text = orderno;
            new BindingErrorDialogAction(this.DataContext as InputDataContext, this.ErrorDialog).Bind();
        }

        private async void OnSubmitWithBoundContext(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as InputDataContext;
            await ProgressSingletonAction.ExecuteWhenWaiting(ctx, async () =>
            {
                var navigator = AppUtil.GetRefreshPageNavigator();
                navigator.State.Forward();
                navigator.NavigateToMatchedPage(this);
           
                
                ctx.Event.Status = InternalEventStaus.success;//xxx:
            });
        }

        private async void OnBackward(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as InputDataContext;
            await ProgressSingletonAction.ExecuteWhenWaiting(ctx, async () =>
            {
                var navigator = AppUtil.GetRefreshPageNavigator();
                navigator.State.Backward();
                navigator.NavigateToMatchedPage(this);
                ctx.Event.Status = InternalEventStaus.success;//xxx:
            });
        }

        private void KeyPad_KeyPadFinish(object sender, RoutedEventArgs e)
        {
            //hmm.
            e.Handled = true;
            AppUtil.GetRefreshPageNavigator().State.Orderno = (sender as VirtualKeyboard).Text;
            this.OnSubmitWithBoundContext(sender, e);
        }

        private void Button_Click(object sender, RoutedEventArgs e)
        {
            (this.KeyPad as VirtualKeyboard).RaiseVirtualkeyboardFinishEvent();
        }
    }
}
