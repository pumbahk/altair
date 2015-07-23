using NLog;
using checkin.core.events;
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
using checkin.core.flow;
using checkin.core.models;

namespace checkin.presentation.gui.page
{

    class AuthPasswordDataContext : InputDataContext
    {
        public AuthPasswordDataContext(Page page) : base(page) { }
        public string LoginPassword { get; set; }

        public override void OnSubmit()
        {
            var ev = this.Event as AuthenticationEvent;
            ev.LoginPassword = this.LoginPassword; //TODO:use seret string
            //logger.Info@(String.Format("Submit: Name:{0}, Password:{1}", ev.LoginName, ev.LoginPassword));
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
            var ctx = this.DataContext as AuthPasswordDataContext;

            //@global ev
            GlobalStaticEvent.DescriptionMessageEvent += GlobalStaticEvent_DescriptionMessageEvent;
        }

        void GlobalStaticEvent_DescriptionMessageEvent(object sender, DescriptionMessageEventArgs e)
        {
            this.Dispatcher.InvokeAsync(() =>
            {
                var ctx = this.DataContext as AuthPasswordDataContext;
                ctx.Description = e.Message;
            });
        }
        

        private InputDataContext CreateDataContext()
        {
            return new AuthPasswordDataContext(this)
            {
                Broker = AppUtil.GetCurrentBroker(),
                Event = new AuthenticationEvent(),
            };
        }

        private async void OnLoaded(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as AuthPasswordDataContext;
            await ctx.PrepareAsync().ConfigureAwait(true);
            this.KeyPad.Text = (ctx.Case as CaseAuthPassword).LoginPassword;
            new BindingErrorDialogAction(ctx, this.ErrorDialog).Bind();
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
                    ctx.TreatErrorMessage();
                    AppUtil.GetNavigator().NavigateToMatchedPage(case_, this, ctx.ErrorMessage); //エラーメッセージを受け渡す

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
                else
                {
                    ctx.TreatErrorMessage();
                    AppUtil.GetNavigator().NavigateToMatchedPage(case_, this, ctx.ErrorMessage); //エラーメッセージを受け渡す
                }
                //@global ev
                GlobalStaticEvent.DescriptionMessageEvent -= this.GlobalStaticEvent_DescriptionMessageEvent;
            });
        }

        private void KeyPad_KeyPadFinish(object sender, RoutedEventArgs e)
        {
            e.Handled = true;
            (this.DataContext as AuthPasswordDataContext).LoginPassword = (sender as VirtualKeyboard).Text;
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
                //@global ev
                GlobalStaticEvent.DescriptionMessageEvent -= this.GlobalStaticEvent_DescriptionMessageEvent;
            });
        }

        private void Button_Click(object sender, RoutedEventArgs e)
        {
            this.KeyPad.RaiseVirtualkeyboardFinishEvent();
        }

    }
}
