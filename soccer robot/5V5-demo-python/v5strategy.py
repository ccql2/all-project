'''
这个文件是主要开发文件，涵盖了策略全部的四个接口
-on_event接收比赛状态变化的信息。
    参数event_type type表示事件类型；
    参数EventArgument表示该事件的参数，如果不含参数，则为NULL。
-get_team_info控制队名。
    修改返回值的字符串即可修改自己的队名
-get_instruction控制5个机器人的轮速(leftspeed,rightspeed)，以及最后的reset(1即表明需要reset)
    通过返回值来给机器人赋轮速
    比赛中的每拍被调用，需要策略指定轮速，相当于旧接口的Strategy。
    参数field为In/Out参数，存储当前赛场信息，并允许策略修改己方轮速。
    ！！！所有策略的开发应该在此模块
-get_placement控制5个机器人及球在需要摆位时的位置
    通过返回值来控制机器人和球的摆位。
    每次自动摆位时被调用，需要策略指定摆位信息。
    定位球类的摆位需要符合规则，否则会被重摆
'''
import random
from typing import Tuple, Union

from V5RPC import *
import math
from baseRobot import *
from GlobalVariable import *
baseRobots = []# 定义我方机器人数组
oppRobots = []# 定义对方机器人数组
data_loader = DataLoader()
race_state = -1  # 定位球状态
race_state_trigger = -1    # 触发方

tickBeginPenalty = 0
tickBeginGoalKick = 0
lastBallx = -110 + 37.5
lastBally = 0
BallPos = [Vector2(0, 0)] * 100000
resetHistoryRecord = False
newMatch = False

# 打印比赛状态，详细请对比v5rpc.py
@unbox_event
def on_event(event_type: int, args: EventArguments):
    event = {
        0: lambda: print(args.judge_result.reason),
        1: lambda: print("Match Start"),
        2: lambda: print("Match Stop"),
        3: lambda: print("First Half Start"),
        4: lambda: print("Second Half Start"),
        5: lambda: print("Overtime Start"),
        6: lambda: print("Penalty Shootout Start"),
        7: lambda: print("MatchShootOutStart"),
        8: lambda: print("MatchBlockStart")
    }
    global race_state_trigger
    global race_state
    if event_type == 0:
        race_state = args.judge_result.type
        race_state_trigger = args.judge_result.offensive_team
        if race_state == JudgeResultEvent.ResultType.PlaceKick:
            print("Place Kick")
        elif race_state == JudgeResultEvent.ResultType.PenaltyKick:
            print("Penalty Kick")
        elif race_state == JudgeResultEvent.ResultType.GoalKick:
            print("Goal Kick")
        elif (race_state == JudgeResultEvent.ResultType.FreeKickLeftBot
              or race_state == JudgeResultEvent.ResultType.FreeKickRightBot
              or race_state == JudgeResultEvent.ResultType.FreeKickLeftTop
              or race_state == JudgeResultEvent.ResultType.FreeKickRightTop):
            print("Free Kick")

        actor = {
            Team.Self: lambda: print("By Self"),
            Team.Opponent: lambda: print("By Opp"),
            Team.Nobody: lambda: print("By Nobody"),
        }
        actor[race_state_trigger]()

    event[event_type]()

@unbox_int
def get_team_info(server_version: int) -> str:
    version = {
        0: "V1.0",
        1: "V1.1"
    }
    print(f'server rpc version: {version.get(server_version, "V1.0")}')
    global newMatch
    newMatch = True
    return '206小队'# 在此行修改双引号中的字符串为自己的队伍名

