
# TODO Licence:
#
# TODO:  move library intensive functions to vtool
from __future__ import absolute_import, division, print_function, unicode_literals
import operator as op
import decimal
import six
from six.moves import zip, range, reduce, map
from collections import defaultdict
from utool import util_type
from utool import util_list
from utool import util_dict
from utool import util_inject
from utool import util_decor
try:
    import numpy as np
    HAVE_NUMPY = True
except ImportError:
    HAVE_NUMPY = False
    # TODO remove numpy
    pass
try:
    import scipy.spatial.distance as spdist
    HAVE_SCIPY = True
except ImportError:
    HAVE_SCIPY = False
print, rrr, profile = util_inject.inject2(__name__, '[alg]')


PHI = 1.61803398875
PHI_A = (1 / PHI)
PHI_B = 1 - PHI_A


def compare_groupings(groups1, groups2):
    r"""
    Returns a measure of how disimilar two groupings are

    Args:
        groups1 (list): grouping of items
        groups2 (list): grouping of items

    CommandLine:
        python -m utool.util_alg --exec-compare_groupings

    SeeAlso:
        vtool.group_indicies
        vtool.apply_grouping

    Example0:
        >>> # ENABLE_DOCTEST
        >>> from utool.util_alg import *  # NOQA
        >>> groups1 = [[1, 2, 3], [4], [5, 6], [7, 8], [9, 10, 11]]
        >>> groups2 = [[1, 2, 11], [3, 4], [5, 6], [7], [8, 9], [10]]
        >>> total_error = compare_groupings(groups1, groups2)
        >>> result = ('total_error = %r' % (total_error,))
        >>> print(result)
        total_error = 20

    Example1:
        >>> # ENABLE_DOCTEST
        >>> from utool.util_alg import *  # NOQA
        >>> groups1 = [[1, 2, 3], [4], [5, 6]]
        >>> groups2 = [[1, 2, 3], [4], [5, 6]]
        >>> total_error = compare_groupings(groups1, groups2)
        >>> result = ('total_error = %r' % (total_error,))
        >>> print(result)
        total_error = 0

    Example2:
        >>> # ENABLE_DOCTEST
        >>> from utool.util_alg import *  # NOQA
        >>> groups1 = [[1, 2, 3], [4], [5, 6]]
        >>> groups2 = [[1, 2], [4], [5, 6]]
        >>> total_error = compare_groupings(groups1, groups2)
        >>> result = ('total_error = %r' % (total_error,))
        >>> print(result)
        total_error = 4
    """
    import utool as ut
    # For each group, build mapping from each item to the members the group
    item_to_others1 = {item: set(_group) - set([item])
                       for _group in groups1 for item in _group}
    item_to_others2 = {item: set(_group) - set([item])
                       for _group in groups2 for item in _group}

    flat_items1 = ut.flatten(groups1)
    flat_items2 = ut.flatten(groups2)

    flat_items = list(set(flat_items1 + flat_items2))

    errors = []
    item_to_error = {}
    for item in flat_items:
        # Determine the number of unshared members in each group
        others1 = item_to_others1.get(item, set([]))
        others2 = item_to_others2.get(item, set([]))
        missing1 = others1 - others2
        missing2 = others2 - others1
        error = len(missing1) + len(missing2)
        if error > 0:
            item_to_error[item] = error
        errors.append(error)
    total_error = sum(errors)
    return total_error


def find_grouping_consistencies(groups1, groups2):
    """
    Returns a measure of group consistency

    Example:
        >>> # ENABLE_DOCTEST
        >>> from utool.util_alg import *  # NOQA
        >>> groups1 = [[1, 2, 3], [4], [5, 6]]
        >>> groups2 = [[1, 2], [4], [5, 6]]
        >>> common_groups = find_grouping_consistencies(groups1, groups2)
        >>> result = ('common_groups = %r' % (common_groups,))
        >>> print(result)
        common_groups = [(5, 6), (4,)]
    """
    group1_list = set([tuple(sorted(_group)) for _group in groups1])
    group2_list = set([tuple(sorted(_group)) for _group in groups2])
    common_groups = list(group1_list.intersection(group2_list))
    return common_groups


def upper_diag_self_prodx(list_):
    """
    upper diagnoal of cartesian product of self and self.
    Weird name. fixme

    Args:
        list_ (list):

    Returns:
        list:

    CommandLine:
        python -m utool.util_alg --exec-upper_diag_self_prodx

    Example:
        >>> # ENABLE_DOCTEST
        >>> from utool.util_alg import *  # NOQA
        >>> list_ = [1, 2, 3]
        >>> result = upper_diag_self_prodx(list_)
        >>> print(result)
        [(1, 2), (1, 3), (2, 3)]
    """
    return [(item1, item2)
            for n1, item1 in enumerate(list_)
            for n2, item2 in enumerate(list_) if n1 < n2]


def diagonalized_iter(size):
    r"""
    TODO: generalize to more than 2 dimensions to be more like
    itertools.product.

    CommandLine:
        python -m utool.util_alg --exec-diagonalized_iter
        python -m utool.util_alg --exec-diagonalized_iter --size=5

    Example:
        >>> # ENABLE_DOCTEST
        >>> from utool.util_alg import *  # NOQA
        >>> import utool as ut
        >>> size = ut.get_argval('--size', default=4)
        >>> iter_ = diagonalized_iter(size)
        >>> mat = [[None] * size for _ in range(size)]
        >>> for count, (r, c) in enumerate(iter_):
        >>>     mat[r][c] = count
        >>> result = ut.repr2(mat, nl=1, packed=True)
        >>> print(result)
        [[0, 2, 5, 9],
         [1, 4, 8, 12],
         [3, 7, 11, 14],
         [6, 10, 13, 15],]
    """
    for i in range(0, size + 1):
        for r, c in zip(reversed(range(i)), (range(i))):
            yield (r, c)
    for i in range(1, size):
        for r, c in zip(reversed(range(i, size)), (range(i, size))):
            yield (r, c)


