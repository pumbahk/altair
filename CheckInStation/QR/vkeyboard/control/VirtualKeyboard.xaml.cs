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

namespace vkeyboard.control
{
    /// <summary>
    /// vkeyboard.xaml の相互作用ロジック
    /// </summary>
    public partial class VirtualKeyboard : UserControl
    {
        public VirtualKeyboard()
        {
            InitializeComponent();
        }

        private static void OnTextChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            var ctl = d as VirtualKeyboard;
            if (ctl != null)
            {
                ctl.Input.Text = ctl.Text;
            }
        }

        public static readonly DependencyProperty TextProperty =
        DependencyProperty.Register("Text", typeof(string), typeof(VirtualKeyboard),
        new FrameworkPropertyMetadata(String.Empty,
            new PropertyChangedCallback(OnTextChanged)));

        public string Text
        {
            get { return (string)this.GetValue(TextProperty); }
            set { this.SetValue(TextProperty, value); }
        }

        public static readonly DependencyProperty DescriptionProperty =
        DependencyProperty.Register("Description", typeof(string), typeof(VirtualKeyboard),
        new UIPropertyMetadata(""));


        public string Description
        {
            get { return (string)this.GetValue(DescriptionProperty); }
            set { this.SetValue(DescriptionProperty, value); }
        }

        public static readonly DependencyProperty DisableTenKeyProperty =
        DependencyProperty.Register("DisableTenKey", typeof(bool), typeof(VirtualKeyboard),
        new FrameworkPropertyMetadata(false));

        public bool DisableTenKey
        {
            get { return (bool)this.GetValue(DisableTenKeyProperty); }
            set { this.SetValue(DisableTenKeyProperty, value); }
        }

        public static readonly DependencyProperty DisableAlphabetKeyProperty =
        DependencyProperty.Register("DisableAlphabetKey", typeof(bool), typeof(VirtualKeyboard),
        new FrameworkPropertyMetadata(false));

        public bool DisableAlphabetKey
        {
            get { return (bool)this.GetValue(DisableAlphabetKeyProperty); }
            set { this.SetValue(DisableAlphabetKeyProperty, value); }
        }

        public static readonly RoutedEvent VirtualkeyboardFinishEvent = EventManager.RegisterRoutedEvent(
       "VirtualkeyboardFinish", RoutingStrategy.Bubble, typeof(RoutedEventHandler), typeof(VirtualKeyboard));

        public event RoutedEventHandler VirtualkeyboardFinish
        {
            add { AddHandler(VirtualkeyboardFinishEvent, value); }
            remove { RemoveHandler(VirtualkeyboardFinishEvent, value); }
        }

        void RaiseVirtualkeyboardFinishEvent()
        {
            var e = new RoutedEventArgs(VirtualKeyboard.VirtualkeyboardFinishEvent);
            RaiseEvent(e);
        }

        private void OnKeyDownHandler(object sender, KeyEventArgs e)
        {
            if (e.Key == Key.Return)
            {
                this.Dispatcher.InvokeAsync(() =>
                {
                    this.Text = this.Input.Text;
                    RaiseVirtualkeyboardFinishEvent();
                });
            }
        }

        private void PlaceHolder_MouseEnter(object sender, MouseEventArgs e)
        {
            this.Input.Input.Focus();
            e.Handled = true;
        }
        
        private void Container_Loaded(object sender, RoutedEventArgs e)
        {
            this.Input.Input.Focus();
            e.Handled = true;
        }

        private void Container_MouseEnter(object sender, MouseEventArgs e)
        {
            this.Input.Input.Focus();
            e.Handled = true;
        }

    }
}
