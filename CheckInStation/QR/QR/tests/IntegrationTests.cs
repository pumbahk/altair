using NUnit.Framework;
using System;
using System.Reflection;

namespace QR
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

	[TestFixture ()]
	public class IntegrationTests
	{
		[Test ()]
		public void TestCase ()
		{

			var content = Testing.ReadFromEmbeddedFile ("QR.tests.misc.login.json");
			Console.WriteLine (content);
		}
	}
}

