using NLog;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;
using System.Printing;
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

namespace QR.presentation.gui.page{


    class HomeMenuDataContext : ViewModel
    {

        // TODO:  viewmodel作成 Printer設定のpopup. 
        public ObservableCollection<PrintQueue> AvailablePrinters { get; set; }        
        private string _selectedPrinterName;
        public string SelectedPrinterName {
            get { return this._selectedPrinterName; }
            set { this._selectedPrinterName = value; this.OnPropertyChanged("SelectedPrinterName"); }
        }
        private bool _isPrinterPopupOpen;
        public bool IsPrinterPopupOpen
        {
            get { return this._isPrinterPopupOpen; }
            set { this._isPrinterPopupOpen = value; this.OnPropertyChanged("IsPrinterPopupOpen");}
        }

        public ObservableCollection<UnitPair<Style>> AvailableWindowStyles { get; set; }
        private UnitPair<Style> _selectedWindowStyle;
        public UnitPair<Style> SelectedWindowStyle
        {
            get { return this._selectedWindowStyle; }
            set { this._selectedWindowStyle = value; this.OnPropertyChanged("SelectedWindowStyle");}
        }

        private bool _isWindowPopupOpen;
        public bool IsWindowPopupOpen
        {
            get { return this._isWindowPopupOpen; }
            set { this._isWindowPopupOpen = value; this.OnPropertyChanged("IsWindowPopupOpen"); }
        }
    }


    /// <summary>
    /// Interaction logic for PageHomeMenu.xaml
    /// </summary>
    public partial class PageHomeMenu : Page//, IDataContextHasCase
    {
        private Logger logger = LogManager.GetCurrentClassLogger();
        public PageHomeMenu()
        {
            InitializeComponent();
            //PasswordBox is not Dependency Property. so.
            this.DataContext = this.CreateDataContext();
        }

        private void Button_Click(object sender, RoutedEventArgs e)
        {
            //別windowで起動
            e.Handled = true;
            var stylePair = (this.DataContext as HomeMenuDataContext).SelectedWindowStyle;
            var win = new MainWindow() { Style = stylePair.Value };
            win.Show();
            //this.NavigationService.Navigate(new PageAuthInput());
        }

        private object CreateDataContext()
        {
            var printing = AppUtil.GetCurrentResource().TicketImagePrinting;
            ObservableCollection<PrintQueue> printers = CandidateCreator.AvailablePrinterCandidates(printing);
            ObservableCollection<UnitPair<Style>> windowStyles = CandidateCreator.WindowStyleCandidates(this);

            return new HomeMenuDataContext()
            {
                AvailablePrinters = printers,
                SelectedPrinterName = printing.DefaultPrinter.FullName,
                AvailableWindowStyles = windowStyles,
                SelectedWindowStyle = windowStyles[0]
            };
        }

        private void OnPrinterSelected(object sender, SelectionChangedEventArgs e)
        {
            var selected = (sender as ListBox).SelectedItem as PrintQueue;
            AppUtil.GetCurrentResource().TicketImagePrinting.DefaultPrinter = selected;
            var ctx = (this.DataContext as HomeMenuDataContext);
            ctx.SelectedPrinterName = selected.FullName;
            ctx.IsPrinterPopupOpen = false;
        }

        private void OnWindowStyleSelected(object sender, SelectionChangedEventArgs e)
        {
            var selected = (sender as ListBox).SelectedItem as UnitPair<Style>;
            var ctx = (this.DataContext as HomeMenuDataContext);
            ctx.SelectedWindowStyle = selected;
            ctx.IsWindowPopupOpen = false;
        }
    }
}
