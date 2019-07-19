## Guide to generate a new version of FAMAZOA


### 1. Get new apps from F-Droid
---

 1.1 **Download applications added after the last FAMAZOA's last release date**.

The next steps needs the [F-droid Crawler](https://github.com/brunomateus/f-droid-crawler). You should inform where the **F-droid Crawler** is located at your system. Then, execute the following command:

```
python get_new_apps_famazoa.py
```

Once the script finishes with success, you will find a json following using the name format **all\_apps\_from\_dd\_mm\_yyyy\_run\_dd\_mm\_yyyy.json** at same folder of the script.

1.2 **Find which applications has Kotlin code at the last commit**.

To find applications that hava Kotlin in the last commits, we follow to approach:

- For applications hosted on github, we use the Github API
  - **It is necessary to modify the script to inform a valid github username and password in order to query the Github API**
- For applications not hosted on github, we clone the repository and execute cloc

Execute these steps using the following command:




```
python extract_kotlin_apps.py <input_file.json> <output_file.json>
```

- The **input_file** should be a json file resulting of the execution of the step 1.1.
- The **output_file** will be stored in the result
- The execution log is saved in the file named **extracting.log**


