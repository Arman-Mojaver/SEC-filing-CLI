# Introduction

The following CLI retrieves the SEC filings of a company given its `cik` (Central Index Key) number.

The `cik` (Central Index Key) number can be found in the following link: 
https://www.sec.gov/edgar/searchedgar/cik'

# Instruccions to clone repository and run the CLI

1. Clone the repository.
   * `git glone https://github.com/Arman-Mojaver/Quartr.git`
2. Install dependencies:
   * `pip install click`
3. Execute following command:
   * `python main.py --help`

# Extra information

You can introduce unlimited `cik` numbers in the same command and all the filings will be retrieved and stored.

You can also place a file named `entities.json` in the running directory 
with `company names` (any name) as keys and `cik` numbers as values.
The CLI will retrieve and store all the `cik` numbers listed in the file.  

The corresponding filing will be stored in a directory named `Data` located in the same directory as the CLI.


# CLI Arguments and Options

There are several arguments and options that can be passed to the command to modify its default behaviour. Neither the arguments nor the options are required to run the CLI, they are all optional.

### Arguments
* `cik` (type: `string`, Default: `None`): the command accepts an unlimited amount of cik values

### Options
* `--form` (type: `string`, Default: `10-K`): SEC form types. Available form types:
  * `10-K`, `10-Q`, `25`, `25-NSE`, `3`, `3/A`, `4`, `4/A`, `424B2`, `8-A12B`, `8-K`, `8-K/A`, `CERT`, `CERTNYS`, `CORRESP`, `DEF 14A`, `DEFA14A`, `DFAN14A`, `FWP`, `IRANNOTICE`, `NO ACT`, `PRE 14A`, `PX14A6G`, `PX14A6N`, `S-3ASR`, `S-8`, `S-8 POS`, `SC 13G`, `SC 13G/A`, `SD`, `UPLOAD`


* `--user` (type: `string`, Default: `None`): User to make the request calls with.


* `--workers` (type: `int`, Default: `10`): Worker count to run the multiprocess with.


* `--chunk_size` (type: `int`, Default: `10`): Chunk size of requests made per user.

# Limitations
The CLI has the following limitations:
* The SEC API has a limitation of 10 requests / second per user. To bypass the restriction, the CLI generates users just in time to make the requests, allowing an unlimited amount of requests per command. However, the order of magnitude tested so far is <100 requests per command, so it is unclear whether the SEC API has some kind of IP block to restrict this kind of bypass (untested)


* The CLI creates a main directory called `Data` and one subdirectory for every company. However, it does not create another subdirectory for every type of SEC `form`, meaning that if for example the command is run for `Apple` once with `10-K`, and a second time with `10-Q`, all the filings would be located inside the `Apple` directory. It would not be possible to identify which files are `10-K` and which ones are `10-Q` just by looking at the folder, the files themselves would have to be opened individually to know its SEC form type
