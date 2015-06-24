using NLog;
using checkin.presentation.gui.control;
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
using System.Windows.Shapes;using checkin.core.support;
using checkin.core.events;
using checkin.core.flow;

namespace checkin.presentation.gui.page
{

    class PageOrdernoOrdernoInputDataContext : InputDataContext
    {
        public PageOrdernoOrdernoInputDataContext(Page page) : base(page) { }

        public string Orderno { get; set; }
        public string _description;
        public string Description
        {
            get { return this._description; }
            set { this._description = value; this.OnPropertyChanged("Description"); }
        }

        public override void OnSubmit()
        {
            var ev = this.Event as OrdernoInputEvent;
            ev.Orderno = this.Orderno;
            ev.OrganizationCode = AppUtil.GetCurrentResource().AuthInfo.organization_code;
            base.OnSubmit();
        }
        private Visibility _refreshModeVisibility;
        public Visibility RefreshModeVisibility
        {
            get { return this._refreshModeVisibility; }
            set { this._refreshModeVisibility = value; this.OnPropertyChanged("RefreshModeVisibility"); }
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
                var organization_code = AppUtil.GetCurrentResource().AuthInfo.organization_code;
                ctx.Description = "(“ü—Í—á:" + organization_code + "0101010101)";
                ctx.Description = "Žó•t”Ô†‚ð“ü—Í‚µ‚Ä‚­‚¾‚³‚¢";
                if (data != null && data.order_no != null)
                    orderno = data.order_no;
                else
                    orderno = organization_code;
                this.KeyPad.Text = orderno;
            }

            if (!AppUtil.GetCurrentResource().RefreshMode)
            {
                ctx.RefreshModeVisibility = Visibility.Hidden;
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

        private async void OnGotoWelcome(object sender, RoutedEventArgs e)
        {
            e.Handled = true;
            var ctx = this.DataContext as InputDataContext;
            await ProgressSingletonAction.ExecuteWhenWaiting(ctx, async () =>
            {
                AppUtil.GotoWelcome(this);
            });
        }
    }
}
