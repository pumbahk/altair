using NLog;
using checkin.presentation.gui.control;
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
using checkin.core.events;
using checkin.core.flow;

namespace checkin.presentation.gui.page
{

    class AuthInputDataContext : InputDataContext
    {
        public AuthInputDataContext(Page page) : base(page) { }

        public string LoginName { get; set; }
 
        public override void OnSubmit()
        {
            var ev = this.Event as AuthenticationEvent;
            ev.LoginName = this.LoginName;
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
            this.DataContext = this.CreateDataContext();
        }

        private InputDataContext CreateDataContext()
        {
            return new AuthInputDataContext(this)
            {
                Broker = AppUtil.GetCurrentBroker(),
                Event = new AuthenticationEvent(),
            };
        }

        private async void OnLoaded(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as AuthInputDataContext;
            await ctx.PrepareAsync().ConfigureAwait(true);
            this.KeyPad.Text = (ctx.Case as CaseAuthInput).LoginName;

            // ErrorMessageが変更されたときにエラーダイアログを表示させる
            new BindingErrorDialogAction(ctx, this.ErrorDialog).Bind();
        }

        private async void OnSubmitWithBoundContext(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as InputDataContext;
            await ProgressSingletonAction.ExecuteWhenWaiting(ctx, async () =>
            {
                var case_ = await ctx.SubmitAsync(); //入力値チェック
                ctx.TreatErrorMessage();
                AppUtil.GetNavigator().NavigateToMatchedPage(case_, this);   
            });
        }

        private void KeyPad_KeyPadFinish(object sender, RoutedEventArgs e)
        {
            //歴史的経緯で
            // virtualkeyboardからの出力がAuthInputDataContext.LoginNameに渡され。
            // AuthInputDataContext.LoginNameがAuthInputEvent.LoginNameに渡され。
            // モデル側の処理はAuthInputEvent.LoginNameを見る。
            e.Handled = true;
            (this.DataContext as AuthInputDataContext).LoginName = (sender as VirtualKeyboard).Text;
            this.OnSubmitWithBoundContext(sender, e);
        }

        private void Button_Click(object sender, RoutedEventArgs e)
        {
            this.KeyPad.RaiseVirtualkeyboardFinishEvent();
        }
    }
}
