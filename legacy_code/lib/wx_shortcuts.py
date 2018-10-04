#!/usr/bin/env python
# file jaspr/lib/wx_shortcuts.py

"""Shortcuts for common wxPython tasks"""

# Third-party imports
import wx


def save_file(parent=None, msg='Save a file:', default_file=''):
    """Select a location to save a file to"""
    dialog = wx.FileDialog(parent, msg, defaultFile=default_file,
            style=wx.SAVE|wx.CHANGE_DIR|wx.OVERWRITE_PROMPT)
    new_file = ''
    if dialog.ShowModal() == wx.ID_OK:
        # this dialog was not canceled
        new_file = dialog.GetPath()
    dialog.Destroy()
    return new_file


def pick_file(parent=None, msg='Select a file:'):
    """Select a file"""
    new_file = ''
    dialog = wx.FileDialog(parent, msg, style=wx.OPEN|wx.CHANGE_DIR)
    if dialog.ShowModal() == wx.ID_OK:
        # this dialog was not canceled
        new_file = dialog.GetPath()
    dialog.Destroy()
    return new_file


def error_dialog(parent=None, msg='An unknown error occured'):
    """Display an error dialog"""
    msg = unicode(msg)
    dialog = wx.MessageDialog(parent, msg, caption='Error',
            style=wx.OK|wx.ICON_ERROR)
    dialog.ShowModal()
    dialog.Destroy()
