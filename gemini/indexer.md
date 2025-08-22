Search Engine
I have a large collection of podcast transcripts, organized in folders corresponding to the podcast they are from, that I want you to index those transcripts into an sqlite database.
Each transcript is structured as a list of objects, whereby each object has a time range and the corresponding text transcribed from that time.

The indexing procedure should be as follows:
1. For each podcast directory being processed note the name of the podcast and the language. If the language does not belong to a list of desired languages INDEXLANGUAGES, then skip the whole directory.
2. For each episode, note the name of the episode.
3. For each object in the transcript list note the time range
4. For each word in the transcribed text, which you have segmented and normalised according to an algorithm of your choosing but in any case using the language established in step 1, make an entry for that word as described below:

Word data
- word
- Number of occurrences

Entry data
- word
- language 
- Podcast name
- Episode name
- Time range
- Full text of  transcription object


Special Cases

1. Obviously I don’t want to explode the database with thousands of references to trivial words so, at a certain limit REFMAX, while building the index, I want the entry for that frequently occurring word to be reduced to a simple record of its existence and an indication that no further references should be added.

1. sometimes errors in transcription lead to junk objects which can be recognised because they are longer than usual and contain many (more than REPMAX) repetitions of the same word or character. These should be ignored,  and the rejected information logged to a separate file so I can check for false negatives.

Final Objective 

The resulting database should be suitable for a web app to use it to search for episodes where a particular word has been used.

