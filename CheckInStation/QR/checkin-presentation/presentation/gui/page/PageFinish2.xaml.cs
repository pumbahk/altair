using NLog;
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
using checkin.core.support;
using checkin.core.events;
using checkin.core.flow;

namespace checkin.presentation.gui.page
{

    /// <summary>
    /// Interaction logic for PageFinish.xaml
    /// </summary>
    public partial class PageFinish2 : Page//, IDataContextHasCase
    {
        private Logger logger = LogManager.GetCurrentClassLogger();

        public PageFinish2()
        {
            InitializeComponent();
            this.DataContext = this.CreateDataContext();
        }

        private InputDataContext CreateDataContext()
        {
            var resource = AppUtil.GetCurrentResource();
            var ctx = new PageFinishDataContext()
            {
                Broker = AppUtil.GetCurrentBroker(),
                Status = FinishStatus.starting
            };
            ctx.Event = new FinishEvent() { StatusInfo = ctx };
            ctx.PropertyChanged += OnStatusChangedSetRedirectCallback;
            var case_ = ctx.Case as CasePrintFinish;
            if (case_ != null)
            {
                ctx.TotalPrinted = case_.RequsetData.printed_ticket_list.Length;
            }
            return ctx;
        }

        void OnStatusChangedSetRedirectCallback(object sender, PropertyChangedEventArgs e)
        {
            var ctx = sender as PageFinishDataContext;
            if (e.PropertyName == "Status" && ctx.Status == FinishStatus.saved)
            {
                ctx.Status = FinishStatus.finished;
                this.Dispatcher.InvokeAsync(async () =>
                {
                    var waitTime = AppUtil.GetCurrentResource().WaitingTimeAfterFinish;
                    await Task.Delay(waitTime);
                    logger.Info("stop case {0}".WithMachineName(), ctx.Broker.FlowManager.Peek());
                    var case_ = await ctx.SubmitAsync();
                    ctx.TreatErrorMessage();
                    AppUtil.GetNavigator().NavigateToMatchedPage(case_, this);
                });
            }
        }

        private async void OnLoaded(object sender, RoutedEventArgs e)
        {
            await (this.DataContext as PageFinishDataContext).VerifyAsync().ConfigureAwait(false);
            // ここに来たら、再発券モードは必ず終了する。
            AppUtil.GetCurrentResource().RefreshMode = false;
        }
    }
}
