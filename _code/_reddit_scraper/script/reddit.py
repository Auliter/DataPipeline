import subprocess
import json
import os
from pathlib import Path
from datetime import datetime

# get date
current_date = datetime.now().strftime("%Y-%m-%d")

# JSON path
base_directory = r"../URS/scrapes"
json_output_dir = os.path.join(base_directory, current_date, "subreddits")

# direction
urs_dir = "../URS"  # URS dir
urs_subdir = "urs"  # urs under URS

# scrape configure
subreddits = ["RealTesla", "TSLA", "teslainvestorsclub", "teslamotors"]
# subreddit = "RealTesla"
posts_count = 2000


# run URS
def run_urs(subreddit):
    # cd URS & cd urs
    os.chdir(os.path.join(urs_dir, urs_subdir))
    # construct scrape command
    urs_command = f"poetry run python Urs.py -r {subreddit} n {posts_count}"
    # run
    process = subprocess.Popen(urs_command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True)
    # input y
    output, errors = process.communicate(input='y\n')

    print(output)
    if errors:
        print("Errors:", errors)


def find_latest_json_file(directory):
    json_files = list(Path(directory).glob('*.json'))
    latest_file = max(json_files, key=os.path.getctime, default=None)
    return latest_file


def process_data():
    latest_json_file = find_latest_json_file(json_output_dir)
    if not latest_json_file:
        print("No JSON file found.")
        return

    with open(latest_json_file, 'r') as file:
        data = json.load(file)

    data_list = data['data']
    for item in data_list:
        if 'created_utc' in item:
            item['date'] = item.pop('created_utc')
        if 'title' in item:
            item['rawContent'] = item.pop('title')

    # rewrite
    with open(latest_json_file, 'w') as file:
        json.dump(data_list, file, indent=4)

    print(f"The original data file has been updated to only contain the data list: {latest_json_file}")


if __name__ == "__main__":
    for subreddit in subreddits:
        run_urs(subreddit)
        process_data()
