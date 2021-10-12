using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace MagicOfHistoryDialog
{
    public partial class MainApp : Form
    {
        public MainApp()
        {
            InitializeComponent();
        }

        private void label1_Click(object sender, EventArgs e)
        {

        }

        private void btnCancel_Click(object sender, EventArgs e)
        {
            this.Close();
        }

        private void MainApp_Load(object sender, EventArgs e)
        {
            string[] args = Environment.GetCommandLineArgs();
            textboxQuestion.Text = args[1];
            listboxAnswer.Items.AddRange(args[2].Split(';'));
            listboxAnswer.SelectedIndex = 0;
        }

        private void btnAdd_Click(object sender, EventArgs e)
        {
            if ((textboxQuestion.Text.Length > 0) && (listboxAnswer.Text.Length >0)) {
                string ansfile = @"Answers.csv";
                using (StreamWriter sw = File.AppendText(ansfile))
                    sw.WriteLine($"{textboxQuestion.Text};{listboxAnswer.Text}");
                MessageBox.Show("Added Successfully.");
                this.Close();
            } else
            {
                MessageBox.Show("Question and answer can't be empty.");
            }
        }
    }
}
