import os
import subprocess
import jinja2
import json

import openchemistry as oc


def run_calculation(geometry_file, output_file, params, scratch_dir):
    # Read in the geometry from the geometry file
    # This container expects the geometry file to be in .xyz format
    with open(geometry_file) as f:
        xyz_structure = f.read()
        # remove the first two lines in the xyz file
        # (i.e. number of atom and optional comment)
        xyz_structure = xyz_structure.split('\n')[2:]
        xyz_structure = '\n  '.join(xyz_structure)

    # Read the input parameters
    theory = params.get('theory', 'hf')
    task = params.get('task', 'energy')
    basis = params.get('basis', 'cc-pvdz')
    functional = params.get('functional', 'b3lyp')
    charge = params.get('charge', 0)
    multiplicity = params.get('multiplicity', 1)

    theory = theory.lower()
    if theory == 'ks':
        _theory = 'dft'
    elif theory == 'hf':
        _theory = 'scf'
    else:
        _theory = theory

    reference = theory.lower()

    if multiplicity == 1:
        reference = 'r' + reference
    else:
        reference = 'u' + reference

    optimization = params.get('optimization', None)
    vibrational = params.get('vibrational', None)
    charge = params.get('charge', 0)
    multiplicity = params.get('multiplicity', 1)
    theory = params.get('theory', 'scf')
    functional = params.get('functional', 'b3lyp')
    basis = params.get('basis', 'cc-pvdz')

    context = {
        'task': task,
        'theory': _theory,
        'reference': reference,
        'charge': charge,
        'multiplicity': multiplicity,
        'basis': basis,
    }

    if context['task'] == 'freq':
        context['freq'] = 'task {} {}' .format(_theory, 'freq')
    elif context['task'] == 'optimize':
        context['optimize'] = task

    if _theory == 'dft':
        context['functional'] = functional
    else:
        # We update the multiplicity key when using scf. SCF accept names and
        # not numbers.
        multiplicities = {'1': 'singlet', '2': 'doublet', '3': 'triplet'}
        context['multiplicity'] = multiplicities[str(multiplicity)]

    # Combine the input parameters and geometry into a concrete input file
    # that can be executed by the simulation code
    template_path = os.path.dirname(__file__)
    jinja2_env = \
        jinja2.Environment(loader=jinja2.FileSystemLoader(template_path),
                           trim_blocks=True)

    os.makedirs(scratch_dir, exist_ok=True)
    os.chdir(scratch_dir)
    raw_input_file = os.path.join(scratch_dir, 'raw.in')
    raw_output_file = os.path.join(scratch_dir, 'raw.json')

    with open(raw_input_file, 'wb') as f:
        if _theory == 'dft':
            jinja2_env.get_template('nwchem.in.j2').stream(**context, xyz_structure=xyz_structure).dump(f, encoding='utf8')
        else:
            jinja2_env.get_template('nwchem.sfc.in.j2').stream(**context, xyz_structure=xyz_structure).dump(f, encoding='utf8')

    # Execute the code and write to output
    cpus = 4
    subprocess.run(['mpirun', '-np', str(cpus), "/opt/nwchem/bin/LINUX64/nwchem",
                   raw_input_file, raw_output_file])

    # Convert the raw output file generated by the code execution, into the
    # output format declared in the container description (cjson)
    with open(raw_output_file) as f:
        cjson = oc.NWChemJsonReader(f).read()

    # Save the calculation parameters in the cjson output for future reference
    cjson['inputParameters'] = params

    with open(output_file, 'w') as f:
        json.dump(cjson, f)