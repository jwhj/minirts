# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
#!/bin/bash
python train_executor_with_unit_selector.py \
  --train_dataset ../../data/dataset/train.json \
  --val_dataset ../../data/dataset/val.json \
  --inst_dict_path ../../data/dataset/dict.pt \
  --emb_field_dim 32 \
  --prev_cmd_dim 64 \
  --num_conv_layers 3 \
  --num_post_layers 1 \
  --conv_hid_dim 256 \
  --army_out_dim 256 \
  --other_out_dim 128 \
  --money_hid_layer 1 \
  --conv_dropout 0.1 \
  --rnn_word_emb_dim 128 \
  --word_emb_dropout 0 \
  --inst_hid_dim 128 \
  --inst_encoder_type zero \
  --model_folder saved_models/executor_zero_with_selector \
  --batch_size 128 \
  --gpu 0 \
  --grad_clip 0.5 \
  --lr 0.002 \
  --optim adamax \
  --epochs 50 \
  --use_hist_inst 0 \
  --pos_dim 32 \
  --prev_cmd_rnn 1 \
  --top_num_inst -1 \
  --seed 3 \
