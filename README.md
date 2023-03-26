# Introduction

The following CLI retrieves the SEC filings of a company given its `cik` (Central Index Key) number.

The `cik` number can be found in the following link: 
https://www.sec.gov/edgar/searchedgar/cik

# Instructions to clone the repository and run the CLI

Open a terminal and execute the following commands

1. Clone the repository:
   * `git clone https://github.com/Arman-Mojaver/SEC-filing-CLI.git`


2. Go to the directory where the repository was cloned:
   * `cd SEC-filing-CLI`


3. Build the image:
   * `docker build . -t sec-filing-app`


4. Run the container:
   * `docker container run -it --rm sec-filing-app /bin/bash`


5. Execute the help function of the CLI:
   * `python main.py --help`


6. Execute the CLI:
   * `python main.py <args> <options>`

# Extra information

You can introduce unlimited `cik` numbers in the same command and all the filings will be retrieved and stored.

You can also place a file named `entities.json` in the running directory 
with `company names` (any name) as keys and `cik` numbers as values.
The CLI will retrieve and store all the `cik` numbers listed in the file.  

The corresponding filing will be stored in a directory named `Data` located in the same directory as the CLI.


# CLI Arguments and Options

There are several arguments and options that can be passed to the command to modify its default behaviour. Neither the arguments nor the options are required to run the CLI, they are all optional.

### Arguments
* `cik` (type: `string`, default: `None`): the command accepts an unlimited amount of cik values

### Options
* `--form` (type: `string`, default: `10-K`): SEC form types. Available form types:
  * `10-K`, `10-Q`, `25`, `25-NSE`, `3`, `3/A`, `4`, `4/A`, `424B2`, `8-A12B`, `8-K`, `8-K/A`, `CERT`, `CERTNYS`, `CORRESP`, `DEF 14A`, `DEFA14A`, `DFAN14A`, `FWP`, `IRANNOTICE`, `NO ACT`, `PRE 14A`, `PX14A6G`, `PX14A6N`, `S-3ASR`, `S-8`, `S-8 POS`, `SC 13G`, `SC 13G/A`, `SD`, `UPLOAD`


* `--user` (type: `string`, default: `None`): User to make the request calls with.


* `--workers` (type: `int`, default: `10`): Worker count to run the multiprocess with.


* `--chunk_size` (type: `int`, default: `10`): Chunk size of requests made per user.

# Limitations
The CLI has the following limitations:
* The SEC API has a limitation of 10 requests / second per user. To bypass the restriction, the CLI generates users just in time to make the requests, allowing an unlimited amount of requests per command. However, the order of magnitude tested so far is <100 requests per command, so it is unclear whether the SEC API has some kind of IP block to restrict this kind of bypass (untested)


* The CLI creates a main output directory called `Data` and one subdirectory for every company. However, it does not create another subdirectory for every type of SEC form type, meaning that if for example the command is run for `Apple` once with `10-K`, and a second time with `10-Q`, all the filings would be located inside the `Apple` directory. It would not be possible to identify which files are `10-K` and which ones are `10-Q` just by looking at the directory, the files themselves would have to be opened individually to know its SEC form type
