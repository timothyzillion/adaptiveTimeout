"""
Implements an Adaptive Timeout using the phi-accrual method.

Callers configure with a window-size given as a number of samples.

Callers add samples with heartbeat times to update internal state.
Callers can ask "is system up" given a time from last heartbeat.
"""
import Queue
import math

class AdaptiveTimeout:
    def __init__(self, windowSize=5, minSigma=0.001):
        self.mean = 0.0
        self.sigma = 0.0
        self.sum_of_samples = 0.0
        self.sum_of_squares = 0.0
        self.minSigma = minSigma
        self.q = Queue.Queue(maxsize=windowSize)

    def update(self, time_since_last_heartbeat):
        """
        Call this for every heartbeat received.

        We're calculating variance as the average of the squares minus the
        square of the average.

        https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance#Online_algorithm
        https://en.wikipedia.org/wiki/Standard_deviation
        """
        newSample = float(time_since_last_heartbeat)
        newSquare = newSample*newSample
        if self.q.full():
            oldSample, oldSquare = self.q.get()
            self.sum_of_samples = self.sum_of_samples - oldSample
            self.sum_of_squares = self.sum_of_squares - oldSquare

        newTuple = (newSample, newSquare)
        self.q.put(newTuple)
        self.sum_of_samples = self.sum_of_samples + newSample
        self.sum_of_squares = self.sum_of_squares + newSquare

        count = self.q.qsize()
        self.mean = self.sum_of_samples / float(count)
        if count > 2:
            average_of_squares = self.sum_of_squares / float(count)
            variance = average_of_squares - (self.mean * self.mean)
        else:
            # completely made-up variance until we have three samples.
            variance = self.mean/2.0
        self.sigma = max(math.sqrt(variance), self.minSigma)

    def phi(self, time_since_last_heartbeat):
        """
        we're trying to calculate
        Phi == -Log10(1 - Normal_Cumulative_Distribution_Function)

        NCDF(x, mean, sigma) == NCDF((x-mean)/sigma, 0, 1)
        NCDF(x, 0, 1) == (1/2) (1 + erf( x / sqrt(2)))
        where erf is the error-function

        The Hayashibara et al P_later function is 1-NCDF
        P_later = 1 - NCDF(x)
        phi = -log10(P_later)

        Python's math lib has the complementary error-function (erfc)
        erfc(x)/2 = (1-NCDF) === P_later
        https://en.wikipedia.org/wiki/Normal_distribution#Cumulative_distribution_function
        https://en.wikipedia.org/wiki/Error_function
        """
        x = (time_since_last_heartbeat - self.mean) / self.sigma
        #ncdf = 0.5 * (1 + math.erf(x / math.sqrt(2)))
        #ret= -math.log10(1 - ncdf)

        p_later = (math.erfc(x))/2.0
        ret = -math.log10(p_later)
        return ret

    def alive(self, time_since_last_heartbeat, threshold):
        """
        Call this periodically to see if the current time is "out of bounds"
        for our current notion of "liveness."
        
        Threshold is given in error-terms:
        1 ==> 10% chance of error given model
        2 ==> 1% chance of error
        3 ==> 0.1% chance of error
        and so on.
        """

        # if we don't have enough info yet, assume we're alive
        # we always require two heartbeats.
        if self.q.qsize() < 2:
            return True
        phi = self.phi(time_since_last_heartbeat)
        return phi < threshold
        
if __name__ == "__main__":
    # do some tests
    at = AdaptiveTimeout(3)
    at.update(1)
    at.update(10)
    import pdb
    pdb.set_trace()
    print at.mean, at.sigma
    print "phi(20): ", at.phi(20)
    print "phi(1): ", at.phi(1)
    print "phi(2): ", at.phi(2)
    exit(0)
