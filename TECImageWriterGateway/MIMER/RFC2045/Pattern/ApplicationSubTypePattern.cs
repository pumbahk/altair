
using System.Collections.Generic;
using System.Text;
using System.Text.RegularExpressions;

namespace MIMER.RFC2045.Pattern
{
    public class ApplicationSubTypePattern:ICompiledPattern
    {
        private IList<string> m_SubTypes;
        private string m_TextPattern;
        private Regex m_Regex;

        public ApplicationSubTypePattern()
        {
            SubTypes = new List<string>();
            SubTypes.Add("octet-stream|");
            SubTypes.Add("PostScript");
            SubTypes.Add("pdf");
            Compile();
            
        }

        public string TextPattern
        {
            get { return m_TextPattern; }
        }

        public Regex RegularExpression
        {
            get { return m_Regex; }
        }

        public IList<string> SubTypes
        {
            get { return m_SubTypes; }
            set { m_SubTypes = value; }
        }

        public void Compile()
        {
            StringBuilder builder = new StringBuilder();
            builder.Append("(");
            for (int i = 0; i < SubTypes.Count; i++ )
            {
                builder.Append(SubTypes[i]);
                if(i < SubTypes.Count)
                {
                    builder.Append("|");
                }
            }
            builder.Append(")");

            m_TextPattern = builder.ToString();
            m_Regex = new Regex(m_TextPattern, RegexOptions.Compiled);
        }
    }
}
