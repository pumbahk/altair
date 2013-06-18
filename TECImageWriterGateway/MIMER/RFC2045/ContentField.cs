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

namespace MIMER.RFC2045
{
    public abstract class ContentField : MIMER.RFC822.Field
    {
        #region REGEX Strings
        public static readonly string s_TSpecials = "][()<>@,;\x5C\x5C:\x22/?=";
        public static readonly string s_Token = "[^" + s_TSpecials + "\x00-\x20]+";
        public static readonly string s_Value = "(" + s_Token + "|" +
            MIMER.RFC822.Field.QuotedString + ")";
        public static readonly string s_Attribute = s_Token;
        public static readonly string s_Parameter = s_Token + "=" + s_Value;
        public static readonly string s_XToken = "(X-|x-)" + s_Token;
        public static readonly string s_CompositeType = "(message|multipart)";
        public static readonly string s_DiscreteType = "(text|image|audio|video|application)";
        public static readonly string s_MultipartSubTypes = "(mixed|alternative|parallel|digest|related)";
        public static readonly string s_TextSubtypes = "(plain|enriched|html)";
        public static readonly string s_ImageSubTypes = "(?i)(jpeg|gif)(?i)";
        public static readonly string s_ApplicationSubtypes = "(octet-stream|PostScript)"; //TODO: add the rest se rfc 2046
        public static readonly string s_MessageSubTypes = "(rfc822|partial|external-body)";
        public static readonly string s_SubTypes = "((?<=multipart/)" + s_MultipartSubTypes + "|" +
            "(?<=text/)" + s_TextSubtypes + "|" + "(?<=image/)" + s_ImageSubTypes + "|" +
            "(?<=application/)" + s_ApplicationSubtypes + "|" + "(?<=message/)" + s_MessageSubTypes + ")"; //TODO: continue with the rest of subtypes
        public static readonly string s_Type = "(" + s_DiscreteType + "|" + s_CompositeType + ")";
        public static readonly string s_IetfToken = ""; //Cant understand what this is :)
        public static readonly string s_IanaToken = ""; //Cant understand what this is :)
        public static readonly string s_ExtensionToken = s_XToken; // or ietf-token
        public static readonly string s_SubType = "(" + s_SubTypes + "|" + s_ExtensionToken + ")";//|" + s_Token + ")"; // or iana-token

        public static readonly string s_BoundaryStartDelimiter = "--.{1,70}\x0D\x0A";
        public static readonly string s_BoundaryEndDelimiter = "--.{1,68}--\x0D\x0A";

        #endregion
    }
}
