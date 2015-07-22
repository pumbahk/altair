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
    class WelcomeDataContext: InputDataContext
    {
        public WelcomeDataContext(Page page) : base(page) { }

        public int PrintType { get; set; }
        private Visibility _refreshModeVisibility;
        public Visibility RefreshModeVisibility
        {
            get { return this._refreshModeVisibility; }
            set { this._refreshModeVisibility = value; this.OnPropertyChanged("RefreshModeVisibility"); }
        }
        public override void OnSubmit()
        {
            var ev = this.Event as WelcomeEvent;
            ev.PrintType = this.PrintType;
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
            return new WelcomeDataContext(this)
            {
                Broker = AppUtil.GetCurrentBroker(),
                Event = new WelcomeEvent(),
                RefreshModeVisibility = Visibility.Hidden,
            };
        }

        private async void OnLoaded(object sender, RoutedEventArgs e)
        {
            if (AppUtil.GetCurrentResource().RefreshMode)
            {
                (this.DataContext as WelcomeDataContext).RefreshModeVisibility = Visibility.Visible;
            }
        }

        private void Button_Click_QR(object sender, RoutedEventArgs e)
        {
            e.Handled = true;
            (this.DataContext as WelcomeDataContext).PrintType = 0;
            this.OnSubmitWithBoundContext(sender, e);
            
        }

        private void Button_Click_Code(object sender, RoutedEventArgs e)
        {
            e.Handled = true;
            (this.DataContext as WelcomeDataContext).PrintType = 1;
            this.OnSubmitWithBoundContext(sender, e);
        }

        private async void OnSubmitWithBoundContext(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as InputDataContext;

            await ProgressSingletonAction.ExecuteWhenWaiting(ctx, async () =>
            {
                var case_ = await ctx.SubmitAsync(); //入力値チェック
                ctx.TreatErrorMessage();
                AppUtil.GetNavigator().NavigateToMatchedPage(case_, this);
            });
        }
    }
}
