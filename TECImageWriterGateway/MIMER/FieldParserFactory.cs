using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace MIMER
{
    public class FieldParserFactory
    {
        private static FieldParserFactory s_Instance = null;

        private IDictionary<Type, IFieldParser> m_Pool;

        FieldParserFactory()
        {
            m_Pool = new Dictionary<Type, IFieldParser>();
        }

        public static FieldParserFactory GetInstance()
        {
            if(s_Instance == null)
                s_Instance = new FieldParserFactory();

            return s_Instance;
        }

        public IFieldParser GetParser(Type type)
        {
            if (type.GetInterface(typeof(IFieldParser).Name) == null)
                throw new ArgumentException("Argument type must be implementation of IFieldParser");

            

            if (m_Pool.ContainsKey(type))
            {
                return m_Pool[type];
            }
            else
            {
                IFieldParser parser = Activator.CreateInstance(type) as IFieldParser;
                if(parser != null)
                    m_Pool.Add(parser.GetType(), parser);
                return parser;
            }
        }
    }
}
