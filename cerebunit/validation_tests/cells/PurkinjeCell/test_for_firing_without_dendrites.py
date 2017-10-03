# ============================================================================
# test_for_firing_without_dendrites.py
#
# created  03 Octoberber 2017 Lungsi
# modified  
#
# Use case:
# o first import the test
#   from cerebunit.validation_tests.cells.PurkinjeCell
#               import NoDendritesTest as noDendtest
# o experimental_data is the loaded json data wrapped
#   with python quantities. This is handled by the
#   HBP validation framework.
# o instantiate the noDendtest with experimental_data
#   test = noDendtest(experimental_data)
# o run the test on desired model
#   s = test.judge(desired_model, deep_error=True)
# o then you can see the outputs to
#   s
#   s.score
#   s.description
#
# ============================================================================

import sciunit
import quantities as pq
from elephant.statistics import mean_firing_rate as mfr

from cerebunit.capabilities.cells.response import ProducesSpikeTrain
from cerebunit.capabilities.cells.morphology import CanDisconnectDendrites
from cerebunit.score_manager import BinaryScore


class NoDendritesTest(sciunit.Test, BinaryScore):
    '''
    The No Dendrites Test is a test for whether firing occurs (from the soma) when all the dendrites are disconnected from the soma. There is no current injection for this test.
    '''
    required_capabilities = (CanDisconnectDendrites,ProducesSpikeTrain,)
    score_type = BinaryScore

    def generate_prediction(self, model, verbose=False):
        '''
        Generates spike train from "vm_soma", cell region.
        The function is automatically called by sciunit.Test
        which this test is a child of.
        Therefore as part of sciunit generate_prediction is
        mandatory.
        '''
        setup_parameters = { "dt": 0.025,   "celsius": 37,
                             "tstop": 1000, "v_init": -65 }
        model.disconnect_all_dendrites()
        model.set_simulation_properties(setup_parameters)
        model.produce_spike_train()
        return model

    def process_prediction(self, model):
        '''
        Once the model has run, this function can be used to
        process the spike_train prediction to get the
        prediction of interest, mean firing rate.
        '''
        cell_region = "vm_soma"
        x = mfr(model.predictions["spike_train"][cell_region])
        return x.rescale(pq.Hz)


    def compute_score(self, observation, model, verbose=False):
        '''
        This is function like generate_prediction is called
        automatically by sciunit which this test is a child of.
        This function with the same name compute_score is also
        therefore mandatory.
        This function calls the function process_prediction to
        return the mean firing rate of spike train from vm_soma.
        This is then compared against the experimental_data to
        get the binary score; 0 if the prediction correspond
        with experiment, otherwise 1.
        '''
        processed_prediction = self.process_prediction(model)
        a_prediction = processed_prediction.item() # just the magnitude
        x = BinaryScore.compute( observation, a_prediction )
        score = BinaryScore(x)
        score.description = "The No Dendrites attached to soma, Soma Firing test results in the prediction by the model to be " + str(processed_prediction) + " which means that the " + str(score)
        return score
