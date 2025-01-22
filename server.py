from flask import Flask, render_template, request
from base64 import b64encode
import striper
from io import BytesIO
import os
import yaml

import matplotlib
matplotlib.use('agg')

default_example = """
lmm_stripe_count:  6
lmm_stripe_size:   4194304
lmm_pattern:       raid0
lmm_layout_gen:    0
lmm_stripe_offset: 2
lmm_objects:
      - l_ost_idx: 2
        l_fid:     0x100020000:0x2:0x0
      - l_ost_idx: 3
        l_fid:     0x100030000:0x2:0x0
      - l_ost_idx: 4
        l_fid:     0x100040000:0x2:0x0
      - l_ost_idx: 5
        l_fid:     0x100050000:0x2:0x0
      - l_ost_idx: 0
        l_fid:     0x100000000:0x3:0x0
      - l_ost_idx: 1
        l_fid:     0x100010000:0x3:0x0
"""

folder_name = os.path.dirname(__file__)
app = Flask(__name__,template_folder=folder_name)

def to_yaml(input_yaml):
    try:
        data = yaml.safe_load(input_yaml)
    except yaml.YAMLError as exc:
        return None, input_yaml
    
    if 'mirrors' not in data:
        data = striper.convert_yaml(data)

    components = striper.parse_yaml(data)
    return components, yaml.dump(data)

@app.route('/', methods=['GET','POST'])
def stripe_plotter():
    input_yaml = request.form.get('input_yaml')
    if input_yaml is None:
        input_yaml = default_example
    data, clean_yaml = to_yaml(input_yaml) 
    
    striper.plt.clf()
    new_plt = striper.draw_extent_diagram(data)
    if new_plt is None:
        return render_template("stripe_plotter.html",image_data="",clean_yaml=clean_yaml)
    else:
        # Apply the new size
        fig = new_plt.gcf()
        original_size = fig.get_size_inches()
        fig.set_size_inches((original_size[0], original_size[1] * 1.5))
        new_plt.tight_layout(pad=0.5)

        image_io = BytesIO()
        new_plt.savefig(image_io, format='png')
        dataurl = b64encode(image_io.getvalue()).decode('ascii')
        return render_template("stripe_plotter.html",image_data=dataurl,clean_yaml=input_yaml)

if __name__ == "__main__":
    app.run(port=5078,debug=True)