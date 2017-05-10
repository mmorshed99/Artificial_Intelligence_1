import warnings
from asl_data import SinglesData


def recognize(models: dict, test_set: SinglesData):
    """ Recognize test word sequences from word models set

   :param models: dict of trained models
       {'SOMEWORD': GaussianHMM model object, 'SOMEOTHERWORD': GaussianHMM model object, ...}
   :param test_set: SinglesData object
   :return: (list, list)  as probabilities, guesses
       both lists are ordered by the test set word_id
       probabilities is a list of dictionaries where each key a word and value is Log Liklihood
           [{SOMEWORD': LogLvalue, 'SOMEOTHERWORD' LogLvalue, ... },
            {SOMEWORD': LogLvalue, 'SOMEOTHERWORD' LogLvalue, ... },
            ]
       guesses is a list of the best guess words ordered by the test set word_id
           ['WORDGUESS0', 'WORDGUESS1', 'WORDGUESS2',...]
   """
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    probabilities = []
    guesses = []
    # TODO implement the recognizer
    for each_item in test_set._data:
       
       current_test_word_logl = {}
       X, lengths = test_set.get_item_Xlengths(each_item)
       for each_model in models:
          try:  
            logL = models[each_model].score(X, lengths)
            current_test_word_logl[each_model] =  logL

          except:
            current_test_word_logl[each_model] =  -9999999999
       probabilities.append(current_test_word_logl)
       current_logl = -9999999999
       for each_guess in current_test_word_logl:
          if current_test_word_logl[each_guess] > current_logl:
            best_word = each_guess
            current_logl = current_test_word_logl[each_guess]
       guesses.append(best_word) 
    return (probabilities, guesses)
