using System;
using System.Collections.Generic;
using System.Configuration;
using System.Data;
using System.Linq;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;

using checkin.presentation.gui;
using NLog;
using checkin.core.support;
using checkin.core;
using checkin.core.models;
using checkin.core.flow;

namespace checkin.presentation
{
    /// <summary>
    /// ロジック的な処理のbroker
    /// </summary>
    public class AppUtil
    {
        private static Logger logger = LogManager.GetCurrentClassLogger();
        public static RequestBroker Broker;
        public static InternalApplication Internal;
        public static PageNavigator PageChoicer;
        public static RefreshPageNavigator RefreshPageNavigator;
        public static void OnStartup(StartupEventArgs e)
        {
            //モデル層の処理をどこに置いたらよいのかわからないので、とりあえずここに。
            var app = AppUtil.Internal = new InternalApplication();
            AppUtil.PageChoicer = new PageNavigator();
            AppUtil.Broker = app.RequestBroker;
            AppUtil.Broker.SetStartCase(new CaseAuthInput(app.Resource));
            AppUtil.RefreshPageNavigator = new RefreshPageNavigator(AppUtil.PageChoicer);
            AppUtil.Loadstyle();
        }

        public static IResource GetCurrentResource()
        {
            return AppUtil.Internal.Resource;
        }

        private static void Loadstyle()
        {
            ResourceDictionary myResourceDictionary = new ResourceDictionary();
            switch (ConfigurationManager.AppSettings["application.flow"])
            {
                case "StandardFlow":
                    myResourceDictionary.Source = new Uri("Styles\\Ticketstar\\StandardFlow.xaml", UriKind.Relative);
                    break;
                case "OneStep":
                    myResourceDictionary.Source = new Uri("Styles\\Ticketstar\\OneStep.xaml", UriKind.Relative);
                    break;
                default:
                    break;
            }
            Application.Current.Resources.MergedDictionaries.Add(myResourceDictionary);
        }

        public static void GotoWelcome(Page previous)
        {
            try
            {
                var broker = AppUtil.GetCurrentBroker();
                var manager = broker.FlowManager;
                var case_ = new CaseWelcome(AppUtil.GetCurrentResource());
                var flow_ = new Flow(manager, case_);
                manager.Refresh();
                manager.Push(flow_);
                AppUtil.GetNavigator().NavigateToMatchedPage(case_, previous);
            }
            catch (Exception ex)
            {
                logger.ErrorException("goto welcome page".WithMachineName(), ex);
            }
            
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
        public static RefreshPageNavigator GetRefreshPageNavigator()
        {
            return AppUtil.RefreshPageNavigator;
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
            logger.ErrorException("unhandled:".WithMachineName(), ex);
            MessageBox.Show(ex.Message, "例外発生(UI スレッド外)",
                                  MessageBoxButton.OK, MessageBoxImage.Error);
            this.Shutdown();
        }
        private void App_DispatcherUnhandledException(object sender, System.Windows.Threading.DispatcherUnhandledExceptionEventArgs e)
        {
            logger.ErrorException("unhandled(ui):".WithMachineName(), e.Exception);
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
