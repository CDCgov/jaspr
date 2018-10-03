#!/usr/bin/env python
# file jaspr/lib/manage_key.py

"""JASPR utilities for working with key files."""

# Python library imports
import csv


def write_key_template(keyfile_name, drugs):
    """Write a template key file"""
    rows = [('Drugs (listed in order)', ), ]
    rows.extend([(drug, ) for drug in drugs])
    rows.extend([('', ), ('ID', 'Strain Name (optional)', )])
    with open(keyfile_name, 'wb') as keyfile_handle:
        writer = csv.writer(keyfile_handle)
        writer.writerows(rows)


def read_keyfile(keyfile_name):
    """Read in a design file describing the experiment"""
    # read in the csv keyfile
    with open(keyfile_name, 'rb') as keyfile_handle:
        rows = [row for row in csv.reader(keyfile_handle)][1:]
    drugs = []
    ids = []
    state = 'drug_list'
    for row in rows:
        if state == 'drug_list':
            if not row or row[0].strip() == '':
                continue
            if row[0].startswith('ID'):
                state = 'sample_list'
                continue
            else:
                drugs.append(row[0].strip())
        elif state == 'sample_list':
            if not row or row[0].strip() == '':
                continue
            elif len(row) < 2:
                row.append('')
            if row[0].lower().strip() == 'blank':
                ids.append(('', ''))
            else:
                ids.append((row[0].strip(), row[1].strip(), ))
    return drugs, ids
