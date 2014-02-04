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
        public ObservableCollection<PrintQueue> AvailablePrinters { get; set; }        
        private string _selectedPrinterName;
        public string SelectedPrinterName {
            get { return this._selectedPrinterName; }
            set { this._selectedPrinterName = value; this.OnPropertyChanged("SelectedPrinterName"); }
        }
        private bool _isPopupOpen;
        public bool IsPopupOpen
        {
            get { return this._isPopupOpen; }
            set { this._isPopupOpen = value; this.OnPropertyChanged("IsPopupOpen");}
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
            e.Handled = true;
            this.NavigationService.Navigate(new PageAuthInput());
        }

        private object CreateDataContext()
        {
            var printers = new ObservableCollection<PrintQueue>();
            var printing = AppUtil.GetCurrentResource().TicketImagePrinting;
            printers.Add(printing.DefaultPrinter);
            foreach (var q in printing.AvailablePrinters())
            {
                if (printing.DefaultPrinter.FullName != q.FullName)
                {
                    printers.Add(q);
                }
            }
            return new HomeMenuDataContext()
            {
                AvailablePrinters = printers,
                SelectedPrinterName = printing.DefaultPrinter.FullName
            };
        }

        private void OnPrinterSelected(object sender, SelectionChangedEventArgs e)
        {
            var selected = (sender as ListBox).SelectedItem as PrintQueue;
            AppUtil.GetCurrentResource().TicketImagePrinting.DefaultPrinter = selected;
            var ctx = (this.DataContext as HomeMenuDataContext);
            ctx.SelectedPrinterName = selected.FullName;
            ctx.IsPopupOpen = false;
        }
    }
}
