"""Direct rational point-metric cross-check; no NumPy or primary metric imports."""
from collections import defaultdict
from fractions import Fraction


def compute(labels, decisions, probabilities):
    n = len(labels)
    if not n or len(decisions) != n or len(probabilities) != n:
        raise ValueError('unaligned metric inputs')
    tp = tn = fp = fn = 0
    squared = Fraction(0)
    bins = defaultdict(lambda: [0, Fraction(0), 0])
    for y, decision, p in zip(labels, decisions, probabilities):
        if type(y) is not int or y not in (0, 1) or type(decision) is not bool:
            raise ValueError('invalid label/decision')
        if not isinstance(p, Fraction) or not 0 <= p <= 1:
            raise ValueError('invalid probability')
        if y == 1 and decision:
            tp += 1
        elif y == 1:
            fn += 1
        elif decision:
            fp += 1
        else:
            tn += 1
        squared += (p - y)**2
        group = bins[min(9, (10*p).numerator // (10*p).denominator)]
        group[0] += 1
        group[1] += p
        group[2] += y
    fpr = Fraction(fp, fp + tn) if fp + tn else None
    fnr = Fraction(fn, fn + tp) if fn + tp else None
    ba = (2 - fpr - fnr) / 2 if fpr is not None and fnr is not None else None
    ece = sum(abs(p_sum - positives) for _count, p_sum, positives in bins.values()) / n
    return {'support': n, 'tp': tp, 'tn': tn, 'fp': fp, 'fn': fn,
            'balanced_accuracy': ba, 'fpr': fpr, 'fnr': fnr, 'brier': squared / n, 'ece': ece}
