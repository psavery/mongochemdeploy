import json

from flask import Flask
from flask import request

import openbabel_api as openbabel

app = Flask(__name__)


@app.route('/convert/<input_format>/<output_format>')
def convert(input_format, output_format):
    """Convert molecule data from one format to another via OpenBabel

    The input format and output format are specified in the path.
    The molecule data should be in the body (in json format) in the
    key "input".

    Some options may also be specified in the json body. The following
    options will be used in all cases other than the special ones:

        gen3d (bool): should we generate 3d coordinates?
        add_hydrogens (bool): should we add hydrogens?
        out_options (dict): what extra output options are there?

    Special cases are:
        output_format:
            svg: returns the SVG
            smi: returns canonical smiles
            inchi: returns json containing "inchi" and "inchikey"

    Curl example:
    curl -X GET 'http://localhost:5000/convert/smiles/inchi' \
      -H "Content-Type: application/json" -d '{"input": "CCO"}'

    """
    json_data = request.get_json()
    data = json_data['input']

    # Treat special cases with special functions
    out_lower = output_format.lower()
    if out_lower == 'svg':
        return openbabel.to_svg(data, input_format)
    elif out_lower in ['smiles', 'smi']:
        return openbabel.to_smiles(data, input_format)
    elif out_lower == 'inchi':
        inchi, inchikey = openbabel.to_inchi(data, input_format)
        d = {
            'inchi': inchi,
            'inchikey': inchikey
        }
        return json.dumps(d)

    # Check for a few specific arguments
    gen3d = json_data.get('gen3d', False)
    add_hydrogens = json_data.get('add_hydrogens', False)
    out_options = json_data.get('out_options', {})

    return openbabel.convert_str(data, input_format, output_format,
                                 gen3d=gen3d, add_hydrogens=add_hydrogens,
                                 out_options=out_options)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
