﻿using NLog;
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
using System.Configuration;
using checkin.core.support;
using checkin.presentation.support;
using checkin.core.events;
using checkin.core.models;
using checkin.core;
using checkin.presentation.gui.control;

namespace checkin.presentation.gui.page{


    class HomeMenuDataContext : ViewModel
    {

        // TODO:  viewmodel作成 Printer設定のpopup. 
        public ObservableCollection<PrintQueue> AvailablePrinters { get; set; }        
        private string _selectedPrinterName;
        public string SelectedPrinterName {
            get { return this._selectedPrinterName; }
            set { this._selectedPrinterName = value; this.OnPropertyChanged("SelectedPrinterName"); }
        }

        private string _selectedServerUrl;
        public string SelectedServerUrl
        {
            get { return this._selectedServerUrl; }
            set { this._selectedServerUrl = value; this.OnPropertyChanged("SelectedServerUrl"); }
        }

        public ObservableCollection<UnitPair<Style>> AvailableWindowStyles { get; set; }
        private UnitPair<Style> _selectedWindowStyle;
        public UnitPair<Style> SelectedWindowStyle
        {
            get { return this._selectedWindowStyle; }
            set { this._selectedWindowStyle = value; this.OnPropertyChanged("SelectedWindowStyle"); }
        }

        public ObservableCollection<UnitPair<FlowDefinitionType>> AvailableFlowStyles { get; set; }
        private UnitPair<FlowDefinitionType> _selectedFlowStyle;
        public UnitPair<FlowDefinitionType> SelectedFlowStyle
        {
            get { return this._selectedFlowStyle; }
            set { this._selectedFlowStyle = value; this.OnPropertyChanged("SelectedFlowStyle"); }
        }

        private string _multiPrintMode;
        public string MultiPrintMode
        {
            get { return this._multiPrintMode; }
            set { this._multiPrintMode = value; this.OnPropertyChanged("MultiPrintMode"); }
        }

        private string _loadedQRCode;
        public string LoadedQRCode {
            get { return this._loadedQRCode; }
            set { this._loadedQRCode = value; this.OnPropertyChanged("LoadedQRCode");}
        }
        private string _TestStatusDescription;
        public string TestStatusDescription
        {
            get { return this._TestStatusDescription; }
            set { this._TestStatusDescription = value; this.OnPropertyChanged("TestStatusDescription"); }
        }

        private string _selectedImage;
        public string SelectedImage
        {
            get { return this._selectedImage; }
            set { this._selectedImage = value; this.OnPropertyChanged("SelectedImage"); }
        }

        public string ApplicationVersion { get; set; }
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
            //別windowで起動(ここで最初に表示するページを指定している)
            e.Handled = true;
            var ctx = this.DataContext as HomeMenuDataContext;
            var stylePair = ctx.SelectedWindowStyle;

            // set Image for QR input instruction
            var defaultFile = AppUtil.GetCurrentResource().QRInputImage;
            AppUtil.GetCurrentResource().Authentication.LoginURL = ctx.SelectedServerUrl;
            if (ctx.SelectedImage == defaultFile || System.IO.File.Exists(ctx.SelectedImage))
            {
                AppUtil.GetCurrentResource().QRInputImage = ctx.SelectedImage;
            }

            //アプリケーションのwindow表示
            AppUtil.init(ctx.SelectedFlowStyle.Value);
            var win = new MainWindow() {
                Style = stylePair.Value,
                ShowsNavigationUI=false
            };
            win.Show();

            //ホームメニューのwindow終了
            var currentWindow = Window.GetWindow(this);
            if (currentWindow != null)
            {
                currentWindow.Close();
            }
        }

        private void SelectImageFile(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as HomeMenuDataContext;

            // Create file dialog instance
            var dialog = new System.Windows.Forms.OpenFileDialog();
 
			// file filter
            dialog.Filter = "画像ファイル (*.PNG;*.JPG)|*.PNG;*.JPG|全てのファイル (*.*)|*.*";
            
            // manage the opacity of parent element
            MenuDialog parentPanel = this.FindName("MenuDialogQRInputImage") as MenuDialog;
            parentPanel.IsOpen = false;
			// show dialog
            if (dialog.ShowDialog() == System.Windows.Forms.DialogResult.OK)
			{
				// Set File to SelectedImage property to use later
                ctx.SelectedImage = dialog.FileName;
			}
            parentPanel.IsOpen = true;
        }

        private void SelectDefaultImageFile(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as HomeMenuDataContext;
            ctx.SelectedImage = "/Resource/qr_input.png";
        }

