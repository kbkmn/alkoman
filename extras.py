import re

def pluralize(number, forms):
    number = abs(number) % 100

    number_1 = number % 10

    if number > 10 and number < 20:
        return forms[2]
    if number_1 > 1 and number_1 < 5:
        return forms[1]
    if number_1 == 1:
        return forms[0]

    return forms[2]

def check_for_kadyrov(message):
    if re.search(r'к[ао]дыров', message, re.I):
        return True
    
    return False

def check_for_words(dictionary, phrase):
    found = 0
    phrase = phrase.lower().replace(" ", "")


    for key, value in replace_dictionary.items():
        for letter in value:
            for phr in phrase:
                if letter == phr:
                    phrase = phrase.replace(phr, key)

    for word in dictionary:
        for part in range(len(phrase)):
            fragment = phrase[part: part+len(word)]
            if levenshtein_distance(fragment, word) <= len(word)*0.25:
                found += 1

    return found

def levenshtein_distance(a, b): 
    n, m = len(a), len(b)
    if n > m:
        a, b = b, a
        n, m = m, n

    current_row = range(n + 1)
    for i in range(1, m + 1):
        previous_row, current_row = current_row, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
            if a[j - 1] != b[i - 1]:
                change += 1
            current_row[j] = min(add, delete, change)

    return current_row[n]

replace_dictionary = {'а' : ['а', 'a', '@'],
  'б' : ['б', '6', 'b'],
  'в' : ['в', 'b', 'v'],
  'г' : ['г', 'r', 'g'],
  'д' : ['д', 'd'],
  'е' : ['е', 'e'],
  'ё' : ['ё', 'e'],
  'ж' : ['ж', 'zh', '*'],
  'з' : ['з', '3', 'z'],
  'и' : ['и', 'u', 'i'],
  'й' : ['й', 'u', 'i'],
  'к' : ['к', 'k', 'i{', '|{'],
  'л' : ['л', 'l', 'ji'],
  'м' : ['м', 'm'],
  'н' : ['н', 'h', 'n'],
  'о' : ['о', 'o', '0'],
  'п' : ['п', 'n', 'p'],
  'р' : ['р', 'r', 'p'],
  'с' : ['с', 'c', 's'],
  'т' : ['т', 'm', 't'],
  'у' : ['у', 'y', 'u'],
  'ф' : ['ф', 'f'],
  'х' : ['х', 'x', 'h' , '}{'],
  'ц' : ['ц', 'c', 'u,'],
  'ч' : ['ч', 'ch'],
  'ш' : ['ш', 'sh'],
  'щ' : ['щ', 'sch'],
  'ь' : ['ь', 'b'],
  'ы' : ['ы', 'bi'],
  'ъ' : ['ъ'],
  'э' : ['э', 'e'],
  'ю' : ['ю', 'io'],
  'я' : ['я', 'ya']
}