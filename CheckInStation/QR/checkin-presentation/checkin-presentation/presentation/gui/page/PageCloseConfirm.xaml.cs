using checkin.presentation.gui.command;
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
using vkeyboard.control;
using checkin.core.message;
using checkin.core.models;

namespace checkin.presentation.gui.page
{
    /// <summary>
    /// PageCloseConfirm.xaml の相互作用ロジック
    /// </summary>
    public partial class PageCloseConfirm : Page
    {
        private Func<string, bool> keyPadFinishCallBack;
        public PageCloseConfirm()
        {
            InitializeComponent();
            var name = AppUtil.GetCurrentResource().LoginUser.login_id;
            var description = String.Format("ログアウトします。「{0}」でログインした際のパスワードを入力してください", name);
            this.keyPadFinishCallBack = this.KeyPadActionGotoShutDown;
            this.DataContext = new InputDataContext(this) {
                Broker=AppUtil.GetCurrentBroker(),
                Description=description
            };
        }

        private void OnLoaded(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as InputDataContext;
        }

        private void KeyPad_KeyPadFinish(object sender, RoutedEventArgs e)
        {
            e.Handled = true;
            var ctx = this.DataContext as InputDataContext;
            var password = (sender as VirtualKeyboard).Text;
            if (!this.keyPadFinishCallBack(password))
            {
                ctx.ErrorMessage = "パスワードと一致しません";
                this.ErrorDialog.Show();
            }
        }

        private bool KeyPadActionGotoShutDown(string password)
        {
            var ctx = this.DataContext as InputDataContext;
            if (ctx.Case.Resource.LoginUser.password != password)
            {
                return false;
            }
            (ctx.AppCloseCommand as AppCloseCommand).Shutdown();
            return true;
        }

        private bool KeyPadActionGotoQRRefreshMode(string password)
        {
            var ctx = this.DataContext as InputDataContext;
            if ((AppUtil.GetCurrentResource() as Resource).GetRefreshPassword() != password)
            {
                return false;
            }
            this.NavigationService.Navigate(new PageQRRefresh());
            return true;
        }

        private void OnForward(object sender, RoutedEventArgs e)
        {
            this.keyPadFinishCallBack = this.KeyPadActionGotoShutDown;
            this.KeyPad.RaiseVirtualkeyboardFinishEvent();
        }

        private void OnBackward(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as InputDataContext;
            AppUtil.GetNavigator().NavigateToMatchedPage(ctx.Case, this);
        }

        private void OnGotoQRRefreshMode(object sender, RoutedEventArgs e)
        {
            this.keyPadFinishCallBack = this.KeyPadActionGotoQRRefreshMode;
            this.KeyPad.RaiseVirtualkeyboardFinishEvent();
        }
    }
}
