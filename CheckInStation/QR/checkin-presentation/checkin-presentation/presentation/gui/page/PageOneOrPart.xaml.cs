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
    class OneOrPartDataContext : InputDataContext
    {
        public OneOrPartDataContext(Page page) : base(page) { }
        public int PrintCount { get; set; }
        private Visibility _refreshModeVisibility;
        public Visibility RefreshModeVisibility
        {
            get { return this._refreshModeVisibility; }
            set { this._refreshModeVisibility = value; this.OnPropertyChanged("RefreshModeVisibility"); }
        }
        public override void OnSubmit()
        {
            var ev = this.Event as OneOrPartEvent;
            ev.PrintCount = this.PrintCount;
            base.OnSubmit();
        }
    }

    /// <summary>
    /// PageOneOrAll.xaml の相互作用ロジック
    /// </summary>
    public partial class PageOneOrPart : Page
    {
        private Logger logger = LogManager.GetCurrentClassLogger();
        public PageOneOrPart()
        {
            InitializeComponent();
            this.DataContext = this.CreateDataContext();
        }

        private object CreateDataContext()
        {
            return new OneOrPartDataContext(this)
            {
                Broker = AppUtil.GetCurrentBroker(),
                Event = new OneOrPartEvent(),
            };
        }

        private async void OnLoaded(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as OneOrPartDataContext;
            if (!AppUtil.GetCurrentResource().RefreshMode)
            {
                (this.DataContext as OneOrPartDataContext).RefreshModeVisibility = Visibility.Hidden;
            }
            await ctx.PrepareAsync().ConfigureAwait(true);
        }

        private void Button_Click_Single(object sender, RoutedEventArgs e)
        {
            e.Handled = true;
            (this.DataContext as OneOrPartDataContext).PrintCount = 0;
            ((this.DataContext as OneOrPartDataContext).Case.PresentationChanel as OneOrPartEvent).PrintCount = 0;
            this.OnSubmitWithBoundContext(sender, e);

        }

        private void Button_Click_All(object sender, RoutedEventArgs e)
        {
            e.Handled = true;
            (this.DataContext as OneOrPartDataContext).PrintCount = 1;
            ((this.DataContext as OneOrPartDataContext).Case.PresentationChanel as OneOrPartEvent).PrintCount = 1;
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
                //(this.DataContext.Case.PresentationChanel as OneOrPartEvent).PrintCount = (this.DataContext as OneOrPartDataContext).PrintCount;
                AppUtil.GetNavigator().NavigateToMatchedPage(case_, this);
            });
        }
    }
}
