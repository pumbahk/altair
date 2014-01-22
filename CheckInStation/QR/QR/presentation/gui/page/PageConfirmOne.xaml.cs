using NLog;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
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
        public string InputString { get; set;}
        public ObservableCollection<UnitPair> Candidates {get;set;}
        public override void OnSubmit()
        {
            var ev = this.Event as QRInputEvent;
            ev.PrintUnitString = this.InputString;
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
            this.DataContext = this.CreateDataContext();
        }

        private InputDataContext CreateDataContext()
        {
            var candidates = new ObservableCollection<UnitPair>();
            candidates.Add(new UnitPair("このチケット１枚を発券", PrintUnit.one.ToString()));
            candidates.Add(new UnitPair("同じ注文番号のチケットをまとめて発券", PrintUnit.all.ToString()));
            return new PageConfirmOneDataContext()
            {
                Candidates = candidates,
                Broker = AppUtil.GetCurrentBroker(),
                Event = new QRInputEvent()
            };
        }

        private async void OnLoaded(object sender, RoutedEventArgs e)
        {
            await (this.DataContext as PageConfirmOneDataContext).PrepareAsync().ConfigureAwait(false);
        }

        private async void OnSubmitWithBoundContext(object sender, SelectionChangedEventArgs e)
        {
            var box = sender as ListBox;
            if (box.SelectedItem != null)
            {
                var pair = box.SelectedItem as UnitPair;
                var ctx = this.DataContext as PageConfirmOneDataContext;
                ctx.InputString = pair.Value;

                //submit
                var case_ = await ctx.SubmitAsync();
                ctx.TreatErrorMessage();
                AppUtil.GetNavigator().NavigateToMatchedPage(case_, this);
            }
        }

        private async void OnBackwardWithBoundContext(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as InputDataContext;
            var case_ = await ctx.BackwardAsync();
            ctx.TreatErrorMessage();
            AppUtil.GetNavigator().NavigateToMatchedPage(case_, this);
        }
    }
}
