#!/usr/bin/python
#-*- coding: utf-8 -*-

# >.>.>.>.>.>.>.>.>.>.>.>.>.>.>.>.
# Licensed under the Apache License, Version 2.0 (the "License")
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0

# --- File Name: modular_transformer.py
# --- Creation Date: 06-04-2021
# --- Last Modified: Wed 07 Apr 2021 22:18:10 AEST
# --- Author: Xinqi Zhu
# .<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<
"""
Modular Transformer networks.
Code borrowed from https://www.tensorflow.org/tutorials/text/transformer
"""
import numpy as np
import tensorflow as tf
from training.networks_stylegan2 import dense_layer, conv2d_layer
from training.networks_stylegan2 import apply_bias_act, naive_upsample_2d
from training.networks_stylegan2 import naive_downsample_2d, modulated_conv2d_layer
from training.networks_stylegan import instance_norm, style_mod
from training.utils import get_return_v


def create_look_ahead_mask(size):
    mask = 1 - tf.linalg.band_part(tf.ones((size, size)), -1, 0)
    return mask  # (seq_len, seq_len)


def scaled_dot_product_attention(q, k, v, mask):
    """Calculate the attention weights.
    q, k, v must have matching leading dimensions.
    k, v must have matching penultimate dimension, i.e.: seq_len_k = seq_len_v.
    The mask has different shapes depending on its type(padding or look ahead)
    but it must be broadcastable for addition.

    Args:
      q: query shape == (..., seq_len_q, depth)
      k: key shape == (..., seq_len_k, depth)
      v: value shape == (..., seq_len_v, depth_v)
      mask: Float tensor with shape broadcastable
            to (..., seq_len_q, seq_len_k). Defaults to None.

    Returns:
      output, attention_weights
    """

    matmul_qk = tf.matmul(q, k, transpose_b=True)  # (..., seq_len_q, seq_len_k)

    # scale matmul_qk
    dk = tf.cast(tf.shape(k)[-1], tf.float32)
    scaled_attention_logits = matmul_qk / tf.math.sqrt(dk)

    # add the mask to the scaled tensor.
    if mask is not None:
      scaled_attention_logits += (mask * -1e9)

    # softmax is normalized on the last axis (seq_len_k) so that the scores
    # add up to 1.
    attention_weights = tf.nn.softmax(scaled_attention_logits, axis=-1)  # (..., seq_len_q, seq_len_k)

    output = tf.matmul(attention_weights, v)  # (..., seq_len_q, depth_v)

    return output, attention_weights


def split_heads(x, num_heads, depth):
    """Split the last dimension into (num_heads, depth).
    Transpose the result such that the shape is (batch_size, num_heads, seq_len, depth)
    """
    batch_size = tf.shape(x)[0]
    x = tf.reshape(x, (batch_size, -1, num_heads, depth))
    return tf.transpose(x, perm=[0, 2, 1, 3])


def multihead_attention(v, k, q, mask, d_model, num_heads):
    batch_size = tf.shape(q)[0]
    depth = d_model // num_heads
    q = dense_layer(q, d_model)
    k = dense_layer(k, d_model)
    v = dense_layer(v, d_model)

    q = split_heads(q, num_heads, depth)  # (batch_size, num_heads, seq_len_q, depth)
    k = split_heads(k, num_heads, depth)  # (batch_size, num_heads, seq_len_k, depth)
    v = split_heads(v, num_heads, depth)  # (batch_size, num_heads, seq_len_v, depth)

    scaled_attention, attention_weights = scaled_dot_product_attention(
        q, k, v, mask)

    scaled_attention = tf.transpose(scaled_attention, perm=[0, 2, 1, 3])  # (batch_size, seq_len_q, num_heads, depth)

    concat_attention = tf.reshape(scaled_attention,
                                  (batch_size, -1, d_model))  # (batch_size, seq_len_q, d_model)
    output = dense_layer(concat_attention, d_model)  # (batch_size, seq_len_q, d_model)

    return output, attention_weights


def point_wise_feed_forward_network(x, d_model, dff):
    x = apply_bias_act(dense_layer(x, dff), act='relu')  # (batch_size, seq_len, dff)
    x = dense_layer(x, d_model)  # (batch_size, seq_len, d_model)
    return x


