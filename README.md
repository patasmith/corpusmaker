# Corpusmaker

Create a corpus for fine-tuning an OpenAI model.

# Table of contents

* [To run](#to-run)
  * [Caveats](#caveats)
* [Overview](#overview)
* [Example workflow](#example-workflow)
* [Command details](#command-details)
* [Roadmap](#roadmap)

# To run

1. `git clone https://github.com/patasmith/corpusmaker.git`
2. `poetry install`
3. `corpusmaker -h` or `corpusmaker <subcommand> -h` to see command help

## Caveats

Developed on Arch Linux using Python 3.11.8 and Poetry 1.8.2; may or may not work on other versions or operating systems.

Functionality is *extremely* limited at the moment. User is advised to make liberal use of a SQLite database browser to alter entries, and grep/sed/awk to sanitize the input text/output JSONL wherever necessary.

# Overview

This is a command-line program that can be used to procedurally construct a large corpus from text data, with the end of fine-tuning an OpenAI model for generative text.

First, you must have available one or more text files containing prose written in a style that you would like to replicate.

This is the general workflow:

- **Scene creation step:** The program can load text files into a SQLite database and automatically "chunk" them into what I call "scenes".

- **Summarization step:** Using each scene as a user prompt, along with a common system prompt, the program makes an API call to OpenAI and stores each response alongside the associated scene in the database.

- **Export step:** Finally, the program can export all scenes plus responses as a JSONL file in two formats, Chat Completion and Legacy Completion. In this JSONL file, the scene becomes the **completion** and the response becomes the **prompt**. You can provide a system prompt of your choosing for the Chat Completion format.

You can send this JSONL file to OpenAI via their fine-tuning API or the uploader on their website. It is suitable for fine-tuning a model that will generate text similar to your initial textfiles, given a prompt that is similar to the response obtained in the Summarization step.

The program is entirely geared towards creating corpuses for longform fiction generation, but you can use it for shorter text formats, as outlined in the example below.

# Example workflow

Let's say you run a retail website selling a wide variety of products. You have a list of three thousand product descriptions, and each description has been written to a specific format:

- One to three sentences long
- Starts with an action phrase, something the buyer can "do" with the product
- Follows a brand guideline, e.g. written using a distinctive vocabulary, certain words are avoided in favor of other words, etc.

You would like to be able to tell your model what product you would like described, and receive a description back that reads similarly to the descriptions in your list.

1. First, collect your product descriptions in one or more text files. Each description is separated by a newline. Perhaps you have 300 descriptions each stored in files named `description_1.txt`, `description_2.txt`, etc, up to `description_10.txt`.

Example excerpt from `description_8.txt`:
```
Making breakfast takes no time at all with this amazing toaster at your beck and call. Simply load it up with up to four slices of your favorite bread and enjoy the most perfect toast you've ever seen.
Breeze your way through the day in this linen jumpsuit that's a comfy choice for summer outings.
Need more pockets in your life? Bring along this handbag for ready access to everything you need for the day. Slip in your laptop, organize books and papers, and even tuck away your wallet for hands-free convenience.
```

2. Since each description is separated by a newline, you can use the newline as a separator. Load your description files into the database and define the newline as a separator using regex.

```bash
corpusmaker --db_file "sqlite:///products.sqlite3" import_files --filenames [description_*.txt] --separator '\n' --use_regex true
```

If you open the resulting sqlite file `products.sqlite3` in a database browser, you will see a raw_text table containing 10 entries.

3. Now you can chunk the entries in the *raw_text* table to individual descriptions.

```bash
corpusmaker --db_file "sqlite:///products.sqlite3" create_scenes
```

Your database will now contain a *scene* table with 3,000 entries, each one being a line from the original 10 text files.

4. At this point you can decide on a system prompt to use when creating your corpus.

Example `system_prompt.txt`:
```
The user will send you a product description of up to 3 sentences in length. You will respond according to this template:
NAME: a phrase up to 8 words in length that identifies the product being described (examples: yellow nail polish set; jumbo-size trombone; shelf painted with flowers)
COUNT: the number of sentences in the description: 1, 2, or 3.
```

5. It is time to get your responses using your database and your system prompt file.

```bash
corpusmaker --db_file "sqlite:///products.sqlite3" summarize_scenes --system_prompt_file system_prompt.txt --model gpt-3.5-turbo
```

The program will proceed to make API call after API call with each stored scene, saving each response as it comes in `products.sqlite3`. If this process gets interrupted, you can repeat the command and it will proceed where it left off, only obtaining responses for product descriptions that don't already have one.

This step will cost a variable amount of money and time depending on the model you're using and the amount of tokens contained in each scene.

6. Once you are finished with summarizing, you can create a JSONL file from your data.

You've decided to fine-tune a Chat Completion model, so you will need to provide the system prompt that you plan on using with the model when you are requesting product descriptions. This can be quite simple; since you will be training the model on so many examples, it will need no cajoling to respond in the correct format.

Example `finetune_system_prompt.txt`:
```
You write product descriptions.
```

Now run the command to generate the JSONL file:

```bash
corpusmaker --db_file "sqlite:///products.sqlite3" export_summaries --system_prompt_file finetune_system_prompt.txt --export_file products.jsonl --filter_for "NAME:"
```

Note: during the Summarization step, you may have received responses that did not fit your desired format. Thus, they are not responses you would like to train your model on. `filter_for` will ensure that the program only exports products that received a response containing the specified phrase.

You will now have a `products.jsonl` file that looks something like the following excerpt:
```json
{"messages": [{"role": "system", "content": "You write product descriptions."}, {"role": "user", "content": "NAME: four-slice toaster\nCOUNT: 2"}, {"role": "assistant", "content": "Making breakfast takes no time at all with this amazing toaster at your beck and call. Simply load it up with up to four slices of your favorite bread and enjoy the most perfect toast you've ever seen."}]}
{"messages": [{"role": "system", "content": "You write product descriptions."}, {"role": "user", "content": "NAME: linen jumpsuit\nCOUNT: 1"}, {"role": "assistant", "content": "Breeze your way through the day in this linen jumpsuit that's a comfy choice for summer outings."}]}
{"messages": [{"role": "system", "content": "You write product descriptions."}, {"role": "user", "content": "NAME: handbag with lots of pockets\nCOUNT: 1"}, {"role": "assistant", "content": "Need more pockets in your life? Bring along this handbag for ready access to everything you need for the day. Slip in your laptop, organize books and papers, and even tuck away your wallet for hands-free convenience."}]}
```

This file can be used with OpenAI's fine-tuning API ([see this guide](https://platform.openai.com/docs/guides/fine-tuning)) or with any service or tool that is compatible with a Chat Completions-formatted dataset.

# Command details

This is the general structure of a command:
```bash
corpusmaker <command flags> <subcommand> <subcommand flags>
```

The only command flag currently implemented (besides `-h` or `--help`) is `db_file`. If you would like to create or load a database file located at `data/my_database.db`, your command flag will look like this: ```--db_file "sqlite:///data/my_database"```. You could also use ```--db_file "sqlite://"``` to use a temporary in-memory database for testing.

Corpusmaker offers four subcommands, each with their own flags:

- `import_files`: Import textfile(s) into a SQLite database as a `raw_text` entry. This uses an md5 checksum to ensure that you cannot add duplicates.
  - `--filenames`: A list of files. You can pass individual files with `["myfile.txt", "myfile2.txt", "myfile3.txt"]`. Or you can pass a glob: `[myfile*.txt]`
  - `--separator` [OPTIONAL] (default: `""`): The separator you would like to assign to the files you are passing. You can pass a plain string, such as `"------"`, or a Python regex (see below), such as `"Chapter \d+"`. Separators are optional as the program can automatically chunk files without them.
  - `--regex` [OPTIONAL] (default: `false`): If you are using a regex separator, you must add the `--regex true` flag for it to be recognized.
- `create_scenes`: Chunk each `raw_text` into `scene` entries according to a separator and/or word limit. As with the above command, checksums are used to prevent duplicates from being added. This will only process `raw_text` entries that have not already been chunked into scenes.
  - `--word-limit` [OPTIONAL] (default: `8000`): The maximum word count for each chunk. Where separators are not present, text will be automatically chunked to this limit. Where separators are present, text will be chunked according to the separator; however any chunk that exceeds this limit will be repeatedly split in half until each subchunk is under the limit.
    - Note that word limit is only a rough approximation of token count. To figure out what you should set this to, take the token context length you are aiming for, multiply by 0.75, and subtract a rough amount: e.g. a token limit of 2048 suggests a word limit of 1536, which I would round down to 1300 or 1400 to be safe.
- `summarize_scenes`: Send each scene to the OpenAI API along with a common system prompt, and save the response. This will only process scenes that have not already been summarized; if the operation is interrupted, you can safely perform it again without resending data.
  - `--system-prompt-file` [OPTIONAL] (default: `data/summarization_system_prompt.txt`): The textfile that contains the system prompt you would like to use during the summarization process.
  - `--model` [OPTIONAL] (default: `gpt-3.5-turbo`): The name of the OpenAI model you would like to use for summarizing.
- `export_summaries`: Export scenes (as completions) and responses (as prompts) as JSONL files suitable for fine-tuning an OpenAI model.
  - `--system_prompt_file` [OPTIONAL] (default: `data/finetuning_system_prompt.txt`): The textfile that contains the system prompt you would like to use during the summarization process. This will likely be different/simpler than the prompt used during the summarization process.
  - `--export_file` [OPTIONAL] (default: `data/scenes_<current datetime>.jsonl`): The file where you would like to save the JSONL file.
  - `--filter_for` [OPTIONAL] (default: `""`): A scene will not be exported unless its summary contains this string.
  - `--chat` [OPTIONAL] (default: `true`): If true, exports in Chat Completions format. If false, exports in legacy Completions format.
  
# Roadmap

This is a quick-and-dirty project I made over the course of a week to do a number of things:
- Automate the process of making a corpus for a personal project.
- Learn test-driven development (TDD).
- Learn Poetry for Python package and dependency management.

Features I would like to add going forward:
- Shortened commandline flags
- Use token count from `tiktoken` as an alternative to `word_limit`
- More flexible export formatting for use with fine-tuning models hosted locally or with non-OpenAI services
- Supply customized API for summarization step
- Append or prepend text to user prompt/completions
- And many more...

Please open an issue if there are any features you would particularly like to see. Contributions are welcome!
