using QR.presentation.gui.command;
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

namespace QR.presentation.gui.page
{
    /// <summary>
    /// PageCloseConfirm.xaml の相互作用ロジック
    /// </summary>
    public partial class PageCloseConfirm : Page
    {
        public PageCloseConfirm()
        {
            InitializeComponent();
            var name = AppUtil.GetCurrentResource().LoginUser.login_id;
            var description = String.Format("アプリケーションを終了します。「{0}」でログインした際のパスワードを入力しログアウトボタンを押してください", name);
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
            if(ctx.Case.Resource.LoginUser.password == password){
                (ctx.AppCloseCommand as AppCloseCommand).Shutdown();
            }
            else
            {
                ctx.ErrorMessage = "パスワードと一致しません";
                this.ErrorDialog.Show();
            }
        }

        private void OnForward(object sender, RoutedEventArgs e)
        {
            this.KeyPad.RaiseVirtualkeyboardFinishEvent();
        }

        private void OnBackward(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as InputDataContext;
            AppUtil.GetNavigator().NavigateToMatchedPage(ctx.Case, this);
        }
    }
}
