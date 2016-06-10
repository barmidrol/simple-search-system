from copy import copy
from blist import sortedlist
from search_engine.db.cassandra_manager import CassandraManager

class QueryHandler:
    def __init__(self):
        self.__cassandra_conn = CassandraManager()

    def __custom_init(self, query):
        self.__query = query
        self.__query_length = len(query)
        self.__count_of_documents = self.__cassandra_conn.get_count_of_documents()
        self.__data = {}
        self.__sorted_keys = sortedlist([])
        self.__result = []

    def feed(self, query):
        self.__custom_init(query)
        self.__get_documents_contain_term()
        self.__documents_lists_intersection()
        self.__ranking()
        self.__sort_result()

    def get_doc(self):
        self.__get_documents_contain_term()

    def __get_documents_contain_term(self):
        for term in self.__query:
            result = self.__cassandra_conn.get_documents_contain_term(term)

            if result:
                count = len(result)
                idf = self.__count_of_documents / count
                self.__sorted_keys.add((count, term))
                documents = sortedlist([])

                for item in result:
                    documents.add([item.url, item.frequence * idf])

                self.__data[term] = documents
                return documents

    def __documents_lists_intersection(self):
        temp = sortedlist([])

        while True:
            try:
                term = self.__sorted_keys.pop(0)[1]
            except IndexError:
                break

            if not temp:
                temp.update(self.__data[term])
            else:
                temp_counter = 0
                data_counter = 0

                while True:
                    try:
                        tepm_item = temp[temp_counter]
                        data_item = self.__data[term][data_counter]

                    except IndexError:
                        break

                    if tepm_item[0] == data_item[0]:
                        tepm_item[1] += data_item[1]

                        temp_counter += 1
                        data_counter += 1
                    elif tepm_item[0] > data_item[0]:
                        data_counter += 1
                    elif tepm_item[0] < data_item[0]:
                        temp.pop(temp_counter)

                temp_last_index = len(temp) - 1

                if temp_counter < temp_last_index:
                    index = temp_counter + 1

                    while index <= temp_last_index:
                        temp.pop(index)
                        temp_last_index -= 1

        for item in temp:
            self.__result.append([item[1], item[0]])

    def __ranking(self):
        for item in self.__result:
            positions = []
            indexes = [0] * self.__query_length
            min_dist = 9999999

            for term in self.__query:
                temp_positions = self.__cassandra_conn.get_positions_of_term_in_doc(term, item[1])

                if temp_positions is None:
                    continue

                positions.append(temp_positions)

                first_entry = temp_positions[0]

                # if term in top of the document, increase weight on 10 percent
                if first_entry and first_entry <= 200:
                    item[0] *= 1.1

            if len(positions) <= 1:
                continue

            last_indexes = [len(item) - 1 for item in positions]

            while True:
                passage = []

                for index, term_positions in zip(indexes, positions):
                    passage.append(term_positions[index])

                dist = sum([abs(passage[i] - passage[i - 1]) for i in range(1, len(passage))])

                if dist < min_dist and dist > 0:
                    min_dist = dist

                temp_passage = copy(passage)

                while True:
                    if not temp_passage:
                        i = None
                        break

                    _min = min(temp_passage)
                    temp_passage.remove(_min)
                    i = passage.index(_min)

                    if indexes[i] < last_indexes[i]:
                        indexes[i] += 1
                        break

                if i is None:
                    break

            item[0] *= 1 + (1 / min_dist)

    def __sort_result(self):
        self.__result.sort(reverse=True)

    def get_documents_list(self):
        return [{'rank': item[0], 'url': item[1]} for item in self.__result]
