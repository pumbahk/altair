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

namespace QR.presentation.gui.page
{
    class InputStrategyDataContext : InputDataContext
    {
        public string inputString { get; set; }
    }

    /// <summary>
    /// Interaction logic for PageInputStrategySelect.xaml
    /// </summary>
    public partial class PageInputStrategySelect : Page
    {
        public PageInputStrategySelect()
        {
            InitializeComponent();
            this.DataContext = this.CreateDataContext();
        }

        private InputDataContext CreateDataContext()
        {
            return new InputStrategyDataContext() { Broker = AppUtil.GetCurrentBroker(), Event = new SelectInputStragetyEvent() };
        }

        private async void OnLoaded(object sender, RoutedEventArgs e)
        {
            await (this.DataContext as InputStrategyDataContext).PrepareAsync().ConfigureAwait(false);
        }

        private async void OnSubmitWithBoundContext(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as InputStrategyDataContext;
            var case_ = await ctx.SubmitAsync();
            ctx.TreatErrorMessage();
            AppUtil.GetNavigator().NavigateNextPage(case_, this);
        }
    }
}
