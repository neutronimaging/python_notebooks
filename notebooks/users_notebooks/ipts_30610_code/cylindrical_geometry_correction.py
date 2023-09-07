import numpy as np


def number_of_pixel_at_that_position2(position=-1, inner_circle_r=1, outer_circle_r=1):
    #    new_position = np.abs(outer_circle_r - position)
    new_position = np.abs(position)

    if new_position < inner_circle_r:
        rp1 = 2 * inner_circle_r * np.sin(np.arccos(new_position / inner_circle_r))
        rp2 = 2 * outer_circle_r * np.sin(np.arccos(new_position / outer_circle_r))
        rp = rp2 - rp1
        return rp
    elif (new_position >= inner_circle_r) and (new_position < outer_circle_r):
        return 2 * outer_circle_r * np.sin(np.arccos(new_position / outer_circle_r))
    elif new_position == outer_circle_r:
        return 1
    else:
        return 0


def number_of_pixels_at_that_position1(position=0, radius=1):
    new_position = np.abs(radius - position)
    half_number_of_pixels = radius * np.sin(np.arccos(new_position / radius))
    if new_position == radius:
        return 1

    number_of_pixels = half_number_of_pixels * 2
    return number_of_pixels
