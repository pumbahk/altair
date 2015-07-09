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
    /// Interaction logic for PagePrinting.xaml
    /// </summary>
    public partial class PagePrinting2 : Page//, IDataContextHasCase
    {
        private Logger logger = LogManager.GetCurrentClassLogger();

        public PagePrinting2()
        {
            InitializeComponent();
            this.DataContext = this.CreateDataContext();
        }

        private InputDataContext CreateDataContext()
        {
            var resource = AppUtil.GetCurrentResource();
            var ctx = new PagePrintingDataContext()
            {
                Broker = AppUtil.GetCurrentBroker(),
                AdImage = resource.AdImageCollector.GetImage(),
            };
            ctx.SubDescription = ctx.SubDescriptionFromStatus(ctx.Status);

            ctx.Event = new PrintingEvent()
            {
                CurrentDispatcher = this.Dispatcher,
                StatusInfo = ctx as IPrintingStatusInfo,
            };
            ctx.PropertyChanged += ctx_PropertyChanged;
            var case_ = ctx.Case as CasePrintForAll;
            if (case_ != null)
            {
                ctx.TotalPrinted = case_.DataCollection.collection.Where(o => o.printed_at == null).Count();
            }
            //ctx.TotalPrinted = 0;
            //ctx.FinishedPrinted = 0;
            return ctx;
        }

        void ctx_PropertyChanged(object sender, PropertyChangedEventArgs e)
        {
            if (e.PropertyName == "Status")
            {
                var ctx = sender as PagePrintingDataContext;
                ctx.SubDescription = ctx.SubDescriptionFromStatus(ctx.Status);
            }
        }

        private async void OnLoaded(object sender, RoutedEventArgs e)
        {
            this.LoadingAdorner.ShowAdorner();
            await (this.DataContext as PagePrintingDataContext).PrepareAsync();
            await OnPrintingStart();
        }

        private async Task OnPrintingStart()
        {
            var ctx = this.DataContext as PagePrintingDataContext;

            await ProgressSingletonAction.ExecuteWhenWaiting(ctx, async () =>
            {
                ctx.Status = PrintingStatus.requesting;
                logger.Trace("** status is requesting".WithMachineName());
                var case_ = await ctx.SubmitAsync();
                ctx.TreatErrorMessage();
                AppUtil.GetNavigator().NavigateToMatchedPage(case_, this);
            });
        }
    }
}