def colwise_diag_idxs(size, num=2):
    r"""
    dont trust this implementation or this function name

    Args:
        size (int):

    Returns:
        ?: upper_diag_idxs

    CommandLine:
        python -m utool.util_alg --exec-colwise_diag_idxs --size=5 --num=2
        python -m utool.util_alg --exec-colwise_diag_idxs --size=3 --num=3

    Example:
        >>> # DISABLE_DOCTEST
        >>> from utool.util_alg import *  # NOQA
        >>> size = ut.get_argval('--size', default=5)
        >>> num = ut.get_argval('--num', default=2)
        >>> mat = np.zeros([size] * num, dtype=np.int)
        >>> upper_diag_idxs = colwise_diag_idxs(size, num)
        >>> poses = np.array(upper_diag_idxs)
        >>> idxs = np.ravel_multi_index(poses.T, mat.shape)
        >>> print('poses.T =\n%s' % (ut.repr2(poses.T),))
        >>> mat[tuple(poses.T)] = np.arange(1, len(poses) + 1)
        >>> print(mat)
        poses.T =
        np.array([[0, 0, 1, 0, 1, 2, 0, 1, 2, 3],
                  [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]])
    """
    # diag_idxs = list(diagonalized_iter(size))
    # upper_diag_idxs = [(r, c) for r, c in diag_idxs if r < c]
    # # diag_idxs = list(diagonalized_iter(size))
    import utool as ut
    diag_idxs = ut.iprod(*[range(size) for _ in range(num)])
    #diag_idxs = list(ut.iprod(range(size), range(size)))
    # this is pretty much a simple c ordering
    upper_diag_idxs = [
        tup[::-1] for tup in diag_idxs
        if all([a > b for a, b in ut.itertwo(tup)])
        #if all([a > b for a, b in ut.itertwo(tup[:2])])
    ]
    #upper_diag_idxs = [(c, r) for r, c in diag_idxs if r > c]
    # # upper_diag_idxs = [(r, c) for r, c in diag_idxs if r > c]
    return upper_diag_idxs


def self_prodx(list_):
    return [(item1, item2)
            for n1, item1 in enumerate(list_)
            for n2, item2 in enumerate(list_) if n1 != n2]


def greedy_max_inden_setcover(candidate_sets_dict, items, max_covers=None):
    """
    greedy algorithm for maximum independent set cover

    Covers items with sets from candidate sets. Could be made faster.

    CommandLine:
        python -m utool.util_alg --test-greedy_max_inden_setcover

    Example0:
        >>> # ENABLE_DOCTEST
        >>> from utool.util_alg import *  # NOQA
        >>> import utool as ut
        >>> candidate_sets_dict = {'a': [5, 3], 'b': [2, 3, 5],
        ...                        'c': [4, 8], 'd': [7, 6, 2, 1]}
        >>> items = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        >>> max_covers = None
        >>> tup = greedy_max_inden_setcover(candidate_sets_dict, items, max_covers)
        >>> (uncovered_items, covered_items_list, accepted_keys) = tup
        >>> result = ut.list_str((uncovered_items, sorted(list(accepted_keys))), nl=False)
        >>> print(result)
        ([0, 9], ['a', 'c', 'd'])

    Example1:
        >>> # ENABLE_DOCTEST
        >>> from utool.util_alg import *  # NOQA
        >>> import utool as ut
        >>> candidate_sets_dict = {'a': [5, 3], 'b': [2, 3, 5],
        ...                        'c': [4, 8], 'd': [7, 6, 2, 1]}
        >>> items = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        >>> max_covers = 1
        >>> tup = greedy_max_inden_setcover(candidate_sets_dict, items, max_covers)
        >>> (uncovered_items, covered_items_list, accepted_keys) = tup
        >>> result = ut.list_str((uncovered_items, sorted(list(accepted_keys))), nl=False)
        >>> print(result)
        ([0, 3, 4, 5, 8, 9], ['d'])
    """
    uncovered_set = set(items)
    rejected_keys = set()
    accepted_keys = set()
    covered_items_list = []
    while True:
        # Break if we have enough covers
        if max_covers is not None and len(covered_items_list) >= max_covers:
            break
        maxkey = None
        maxlen = -1
        # Loop over candidates to find the biggested unadded cover set
        for key, candidate_items in six.iteritems(candidate_sets_dict):
            if key in rejected_keys or key in accepted_keys:
                continue
            #print('Checking %r' % (key,))
            lenval = len(candidate_items)
            # len(uncovered_set.intersection(candidate_items)) == lenval:
            if uncovered_set.issuperset(candidate_items):
                if lenval > maxlen:
                    maxkey = key
                    maxlen = lenval
            else:
                rejected_keys.add(key)
        # Add the set to the cover
        if maxkey is None:
            break
        maxval = candidate_sets_dict[maxkey]
        accepted_keys.add(maxkey)
        covered_items_list.append(list(maxval))
        # Add values in this key to the cover
        uncovered_set.difference_update(maxval)
    uncovered_items = list(uncovered_set)
    covertup = uncovered_items, covered_items_list, accepted_keys
    return covertup


def bayes_rule(b_given_a, prob_a, prob_b):
    r"""
    bayes_rule

    P(A | B) = \frac{ P(B | A) P(A) }{ P(B) }

    Args:
        b_given_a (ndarray or float):
        prob_a (ndarray or float):
        prob_b (ndarray or float):

    Returns:
        ndarray or float: a_given_b

    Example:
        >>> # ENABLE_DOCTEST
        >>> from utool.util_alg import *  # NOQA
        >>> b_given_a = .1
        >>> prob_a = .3
        >>> prob_b = .4
        >>> a_given_b = bayes_rule(b_given_a, prob_a, prob_b)
        >>> result = a_given_b
        >>> print(result)
        0.075
    """
    a_given_b = (b_given_a * prob_a) / prob_b
    return a_given_b


