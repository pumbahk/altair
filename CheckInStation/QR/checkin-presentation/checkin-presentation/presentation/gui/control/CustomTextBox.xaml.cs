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

namespace checkin.presentation.gui.control {
    public enum CustomTextBoxDisplayMode {
        raw,
        star
    }


    /// <summary>
    /// CustomTextBox.xaml の相互作用ロジック
    /// </summary>
    public partial class CustomTextBox : UserControl
    {

        private double padding_dx;
        public static readonly DependencyProperty DisplayModeProperty =
        DependencyProperty.Register("DisplayMode", typeof(CustomTextBoxDisplayMode), typeof(CustomTextBox),
        new FrameworkPropertyMetadata(CustomTextBoxDisplayMode.raw));

        public CustomTextBoxDisplayMode DisplayMode
        {
            get { return (CustomTextBoxDisplayMode)this.GetValue(DisplayModeProperty); }
            set { this.SetValue(DisplayModeProperty, value); }
        }

        public static readonly DependencyProperty TextProperty =
        DependencyProperty.Register("Text", typeof(string), typeof(CustomTextBox),
        new FrameworkPropertyMetadata(String.Empty));

        public string Text
        {
            get { return (string)this.GetValue(TextProperty); }
            set { this.SetValue(TextProperty, value); }
        }


        private static void OnBorderBrushChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            var ctl = d as CustomTextBox;
            if(ctl != null){
                ctl.Input.BorderBrush = ctl.BorderBrush;
            }
        }

        public new static readonly DependencyProperty BorderBrushProperty =
        DependencyProperty.Register("BorderBrush", typeof(Brush), typeof(CustomTextBox),
        new FrameworkPropertyMetadata(null, OnBorderBrushChanged));
        

        public new Brush BorderBrush
        {
            get { return (Brush)this.GetValue(BorderBrushProperty); }
            set { this.SetValue(BorderBrushProperty, value); }
        }

