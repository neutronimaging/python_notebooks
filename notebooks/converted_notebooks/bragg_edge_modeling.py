# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Tools

# +
from matplotlib import pyplot as plt
import numpy as np, os, glob

from diffpy.Structure import loadStructure
import base64

from diffpy.structure.parsers import getParser
from bem import matter, xscalc, xtaloriprobmodel as xopm
# -

# %matplotlib inline

# # Isotropic Model

# calculate xs
import numpy as np
wavelengths = np.arange(0.05, 5.5, 0.001)
T = 300

# ## Manual input 

# create material
atoms = [matter.Atom('Ni0+', (0,0,0)), matter.Atom('Ni', (0.5, 0.5, 0)),
         matter.Atom('Ni', (0.5,0,0.5)), matter.Atom('Ni', (0, 0.5, 0.5))]
a=3.5238
alpha = 90.
lattice = matter.Lattice(a=a, b=a, c=a, alpha=alpha, beta=alpha, gamma=alpha)
fccNi = matter.Structure(atoms, lattice, sgid=225)

fccNi_1

calc = xscalc.XSCalculator(fccNi_1, T, max_diffraction_index=4)

# ## Using CIF file 

cif_file = "/Users/j35/git/NEUIT/static/cif/ni.cif"
#cif_file = "/Users/j35/git/NEUIT/static/cif/Cu.cif"
#cif_file = "/Users/j35/git/NEUIT/static/cif/EntryWithCollCode9805.cif"

# ### reading manually 

# +
with open(cif_file, 'r') as f:
    cif_file_content = f.read()

def parse_cif_upload(content):
    cif_s = content
    p = getParser('cif')
    struc = p.parse(cif_s)
    struc.sg = p.spacegroup
    return struc

fcc_2a = parse_cif_upload(cif_file_content)
# -

print(f"element: {fcc_2a[0].element}")
print(f"latice: {fcc_2a[0].lattice}")

# +
# fcc_2a[1].z

# +
# fcc_2a[0].lattice
# -

calc = xscalc.XSCalculator(fcc_2a, T, max_diffraction_index=4)

# ### reading via loadStructure 

# +
# fcc_2b = loadStructure(cif_file, fmt='cif')
# p = getParser('cif')
# # fcc_2.sg = p.spacegroup

# +
# fcc_2b

# +
# calc = xscalc.XSCalculator(fcc_2b, T, max_diffraction_index=4)
# -

# ## Calculation 

xs = calc.xs(wavelengths)

plt.plot(wavelengths, xs)



inc_inel_xs = [calc.xs_inc_inel(l) for l in wavelengths]
coh_el_xs = [calc.xs_coh_el(l) for l in wavelengths]
inc_el_xs = [calc.xs_inc_el(l) for l in wavelengths]
inel_xs = [calc.xs_inel(l) for l in wavelengths]
abs_xs = np.array([calc.xs_abs(l) for l in wavelengths])
plt.plot(wavelengths, inc_inel_xs, label='incoherent inelastic')
plt.plot(wavelengths, coh_el_xs, label='coherent elastic')
plt.plot(wavelengths, inc_el_xs, label='incoherent elastic')
plt.plot(wavelengths, inel_xs, label='inelastic')
plt.plot(wavelengths, abs_xs, label='absorption')
plt.plot(wavelengths, abs_xs+coh_el_xs+inc_el_xs+inel_xs+inc_inel_xs, label='sum')
plt.legend()

# # With texture

# +
texture_model = xopm.MarchDollase()
# by default, r for all hkl are 1.
# use the following form to change r
# make sure l>k>h
texture_model.r[(0,0,1)] = 2
# similarly beta can be changed
# texture_model.beta[(0,0,1)] = np.pi/2

calc = xscalc.XSCalculator(fccNi, T, texture_model)
# -

xs = calc.xs(wavelengths)

plt.plot(wavelengths, xs)

# # With size effect (dynamical diffraction)

# use keyword "size". unit: meter
calc = xscalc.XSCalculator(fccNi, T, size=10e-6)

xs = calc.xs(wavelengths)

plt.plot(wavelengths, xs)


