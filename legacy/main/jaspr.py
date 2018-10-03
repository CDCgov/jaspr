#!/usr/bin/env python
# file main/jaspr.py

"""A program to fit inhibition binding data.

The CDC Influenza Division Molecular Epidemology Team used to use
RoboSage, a Levenberg-Marquardt curve-fitting program implemented as an
Excel plugin, to fit inhibition binding data.  This program is intended
as a replacement to automate that functionality.

Curve fitting is handled through the LM package in scipy, and graphing though
matplotlib.

History:
    20080630 James Smagala: File created
    20080813 James Smagala: Project created, initial gui design and
                            functionality
    20080904 JS: Refactored swap_plates to work with inhibition
    20100415 JS: Heavy refactoring and additions to make jaspr more versitile
    20110926 JS: Added management of the graph generation option
    20110928 JS: Added help menu
    20140304 JS: Added blank configuration options

"""

# Python standard library imports
import sys
import os
import os.path
import webbrowser

# 3rd-party package imports
sys.path.extend('.')
import wx

# jaspr local imports
from gui.jaspr_gui import JasprGUIMainFrame
from lib.wx_shortcuts import save_file, pick_file, error_dialog
import lib.manage_config as manage_config
import lib.manage_key as manage_key
from lib.manage_data import JasprDataParser
from lib.analysis import JasprAnalysisManager


class JasprError(Exception):
    """Custom error class for inhibition specific errors"""
    pass


