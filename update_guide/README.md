## Guide to generate a new version of FAMAZOA


### 1. Get new apps from F-Droid
---

 1.1 **Download applications added after the last FAMAZOA's last release date**.

The next steps needs the [F-droid Crawler](https://github.com/brunomateus/f-droid-crawler). You should inform where the **F-droid Crawler** is located at your system. Then, execute the following command:

```
python get_new_apps_from_fdroid.py
```

Once the script finishes with success, you will find a json following using the name format **all\_apps\_from\_dd\_mm\_yyyy\_run\_dd\_mm\_yyyy.json** at same folder of the script.

1.2 **Find which applications has Kotlin code at the last commit**.

To find applications that hava Kotlin in the last commits, we follow to approach:

- For applications hosted on github, we use the Github API
  - **It is necessary to modify the script to inform a valid github username and password in order to query the Github API**
- For applications not hosted on github, we clone the repository and execute cloc

Execute these steps using the following command:




```
python extract_kotlin_apps.py --apps_list <input_file.json> --output <output_file.json>
```

- The **--apps_list** should be a json file resulting of the execution of the step 1.1.
- The **--output** will be stored in the result
- The execution log is saved in the file named **extracting.log**


### 2. Get new apps from AndroidTimeMachine

2.1 **Execute all steps to the package contained in repositories that have only one AndroidManifest.xml**

You will need to query  using **Google BigQuery**.

All the queries need are described [here](https://github.com/AndroidTimeMachine/open_source_android_apps/blob/master/doc/app-selection.md)

After step 3 described in the link above, execute the following query to get **package** declared on repositories that have only one **AndroidManifest.xml**.

```
SELECT
   DISTINCT(M1.package)
FROM `malavolta_v3.all_package_names` as M1
WHERE M1.repo_name in(
  SELECT repo_name as repo_one_manifest
  FROM `malavolta_v3.all_package_names`
  GROUP BY repo_name
  HAVING count(repo_name) = 1
)
```

Then download the **csv** containg the list of packages and repositories paths.

--
**For the next steps we need to use the [Android-app-search](https://github.com/S2-group/android-app-search).**

You also need to export you Github token:

```
export GITHUB_AUTH_TOKEN="1234abcd...xyz"
```

--

2.2 **Verify Package exists on Google Play**

First of all, it a good idea to remove duplicated packages from the **csv** resulting of the execution of the step **2.1**.

Moreover, it is necessary to create a file in the format need by the next step (one package per line).

The following command will generate a file with the correct format and without duplicated packages:

```
python remove_duplicate_packages.py <input_file> --output <output_file> 
```
- **input\_input**: The csv from the previous step
- **--output**: File to store the result. By default it will be store on the file **pkgs\_one\_manifest\_repo**

Execute the following command:

```
./gh_android_apps.py verify_play_link --input <input_file> --output <output_file> --include-403
```

- The input file should have one package per line
- The output file will have one package per line where these packages were found on GooglePlay

2.3 **Download Meta Data for Apps from Google Play**

Now it is necessary to download the meta data from the packages that are available on the Google Play Store.

As input of the following command you should use the output file from the previous step.

Moreover, the following environment variables are used:

- GOOGLE_LOGIN - email address used on a mobile phone.
- GOOGLE_PASSWORD - The password used to access the Play service.
- ANDROID_ID - the ID for the device for Google. This is the GSF ID not the id from dialing *#*#8255#*#*. You can get the gsf id e.g., using the [device id app](https://play.google.com/store/apps/details?id=com.evozi.deviceid&hl=en)

The execute this command:

```
./split_and_get_play_data.sh <file_package_list>
```

This script will break the list of packgage in 20 files, they will be stored inside a new folder called **pieces**, and for each of these files the following command will be executed:

```
./gh_android_apps.py get_play_data --input <piece_file> --outdir google_play_data --bulk_details-bin $bulk >> /dev/null 2>&1
```

- **piece_file**: file containg a portion of packages. Better strategy to lead with a possible exception raise by the **get\_play\_data** subcommand
- **outdir**: folder where the meta data will be store
- **bulk_details-bin**: path to [Node-google-play-cli](https://github.com/dweinstein/node-google-play-cli) binary. It's hardcoded.

If no piece\_file fail, the pieces folder will be removed. Otherwise, the **fail.log** will contain the name of the files which failed. In this case, run the command above manually for each file in the **fail.log**.

Check the number of files inside the **outdir**, the number of files there shoulb equals to the number of lines of **file\_package\_list**.

2.4 **Getting applications' package and repository released after last update**

To avoid uncessary queries to get the github metada, we can inform **start date** to next command. Then, the script will get the list of applications(packages) added on the Google Play Store after this **date**.

```
python -m helpers.filter_apps_by_date --start_date 2009-01-01 --details_dir google_play_data --output <filename>
```

- **--start_date**: The date of the last update
- **--details_dir**: Folder where metadata from google play is stored.
- **--output**: Output file. Default: **filtered_pkgs**.

2.5 **Generate csv to match repositories and packages**

```
generate_to_match.py [-h] [--output OUTPUT] all_repos repos_at_play
```
- **--output**: Output file. Defautl: to_match.csv
- **all\_repos**: csv from step 2.1
- **repos\_at\_play**: csv from step 2.4

Generete the file need to match repositories with applications

2.6 **Matching Github repositories with Android Application available at Google Play Store**

```
gh_android_apps.py -v match_packages --package_list <PACKAGE_LIST> --out <OUT> <google_play_data>
```
- **--package_list**: the output from step 2.6
- **--out**: a file to store the results
- **google\_play\_data**: Folder where the metadata from Google Play is stored

2.7 **Generating json with the matched packages for later to find out whether they have Kotlin**

```
python  -m helpers.get_matched_metadata --package_list matched_repos.csv  --details_dir google_play_data --output <output_file>
```
- **--package_list**: the output from step 2.7
- **--details_dir**: Folder where metadata from google play is stored.
- **--out**: a file to store the results

### 3. Merge the applications from both datasets

```
merge_datasets.py --dataset_1 FDROID_APPS --dataset_2
                         TIMEMACHINE_APPS --output OUTPUT
```

- **--dataset1**: The json file applications from F-droid
- **--dataset2**: The json file applications from AndroidTimeMachine
- **--output**: Output file to store the result

### 4. Generate a json containing the new apps and apps from previous version of FAMAZOA

Use the same command from the last step. Take a look in possible conflicts. These are shown at the output of the merge command.

```
merge_datasets.py --dataset1 FAMAZOA_OLD --dataset2
                         FAMAZOA_NEW --output OUTPUT
```

- **--dataset1**: The json file applications from the previous version of FAMAZOA
- **--dataset2**: The json file applications resulting of the last step
- **--output**: Output file to store the result