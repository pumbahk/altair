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
using checkin.core.events;

namespace checkin.presentation.gui.page
{

    class InputStrategyDataContext : InputDataContext
    {
        public string InputString { get; set;}
        public ObservableCollection<UnitStringPair> Candidates {get;set;}

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

            return new InputStrategyDataContext() { 
                Candidates = CandidateCreator.InputUnitCandidates(),
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
                    var pair = box.SelectedItem as UnitStringPair;
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
