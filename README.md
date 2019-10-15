# S3 Backup

For backing up S3 buckets to local folders using python 3.

There are four steps to backup happiness...


## 1. Install

Check out the code and install requirements, either with [pip][pip]:

```shell
$ pip install -r requirements.txt
```

Or [pipenv][pipenv]:

```shell
$ pipenv install
$ pipenv shell
```


## 2. Create a config file

Create a `config.yaml` file at the same level as `backup.py`.

For each AWS account that you want to backup, enter the details about what you
want to sync. It's possible to sync multiple directories for each account.
For example:

```yaml
---
mysite-production:
  paths:
    - remote: s3://mysite-assets-production
      local: ~/Sites/mysite-assets-production
      delete: yes
my-database-backups:
  paths:
    - remote: s3://database_backups/postgres-dragon-12345
      local: ~/Documents/backups/databases/dragon
      delete: no
    - remote: s3://database_backups/other-site/mysql-backups
      local: ~/Documents/backups/databases/other-site
      delete: no
```

The starting `---` line is an optional YAML start marker. Note that indention
is important with YAML. [Here's a tutorial.][yaml]

The top-level list items (such as `mysite-production`) are profile names, as used
when setting up AWS credentials (see below).

Each one has a `paths` list. That contains one or more dictionaries with the
following keys:

* `remote` – The path to an S3 bucket, or folder within a bucket, to be backed
    up.

* `local` – The path to a folder on the local filesystem into which the files
    from `remote` will be put.

* `delete` – By default local files will not be deleted if they don't exist in
    the remote bucket. Setting `delete` to `yes`, `true`, `1`,
    [etc.][bool] will delete local files so that the local copy matches the
    contents of the remote bucket or folder exactly.

If there are problems with your YAML file, use [a validator][validator] to make
sure it's OK.


## 3. Set up AWS credentials

For each AWS account, set up the credentials as a named profile using the `aws`
command, as [described in the docs][aws-config]:

```shell
$ aws configure --profile mysite-production
AWS Access Key ID [None]: YOURKEYHERE
AWS Secret Access Key [None]: YOURSECRETKEYHERE
Default region name [None]: your-region
Default output format [None]: text
```

The region is something like `us-east-1` or `eu-west-2`. I'm not sure that it's
needed in this situation, for only downloading things.

The profile name should match the name(s) used in `config.yaml` exactly.


## 4. Run it

```shell
$ ./backup.py
```

Or as a dry-run. It will display the commands that would be run, and the files
that would be downloaded, but nothing is downloaded:

```shell
$ ./backup.py --dryrun
```

[pip]: https://pip.pypa.io/en/stable/
[pipenv]: https://pipenv.readthedocs.io/en/latest/
[yaml]: https://gettaurus.org/docs/YAMLTutorial/
[bool]: https://yaml.org/type/bool.html
[validator]: https://yaml.org/type/bool.html
[aws-config]: https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html#cli-quick-configuration-multi-profiles

----

From: https://github.com/philgyford/s3-backup  
By: Phil Gyford  
Email: phil@gyford.com  
Website: https://www.gyford.com
