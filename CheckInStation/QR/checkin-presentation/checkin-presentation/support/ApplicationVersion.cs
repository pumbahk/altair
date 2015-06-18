using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Threading.Tasks;

namespace checkin.presentation.support
{
    public static class ApplicationVersion
    {
       
        public static string GetApplicationInformationalVersion()
        {
            var assembly = Assembly.GetExecutingAssembly();
            var attribute = assembly.GetCustomAttributes(typeof(AssemblyInformationalVersionAttribute), true).FirstOrDefault() as AssemblyInformationalVersionAttribute;
            //return "<todo fix>";
            return attribute.InformationalVersion.Substring(0, 3);
        }
    }
}
