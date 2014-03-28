﻿using QR.presentation.gui.control;
using System;
using System.Windows.Input;

public class DialogOpenCommand : ICommand
{

    public bool CanExecute(object parameter)
    {
        return true;
    }

    public event EventHandler CanExecuteChanged;

    public void Execute(object parameter)
    {
        (parameter as IDialog).Show();
    }
}
