using System;
using System.Collections.Generic;
using System.Text;
using System.Drawing;

namespace TECImageWriterGateway
{
    public enum RenderingResultType
    {
        Success,
        Fail
    }

    public class RenderingResult
    {
        public RenderingResultType type;
        public RenderingResultType Type { get { return type; } }

        public Image image;
        public Image Image { get { return image; } }

        public Exception exception;
        public Exception Exception { get { return exception; } }

        public RenderingResult(Image image)
        {
            this.type = RenderingResultType.Success;
            this.image = image;
            this.exception = null;
        }

        public RenderingResult(Exception exception)
        {
            this.type = RenderingResultType.Fail;
            this.image = null;
            this.exception = exception;
        }
    }
}
