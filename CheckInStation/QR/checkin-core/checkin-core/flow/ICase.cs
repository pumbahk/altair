using System;
using System.Threading.Tasks;
using checkin.core.models;
using checkin.core.events;

namespace checkin.core.flow
{
    /// <summary>
    /// Caseの使われ方
    /// Case.configure(); if(Case.Verify()) then Case.OnSuccess() else Case.OnFailure();
    /// </summary>
    public interface ICase
    {
        IResource Resource{ get; set; }
        string Description { get;}
        IInternalEvent PresentationChanel { get; set; }

        /// <summary>
        /// ユーザーが入力をする前に実行されるメソッド
        /// </summary>
        /// <returns>The async.</returns>
        /// <param name="ev">Ev.</param>
        Task PrepareAsync (IInternalEvent ev);

        Task PrepareAsync ();

        ICase OnSuccess (IFlow flow);

        ICase OnFailure (IFlow flow);

        /// <summary>
        /// ユーザが入力した後い実行されるメソッド。このメソッドの戻り値いよってOnSuccess,OnFailureが呼ばれるか決まる
        /// </summary>
        /// <returns>The async.</returns>
        Task<bool> VerifyAsync ();
    }
}

