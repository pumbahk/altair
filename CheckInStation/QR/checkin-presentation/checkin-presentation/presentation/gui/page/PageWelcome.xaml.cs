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
using NLog;
using checkin.core.events;
using checkin.core.flow;

namespace checkin.presentation.gui.page
{
    class PageWelcomeDataContext: InputDataContext
    {
        public override void OnSubmit()
        {
            var ev = this.Event as WelcomeEvent;
            base.OnSubmit();
        }
    }

    /// <summary>
    /// Page1.xaml の相互作用ロジック
    /// </summary>
    public partial class PageWelcome : Page
    {
        private Logger logger = LogManager.GetCurrentClassLogger();
        public PageWelcome()
        {
            InitializeComponent();
            this.DataContext = this.CreateDataContext();
        }

        private object CreateDataContext()
        {
            return new PageWelcomeDataContext()
            {
                Broker = AppUtil.GetCurrentBroker(),
                Event = new WelcomeEvent(),
            };
        }

        private async void Button_Click_QR(object sender, RoutedEventArgs e)
        {

            var ctx = this.DataContext as InputDataContext;
            await ProgressSingletonAction.ExecuteWhenWaiting(ctx, async () =>
            {
                var case_ = await ctx.SubmitAsync(); //入力値チェック
                ctx.TreatErrorMessage();
                AppUtil.GetNavigator().NavigateToMatchedPage(case_, this);
            });
            /*
            this.Dispatcher.Invoke(() =>
            {
                var nextPage = new PageQRCodeInput();
                var service = this.NavigationService;
                if (service != null)
                {
                    service.Navigate(nextPage);
                    nextPage.Dispatcher.Invoke(() =>
                    {
                        (nextPage.DataContext as InputDataContext).PassingErrorMessage("");
                    }
                        );
                }
                else
                {
                    logger.Info("previous:NavigationService is not found");
                }
            });
              * */
            
        }

        private void Button_Click_Code(object sender, RoutedEventArgs e)
        {

        }
    }
}