def negative_minclamp_inplace(arr):
    arr[arr > 0] -= arr[arr > 0].min()
    arr[arr <= 0] = arr[arr > 0].min()
    return arr


def xywh_to_tlbr(bbox, img_wh):
    """ converts xywh format to (tlx, tly, blx, bly) """
    (img_w, img_h) = img_wh
    if img_w == 0 or img_h == 0:
        img_w = 1
        img_h = 1
        msg = '[cc2.1] Your csv tables have an invalid ANNOTATION.'
        print(msg)
        #warnings.warn(msg)
        #ht = 1
        #wt = 1
    # Ensure ANNOTATION is within bounds
    (x, y, w, h) = bbox
    x1 = max(x, 0)
    y1 = max(y, 0)
    x2 = min(x + w, img_w - 1)
    y2 = min(y + h, img_h - 1)
    return (x1, y1, x2, y2)


def item_hist(list_):
    """ counts the number of times each item appears in the dictionary """
    dict_hist = {}
    # Insert each item into the correct group
    for item in list_:
        if item not in dict_hist:
            dict_hist[item] = 0
        dict_hist[item] += 1
    return dict_hist


def flatten_membership_mapping(uid_list, members_list):
    num_members = sum(list(map(len, members_list)))
    flat_uids = [None for _ in range(num_members)]
    flat_members = [None for _ in range(num_members)]
    count = 0
    for uid, members in zip(uid_list, members_list):
        for member in members:
            flat_uids[count]    = uid
            flat_members[count] = member
            count += 1
    return flat_uids, flat_members


def get_phi():
    """ Golden Ratio: phi = 1 / sqrt(5) / 2.0 = 1.61803398875 """
    #phi = (1.0 + sqrt(5)) / 2.0 = 1.61803398875
    # return phi
    return PHI


def get_phi_ratio1():
    return 1.0 / get_phi()


def is_prime(num):
    """
    naive function for finding primes. Good for stress testing

    References:
        http://thelivingpearl.com/2013/01/06/how-to-find-prime-numbers-in-python/

    CommandLine:
        python -m utool.util_alg --test-is_prime

    Example:
        >>> # ENABLE_DOCTEST
        >>> from utool.util_alg import *  # NOQA
        >>> import utool as ut
        >>> with ut.Timer('isprime'):
        >>>     series = [is_prime(n) for n in range(30)]
        >>> result = ('primes = %s' % (str(ut.list_where(series[0:10])),))
        >>> print(result)
        primes = [2, 3, 5, 7]
    """
    if num < 2:
        return False
    for j in range(2, num):
        if (num % j) == 0:
            return False
    return True


def fibonacci_recursive(n):
    """
    CommandLine:
        python -m utool.util_alg --test-fibonacci_recursive

    Example:
        >>> # ENABLE_DOCTEST
        >>> from utool.util_alg import *  # NOQA
        >>> import utool as ut
        >>> with ut.Timer('fib rec'):
        >>>     series = [fibonacci_recursive(n) for n in range(20)]
        >>> result = ('series = %s' % (str(series[0:10]),))
        >>> print(result)
        series = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
    """
    if n < 2:
        return n
    return fibonacci_recursive(n - 2) + fibonacci_recursive(n - 1)


def fibonacci_iterative(n):
    """
    Args:
        n (int):

    Returns:
        int: a

    References:
        http://stackoverflow.com/questions/15047116/a-iterative-algorithm-for-fibonacci-numbers

    CommandLine:
        python -m utool.util_alg --test-fibonacci_iterative

    Example:
        >>> # ENABLE_DOCTEST
        >>> from utool.util_alg import *  # NOQA
        >>> import utool as ut
        >>> with ut.Timer('fib iter'):
        >>>     series = [fibonacci_iterative(n) for n in range(20)]
        >>> result = ('series = %s' % (str(series[0:10]),))
        >>> print(result)
        series = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
    """
    a, b = 0, 1
    for _ in range(0, n):
        a, b = b, a + b
    return a

fibonacci = fibonacci_iterative


def enumerate_primes(max_prime=4100):
    primes = [num for num in range(2, max_prime) if is_prime(num)]
    return primes


def get_nth_prime(n, max_prime=4100, safe=True):
    """ hacky but still brute force algorithm for finding nth prime for small tests """
    if n <= 100:
        first_100_primes = (
            2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61,
            67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137,
            139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199,
            211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277,
            281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359,
            367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439,
            443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521,
            523, 541, )
        #print(len(first_100_primes))
        nth_prime = first_100_primes[n - 1]
    else:
        if safe:
            primes = [num for num in range(2, max_prime) if is_prime(num)]
            nth_prime = primes[n]
        else:
            # This can run for a while... get it? while?
            nth_prime = get_nth_prime_bruteforce(n)
    return nth_prime


def get_nth_prime_bruteforce(n, start_guess=2, start_num_primes=0):
    guess = start_guess
    num_primes_found = start_num_primes
    while True:
        if is_prime(guess):
            num_primes_found += 1
        if num_primes_found == n:
            nth_prime = guess
            break
        guess += 1
    return nth_prime


def get_prime_index(prime):
    guess = 2
    num_primes_found = 0
    while True:
        if is_prime(guess):
            num_primes_found += 1
            if guess == prime:
                return num_primes_found
        else:
            assert guess != prime, 'input=%r is not prime. has %r primes less than it' % (prime, num_primes_found)
        guess += 1


def generate_primes(start_guess=2):
    guess = start_guess
    while True:
        if is_prime(guess):
            yield guess
        guess += 1


