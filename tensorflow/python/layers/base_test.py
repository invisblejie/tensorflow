# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Tests for tf.layers.base."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf

from tensorflow.python.layers import base as base_layers


class BaseLayerTest(tf.test.TestCase):

  def testLayerProperties(self):
    layer = base_layers._Layer(name='my_layer')
    self.assertEqual(layer.name, 'my_layer')
    self.assertListEqual(layer.weights, [])
    self.assertListEqual(layer.trainable_weights, [])
    self.assertListEqual(layer.non_trainable_weights, [])
    self.assertListEqual(layer.updates, [])
    self.assertListEqual(layer.losses, [])
    self.assertEqual(layer.built, False)
    layer = base_layers._Layer(name='my_layer', trainable=False)
    self.assertEqual(layer.trainable, False)

  def testAddWeight(self):
    with self.test_session():
      layer = base_layers._Layer(name='my_layer')

      # Test basic variable creation.
      variable = layer._add_weight('my_var', [2, 2],
                                   initializer=tf.zeros_initializer)
      self.assertEqual(variable.name, 'my_var:0')
      self.assertListEqual(layer.weights, [variable])
      self.assertListEqual(layer.trainable_weights, [variable])
      self.assertListEqual(layer.non_trainable_weights, [])
      self.assertListEqual(layer.weights,
                           tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES))

      # Test non-trainable variable creation.
      # layer._add_weight should work even outside `build` and `call`.
      variable_2 = layer._add_weight('non_trainable_var', [2, 2],
                                     initializer=tf.zeros_initializer,
                                     trainable=False)
      self.assertListEqual(layer.weights, [variable, variable_2])
      self.assertListEqual(layer.trainable_weights, [variable])
      self.assertListEqual(layer.non_trainable_weights, [variable_2])
      self.assertEqual(
          len(tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES)), 1)

      # Test with regularizer.
      regularizer = lambda x: tf.reduce_sum(x) * 1e-3
      variable = layer._add_weight('reg_var', [2, 2],
                                   initializer=tf.zeros_initializer,
                                   regularizer=regularizer)
      self.assertEqual(len(layer.losses), 1)

  def testGetVariable(self):
    with self.test_session():
      # From inside `build` and `call` it should be possible to use
      # either tf.get_variable

      class MyLayer(base_layers._Layer):

        def build(self, input_shape):
          self.w = tf.get_variable('my_var', [2, 2],
                                   initializer=tf.zeros_initializer)

      layer = MyLayer(name='my_layer')
      inputs = tf.random_uniform((5,), seed=1)
      _ = layer.apply(inputs)
      self.assertListEqual(layer.weights, [layer.w])

  def testCall(self):

    class MyLayer(base_layers._Layer):

      def call(self, inputs):
        return tf.square(inputs)

    layer = MyLayer(name='my_layer')
    inputs = tf.random_uniform((5,), seed=1)
    outputs = layer.apply(inputs)
    self.assertEqual(layer.built, True)
    self.assertEqual(outputs.op.name, 'my_layer/Square')


if __name__ == '__main__':
  tf.test.main()
