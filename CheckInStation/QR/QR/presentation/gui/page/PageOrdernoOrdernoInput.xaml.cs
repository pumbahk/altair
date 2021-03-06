using NLog;
using QR.presentation.gui.control;
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
using vkeyboard.control;
using QR.support;

namespace QR.presentation.gui.page
{

    class PageOrdernoOrdernoInputDataContext : InputDataContext
    {
        public PageOrdernoOrdernoInputDataContext(Page page) : base(page) { }

        public string Orderno { get; set; }

        public override void OnSubmit()
        {
            var ev = this.Event as OrdernoInputEvent;
            ev.Orderno = this.Orderno;
            base.OnSubmit();
        }
    }


    /// <summary>
    /// Interaction logic for PageOrdernoOrdernoInput.xaml
    /// </summary>
    public partial class PageOrdernoOrdernoInput : Page//, IDataContextHasCase
    {
        private Logger logger = LogManager.GetCurrentClassLogger();

        public PageOrdernoOrdernoInput()
        {
            InitializeComponent();
            this.DataContext = this.CreateDataContext();
        }

        private InputDataContext CreateDataContext()
        {
            return new PageOrdernoOrdernoInputDataContext(this)
            {
                Broker = AppUtil.GetCurrentBroker(),
                Event = new OrdernoInputEvent()
            };
        }

        private async void OnLoaded(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as PageOrdernoOrdernoInputDataContext;
            await ctx.PrepareAsync().ConfigureAwait(true);
            var data = (ctx.Case as CaseOrdernoOrdernoInput).RequestData;
            {
                string orderno;
                if (data != null && data.order_no != null)
                    orderno = data.order_no;
                else
                    orderno = AppUtil.GetCurrentResource().AuthInfo.organization_code;
                this.KeyPad.Text = orderno;
            }
            new BindingErrorDialogAction(ctx, this.ErrorDialog).Bind();
        }

        private async void OnSubmitWithBoundContext(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as InputDataContext;
            await ProgressSingletonAction.ExecuteWhenWaiting(ctx, async () =>
            {
                var case_ = await ctx.SubmitAsync();
                ctx.TreatErrorMessage();              
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

        private void KeyPad_KeyPadFinish(object sender, RoutedEventArgs e)
        {
            //hmm.
            e.Handled = true;
            (this.DataContext as PageOrdernoOrdernoInputDataContext).Orderno = (sender as VirtualKeyboard).Text;
            this.OnSubmitWithBoundContext(sender, e);
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

        private void Button_Click(object sender, RoutedEventArgs e)
        {
            (this.KeyPad as VirtualKeyboard).RaiseVirtualkeyboardFinishEvent();
        }
    }
}
