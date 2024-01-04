import fastdup

OUTPUT_DIR = "/mnt/sdc1/dl_work/rapidev_owlsense/datasets/classfication/to_train_splits"

TRAIN_DIR = OUTPUT_DIR + "/train"
VAL_DIR = OUTPUT_DIR + "/val"
TEST_DIR = OUTPUT_DIR + "/test"

fastdup.run(TRAIN_DIR)