# 策略行为主函数，可将以下函数用策略模式封装
def strategy_common(field):
    # 最基本最常规情况下的执行策略
    # 假设黄方，给三个机器人限制活动范围

    football_now_x = field.ball.position.x
    football_now_y = field.ball.position.y
    futureBallx = 8 * football_now_x - 7 * BallPos[GlobalVariable.tick - 1].x
    futureBally = 8 * football_now_y - 7 * BallPos[GlobalVariable.tick - 1].y
    baseRobots[2].shoot(futureBallx, futureBally)# 1号机器人x不超过80的情况下追球（前锋）
    baseRobots[1].moveto_within_x_limits(-90, -12, futureBallx, futureBally)# 2号机器人x不超过-12的情况下追球（后卫）
    baseRobots[4].moveto_within_x_limits(-90, 5, futureBallx, futureBally)# 3号机器人x不超过5的情况下追球（中场）
    # 己方场地无对方机器人，且威胁不到球门，门卫应当适当出门
    judge_num=0
    for i in range(1,5):
        if(oppRobots[i].get_pos().x>0):
            judge_num+=1
    if(judge_num==4 and football_now_x<0):
        baseRobots[0].shoot(futureBallx,futureBally)

    #球在己方场地，4号追求，球在大禁区以内则阻挡对方一名球员
    if(futureBallx<0 and futureBallx>-90):
        baseRobots[4].shoot(futureBallx, futureBally)
    elif(futureBallx < -90):
        if(oppRobots[1].get_pos().x<0):
            baseRobots[4].moveto(oppRobots[1].get_pos().x,oppRobots[1].get_pos().y)
        elif(oppRobots[2].get_pos().x<0):
            baseRobots[4].moveto(oppRobots[2].get_pos().x, oppRobots[2].get_pos().y)
        elif (oppRobots[3].get_pos().x < 0):
            baseRobots[4].moveto(oppRobots[3].get_pos().x, oppRobots[3].get_pos().y)
        elif (oppRobots[4].get_pos().x < 0):
            baseRobots[4].moveto(oppRobots[4].get_pos().x, oppRobots[4].get_pos().y)


    baseRobots[3].shoot(futureBallx, futureBally)# 3号自由人追球

    num_in_big_area = 0
    dis = [-1, -1, -1, -1, -1]	# -1 表示不在禁区里面
    for i in range(1, 5):
        if baseRobots[i].get_pos().x < -77 and np.fabs(baseRobots[i].get_pos().y) < 50:	#禁区内机器人计数且计算距离，禁区外距离为负
            num_in_big_area += 1
            dis[i] = min(np.fabs(-72.5 - baseRobots[i].get_pos().x), np.fabs(np.fabs(baseRobots[i].get_pos().y) - 40))
    if num_in_big_area >= 2:
        out_robot1 = 1
        out_robot2 = 2
        for i in range(1, 5):
            if dis[i] < dis[out_robot1]:
                out_robot2 = out_robot1
                out_robot1 = i
            elif dis[i] < dis[out_robot2]:
                out_robot2 = i
        if dis[out_robot1] == np.fabs(baseRobots[out_robot1].get_pos().x + 72.5):
            baseRobots[out_robot1].moveto(-65, baseRobots[out_robot1].get_pos().y)
        elif np.fabs(baseRobots[out_robot1].get_pos().y > 0):
            baseRobots[out_robot1].moveto(baseRobots[out_robot1].get_pos().x, 50)
        else:
            baseRobots[out_robot1].moveto(baseRobots[out_robot1].get_pos().x, -50)

        if dis[out_robot2] == np.fabs(baseRobots[out_robot2].get_pos().x + 72.5):
            baseRobots[out_robot2].moveto(-65, baseRobots[out_robot2].get_pos().y)
        elif np.fabs(baseRobots[out_robot2].get_pos().y > 0):
            baseRobots[out_robot2].moveto(baseRobots[out_robot2].get_pos().x, 50)
        else:
            baseRobots[out_robot2].moveto(baseRobots[out_robot2].get_pos().x, -50)

    if baseRobots[0].get_pos().x <= -110 + 2.9:
        baseRobots[0].moveto(-105 + 2.5, 0)
    else:

        temp = random.randint(0, 2)
        if temp == 0:
            if np.fabs(football_now_y) < 20 - 1.7:
                if football_now_x > -105 + 17:
                    baseRobots[0].moveto(-115 + 1.6, football_now_y)
                else:
                    baseRobots[0].moveto(football_now_x, football_now_y)
            else:
                if football_now_y > 0:
                    baseRobots[0].moveto(-110 + 1.6, 20 - 2.2)
                else:
                    baseRobots[0].moveto(-110 + 1.6, -(20 - 2.2))
        elif temp == 1:
            if np.fabs(football_now_y) < 23 - 1.7:
                if football_now_x > -105 + 17:
                    baseRobots[0].moveto(-116 + 1.9, football_now_y)
                else:
                    baseRobots[0].moveto(football_now_x, football_now_y)
            else:
                if football_now_y > 0:
                    baseRobots[0].moveto(-110 + 3.2, 20 - 2.2)
                else:
                    baseRobots[0].moveto(-110 + 1.1, -(20 - 2.2))
        else:
            if np.fabs(football_now_y) < 21 - 1.7:
                if football_now_x > -110 + 16:
                    baseRobots[0].moveto(-115 + 0.6, football_now_y)
                else:
                    baseRobots[0].moveto(football_now_x, football_now_y)
            else:
                if football_now_y > 0:
                    baseRobots[0].moveto(-110 + 1.6, 20 - 2.2)
                else:
                    baseRobots[0].moveto(-110 + 1.6, -(20 - 2.2))

