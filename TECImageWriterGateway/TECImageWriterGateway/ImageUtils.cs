using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Imaging;

namespace TECImageWriterGateway
{
    public class ImageUtils
    {
        public static Bitmap whiteAsAlpha(Bitmap img)
        {
            Bitmap retval = new Bitmap(img.Width, img.Height, PixelFormat.Format32bppArgb);
            for (int y = 0; y < img.Height; y++)
            {
                for (int x = 0; x < img.Width; x++)
                {
                    Color c = img.GetPixel(x, y);
                    if ((c.ToArgb() & 0xffffff) == 0xffffff)
                    {
                        c = Color.Transparent;
                    }
                    retval.SetPixel(x, y, c);
                }
            }
            return retval;
        }
    }
}
