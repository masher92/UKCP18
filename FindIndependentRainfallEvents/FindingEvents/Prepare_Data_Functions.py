from collections import OrderedDict
import pickle
import glob
import iris
import warnings
import os 
import numpy as np

def filtered_cube (cube, filter_above):
    # cube = cube.copy()
    cube.data = np.where(cube.data < 0, np.nan, cube.data)
    cube.data = np.where(cube.data > filter_above, np.nan, cube.data)
    return cube 


def promote_scalar_to_dim_coord(cube, scalar_coord_name):
    """
    For when a cube just contains one time, so there is a scalar coordinate 'time'.
    Promote this to a dimension coordinate and remove the scalar coordinate
    
    Parameters:
        cube (iris.cube.Cube): The input cube with the scalar coordinate.
        scalar_coord_name (str): The name of the scalar coordinate to be promoted.
    
    Returns:
        iris.cube.Cube: The restructured cube with the scalar coordinate promoted to a dimension coordinate and removed from aux_coords.
    """
    # Extract the scalar coordinate
    scalar_coord = cube.coord(scalar_coord_name)
    
    # Create a new dimension coordinate from the scalar coordinate
    new_dim_coord = iris.coords.DimCoord([scalar_coord.points[0]], standard_name=scalar_coord.standard_name, units=scalar_coord.units)
    
    # Reshape the data array to include the new dimension
    new_shape = (1,) + cube.shape
    new_data = cube.data.reshape(new_shape)
    
    # Create a list of dimension coordinates and their dimensions
    dim_coords_and_dims = [(new_dim_coord, 0)]
    for dim, coord in enumerate(cube.dim_coords):
        if coord.standard_name != scalar_coord.standard_name:  # Skip the old scalar coord
            dim_coords_and_dims.append((coord, dim + 1))
    
    # Create a list of auxiliary coordinates without the scalar coordinate
    aux_coords = [coord for coord in cube.aux_coords if coord.standard_name != scalar_coord.standard_name]
    aux_coords_and_dims = [(coord, None) for coord in aux_coords]

    # Create the new cube
    new_cube = iris.cube.Cube(new_data, 
                              dim_coords_and_dims=dim_coords_and_dims, 
                              aux_coords_and_dims=aux_coords_and_dims)

    return new_cube


def remove_problematic_cubes(cube_list):
    """
    Iteratively remove problematic cubes to allow concatenation.
    Problematic cubes in this sense are those with dates that are outside the date range in the rest of the cubes
    
    Parameters:
        cube_list (iris.cube.CubeList): The list of cubes to process.
    
    Returns:
        iris.cube.Cube: The concatenated cube.
    """
    while True:
        problematic_cube_index = []
        start = 0

        # Attempt to concatenate cubes, identify problematic cubes
        for i, cube in enumerate(cube_list):
            try:
                concatenated_cube = cube_list[start:i+1].concatenate_cube()
            except Exception as e:
                print(f"Error concatenating cube {i}: {str(e)}")
                problematic_cube_index.append(i)
                start = i
        
        # If no problematic cubes, break the loop
        if not problematic_cube_index:
            break

        # Process and fix the problematic cubes
        for index in problematic_cube_index:
            try:
                cube = cube_list[index]
                # Example fix: Slice off the first time step
                cube = cube[1:,:,:]
                cube_list[index] = cube
            except Exception as e:
                print(f"Error processing cube {index}: {str(e)}")
                # Remove the cube if it cannot be fixed
                del cube_list[index]
        
        # If there are no more cubes to process, break the loop
        if not cube_list:
            raise RuntimeError("All cubes are problematic and cannot be concatenated.")
    
    # Final attempt to concatenate the cubes
    return cube_list.concatenate_cube()

# # Custom limited-size cache
# class LimitedSizeDict(OrderedDict):
#     def __init__(self, *args, max_size=100, **kwargs):
#         self.max_size = max_size
#         super().__init__(*args, **kwargs)

#     def __setitem__(self, key, value):
#         if len(self) >= self.max_size:
#             self.popitem(last=False)
#         OrderedDict.__setitem__(self, key, value)

def load_files_to_cubelist(year, filenames_pattern):
    filenames = [filename for filename in glob.glob(filenames_pattern) if '.nc' in filename]
    if not filenames:
        raise FileNotFoundError(f"No files found for the year {year} with pattern {filenames_pattern}")

    ## Load in data    
    cubes = iris.load(filenames)
    cubes = iris.cube.CubeList([cube for cube in cubes if has_named_dimension_coordinates(cube)])
    return cubes

def clean_cubes (cubes):
    
    ## Get the metadata from one cube, to apply to other cubes
    metadata = cubes[0].metadata
    time_metadata = cubes[0].coord('time').metadata
    
    for cube_num in range(0,len(cubes)):
        # Get this cube
        cube=cubes[cube_num]
        
        ## If cube only has one time dimension then promote it from scalar to dimension
        if len(cube.shape)<3:
            cube = promote_scalar_to_dim_coord(cube, 'time')
            print(f"promoted time from scalar to dimension for cube num {cube_num}")
        
        #### Remove coordinates that aren't the same on all cubes
        try:
            cube.remove_coord("forecast_period")
        except:
            pass
        try:
            cube.remove_coord("forecast_reference_time")
        except:
            pass
        
        #### Set the metadata to the values from the first cube
        cube.coord('time').metadata = time_metadata
        cube.metadata = metadata    
        
        #### Rename the cube 
        #if cube.name() != 'Rainfall rate Composite':
        #    print(f"Cube {cube_num + 1} name '{cube.name()}' does not match the desired name '{'Rainfall rate Composite'}'. Updating...")
        #    cube.rename('Rainfall rate Composite')
        #else:
        #    pass        
        
        ### Set the edited cube back on the cube list
        cubes[cube_num]=cube
    
    return cubes

def create_concated_cube(cubes):
    try:
        full_day_cube = cubes.concatenate_cube()
        print("Concatenation successful!")
    except Exception as e:
        print(f"Initial concatenation failed: {str(e)}")

        # If initial concatenation fails, remove problematic cubes and try again
        try:
            full_day_cube = remove_problematic_cubes(cubes)
            print("Concatenation successful after removing problematic cubes!")
        except RuntimeError as e:
            print(f"Concatenation failed after removing problematic cubes: {str(e)}")               
    
    return full_day_cube

def save_cube_as_pickle_file(cube, filepath):
    directory_path = filepath.rsplit('/', 1)[0]
    if not os.path.isdir(directory_path):
                os.makedirs(directory_path)
    
    with open(filepath, 'wb') as f:
        pickle.dump(cube, f)

def load_cube_from_picklefile(filepath):
    with open(filepath, 'rb') as f:
        return pickle.load(f)

def has_named_dimension_coordinates(cube):
    '''
    Some cubes don't have names so cause a problem when we try to load them.
    Here, we filter those out.
    '''
    
    # Check if any dimension coordinate has a name
    named_dim_coords = [coord for coord in cube.dim_coords if coord.standard_name or coord.long_name]

    # Return True if any dimension coordinate has a name
    return bool(named_dim_coords)