def strategy_find_pos(field):
    destination_pos_x = 110
    destination_pos_y = 0
    football_now_x = field.ball.position.x
    football_now_y = field.ball.position.y
    futureBallx = 4 * football_now_x - 3 * BallPos[GlobalVariable.tick - 1].x
    futureBally = 4 * football_now_y - 3 * BallPos[GlobalVariable.tick - 1].y
    slope = (destination_pos_y-destination_pos_y)/(destination_pos_x-futureBallx)
    b=futureBally-slope*futureBallx
    # temp_location_x =
    # temp_location_y =
    # diagonal = math.sqrt(temp_location_x*temp_location_x+temp_location_y*temp_location_y)
    final_destination_pos_x = football_now_x-2
    final_destination_pos_y = slope*final_destination_pos_x+b
    return final_destination_pos_x,final_destination_pos_y

def strategy_penalty(field):
    football_now_x = field.ball.position.x
    football_now_y = field.ball.position.y
    futureBallx = 4 * football_now_x - 3 * BallPos[GlobalVariable.tick - 1].x
    futureBally = 4 * football_now_y - 3 * BallPos[GlobalVariable.tick - 1].y
    global tickBeginPenalty
    global race_state_trigger

    if race_state_trigger == Team.Self:
        for i in range(0, 5):
            baseRobots[i].set_wheel_velocity(0, 0)
        if GlobalVariable.tick - tickBeginPenalty <= 12:
            baseRobots[1].set_wheel_velocity(45, 45)
            baseRobots[3].set_wheel_velocity(125, 125)
        elif GlobalVariable.tick - tickBeginPenalty <= 35:
            baseRobots[1].set_wheel_velocity(10, 10)
            baseRobots[3].set_wheel_velocity(125, 125)
        elif GlobalVariable.tick - tickBeginPenalty <= 60:
            baseRobots[1].set_wheel_velocity(0, 0)
            baseRobots[3].throw_ball(football_now_x, football_now_y)
        else:
            strategy_common(field)

    if race_state_trigger == Team.Opponent:
        if GlobalVariable.tick - tickBeginPenalty <= 60 and football_now_x <= -70 and football_now_y <= 40:
            for i in range(0, 5):
                baseRobots[i].set_wheel_velocity(0, 0)
            baseRobots[0].moveto(futureBallx, futureBally-3)
        else:
            strategy_common(field)