def knapsack(items, maxweight, recursive=True):
    r"""
    Solve the knapsack problem by finding the most valuable
    subsequence of `items` subject that weighs no more than
    `maxweight`.

    Args:
        `items` (tuple): is a sequence of tuples `(value, weight, id_)`, where `value`
            is a number and `weight` is a non-negative integer, and `id_` is an
            item identifier.

        `maxweight` (scalar):  is a non-negative integer.

    Returns:
        tuple: (total_value, items_subset) - a pair whose first element is the
            sum of values in the most valuable subsequence, and whose second
            element is the subsequence. Subset may be different depending on
            implementation (ie top-odwn recusrive vs bottom-up iterative)

    References:
        http://codereview.stackexchange.com/questions/20569/dynamic-programming-solution-to-knapsack-problem
        http://stackoverflow.com/questions/141779/solving-the-np-complete-problem-in-xkcd
        http://www.es.ele.tue.nl/education/5MC10/Solutions/knapsack.pdf

    CommandLine:
        python -m utool.util_alg --test-knapsack

        python -m utool.util_alg --test-knapsack:0
        python -m utool.util_alg --exec-knapsack:1

    Example:
        >>> # ENABLE_DOCTEST
        >>> from utool.util_alg import *  # NOQA
        >>> items = [(4, 12, 0), (2, 1, 1), (6, 4, 2), (1, 1, 3), (2, 2, 4)]
        >>> maxweight = 15
        >>> total_value, items_subset = knapsack(items, maxweight, recursive=True)
        >>> total_value1, items_subset1 = knapsack(items, maxweight, recursive=False)
        >>> result =  'total_value = %.2f\n' % (total_value,)
        >>> result += 'items_subset = %r' % (items_subset,)
        >>> print(result)
        >>> ut.assert_eq(total_value1, total_value)
        >>> ut.assert_eq(items_subset1, items_subset)
        total_value = 11.00
        items_subset = [(2, 1, 1), (6, 4, 2), (1, 1, 3), (2, 2, 4)]

    Example:
        >>> # ENABLE_DOCTEST
        >>> from utool.util_alg import *  # NOQA
        >>> # Solve https://xkcd.com/287/
        >>> weights = [2.15, 2.75, 3.35, 3.55, 4.2, 5.8] * 2
        >>> items = [(w, w, i) for i, w in enumerate(weights)]
        >>> maxweight = 15.05
        >>> total_value, items_subset = knapsack(items, maxweight, recursive=True)
        >>> total_value1, items_subset1 = knapsack(items, maxweight, recursive=False)
        >>> total_weight = sum([t[1] for t in items_subset])
        >>> print('total_weight = %r' % (total_weight,))
        >>> result =  'total_value = %.2f' % (total_value,)
        >>> print(result)
        >>> print('items_subset = %r' % (items_subset,))
        >>> print('items_subset1 = %r' % (items_subset1,))
        >>> #assert items_subset1 == items_subset, 'NOT EQ\n%r !=\n%r' % (items_subset1, items_subset)
        total_value = 15.05

    Timeit:
        >>> import utool as ut
        >>> setup = ut.codeblock(
        >>>     '''
                import utool as ut
                weights = [215, 275, 335, 355, 42, 58] * 10
                items = [(w, w, i) for i, w in enumerate(weights)]
                maxweight = 2505
                import numba
                knapsack_numba = numba.autojit(ut.knapsack_iterative)
                knapsack_numba = numba.autojit(ut.knapsack_iterative_numpy)
                ''')
        >>> # Test load time
        >>> stmt_list1 = ut.codeblock(
        >>>     '''
                ut.knapsack_recursive(items, maxweight)
                ut.knapsack_iterative(items, maxweight)
                knapsack_numba(items, maxweight)
                ut.knapsack_iterative_numpy(items, maxweight)
                ''').split('\n')
        >>> ut.util_dev.timeit_compare(stmt_list1, setup, int(5))
    """
    if recursive:
        return knapsack_recursive(items, maxweight)
    else:
        return knapsack_iterative(items, maxweight)
        #return knapsack_iterative_numpy(items, maxweight)


def knapsack_recursive(items, maxweight):
    @util_decor.memoize_nonzero
    def bestvalue(i, j):
        """ Return the value of the most valuable subsequence of the first i
        elements in items whose weights sum to no more than j. """
        if i == 0:
            return 0
        value, weight = items[i - 1][0:2]
        if weight > j:
            return bestvalue(i - 1, j)
        else:
            return max(bestvalue(i - 1, j),
                       bestvalue(i - 1, j - weight) + value)

    j = maxweight
    items_subset = []
    for i in range(len(items), 0, -1):
        if bestvalue(i, j) != bestvalue(i - 1, j):
            items_subset.append(items[i - 1])
            j -= items[i - 1][1]
    items_subset.reverse()
    total_value = bestvalue(len(items), maxweight)
    return total_value, items_subset


def number_of_decimals(num):
    r"""
    Args:
        num (float):

    References:
        stackoverflow.com/questions/6189956/finding-decimal-places

    Example:
        >>> # ENABLE_DOCTEST
        >>> from utool.util_alg import *  # NOQA
        >>> num = 15.05
        >>> result = number_of_decimals(num)
        >>> print(result)
        2
    """
    exp = decimal.Decimal(str(num)).as_tuple().exponent
    return max(0, -exp)


def knapsack_iterative(items, maxweight):
    # Knapsack requires integral weights
    weights = [t[1] for t in items]
    max_exp = max([number_of_decimals(w_) for w_ in weights])
    coeff = 10 ** max_exp
    # Adjust weights to be integral
    int_maxweight = int(maxweight * coeff)
    int_items = [(v, int(w * coeff), idx) for v, w, idx in items]
    return knapsack_iterative_int(int_items, int_maxweight)


