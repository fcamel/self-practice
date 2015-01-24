# Modified from python-cluster: cluster.py by fcamel

from types import TupleType
import sys


class ClusteringError(Exception):
    pass


def median(numbers):
    """
    Return the median of the list of numbers.
    see: http://mail.python.org/pipermail/python-list/2004-December/294990.html
    """

    # Sort the list and take the middle element.
    n = len(numbers)
    copy = sorted(numbers)
    if n & 1:  # There is an odd number of elements
        return copy[n // 2]
    else:
        return (copy[n // 2 - 1] + copy[n // 2]) / 2.0

def minkowski_distance(x, y, p=2):
    """
    Calculates the minkowski distance between two points.

    PARAMETERS
        x - the first point
        y - the second point
        p - the order of the minkowski algorithm.
            This is equal to the euclidian distance.  If the order is 1, it is
            equal to the manhatten distance.
            The higher the order, the closer it converges to the Chebyshev
            distance, which has p=infinity. Default = 2.
    """
    from math import pow
    assert len(y) == len(x)
    assert x >= 1
    sum = 0
    for i in range(len(x)):
        sum += abs(x[i] - y[i]) ** p
    return pow(sum, 1.0 / float(p))


def centroid(list, method=median):
    "returns the central vector of a list of vectors"
    out = []
    for i in range(len(list[0].numbers)):
        out.append(method([x.numbers[i] for x in list]))
    return tuple(out)


class Data(object):
    def __init__(self, id_, numbers):
        self.id_ = id_
        self.numbers = numbers

    def __str__(self):
        return '%s: %s' % (self.id_, ' '.join(map(str, self.numbers)))

    def __cmp__(self, other):
        return cmp(self.id_, other.id_)


class KMeansClustering(object):
    def __init__(self, data, distance=None, equality=None):
        self.__clusters = []
        self.__data = data
        self.distance = distance
        self.__initial_length = len(data)
        self.equality = equality

        # test if each item is of same dimensions
        if len(data) > 1 and isinstance(data[0], TupleType):
            control_length = len(data[0])
            for item in data[1:]:
                if len(item) != control_length:
                    raise ValueError("Each item in the data list must have "
                            "the same amount of dimensions. Item %r was out "
                            "of line!" % (item,))
        # now check if we need and have a distance function
        if (len(data) > 1 and not isinstance(data[0].numbers, TupleType) and
                distance is None):
            raise ValueError("You supplied non-standard items but no "
                    "distance function! We cannot continue!")
        # we now know that we have tuples, and assume therefore that it's
        # items are numeric
        elif distance is None:
            self.distance = minkowski_distance

    def getclusters(self, count):
        """
        Generates <count> clusters

        PARAMETERS
            count - The amount of clusters that should be generated.
                    count must be greater than 1
        """

        # only proceed if we got sensible input
        if count <= 1:
            raise ClusteringError("When clustering, you need to ask for at "
                    "least two clusters! You asked for %d" % count)

        # return the data straight away if there is nothing to cluster
        if (self.__data == [] or len(self.__data) == 1 or
                count == self.__initial_length):
            return self.__data

        # It makes no sense to ask for more clusters than data-items available
        if count > self.__initial_length:
            raise ClusteringError("Unable to generate more clusters than "
                    "items available. You supplied %d items, and asked for "
                    "%d clusters." % (self.__initial_length, count) )

        self.initialise_clusters(self.__data, count)

        items_moved = True  # tells us if any item moved between the clusters,
                            # as we initialised the clusters, we assume that
                            # is the case

        iteration = 0
        while items_moved is True:
            items_moved = False
            iteration += 1
            sys.stderr.write('iteration: %d\n' % iteration)
            for cluster in self.__clusters:
                for item in cluster:
                    res = self.assign_item(item, cluster)
                    if items_moved is False:
                        items_moved = res
        return self.__clusters

    def assign_item(self, item, origin):
        """
        Assigns an item from a given cluster to the closest located cluster

        PARAMETERS
            item   - the item to be moved
            origin - the originating cluster
        """
        closest_cluster = origin
        for cluster in self.__clusters:
            if self.distance(item.numbers, centroid(cluster)) < self.distance(item.numbers,
                    centroid(closest_cluster)):
                closest_cluster = cluster

        if id(closest_cluster) != id(origin):
            self.move_item(item, origin, closest_cluster)
            return True
        else:
            return False

    def move_item(self, item, origin, destination):
        """
        Moves an item from one cluster to anoter cluster

        PARAMETERS

            item        - the item to be moved
            origin      - the originating cluster
            destination - the target cluster
        """
        if self.equality:
            item_index = 0
            for i, element in enumerate(origin):
                if self.equality(element, item):
                    item_index = i
                    break
        else:
            item_index = origin.index(item)

        destination.append(origin.pop(item_index))

    def initialise_clusters(self, input_, clustercount):
        """
        Initialises the clusters by distributing the items from the data
        evenly across n clusters

        PARAMETERS
            input_       - the data set (a list of tuples)
            clustercount - the amount of clusters (n)
        """
        # initialise the clusters with empty lists
        self.__clusters = []
        for _ in xrange(clustercount):
            self.__clusters.append([])

        # distribute the items into the clusters
        count = 0
        for item in input_:
            self.__clusters[count % clustercount].append(item)
            count += 1


if __name__ == '__main__':
    data = [
        Data('b', (2, 1)),
        Data('c', (1, 2)),
        Data('d', (10, 1)),
        Data('y', (-1, -2)),
        Data('f', (9, 9)),
        Data('e', (11, 1)),
        Data('z', (7, 7)),
        Data('a', (1, 1)),
    ]
    cl = KMeansClustering(data)
    clusters = cl.getclusters(2)
    for c in clusters:
        print 'Cluster'
        print '-' * 40
        for d in c:
            print str(d)
        print