def strategy_goalkick(field):
    global tickBeginGoalKick
    global race_state_trigger

    football_now_x = field.ball.position.x
    football_now_y = field.ball.position.y
    futureBallx = 4 * football_now_x - 3 * BallPos[GlobalVariable.tick - 1].x
    futureBally = 4 * football_now_y - 3 * BallPos[GlobalVariable.tick - 1].y

    if race_state_trigger == Team.Self:
        if GlobalVariable.tick - tickBeginGoalKick <= 40:
            for i in range(0, 5):
                baseRobots[i].set_wheel_velocity(0, 0)
            baseRobots[0].moveto(-100,9)
            baseRobots[0].set_wheel_velocity(120, 120)
            # baseRobots[0].shoot(futureBallx,futureBally)
        else:
            strategy_common(field)
    if race_state_trigger == Team.Opponent:
        strategy_common(field)
        # python start.py 20001

@unbox_field
def get_instruction(field: Field):
    # python start.py 20000    print(field.tick)  # tick从2起始
    GlobalVariable.tick = field.tick
    global resetHistoryRecord
    for i in range(0, 5):
        baseRobots.append(BaseRobot())
        oppRobots.append(BaseRobot())
        baseRobots[i].update(field.self_robots[i], resetHistoryRecord)
        oppRobots[i].update(field.opponent_robots[i], resetHistoryRecord)
        global newMatch
        if field.tick == 2: #newMatch is True:
            for j in range(0, 8):
                baseRobots[i].HistoryInformation[j] = field.self_robots[i].copy()   # 第0拍主动维护历史数据
                baseRobots[i].PredictInformation[j] = field.self_robots[i].copy()	# 第0拍主动维护预测数据
            newMatch = False
        baseRobots[i].PredictRobotInformation(4)#(GlobalVariable.tick_delay)

    football_now_x = -field.ball.position.x   # 黄方假设，球坐标取反
    football_now_y = -field.ball.position.y

    field.ball.position.x = -field.ball.position.x
    field.ball.position.y = -field.ball.position.y

    global BallPos
    BallPos[GlobalVariable.tick] = Vector2(football_now_x, football_now_y)
    if resetHistoryRecord is True:
        for i in range(GlobalVariable.tick, GlobalVariable.tick - 11, -1):
            BallPos[i] = Vector2(football_now_x, football_now_y)

    if race_state == JudgeResultEvent.ResultType.PenaltyKick:
        strategy_penalty(field)
    elif race_state == JudgeResultEvent.ResultType.GoalKick:
        strategy_goalkick(field)
    else:
        strategy_common(field)


    for i in range(0, 5):
        baseRobots[i].save_last_information(football_now_x, football_now_y)
    data_loader.set_tick_state(GlobalVariable.tick, race_state)
    resetHistoryRecord = False

    velocity_to_set = []
    for i in range(0, 5):
        velocity_to_set.append((baseRobots[i].robot.wheel.left_speed, baseRobots[i].robot.wheel.right_speed))

    return velocity_to_set, 0    # 以第二元素的(0,1)表明重置开关,1表示重置


