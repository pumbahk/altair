using NLog;
using QR.presentation.gui.control;
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

    class AuthPasswordDataContext : InputDataContext
    {

        public string LoginPassword { get; set; }

        public override void OnSubmit()
        {
            var ev = this.Event as AuthenticationEvent;
            ev.LoginPassword = this.LoginPassword; //TODO:use seret string
            //logger.Info(String.Format("Submit: Name:{0}, Password:{1}", ev.LoginName, ev.LoginPassword));
            base.OnSubmit();
        }
    }


    /// <summary>
    /// Interaction logic for PageAuthPassword.xaml
    /// </summary>
    public partial class PageAuthPassword : Page//, IDataContextHasCase
    {
        private Logger logger = LogManager.GetCurrentClassLogger();
        public PageAuthPassword()
        {
            InitializeComponent();
            this.DataContext = this.CreateDataContext();
        }

        private InputDataContext CreateDataContext()
        {
            return new AuthPasswordDataContext()
            {
                Broker = AppUtil.GetCurrentBroker(),
                Event = new AuthenticationEvent(),
            };
        }

        private async void OnLoaded(object sender, RoutedEventArgs e)
        {
            await (this.DataContext as AuthPasswordDataContext).PrepareAsync().ConfigureAwait(false);
        }

        private async void OnSubmitWithBoundContext(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as InputDataContext;
            await ProgressSingletonAction.ExecuteWhenWaiting(ctx, async () =>
            {
                var case_ = await ctx.SubmitAsync(); //入力値チェック
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
                ctx.TreatErrorMessage();
                AppUtil.GetNavigator().NavigateToMatchedPage(case_, this, ctx.ErrorMessage); //エラーメッセージを受け渡す
            });
        }

        private void KeyPad_KeyPadFinish(object sender, RoutedEventArgs e)
        {
            (this.DataContext as AuthPasswordDataContext).LoginPassword = (sender as KeyPad).InputString;
            this.OnSubmitWithBoundContext(sender, e);
        }

        private async void OnBackwardWithBoundContext(object sender, RoutedEventArgs e)
        {
            e.Handled = true;
            var ctx = this.DataContext as InputDataContext;
            await ProgressSingletonAction.ExecuteWhenWaiting(ctx, async () =>
            {
                var case_ = await ctx.BackwardAsync();
                ctx.TreatErrorMessage();
                AppUtil.GetNavigator().NavigateToMatchedPage(case_, this);
            });
        }

    }
}
