using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Globalization;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Controls.Primitives;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace QR.presentation.gui.control
{
    public enum KeyPadPreviewType
    {
        raw,
        password
    }

    public class KeyPadPopupContext : INotifyPropertyChanged
    {
        private string _InputString;

        public string InputString
        {
            get { return this._InputString; }
            set { this._InputString = value; this.OnPropertyChanged("InputString"); }
        }

        private KeyPadPreviewType _previewType;
        public KeyPadPreviewType PreviewType
        {
            get
            {
                return this._previewType;
            }
            set
            {
                this._previewType = value;
                this.OnPropertyChanged("PreviewType");
            }
        }

        public event PropertyChangedEventHandler PropertyChanged;
        public void OnPropertyChanged(string name)
        {
            if (this.PropertyChanged != null)
            {
                this.PropertyChanged(this, new PropertyChangedEventArgs(name));
            }
        }
        //public bool EnableDebug { get; set; }
    }

    //[ValueConversion(typeof(string),typeof(string))]
    public class StringToStarConverter : IValueConverter
    {
        public object Convert(object value, Type targetType, object paramater, CultureInfo cu)
        {
            if (value == null)
                return "";
            return new String((value as string).Select(c => '*').ToArray<char>());
        }

        public object ConvertBack(object value, Type targetType, object paramater, CultureInfo cu)
        {
            if (value == null)
                return "";
            throw new InvalidOperationException("one direction!!");
        }
    }

    /// <summary>
    /// KeyPad.xaml の相互作用ロジック
    /// </summary>
    public partial class KeyPad : UserControl
    {            
        public KeyPad()
        {
            InitializeComponent();
            this.DataContext = new KeyPadPopupContext();
        }
                
        public static readonly RoutedEvent KeyPadFinishEvent = EventManager.RegisterRoutedEvent(
            "KeyPadFinish", RoutingStrategy.Bubble, typeof(RoutedEventHandler), typeof(KeyPad));

        public event RoutedEventHandler KeyPadFinish
        {
            add { AddHandler(KeyPadFinishEvent, value); }
            remove { RemoveHandler(KeyPadFinishEvent, value); }
        }

        public string InputString { get {
            var ctx = this.DataContext as KeyPadPopupContext;
            return ctx.InputString;
        }}

        void RaiseKeyPadFinishEvent()
        {
            var e = new RoutedEventArgs(KeyPad.KeyPadFinishEvent);
            RaiseEvent(e);
        }


        private void OnKeyDownHandler(object sender, KeyEventArgs e)
        {
            if (e.Key == Key.Return)
            {
                this.Dispatcher.InvokeAsync(() =>
                {
                    var v = (sender as TextBox).Text;
                    (this.DataContext as KeyPadPopupContext).InputString = v;
                    RaiseKeyPadFinishEvent();
                });
            }
        }
    }
}

