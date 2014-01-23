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

    class PageConfirmOneDataContext : InputDataContext
    {
        public override void OnSubmit()
        {
            var ev = this.Event as InternalEvent;
            base.OnSubmit();
        }
    }


    /// <summary>
    /// Interaction logic for PageConfirmOne.xaml
    /// </summary>
    public partial class PageConfirmOne : Page//, IDataContextHasCase
    {
        private Logger logger = LogManager.GetCurrentClassLogger();

        public PageConfirmOne()
        {
            InitializeComponent();
            //PasswordBox is not Dependency Property. so.
            this.DataContext = this.CreateDataContext();
        }

        private InputDataContext CreateDataContext()
        {
            return new PageConfirmOneDataContext(this.PasswordInput)
            {
                Broker = AppUtil.GetCurrentBroker(),
                Event = new IInternalEvent()
            };
        }

        private async void OnLoaded(object sender, RoutedEventArgs e)
        {
            await(this.DataContext as PageConfirmOneDataContext).PrepareAsync().ConfigureAwait(false);
        }

        private async void OnSubmitWithBoundContext(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as InputDataContext;
            var case_ = await ctx.SubmitAsync();
            ctx.TreatErrorMessage();
            AppUtil.GetNavigator().NavigateNextPage(case_, this);
        }
    }
}
