import splitfolders

INPUT_DIR = "/media/subait-malik-ml/datasets/satellite/full-scale/zoomed_imagery"
OUTPUT_DIR = "/media/subait-malik-ml/datasets/satellite/full-scale/zoomed_imagery_train"

#######################################
# FOR BALANCED DATASET ################
#######################################
# To only split into training and validation set, set a tuple to `ratio`, i.e, `(.8, .2)`.
# splitfolders.ratio("input_folder", output="output",
#     seed=1337, ratio=(.8, .1, .1), group_prefix=None, move=False) # default values

#######################################
# FOR IM-BALANCED DATASET ################
#######################################
# Split val/test with a fixed number of items, e.g. `(100, 100)`, for each set.
# To only split into training and validation set, use a single number to `fixed`, i.e., `10`.
# Set 3 values, e.g. `(300, 100, 100)`, to limit the number of training values.
splitfolders.fixed(
    input=INPUT_DIR,
    output=OUTPUT_DIR,
    seed=1337,
    fixed=(20, 10),
    oversample=True,
    group_prefix=None,
    move=False,
)
