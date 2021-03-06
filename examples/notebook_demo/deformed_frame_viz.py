import time
import numpy as np
import meshcat
import meshcat.geometry as g
from copy import copy

def rgb_to_hex(rgb):
    """Return color as '0xrrggbb' for the given color values."""
    red = hex(int(255*rgb[0])).lstrip('0x')
    green = hex(int(255*rgb[1])).lstrip('0x')
    blue = hex(int(255*rgb[2])).lstrip('0x')
    return '0x{0:0>2}{1:0>2}{2:0>2}'.format(red, green, blue)

def meshcat_visualize_deformed(meshcat_vis, beam_disp, orig_shape, disc=10, scale=1.0, time_step=1):
    red = np.array([1.0, 0.0, 0.0])
    blue = np.array([0.0, 0.0, 1.0])
    white = np.array([1.0,1.0,1.0])
    pink = np.array([255.0,20.0,147.0]) / 255
    black = [.0, .0, .0]

    n_row, _ = beam_disp.shape
    n_row_orig, _ = orig_shape.shape
    ref_pt = np.array([0,0,0]) #beam_disp[0,:]
    e = np.ones(disc+1)
    ref_trans = np.outer(e, ref_pt)
    
    assert(int(n_row / disc) == int(n_row_orig / disc))
#     print('-----------')
    
    for k in range(int(n_row / (disc+1))):
        beam_pts = beam_disp[k*(disc+1):(k+1)*(disc+1),:]
        beam_pts = ref_trans + (beam_pts - ref_trans) * scale

        orig_beam_pts = orig_shape[k*(disc+1):(k+1)*(disc+1),:]
#         print(orig_beam_pts)
        scaled_orig_beam_pts = ref_trans + (orig_beam_pts - ref_trans) * scale
        
        delta = np.abs(np.subtract(beam_pts, scaled_orig_beam_pts))
        pt_delta = np.apply_along_axis(np.linalg.norm, 1, delta)
        if np.max(pt_delta) > 1e-30:
            pt_delta /= np.max(pt_delta)
            
        color = np.outer(white, e - pt_delta) + np.outer(pink, pt_delta)

        mc_key = 'deformed_' + str(k)
        for i in range(disc):
            mc_key_k = mc_key + str(i)
            meshcat_vis[mc_key_k].set_object(g.Line(g.PointsGeometry(beam_pts[i:i+2,:].T), g.MeshBasicMaterial(rgb_to_hex(color[:,i]))))
#             meshcat_vis[mc_key_k].set_object(g.Line(g.PointsGeometry(beam_pts[i:i+2,:].T), g.MeshBasicMaterial(rgb_to_hex(black),opacity=0.6)))

        or_key = 'original_' + str(k)
        meshcat_vis[or_key].set_object(g.Line(g.PointsGeometry(scaled_orig_beam_pts.T), g.MeshBasicMaterial(rgb_to_hex(black),opacity=0.6)))
        
#         time.sleep(time_step)