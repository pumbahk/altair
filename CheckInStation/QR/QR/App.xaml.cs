using System;
using System.Collections.Generic;
using System.Configuration;
using System.Data;
using System.Linq;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;

using QR.presentation.gui;

namespace QR
{
    /// <summary>
    /// ロジック的な処理のbroker
    /// </summary>
    public class AppUtil
    {
        public static RequestBroker Broker;
        public static InternalApplication Internal;
        public static NextPageChoicer PageChoicer;

        public static void OnStartup(StartupEventArgs e)
        {
            //モデル層の処理をどこに置いたらよいのかわからないので、とりあえずここに。
            var app = AppUtil.Internal = new InternalApplication();
            AppUtil.PageChoicer = new NextPageChoicer();
            AppUtil.Broker = app.RequestBroker;
            AppUtil.Broker.SetStartCase(new CaseAuthInput(app.Resource));
        }

        public static void OnExit(ExitEventArgs e)
        {
            AppUtil.Internal.ShutDown();
        }

        public static RequestBroker GetCurrentBroker()
        {
            return AppUtil.Broker;
        }

        public static NextPageChoicer GetNavigator()
        {
            return AppUtil.PageChoicer;
        }
    }

    /// <summary>
    /// App.xaml の相互作用ロジック
    /// </summary>    
    ///
    public partial class App : Application
    {
        protected override void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);
            AppUtil.OnStartup(e);
        }

        protected override void OnExit(ExitEventArgs e)
        {
            AppUtil.OnExit(e);
            base.OnExit(e);
        }
    }
}
