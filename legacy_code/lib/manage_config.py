#!/usr/bin/env python
# file jaspr/lib/manage_config.py

"""JASPR utilities for working with config files."""

# Python library imports
import os
import sys
import ConfigParser

# Third-party imports
import wx

sys.path.append('.')


class JasprConfigParserError(Exception):
    """Error for badly formed jaspr config files"""
    pass


class JasprConfigParser(ConfigParser.SafeConfigParser):
    """Add validation"""

    def get(self, *args, **kwargs):
        return ConfigParser.SafeConfigParser.get(self, *args, **kwargs).strip()

    def get_valid(self, section, option, acceptable_values):
        value = self.get(section, option)
        if not value in acceptable_values:
            msg = 'Unrecognized %s.%s value: %s' % (section, option, value)
            raise jasprConfigParserError(msg)
        return value


def load_experiment_configs(path='config'):
    """Load config filesfor various experiment types"""

    def _check_concs(orientation, concs):
        """Ensure that the plate orientation and concs work together"""
        max_length = 11 if orientation == 'row' else 8
        if len(concs) > max_length:
            msg = 'Dilution series too long for %s orientation' % orientation
            raise BadJasprConfigError(msg)
        if any([conc < 0 for conc in concs]):
            msg = 'Dilution series contains negative number'
            raise BadJasprConfigError(msg)
        if not concs[-1] == float(0):
            msg = 'Last concentration is not zero'
            raise BadJasprConfigError(msg)

    def _parse_csv_floats(csv_str):
        """Parse a csv string into a list of floats"""
        try:
            return [float(conc) for conc in csv_str.split(',')]
        except ValueError:
            msg = 'Bad concentration string: %s' % csv_str
            raise ValueError(msg)

    def _build_experiment(parser):
        """Build a single experiment definition"""
        experiment = {}

        # parse the name section
        experiment['name'] = parser.get('experiment', 'name')
        experiment['description'] = parser.get('experiment', 'description')

        # parse the plate section
        experiment['orientation'] = \
                parser.get_valid('plate', 'orientation', ('row', 'col'))
        experiment['reverse_dilution'] = \
                parser.getboolean('plate', 'reverse_dilution')

        # parse the detection section
        experiment['detection_method'] = parser.get('detection', 'method')
        experiment['detection_units'] = parser.get('detection', 'units')

        # parse the drug section
        drugs = [drug.strip() for drug in
                parser.get('drug', 'drugs').split(',')]
        experiment['drugs'] = drugs
        concs = _parse_csv_floats(parser.get('drug', 'concs'))
        _check_concs(experiment['orientation'], concs)
        experiment['concs'] = concs
        experiment['conc_unit'] = parser.get('drug', 'conc_unit')
        experiment['graph_zero'] = parser.get('drug', 'graph_zero')
        return experiment['name'], experiment

    config_errors = (ConfigParser.MissingSectionHeaderError, 
            ConfigParser.NoSectionError, ConfigParser.NoOptionError, )
    default_experiment_name = None
    experiments = {}
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            # attempt to read a config file
            parser = JasprConfigParser()
            try:
                parser.read(os.path.join(dirpath, filename))
            except ConfigParser.ParsingError:
                continue
            # the default file lists only the name of the default experiment
            if filename.endswith('default_settings'):
                try:
                    parser.read(filename)
                    default_experiment_name = parser.get('selected', 'name')
                    generate_graphs = \
                            parser.getboolean('selected', 'generate_graphs')
                    reverse_axis = \
                            parser.getboolean('selected', 'reverse_axis')
                except config_errors:
                    pass
            # this is an experiment definition file
            else:
                try:
                    experiment_name, experiment = _build_experiment(parser)
                except config_errors:
                    pass
                else:
                    experiments[experiment_name] = experiment
    # get an alphabetical ordering of experiment names so that things
    # show up in a stable position in the menues
    experiment_names = experiments.keys()
    experiment_names.sort()
    if not default_experiment_name in experiments:
        default_experiment_name = experiment_names[0]
    return default_experiment_name, generate_graphs, reverse_axis, \
            experiment_names, experiments


def write_default_config(default_name, generate_graphs, reverse_axis,
        path='config'):
    """Write out the default experiment name to the default config file"""
    writer = ConfigParser.SafeConfigParser()
    writer.add_section('selected')
    writer.set('selected', 'name', default_name)
    writer.set('selected', 'generate_graphs', str(generate_graphs))
    writer.set('selected', 'reverse_axis', str(reverse_axis))
    with open(os.path.join(path, 'default_settings'), 'wb') as filehandle:
        writer.write(filehandle)


if __name__ == '__main__':

    def main():
        """Print the results of parsing config files"""
        from pprint import pprint
        default_experiment_name, experiment_names, experiments = \
                load_experiment_configs()
        print 'selected: %s' % default_experiment_name
        pprint(experiment_names)
        pprint(experiments)

    main()
