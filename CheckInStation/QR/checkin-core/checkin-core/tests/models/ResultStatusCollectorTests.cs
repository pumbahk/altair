using NUnit.Framework;
using System;
using System.Linq;
using checkin.core.models;

namespace checkin.core
{
    [TestFixture ()]
    public class ResultStatusCollectorTests
    {
        [Test ()]
        public void Test_1TT_2T__True ()
        {
            var target = new ResultStatusCollector<int> ();
            target.AddSuccess (1);
            target.AddSuccess (1);
            target.AddSuccess (2);
            Assert.IsTrue (target.Status);
            CollectionAssert.AreEqual (new int[]{ 1, 2 }, target.Result ().SuccessList.ToArray ());
            CollectionAssert.AreEqual (new int[]{ }, target.Result ().FailureList.ToArray ());
        }

        [Test ()]
        public void Test_1TF_2T__False ()
        {
            var target = new ResultStatusCollector<int> ();
            target.AddSuccess (1);
            target.AddFailure (1);
            target.AddSuccess (2);
            Assert.IsFalse (target.Status);
            CollectionAssert.AreEqual (new int[]{ 2 }, target.Result ().SuccessList.ToArray ());
            CollectionAssert.AreEqual (new int[]{ 1 }, target.Result ().FailureList.ToArray ());
        }
    }
}

