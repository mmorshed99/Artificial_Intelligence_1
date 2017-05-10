import math
import statistics
import warnings

import numpy as np
from hmmlearn.hmm import GaussianHMM
from sklearn.model_selection import KFold
from asl_utils import combine_sequences


class ModelSelector(object):
    '''
    base class for model selection (strategy design pattern)
    '''

    def __init__(self, all_word_sequences: dict, all_word_Xlengths: dict, this_word: str,
                 n_constant=3,
                 min_n_components=2, max_n_components=10,
                 random_state=14, verbose=False):
        self.words = all_word_sequences
        self.hwords = all_word_Xlengths
        self.sequences = all_word_sequences[this_word]
        self.X, self.lengths = all_word_Xlengths[this_word]
        self.this_word = this_word
        self.n_constant = n_constant
        self.min_n_components = min_n_components
        self.max_n_components = max_n_components
        self.random_state = random_state
        self.verbose = verbose

    def select(self):
        raise NotImplementedError

    def base_model(self, num_states):
        # with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        # warnings.filterwarnings("ignore", category=RuntimeWarning)
        try:
            hmm_model = GaussianHMM(n_components=num_states, covariance_type="diag", n_iter=1000,
                                    random_state=self.random_state, verbose=False).fit(self.X, self.lengths)
            if self.verbose:
                print("model created for {} with {} states".format(self.this_word, num_states))
            return hmm_model
        except:
            if self.verbose:
                print("failure on {} with {} states".format(self.this_word, num_states))
            return None


class SelectorConstant(ModelSelector):
    """ select the model with value self.n_constant

    """

    def select(self):
        """ select based on n_constant value

        :return: GaussianHMM object
        """
        best_num_components = self.n_constant
        return self.base_model(best_num_components)


class SelectorBIC(ModelSelector):
    """ select the model with the lowest Baysian Information Criterion(BIC) score

    http://www2.imm.dtu.dk/courses/02433/doc/ch6_slides.pdf
    Bayesian information criteria: BIC = -2 * logL + p * logN
    """

    def select(self):
        """ select the best model for self.this_word based on
        BIC score for n between self.min_n_components and self.max_n_components

        :return: GaussianHMM object
        """
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        # setting a default model and score at the beginning
        bic_score = 99999999999
        saved_model = self.base_model(self.n_constant)
        # iterating from min to max number of components
        for i in range(self.min_n_components,self.max_n_components + 1):
          try:
             #training the model
             hmm_model = GaussianHMM(n_components=i, covariance_type="diag", n_iter=1000,random_state=self.random_state, verbose=False).fit(self.X, self.lengths)
             # calculating to find the bic score
             logL = hmm_model.score(self.X, self.lengths)
             bic1 = -2 * logL
             num_data_points = len(self.X)
             num_features = len(self.X[0])
             num_params = i * i + 2 * i * num_features - 1
             bic2 = num_params * math.log(num_data_points)
             bic_current = bic1 + bic2
             #comparing the bic score with the previous one to look for a better one
             if bic_current < bic_score:
               saved_model = hmm_model
               bic_score = bic_current
          except:
           #if exception occurs, just continuing to next one 
           continue

        return saved_model

class SelectorDIC(ModelSelector):
    ''' select best model based on Discriminative Information Criterion

    Biem, Alain. "A model selection criterion for classification: Application to hmm topology optimization."
    Document Analysis and Recognition, 2003. Proceedings. Seventh International Conference on. IEEE, 2003.
    http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.58.6208&rep=rep1&type=pdf
    DIC = log(P(X(i)) - 1/(M-1)SUM(log(P(X(all but i))
    '''

    def select(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        # having the default score and model at the beginning
        dic_score = -99999999999
        saved_model = self.base_model(self.n_constant)
        # iterating through min to max number of components to find the best one
        for i in range(self.min_n_components,self.max_n_components + 1):
           try:
             # getting the model
             hmm_model = GaussianHMM(n_components=i, covariance_type="diag", n_iter=1000,random_state=self.random_state, verbose=False).fit(self.X, self.lengths)
             # getting the log likelihood of the current example
             logL_i = hmm_model.score(self.X, self.lengths)
           except:
             # if fails, will continue to next word
             continue
           logL_rest = 0
           # will get the model of all other examples to calculate dic score
           for key in self.words:
                if key == self.this_word:
                  continue
                X_temp, lengths_temp = self.hwords[key]
                try:
                  hmm_model_temp = GaussianHMM(n_components=i, covariance_type="diag", n_iter=1000,random_state=self.random_state, verbose=False).fit(X_temp, lengths_temp)
                  # accumulating log likelihood of all examples
                  logL_rest += hmm_model_temp.score(X_temp, lengths_temp)
                except:
                  continue
           coeff = 1 / (len(self.words) -1 )
           dic_current = logL_i - coeff * logL_rest
           # comparing for the best score
           if dic_current > dic_score:
                saved_model = hmm_model
                dic_score = dic_current

        return saved_model


class SelectorCV(ModelSelector):
    ''' select best model based on average log Likelihood of cross-validation folds

    '''

    def select(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        #Initializing and choosing number of folds
        best_logL = -9999999999
        
        split_method = KFold(n_splits=3, shuffle=False, random_state=None)
        # Iteraing through min to max components
        for i in range(self.min_n_components,self.max_n_components + 1):
         logL = 0
         try:
          # combining the data after choosing the indexes for training and test data
          for cv_train_idx, cv_test_idx in split_method.split(self.sequences):
            X_train, lengths_train = combine_sequences(cv_train_idx,self.sequences)
            X_test, lengths_test = combine_sequences(cv_test_idx,self.sequences)
            # getting model and computing log likelihood
            hmm_model = GaussianHMM(n_components=i, covariance_type="diag", n_iter=1000,random_state=self.random_state, verbose=False).fit(X_train, lengths_train)
            logL += hmm_model.score(X_test, lengths_test)
          logL = logL/3
          # comparing for best model
          if logL > best_logL :                                                                                                                                 
              best_logL = logL                                                                                                                                    
              best_model = GaussianHMM(n_components=i, covariance_type="diag", n_iter=1000,random_state=self.random_state, verbose=False).fit(self.X,self.lengths)
         except:
            # return default model in case of exception
            return self.base_model(self.n_constant)
        return best_model 
        
