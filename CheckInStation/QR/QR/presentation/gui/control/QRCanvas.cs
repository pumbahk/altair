using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Shapes;

namespace QR.presentation.gui.control
{

    public class QRCodeCanvas : Canvas
    {
        public readonly Brush InverseForeground;
        public static readonly DependencyProperty QRCodeProperty =
        DependencyProperty.Register("QRCode", typeof(string), typeof(QRCodeCanvas));

        public string QRCode
        {
            get { return (string)GetValue(QRCodeProperty); }
            set { SetValue(QRCodeProperty, value); }
        }

        public static readonly DependencyProperty ForegroundProperty =
        DependencyProperty.Register("Foreground", typeof(Brush), typeof(QRCodeCanvas));

        public Brush Foreground
        {
            get { return (Brush)GetValue(ForegroundProperty); }
            set { SetValue(ForegroundProperty, value); }
        }

        public QRCodeCanvas()
            : base()
        {
            this.Loaded += QRCodeCanvas_Loaded;
            this.InverseForeground = new SolidColorBrush(Color.FromRgb(255, 255, 255));
        }

        void QRCodeCanvas_Loaded(object sender, RoutedEventArgs e)
        {
            if (this.QRCode == null)
                return;

            // temporary
            var y = -this.Height / 2;
            var default_x = -this.Width / 2;
            var x = default_x;

            var path = new Path() { Fill = this.Foreground, Stroke = this.Foreground };
            var group = new GeometryGroup();

            var writer = new ZXing.QrCode.QRCodeWriter();
            var matrix = writer.encode(this.QRCode, ZXing.BarcodeFormat.QR_CODE, 96, 96);

            var w = (2 * this.Width / matrix.Width);
            var h = (2 * this.Height / matrix.Height);

            for (var i = 0; i < matrix.Height; i++)
            {
                for (var j = 0; j < matrix.Width; j++)
                {
                    if (matrix[j, i] == true)
                    {
                        var rect = new RectangleGeometry() { Rect = new Rect(x, y, w, h) };
                        group.Children.Add(rect);
                    }
                    x += w;
                }
                y += h;
                x = default_x;
            }

            path.Data = group;
            this.Children.Add(path);
            this.Loaded -= QRCodeCanvas_Loaded;
        }
    }
}