class JasprMainFrame(JasprGUIMainFrame):
    """Inherit from wxGlade-generated frame and add functionality"""

    def __init__(self, *args, **kwargs):
        super(JasprMainFrame, self).__init__(*args, **kwargs)
        self.version = 'v1.3'

        # add version info to the title
        self.SetTitle('jaspr %s - Inhibition Curve Fitting' % self.version)

        # add the experiment menu, based on config files
        self._set_experiment_menu()

        # set up an icon for the window
        icon = wx.Icon('icons/graph.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon) 

        # get a reference to the app object
        self.app = wx.GetApp()

        # bind events to handlers
        self.Bind(wx.EVT_CLOSE, self.OnExit)

    def _set_experiment_menu(self):
        """Build a dynamic menu based on config files"""
        self.configdir = os.path.join(os.getcwd(), 'config')
        default_experiment_name, generate_graphs, reverse_axis, \
                experiment_names, self.experiments = \
                manage_config.load_experiment_configs(self.configdir)
        self.gen_graph_menu_option.Check(generate_graphs)
        self.reverse_x_menu_option.Check(reverse_axis)

        self.experiment = self.experiments[default_experiment_name]
        self.experiment_menu = wx.Menu()
        for experiment_name in experiment_names:
            menu_item = wx.MenuItem(self.experiment_menu, wx.NewId(),
                    experiment_name,
                    self.experiments[experiment_name]['description'],
                    wx.ITEM_RADIO)
            self.experiment_menu.AppendItem(menu_item)
            self.Bind(wx.EVT_MENU, self.OnChangeExperiment, menu_item)
            if experiment_name == default_experiment_name:
                self.experiment_menu.Check(menu_item.Id, True)
        self.main_frame_menubar.Insert(2, self.experiment_menu, 'Experiment')

    def _write_default_config(self):
        """Get current menu options and save them"""
        experiment_name = ''
        for item in self.experiment_menu.GetMenuItems():
            if item.IsChecked():
                experiment_name = item.GetLabel()
                break

        generate_graphs = self.gen_graph_menu_option.IsChecked()
        reverse_axis = self.reverse_x_menu_option.IsChecked()
        manage_config.write_default_config(experiment_name,
                generate_graphs, reverse_axis, path=self.configdir)

    def OnChangeExperiment(self, event):
        """Change which type of experiment we are parsing"""
        self.experiment = self.experiments[
                self.experiment_menu.GetLabel(event.Id)]
        self._write_default_config()

    def OnGetExpFile(self, event):
        """Get the experiment file using a file picker"""
        path = pick_file(self, 'Pick an experiment file:')
        if path:
            self.exp_file_box.SetValue(path)
        event.Skip()

    def OnGetKeyFile(self, event):
        """Get the experiment key file using a file picker"""
        path = pick_file(self, 'Pick a key file:')
        if path:
            self.key_file_box.SetValue(path)
        event.Skip()

    def OnToggleGraphs(self, event):
        """Record the most recent setting for generating graphs."""
        self._write_default_config()

    def OnToggleAxis(self, event):
        """Record the most recent setting for generating graphs."""
        self._write_default_config()

    def OnHelp(self, event):
        """Display the help index.html file in a browser window."""
        if hasattr(sys, 'frozen'):
            path = sys.executable
            path = os.path.dirname(unicode(path, sys.getfilesystemencoding()))
            path = os.path.join(path, 'docs/index.html')
        else:
            path = __file__
            path = os.path.dirname(unicode(path, sys.getfilesystemencoding()))
            path = os.path.join(path, '../docs/index.html')
        webbrowser.open(os.path.normpath(path))

    def OnAbout(self, event):
        """Display a dialog about the jaspr software."""
        dialog = wx.MessageDialog(self, 'jaspr %s\nInhibition ' \
                'curve fitting software\nJames Smagala\n' \
                'CDC Influenza Division' % self.version, 'About jaspr',
                wx.OK|wx.ICON_INFORMATION)
        dialog.ShowModal()
        dialog.Destroy()

    def _get_raw_data(self):
        """Read in a raw data file from the instrument"""
        datafile_name = self.exp_file_box.GetValue()
        if not datafile_name:
            raise JasprError('Select an experiment file')
        try:
            parser = JasprDataParser()
            raw_data = parser(datafile_name)
        except :
            # FIXME add exception types
            raise JasprError('Error reading experiment file')
        return raw_data

    def _get_key(self):
        """Read in a key file"""
        keyfile_name = self.key_file_box.GetValue()
        if not keyfile_name:
            raise JasprError('Select a key file')
        try:
            return manage_key.read_keyfile(keyfile_name)
        except:
            # FIXME add exception types
            raise JasprError('Error reading key file')

    def OnRunAnalysis(self, event):
        """Analyze an experiment file"""
        try:
            drugs, ids = self._get_key()
            raw_data = self._get_raw_data()
            reverse_axis = self.reverse_x_menu_option.IsChecked()
            jam = JasprAnalysisManager(self.experiment, drugs, ids,
                    raw_data, reverse_axis)
            datafile_name = self.exp_file_box.GetValue()
            results_basename = os.path.splitext(os.path.split(
                    datafile_name)[1])[0] + '_results'
            results_filename = save_file(msg='Save the results file:',
                    default_file=results_basename + '.csv')
            os.startfile(jam.save_results(results_filename))
            if self.gen_graph_menu_option.IsChecked():
                graph_filename = save_file(msg='Save the graph file:',
                        default_file=results_basename + '.pdf')
                os.startfile(jam.save_graph(graph_filename))
        except Exception, e:
            # FIXME add exception types
            error_dialog(self, e)
        event.Skip()

    def OnKey(self, event):
        """Generate a new key file"""
        keyfile_name = save_file(self, msg='Save a new key file:',
                default_file='inhibition_key.csv')
        try:
            manage_key.write_key_template(keyfile_name,
                    self.experiment['drugs'])
            os.startfile(keyfile_name)
        except IOError:
            pass

    def OnExit(self, event):
        """Explicitly destroy this frame"""
        self.Destroy()
        self.app.Exit()


class JasprApp(wx.App):
    """The wx gui application manager for the inhibition app"""

    def OnInit(self):
        """Required setup for the applicaiton"""
        #wx.InitAllImageHandlers()

        # set a top level frame and show it
        main_frame = JasprMainFrame(None, -1, "")
        self.SetTopWindow(main_frame)
        main_frame.Show()

        # must retrun True or the applicaiton will exit
        return True


if __name__ == "__main__":

    def init_gui():
        """Run the inhibition gui interface"""
        app = JasprApp(redirect=False)
        app.MainLoop()

    init_gui()
