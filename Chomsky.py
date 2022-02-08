from string import ascii_letters
import copy
import json
import traceback
import jsbeautifier

# Remove large rules (more than 2 states in the right part, eg. A->BCD)
def large(rules,let,voc):

    # Make a hard copy of the dictionary (as its size is changing over the
    # process)
    new_dict = copy.deepcopy(rules)
    for key in new_dict:
        values = new_dict[key]
        for i in range(len(values)):
            # Check if we have a rule violation
            if len(values[i]) > 2:

                # A -> BCD gives 1) A-> BE (if E is the first "free"
                # letter from letters pool) and 2) E-> CD
                for j in range(0, len(values[i]) - 2):
                    # replace first rule
                    if j==0:
                        rules[key][i] = rules[key][i][0] + let[0]
                    # add new rules
                    else:
                        rules.setdefault(new_key, []).append(values[i][j] + let[0])
                    voc.append(let[0])
                    # save letter, as it'll be used in next rule
                    new_key = copy.deepcopy(let[0])
                    # remove letter from free letters list
                    let.remove(let[0])
                # last 2 letters remain always the same
                rules.setdefault(new_key, []).append(values[i][-2:])

    return rules,let,voc


# Remove empty rules (A->e)
def empty(rules,voc):

    # list with keys of empty rules
    e_list = []

    # find  non-terminal rules and add them in list
    new_dict = copy.deepcopy(rules)
    for key in new_dict:
        values = new_dict[key]
        for i in range(len(values)):
            # if key gives an empty state and is not in list, add it
            if values[i] == 'e' and key not in e_list:
                e_list.append(key)
                # remove empty state
                rules[key].remove(values[i])
        # if key doesn't contain any values, remove it from dictionary
        if len(rules[key]) == 0:
            if key not in rules:
                voc.remove(key)
            rules.pop(key, None)

    # delete empty rules
    new_dict = copy.deepcopy(rules)
    for key in new_dict:
        values = new_dict[key]
        for i in range(len(values)):
            # check for rules in the form A->BC or A->CB, where B is in e_list
            # and C in vocabulary
            if len(values[i]) == 2:
                # check for rule in the form A->BC, excluding the case that
                # gives A->A as a result)
                if values[i][0] in e_list and key!=values[i][1]:
                    rules.setdefault(key, []).append(values[i][1])
                # check for rule in the form A->CB, excluding the case that
                # gives A->A as a result)
                if values[i][1] in e_list and key!=values[i][0]:
                    if values[i][0]!=values[i][1]:
                        rules.setdefault(key, []).append(values[i][0])

    return rules,voc

# Remove short rules (A->B)
def short(rules,voc):

    # create a dictionary in the form letter:letter (at the beginning
    # D(A) = {A})
    terminals = dict(zip(voc, voc))

    # just transform value from string to list, to be able to insert more values
    for key in terminals:
        terminals[key] = list(terminals[key])

    # for every letter A of the vocabulary, if B->C, B in D(A) and C not in D(A)
    # add C in D(A)
    for letter in voc:
        for key in rules:
            if key in terminals[letter]:
                values = rules[key]
                for i in range(len(values)):
                    if len(values[i]) == 1 and values[i] not in terminals[letter]:
                        terminals.setdefault(letter, []).append(values[i])

    rules,terminals = short1(rules,terminals)
    return rules,terminals


def short1(rules,terminals):

    # remove short rules (with length in right side = 1)
    new_dict = copy.deepcopy(rules)
    for key in new_dict:
        values = new_dict[key]
        for i in range(len(values)):
            if len(values[i]) == 1:
                rules[key].remove(values[i])
        if len(rules[key]) == 0: rules.pop(key, None)

    # replace each rule A->BC with A->B'C', where B' in terminals(B) and C' in D(C)
    for key in rules:
        values = rules[key]
        for i in range(len(values)):
            # search all possible B' in D(B)
            for j in terminals[values[i][0]]:
                # search all possible C' in D(C)
                for k in terminals[values[i][1]]:
                    # concatenate B' and C' and insert a new rule
                    if j+k not in values:
                        rules.setdefault(key, []).append(j + k)

    return rules,terminals


# Insert rules S->BC for every A->BC where A in D(S)-{S}
def final_rules(rules,terminals,starter):

    for let in terminals[starter]:
        # check if a key has no values
        if not rules[starter] and not rules[let]:
            for v in rules[let]:
                if v not in rules[starter]:
                    rules.setdefault(starter, []).append(v)
    return rules

# Print rules
def print_rules(variables, terminals, rules, starter):
    auxRules = []
    for var in rules.keys():
        for rule in rules[var]:
            auxRules.append([var, rule])
    data = {}
    data["glc"] = [variables, terminals, auxRules, starter]
    json_data = json.dumps(data)
    options = jsbeautifier.default_options()
    options.indent_size = 2
    print(jsbeautifier.beautify(json_data, options))


def main(archive):

    rules = {}
    voc = []
    # This list's going to be our "letters pool" for naming new states
    let = list(ascii_letters[26:]) + list(ascii_letters[:25])

    let.remove('e')

    try: 
        file = open(archive)    
        try:
            data = json.load(file)
            variables = data['glc'][0]
            terminals = data['glc'][1]
            rules = data['glc'][2]                  # Number of grammar rules
            starter = data['glc'][3]
        except Exception as e:
            traceback.print_exc()
            print("\nSomething went wrong")
            print( f"Error: {e}\n")
        finally:
            file.close()
    except:
        print("Something went wrong when opening the file")
        print("To run the script use: python [path to main.py] [path to json]")

    

    # Initial state

    print('\nFinal rules')
    rules = final_rules(rules,terminals,starter)
    print_rules(rules)

if __name__ == "__main__":
    #print(f"size: {len(sys.argv)} & content: {sys.argv}")    
    main('G.json')