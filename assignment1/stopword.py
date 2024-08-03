# Ask user to enter the file path
#cacm_file = input("Enter the file path: ")

def main():
    # open stopwords.txt
    f = open("../cacm/stopwords.txt", "r")
    # open the file
    main_file = open("../cacm/cacm.all", "r+")
    # create the file that stores the new text
    reduced_file = open("../cacm/reduced.txt", "w")
    stop_words = []
    for word in f:
        # append stopwords.txt word by word
        stop_words.append(word.lower().split("\n")[0])
    for line in main_file:
        modified_line = []
        for word in line.split():
            # checks if the word is not in stopwords.txt
            if word.lower() not in stop_words:
                modified_line.append(word)
        line_to_write = ' '.join(modified_line)
        reduced_file.write(line_to_write + '\n')
    reduced_file.close()
    main_file.close()
    f.close()
main()
