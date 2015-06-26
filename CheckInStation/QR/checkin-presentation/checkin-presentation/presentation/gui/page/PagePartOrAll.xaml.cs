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
    class PartOrAllDataContext : InputDataContext
    {
        public PartOrAllDataContext(Page page) : base(page) { }
        public int PrintCount { get; set; }
        private Visibility _refreshModeVisibility;
        public Visibility RefreshModeVisibility
        {
            get { return this._refreshModeVisibility; }
            set { this._refreshModeVisibility = value; this.OnPropertyChanged("RefreshModeVisibility"); }
        }
        public override void OnSubmit()
        {
            var ev = this.Event as PartOrAllEvent;
            ev.PrintCount = this.PrintCount;
            base.OnSubmit();
        }
    }

    /// <summary>
    /// PageOneOrAll.xaml の相互作用ロジック
    /// </summary>
    public partial class PagePartOrAll : Page
    {
        private Logger logger = LogManager.GetCurrentClassLogger();
        public PagePartOrAll()
        {
            InitializeComponent();
            this.DataContext = this.CreateDataContext();
        }

        private object CreateDataContext()
        {
            return new PartOrAllDataContext(this)
            {
                Broker = AppUtil.GetCurrentBroker(),
                Event = new PartOrAllEvent(),
                RefreshModeVisibility = Visibility.Hidden,
            };
        }

        private async void OnLoaded(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as PartOrAllDataContext;
            if (AppUtil.GetCurrentResource().RefreshMode)
            {
                (this.DataContext as PartOrAllDataContext).RefreshModeVisibility = Visibility.Visible;
            }
            await ctx.PrepareAsync().ConfigureAwait(true);
        }

        private void Button_Click_Part(object sender, RoutedEventArgs e)
        {
            e.Handled = true;
            (this.DataContext as PartOrAllDataContext).PrintCount = 0;
            //((this.DataContext as PartOrAllDataContext).Case.PresentationChanel as PartOrAllEvent).PrintCount = 0;
            this.OnSubmitWithBoundContext(sender, e);

        }

        private void Button_Click_All(object sender, RoutedEventArgs e)
        {
            e.Handled = true;
            (this.DataContext as PartOrAllDataContext).PrintCount = 1;
            //((this.DataContext as PartOrAllDataContext).Case.PresentationChanel as PartOrAllEvent).PrintCount = 1;
            this.OnSubmitWithBoundContext(sender, e);
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

        private async void OnGotoWelcome(object sender, RoutedEventArgs e)
        {
            e.Handled = true;
            var ctx = this.DataContext as InputDataContext;
            await ProgressSingletonAction.ExecuteWhenWaiting(ctx, async () =>
            {
                AppUtil.GotoWelcome(this);
            });
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
