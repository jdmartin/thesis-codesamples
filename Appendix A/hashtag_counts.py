#N.B. Yeah, this script will run in n^n, but what can you do?

#utility
import os
import csv
import pandas as pd

hashtag_files = []
count_files = []

def generate_hashtag_file_list():
    basepath = 'output/hashtags'
    for fname in os.listdir(basepath):
        if fname == '.DS_Store':
            continue
        path = os.path.join(basepath, fname)
        if os.path.isdir(path):
            # skip directories
            continue
        hashtag_files.append(path)

def generate_count_file_list():
    basepath = 'output/hashtags/with_user_counts'
    for fname in os.listdir(basepath):
        if fname == '.DS_Store':
            continue
        path = os.path.join(basepath, fname)
        if os.path.isdir(path):
            # skip directories
            continue
        count_files.append(path)

def clean_word(word):
    #Again, I know.  But strip(punctuation) takes the '#', too, and counts go insane.
    #And yes, I should use a regex for domain suffixes... but there aren't that many, and I'd rather catch errors in analysis...
    for ch in [',', '.', '!', '?', ';', ':', '"', '(', ')', '“', '\'', '…', '.ca']:
        word = word.replace(ch, '')
        #People who have lots of new lines in tweets cause problems.  I'm here to fix those problems.
        word = word.replace('\n', ' ').replace('\r', '')
    return word

def do_the_counts():
    for file in hashtag_files:
        with open(file, 'r') as hashtag_file:
            #Prepare the output path by stripping the file name from the source path and appending it to the output path.
            fname = file.split('/')[2]
            output_path = 'output/hashtags/with_user_counts/' + fname
            print("\n" + "Starting: " + fname + "\n")
            with open(output_path, 'w') as csvfile:
                csvfile.write('hashtag' + ',' + 'raw_count' + ',' + 'unique_users' + "\n")
                tags = {}
                counts = {}

                hashtags_read = csv.reader(hashtag_file)
                #Skip the Header Row
                next(hashtags_read, None)
                for row in hashtags_read:
                    #Get current number of occurrences of hashtag from second column of csv and store in instances
                    tags[row[0]] = int(row[1])
                #Now, for each tag in this set of tags, get the number of unique users employing it.
                for tag in tags.keys():
                    users = 0
                    unique_users = []
                    #Open the Raw archive for this set of hashtags.
                    f = open("data" + "/" + fname, 'r')
                    csv_f = csv.reader(f)
                    #Skip the Header Row
                    next(csv_f, None)

                    #If it's only one instance of a tag, then it's only one user.
                    if int(tags[tag]) == 1:
                        counts[tag] = 1

                    #For Tags with a greater frequency than one, determine unique users.
                    if int(tags[tag]) > 1:
                        for row in csv_f:
                            #Check the body text for the current hashtag.
                            #Tiny guard against counting #dhsi1 as present, even when only #dhsi19 is.
                            bag_of_words = row[2].split(' ')
                            for word in bag_of_words:
                                #If the tag is there, check if you've seen this user before.  If not, add it to unique_users, increment count by 1.
                                if tag == clean_word(word):
                                    if unique_users.count(row[1]) >= 1:
                                        break
                                    if unique_users.count(row[1]) < 1:
                                        unique_users.append(row[1])
                                        users += 1
                                    break
                        counts[tag] = users

                    #Report output to user, write line of csv file.
                    print(tag, tags[tag], counts[tag])
                    csvfile.write(str(tag) + "," + str(tags[tag]) + "," + str(counts[tag]) + "\n")

        f.close()
        hashtag_file.close()
        csvfile.close()

        #Now, let's sort those files by the number of users, not the number of occurrences
        df = pd.read_csv(output_path)
        df = df.sort_values(['raw_count','unique_users'],ascending=(False, False))
        outfile = open(output_path, 'w')
        df.to_csv(outfile, index=False)
        outfile.close()

def do_some_stats():
    for file in count_files:
        with open(file, 'r') as count_file:
            #Prepare the output path by stripping the file name from the source path and appending it to the output path.
            fname = file.split('/')[3]
            output_path = 'output/hashtags/with_user_counts/' + fname
            print("\n" + "Doing stats on: " + fname + "\n")

            #Prepare to process the file and create a placeholder... also, add the header
            temp_output = []
            temp_output.append(('hashtag', 'raw_count', 'unique_users', 'percent_unique', 'percent of total'))

            ###Do Some Math

            #Open the existing archive for this set of hashtags.
            f = open(output_path, 'r')
            csv_f = csv.reader(f)
            

            #Get Total Number of hashtags in file
            num_tweets = 0
            for row in csv_f:
                if row[1] != 'raw_count':
                    num_tweets += int(row[1])

                    percent_unique = (int(row[2]) / int(row[1])) * 100
                    percent_of_total = (int(row[2]) / num_tweets) * 100

                    #Append row to temp_output
                    temp_output.append((row[0], row[1], row[2], str(round(percent_unique, 6)), str(percent_of_total)))
        
        #Open the file and write out temp_output
        with open(output_path, 'w') as output_file:
            writer = csv.writer(output_file, delimiter=',', lineterminator="\n")
            writer.writerows(temp_output)
                            

    count_file.close()
    output_file.close()
    f.close()

#TODO - use argv to either a) generate everything, or b) just refresh the stats.  This will save me time.
generate_hashtag_file_list()
do_the_counts()
generate_count_file_list()
do_some_stats()
