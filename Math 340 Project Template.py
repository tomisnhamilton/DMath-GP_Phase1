#use these ffive global variables to set the directories for your data and output files for each
#phase.  P.S.  Don't tell Dr Fagin I'm using global variables.  I distinctly remember him telling
#me not to while standing on a soap box in CS210
import os

T1_data_path="./data/T1/data/"
T2_data_path= "./data/T2/data/"
T2_soln_path="./data/T2/soln/"
T3_data_path="./data/T3/data/"
T3_soln_path="./data/T3/soln/"

#This function reads a priorities CSV file and returns the priorities in a single data structure
#as follows:  The top level data structure is a dictionary with two entries.  Each entry is
#indexed by a string that also serves as the prefix for each entity to be paired.  For example,
#when reading size_6_priorities.csv, the two top level keys are 'B' (for blue) and 'R' (for red).
#The values stored in the top level dictionary are two more dictionaries.  This lower level
#dictionary is indexed by an entity name (e.g. 'B3' or 'R2' from size_6_priorities.csv).  The
#lower level dictionary values are lists that indicate priorities from most desired to least
#desired.  For example, calling priorities['B']['B3'][1] would return 'R2' indicating that R2
#is B3's second choice mate.
def read_priorities(csv_filepath):
    priorities={}
    file=open(csv_filepath,"r")
    lines=file.read().split("\n")
    for line in lines:
        if line:
            tokens=line.split(",")
            label=tokens[0].strip(':')
            row_priorities=[]
            for token in tokens[1:]:
                if token.strip()!="":
                    row_priorities.append(token.strip())
            if label[0] in priorities:
                priorities[label[0]][label]=row_priorities
            else:
                priorities[label[0]]={}
                priorities[label[0]][label]=row_priorities
    file.close()
    return priorities

#This function prints a priorities structure from a file to the console.
def show_priorities(csv_path):
    priorities=read_priorities(csv_path)
    for key in priorities:
        for row in priorities[key]:
            print(row,end=": ")
            for col in priorities[key][row]:
                print(col,end=", ")
            print("")
        print("")
    return 0

#This funciton reads a set of pairings from a CSV file and returns a dictionary as described:
#The entities that were designated as boys during pairing are used as the keys in the
#dictionary.  The values that are stored are the entities that the boys ended up paired to.
#For example, after reading size_6_pairings_0.csv, pairs['B2'] would return 'R4' indicating
#B2 was paired with R4.
def read_pairs(csv_filename):
    pairs={}
    file=open(csv_filename,"r")
    lines=file.read().split("\n")
    for line in lines:
        if line:
            tokens=line.split(",")
            label=tokens[0].strip(": ")
            pairs[label]=tokens[1]
    file.close()
    return pairs

#This function writes a pairs structure (as defined in the comment for read_pairs() to a CSV
#at the filepath given as a parameter.
def write_pairs(csv_filename,pairs):
    of=open(csv_filename,"w")
    for boy in pairs:
        of.write(boy)
        of.write(":,")
        of.write(pairs[boy])
        of.write("\n")
    of.close()
    return 0


#This function should test Hall's conditions on a graph defined in a priorities CSV file.  It
#will ensure that all members of the boys set can be paired to a girl from the girls set.  It
#makes no guarantees that all girls can be paired to a boy.  I wrote it to return "pass" or
#"fail" as strings.
def test_halls(priorities_filename,boy_set_label,girl_set_label):
    #This helper function generates and returns the powerset of the input collection (with the
    #exception of null set).
    #source: https://stackoverflow.com/questions/1482308/how-to-get-all-subsets-of-a-set-powerset
    def powerset(iterable):
        from itertools import chain, combinations
        s = list(iterable)
        return chain.from_iterable(combinations(s, r) for r in range(1,len(s)+1))

    # Hall's Condition
    priorities = read_priorities(priorities_filename)
    # Get preferences for boys and girls
    boy_preferences = priorities[boy_set_label]
    girl_preferences = priorities[girl_set_label]

    # Test Hall's condition for every subset of boys
    for subset_boys in powerset(boy_preferences):
        girls_subsets = set(girl for boy in subset_boys for girl in boy_preferences[boy])
        if len(girls_subsets) < len(subset_boys) or any(len(girl_preferences[girl]) < 1 for girl in girls_subsets):
            return 'fail'

    return 'pass'

