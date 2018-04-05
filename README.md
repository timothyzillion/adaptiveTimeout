# adaptiveTimeout

https://twitter.com/jmclulow/status/879362528911872000

In olden times, I wrote a quick and dirty fault detector for a piece of software:

https://github.com/greenplum-db/gpdb/blob/master/src/backend/fts/ftsprobe.c

It has static timeouts, but does a bunch of its outbound checks concurrently, which was an improvement of what that particular software had been doing previously.

My intent had been to update that code with a better, adaptive scheme. Around the time the quick&dirty version was written, someone sent me a copy of "The ϕ Accrual Failure Detector" by Hayashibara, Défago, Yared, and Katayama (2004). I've been thinking about it off and on ever since. I'm not including a link to the paper because I've had trouble finding one which is stable.

The basic idea is that a series of heartbeat messages are recorded, and then run against a threshold. In a fixed timeout system, the threshold would just be the timeout. In the Phi-accrual system, the threshold is a function given by the cumulative distribution of the normal distribution: where the parameters of the normal distribution are themselves given by the previous hearbeat times (generally over some fixed window of "recent" measurements).

The neat part about the Phi-accrual system is that it ties the timeout to a failure-model of the system, with a quantifiable notion of mistake-rate (see IV.A, "meaning of the value ϕ" in Hayashibara et al.): making the mistake-rate/fault-detect-time tradeoff explicit.

Recently, it seemed to me that the idea is simple enough, but useful enough, to make a good polyglot programming exercise.

Some helpful math links:
- https://en.wikipedia.org/wiki/Normal_distribution#Cumulative_distribution_function
- https://en.wikipedia.org/wiki/Error_function
- http://mathworld.wolfram.com/Erf.html
- https://www.mathworks.com/help/stats/normcdf.html
- https://www.johndcook.com/erf_and_normal_cdf.pdf
- https://www.wolframalpha.com/input/?i=1%2F2*(1%2B+erf(x%2Fsqrt(2)))
