using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Printing;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using checkin.core.models;
using checkin.core.events;
using checkin.core;

namespace checkin.presentation.gui
{
    public class UnitStringPair
    {
        public UnitStringPair(string k, string v) { this.Key = k; this.Value = v; }
        public string Key {get;set;}
        public string Value {get;set;}
    }

    public class UnitPair<T>
    {
        public UnitPair(string k, T v){this.Key = k; this.Value = v;}
        public string Key {get;set;}
        public T Value {get;set;}
    }

    public class CandidateCreator
    {
        public static ObservableCollection<UnitStringPair> PrintUnitCandidates()
        {
            var candidates = new ObservableCollection<UnitStringPair>();
            candidates.Add(new UnitStringPair("このチケット１枚を発券", PrintUnit.one.ToString()));
            candidates.Add(new UnitStringPair("同じ受付番号のチケットをまとめて発券", PrintUnit.all.ToString()));
            return candidates;
        }

        public static ObservableCollection<UnitStringPair> InputUnitCandidates()
        {
            var candidates = new ObservableCollection<UnitStringPair>();
            candidates.Add(new UnitStringPair("QRで認証", InputUnit.qrcode.ToString()));
            candidates.Add(new UnitStringPair("受付番号を入力して認証", InputUnit.order_no.ToString()));
            return candidates;
        }

        public static ObservableCollection<UnitPair<Style>> WindowStyleCandidates(FrameworkElement el)
        {
            var candidates = new ObservableCollection<UnitPair<Style>>();
            candidates.Add(new UnitPair<Style>("全画面表示", (Style)el.FindResource("MainWindow")));
            candidates.Add(new UnitPair<Style>("ウィンドウ表示", (Style)el.FindResource("MainWindowSmall")));
            return candidates;
        }

        public static ObservableCollection<UnitPair<FlowDefinitionType>> FlowStyleCandidates()
        {
            var candidates = new ObservableCollection<UnitPair<FlowDefinitionType>>();
            candidates.Add(new UnitPair<FlowDefinitionType>("汎用発券", FlowDefinitionType.StandardFlow));
            candidates.Add(new UnitPair<FlowDefinitionType>("一括発券", FlowDefinitionType.OneStep));
            return candidates;
        }

        public static ObservableCollection<PrintQueue> AvailablePrinterCandidates(ITicketPrinting printing){
            var printers = new ObservableCollection<PrintQueue>();
            printers.Add(printing.DefaultPrinter);
            foreach (var q in printing.AvailablePrinters())
            {
                if (printing.DefaultPrinter.FullName != q.FullName)
                {
                    printers.Add(q);
                }
            }
            return printers;
        }
    }
}
