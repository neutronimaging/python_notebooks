import numpy as np


def replace_nan_with_local_median(
    data: np.ndarray,
    kernel_size: tuple[int, int, int] = (3, 3, 3),
    max_iterations: int = 10,
) -> np.ndarray:
    """
    Replace NaN values in a 3D array using local median filtering.

    This function ONLY processes small neighborhoods around NaN pixels,
    avoiding expensive computation on the entire dataset.

    Parameters:
    -----------
    data : np.ndarray
        3D input array that may contain NaN values
    kernel_size : Tuple[int, int, int]
        Size of the kernel for median filtering in (height, width, depth) format
        Default is (3, 3, 3)
    max_iterations : int
        Maximum number of iterations to replace NaN values
        Default is 10

    Returns:
    --------
    np.ndarray
        Array with NaN values replaced by local median values
    """
    # Work on a copy to avoid modifying the original data
    result = data.copy()

    # Track initial NaN count
    initial_nan_count = np.sum(np.isnan(result))
    if initial_nan_count == 0:
        return result

    print(f"Starting efficient NaN replacement with kernel size {kernel_size}")
    print(f"Initial NaN count: {initial_nan_count}")

    # Calculate padding for kernel
    pad_h, pad_w, pad_d = [k // 2 for k in kernel_size]

    for iteration in range(max_iterations):
        # Find current NaN locations
        nan_coords = np.argwhere(np.isnan(result))
        current_nan_count = len(nan_coords)

        if current_nan_count == 0:
            print(f"All NaN values replaced after {iteration} iterations")
            break

        print(f"Iteration {iteration + 1}: {current_nan_count} NaN values remaining")

        # Process each NaN pixel individually
        replaced_count = 0
        for coord in nan_coords:
            y, x, z = coord

            # Define the local neighborhood bounds
            y_min = max(0, y - pad_h)
            y_max = min(result.shape[0], y + pad_h + 1)
            x_min = max(0, x - pad_w)
            x_max = min(result.shape[1], x + pad_w + 1)
            z_min = max(0, z - pad_d)
            z_max = min(result.shape[2], z + pad_d + 1)

            # Extract the local neighborhood
            neighborhood = result[y_min:y_max, x_min:x_max, z_min:z_max]

            # Get non-NaN values in the neighborhood
            valid_values = neighborhood[~np.isnan(neighborhood)]

            # If we have valid values, compute median and replace
            if len(valid_values) > 0:
                median_value = np.median(valid_values)
                result[y, x, z] = median_value
                replaced_count += 1

        print(f"  Replaced {replaced_count} NaN values in this iteration")

        # If no progress was made, break
        if replaced_count == 0:
            remaining_nan_count = np.sum(np.isnan(result))
            print(
                f"No progress made. {remaining_nan_count} NaN values could not be replaced"
            )
            print("(These may be in regions with no valid neighbors)")
            break

    final_nan_count = np.sum(np.isnan(result))
    print(f"Final NaN count: {final_nan_count}")
    print(f"Successfully replaced {initial_nan_count - final_nan_count} NaN values")

    return result
