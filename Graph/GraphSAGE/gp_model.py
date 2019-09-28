import tensorflow as tf
import numpy as np
import gp_minibatch
import gp_loaddata
tf.enable_eager_execution()
KERAS = tf.keras


# 输入为图的邻居结点结构信息，输出为选取的某些结点的邻居（从各个结点邻居中随机）
class UniformNeighborSampler(KERAS.layers.Layer):
    def __init__(self, adj_info, num_choosed):
        self.adj_info = adj_info
        self.num_choosed = num_choosed
        super().__init__()

    def call(self, inputs):
        id_list = inputs
        adj_list = tf.nn.embedding_lookup(self.adj_info, id_list)
        adj_list = tf.squeeze(adj_list, axis=1)
        adj_list = tf.transpose(tf.random_shuffle(tf.transpose(adj_list)))
        adj_list = tf.slice(adj_list, [0, 0], [-1, self.num_choosed])
        return adj_list


class GCNAggregator():
    pass


class NeighborSampler():
    pass


class SampleAndAggregate(object):
    def __init__(self):
        self.aggregator = GCNAggregator()


    def sample(self, inputs, layer_infos, batch_size=None):
        '''
        inputs为一系列的结点（一系列边中的结点）
        '''
        if batch_size is None:
            batch_size = self.batch_size
        samples = [inputs]
        # size of convolution support at each layer per node
        support_size = 1
        support_sizes = [support_size]
        for k in range(len(layer_infos)):
            t = len(layer_infos) - k - 1
            support_size *= layer_infos[t].num_samples
            sampler = layer_infos[t].neigh_sampler
            node = sampler((samples[k], layer_infos[t].num_samples))
            samples.append(tf.reshape(node, [support_size * batch_size, ]))
            support_sizes.append(support_size)
        return samples, support_sizes


if __name__ == '__main__':
    director = r'Datasets\Temp\Graphsage_data'
    graph, features, labels = gp_loaddata.load_data(director+r'\toy-ppi-G.json')
    node_itor = gp_minibatch.NodeMinibatchIterator(graph, labels, 1000)

    # 定义模型
    model_inputs_nodes = KERAS.layers.Input(shape=1, dtype=tf.int32)  # 注意1代表位输入的是一个数字
    predict = UniformNeighborSampler(node_itor.node_adjlist, 10)(model_inputs_nodes)
    model = KERAS.models.Model(inputs=model_inputs_nodes, outputs=predict)

    # 测试模型
    temp = node_itor.next_minibatch_feed_dict()['batch_nodes']
    temp_input = KERAS.initializers.constant(temp, dtype=tf.int32)
    temp_result = model(temp)
    pass