#this is where you will test whether a set of proposed pairings are stable or not.  It should
#return a set of touples.  Each touple represents a rogue pairing.  A stable pairing should
#return an empty set.
def find_rogues(pairs_filename, priorities_filename):
    # identify rogue pairings

    pairs = read_pairs(pairs_filename)
    priorities = read_priorities(priorities_filename)

    rogues = set()

    # Invert pairs for easy look-up from girls to boys
    reverse_pairs = {v: k for k, v in pairs.items()}

    for boy, paired_girl in pairs.items():
        # Check if the boy is in the priorities, if not, skip to the next iteration
        if boy not in priorities['B']:
            continue

        boy_preferences = priorities['B'][boy]
        for preferred_girl in boy_preferences:
            if preferred_girl == paired_girl:
                break  # The boy's current partner is found in his preferences before any potential rogue, stop searching

            # Check if the preferred girl and her current boy are in the priorities, if not, continue to the next preferred girl
            if preferred_girl not in reverse_pairs or preferred_girl not in priorities['R'] or reverse_pairs[
                preferred_girl] not in priorities['B']:
                continue

            preferred_girl_current_boy = reverse_pairs[preferred_girl]
            preferred_girl_preferences = priorities['R'][preferred_girl]

            # Check if the preferred girl ranks this boy higher than her current pairing
            if boy in preferred_girl_preferences and preferred_girl_preferences.index(
                    boy) < preferred_girl_preferences.index(preferred_girl_current_boy):
                rogues.add((boy, preferred_girl))
    # Return the set of rogue pairs
    return rogues


#This is where you need to implement the Gale-Shapley algorithm on a set of priorities defined
#in a CSV file located by the csv_path parameter.  boy_set_label and girl_set_label are strings
#used to label the boy set and the girl set.  Each label are also used as a prefix for each
#individual boy and girl.  Boys propose to girls and girls reject boys as described in the
#assigned videos.  This function should return a dictionary where the indexes are the boys
#and the values are the girls.
def pair(csv_path,boy_set_label,girl_set_label):
    #TODO: implement the Gale-Shapley algorithm

    priorities = read_priorities(csv_path)  # Assume correct implementation

    free_boys = set(priorities[boy_set_label].keys())
    engagements = {}  # Stores final pairings
    proposals_made = {boy: [] for boy in free_boys}  # Tracks proposals

    while free_boys:
        for boy in list(free_boys):  # Iterate over a snapshot of free_boys
            boy_prefs = priorities[boy_set_label][boy]
            for girl in boy_prefs:
                if girl in proposals_made[boy]:
                    continue  # Skip if this boy has already proposed to this girl
                proposals_made[boy].append(girl)  # Mark this girl as proposed by this boy

                # Check if the girl is either not engaged or prefers this boy over her current partner
                if girl not in engagements or (
                        girl in priorities[girl_set_label] and priorities[girl_set_label][girl].index(boy) <
                        priorities[girl_set_label][girl].index(engagements[girl])):
                    # If girl is already engaged, make her current partner free again
                    if girl in engagements:
                        free_boys.add(engagements[girl])
                    engagements[girl] = boy  # Engage this boy with the girl
                    free_boys.remove(boy)  # This boy is now engaged and not free
                    break  # Move on to the next free boy

    # Inverting engagements to have boys as keys and girls as values
    return {v: k for k, v in engagements.items()}

#This is the main program.  For each of the three tasks you've been assigned, it has code to loop
#through all the files provided.  My suggestion is that you only use it once you have each task
#working as desired by uncommenting the calls to each task as appropriate.  Use the test() function
#as your main program as you're developing and debugging.
def main():
    def task_1():
        #test Hall's Condition for each
        for size in (6,10,20):
            for file in range(1,5):
                print("size "+str(size)+" file "+str(file),end=": ")
                halls_result=test_halls(T1_data_path+"size"+str(size)+"-"+str(file)+".txt",'B','R')
                print(halls_result)
        return 0            

    def task_2():
        #find rogue pairs for each proposed
        for size in (6,10,25,100):
            for pairing in(0,1,2,3):
                rogues=find_rogues(T2_data_path+"size_"+str(size)+"_pairings_"+str(pairing)+".csv", T2_data_path+"size_"+str(size)+"_priorities.csv")
                of=open(T2_soln_path+"size_"+str(size)+"_rogues_"+str(pairing)+".txt","w")
                of.write(str(rogues))
                of.close()
        return 0
    
    def task_3():
        #generate the blue and red optimal solutions for each
        for size in (6,10,25,100):
            priorities_filename=T3_data_path+"size_"+str(size)+"_priorities.csv"
            pairs=pair(priorities_filename,'B','R')
            write_pairs(T3_soln_path+"size_"+str(size)+"_B-R_soln.csv",pairs)
            pairs=pair(priorities_filename,'R','B')
            write_pairs(T3_soln_path+"size_"+str(size)+"_R-B_soln.csv",pairs)
        return 0
    
    #task_1()#test Hall's Condition for each
    #task_2()#find rogue pairs for each proposed
    task_3()#generate the blue and red optimal solutions for each

    return 0
   
#As stated in the comment for main(), I suggest you use this as the main program while you're
#developing and debugging.  Once you have one of your tasks working, uncomment the call to
#each task as appropriate and call main() instead of test() at the bottom by toggeling
# whether each of those lines are commented out
def test():

    return 0

#Here's where main() and/or test() gets executed when you run this script.
main()
#test()
