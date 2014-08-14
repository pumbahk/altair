using System.Reflection;

namespace checkin.core
{
    // *utility*
    public static class Testing
    {
        public static System.IO.Stream GetEmbeddedFileStream (string name)
        {
            var assembly = Assembly.GetExecutingAssembly ();
            return assembly.GetManifestResourceStream (name);
        }

        public static string ReadFromEmbeddedFile (string name)
        {
            using (var stream = GetEmbeddedFileStream (name))
            using (var reader = new System.IO.StreamReader (stream)) {
                return reader.ReadToEnd ();
            }
        }
    }
}