using NUnit.Framework;
using System;
using NUnit.Framework.SyntaxHelpers;

namespace QR
{
	public class DummyConfigurator :Configurator
	{
		public Boolean called{ get; set; }

		public DummyConfigurator (IResource resource) : base (resource)
		{
			called = false;
		}
	}

	[TestFixture ()]
	public class ConfigratorTests
	{
		public void Includeme (IConfigrator config)
		{
			(config as DummyConfigurator).called = true;
		}

		[Test, Description ("includemeのチェック")]
		public void TestIncludeMe ()
		{
			var target = new DummyConfigurator (new Resource());
			Assert.IsFalse (target.called);

			Action<IConfigrator> includeme = this.Includeme;
			target.include (includeme);

			Assert.IsTrue (target.called);
		}

		[Test, Description ("app.configの読み取り異能")]
		public void TestAppSettingsValue ()
		{
			var target = new Configurator (new Resource());
			var value = target.AppSettingValue ("test.dummy.key");

			Assert.That (Is.Equals (value, "test-test-test"));
		}
	}
}

