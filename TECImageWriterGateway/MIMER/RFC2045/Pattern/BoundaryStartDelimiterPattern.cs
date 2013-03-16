﻿

using System.Text.RegularExpressions;

namespace MIMER.RFC2045.Pattern
{
    public class BoundaryStartDelimiterPattern:IPattern
    {
        private const string m_TextPattern = "--.{1,70}\x0D\x0A";
        private readonly Regex m_Regex;

        public BoundaryStartDelimiterPattern()
        {
            m_Regex = new Regex(m_TextPattern);
        }

        public string TextPattern
        {
            get { return m_TextPattern; }
        }

        public Regex RegularExpression
        {
            get { return m_Regex; }
        }
    }
}
