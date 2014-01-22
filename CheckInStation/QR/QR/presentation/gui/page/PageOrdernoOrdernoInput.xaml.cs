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

namespace QR.presentation.gui.page
{

    class PageOrdernoOrdernoInputDataContext : InputDataContext
    {
        public override void OnSubmit()
        {
            var ev = this.Event as IInternalEvent;
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
            return new PageOrdernoOrdernoInputDataContext()
            {
                Broker = AppUtil.GetCurrentBroker(),
                Event = new OrdernoInputEvent()
            };
        }

        private async void OnLoaded(object sender, RoutedEventArgs e)
        {
            await(this.DataContext as PageOrdernoOrdernoInputDataContext).PrepareAsync().ConfigureAwait(false);
        }

        private async void OnSubmitWithBoundContext(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as InputDataContext;
            var case_ = await ctx.SubmitAsync();
            ctx.TreatErrorMessage();
            AppUtil.GetNavigator().NavigateToMatchedPage(case_, this);
        }
    }
}
