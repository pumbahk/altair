using NLog;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using checkin.core.support;
using checkin.core.events;

namespace checkin.presentation.gui
{
    public class ProgressSingletonAction
    {
        private static Logger logger = LogManager.GetCurrentClassLogger();
        /// <summary>
        /// 各ケースでのsubmitをclosureで受け取る。多重リクエスト防止のための機能。failureの場合には復活させる。
        /// </summary>
        /// <param name="ctx"></param>
        /// <param name="ac"></param>
        /// <returns></returns>
        public static async Task ExecuteWhenWaiting(InputDataContext ctx, Func<Task> ac){
            if (ctx.Progress == DataContextProgress.waiting)
            {
                ctx.Progress = DataContextProgress.runnig;
                await ac();
                if (ctx.Event.Status == InternalEventStaus.failure){
                    ctx.Progress = DataContextProgress.waiting;
                } else {
                    ctx.Progress = DataContextProgress.finished;
                }
            }
            else
            {
                logger.Info("execute submit action is called. ignored. (ctx: {0})".WithMachineName(), ctx);
            }
        }
    }
}
