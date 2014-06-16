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
using checkin.core.support;
using NLog;

//model ::xxx
using checkin.core.message;

namespace checkin.presentation.gui.page
{
    /// <summary>
    /// Interaction logic for PagePrintingConfirm.xaml
    /// </summary>
    public partial class PagePrintingConfirm : Page
    {
        public PagePrintingConfirm()
        {
            InitializeComponent();
            this.DataContext = this.CreateDataContext();
        }

        private InputDataContext CreateDataContext()
        {
            return new InputDataContext(this) { Broker = AppUtil.GetCurrentBroker() };;
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

        private void OnSubmitWithBoundContext(object sender, RoutedEventArgs e)
        {
            e.Handled = true;
            var broker = AppUtil.GetCurrentBroker();
            var case_ = broker.FlowManager.Peek().Case;
            AppUtil.GetNavigator().NavigateToMatchedPage(case_, this);
        }
    }
}