def trans_encoder_layer(x, mask, d_model, num_heads, dff, is_training, rate=0.1):

    attn_output, attention_weights = multihead_attention(x, x, x, mask, d_model, num_heads)  # (batch_size, input_seq_len, d_model)
    if is_training:
        attn_output = tf.nn.dropout(attn_output, rate=rate)
    out1 = tf.contrib.layers.layer_norm(inputs=x + attn_output, begin_norm_axis=-1, begin_params_axis=-1)

    ffn_output = point_wise_feed_forward_network(out1, d_model, dff)
    if is_training:
        ffn_output = tf.nn.dropout(ffn_output, rate=rate)
    out2 = tf.contrib.layers.layer_norm(inputs=out1 + ffn_output, begin_norm_axis=-1, begin_params_axis=-1)

    return out2, attention_weights

def trans_decoder_layer(x, enc_output, d_model, num_heads, dff, is_training,
                        look_ahead_mask, padding_mask, rate=0.1):
    attn1, attn_weights_block1 = multihead_attention(x, x, x, look_ahead_mask, d_model, num_heads)  # (batch_size, target_seq_len, d_model)
    if is_training:
        attn1 = tf.nn.dropout(attn1, rate=rate)
    out1 = tf.contrib.layers.layer_norm(inputs=attn1 + x, begin_norm_axis=-1, begin_params_axis=-1)

    attn2, attn_weights_block2 = multihead_attention(
        enc_output, enc_output, out1, padding_mask, d_model, num_heads)  # (batch_size, target_seq_len, d_model)
    if is_training:
        attn2 = tf.nn.dropout(attn2, rate=rate)
    out2 = tf.contrib.layers.layer_norm(inputs=attn2 + out1, begin_norm_axis=-1, begin_params_axis=-1)  # (batch_size, target_seq_len, d_model)

    ffn_output = point_wise_feed_forward_network(out2, d_model, dff)  # (batch_size, target_seq_len, d_model)
    if is_training:
        ffn_output = tf.nn.dropout(ffn_output, rate=rate)
    out3 = tf.contrib.layers.layer_norm(inputs=ffn_output + out2, begin_norm_axis=-1, begin_params_axis=-1)  # (batch_size, target_seq_len, d_model)

    return out3, attn_weights_block1, attn_weights_block2