def knapsack_iterative_int(items, maxweight):
    """
    Iterative knapsack method

    Math:
        maximize \sum_{i \in T} v_i
        subject to \sum_{i \in T} w_i \leq W

    Notes:
        dpmat is the dynamic programming memoization matrix.
        dpmat[i, w] is the total value of the items with weight at most W
        T is idx_subset, the set of indicies in the optimal solution

    CommandLine:
        python -m utool.util_alg --exec-knapsack_iterative_int --show

    Example:
        >>> # ENABLE_DOCTEST
        >>> from utool.util_alg import *  # NOQA
        >>> weights = [1, 3, 3, 5, 2, 1] * 2
        >>> items = [(w, w, i) for i, w in enumerate(weights)]
        >>> maxweight = 10
        >>> total_value, items_subset = knapsack_iterative_int(items, maxweight)
        >>> total_weight = sum([t[1] for t in items_subset])
        >>> print('total_weight = %r' % (total_weight,))
        >>> print('items_subset = %r' % (items_subset,))
        >>> result =  'total_value = %.2f' % (total_value,)
        >>> print(result)
        total_value = 10.00

    Ignore:
        DPMAT = [[dpmat[r][c] for c in range(maxweight)] for r in range(len(items))]
        KMAT  = [[kmat[r][c] for c in range(maxweight)] for r in range(len(items))]
    """
    values  = [t[0] for t in items]
    weights = [t[1] for t in items]
    maxsize = maxweight + 1
    # Sparse representation seems better
    dpmat = defaultdict(lambda: defaultdict(lambda: np.inf))
    kmat = defaultdict(lambda: defaultdict(lambda: False))
    idx_subset = []  # NOQA
    for w in range(maxsize):
        dpmat[0][w] = 0
    # For each item consider to include it or not
    for idx in range(1, len(items)):
        item_val = values[idx]
        item_weight = weights[idx]
        # consider at each possible bag size
        for w in range(maxsize):
            valid_item = item_weight <= w
            prev_val = dpmat[idx - 1][w]
            prev_noitem_val = dpmat[idx - 1][w - item_weight]
            withitem_val = item_val + prev_noitem_val
            more_valuable = withitem_val > prev_val
            if valid_item and more_valuable:
                dpmat[idx][w] = withitem_val
                kmat[idx][w] = True
            else:
                dpmat[idx][w] = prev_val
                kmat[idx][w] = False
    # Trace backwards to get the items used in the solution
    K = maxweight
    for idx in reversed(range(1, len(items))):
        if kmat[idx][K]:
            idx_subset.append(idx)
            K = K - weights[idx]
    idx_subset = sorted(idx_subset)
    items_subset = [items[i] for i in idx_subset]
    total_value = dpmat[len(items) - 1][maxweight]
    return total_value, items_subset


def knapsack_iterative_numpy(items, maxweight):
    """
    Iterative knapsack method

    maximize \sum_{i \in T} v_i
    subject to \sum_{i \in T} w_i \leq W

    Notes:
        dpmat is the dynamic programming memoization matrix.
        dpmat[i, w] is the total value of the items with weight at most W
        T is the set of indicies in the optimal solution
    """
    #import numpy as np
    items = np.array(items)
    weights = items.T[1]
    # Find maximum decimal place (this problem is in NP)
    max_exp = max([number_of_decimals(w_) for w_ in weights])
    coeff = 10 ** max_exp
    # Adjust weights to be integral
    weights = (weights * coeff).astype(np.int)
    values  = items.T[0]
    MAXWEIGHT = int(maxweight * coeff)
    W_SIZE = MAXWEIGHT + 1

    dpmat = np.full((len(items), W_SIZE), np.inf)
    kmat = np.full((len(items), W_SIZE), 0, dtype=np.bool)
    idx_subset = []

    for w in range(W_SIZE):
        dpmat[0][w] = 0
    for idx in range(1, len(items)):
        item_val = values[idx]
        item_weight = weights[idx]
        for w in range(W_SIZE):
            valid_item = item_weight <= w
            prev_val = dpmat[idx - 1][w]
            if valid_item:
                prev_noitem_val = dpmat[idx - 1][w - item_weight]
                withitem_val = item_val + prev_noitem_val
                more_valuable = withitem_val > prev_val
            else:
                more_valuable = False
            dpmat[idx][w] = withitem_val if more_valuable else prev_val
            kmat[idx][w] = more_valuable
    K = MAXWEIGHT
    for idx in reversed(range(1, len(items))):
        if kmat[idx, K]:
            idx_subset.append(idx)
            K = K - weights[idx]
    idx_subset = sorted(idx_subset)
    items_subset = [items[i] for i in idx_subset]
    total_value = dpmat[len(items) - 1][MAXWEIGHT]
    return total_value, items_subset


#def knapsack_all_solns(items, maxweight):
#    """
#    TODO: return all optimal solutions to the knapsack problem

#    References:
#        stackoverflow.com/questions/30554290/all-solutions-from-knapsack-dp-matrix

#    >>> items = [(1, 2, 0), (1, 3, 1), (1, 4, 2), (1, 3, 3), (1, 3, 4), (1, 5, 5), (1, 4, 6), (1, 1, 7), (1, 1, 8), (1, 3, 9)]
#    >>> weights = ut.get_list_column(items, 1)
#    >>> maxweight = 6
#    """


