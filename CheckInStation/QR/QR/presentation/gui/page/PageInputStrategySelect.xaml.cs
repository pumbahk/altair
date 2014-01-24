using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
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

    class UnitPair
    {
        public UnitPair(){}
        public UnitPair(string k, string v) { this.Key = k; this.Value = v; }
        public string Key { get; set; }
        public string Value { get; set; }
    }

    class InputStrategyDataContext : InputDataContext
    {
        public string InputString { get; set;}
        public ObservableCollection<UnitPair> Candidates {get;set;}

        public override void OnSubmit()
        {
            var ev = this.Event as SelectInputStragetyEvent;
            ev.InputUnitString = this.InputString;
            base.OnSubmit();
        }
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
            var candidates = new ObservableCollection<UnitPair>();
            candidates.Add(new UnitPair("QRで認証", InputUnit.qrcode.ToString()));
            candidates.Add(new UnitPair("注文番号を入力して認証", InputUnit.order_no.ToString()));
            return new InputStrategyDataContext() { 
                Candidates = candidates,
                Broker = AppUtil.GetCurrentBroker(), 
                Event = new SelectInputStragetyEvent() };
        }

        private async void OnLoaded(object sender, RoutedEventArgs e)
        {
            await (this.DataContext as InputStrategyDataContext).PrepareAsync().ConfigureAwait(false);
        }

        private async void OnSubmitWithBoundContext(object sender, SelectionChangedEventArgs e)
        {
            var box = sender as ListBox;
            if (box.SelectedItem != null)
            {
                var ctx = this.DataContext as InputStrategyDataContext;
                await ProgressSingletonAction.ExecuteWhenWaiting(ctx, async () =>
                {
                    var pair = box.SelectedItem as UnitPair;
                    (this.DataContext as InputStrategyDataContext).InputString = pair.Value;

                    //submit
                    var case_ = await ctx.SubmitAsync();
                    ctx.TreatErrorMessage();
                    AppUtil.GetNavigator().NavigateToMatchedPage(case_, this);
                });
            }
        }
    }
}