def get_angles(pos, i, d_model):
    angle_rates = 1 / np.power(10000, (2 * (i//2)) / np.float32(d_model))
    return pos * angle_rates


def positional_encoding(position, d_model):
    angle_rads = get_angles(np.arange(position)[:, np.newaxis],
                            np.arange(d_model)[np.newaxis, :],
                            d_model)

    # apply sin to even indices in the array; 2i
    angle_rads[:, 0::2] = np.sin(angle_rads[:, 0::2])

    # apply cos to odd indices in the array; 2i+1
    angle_rads[:, 1::2] = np.cos(angle_rads[:, 1::2])

    pos_encoding = angle_rads[np.newaxis, ...]

    return tf.cast(pos_encoding, dtype=tf.float32)


def trans_encoder_basic(x, is_training, mask, num_layers, d_model, num_heads, dff, rate=0.1):
    if is_training:
        x = tf.nn.dropout(x, rate=rate)

    atts = []
    for _ in range(num_layers):
        x, tmp_atts = trans_encoder_layer(x, mask, d_model, num_heads, dff, is_training, rate=rate)
        atts.append(tmp_atts)

    # x.shape == (batch_size, input_seq_len, d_model)
    return x, atts


def trans_decoder_basic(x, enc_output, is_training, look_ahead_mask, padding_mask, num_layers,
                        d_model, num_heads, dff, rate=0.1, maximum_position_encoding=40):
    seq_len = tf.shape(x)[1]
    atts_1 = []
    atts_2 = []

    pos_encoding = positional_encoding(maximum_position_encoding, d_model)
    x += pos_encoding[:, :seq_len, :]
    if is_training:
        x = tf.nn.dropout(x, rate=rate)

    for _ in range(num_layers):
        x, block1, block2 = trans_decoder_layer(x, enc_output, d_model, num_heads, dff, is_training,
                                                look_ahead_mask, padding_mask, rate=rate)
        atts_1 = block1
        atts_2 = block2

    # x.shape == (batch_size, target_seq_len, d_model)
    return x, atts_1, atts_2


def sc_masks(mask_logits, n_masks, n_subs, wh):
    atts_wh = dense_layer(mask_logits, fmaps=n_subs * 4 * wh)
    atts_wh = tf.reshape(atts_wh, [-1, n_masks, n_subs, 4, wh]) # [b, n_masks, n_subs, 4, wh]
    att_wh_sm = tf.nn.softmax(atts_wh, axis=-1)
    att_wh_cs = tf.cumsum(att_wh_sm, axis=-1)
    att_h_cs_starts, att_h_cs_ends, att_w_cs_starts, att_w_cs_ends = tf.split(att_wh_cs, 4, axis=3)
    att_h_cs_ends = 1 - att_h_cs_ends # [b, n_masks, n_subs, 1, wh]
    att_w_cs_ends = 1 - att_w_cs_ends # [b, n_masks, n_subs, 1, wh]
    att_h_cs_starts = tf.reshape(att_h_cs_starts, [-1, n_masks, n_subs, wh, 1])
    att_h_cs_ends = tf.reshape(att_h_cs_ends, [-1, n_masks, n_subs, wh, 1])
    att_h = att_h_cs_starts * att_h_cs_ends # [b, n_masks, n_subs, wh, 1]
    att_w_cs_starts = tf.reshape(att_w_cs_starts, [-1, n_masks, n_subs, 1, wh])
    att_w_cs_ends = tf.reshape(att_w_cs_ends, [-1, n_masks, n_subs, 1, wh])
    att_w = att_w_cs_starts * att_w_cs_ends # [b, n_masks, n_subs, 1, wh]
    atts = att_h * att_w # [b, n_masks, n_subs, wh, wh]
    atts = tf.reduce_mean(atts, axis=2) # [b, n_masks, wh, wh]
    return atts


def build_trans_paral_layer(x, name, n_layers, scope_idx, act, dtype,
                            is_training, wh, n_subs,
                            trans_dim=512, return_atts=False, **kwargs):
    '''
    Build parallel forwarding transformer to predict semantic variation masks.
    '''
    with tf.variable_scope(name + '-' + str(scope_idx)):
        with tf.variable_scope('MaskEncoding'):
            n_masks = tf.shape(x)[-1]
            mask_encoding = tf.get_variable('mask_encoding', shape=[1, n_masks, trans_dim],
                                            initializer=tf.initializers.random_normal())
            mask_encoding = tf.tile(tf.cast(mask_encoding, dtype), [tf.shape(x)[0], 1, 1])
            mask_logits, encoder_inner_atts = trans_encoder_basic(mask_encoding, is_training, None, n_layers,
                                                                  trans_dim, num_heads=8, dff=512, rate=0.1)  # (b, z_dim, d_model)

        with tf.variable_scope('MaskMapping'):
            atts = sc_masks(mask_logits, n_masks, n_subs, wh)
            masks = tf.reshape(atts, [-1, n_masks, wh * wh])
            y = tf.concat([x[:, :, np.newaxis], masks], axis=-1)
        return y, atts

def build_trans_z_to_mask_layer(x, name, n_layers, scope_idx, act, dtype,
                                is_training, wh, n_subs,
                                trans_dim=512, return_atts=False, **kwargs):
    '''
    Build z_to_mask forwarding transformer to predict semantic variation masks.
    '''
    with tf.variable_scope(name + '-' + str(scope_idx)):
        with tf.variable_scope('MaskEncoding'):
            x = x[:, :, np.newaxis]
            n_masks = tf.shape(x)[-2]
            mask_logits = get_return_v(trans_encoder_basic(x, is_training, None, n_layers,
                                                           trans_dim, num_heads=8, dff=512, rate=0.1), 1)  # (b, z_dim, d_model)

        with tf.variable_scope('MaskMapping'):
            atts = sc_masks(mask_logits, n_masks, n_subs, wh)
            masks = tf.reshape(atts, [-1, n_masks, wh * wh])
            y = tf.concat([x[:, :, np.newaxis], masks], axis=-1)
        return y, atts

def build_trans_mask_to_feat_layer(x, name, n_layers, scope_idx, act, dtype,
                                   is_training, wh, n_subs,
                                   trans_dim=512, return_atts=False, **kwargs):
    '''
    Build mask_to_feat forwarding transformer to predict semantic variation masks.
    '''
    with tf.variable_scope(name + '-' + str(scope_idx)):
        with tf.variable_scope('MaskEncoding'):
            x = x[:, :, np.newaxis]
            n_masks = tf.shape(x)[-2]
            mask_logits = get_return_v(trans_encoder_basic(x, is_training, None, n_layers,
                                                           trans_dim, num_heads=8, dff=512, rate=0.1), 1)  # (b, z_dim, d_model)

        with tf.variable_scope('MaskMapping'):
            atts = sc_masks(mask_logits, n_masks, n_subs, wh)
            masks = tf.reshape(atts, [-1, n_masks, wh * wh])
            y = tf.concat([x[:, :, np.newaxis], masks], axis=-1)
        return y, atts
