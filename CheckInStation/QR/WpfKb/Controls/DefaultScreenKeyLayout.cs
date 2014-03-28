using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Media;
using System.Windows.Media.Animation;
using WpfKb.LogicalKeys;

namespace WpfKb.Controls
{
    public class DefaultScreenKeyLayout : IScreenKeyLayout
    {
        private Border _keySurface;
        private Border _mouseDownSurface;
        private TextBlock _keyText;
        private readonly OnScreenKey core;

        public DefaultScreenKeyLayout(OnScreenKey key){
            this.core = key;
            this.SetupControl(key.Key);
        }

        private readonly GradientBrush _keySurfaceBrush = new LinearGradientBrush(
            new GradientStopCollection
                {
                    new GradientStop(Color.FromRgb(56, 56, 56), 0),
                    new GradientStop(Color.FromRgb(56, 56, 56), 0.6),
                    new GradientStop(Color.FromRgb(26, 26, 26), 1)
                }, 90);

        private readonly GradientBrush _keySurfaceBorderBrush = new LinearGradientBrush(
            new GradientStopCollection
                {
                    new GradientStop(Color.FromRgb(200, 200, 200), 0),
                    new GradientStop(Color.FromRgb(56, 56, 56), 1)
                }, 90);

        private readonly GradientBrush _keySurfaceMouseOverBrush = new LinearGradientBrush(
            new GradientStopCollection
                {
                    new GradientStop(Color.FromRgb(120, 120, 120), 0),
                    new GradientStop(Color.FromRgb(120, 120, 120), 0.6),
                    new GradientStop(Color.FromRgb(80, 80, 80), 1)
                }, 90);

        private readonly GradientBrush _keySurfaceMouseOverBorderBrush = new LinearGradientBrush(
            new GradientStopCollection
                {
                    new GradientStop(Color.FromRgb(255, 255, 255), 0),
                    new GradientStop(Color.FromRgb(100, 100, 100), 1),
                }, 90);

        private readonly SolidColorBrush _keyOutsideBorderBrush = new SolidColorBrush(Color.FromArgb(255, 26, 26, 26));

        public void AnimateMouseDown()
        {
            _mouseDownSurface.BeginAnimation(OnScreenKey.OpacityProperty, new DoubleAnimation(1, new Duration(TimeSpan.Zero)));
            _keyText.Foreground = _keyOutsideBorderBrush;
        }

        public void AnimateMouseUp()
        {
            var core = this.core;
            if ((core.Key is TogglingModifierKey || core.Key is InstantaneousModifierKey) && ((ModifierKeyBase)core.Key).IsInEffect) return;
            _keySurface.BorderBrush = _keySurfaceBorderBrush;
            _keyText.Foreground = Brushes.White;
            if (!core.AreAnimationsEnabled || core.Key is TogglingModifierKey || core.Key is InstantaneousModifierKey)
            {
                _mouseDownSurface.BeginAnimation(OnScreenKey.OpacityProperty, new DoubleAnimation(0, new Duration(TimeSpan.Zero)));
            }
            else
            {
                _mouseDownSurface.BeginAnimation(OnScreenKey.OpacityProperty, new DoubleAnimation(0, Duration.Automatic));
            }
        }

        public void OnMouseEnter()
        {
            _keySurface.Background = _keySurfaceMouseOverBrush;
            _keySurface.BorderBrush = _keySurfaceMouseOverBorderBrush;
        }

        public void OnMouseLeave()
        {
            _keySurface.Background = _keySurfaceBrush;
            _keySurface.BorderBrush = _keySurfaceBorderBrush;
        }

        public void BuildVisual()
        {
            var core = this.core;            
            core.CornerRadius = new CornerRadius(3);
            core.BorderBrush = _keyOutsideBorderBrush;
            core.BorderThickness = new Thickness(1);
            core.SnapsToDevicePixels = true;

            var g = new Grid();
            core.Child = g;

            _keySurface = new Border
            {
                CornerRadius = new CornerRadius(3),
                BorderBrush = _keySurfaceBorderBrush,
                BorderThickness = new Thickness(1),
                Background = _keySurfaceBrush,
                SnapsToDevicePixels = true
            };
            g.Children.Add(_keySurface);

            _mouseDownSurface = new Border
            {
                CornerRadius = new CornerRadius(3),
                Background = Brushes.White,
                Opacity = 0,
                SnapsToDevicePixels = true
            };
            g.Children.Add(_mouseDownSurface);

            _keyText = new TextBlock
            {
                Margin = new Thickness(3, 0, 0, 0),
                FontSize = 20,
                HorizontalAlignment = HorizontalAlignment.Left,
                VerticalAlignment = VerticalAlignment.Top,
                Foreground = Brushes.White,
                SnapsToDevicePixels = true
            };
        }

        public void SetupControl(ILogicalKey key)
        {
            this.BuildVisual();
            _keyText.SetBinding(TextBlock.TextProperty, new Binding("DisplayName") { Source = key });
            (this.core.Child as Grid).Children.Add(_keyText);
        }

    }
}
