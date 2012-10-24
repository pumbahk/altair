using System;
using System.Collections.Generic;
using System.Windows.Forms;
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
        static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            AdjustIEPageSettings();
            Application.Run(new BootstrapForm());
        }

        static void AdjustIEPageSettings()
        {
            using (RegistryKey k = Registry.CurrentUser.OpenSubKey(PageSetupKey, true))
            {
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
    }
}