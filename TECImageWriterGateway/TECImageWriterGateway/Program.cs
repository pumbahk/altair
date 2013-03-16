using System;
using System.Collections.Generic;
using System.Windows.Forms;
using System.Net;
using Microsoft.Win32;

namespace TECImageWriterGateway
{
    static class Program
    {
        const string PageSetupKey = "Software\\Microsoft\\Internet Explorer\\PageSetup";

        /// <summary>
        /// アプリケーションのメイン エントリ ポイントです。
        /// </summary>
        [STAThread]
        static void Main(string[] args)
        {
            Environment.Exit(RealMain(args));
        }

        static int RealMain(string[] args)
        {
            AdjustIEPageSettings();
            if (args.Length >= 1)
            {
                if (args[0] == "test")
                {
                    StartGUI();
                    return 0;
                }
                else if (args[0] == "server")
                {
                    if (!HttpListener.IsSupported)
                    {
                        Console.WriteLine("HttpListener not supported");
                        return 1;
                    }
                    if (args.Length < 2)
                    {
                        Console.WriteLine("prefix is not specified");
                    }
                    else
                    {
                        StartListening(args[1]);
                        return 0;
                    }
                }
            }
            {
                Console.WriteLine("Usage: " + new System.IO.FileInfo(Application.ExecutablePath).Name + " (test | server) prefix");
                return 255;
            }
        }

        static void AdjustIEPageSettings()
        {
            using (RegistryKey k = Registry.CurrentUser.OpenSubKey(PageSetupKey, true))
            {
                if (k == null)
                {
                    return;
                }
                k.SetValue("header", "", RegistryValueKind.String);
                k.SetValue("footer", "", RegistryValueKind.String);
                k.SetValue("margin_bottom", "0", RegistryValueKind.String);
                k.SetValue("margin_top", "0", RegistryValueKind.String);
                k.SetValue("margin_left", "0", RegistryValueKind.String);
                k.SetValue("margin_right", "0", RegistryValueKind.String);
                k.SetValue("Print_Background", "no", RegistryValueKind.String);
                k.SetValue("Shrink_To_Fit", "yes", RegistryValueKind.String);
            }
        }

        static void StartGUI()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new BootstrapForm());
        }

        static void StartListening(string prefix)
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Server server = new Server(prefix);
            Console.CancelKeyPress += delegate(object obj, ConsoleCancelEventArgs args)
            {
                server.Stop();
            };
            server.Run();
        }
    }
}
