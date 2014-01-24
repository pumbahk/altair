using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace QR.presentation.gui
{
    public class UnitPair
    {
        public UnitPair() { }
        public UnitPair(string k, string v) { this.Key = k; this.Value = v; }
        public string Key { get; set; }
        public string Value { get; set; }
    }

    public class CandidateCreator
    {
        public static ObservableCollection<UnitPair> PrintUnitCandidates()
        {
            var candidates = new ObservableCollection<UnitPair>();
            candidates.Add(new UnitPair("このチケット１枚を発券", PrintUnit.one.ToString()));
            candidates.Add(new UnitPair("同じ注文番号のチケットをまとめて発券", PrintUnit.all.ToString()));
            return candidates;
        }

        public static ObservableCollection<UnitPair> InputUnitCandidates()
        {
            var candidates = new ObservableCollection<UnitPair>();
            candidates.Add(new UnitPair("QRで認証", InputUnit.qrcode.ToString()));
            candidates.Add(new UnitPair("注文番号を入力して認証", InputUnit.order_no.ToString()));
            return candidates;
        }
    }
}
