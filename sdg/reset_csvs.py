from sdg.path import get_ids, input_path
import pandas as pd


# Define a function that identifies the list of indicators and generates
# new indicator files for each of them
def reset_all_csv(src_dir=''):
    """
    Reset the csv files with test data

    Args:
        src_dir: str. Project root. Expect to find the data
            directory here
    """

    status = True

    ids = get_ids(src_dir=src_dir)

    if len(ids) == 0:
        raise FileNotFoundError("No indicator IDs found")
    
    print("Resetting " + str(len(ids)) + " csv files...")
    
    # Create the test data sets
    blank_df = {
      'Year': [2015, 2015, 2015, 2016, 2016, 2016],
      'Group': ['A', 'B', '', 'A', 'B', ''],
      'Value': [1, 3, 2, 1, 3, 2]
    }
    blank_df = pd.DataFrame(
        blank_df, columns=['Year', 'Group', 'Value']
    )
    # Overwrite the csvs
    for inid in ids:
        csv_path = input_path(inid, ftype='data', src_dir=src_dir, must_work=True)
        blank_df.to_csv(csv_path, index=False)
