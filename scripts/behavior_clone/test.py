import argparse
import os
import time
from rnn_coach import ConvRnnCoach
from executor_wrapper import ExecutorWrapper
from executor import Executor
from common_utils import to_device
from gym_minirts.wrappers import VecMiniRTSEnv

# import gym
from set_path import append_sys_path

append_sys_path()
import torch  # this is important: without importing torch, the program crashes
from torch.functional import F
import tube
from pytube import DataChannelManager
import minirts


def parse_args():
    parser = argparse.ArgumentParser(description='human coach')
    parser.add_argument('--seed', type=int, default=1)
    parser.add_argument('--num_thread', type=int, default=1)
    parser.add_argument('--game_per_thread', type=int, default=1)
    parser.add_argument('--gpu', type=int, default=0)

    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # root = '/workspace/minirts'
    default_lua = os.path.join(root, 'game/game_MC/lua')
    parser.add_argument('--lua_files', type=str, default=default_lua)

    # ai1 option
    parser.add_argument('--frame_skip', type=int, default=50)
    parser.add_argument('--fow', type=int, default=1)
    parser.add_argument('--use_moving_avg', type=int, default=1)
    parser.add_argument('--moving_avg_decay', type=float, default=0.98)
    parser.add_argument('--num_resource_bins', type=int, default=11)
    parser.add_argument('--resource_bin_size', type=int, default=50)
    parser.add_argument('--max_num_units', type=int, default=50)
    parser.add_argument('--num_prev_cmds', type=int, default=25)
    # TOOD: add max instruction span

    parser.add_argument('--max_raw_chars', type=int, default=200)
    parser.add_argument('--verbose', action='store_true')

    # game option
    parser.add_argument('--max_tick', type=int, default=int(2e5))
    parser.add_argument('--no_terrain', action='store_true')
    parser.add_argument('--resource', type=int, default=500)
    parser.add_argument('--resource_dist', type=int, default=4)
    parser.add_argument('--fair', type=int, default=0)
    parser.add_argument('--save_replay_freq', type=int, default=0)
    parser.add_argument('--save_replay_per_games', type=int, default=1)
    parser.add_argument('--save_dir', type=str, default='matches/dev')

    #
    parser.add_argument('--cheat', type=int, default=0)

    # model
    # 21.4 for best_rnn_executor
    # 25.2 for best_bow_executor
    # parser.add_argument('--coach_path', type=str, required=True)
    # parser.add_argument('--model_path', type=str, required=True)

    args = parser.parse_args()
    return args


def get_game_option(args):
    game_option = minirts.RTSGameOption()
    game_option.seed = args.seed
    game_option.max_tick = args.max_tick
    game_option.no_terrain = args.no_terrain
    game_option.resource = args.resource
    game_option.resource_dist = args.resource_dist
    game_option.fair = args.fair
    game_option.save_replay_freq = args.save_replay_freq
    game_option.save_replay_per_games = args.save_replay_per_games
    game_option.lua_files = args.lua_files
    game_option.num_games_per_thread = args.game_per_thread
    # !!! this is important
    game_option.max_num_units_per_player = args.max_num_units

    save_dir = os.path.abspath(args.save_dir)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    game_option.save_replay_prefix = save_dir + '/'

    return game_option


def get_ai_options(args, num_instructions):
    options = []
    for i in range(2):
        ai_option = minirts.AIOption()
        ai_option.t_len = 1
        ai_option.fs = args.frame_skip
        ai_option.fow = args.fow
        ai_option.use_moving_avg = args.use_moving_avg
        ai_option.moving_avg_decay = args.moving_avg_decay
        ai_option.num_resource_bins = args.num_resource_bins
        ai_option.resource_bin_size = args.resource_bin_size
        ai_option.max_num_units = args.max_num_units
        ai_option.num_prev_cmds = args.num_prev_cmds
        ai_option.num_instructions = num_instructions
        ai_option.max_raw_chars = args.max_raw_chars
        ai_option.verbose = args.verbose
        options.append(ai_option)

    return options[0], options[1]


if __name__ == '__main__':
    args = parse_args()
    os.environ['LUA_PATH'] = os.path.join(args.lua_files, '?.lua')
    game_option = get_game_option(args)
    ai1_option, ai2_option = get_ai_options(args, 500)
    # TODO: 500?

    device = torch.device('cuda:%d' % args.gpu)
    coach = ConvRnnCoach.load('saved_models/coach_rnn500/best_checkpoint.pt').to(device)
    coach.max_raw_chars = args.max_raw_chars
    executor = Executor.load('saved_models/executor_rnn/best_checkpoint.pt').to(device)
    executor_wrapper = ExecutorWrapper(
        coach, executor, coach.num_instructions, args.max_raw_chars, args.cheat
    )
    executor_wrapper.train(False)

    # envs=VecMiniRTSEnv(5,game_option,ai1_option,ai2_option)
    # obs=envs.reset()
    # action=executor_wrapper.forward(to_device(obs,device))
    # obs,_,_,_=envs.step(action)
    # envs.close()

    batchsize = min(16, max(args.num_thread // 2, 1))
    act_dc = tube.DataChannel('act', batchsize, 1)
    context = tube.Context()
    idx2utype = [
        minirts.UnitType.SPEARMAN,
        minirts.UnitType.SWORDMAN,
        minirts.UnitType.CAVALRY,
        minirts.UnitType.DRAGON,
        minirts.UnitType.ARCHER,
    ]

    for idx in range(args.num_thread):
        g_option = minirts.RTSGameOption(game_option)
        g_option.seed = game_option.seed + idx
        if game_option.save_replay_prefix:
            g_option.save_replay_prefix = game_option.save_replay_prefix + str(idx)

        g = minirts.RTSGame(g_option)
        bot1 = minirts.CheatExecutorAI(ai1_option, 0, None, act_dc)
        utype = idx2utype[idx % len(idx2utype)]
        bot2 = minirts.MediumAI(ai2_option, 0, None, utype, False)
        g.add_bot(bot1)
        g.add_bot(bot2)
        context.push_env_thread(g)

    # self.act_dc = act_dc
    # dc = DataChannelManager([act_dc])
    context.start()
    # with torch.no_grad():
    #     a = act_dc.get_input()
    #     tmp = a['map'].clone()
    #     reply = executor_wrapper.forward(to_device(a, device))
    #     g.terminate()
    #     print(1)
    #     act_dc.set_reply(reply)
    #     print(2)
    #     act_dc.terminate()
    # time.sleep(5)
    # print(context.terminated())
    i = 0
    while not context.terminated():
        print(i)
        i += 1
        a = act_dc.get_input()
        print(a['reward'].item())
        with torch.no_grad():
            __import__('pdb').set_trace()
            reply = executor_wrapper.forward(to_device(a, device))
        act_dc.set_reply(reply)
        if a['reward'].item() != 0:
            break
    act_dc.terminate()