        private static void OnBackgroundChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            var ctl = d as CustomTextBox;
            if (ctl != null)
            {
                ctl.Input.Background = ctl.Background;
            }
        }

        public new static readonly DependencyProperty BackgroundProperty =
        DependencyProperty.Register("Background", typeof(Brush), typeof(CustomTextBox),
        new FrameworkPropertyMetadata(Brushes.White, OnBackgroundChanged));


        public new Brush Background
        {
            get { return (Brush)this.GetValue(BackgroundProperty); }
            set { this.SetValue(BackgroundProperty, value); }
        }


        private static void OnForegroundChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            var ctl = d as CustomTextBox;
            if (ctl != null)
            {
                //ctl.Input.Foreground = ctl.Foreground;
                ctl.DisplayText.Foreground = ctl.Foreground;
            }
        }

        public new static readonly DependencyProperty ForegroundProperty =
        DependencyProperty.Register("Foreground", typeof(Brush), typeof(CustomTextBox),
        new FrameworkPropertyMetadata(Brushes.Black, OnForegroundChanged));


        public new Brush Foreground
        {
            get { return (Brush)this.GetValue(ForegroundProperty); }
            set { this.SetValue(ForegroundProperty, value); }
        }

        private static void OnBorderThicknessChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            var ctl = d as CustomTextBox;
            if (ctl != null)
            {
                ctl.Input.BorderThickness = ctl.BorderThickness;
            }
        }

        public new static readonly DependencyProperty BorderThicknessProperty =
        DependencyProperty.Register("BorderThickness", typeof(Thickness), typeof(CustomTextBox),
        new FrameworkPropertyMetadata(new Thickness(0,0,0,0), OnBorderThicknessChanged));

        public new Thickness BorderThickness
        {
            get { return (Thickness)this.GetValue(BorderThicknessProperty); }
            set { this.SetValue(BorderThicknessProperty, value); }
        }


        private static void OnPaddingChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            var ctl = d as CustomTextBox;
            if (ctl != null)
            {
                ctl.Input.Padding = ctl.Padding;
                ctl.DisplayText.Padding = ctl.Padding;
                ctl.padding_dx = ctl.Padding.Left;
            }
        }
        public new static readonly DependencyProperty PaddingProperty =
        DependencyProperty.Register("Padding", typeof(Thickness), typeof(CustomTextBox),
        new FrameworkPropertyMetadata(new Thickness(0,0,0,0), OnPaddingChanged));


        public new Thickness Padding
        {
            get { return (Thickness)this.GetValue(PaddingProperty); }
            set { this.SetValue(PaddingProperty, value); }
        }


        private static void OnFontWeightChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            var ctl = d as CustomTextBox;
            if (ctl != null)
            {
                ctl.Input.FontWeight = ctl.FontWeight;
                ctl.DisplayText.FontWeight = ctl.FontWeight;
            }
        }

        public new FontWeight FontWeight
        {
            get { return (FontWeight)this.GetValue(FontWeightProperty); }
            set { this.SetValue(FontWeightProperty, value); }
        }
        public new static readonly DependencyProperty FontWeightProperty =
               DependencyProperty.Register("FontWeight", typeof(FontWeight), typeof(CustomTextBox),
               new FrameworkPropertyMetadata(SystemFonts.MessageFontWeight, OnFontWeightChanged));


        private static void OnFontSizeChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            var ctl = d as CustomTextBox;
            if (ctl != null)
            {
                ctl.Input.FontSize = ctl.FontSize;
                ctl.DisplayText.FontSize = ctl.FontSize;
            }
        }

        public new double FontSize
        {
            get { return (double)this.GetValue(FontSizeProperty); }
            set { this.SetValue(FontSizeProperty, value); }
        }
        public new static readonly DependencyProperty FontSizeProperty =
               DependencyProperty.Register("FontSize", typeof(double), typeof(CustomTextBox),
               new FrameworkPropertyMetadata(SystemFonts.MessageFontSize, OnFontSizeChanged));


        private static void OnWidthChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            var ctl = d as CustomTextBox;
            if (ctl != null)
            {
                ctl.Input.Width = ctl.Width;
            }
        }

        public new double Width
        {
            get { return (double)this.GetValue(WidthProperty); }
            set { this.SetValue(WidthProperty, value); }
        }
        public new static readonly DependencyProperty WidthProperty =
               DependencyProperty.Register("Width", typeof(double), typeof(CustomTextBox),
               new FrameworkPropertyMetadata(Double.NaN, OnWidthChanged));


        private static void OnHeightChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            var ctl = d as CustomTextBox;
            if (ctl != null)
            {
                ctl.Input.Height = ctl.Height;
            }
        }

        public new double Height
        {
            get { return (double)this.GetValue(HeightProperty); }
            set { this.SetValue(HeightProperty, value); }
        }
        public new static readonly DependencyProperty HeightProperty =
               DependencyProperty.Register("Height", typeof(double), typeof(CustomTextBox),
               new FrameworkPropertyMetadata(Double.NaN, OnHeightChanged));

        public double DisplayTop
        {
            get { return (double)this.GetValue(DisplayTopProperty); }
            set { this.SetValue(DisplayTopProperty, value); }
        }
        public static readonly DependencyProperty DisplayTopProperty =
               DependencyProperty.Register("DisplayTop", typeof(double), typeof(CustomTextBox),
               new FrameworkPropertyMetadata(0.0, OnFontSizeChanged));

        public double DisplayLeft
        {
            get { return (double)this.GetValue(DisplayLeftProperty); }
            set { this.SetValue(DisplayLeftProperty, value); }
        }

        public static readonly DependencyProperty DisplayLeftProperty =
               DependencyProperty.Register("DisplayLeft", typeof(double), typeof(CustomTextBox),
               new FrameworkPropertyMetadata(0.0, OnFontSizeChanged));
        private static void OnCaretWidthChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            var ctl = d as CustomTextBox;
            if (ctl != null)
            {
                ctl.Caret.Width = ctl.CaretWidth;
            }
        }

        public double CaretWidth
        {
            get { return (double)this.GetValue(CaretWidthProperty); }
            set { this.SetValue(CaretWidthProperty, value); }
        }
        public static readonly DependencyProperty CaretWidthProperty =
               DependencyProperty.Register("CaretWidth", typeof(double), typeof(CustomTextBox),
               new FrameworkPropertyMetadata(5.0, OnCaretWidthChanged));


        private static void OnCaretHeightChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            var ctl = d as CustomTextBox;
            if (ctl != null)
            {
                ctl.Caret.Height = ctl.CaretHeight;
            }
        }

        public double CaretHeight
        {
            get { return (double)this.GetValue(CaretHeightProperty); }
            set { this.SetValue(CaretHeightProperty, value); }
        }
        public static readonly DependencyProperty CaretHeightProperty =
               DependencyProperty.Register("CaretHeight", typeof(double), typeof(CustomTextBox),
               new FrameworkPropertyMetadata(SystemFonts.MessageFontSize, OnFontSizeChanged));

        /* TODO:
        private static void OnCaretBrushChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            var ctl = d as CustomTextBox;
            if (ctl != null)
            {
                ctl.Caret.Background = ctl.CaretBrush;
            }
        }

        public static readonly DependencyProperty CaretBrushProperty =
        DependencyProperty.Register("CaretBrush", typeof(Brush), typeof(CustomTextBox),
        new FrameworkPropertyMetadata(new SolidColorBrush(SystemColors.HighlightColor), OnCaretBrushChanged));
        

        public Brush CaretBrush
        {
            get { return (Brush)this.GetValue(CaretBrushProperty); }
            set { this.SetValue(CaretBrushProperty, value); }
        }
        */

        public CustomTextBox()
        {
            InitializeComponent();

            this.Input.SelectionChanged += (sender, e) => MoveCustomCaret();
            this.Input.LostFocus += (sender, e) => Caret.Visibility = Visibility.Collapsed;
            this.Input.GotFocus += (sender, e) => Caret.Visibility = Visibility.Visible;

            this.Loaded += CustomTextBox_Loaded;
        }

        void CustomTextBox_Loaded(object sender, RoutedEventArgs e)
        {
            this.Caret.Width = this.CaretWidth;
            this.Caret.Height = this.CaretHeight;
            this.MoveCustomCaret();
            //this.Caret.Background = this.CaretBrush;
        }

        private void MoveCustomCaret()
        {
            var caretLocation = Input.GetRectFromCharacterIndex(Input.CaretIndex).Location;

            if (!double.IsInfinity(caretLocation.X))
            {
                Canvas.SetLeft(Caret, caretLocation.X);
            }

            if (!double.IsInfinity(caretLocation.Y))
            {
                Canvas.SetTop(Caret, caretLocation.Y);
            }
        }


    }
}