@unbox_field
def get_placement(field: Field) -> List[Tuple[float, float, float]]:
    final_set_pos: List[Union[Tuple[int, int, int], Tuple[float, float, float]]]
    global resetHistoryRecord
    resetHistoryRecord = True
    if race_state == JudgeResultEvent.ResultType.PlaceKick:
        if race_state_trigger == Team.Self:
            print("开球进攻摆位")
            set_pos = [[-100, 20, 0],
                       [0, -5, 90],
                       [-30, -30, 0],
                       [-50, 30, 0],
                       [-80, 0, 0],
                       [0.0, 0.0, 0.0]]
            # set_pos = [(-103, 0, 90), (30, 0, 0), (-3, -10, 0), (-3, 10, 0), (-3, 0, 0), (0.0, 0.0, 0.0)]
        else:   # if race_state_trigger == Team.Opponent:
            print("开球防守摆位")
            set_pos = [[-100, 20, 0],
                       [-10, 80, -90],
                       [-30, -80, -90],
                       [-50, 70, -90],
                       [-80, -80, -90],
                       [0.0, 0.0, 0.0]]
            # set_pos = [(-105, 0, 90), (10, 20, -90), (10, -20, -90), (10, 40, -90), (10, -40, -90), (0.0, 0.0, 0.0)]
    elif race_state == JudgeResultEvent.ResultType.PenaltyKick:
        global tickBeginPenalty
        tickBeginPenalty = field.tick
        if race_state_trigger == Team.Self:
            print("点球进攻摆位")
            set_pos = [[-103, 0, 0],
                       [72.5, -10, 90],
                       [-50, -50, -30],
                       [-10, 50, -20],
                       [-30, 0, 0],
                       [5, 10, 0.0]]
        else:   # if race_state_trigger == Team.Opponent:
            print("点球防守摆位")
            set_pos = [[-95, 0, 0],
                       [10, 20, 0],
                       [10, -20, -90],
                       [10, 40, -90],
                       [10, -40, -90],
                       [0, 0.0, 0.0]]
    elif race_state == JudgeResultEvent.ResultType.GoalKick:
        global tickBeginGoalKick
        tickBeginGoalKick = field.tick
        if race_state_trigger == Team.Self:
            print("门球进攻摆位")
            set_pos = [[-101-1, 0, 73],
                       [-110+60, 40, -90],
                       [-50, -40, -90],
                       [-30, 0, -90],
                       [-50, 0, -90],
                       [-95.27, 9.05, 0.0]]
        else:   # if race_state_trigger == Team.Opponent:
            print("门球防守摆位")
            set_pos = [[-105, 0, 0],
                       [30, 0, 0],
                       [-30, -10, 0],
                       [-50, 10, 0],
                       [-80, 0, 0],
                       [0.0, 0.0, 0.0]]
    elif (race_state == JudgeResultEvent.ResultType.FreeKickLeftTop
          or race_state == JudgeResultEvent.ResultType.FreeKickRightTop
          or race_state == JudgeResultEvent.ResultType.FreeKickRightBot
          or race_state == JudgeResultEvent.ResultType.FreeKickLeftBot):
        if race_state_trigger == Team.Self:
            print("争球进攻摆位")
            set_pos = [[-103, 0, 90],
                       [30, 0, 0],
                       [-3, -10, 0],
                       [-3, 10, 0],
                       [-3, 0, 0],
                       [0.0, 0.0, 0.0]]
        else:   # if race_state_trigger == Team.Opponent:
            print("争球防守摆位")
            set_pos = [[-105, 0, 0],
                       [30, 0, 0],
                       [10, -10, 0],
                       [10, 10, 0],
                       [10, 0, 0],
                       [0.0, 0.0, 0.0]]
    else:
        print("race_state = " + str(race_state))

    for set_pos_s in set_pos:     # 摆位反转
        set_pos_s[0] = -set_pos_s[0]
        set_pos_s[1] = -set_pos_s[1]
        set_pos_s[2] -= 180
        if set_pos_s[2] < -180:
            set_pos_s[2] += 360
    final_set_pos = [(set_pos[0][0], set_pos[0][1], set_pos[0][2]),
                     (set_pos[1][0], set_pos[1][1], set_pos[1][2]),
                     (set_pos[2][0], set_pos[2][1], set_pos[2][2]),
                     (set_pos[3][0], set_pos[3][1], set_pos[3][2]),
                     (set_pos[4][0], set_pos[4][1], set_pos[4][2]),
                     (set_pos[5][0], set_pos[5][1], set_pos[5][2])]

    print(final_set_pos)
    return final_set_pos  # 最后一个是球位置（x,y,角）,角其实没用