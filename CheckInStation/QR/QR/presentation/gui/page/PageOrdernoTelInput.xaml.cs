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

namespace QR.presentation.gui.page
{

    class PageOrdernoTelInputDataContext : InputDataContext
    {
        public string Tel { get; set; }
        public override void OnSubmit()
        {
            var ev = this.Event as IInternalEvent;
            (ev as OrdernoInputEvent).Tel = this.Tel;
            base.OnSubmit();
        }
    }


    /// <summary>
    /// Interaction logic for PageOrdernoTelInput.xaml
    /// </summary>
    public partial class PageOrdernoTelInput : Page//, IDataContextHasCase
    {
        private Logger logger = LogManager.GetCurrentClassLogger();

        public PageOrdernoTelInput()
        {
            InitializeComponent();
            this.DataContext = this.CreateDataContext();
        }

        private InputDataContext CreateDataContext()
        {
            return new PageOrdernoTelInputDataContext()
            {
                Broker = AppUtil.GetCurrentBroker(),
                Event = new OrdernoInputEvent()
            };
        }

        private async void OnLoaded(object sender, RoutedEventArgs e)
        {
            await(this.DataContext as PageOrdernoTelInputDataContext).PrepareAsync().ConfigureAwait(false);
        }

        private async void OnSubmitWithBoundContext(object sender, RoutedEventArgs e)
        {
            e.Handled = true;
            var ctx = this.DataContext as InputDataContext;
            await ProgressSingletonAction.ExecuteWhenWaiting(ctx, async () =>
            {
                var case_ = await ctx.SubmitAsync();
                //slackoff
                if (ctx.Event.Status == InternalEventStaus.success)
                {
                    case_ = await ctx.SubmitAsync();
                }
                ctx.TreatErrorMessage();
                AppUtil.GetNavigator().NavigateToMatchedPage(case_, this);
            });
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

        private void KeyPad_KeyPadFinish(object sender, RoutedEventArgs e)
        {
            e.Handled = true;
            var v = ((sender as KeyPad).DataContext as KeyPadPopupContext).InputString;
            MessageBox.Show(String.Format("box: {0}", v));
            OnSubmitWithBoundContext(sender, e);
        }
    }
}
