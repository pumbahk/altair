using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;

namespace TECImageWriterGateway
{
    public partial class BootstrapForm : Form
    {
        RendererForm rendererForm;

        public BootstrapForm()
        {
            InitializeComponent();
            rendererForm = new RendererForm();
            rendererForm.Show();
        }

        private void button1_Click(object sender, EventArgs e)
        {
            OpenFileDialog d = new OpenFileDialog();
            d.Multiselect = false;
            DialogResult result = d.ShowDialog();
            if (result == DialogResult.OK)
            {
                rendererForm.Show();
                rendererForm.Render(
                    new System.Uri(d.FileName),
                    delegate(Image image)
                    {
                        pictureBox1.Invoke(
                            new MethodInvoker(
                                delegate
                                {
                                    pictureBox1.Image = image;
                                }
                            )
                        );
                    }
                );
            }
        }

        private void BootstrapForm_FormClosed(object sender, FormClosedEventArgs e)
        {
            rendererForm.Close();
        }
    }
}