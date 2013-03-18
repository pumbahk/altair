﻿using System.Text.RegularExpressions;

namespace MIMER.RFC822.Pattern
{
    public class MonthPattern:IPattern
    {
        private const string m_TextPattern = "(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)";
        private readonly Regex m_Regex;

        public MonthPattern()
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