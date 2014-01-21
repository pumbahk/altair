using System;
using System.Collections.Generic;
using System.Configuration;
using System.Data;
using System.Linq;
using System.Threading.Tasks;
using System.Windows;

namespace QR
{
    /// <summary>
    /// ロジック的な処理のbroker
    /// </summary>
    public class AppUtil
    {
        public static RequestBroker Broker;
        public static InternalApplication Internal;

        public static void OnStartup(StartupEventArgs e)
        {
            //モデル層の処理をどこに置いたらよいのかわからないので、とりあえずここに。
            var app = AppUtil.Internal = new InternalApplication();
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