def knapsack_greedy(items, maxweight):
    r"""
    non-optimal greedy version of knapsack algorithm
    does not sort input. Sort the input by largest value
    first if desired.

    Args:
        `items` (tuple): is a sequence of tuples `(value, weight, id_)`, where `value`
            is a scalar and `weight` is a non-negative integer, and `id_` is an
            item identifier.

        `maxweight` (scalar):  is a non-negative integer.

    CommandLine:
        python -m utool.util_alg --exec-knapsack_greedy

    Example:
        >>> # ENABLE_DOCTEST
        >>> from utool.util_alg import *  # NOQA
        >>> items = [(4, 12, 0), (2, 1, 1), (6, 4, 2), (1, 1, 3), (2, 2, 4)]
        >>> maxweight = 15
        >>> total_value, items_subset = knapsack_greedy(items, maxweight)
        >>> result =  'total_value = %r\n' % (total_value,)
        >>> result += 'items_subset = %r' % (items_subset,)
        >>> print(result)
        total_value = 7
        items_subset = [(4, 12, 0), (2, 1, 1), (1, 1, 3)]
    """
    items_subset = []
    total_weight = 0
    total_value = 0
    for item in items:
        value, weight = item[0:2]
        if total_weight + weight > maxweight:
            continue
        else:
            items_subset.append(item)
            total_weight += weight
            total_value += value
    return total_value, items_subset


def cumsum(num_list):
    """ python cumsum

    References:
        stackoverflow.com/questions/9258602/elegant-pythonic-cumsum
    """
    return reduce(lambda acc, itm: op.iadd(acc, [acc[-1] + itm]), num_list, [0])[1:]


def safe_div(a, b):
    return None if a is None or b is None else a / b


def choose(n, k):
    """
    N choose k

    binomial combination (without replacement)
    """
    import scipy.misc
    return scipy.misc.comb(n, k, exact=True, repetition=False)


def triangular_number(n):
    r"""
    Latex:
        T_n = \sum_{k=1}^{n} k = \frac{n (n + 1)}{2} = \binom{n + 1}{2}

    References:
        en.wikipedia.org/wiki/Triangular_number
    """
    return ((n * (n + 1)) / 2)


# Functions using NUMPY / SCIPY (need to make python only or move to vtool)


def maximin_distance_subset1d(items, K=None, min_thresh=None, verbose=False):
    """
    Greedy algorithm, may be exact for 1d case.

    CommandLine:
        python -m utool.util_alg --exec-maximin_distance_subset1d

    Example:
        >>> # DISABLE_DOCTEST
        >>> import utool as ut
        >>> from utool.util_alg import *  # NOQA
        >>> #items = [1, 2, 3, 4, 5, 6, 7]
        >>> items = [20, 1, 1, 9, 21, 6, 22]
        >>> min_thresh = 5
        >>> K = None
        >>> result = maximin_distance_subset1d(items, K, min_thresh, verbose=True)
        >>> print(result)

    Example:
        >>> # DISABLE_DOCTEST
        >>> import utool as ut
        >>> from utool.util_alg import *  # NOQA
        >>> #items = [1, 2, 3, 4, 5, 6, 7]
        >>> items = [0, 1]
        >>> min_thresh = 5
        >>> K = None
        >>> result = maximin_distance_subset1d(items, K, min_thresh, verbose=True)
        >>> print(result)
    """
    import utool as ut
    import vtool as vt
    points = np.array(items)[:, None]
    # Initial sorting of 1d points
    initial_sortx = points.argsort(axis=0).flatten()
    points = points.take(initial_sortx, axis=0)

    if K is None:
        K = len(items)

    def distfunc(x, y):
        return np.abs(x - y)

    assert points.shape[1] == 1
    assert len(points) >= K, 'cannot return subset'
    if K == 1:
        current_idx = [0]
    else:
        current_idx = [0, -1]
        if min_thresh is not None and distfunc(points[0], points[-1])[0] < min_thresh:
            current_idx = [0]
    chosen_mask = vt.index_to_boolmask(current_idx, len(points))

    for k in range(2, K):
        unchosen_idx = np.nonzero(~chosen_mask)[0]
        unchosen_items = points.compress(~chosen_mask, axis=0)
        chosen_items = points.compress(chosen_mask, axis=0)
        distances = distfunc(unchosen_items, chosen_items.T)
        min_distances = distances.min(axis=1)
        argx = min_distances.argmax()
        if min_thresh is not None:
            if min_distances[argx] < min_thresh:
                break
        new_idx = unchosen_idx[argx]
        chosen_mask[new_idx] = True

    # Put chosen mask back in the input order of items
    chosen_items_mask = chosen_mask.take(initial_sortx.argsort())
    chosen_items_idxs = np.nonzero(chosen_items_mask)[0]
    chosen_items = ut.list_take(items, chosen_items_idxs)
    #current_idx = np.nonzero(chosen_mask)[0]
    if verbose:
        print('Chose subset')
        chosen_points = points.compress(chosen_mask, axis=0)
        distances = (spdist.pdist(chosen_points, distfunc))
        print('chosen_items_idxs = %r' % (chosen_items_idxs,))
        print('chosen_items = %r' % (chosen_items,))
        print('distances = %r' % (distances,))
    return chosen_items_idxs, chosen_items


