/*
Copyright (c) 2007, Robert Wallström, smithimage.com
All rights reserved.
 
Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
	
	* Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer. 
	* Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution. 
	* Neither the name of the SMITHIMAGE nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission. 

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH  DAMAGE.
*/
using System;
using System.Collections.Generic;
using System.Text;

using System.Text.RegularExpressions;

namespace MIMER
{
    /// <summary>
    /// This class acts as a singleton proxy towards any other class
    /// which needs parsing functionality but does not need to extend the
    /// default funtionality of the existent parsers.
    /// </summary>
    public class FieldParserProxy:RFC2045.ContentTransferEncodingFieldParser, IFieldParser, MIMER.IFieldParserProxy
    {
        private RFC822.FieldParser m_822Parser;
        private RFC2045.ContentTypeFieldParser m_ContentTypeFieldParser;
        private RFC2045.ContentTransferEncodingFieldParser m_ContentTransferEncodingFieldParser;
        private RFC2183.ContentDispositionFieldParser m_ContentDispositionFieldParser;
        private RFC2047.ExtendedFieldParser m_ExtendedFieldParser;
        
        protected static IFieldParserProxy s_Proxy = null;

        protected FieldParserProxy() 
        {
            m_822Parser = new MIMER.RFC822.FieldParser();
            m_ContentTypeFieldParser = new MIMER.RFC2045.ContentTypeFieldParser();
            m_ContentTransferEncodingFieldParser = new MIMER.RFC2045.ContentTransferEncodingFieldParser();
            m_ContentDispositionFieldParser = new MIMER.RFC2183.ContentDispositionFieldParser();
            m_ExtendedFieldParser = new MIMER.RFC2047.ExtendedFieldParser();
        }

        #region Static methods
        public static IFieldParserProxy Getinstance()
        {
            if (s_Proxy == null)
                s_Proxy = new FieldParserProxy();
            return s_Proxy;
        }

        public static string ParseAddress(string data)
        {
            IFieldParserProxy proxy = Getinstance();
            if (proxy.AddrSpec.IsMatch(data))
                return proxy.AddrSpec.Match(data).Value;
            else
                return string.Empty;
        }        

        public static void ParseFields(ref IList<MIMER.RFC822.Field> fields, ref string fieldString)
        {
            IFieldParserProxy proxy = Getinstance();
            proxy.Parse(ref fields, ref fieldString);
        }

        #endregion

        #region IFieldParser Members

        public override void Parse(ref IList<MIMER.RFC822.Field> fields, ref string fieldString)
        {   
            m_822Parser.Parse(ref fields, ref fieldString);
            m_ExtendedFieldParser.Parse(ref fields, ref fieldString);
            m_ContentTypeFieldParser.Parse(ref fields, ref fieldString);
            m_ContentTransferEncodingFieldParser.Parse(ref fields, ref fieldString);
            m_ContentDispositionFieldParser.Parse(ref fields, ref fieldString);            
        }

        public override void CompilePattern()
        {
            m_822Parser.CompilePattern();
            m_ContentTypeFieldParser.CompilePattern();
            m_ContentTransferEncodingFieldParser.CompilePattern();
            m_ContentDispositionFieldParser.CompilePattern();
            m_ExtendedFieldParser.CompilePattern();
        }       

        #endregion

        public new Regex CompositeType
        {
            get { return m_ContentTypeFieldParser.CompositeType; }
        }

        public new Regex DescriteType
        {
            get { return m_ContentTypeFieldParser.DescriteType; }
        }

        public new Regex StartBoundary
        {
            get { return m_ContentTypeFieldParser.StartBoundary; }
        }

        public new Regex EndBoundary
        {
            get { return m_ContentTypeFieldParser.EndBoundary; }
        }

        public new Regex MIMEVersion
        {
            get { return m_ContentTypeFieldParser.MIMEVersion; }
        }

        public new Regex AddrSpec
        {
            get
            {
                return m_822Parser.AddrSpec;
            }
        }
    }
}