        private object CreateDataContext()
        {
            var resource = AppUtil.GetCurrentResource();
            var printing = resource.TicketPrinting;
            ObservableCollection<PrintQueue> printers = CandidateCreator.AvailablePrinterCandidates(printing);
            ObservableCollection<UnitPair<Style>> windowStyles = CandidateCreator.WindowStyleCandidates(this);
            ObservableCollection<UnitPair<FlowDefinitionType>> flowStyles = CandidateCreator.FlowStyleCandidates();

            var ctx = new HomeMenuDataContext()
            {
                AvailablePrinters = printers,
                SelectedPrinterName = printing.DefaultPrinter.FullName,
                AvailableWindowStyles = windowStyles,
                AvailableFlowStyles = flowStyles,
                SelectedWindowStyle = windowStyles[0],
                SelectedFlowStyle = flowStyles.FirstOrDefault(o => o.Value == (FlowDefinitionType)Enum.Parse(typeof(FlowDefinitionType), ConfigurationManager.AppSettings["application.flow"])),
                SelectedServerUrl = resource.Authentication.LoginURL,
                SelectedImage = resource.QRInputImage,
                LoadedQRCode = "<準備中>",
                TestStatusDescription = "<準備中>",
                ApplicationVersion=ApplicationVersion.GetApplicationInformationalVersion()
            };

            if (AppUtil.GetCurrentResource().MultiPrintMode)
            {
                ctx.MultiPrintMode = "On";
            }
            else
            {
                ctx.MultiPrintMode = "Off";
            } 
            return ctx;
        }

        private void OnPrinterSelected(object sender, SelectionChangedEventArgs e)
        {
            var selected = (sender as ListBox).SelectedItem as PrintQueue;
            AppUtil.GetCurrentResource().TicketPrinting.DefaultPrinter = selected;
            var ctx = (this.DataContext as HomeMenuDataContext);
            ctx.SelectedPrinterName = selected.FullName;
        }

        private void OnWindowStyleSelected(object sender, SelectionChangedEventArgs e)
        {
            var selected = (sender as ListBox).SelectedItem as UnitPair<Style>;
            var ctx = (this.DataContext as HomeMenuDataContext);
            ctx.SelectedWindowStyle = selected;
        }

        private void OnFlowStyleSelected(object sender, SelectionChangedEventArgs e)
        {
            var selected = (sender as ListBox).SelectedItem as UnitPair<FlowDefinitionType>;
            var ctx = (this.DataContext as HomeMenuDataContext);
            ctx.SelectedFlowStyle = selected;
        }



        private void MenuDialogTesting_OnTestPrinting(object sender, RoutedEventArgs e)
        {
            var resource = AppUtil.GetCurrentResource();
            var printing = resource.TicketPrinting;

            var xaml = Testing.ReadFromEmbeddedFile("checkin_core.Resources.sample.qr.svg");
            var data = TicketImageData.XamlTicketData("-1", "-1", xaml);

            var ev = new EmptyEvent();
            ev.CurrentDispatcher = this.Dispatcher;
            var ctx = (this.DataContext as HomeMenuDataContext);

            ctx.TestStatusDescription = "印刷中";

            printing.BeginEnqueue();
            try
            {
               printing.EnqueuePrinting(data, ev);
            }
            catch (Exception ex)
            {
                logger.WarnException("test printing:".WithMachineName(), ex);
            }
            printing.EndEnqueue();

            ctx.TestStatusDescription = "印刷完了しました";
        }

        private void _PrintTestQRInput_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.Key == Key.Return)
            {
                var ctx = (this.DataContext as HomeMenuDataContext);
                var tbox = sender as TextBox;
                ctx.LoadedQRCode = tbox.Text;
                tbox.SelectedText = "";
            }
        }

        private void Button_Click_1(object sender, RoutedEventArgs e)
        {
            //これでもだめらしい.
            var tbox = WpfUtilEx.FindVisualChild<TextBox>(this.MenuDialogQRTesting);
            if (tbox != null)
            {
                tbox.Focus();
            }
        }

        private void CheckBox_Checked(object sender, RoutedEventArgs e)
        {
            checkMultiPrintMode(sender, e);
        }

        private void CheckBox_Unchecked(object sender, RoutedEventArgs e)
        {
            checkMultiPrintMode(sender, e);
        }

        private void checkMultiPrintMode(object sender, RoutedEventArgs e)
        {
            var checkBox = sender as CheckBox;
            var ctx = (this.DataContext as HomeMenuDataContext);
            if ((bool)checkBox.IsChecked)
            {
                ctx.MultiPrintMode = "On";
            }
            else
            {
                ctx.MultiPrintMode = "Off";
            }
            AppUtil.GetCurrentResource().MultiPrintMode = (bool)checkBox.IsChecked;
        }
    }
}
