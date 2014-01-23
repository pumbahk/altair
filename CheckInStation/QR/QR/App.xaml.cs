using System;
using System.Collections.Generic;
using System.Configuration;
using System.Data;
using System.Linq;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;

using QR.presentation.gui;
using NLog;

namespace QR
{
    /// <summary>
    /// ロジック的な処理のbroker
    /// </summary>
    public class AppUtil
    {
        public static RequestBroker Broker;
        public static InternalApplication Internal;
        public static PageNavigator PageChoicer;

        public static void OnStartup(StartupEventArgs e)
        {
            //モデル層の処理をどこに置いたらよいのかわからないので、とりあえずここに。
            var app = AppUtil.Internal = new InternalApplication();
            AppUtil.PageChoicer = new PageNavigator();
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

        public static PageNavigator GetNavigator()
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
        private static Logger logger = LogManager.GetCurrentClassLogger();

        private void App_Startup(object sender, StartupEventArgs e)
        {
            AppDomain.CurrentDomain.UnhandledException += CurrentDomain_UnhandledException;
        }
        void CurrentDomain_UnhandledException(object sender, UnhandledExceptionEventArgs e)
        {
            Exception ex = e.ExceptionObject as Exception;
            logger.ErrorException("unhandled:", ex);
            MessageBox.Show(ex.Message, "例外発生(UI スレッド外)",
                                  MessageBoxButton.OK, MessageBoxImage.Error);
            this.Shutdown();
        }
        private void App_DispatcherUnhandledException(object sender, System.Windows.Threading.DispatcherUnhandledExceptionEventArgs e)
        {
            logger.ErrorException("unhandled(ui):", e.Exception);
            MessageBox.Show(e.Exception.Message, "システムエラーが発生しました。終了します",
                                  MessageBoxButton.OK, MessageBoxImage.Error);
            e.Handled = true;
        }

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