def maximum_distance_subset(items, K, verbose=False):
    """
    FIXME: I believe this does not work.

    Returns a subset of size K from items with the maximum pairwise distance

    References:
        stackoverflow.com/questions/12278528/subset-elements-furthest-apart-eachother
        stackoverflow.com/questions/13079563/condensed-distance-matrix-pdist

    Recurance:
        Let X[n,k] be the solution for selecting k elements from first n elements items.
        X[n, k] = max( max( X[m, k - 1] + (sum_{p in prev_solution} dist(o, p)) for o < n and o not in prev solution) ) for m < n.

    Example:
        >>> import scipy.spatial.distance as spdist
        >>> items = [1, 6, 20, 21, 22]

    CommandLine:
        python -m utool.util_alg --exec-maximum_distance_subset

    Example:
        >>> # DISABLE_DOCTEST
        >>> from utool.util_alg import *  # NOQA
        >>> #items = [1, 2, 3, 4, 5, 6, 7]
        >>> items = [1, 6, 20, 21, 22]
        >>> K = 3
        >>> result = maximum_distance_subset(items, K)
        >>> print(result)
        (42.0, array([4, 3, 0]), array([22, 21,  1]))
    """
    from utool import util_decor
    if verbose:
        print('maximum_distance_subset len(items)=%r, K=%r' % (len(items), K,))

    points = np.array(items)[:, None]

    if False:
        # alternative definition (not sure if works)
        distmat = spdist.squareform(spdist.pdist(points, lambda x, y: np.abs(x - y)))
        D = np.triu(distmat)
        remaining_idxs = np.arange(len(D))
        for count in range(len(points) - K):
            values = D.sum(axis=1) + D.sum(axis=0)
            remove_idx = values.argmin()  # index with minimum pairwise distance
            remaining_idxs = np.delete(remaining_idxs, remove_idx)
            D = np.delete(np.delete(D, remove_idx, axis=0), remove_idx, axis=1)
        value = D.sum()
        subset_idx = remaining_idxs.tolist()
        value, subset_idx
        subset = points.take(subset_idx)
        #print((value, subset_idx, subset))

    sortx = points.T[0].argsort()[::-1]
    sorted_points = points.take(sortx, axis=0)
    pairwise_distance = spdist.pdist(sorted_points, lambda x, y: np.abs(x - y))
    distmat = (spdist.squareform(pairwise_distance))

    def condensed_idx(i, j):
        if i >= len(sorted_points) or j >= len(sorted_points):
            raise IndexError('i=%r j=%r out of range' % (i, j))
        elif i == j:
            return None
        elif j < i:
            i, j = j, i
        return (i * len(sorted_points) + j) - (i * (i + 1) // 2) - (i) - (1)

    def dist(i, j):
        idx = condensed_idx(i, j)
        return 0 if idx is None else pairwise_distance[idx]

    @util_decor.memoize_nonzero
    def optimal_solution(n, k):
        """
        Givem sorted items sorted_points
        Pick subset_idx of size k from sorted_points[:n] with maximum pairwise distance
        Dynamic programming solution
        """
        "# FIXME BROKEN "
        assert n <= len(sorted_points) and k <= len(sorted_points)
        if k < 2 or n < 2 or n < k:
            # BASE CASE
            value, subset_idx =  0, []
        elif k == 2:
            # BASE CASE
            # when k==2 we choose the maximum pairwise pair
            subdist = np.triu(distmat[0:n, 0:n])
            maxpos = subdist.argmax()
            ix, jx = np.unravel_index(maxpos, subdist.shape)
            value = distmat[ix, jx]
            subset_idx = [ix, jx]
        else:
            # RECURSIVE CASE
            value = 0
            subset_idx = None
            # MAX OVER ALL OTHER NODES (might not need a full on loop here, but this will definitely work)
            for m in range(k - 1, n):
                # Choose which point to add would maximize the distance with the previous best answer.
                prev_value, prev_subset_idx = optimal_solution(m, k - 1)
                for o in range(n):
                    if o in prev_subset_idx:
                        continue
                    add_value = sum([distmat[o, px] for px in prev_subset_idx])
                    cur_value = prev_value + add_value
                    if cur_value > value:
                        value = cur_value
                        subset_idx = prev_subset_idx + [o]
        return value, subset_idx

    value, sorted_subset_idx = optimal_solution(len(points), K)
    subset_idx = sortx.take(sorted_subset_idx)
    subset = points.take(subset_idx)
    #print((value, subset_idx, subset))
    return value, subset_idx, subset
    #np.array([[dist(i, k) if k < i else 0 for k in range(len(A))] for i in range(len(A))])
    #raise NotImplementedError('unfinished')


def safe_max(arr):
    return np.nan if arr is None or len(arr) == 0 else arr.max()


def safe_min(arr):
    return np.nan if arr is None or len(arr) == 0 else arr.min()


def deg_to_rad(degree):
    degree %= 360.0
    tau = 2 * np.pi
    return (degree / 360.0) * tau


def rad_to_deg(radians):
    tau = 2 * np.pi
    radians %= tau
    return (radians / tau) * 360.0


def inbounds(num, low, high, eq=False):
    r"""
    Args:
        num (scalar or ndarray):
        low (scalar or ndarray):
        high (scalar or ndarray):
        eq (bool):

    Returns:
        scalar or ndarray: is_inbounds

    CommandLine:
        python -m utool.util_alg --test-inbounds

    Example:
        >>> # ENABLE_DOCTEST
        >>> from utool.util_alg import *  # NOQA
        >>> import utool as ut
        >>> num = np.array([[ 0.   ,  0.431,  0.279],
        ...                 [ 0.204,  0.352,  0.08 ],
        ...                 [ 0.107,  0.325,  0.179]])
        >>> low  = .1
        >>> high = .4
        >>> eq = False
        >>> is_inbounds = inbounds(num, low, high, eq)
        >>> result = ut.numpy_str(is_inbounds)
        >>> print(result)
        np.array([[False, False,  True],
                  [ True,  True, False],
                  [ True,  True,  True]], dtype=bool)

    """
    less    = op.le if eq else op.lt
    greater = op.ge if eq else op.gt
    and_ = np.logical_and if isinstance(num, np.ndarray) else op.and_
    is_inbounds = and_(greater(num, low), less(num, high))
    return is_inbounds


def almost_eq(arr1, arr2, thresh=1E-11, ret_error=False):
    """ checks if floating point number are equal to a threshold
    """
    error = np.abs(arr1 - arr2)
    passed = error < thresh
    if ret_error:
        return passed, error
    return passed


def almost_allsame(vals):
    if len(vals) == 0:
        return True
    x = vals[0]
    return np.all([np.isclose(item, x) for item in vals])


def unixtime_hourdiff(x, y):
    return np.abs((x - y)) / (60. ** 2)


def absdiff(x, y):
    return np.abs(np.subtract(x, y))


def safe_pdist(arr, *args, **kwargs):
    """
    Kwargs:
        metric = ut.absdiff
    SeeAlso:
        scipy.spatial.distance.pdist
    """
    if arr is None or len(arr) < 2:
        return None
    else:
        return spdist.pdist(arr, *args, **kwargs)


def normalize(array, dim=0):
    return norm_zero_one(array, dim)


def norm_zero_one(array, dim=None):
    """
    normalizes a numpy array from 0 to 1 based in its extent

    Args:
        array (ndarray):
        dim   (int):

    Returns:
        ndarray:

    CommandLine:
        python -m utool.util_alg --test-norm_zero_one

    Example:
        >>> # ENABLE_DOCTEST
        >>> from utool.util_alg import *  # NOQA
        >>> array = np.array([ 22, 1, 3, 2, 10, 42, ])
        >>> dim = None
        >>> array_norm = norm_zero_one(array, dim)
        >>> result = np.array_str(array_norm, precision=3)
        >>> print(result)
        [ 0.512  0.     0.049  0.024  0.22   1.   ]
    """
    if not util_type.is_float(array):
        array = array.astype(np.float32)
    array_max  = array.max(dim)
    array_min  = array.min(dim)
    array_exnt = np.subtract(array_max, array_min)
    array_norm = np.divide(np.subtract(array, array_min), array_exnt)
    return array_norm


def euclidean_dist(vecs1, vec2, dtype=None):
    if dtype is None:
        dtype = np.float32
    return np.sqrt(((vecs1.astype(dtype) - vec2.astype(dtype)) ** 2).sum(1))


def max_size_max_distance_subset(items, min_thresh=0, Kstart=2, verbose=False):
    r"""
    Args:
        items (?):
        min_thresh (int): (default = 0)
        Kstart (int): (default = 2)

    Returns:
        ?: prev_subset_idx

    CommandLine:
        python -m utool.util_alg --exec-max_size_max_distance_subset

    Example:
        >>> # DISABLE_DOCTEST
        >>> from utool.util_alg import *  # NOQA
        >>> items = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        >>> min_thresh = 3
        >>> Kstart = 2
        >>> verbose = True
        >>> prev_subset_idx = max_size_max_distance_subset(items, min_thresh,
        >>>                                                Kstart, verbose=verbose)
        >>> result = ('prev_subset_idx = %s' % (str(prev_subset_idx),))
        >>> print(result)
    """
    import utool as ut
    assert Kstart >= 2, 'must start with group of size 2'
    best_idxs = []
    for K in range(Kstart, len(items)):
        if verbose:
            print('Running subset chooser')
        value, subset_idx, subset = ut.maximum_distance_subset(items, K=K, verbose=verbose)
        if verbose:
            print('subset = %r' % (subset,))
            print('subset_idx = %r' % (subset_idx,))
            print('value = %r' % (value,))
        distances = ut.safe_pdist(subset[:, None])
        if np.any(distances < min_thresh):
            break
        best_idxs = subset_idx
    return best_idxs


def group_indices(items):
    """
    groups indicies of each item in ``items``

    Args:
        items (list): group ids

    SeeAlso:
        vt.group_indices - optimized numpy version
        ut.apply_grouping

    CommandLine:
        python -m utool.util_alg --exec-group_indices

    Example:
        >>> # ENABLE_DOCTEST
        >>> from utool.util_alg import *  # NOQA
        >>> import utool as ut
        >>> idx2_groupid = ['b', 1, 'b', 1, 'b', 1, 'b', 'c', 'c', 'c', 'c']
        >>> (keys, groupxs) = ut.group_indices(idx2_groupid)
        >>> result = ut.repr3((keys, groupxs), nobraces=1, nl=1)
        >>> print(result)
        [1, 'c', 'b'],
        [[1, 3, 5], [7, 8, 9, 10], [0, 2, 4, 6]],
    """
    grouped_dict = util_dict.group_items(range(len(items)), items)
    keys = list(grouped_dict.keys())
    groupxs = util_dict.dict_take(grouped_dict, keys)
    return keys, groupxs


def apply_grouping(items, groupxs):
    r"""
    applies grouping from group_indicies
    non-optimized version

    Args:
        items (list): items to group
        groupxs (list of list of ints): grouped lists of indicies

    SeeAlso:
        vt.apply_grouping - optimized numpy version
        ut.group_indices

    CommandLine:
        python -m utool.util_alg --exec-apply_grouping --show

    Example:
        >>> # ENABLE_DOCTEST
        >>> from utool.util_alg import *  # NOQA
        >>> import utool as ut
        >>> idx2_groupid = [2, 1, 2, 1, 2, 1, 2, 3, 3, 3, 3]
        >>> items        = [1, 8, 5, 5, 8, 6, 7, 5, 3, 0, 9]
        >>> (keys, groupxs) = ut.group_indices(idx2_groupid)
        >>> grouped_items = ut.apply_grouping(items, groupxs)
        >>> result = ut.repr2(grouped_items)
        >>> print(result)
        [[8, 5, 6], [1, 5, 8, 7], [5, 3, 0, 9]]
    """
    return [util_list.list_take(items, xs) for xs in groupxs]


if __name__ == '__main__':
    """
    CommandLine:
        python -c "import utool, utool.util_alg; utool.doctest_funcs(utool.util_alg, allexamples=True)"
        python -c "import utool, utool.util_alg; utool.doctest_funcs(utool.util_alg)"
        python -m utool.util_alg
        python -m utool.util_alg --allexamples
    """
    import multiprocessing
    multiprocessing.freeze_support()  # for win32
    import utool as ut  # NOQA
    ut.doctest_funcs()
