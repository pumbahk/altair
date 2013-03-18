using System;
using System.Collections.Generic;
using System.Linq;
using MIMER.RFC2045;
using MIMER.RFC2183;
using MIMER.RFC822;
using MIMER.RFC2045.Pattern;

namespace MIMER.RFC2633
{
    class SMIMEFieldParser:FieldParserDecorator
    {
        #region IFieldParser Members        

        public SMIMEFieldParser(ContentDispositionFieldParser original)
            : base(original)
        {
            Original = original;
            IPattern pattern =
                PatternFactory.GetInstance().Get(typeof (ApplicationSubTypePattern));
            ApplicationSubTypePattern applicationSubtypePattern =
                pattern as ApplicationSubTypePattern;

            if (applicationSubtypePattern == null)
                throw new ApplicationException("Could not retrive a " + typeof(ApplicationSubTypePattern).Name);

            applicationSubtypePattern.SubTypes.Add("pkcs7-mime");
            applicationSubtypePattern.SubTypes.Add("pkcs7-signature");
            applicationSubtypePattern.SubTypes.Add("x-pkcs7-mime");
            applicationSubtypePattern.Compile();
        }

        public ContentDispositionFieldParser Original;

        public override void CompilePattern()
        {
            DecoratedFieldParser.CompilePattern();
        }

        public override void Parse(IList<Field> fields, string fieldString)
        {
            DecoratedFieldParser.Parse(fields, fieldString);
            foreach (Field field in fields)
            {
                if (field is ContentTypeField && !string.IsNullOrEmpty(((ContentTypeField) field).Parameters["smime-type"]))
                {
                    fields.Add(field);
                }
            }            
        }

        #endregion
    }
}
